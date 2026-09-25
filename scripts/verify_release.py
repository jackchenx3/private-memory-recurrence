"""Check release hashes, source provenance, local links and plotted statistics."""
from pathlib import Path
import gzip,hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    verified=0
    for line in (ROOT/'SHA256SUMS').read_text().splitlines():
        expected,name=line.split(None,1)
        path=ROOT/name
        assert path.is_file() and sha(path)==expected,name
        verified+=1
    source_map=json.loads((ROOT/'provenance/EXPORT_MAP.json').read_text())
    for record in source_map:
        assert sha(ROOT/record['path'])==record['published_sha256'],record['path']
    checked=0
    for record in json.loads((ROOT/'figures/FIGURE_DATA.json').read_text()):
        if 'key' not in record:continue
        q=json.loads((ROOT/'results'/record['study']/'summary.json').read_text())['values'][record['key']]
        assert record['mean_pp']==q['mean']*100
        assert record['ci95_pp']==[v*100 for v in q['ci95']]
        checked+=1
    registry=json.loads((ROOT/'EVIDENCE_REGISTRY.json').read_text())
    assert registry['statistical_estimates']['count']==15284
    assert registry['certified_mathematical_quantities']['count']==14 and registry['figures']['count']==18
    for item in json.loads((ROOT/'provenance/RELEASE_061_CHECK_REUSE.json').read_text())['inputs']:
        assert sha(ROOT/item['path'])==item['sha256'],item['path']
    math_check=json.loads((ROOT/'provenance/061_CERTIFICATES_CHECK.json').read_text())
    assert math_check['status']=='PASS' and math_check['records']==14 and math_check['stationary_solves']==0
    math_fig=json.loads((ROOT/'figures/FIGURE_061_DATA.json').read_text())
    assert len(math_fig['bindings'])==11 and math_fig['source_sha256']==sha(ROOT/math_fig['source'])
    math_values=json.loads((ROOT/math_fig['source']).read_text());math_bindings=0
    for item in math_fig['bindings']:
        for kind in ('center','lower','upper'):
            if kind in item:
                assert item[kind]==math_values[item['key']][kind]
                math_bindings+=1
    assert math_bindings==27 and len(list((ROOT/'figures').glob('*.png')))==18
    broken=[];links=0
    for path in ROOT.rglob('*.md'):
        if any(p in path.parts for p in ['.git','_rebuilt']):continue
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if target.startswith(('https://','http://','mailto:','#')):continue
            target=target.split('#')[0]
            if target:
                links+=1
                if not (path.parent/target).resolve().exists():broken.append((str(path.relative_to(ROOT)),target))
    assert not broken,broken
    files=[p for p in ROOT.rglob('*') if p.is_file() and not any(v in p.parts for v in ['.git','_rebuilt','__pycache__'])]
    leaks=[]
    for path in files:
        if path.suffix in ['.md','.json','.jsonl','.py','.txt','.yml','.cff','.csv','.gz']:
            text=gzip.decompress(path.read_bytes()).decode() if path.suffix=='.gz' else path.read_text()
            if re.search(r'/Users/[A-Za-z0-9_.-]+/|/mnt/ccrsf-static/Analysis/[A-Za-z0-9_.-]+/|gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{25,}|-----BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY',text):
                leaks.append(str(path.relative_to(ROOT)))
    assert not leaks,leaks
    print(json.dumps(dict(status='PASS',manifest_files=verified,source_records=len(source_map),
                          figure_statistic_records=checked,statistical_estimates=15284,certified_mathematical_quantities=14,mathematical_figure_bindings=math_bindings,figures=18,local_links=links,
                          broken_links=0,detected_private_paths_or_secrets=0),indent=2))

if __name__=='__main__':main()
