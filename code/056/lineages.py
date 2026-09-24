from accepted_model import metrics
from analysis import FREQ

def extract(rec,labels,config):
 ids=labels[:2];fs={r:list(rec['frequencies'][r]) for r in ('H','F','R')};fs.update(p0=[],p1=[])
 for j,pop in enumerate(rec['populations']):
  for role,fid in zip(('p0','p1'),ids):fs[role].append(sum(q[2]==fid for q in pop)/32.)
  assert fs['H'][j]+fs['F'][j]==1 and fs['R'][j]==0 and all(q[1] in (1,2) and q[3] is not None for q in pop)
 if 'SWITCH' in config:
  i=int(config[-1]);role='F' if config.startswith('H') else 'H';fs['RARE']=list(fs['p'+str(i)]);assert fs['RARE']==fs[role]
  for pop in rec['populations']:assert all((q[2]==ids[i])==(q[1]==(1 if role=='H' else 2)) for q in pop)
 else:assert fs[config[0]]==[1]*41
 for xs in fs.values():
  for a,b in zip(xs,xs[1:]):assert a!=0 or b==0
 u=dict(rec['utilities']);u['founders']={r:{m:metrics(rec['raw_losses'],fs[r])[m] for m in FREQ} for r in ('p0','p1')}
 return fs,u

def time_series(rows):
 out={}
 for bg in ('F','H'):
  a,b=rows[bg+'_SWITCH0'],rows[bg+'_SWITCH1'];stay=rows[bg+'_STAY']
  out[bg+'_BG_SWITCH']=[(x+y)/2 for x,y in zip(a['frequency']['p0'],b['frequency']['p1'])];out[bg+'_BG_STAY']=[(x+y)/2 for x,y in zip(stay['frequency']['p0'],stay['frequency']['p1'])];out[bg+'_BG_SWITCH_POP']=[(x+y)/2 for x,y in zip(a['accuracy'],b['accuracy'])];out[bg+'_BG_STAY_POP']=list(stay['accuracy'])
  for suffix in ('','_POP'):out[bg+'_BG_EFFECT'+suffix]=[x-y for x,y in zip(out[bg+'_BG_SWITCH'+suffix],out[bg+'_BG_STAY'+suffix])]
  assert out[bg+'_BG_SWITCH'][0]==out[bg+'_BG_STAY'][0]==1/32 and out[bg+'_BG_EFFECT'][0]==out[bg+'_BG_EFFECT_POP'][0]==0
 return out
