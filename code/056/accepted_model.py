"""Abstract private-cache inheritance. No RNG or target access in Policy."""
MODES=('ACTIVE_C0','SHAM_C0','ACTIVE_C1','SHAM_C1','PURE_M','PURE_C')
def hamming(x,t):return bin(x^t).count('1')
def properties(mode):
 assert mode in MODES
 return mode.startswith('ACTIVE') or mode=='PURE_M',int(mode.endswith('C1'))
def initial(mode,labels):
 assert sorted(labels)==list(range(32));marked=set(labels[:16]);out=[]
 for i in range(32):
  m=int(mode=='PURE_M' or mode!='PURE_C' and i in marked);out.append((0,m,i,(0,0,i) if m else None))
 return out

def offspring(parent,x,g,i):return (x,parent[1],parent[2],(parent[0],g,i) if parent[1] else None)
class Evaluator:
 def __init__(self):self.calls=0;self.records=[]
 def begin(self):self.records=[]
 def score(self,record,index):
  assert 0<=record[0]<2**32;h=hamming(record[0],self.target);self.records.append(dict(candidate_index=index,genotype=record[0],raw_mismatch=h));self.calls+=1;return h
class Policy:
 def __init__(self,mode,pop):self.active,self.cost=properties(mode);self.pop=list(pop);self.completed=0
 def probes(self):return [offspring(p,p[3][0] if self.active and p[1] else p[0],self.completed,i) for i,p in enumerate(self.pop)]
 def scouts(self,masks):return [offspring(p,p[0]^masks[i],self.completed,i) for i,p in enumerate(self.pop)]
 def children(self,pool,scores,ties,masks):
  donors=[];children=[]
  for i,p in enumerate(self.pop):
   indices=[i,32+i,64+i];win=min(indices,key=lambda j:(scores[j],ties[j],j));donors.append(dict(parent=i,candidate_indices=indices,raw_mismatches=[scores[j] for j in indices],tie_values=[ties[j] for j in indices],winner_index=win,winner_family=('parent','probe','scout')[win//32]));children.append(offspring(p,pool[win][0]^masks[i],self.completed,i))
  return children,donors

def step(engine,ev,local,scout,ties):
 assert len(local)==len(scout)==32 and len(ties)==128
 before=engine.pop;start=ev.calls;pool=list(before);raw=[ev.score(p,i) for i,p in enumerate(before)]
 for group in (engine.probes(),engine.scouts(scout)):
  for p in group:j=len(pool);pool.append(p);raw.append(ev.score(p,j))
 children,donors=engine.children(pool,raw,ties,local)
 for p in children:j=len(pool);pool.append(p);raw.append(ev.score(p,j))
 penalized=[h+engine.cost*p[1] for h,p in zip(raw,pool)];selected=sorted(range(128),key=lambda j:(penalized[j],ties[j],j))[:32];out=[pool[j] for j in selected];desc=[0]*32
 for j in selected:desc[j%32]+=1
 f=sum(p[1] for p in before)/32.;newf=sum(p[1] for p in out)/32.;term=sum((n-1)*(p[1]-f) for n,p in zip(desc,before))/32.;assert sum(desc)==32 and newf-f==term
 B=sum(raw[:32])/1024.;L=sum(raw[j] for j in selected)/1024.;BP=sum(penalized[:32])/1024.;LP=sum(penalized[j] for j in selected)/1024.;S=B-L;SP=BP-LP;assert SP>=0 and SP==S+engine.cost*(f-newf)/32.;assert ev.calls-start==128
 assert all(pool[j][1:3]==before[j%32][1:3] for j in range(128));assert set(p[1] for p in out)<=set(p[1] for p in before)
 sources=[dict(parent=j%32,family=('parent','probe','scout','local_child')[j//32]) for j in range(128)]
 engine.completed+=1;engine.pop=out
 return dict(candidates=pool,candidate_raw_mismatches=raw,candidate_penalized_mismatches=penalized,ties=list(ties),query_records=ev.records,donor_choices=donors,selected_indices=selected,selected_records=out,sources=sources,selected_sources=[sources[j] for j in selected],current_descendant_counts=desc,f_before=f,f_after=newf,frequency_term=term,persistent_cache_count=sum(p[1] for p in out),B_raw=B,L_raw=L,S_raw=S,B_pen=BP,L_pen=LP,S_pen=SP,evaluator_calls=128,probe_access=[bool(engine.active and p[1]) for p in before])

def metrics(rawloss,freq):
 a=[1-x for x in rawloss];v=dict(U0=a[0],U1=a[1],U=sum(a[1:])/40,U40=a[-1],MLOSS=sum(rawloss[1:])/40,F0=freq[0],F1=freq[1],F=sum(freq[1:])/40,F40=freq[-1],D40=freq[-1]-freq[0])
 for j in range(8):v['E'+str(j+1)]=sum(a[1+5*j:6+5*j])/5;v['FE'+str(j+1)]=sum(freq[1+5*j:6+5*j])/5
 return v

def sequence(targets,draws,mode):
 ev=Evaluator();ev.target=targets[0];pop=initial(mode,draws['labels']);engine=Policy(mode,pop);initialscores=[ev.score(p,i) for i,p in enumerate(pop)];iq=ev.records;f=sum(p[1] for p in pop)/32.;raw=[sum(initialscores)/1024.];pen=[raw[0]+engine.cost*f/32.];freq=[f];pops=[pop];steps=[];truth=[]
 for g in range(40):
  old=ev.target;ev.target=targets[g];ev.begin();s=step(engine,ev,draws['local'][g],draws['scout'][g],draws['ties'][g]);s['W_raw']=s['B_raw']-raw[-1];s['W_pen']=s['B_pen']-pen[-1]
  for suffix,ls in [('raw',raw),('pen',pen)]:assert s['L_'+suffix]-ls[-1]==s['W_'+suffix]-s['S_'+suffix];ls.append(s['L_'+suffix])
  steps.append(s);freq.append(s['f_after']);pops.append(engine.pop);truth.append(dict(target=ev.target,actual_change=ev.target!=old))
 for suffix,ls in [('raw',raw),('pen',pen)]:assert ls[0]+sum(s['W_'+suffix]-s['S_'+suffix] for s in steps)==ls[-1]
 assert ev.calls==5152 and all(0<=x<=1 for x in raw);return dict(initial_queries=iq,initial_raw_mismatches=initialscores,populations=pops,raw_losses=raw,penalized_losses=pen,raw_accuracies=[1-x for x in raw],penalized_accuracies=[1-x for x in pen],frequencies=freq,steps=steps,ground_truth=truth,utilities=metrics(raw,freq),query_counts=dict(initial=32,candidates=5120,total=5152,extra_diagnostic_loss_calls=0))
