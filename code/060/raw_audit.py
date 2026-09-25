"""Independent query/observation/donor/race/state reconstruction of saved block0."""
import math,struct

def canon(x):return tuple(canon(v) for v in x) if isinstance(x,(list,tuple)) else x
def ulp(a,b):return abs(struct.unpack('>Q',struct.pack('>d',a))[0]-struct.unpack('>Q',struct.pack('>d',b))[0])
def truth(x,t):return sum(((x>>i)&1)!=((t>>i)&1) for i in range(32))
def audit_record(rec,targets,draws,initial,fresh,survival,noise,previous_target):
 assert canon(rec['populations'][0])==canon(initial) and len(rec['steps'])==40 and len(rec['populations'])==41
 assert rec['absolute_start']==40 and rec['boundary_previous_target']==previous_target and rec['boundary_current_target']==targets[0] and rec['boundary_actual_change']==(targets[0]!=previous_target)
 uniforms=noise['initial']+[u for row in noise['updates'] for u in row];assert len(uniforms)==5152
 def queries(pool,target,offset):
  out=[]
  for j,q in enumerate(pool):
   h=truth(q[0],target);u=uniforms[offset+j];error=0 if rec['interface']=='EXACT' else 2*u-1
   out.append(dict(query_ordinal=offset+j,candidate_index=j,genotype=q[0],true_loss=h,noise_uniform=u,error=error,observed_score=h+error))
  return out
 iq=queries(initial,targets[0],0);assert iq==rec['initial_queries'];assert [q['true_loss'] for q in iq]==rec['initial_true_losses'];assert [q['observed_score'] for q in iq]==rec['initial_observed_scores'];assert rec['true_losses'][0]==sum(q['true_loss'] for q in iq)/1024.
 for g,s in enumerate(rec['steps']):
  before=rec['populations'][g];pool=s['candidates'];target=targets[g];assert len(pool)==128 and canon(pool[:32])==canon(before)
  qs=queries(pool,target,32+128*g);assert qs==s['query_records'];hs=[q['true_loss'] for q in qs];obs=[q['observed_score'] for q in qs];assert hs==s['candidate_true_losses'] and obs==s['candidate_observed_scores'];assert s['ties']==draws['ties'][g] and s['fresh_probe_masks']==fresh[g]
  for i,parent in enumerate(before):
   x,k,fid,cache=parent;assert k in (1,2);ids=[i,32+i,64+i];win=min(ids,key=lambda j:(obs[j],draws['ties'][g][j],j))
   assert s['donor_choices'][i]==dict(parent=i,candidate_indices=ids,observed_scores=[obs[j] for j in ids],tie_values=[draws['ties'][g][j] for j in ids],winner_index=win,winner_family=('parent','probe','scout')[win//32])
   for group,xx in ((1,cache[0] if k==1 else x^fresh[g][i]),(2,x^draws['scout'][g][i]),(3,pool[win][0]^draws['local'][g][i])):assert canon(pool[group*32+i])==(xx,k,fid,(x,40+g,i))
  us=[(k+1)/(2**52+1) for k in survival[g]['k']];assert us==survival[g]['u']==s['survival_uniforms'] and survival[g]['k']==s['survival_integers'];keys=[-math.log(u)*(2.**score) for u,score in zip(us,obs)];assert all(ulp(a,b)<=2 for a,b in zip(keys,s['race_keys']))
  selected=sorted(range(128),key=lambda j:(keys[j],draws['ties'][g][j],j))[:32];after=[pool[j] for j in selected];assert selected==s['selected_indices'] and canon(after)==canon(s['selected_records'])==canon(rec['populations'][g+1])
  desc=[sum(j%32==i for j in selected) for i in range(32)];assert desc==s['current_descendant_counts'];sources=[dict(parent=j%32,family=('parent','probe','scout','local_child')[j//32]) for j in range(128)];assert sources==s['sources'] and [sources[j] for j in selected]==s['selected_sources']
  assert s['h_retrieval_use']==[q[1]==1 for q in before] and s['f_fresh_use']==[q[1]==2 for q in before]
  for k,role in ((0,'R'),(1,'H'),(2,'F')):
   fb=sum(q[1]==k for q in before)/32.;fa=sum(q[1]==k for q in after)/32.;term=sum((d-1)*(int(q[1]==k)-fb) for d,q in zip(desc,before))/32.
   assert s['type_frequencies_before'][role]==rec['frequencies'][role][g]==fb and s['type_frequencies_after'][role]==rec['frequencies'][role][g+1]==fa and s['type_frequency_terms'][role]==term==fa-fb
  b=sum(hs[:32])/1024.;l=sum(hs[j] for j in selected)/1024.;assert s['B_true']==b and s['L_true']==l and s['S_true']==b-l and s['W_true']==b-rec['true_losses'][g]
  assert rec['true_losses'][g+1]==l and rec['true_accuracies'][g+1]==1-l and s['evaluator_calls']==128
  assert rec['ground_truth'][g]==dict(target=target,actual_change=g>0 and target!=targets[g-1],absolute_update=40+g)
 assert rec['query_counts']==dict(initial=32,candidates=5120,total=5152,extra_diagnostic_loss_calls=0)
 return dict(paths=1,queries=5152,race_keys=5120,updates=40)
