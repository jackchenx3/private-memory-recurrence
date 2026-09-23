from accepted_model import metrics
from analysis import FREQ

def extract(rec,labels):
 ids=labels[:2];fs={'p0':[],'p1':[],'CARR':[],'R':[]}
 for pop in rec['populations']:
  a,b=[sum(q[2]==fid for q in pop)/32. for fid in ids];car=sum(q[1]!=0 for q in pop)/32.;assert a+b==car;assert all((q[2] in ids)==(q[1]!=0) for q in pop);fs['p0'].append(a);fs['p1'].append(b);fs['CARR'].append(car);fs['R'].append(1-car)
 for k,xs in fs.items():
  for a,b in zip(xs,xs[1:]):assert a!=0 or b==0
 u=dict(rec['utilities']);u['founders']={k:{m:metrics(rec['raw_losses'],fs[k])[m] for m in FREQ} for k in ('p0','p1')}
 return fs,u

def prefix(rec):
 import json
 return json.dumps({k:rec[k][:n] for k,n in [('initial_queries',32),('initial_raw_mismatches',32),('populations',3),('raw_losses',3),('penalized_losses',3),('steps',2),('ground_truth',2)]},sort_keys=True,separators=(',',':'))

def time_series(rows):
 out={s:[] for s in ('HH_AVG','HF_H','HF_F','FF_AVG','R_H','R_F','COMP_H','COMP_F','INTERACTION','MIX_RANK','HH_CARR','HF_CARR','FF_CARR','HH_POP','HF_POP','FF_POP','HH_MINUS_HF_POP','HH_MINUS_FF_POP','HF_MINUS_FF_POP')}
 for i in range(41):
  hh=(rows['HH']['founders']['p0'][i]+rows['HH']['founders']['p1'][i])/2;ff=(rows['FF']['founders']['p0'][i]+rows['FF']['founders']['p1'][i])/2;h=(rows['MIX0']['founders']['p0'][i]+rows['MIX1']['founders']['p1'][i])/2;f=(rows['MIX0']['founders']['p1'][i]+rows['MIX1']['founders']['p0'][i])/2
  q=dict(HH_AVG=hh,HF_H=h,HF_F=f,FF_AVG=ff,R_H=hh-f,R_F=h-ff,COMP_H=hh-h,COMP_F=f-ff,INTERACTION=(hh-f)-(h-ff),MIX_RANK=h-f,HH_CARR=2*hh,HF_CARR=h+f,FF_CARR=2*ff);assert q['INTERACTION']==q['COMP_H']-q['COMP_F']==(q['HH_CARR']+q['FF_CARR'])/2-q['HF_CARR']
  a=rows['HH']['accuracy'][i];b=(rows['MIX0']['accuracy'][i]+rows['MIX1']['accuracy'][i])/2;c=rows['FF']['accuracy'][i];q.update(HH_POP=a,HF_POP=b,FF_POP=c,HH_MINUS_HF_POP=a-b,HH_MINUS_FF_POP=a-c,HF_MINUS_FF_POP=b-c)
  for s,x in q.items():out[s].append(x)
 return out
