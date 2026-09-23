"""Uniform Hamming-sphere probe retaining own-state private-cache distance."""
from accepted_model import Policy as PrivatePolicy,Evaluator,metrics,offspring,step as accepted_step
from accepted_resident_model import initial
from analysis import NEW

def radius_probe(parent,permutation):
 assert sorted(permutation)==list(range(32))
 x,carrier,founder,cache=parent;used=bool(carrier and cache is not None)
 d=bin(x^cache[0]).count('1') if used else 0
 mask=sum(1<<bit for bit in permutation[:d]);probe=x^mask
 assert 0<=d<=32 and 0<=mask<2**32 and bin(x^probe).count('1')==d
 return dict(permutation=list(permutation),distance=d,mask=mask,expressed_genotype=probe,use=used)

class Policy(PrivatePolicy):
 def __init__(self,mode,pop,permutations):
  assert mode in NEW;super().__init__(mode.replace('RADIUS','ACTIVE'),pop);self.active=False;self.permutations=permutations
 def probes(self):
  self.radius_records=[radius_probe(p,self.permutations[self.completed][i]) for i,p in enumerate(self.pop)]
  return [offspring(p,self.radius_records[i]['expressed_genotype'],self.completed,i) for i,p in enumerate(self.pop)]

def step(engine,ev,local,scout,ties):
 s=accepted_step(engine,ev,local,scout,ties);s['radius_probe']=engine.radius_records
 assert not any(s['probe_access'])
 for i,q in enumerate(s['radius_probe']):assert s['candidates'][32+i][0]==q['expressed_genotype']
 return s

def sequence(targets,draws,mode,permutations,genotypes):
 ev=Evaluator();ev.target=targets[0];pop=initial(mode,draws['labels'],genotypes);engine=Policy(mode,pop,permutations);initialscores=[ev.score(p,i) for i,p in enumerate(pop)];iq=ev.records;f=sum(p[1] for p in pop)/32.;raw=[sum(initialscores)/1024.];pen=[raw[0]+engine.cost*f/32.];freq=[f];pops=[pop];steps=[];truth=[]
 for g in range(40):
  old=ev.target;ev.target=targets[g];ev.begin();s=step(engine,ev,draws['local'][g],draws['scout'][g],draws['ties'][g]);s['W_raw']=s['B_raw']-raw[-1];s['W_pen']=s['B_pen']-pen[-1]
  for suffix,ls in [('raw',raw),('pen',pen)]:assert s['L_'+suffix]-ls[-1]==s['W_'+suffix]-s['S_'+suffix];ls.append(s['L_'+suffix])
  steps.append(s);freq.append(s['f_after']);pops.append(engine.pop);truth.append(dict(target=ev.target,actual_change=ev.target!=old))
 for suffix,ls in [('raw',raw),('pen',pen)]:assert ls[0]+sum(s['W_'+suffix]-s['S_'+suffix] for s in steps)==ls[-1]
 assert ev.calls==5152 and all(0<=x<=1 for x in raw);return dict(initial_queries=iq,initial_raw_mismatches=initialscores,populations=pops,raw_losses=raw,penalized_losses=pen,raw_accuracies=[1-x for x in raw],penalized_accuracies=[1-x for x in pen],frequencies=freq,steps=steps,ground_truth=truth,utilities=metrics(raw,freq),query_counts=dict(initial=32,candidates=5120,total=5152,extra_diagnostic_loss_calls=0))
