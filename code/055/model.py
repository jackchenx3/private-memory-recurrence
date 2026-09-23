"""Stage wrappers only; the accepted Policy, step and survival operators are unchanged."""
from accepted_transfer_model import Policy,Evaluator,step,frequencies,utilities,to_uniform

def all_policy(genotypes,policy):
 assert policy in ('H','F') and len(genotypes)==32;k=1 if policy=='H' else 2
 return [(x,k,i,(x,0,i)) for i,x in enumerate(genotypes)]

def rebase(pop):
 assert len(pop)==32
 out=[(q[0],q[1],i,q[3]) for i,q in enumerate(pop)];mapping=[dict(current_slot=i,preparation_founder=q[2],genotype=q[0],policy=q[1],cache=q[3]) for i,q in enumerate(pop)]
 return out,mapping

def substitute(pop,background,slot=None):
 assert background in ('H','F');k=1 if background=='H' else 2;assert all(q[1]==k for q in pop)
 return [(q[0],3-k if i==slot else k,q[2],q[3]) for i,q in enumerate(pop)]

def stage(targets,draws,pop,cost,fresh,survival,absolute_start=0,boundary_previous_target=None):
 assert len(targets)==40 and absolute_start in (0,40) and len(fresh)>=absolute_start+40
 ev=Evaluator();ev.target=targets[0];engine=Policy(cost,pop,fresh);engine.completed=absolute_start;initialscores=[ev.score(q,i) for i,q in enumerate(pop)];iq=ev.records;fs=frequencies(pop);raw=[sum(initialscores)/1024.];pen=[raw[0]+cost*(fs['H']+fs['F'])/32.];freq={r:[x] for r,x in fs.items()};pops=[list(pop)];steps=[];truth=[]
 for g in range(40):
  old=ev.target;ev.target=targets[g];ev.begin();s=step(engine,ev,draws['local'][g],draws['scout'][g],draws['ties'][g],survival[g]);s['W_raw']=s['B_raw']-raw[-1];s['W_pen']=s['B_pen']-pen[-1]
  for suffix,ls in [('raw',raw),('pen',pen)]:assert s['L_'+suffix]-ls[-1]==s['W_'+suffix]-s['S_'+suffix];ls.append(s['L_'+suffix])
  for r in freq:freq[r].append(s['type_frequencies_after'][r])
  steps.append(s);pops.append(engine.pop);truth.append(dict(target=ev.target,actual_change=ev.target!=old,absolute_update=absolute_start+g))
 for suffix,ls in [('raw',raw),('pen',pen)]:assert ls[0]+sum(s['W_'+suffix]-s['S_'+suffix] for s in steps)==ls[-1]
 assert ev.calls==5152 and all(a+b==1 and r==0 for a,b,r in zip(freq['H'],freq['F'],freq['R']))
 return dict(initial_queries=iq,initial_raw_mismatches=initialscores,populations=pops,raw_losses=raw,penalized_losses=pen,raw_accuracies=[1-x for x in raw],penalized_accuracies=[1-x for x in pen],frequencies=freq,steps=steps,ground_truth=truth,utilities=utilities(raw,freq),absolute_start=absolute_start,boundary_previous_target=boundary_previous_target,boundary_current_target=targets[0],boundary_actual_change=None if boundary_previous_target is None else boundary_previous_target!=targets[0],initial_evaluated_on_first_stage_target=True,query_counts=dict(initial=32,candidates=5120,total=5152,extra_diagnostic_loss_calls=0))
