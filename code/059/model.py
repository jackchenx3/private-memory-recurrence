"""Explicit one-update policy pulse; accepted candidate and selection machinery unchanged."""
from accepted_transfer_model import Policy,Evaluator,step,frequencies

def substitute(pop,slot):
 assert len(pop)==32 and all(q[1]==1 for q in pop)
 return [(q[0],2 if i==slot else 1,q[2],q[3]) for i,q in enumerate(pop)]

def revert_to_H(pop):
 assert all(q[1] in (1,2) for q in pop)
 return [(q[0],1,q[2],q[3]) for q in pop]

def stage(targets,draws,pop,fresh,survival,arm,previous_target):
 assert arm in ('STAY','PULSE','CONT') and len(targets)==40 and len(fresh)==40 and len(survival)==40
 # An explicitly unused zero prefix supplies the accepted absolute indexing convention.
 # Only entries40..79 are consumed; all are new059 transfer masks.
 indexed_fresh=[[0]*32 for _ in range(40)]+fresh
 engine=Policy(0,pop,indexed_fresh);engine.completed=40;ev=Evaluator();ev.target=targets[0]
 initialscores=[ev.score(q,i) for i,q in enumerate(pop)];queries=ev.records
 raw=[sum(initialscores)/1024.];pops=[list(pop)];steps=[];truth=[];events=[]
 carried={k:[v] for k,v in frequencies(pop).items()};selected={k:[v] for k,v in frequencies(pop).items()};forced=[]
 for g in range(40):
  old=ev.target;ev.target=targets[g];ev.begin();s=step(engine,ev,draws['local'][g],draws['scout'][g],draws['ties'][g],survival[g]);s['W_raw']=s['B_raw']-raw[-1];s['W_pen']=s['W_raw'];raw.append(s['L_raw'])
  selected_pop=list(engine.pop);before=frequencies(selected_pop)
  if arm=='PULSE' and g==0:
   after=revert_to_H(selected_pop);events.append(dict(after_update=1,before_update=2,absolute_completed=41,pre_reversion_population=selected_pop,post_reversion_population=after,changed_indices=[i for i,q in enumerate(selected_pop) if q[1]==2]));engine.pop=after
  carry=frequencies(engine.pop);delta={k:carry[k]-before[k] for k in carry};forced.append(delta)
  for k in carry:
   assert carry[k]-carried[k][-1]==s['type_frequency_terms'][k]+delta[k]
   selected[k].append(before[k]);carried[k].append(carry[k])
  if arm=='PULSE':assert carry['F']==0 and carry['H']==1
  assert raw[-1]-raw[-2]==s['W_raw']-s['S_raw']
  pops.append(list(engine.pop));steps.append(s);truth.append(dict(target=ev.target,actual_change=ev.target!=old,absolute_update=40+g))
 assert ev.calls==5152 and engine.completed==80
 return dict(arm=arm,absolute_start=40,boundary_previous_target=previous_target,boundary_current_target=targets[0],boundary_actual_change=previous_target!=targets[0],initial_queries=queries,initial_raw_mismatches=initialscores,populations=pops,steps=steps,ground_truth=truth,raw_losses=raw,raw_accuracies=[1-x for x in raw],expression_selected=selected,expression_carried=carried,intervention_frequency_terms=forced,reversion_events=events,query_counts=dict(initial=32,candidates=5120,total=5152,extra_diagnostic_loss_calls=0),population_record_convention='Initial state, then post-selection and post-scheduled-intervention states. steps.selected_records preserves pre-intervention selection.',expression_convention='Selection and scheduled label changes are separate; focal founders retain IDs.')
