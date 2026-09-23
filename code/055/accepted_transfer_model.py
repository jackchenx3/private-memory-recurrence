from accepted_model import Evaluator,Policy as Base,offspring,metrics
from accepted_survival_model import race_select,to_uniform
from analysis import RAW,FREQ
STRATEGIES={0:'R',1:'H',2:'F'}
def initial(config,labels,genotypes):
 assert sorted(labels)==list(range(32)) and len(genotypes)==32
 p0,p1=labels[:2];assign={'LOW0':{i:1 if i==p0 else 2 for i in range(32)},'LOW1':{i:1 if i==p1 else 2 for i in range(32)},'HIGH0':{i:2 if i==p0 else 1 for i in range(32)},'HIGH1':{i:2 if i==p1 else 1 for i in range(32)},'HH':{p0:1,p1:1},'FF':{p0:2,p1:2},'MIX0':{p0:1,p1:2},'MIX1':{p1:1,p0:2},'H0':{p0:1},'H1':{p1:1},'F0':{p0:2},'F1':{p1:2}}[config]
 return [(x,assign.get(i,0),i,(x,0,i) if i in assign else None) for i,x in enumerate(genotypes)]
class Policy(Base):
 def __init__(self,cost,pop,fresh,strategies=None):
  assert cost in (0,1);self.cost=cost;self.pop=list(pop);self.fresh=fresh;self.completed=0;self.strategies=dict(STRATEGIES if strategies is None else strategies);assert self.strategies[0]=='R'
 def probes(self):
  out=[]
  for i,p in enumerate(self.pop):
   role=self.strategies[p[1]];x=p[3][0] if role=='H' else p[0]^self.fresh[self.completed][i] if role=='F' else p[0];out.append(offspring(p,x,self.completed,i))
  return out

def frequencies(pop):return {r:sum(p[1]==k for p in pop)/32. for k,r in STRATEGIES.items()}
def utilities(raw,freq):
 q=metrics(raw,freq['H']);return dict(raw={k:q[k] for k in RAW},frequency={r:{k:metrics(raw,fs)[k] for k in FREQ} for r,fs in freq.items()})

def step(engine,ev,local,scout,ties,survival):
 assert len(local)==len(scout)==32 and len(ties)==128
 before=engine.pop;start=ev.calls;pool=list(before);raw=[ev.score(p,i) for i,p in enumerate(before)]
 for group in (engine.probes(),engine.scouts(scout)):
  for p in group:j=len(pool);pool.append(p);raw.append(ev.score(p,j))
 children,donors=engine.children(pool,raw,ties,local)
 for p in children:j=len(pool);pool.append(p);raw.append(ev.score(p,j))
 penalized=[h+engine.cost*int(p[1]!=0) for h,p in zip(raw,pool)];selected,keys=race_select(penalized,ties,survival['k'],survival['u']);out=[pool[j] for j in selected];desc=[0]*32
 for j in selected:desc[j%32]+=1
 f=sum(p[1]!=0 for p in before)/32.;newf=sum(p[1]!=0 for p in out)/32.;term=sum((n-1)*(int(p[1]!=0)-f) for n,p in zip(desc,before))/32.;assert sum(desc)==32 and newf-f==term
 B=sum(raw[:32])/1024.;L=sum(raw[j] for j in selected)/1024.;BP=sum(penalized[:32])/1024.;LP=sum(penalized[j] for j in selected)/1024.;S=B-L;SP=BP-LP;assert SP==S+engine.cost*(f-newf)/32.;assert ev.calls-start==128
 assert all(pool[j][1:3]==before[j%32][1:3] for j in range(128));assert set(p[1] for p in out)<=set(p[1] for p in before)
 sources=[dict(parent=j%32,family=('parent','probe','scout','local_child')[j//32]) for j in range(128)]
 tb=frequencies(before);ta=frequencies(out);terms={r:sum((n-1)*(int(p[1]==k)-tb[r]) for n,p in zip(desc,before))/32. for k,r in STRATEGIES.items()};assert sum(tb.values())==sum(ta.values())==1
 for r in STRATEGIES.values():assert ta[r]-tb[r]==terms[r];assert tb[r]!=0 or ta[r]==0
 engine.completed+=1;engine.pop=out
 return dict(type_frequencies_before=tb,type_frequencies_after=ta,type_frequency_terms=terms,h_retrieval_use=[engine.strategies[p[1]]=='H' for p in before],f_fresh_use=[engine.strategies[p[1]]=='F' for p in before],fresh_probe_masks=list(engine.fresh[engine.completed-1]),survival_integers=survival['k'],survival_uniforms=survival['u'],race_keys=keys,survival_weight_definition='2**(-candidate_penalized_mismatch)',candidates=pool,candidate_raw_mismatches=raw,candidate_penalized_mismatches=penalized,ties=list(ties),query_records=ev.records,donor_choices=donors,selected_indices=selected,selected_records=out,sources=sources,selected_sources=[sources[j] for j in selected],current_descendant_counts=desc,f_before=f,f_after=newf,frequency_term=term,persistent_cache_count=sum(p[1]!=0 for p in out),B_raw=B,L_raw=L,S_raw=S,B_pen=BP,L_pen=LP,S_pen=SP,evaluator_calls=128,probe_access=[engine.strategies[p[1]]=='H' for p in before])


def sequence(targets,draws,config,cost,fresh,genotypes,survival):
 ev=Evaluator();ev.target=targets[0];pop=initial(config,draws['labels'],genotypes);engine=Policy(cost,pop,fresh);initialscores=[ev.score(p,i) for i,p in enumerate(pop)];iq=ev.records;fs=frequencies(pop);raw=[sum(initialscores)/1024.];pen=[raw[0]+cost*(fs['H']+fs['F'])/32.];freq={r:[x] for r,x in fs.items()};pops=[pop];steps=[];truth=[]
 for g in range(40):
  old=ev.target;ev.target=targets[g];ev.begin();s=step(engine,ev,draws['local'][g],draws['scout'][g],draws['ties'][g],survival[g]);s['W_raw']=s['B_raw']-raw[-1];s['W_pen']=s['B_pen']-pen[-1]
  for suffix,ls in [('raw',raw),('pen',pen)]:assert s['L_'+suffix]-ls[-1]==s['W_'+suffix]-s['S_'+suffix];ls.append(s['L_'+suffix])
  for r in freq:freq[r].append(s['type_frequencies_after'][r])
  steps.append(s);pops.append(engine.pop);truth.append(dict(target=ev.target,actual_change=ev.target!=old))
 for suffix,ls in [('raw',raw),('pen',pen)]:assert ls[0]+sum(s['W_'+suffix]-s['S_'+suffix] for s in steps)==ls[-1]
 assert ev.calls==5152 and all(0<=x<=1 for x in raw);return dict(initial_queries=iq,initial_raw_mismatches=initialscores,populations=pops,raw_losses=raw,penalized_losses=pen,raw_accuracies=[1-x for x in raw],penalized_accuracies=[1-x for x in pen],frequencies=freq,steps=steps,ground_truth=truth,utilities=utilities(raw,freq),query_counts=dict(initial=32,candidates=5120,total=5152,extra_diagnostic_loss_calls=0))
