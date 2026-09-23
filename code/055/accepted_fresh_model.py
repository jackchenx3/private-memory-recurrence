"""Only carrier probe genotype changes: current genotype XOR saved fresh mask."""
from accepted_model import Evaluator,offspring,metrics,step as accepted_step
from accepted_model import Policy as PrivatePolicy
from accepted_rare_model import initial
class Policy(PrivatePolicy):
 def __init__(self,mode,pop,fresh):
  assert mode in ('NOVEL_C0','NOVEL_C1');super().__init__(mode.replace('NOVEL','ACTIVE'),pop);self.active=False;self.fresh=fresh
 def probes(self):
  return [offspring(p,p[0]^self.fresh[self.completed][i] if p[1] else p[0],self.completed,i) for i,p in enumerate(self.pop)]

def step(engine,ev,local,scout,ties):
 used=[bool(p[1]) for p in engine.pop];masks=list(engine.fresh[engine.completed]);s=accepted_step(engine,ev,local,scout,ties);s['fresh_probe_use']=used;s['fresh_probe_masks']=masks;assert not any(s['probe_access']);return s

def sequence(targets,draws,mode,fresh):
 ev=Evaluator();ev.target=targets[0];pop=initial(mode.replace('NOVEL','ACTIVE'),draws['labels']);engine=Policy(mode,pop,fresh);initialscores=[ev.score(p,i) for i,p in enumerate(pop)];iq=ev.records;f=sum(p[1] for p in pop)/32.;raw=[sum(initialscores)/1024.];pen=[raw[0]+engine.cost*f/32.];freq=[f];pops=[pop];steps=[];truth=[]
 for g in range(40):
  old=ev.target;ev.target=targets[g];ev.begin();s=step(engine,ev,draws['local'][g],draws['scout'][g],draws['ties'][g]);s['W_raw']=s['B_raw']-raw[-1];s['W_pen']=s['B_pen']-pen[-1]
  for suffix,ls in [('raw',raw),('pen',pen)]:assert s['L_'+suffix]-ls[-1]==s['W_'+suffix]-s['S_'+suffix];ls.append(s['L_'+suffix])
  steps.append(s);freq.append(s['f_after']);pops.append(engine.pop);truth.append(dict(target=ev.target,actual_change=ev.target!=old))
 for suffix,ls in [('raw',raw),('pen',pen)]:assert ls[0]+sum(s['W_'+suffix]-s['S_'+suffix] for s in steps)==ls[-1]
 assert ev.calls==5152 and all(0<=x<=1 for x in raw);return dict(initial_queries=iq,initial_raw_mismatches=initialscores,populations=pops,raw_losses=raw,penalized_losses=pen,raw_accuracies=[1-x for x in raw],penalized_accuracies=[1-x for x in pen],frequencies=freq,steps=steps,ground_truth=truth,utilities=metrics(raw,freq),query_counts=dict(initial=32,candidates=5120,total=5152,extra_diagnostic_loss_calls=0))
