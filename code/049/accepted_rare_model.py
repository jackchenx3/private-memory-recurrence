"""The sole scientific change is one carrier at stored labels[0]."""
from accepted_model import Evaluator,Policy,step,metrics,offspring
MODES=('ACTIVE_C0','SHAM_C0','ACTIVE_C1','SHAM_C1')
def initial(mode,labels):
 assert mode in MODES and sorted(labels)==list(range(32));founder=labels[0]
 return [(0,int(i==founder),i,(0,0,i) if i==founder else None) for i in range(32)]

def sequence(targets,draws,mode):
 ev=Evaluator();ev.target=targets[0];pop=initial(mode,draws['labels']);engine=Policy(mode,pop);initialscores=[ev.score(p,i) for i,p in enumerate(pop)];iq=ev.records;f=sum(p[1] for p in pop)/32.;raw=[sum(initialscores)/1024.];pen=[raw[0]+engine.cost*f/32.];freq=[f];pops=[pop];steps=[];truth=[]
 for g in range(40):
  old=ev.target;ev.target=targets[g];ev.begin();s=step(engine,ev,draws['local'][g],draws['scout'][g],draws['ties'][g]);s['W_raw']=s['B_raw']-raw[-1];s['W_pen']=s['B_pen']-pen[-1]
  for suffix,ls in [('raw',raw),('pen',pen)]:assert s['L_'+suffix]-ls[-1]==s['W_'+suffix]-s['S_'+suffix];ls.append(s['L_'+suffix])
  steps.append(s);freq.append(s['f_after']);pops.append(engine.pop);truth.append(dict(target=ev.target,actual_change=ev.target!=old))
 for suffix,ls in [('raw',raw),('pen',pen)]:assert ls[0]+sum(s['W_'+suffix]-s['S_'+suffix] for s in steps)==ls[-1]
 assert ev.calls==5152 and all(0<=x<=1 for x in raw);return dict(initial_queries=iq,initial_raw_mismatches=initialscores,populations=pops,raw_losses=raw,penalized_losses=pen,raw_accuracies=[1-x for x in raw],penalized_accuracies=[1-x for x in pen],frequencies=freq,steps=steps,ground_truth=truth,utilities=metrics(raw,freq),query_counts=dict(initial=32,candidates=5120,total=5152,extra_diagnostic_loss_calls=0))
