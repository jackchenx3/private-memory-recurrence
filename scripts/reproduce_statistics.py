"""Recompute every published mean/interval from saved blocks; no simulation."""
from pathlib import Path
import argparse, hashlib, json
import numpy as np

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'_rebuilt/statistics_check.json')
    args=parser.parse_args()
    results=[];maximum=0.0;total=0
    for study in json.loads((ROOT/'provenance/STUDIES.json').read_text()):
        directory=ROOT/'results'/study['study']
        rows=[json.loads(line) for line in (directory/'BLOCK_SUMMARIES.jsonl').read_text().splitlines()]
        expected=json.loads((directory/'summary.json').read_text())['values']
        if (directory/'ESTIMATES.json').exists():
            native=json.loads((directory/'ESTIMATES.json').read_text())
            assert set(native)==set(expected)
            for key,value in native.items():
                assert expected[key]==dict(mean=value['mean'],ci95=value['ci95'],zero_classification=value['classification'])
            assert rows==json.loads((directory/'BLOCK_SUMMARIES.json').read_text())
        indices=np.asarray(json.loads((directory/'BOOTSTRAP_INDICES.json').read_text()),dtype=int)
        assert indices.shape==(2000,24) and len(rows)==24
        assert sorted(row['block'] for row in rows)==list(range(24))
        rows=sorted(rows,key=lambda row:row['block'])
        assert all(set(row['values'])==set(expected) for row in rows)
        error=0.0
        for key,item in expected.items():
            values=np.asarray([row['values'][key] for row in rows],dtype=float)
            mean=float(values.mean())
            interval=np.quantile(values[indices].mean(axis=1),[.025,.975],method='linear')
            delta=max(abs(mean-item['mean']),float(np.max(np.abs(interval-np.asarray(item['ci95'])))))
            assert delta<=2e-14,(study['study'],key,delta)
            error=max(error,delta)
            if item['zero_classification']=='structural_zero':
                assert np.all(values==0)
            else:
                classification=('observed_exact_zero' if np.all(values==0) else
                                'positive' if interval[0]>0 else
                                'negative' if interval[1]<0 else 'unresolved')
                assert item['zero_classification']==classification,(study['study'],key,classification)
        total+=len(expected);maximum=max(maximum,error)
        results.append(dict(study=study['study'],intervals=len(expected),maximum_error=error))
    # Verify figure/manuscript statistic records against the public source tables.
    cited=json.loads((ROOT/'provenance/MANUSCRIPT_STATISTICS.json').read_text())
    for record in cited['displayed_statistics']:
        values=json.loads((ROOT/'results'/record['study']/'summary.json').read_text())['values']
        assert record['value']==values[record['key']],record
    for record in cited['fate_records']:
        values=json.loads((ROOT/'results'/record['study']/'TYPE_EVENT_COUNTS.json').read_text())
        assert record['counts']==values[record['key']],record
    for record in cited.get('added_fate_records',[]):
        values=json.loads((ROOT/'results'/record['study']/'FATE_COUNTS.json').read_text())
        assert record['counts']==values[record['key']],record
    for record in json.loads((ROOT/'results/QUOTED_056_057_STATISTICS.json').read_text()):
        native=json.loads((ROOT/'results'/record['study']/'ESTIMATES.json').read_text())
        assert record['value']==native[record['key']],record
    result=dict(status='PASS',studies=results,total_intervals=total,maximum_error=maximum,
                statistic_records=len(cited['displayed_statistics']),
                new_population_paths=0,new_random_draws=0,
                scope='Recomputation from published block aggregates and frozen bootstrap rows. This does not reconstruct raw trajectories or constitute independent scientific replication.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
