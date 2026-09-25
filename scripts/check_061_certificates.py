"""Check14 saved mathematical records without transition reconstruction or a solve."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal
import argparse,gzip,hashlib,json
from stationary061_audit_core import D,ALPHA,KERNELS,exact_certificate,outcomes

ROOT=Path(__file__).resolve().parents[1]
def read(p):
    if p.suffix=='.gz':
        with gzip.open(p,'rt') as f:return json.load(f)
    return json.loads(p.read_text())
def rational(x):return F(int(x['numerator']),int(x['denominator']))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'_rebuilt/061_CERTIFICATES_CHECK.json');args=ap.parse_args()
    vectors={};errors={}
    for kernel in KERNELS:
        m=read(ROOT/'results/061/matrices'/f'{kernel}.json.gz');v=read(ROOT/'results/061/vectors'/f'{kernel}.json.gz')
        assert m['denominator']==D and v['status']=='COMPUTED'
        k=[int(x) for x in v['k']];c=exact_certificate(m['numerators'],k)
        stored=v['certificate'];assert int(stored['K'])==c['K'] and int(stored['R'])==c['R']
        assert rational(stored['residual'])==c['r'] and rational(stored['total_variation_bound'])==c['E']
        assert rational(stored['alpha'])==ALPHA and c['r']<=F(1,10**30) and stored['criterion_pass']
        vectors[kernel]=k;errors[kernel]=c['E']
    calculated=outcomes(vectors,errors);saved=read(ROOT/'results/061/OUTCOMES.json')
    assert set(saved)==set(calculated) and len(saved)==14
    quoted=read(ROOT/'results/QUOTED_061_STATISTICS.json');assert quoted['records']==saved
    for key,vals in calculated.items():
        q=saved[key];assert tuple(rational(q[n]) for n in ('center','lower','upper'))==vals
        assert q['status']=='CERTIFIED'
        assert q['sign']==('positive' if vals[1]>0 else 'negative' if vals[2]<0 else 'contains_zero')
        for scale,lo,hi in ((1,'lower_decimal','upper_decimal'),(100,'lower_percentage_points','upper_percentage_points')):
            assert F(Decimal(q[lo]))<=scale*vals[1] and F(Decimal(q[hi]))>=scale*vals[2]
    figure=read(ROOT/'figures/FIGURE_061_DATA.json');assert figure['source_sha256']==hashlib.sha256((ROOT/figure['source']).read_bytes()).hexdigest()
    count=0
    for binding in figure['bindings']:
        q=saved[binding['key']]
        for kind in ('center','lower','upper'):
            if kind in binding:assert rational(binding[kind])==rational(q[kind]);count+=1
    assert len(figure['bindings'])==11 and count==27
    # Decimal display rounding must occur in manuscript/supplement and preserve every table row.
    manuscript=(ROOT/'paper/MANUSCRIPT.md').read_text();supplement=(ROOT/'paper/SUPPLEMENT.md').read_text()
    for key,q in saved.items():assert f"{float(q['center_percentage_points']):.9f}" in supplement
    for key in ('ACTIVE_HALF_MINUS_ZERO|H','ACTIVE_MINUS_NEUTRAL_ZERO|U','ACTIVE_MINUS_NEUTRAL_HALF|U'):
        assert f"{abs(float(saved[key]['center_percentage_points'])):.9f}" in manuscript
    result={'status':'PASS','kind':'certified_stationary_mathematics','certificates':4,'records':14,'quoted_records':14,'figure_records':11,'figure_numeric_bindings':count,'statistical_estimates_added':0,'raw_transition_rows_reconstructed':0,'stationary_solves':0,'population_paths':0,'scope':'Saved rational matrix/vector residual and outcome verification; original focused transition audit is retained, not repeated.'}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
