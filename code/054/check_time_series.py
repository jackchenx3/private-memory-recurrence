"""Saved-output arithmetic audit; no scoring, propagation or draws."""
import pathlib,json,gzip
from accepted_model import metrics
from analysis import FREQ,RAW
P=pathlib.Path(__file__).resolve().parent

def main():
 rows={(r['block'],r['replicate']):r['values'] for r in map(json.loads,(P/'PAIRED_METRICS.jsonl').read_text().splitlines())};n=0;err=0
 with gzip.open(P/'TIME_SERIES_IDENTITIES.jsonl.gz','rt') as src:
  for line in src:
   q=json.loads(line);v=q['values'];assert len(v)==8 and all(len(xs)==41 for xs in v.values());assert v['LOW_MINUS_HIGH_H'][0]==-30/32
   for i in range(41):
    assert v['LOW_H'][i]+v['LOW_F'][i]==v['HIGH_H'][i]+v['HIGH_F'][i]==1
    assert v['LOW_MINUS_HIGH_H'][i]==v['LOW_H'][i]-v['HIGH_H'][i];assert v['LOW_MINUS_HIGH_POP'][i]==v['LOW_POP'][i]-v['HIGH_POP'][i]
   for s,xs in v.items():
    if s.endswith('POP'):
     stats=metrics([1-x for x in xs],[0]*41);ms=[m for m in RAW if m!='MLOSS']
    else:stats=metrics([0]*41,xs);ms=FREQ
    for m in ms:
     d=abs(stats[m]-rows[q['block'],q['replicate']][q['geometry']+'|C0|'+s+'|'+m]);err=max(err,d);assert d<2e-15
   n+=1
 assert n==576;(P/'TIME_SERIES_CHECK.json').write_text(json.dumps(dict(status='PASS',rows=n,series_per_row=8,states_per_series=41,max_metric_roundoff=err,complement_and_difference_state_identities_exact=True,extra_objective_calls=0),indent=2)+'\n')
if __name__=='__main__':main()
