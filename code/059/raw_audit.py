"""Recorded-score and state reconstruction only; never executes a population trajectory."""
import math,struct

def canon(x):return tuple(canon(v) for v in x) if isinstance(x,(list,tuple)) else x
def ulp(a,b):return abs(struct.unpack('>Q',struct.pack('>d',a))[0]-struct.unpack('>Q',struct.pack('>d',b))[0])
def score(x,t):return sum(((x>>i)&1)!=((t>>i)&1) for i in range(32))
def audit_record(rec,targets,draws,initial,fresh,survival,previous_target):
 assert canon(rec['populations'][0])==canon(initial) and len(rec['populations'])==41 and len(rec['steps'])==40
 assert rec['absolute_start']==40 and rec['boundary_previous_target']==previous_target and rec['boundary_current_target']==targets[0] and rec['boundary_actual_change']==(targets[0]!=previous_target)
 def qs(pool,target):return [dict(candidate_index=j,genotype=p[0],raw_mismatch=score(p[0],target)) for j,p in enumerate(pool)]
 iq=qs(initial,targets[0]);assert iq==rec['initial_queries'];assert [q['raw_mismatch'] for q in iq]==rec['initial_raw_mismatches'];assert rec['raw_losses'][0]==sum(q['raw_mismatch'] for q in iq)/1024.
 assert rec['query_counts']==dict(initial=32,candidates=5120,total=5152,extra_diagnostic_loss_calls=0)
 events=[]
 for g,s in enumerate(rec['steps']):
  before=rec['populations'][g];pool=s['candidates'];target=targets[g];assert canon(pool[:32])==canon(before) and len(pool)==128
  qr=qs(pool,target);raw=[q['raw_mismatch'] for q in qr];assert qr==s['query_records'] and raw==s['candidate_raw_mismatches']==s['candidate_penalized_mismatches']
  assert s['ties']==draws['ties'][g] and s['fresh_probe_masks']==fresh[g]
  for i,parent in enumerate(before):
   x,k,fid,cache=parent;assert k in (1,2)
   ids=[i,32+i,64+i];win=min(ids,key=lambda j:(raw[j],draws['ties'][g][j],j))
   assert s['donor_choices'][i]==dict(parent=i,candidate_indices=ids,raw_mismatches=[raw[j] for j in ids],tie_values=[draws['ties'][g][j] for j in ids],winner_index=win,winner_family=('parent','probe','scout')[win//32])
   for group,xx in ((1,cache[0] if k==1 else x^fresh[g][i]),(2,x^draws['scout'][g][i]),(3,pool[win][0]^draws['local'][g][i])):
    assert canon(pool[group*32+i])==(xx,k,fid,(x,40+g,i))
  us=[(k+1)/(2**52+1) for k in survival[g]['k']];assert us==survival[g]['u']==s['survival_uniforms'] and survival[g]['k']==s['survival_integers'];keys=[-math.log(u)*(2.**v) for u,v in zip(us,raw)];assert all(ulp(a,b)<=2 for a,b in zip(keys,s['race_keys']))
  ids=sorted(range(128),key=lambda j:(keys[j],draws['ties'][g][j],j))[:32];selected=[pool[j] for j in ids];assert ids==s['selected_indices'] and canon(selected)==canon(s['selected_records'])
  carried=selected
  if rec['arm']=='PULSE' and g==0:
   carried=[(p[0],1,p[2],p[3]) for p in selected];events.append(dict(after_update=1,before_update=2,absolute_completed=41,pre_reversion_population=selected,post_reversion_population=carried,changed_indices=[i for i,p in enumerate(selected) if p[1]==2]))
  assert canon(carried)==canon(rec['populations'][g+1])
  if rec['arm']=='PULSE':assert all(q[1]==1 for q in carried)
  src=[dict(parent=j%32,family=('parent','probe','scout','local_child')[j//32]) for j in range(128)];assert src==s['sources'] and s['selected_sources']==[src[j] for j in ids]
  desc=[sum(j%32==i for j in ids) for i in range(32)];assert s['current_descendant_counts']==desc
  assert s['h_retrieval_use']==s['probe_access']==[q[1]==1 for q in before] and s['f_fresh_use']==[q[1]==2 for q in before]
  for k,role in ((0,'R'),(1,'H'),(2,'F')):
   fb=sum(q[1]==k for q in before)/32.;fs=sum(q[1]==k for q in selected)/32.;fc=sum(q[1]==k for q in carried)/32.
   assert s['type_frequencies_before'][role]==rec['expression_carried'][role][g]==fb
   assert s['type_frequencies_after'][role]==rec['expression_selected'][role][g+1]==fs
   assert rec['expression_carried'][role][g+1]==fc and rec['intervention_frequency_terms'][g][role]==fc-fs
   term=sum((d-1)*(int(q[1]==k)-fb) for d,q in zip(desc,before))/32.;assert s['type_frequency_terms'][role]==term==fs-fb
  b=sum(raw[:32])/1024.;l=sum(raw[j] for j in ids)/1024.
  for suffix in ('raw','pen'):assert s['B_'+suffix]==b and s['L_'+suffix]==l and s['S_'+suffix]==b-l and s['W_'+suffix]==b-rec['raw_losses'][g]
  assert rec['raw_losses'][g+1]==l and rec['raw_accuracies'][g+1]==1-l and s['evaluator_calls']==128
  assert rec['ground_truth'][g]==dict(target=target,actual_change=g>0 and target!=targets[g-1],absolute_update=40+g)
 # Compare nested lists/tuples without relaxing any values or ordering.
 import json
 assert json.loads(json.dumps(events))==json.loads(json.dumps(rec['reversion_events']))
 return dict(paths=1,recorded_scores=5152,race_keys=5120,updates=40)
