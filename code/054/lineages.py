from accepted_model import metrics
from analysis import FREQ

def extract(rec,rare_id,config):
 rare='H' if config.startswith('LOW') else 'F';fs={r:list(rec['frequencies'][r]) for r in ('H','F','R')};fs['RARE']=[]
 for j,pop in enumerate(rec['populations']):
  a=sum(q[2]==rare_id for q in pop)/32.;assert a==fs[rare][j];assert fs['H'][j]+fs['F'][j]==1 and fs['R'][j]==0;assert all(q[1] in (1,2) and q[3] is not None for q in pop);assert all((q[2]==rare_id)==(q[1]==(1 if rare=='H' else 2)) for q in pop);fs['RARE'].append(a)
 for xs in fs.values():
  for a,b in zip(xs,xs[1:]):assert a!=0 or b==0
 u=dict(rec['utilities']);u['rare_founder']={m:metrics(rec['raw_losses'],fs['RARE'])[m] for m in FREQ};assert u['rare_founder']==u['frequency'][rare]
 return fs,u

def prefix(rec):
 import json
 return json.dumps({k:rec[k][:n] for k,n in [('initial_queries',32),('initial_raw_mismatches',32),('populations',3),('raw_losses',3),('penalized_losses',3),('steps',2),('ground_truth',2)]},sort_keys=True,separators=(',',':'))

def time_series(rows):
 out={}
 for pre in ('LOW','HIGH'):
  for r in ('H','F'):out[pre+'_'+r]=[(a+b)/2 for a,b in zip(rows[pre+'0']['frequency'][r],rows[pre+'1']['frequency'][r])]
  out[pre+'_POP']=[(a+b)/2 for a,b in zip(rows[pre+'0']['accuracy'],rows[pre+'1']['accuracy'])]
 out['LOW_MINUS_HIGH_H']=[a-b for a,b in zip(out['LOW_H'],out['HIGH_H'])];out['LOW_MINUS_HIGH_POP']=[a-b for a,b in zip(out['LOW_POP'],out['HIGH_POP'])]
 assert out['LOW_MINUS_HIGH_H'][0]==-30/32.
 for pre in ('LOW','HIGH'):assert all(a+b==1 for a,b in zip(out[pre+'_H'],out[pre+'_F']))
 return out
