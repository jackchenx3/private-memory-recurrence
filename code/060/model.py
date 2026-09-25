"""Explicit measurement and real-score survival adapter; immutable accepted Policy."""
import math
from accepted_model import hamming
from accepted_transfer_model import Policy,frequencies
from accepted_survival_model import to_uniform
from accepted_stage057 import substitute

class Evaluator:
 def __init__(self,interface,noise):
  assert interface in ('EXACT','NOISY') and len(noise['initial'])==32 and len(noise['updates'])==40 and all(len(row)==128 for row in noise['updates'])
  self.interface=interface;self.noise=list(noise['initial'])+[u for row in noise['updates'] for u in row];assert len(self.noise)==5152 and all(0<=u<1 for u in self.noise);self.calls=0;self.records=[]
 def begin(self):self.records=[]
 def score(self,record,index):
  assert type(record[0])==int and 0<=record[0]<2**32
  ordinal=self.calls;expected=ordinal if ordinal<32 else (ordinal-32)%128;assert index==expected
  h=hamming(record[0],self.target);u=self.noise[ordinal];error=0 if self.interface=='EXACT' else 2*u-1;returned=h+error
  self.records.append(dict(query_ordinal=ordinal,candidate_index=index,genotype=record[0],true_loss=h,noise_uniform=u,error=error,observed_score=returned));self.calls+=1
  return returned

def race_select_real(scores,ties,ks,us):
 assert len(scores)==len(ties)==len(ks)==len(us)==128 and all(math.isfinite(x) and -1<=x<=33 for x in scores)
 assert all(u==to_uniform(k) for k,u in zip(ks,us))
 keys=[-math.log(u)*(2.0**score) for u,score in zip(us,scores)];assert all(math.isfinite(x) and x>0 for x in keys)
 return sorted(range(128),key=lambda j:(keys[j],ties[j],j))[:32],keys

def step(engine,ev,local,scout,ties,survival):
 assert engine.cost==0 and len(local)==len(scout)==32 and len(ties)==128 and 40<=engine.completed<80
 before=engine.pop;start=ev.calls;pool=list(before);observed=[ev.score(q,i) for i,q in enumerate(before)]
 for group in (engine.probes(),engine.scouts(scout)):
  for q in group:j=len(pool);pool.append(q);observed.append(ev.score(q,j))
 children,donors=engine.children(pool,observed,ties,local)
 for d in donors:d['observed_scores']=d.pop('raw_mismatches')
 for q in children:j=len(pool);pool.append(q);observed.append(ev.score(q,j))
 selected,keys=race_select_real(observed,ties,survival['k'],survival['u']);after=[pool[j] for j in selected]
 # Truth becomes a diagnostic only after all decisions are made; no reevaluation.
 true=[q['true_loss'] for q in ev.records];assert len(true)==128 and ev.calls-start==128
 desc=[sum(j%32==i for j in selected) for i in range(32)];tb=frequencies(before);ta=frequencies(after);terms={r:sum((d-1)*(int(p[1]==k)-tb[r]) for d,p in zip(desc,before))/32. for k,r in ((0,'R'),(1,'H'),(2,'F'))}
 for r in tb:assert ta[r]-tb[r]==terms[r] and (tb[r]!=0 or ta[r]==0)
 assert all(pool[j][1:3]==before[j%32][1:3] for j in range(128));assert set(p[1] for p in after)<=set(p[1] for p in before)
 sources=[dict(parent=j%32,family=('parent','probe','scout','local_child')[j//32]) for j in range(128)]
 B=sum(true[:32])/1024.;L=sum(true[j] for j in selected)/1024.;engine.completed+=1;engine.pop=after
 return dict(candidates=pool,candidate_true_losses=true,candidate_observed_scores=observed,query_records=ev.records,donor_choices=donors,ties=list(ties),survival_integers=survival['k'],survival_uniforms=survival['u'],race_keys=keys,survival_weight_definition='2**(-observed_score)',selected_indices=selected,selected_records=after,sources=sources,selected_sources=[sources[j] for j in selected],current_descendant_counts=desc,type_frequencies_before=tb,type_frequencies_after=ta,type_frequency_terms=terms,h_retrieval_use=[p[1]==1 for p in before],f_fresh_use=[p[1]==2 for p in before],fresh_probe_masks=list(engine.fresh[engine.completed-1]),B_true=B,L_true=L,S_true=B-L,evaluator_calls=128)

def stage(targets,draws,pop,fresh,survival,noise,interface,previous_target):
 assert len(targets)==len(fresh)==len(survival)==40
 engine=Policy(0,pop,[[0]*32 for _ in range(40)]+fresh);engine.completed=40;ev=Evaluator(interface,noise);ev.target=targets[0]
 initial_observed=[ev.score(q,i) for i,q in enumerate(pop)];initial_queries=ev.records;initial_true=[q['true_loss'] for q in initial_queries];loss=[sum(initial_true)/1024.];pops=[list(pop)];steps=[];truth=[];freq={k:[v] for k,v in frequencies(pop).items()}
 for g in range(40):
  old=ev.target;ev.target=targets[g];ev.begin();assert engine.completed==40+g
  s=step(engine,ev,draws['local'][g],draws['scout'][g],draws['ties'][g],survival[g]);s['W_true']=s['B_true']-loss[-1];assert s['L_true']-loss[-1]==s['W_true']-s['S_true'];loss.append(s['L_true'])
  for k in freq:freq[k].append(s['type_frequencies_after'][k])
  steps.append(s);pops.append(list(engine.pop));truth.append(dict(target=ev.target,actual_change=ev.target!=old,absolute_update=40+g))
 assert ev.calls==5152 and loss[0]+sum(s['W_true']-s['S_true'] for s in steps)==loss[-1]
 return dict(interface=interface,absolute_start=40,boundary_previous_target=previous_target,boundary_current_target=targets[0],boundary_actual_change=targets[0]!=previous_target,initial_queries=initial_queries,initial_true_losses=initial_true,initial_observed_scores=initial_observed,populations=pops,steps=steps,ground_truth=truth,true_losses=loss,true_accuracies=[1-x for x in loss],frequencies=freq,query_counts=dict(initial=32,candidates=5120,total=5152,extra_diagnostic_loss_calls=0))
