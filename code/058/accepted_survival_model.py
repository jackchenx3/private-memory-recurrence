"""Only global survivor choice changes; accepted candidate operators unchanged."""
import math
from accepted_model import Evaluator,metrics,Policy as PrivatePolicy
from accepted_fresh_model import Policy
from accepted_resident_model import initial

def to_uniform(k):
 assert type(k)==int and 0<=k<2**52
 u=(k+1)/(2**52+1);assert 0<u<1
 return u

def race_select(scores,ties,ks,us):
 assert len(scores)==len(ties)==len(ks)==len(us)==128 and all(type(s)==int and 0<=s<=33 for s in scores)
 assert all(u==to_uniform(k) for k,u in zip(ks,us))
 keys=[-math.log(u)*float(1<<s) for u,s in zip(us,scores)];assert all(math.isfinite(k) and k>0 for k in keys)
 selected=sorted(range(128),key=lambda j:(keys[j],ties[j],j))[:32];assert len(set(selected))==32
 return selected,keys

def core_step(engine,ev,local,scout,ties,survival):
 assert len(local)==len(scout)==32 and len(ties)==128
 before=engine.pop;start=ev.calls;pool=list(before);raw=[ev.score(p,i) for i,p in enumerate(before)]
 for group in (engine.probes(),engine.scouts(scout)):
  for p in group:j=len(pool);pool.append(p);raw.append(ev.score(p,j))
 children,donors=engine.children(pool,raw,ties,local)
 for p in children:j=len(pool);pool.append(p);raw.append(ev.score(p,j))
 penalized=[h+engine.cost*p[1] for h,p in zip(raw,pool)];selected,keys=race_select(penalized,ties,survival['k'],survival['u']);out=[pool[j] for j in selected];desc=[0]*32
 for j in selected:desc[j%32]+=1
 f=sum(p[1] for p in before)/32.;newf=sum(p[1] for p in out)/32.;term=sum((n-1)*(p[1]-f) for n,p in zip(desc,before))/32.;assert sum(desc)==32 and newf-f==term
 B=sum(raw[:32])/1024.;L=sum(raw[j] for j in selected)/1024.;BP=sum(penalized[:32])/1024.;LP=sum(penalized[j] for j in selected)/1024.;S=B-L;SP=BP-LP;assert SP==S+engine.cost*(f-newf)/32.;assert ev.calls-start==128
 assert all(pool[j][1:3]==before[j%32][1:3] for j in range(128));assert set(p[1] for p in out)<=set(p[1] for p in before)
 sources=[dict(parent=j%32,family=('parent','probe','scout','local_child')[j//32]) for j in range(128)]
 engine.completed+=1;engine.pop=out
 return dict(survival_integers=survival['k'],survival_uniforms=survival['u'],race_keys=keys,survival_weight_definition='2**(-candidate_penalized_mismatch)',candidates=pool,candidate_raw_mismatches=raw,candidate_penalized_mismatches=penalized,ties=list(ties),query_records=ev.records,donor_choices=donors,selected_indices=selected,selected_records=out,sources=sources,selected_sources=[sources[j] for j in selected],current_descendant_counts=desc,f_before=f,f_after=newf,frequency_term=term,persistent_cache_count=sum(p[1] for p in out),B_raw=B,L_raw=L,S_raw=S,B_pen=BP,L_pen=LP,S_pen=SP,evaluator_calls=128,probe_access=[bool(engine.active and p[1]) for p in before])


def step(engine,ev,local,scout,ties,survival):
 fresh=isinstance(engine,Policy)
 if fresh:used=[bool(p[1]) for p in engine.pop];masks=list(engine.fresh[engine.completed])
 s=core_step(engine,ev,local,scout,ties,survival)
 if fresh:s['fresh_probe_use']=used;s['fresh_probe_masks']=masks;assert not any(s['probe_access'])
 return s

def sequence(targets,draws,mode,fresh,genotypes,survival):
 ev=Evaluator();ev.target=targets[0];pop=initial(mode,draws['labels'],genotypes);engine=Policy(mode,pop,fresh) if mode.startswith('NOVEL') else PrivatePolicy(mode,pop);initialscores=[ev.score(p,i) for i,p in enumerate(pop)];iq=ev.records;f=sum(p[1] for p in pop)/32.;raw=[sum(initialscores)/1024.];pen=[raw[0]+engine.cost*f/32.];freq=[f];pops=[pop];steps=[];truth=[]
 for g in range(40):
  old=ev.target;ev.target=targets[g];ev.begin();s=step(engine,ev,draws['local'][g],draws['scout'][g],draws['ties'][g],survival[g]);s['W_raw']=s['B_raw']-raw[-1];s['W_pen']=s['B_pen']-pen[-1]
  for suffix,ls in [('raw',raw),('pen',pen)]:assert s['L_'+suffix]-ls[-1]==s['W_'+suffix]-s['S_'+suffix];ls.append(s['L_'+suffix])
  steps.append(s);freq.append(s['f_after']);pops.append(engine.pop);truth.append(dict(target=ev.target,actual_change=ev.target!=old))
 for suffix,ls in [('raw',raw),('pen',pen)]:assert ls[0]+sum(s['W_'+suffix]-s['S_'+suffix] for s in steps)==ls[-1]
 assert ev.calls==5152 and all(0<=x<=1 for x in raw);return dict(initial_queries=iq,initial_raw_mismatches=initialscores,populations=pops,raw_losses=raw,penalized_losses=pen,raw_accuracies=[1-x for x in raw],penalized_accuracies=[1-x for x in pen],frequencies=freq,steps=steps,ground_truth=truth,utilities=metrics(raw,freq),query_counts=dict(initial=32,candidates=5120,total=5152,extra_diagnostic_loss_calls=0))
