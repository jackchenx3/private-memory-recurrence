"""Independent reconstruction of recorded scores/operators; no new trajectory."""
import math,struct

def reference_loss(x,t,objective):
 matches=[int((x>>i)&1 == (t>>i)&1) for i in range(32)]
 if objective=='HAM':return 32-sum(matches)
 assert objective=='TRAP4'
 return sum(0 if sum(matches[j:j+4])==4 else 1+sum(matches[j:j+4]) for j in range(0,32,4))

def ulp(a,b):return abs(struct.unpack('>Q',struct.pack('>d',a))[0]-struct.unpack('>Q',struct.pack('>d',b))[0])
def canon(x):
 if isinstance(x,(list,tuple)):return tuple(canon(v) for v in x)
 return x

def audit_record(rec,draws,targets,initial,fresh=None,survival=None,absolute_start=0,expected_updates=40):
 obj=rec['objective'];n=expected_updates
 assert len(rec['steps'])==n and canon(rec['populations'][0])==canon(initial)
 def queries(records,pool,target):
  want=[dict(candidate_index=j,genotype=q[0],raw_mismatch=reference_loss(q[0],target,obj),objective=obj) for j,q in enumerate(pool)]
  assert records==want
  return [q['raw_mismatch'] for q in want]
 vals=queries(rec['initial_queries'],initial,targets[0]);assert vals==rec['initial_raw_mismatches'];assert rec['raw_losses'][0]==sum(vals)/1024.
 scores=32;clocks=0
 for g,s in enumerate(rec['steps']):
  before=rec['populations'][g];pool=s['candidates'];t=targets[g];assert len(pool)==128 and canon(pool[:32])==canon(before)
  assert rec['ground_truth'][g]['target']==t and rec['ground_truth'][g]['actual_change']==(g>0 and t!=targets[g-1])
  raw=queries(s['query_records'],pool,t);scores+=128
  assert raw==s['candidate_raw_mismatches']==s['candidate_penalized_mismatches']
  assert s['ties']==draws['ties'][g]
  for i,parent in enumerate(before):
   x,k,fid,cache=parent
   probe=x if survival is None else cache[0] if k==1 else x^fresh[absolute_start+g][i]
   scout=x^draws['scout'][g][i]
   ids=[i,32+i,64+i];win=min(ids,key=lambda j:(raw[j],s['ties'][j],j))
   donor=s['donor_choices'][i];assert donor==dict(parent=i,candidate_indices=ids,raw_mismatches=[raw[j] for j in ids],tie_values=[s['ties'][j] for j in ids],winner_index=win,winner_family=('parent','probe','scout')[win//32])
   child=pool[win][0]^draws['local'][g][i]
   newcache=(x,absolute_start+g,i) if k else None
   for group,genotype in ((1,probe),(2,scout),(3,child)):
    assert canon(pool[group*32+i])==(genotype,k,fid,newcache)
  if survival is None:
   selected=sorted(range(128),key=lambda j:(raw[j],s['ties'][j],j))[:32]
   assert not any(s['probe_access']) and s['S_raw']>=0
  else:
   ss=survival[g];us=[(v+1)/(2**52+1) for v in ss['k']];assert us==ss['u']==s['survival_uniforms'];assert ss['k']==s['survival_integers']
   keys=[-math.log(u)*(2.**raw[j]) for j,u in enumerate(us)]
   assert all(ulp(a,b)<=2 for a,b in zip(keys,s['race_keys']));clocks+=128
   selected=sorted(range(128),key=lambda j:(keys[j],s['ties'][j],j))[:32]
   assert s['fresh_probe_masks']==fresh[absolute_start+g]
   assert s['h_retrieval_use']==s['probe_access']==[p[1]==1 for p in before]
   assert s['f_fresh_use']==[p[1]==2 for p in before]
  assert selected==s['selected_indices'] and len(set(selected))==32
  after=[pool[j] for j in selected];assert canon(after)==canon(s['selected_records'])==canon(rec['populations'][g+1])
  sources=[dict(parent=j%32,family=('parent','probe','scout','local_child')[j//32]) for j in range(128)]
  assert s['sources']==sources and s['selected_sources']==[sources[j] for j in selected]
  desc=[sum(j%32==i for j in selected) for i in range(32)];assert s['current_descendant_counts']==desc
  b=sum(raw[:32])/1024.;l=sum(raw[j] for j in selected)/1024.
  for suffix in ('raw','pen'):
   assert s['B_'+suffix]==b and s['L_'+suffix]==l and s['S_'+suffix]==b-l
   assert rec[('raw_losses' if suffix=='raw' else 'penalized_losses')][g+1]==l
   assert s['W_'+suffix]==b-rec['raw_losses'][g]
  assert rec['raw_accuracies'][g+1]==rec['penalized_accuracies'][g+1]==1-l
  if survival is not None:
   for k,role in ((0,'R'),(1,'H'),(2,'F')):
    fb=sum(p[1]==k for p in before)/32.;fa=sum(p[1]==k for p in after)/32.
    assert s['type_frequencies_before'][role]==rec['frequencies'][role][g]==fb
    assert s['type_frequencies_after'][role]==rec['frequencies'][role][g+1]==fa
    assert s['type_frequency_terms'][role]==sum((d-1)*(int(p[1]==k)-fb) for d,p in zip(desc,before))/32.==fa-fb
  assert s['evaluator_calls']==128
 assert rec['query_counts']['total']==32+128*n
 return dict(scores=scores,clocks=clocks,paths=1)
