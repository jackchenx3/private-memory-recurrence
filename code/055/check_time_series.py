"""Saved-output arithmetic only, without diagnostic scoring or draws."""
import pathlib,json,gzip
from accepted_model import metrics
from analysis import FREQ,RAW
P=pathlib.Path(__file__).resolve().parent

def main():
 rows={(r['block'],r['replicate']):r['values'] for r in map(json.loads,(P/'PAIRED_METRICS.jsonl').read_text().splitlines())};n=0;err=0
 with gzip.open(P/'TIME_SERIES_IDENTITIES.jsonl.gz','rt') as src:
  for line in src:
   q=json.loads(line);v=q['values'];assert len(v)==12 and all(len(xs)==41 for xs in v.values())
   for bg in ('F','H'):
    assert v[bg+'_BG_SWITCH'][0]==v[bg+'_BG_STAY'][0]==1/32 and v[bg+'_BG_EFFECT'][0]==v[bg+'_BG_EFFECT_POP'][0]==0
    for suffix in ('','_POP'):
     for i in range(41):assert v[bg+'_BG_EFFECT'+suffix][i]==v[bg+'_BG_SWITCH'+suffix][i]-v[bg+'_BG_STAY'+suffix][i]
   for s,xs in v.items():
    stats=metrics([1-x for x in xs],[0]*41) if s.endswith('POP') else metrics([0]*41,xs);ms=[m for m in RAW if m!='MLOSS'] if s.endswith('POP') else FREQ
    for m in ms:
     d=abs(stats[m]-rows[q['block'],q['replicate']][q['geometry']+'|C0|'+s+'|'+m]);err=max(err,d);assert d<2e-15
   n+=1
 assert n==576;(P/'TIME_SERIES_CHECK.json').write_text(json.dumps(dict(status='PASS',rows=n,series_per_row=12,states_per_series=41,max_metric_roundoff=err,matched_effect_state_identities_exact=True,extra_objective_calls=0),indent=2)+'\n')
if __name__=='__main__':main()
