"""Explicit starting genotypes; all post-introduction step operators unchanged."""
from accepted_model import Evaluator,metrics,Policy as PrivatePolicy,step as private_step
from accepted_fresh_model import Policy,step as fresh_step
from analysis import MODES

def initial(mode,labels,genotypes):
 assert mode in MODES and sorted(labels)==list(range(32));assert len(genotypes)==32 and all(type(x)==int and 0<=x<2**32 for x in genotypes);carrier=labels[0]
 return [(x,int(i==carrier),i,(x,0,i) if i==carrier else None) for i,x in enumerate(genotypes)]

def step(engine,ev,local,scout,ties):return (fresh_step if isinstance(engine,Policy) else private_step)(engine,ev,local,scout,ties)

def sequence(targets,draws,mode,fresh,genotypes):
 ev=Evaluator();ev.target=targets[0];pop=initial(mode,draws['labels'],genotypes);engine=Policy(mode,pop,fresh) if mode.startswith('NOVEL') else PrivatePolicy(mode,pop);initialscores=[ev.score(p,i) for i,p in enumerate(pop)];iq=ev.records;f=sum(p[1] for p in pop)/32.;raw=[sum(initialscores)/1024.];pen=[raw[0]+engine.cost*f/32.];freq=[f];pops=[pop];steps=[];truth=[]
 for g in range(40):
  old=ev.target;ev.target=targets[g];ev.begin();s=step(engine,ev,draws['local'][g],draws['scout'][g],draws['ties'][g]);s['W_raw']=s['B_raw']-raw[-1];s['W_pen']=s['B_pen']-pen[-1]
  for suffix,ls in [('raw',raw),('pen',pen)]:assert s['L_'+suffix]-ls[-1]==s['W_'+suffix]-s['S_'+suffix];ls.append(s['L_'+suffix])
  steps.append(s);freq.append(s['f_after']);pops.append(engine.pop);truth.append(dict(target=ev.target,actual_change=ev.target!=old))
 for suffix,ls in [('raw',raw),('pen',pen)]:assert ls[0]+sum(s['W_'+suffix]-s['S_'+suffix] for s in steps)==ls[-1]
 assert ev.calls==5152 and all(0<=x<=1 for x in raw);return dict(initial_queries=iq,initial_raw_mismatches=initialscores,populations=pops,raw_losses=raw,penalized_losses=pen,raw_accuracies=[1-x for x in raw],penalized_accuracies=[1-x for x in pen],frequencies=freq,steps=steps,ground_truth=truth,utilities=metrics(raw,freq),query_counts=dict(initial=32,candidates=5120,total=5152,extra_diagnostic_loss_calls=0))
