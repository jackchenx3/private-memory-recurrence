"""Exact055 policy stages, now from new058 cohort and independent stage tapes."""
import os,collections
from common import *
from model import all_policy,stage,rebase

def main():
 assert os.environ.get('SLURM_JOB_ID') and not (P/'POLICY_STARTED.json').exists();check_stage('INPUT');check_stage('INITIAL');save('POLICY_STARTED.json',dict(start=time.time(),initial_freeze_sha256=sha(P/'INITIAL_FREEZE.json')));(P/'policy').mkdir();ts=read('POLICY_TARGETS.json');n=0
 with File(P/'INITIAL_STATES.jsonl.gz','r') as roots,File(P/'policy_streams.jsonl.gz','r') as streams,File(P/'policy_fresh_probe_masks.jsonl.gz','r') as fresh,File(P/'policy_survival_streams.jsonl.gz','r') as survival,File(P/'RESIDENT_STATES.jsonl.gz','w') as states:
  for b in range(24):
   blockstates=[]
   with File(P/('policy/block%02d.jsonl.gz'%b),'w') as out:
    for r in range(8):
     d,f,s=next(streams),next(fresh),next(survival);assert all((x['block'],x['replicate'])==(b,r) for x in (d,f,s))
     for objective in ('HAM','TRAP4'):
      root=next(roots);assert (root['block'],root['replicate'],root['objective'])==(b,r,objective)
      for bg in ('F','H'):
       targets=ts['HALF'][b]['targets'];rec=stage(targets,d['draws'],all_policy(root['genotypes'],bg),0,f['fresh'],s['survival'],objective=objective);pop,mapping=rebase(rec['populations'][-1]);assert rec['query_counts']['total']==5152
       out.write(dict(block=b,replicate=r,objective=objective,geometry='HALF',background=bg,record=rec));state=dict(block=b,replicate=r,objective=objective,geometry='HALF',background=bg,population=rec['populations'][-1],rebased_population=pop,founder_rebase_map=mapping,last_preparation_target=targets[-1],last_two_preparation_targets=targets[-2:],source='new058 unfiltered policy preparation');states.write(state);blockstates.append(state);n+=1
   save('policy/states-block%02d.json'%b,blockstates);checkpoint('policy',b,['policy/block%02d.jsonl.gz'%b,'policy/states-block%02d.json'%b],dict(paths=n))
   save('POLICY_PROGRESS.json',dict(blocks=b+1,paths=n))
  assert all(next(x,None) is None for x in (roots,streams,fresh,survival))
 assert n==768;save('POLICY_BUDGET.json',dict(paths=n,total_objective_calls=n*5152,candidate_calls=n*5120,initial_calls=n*32,outcome_filtering=False));freeze_stage('RESIDENT',['RESIDENT_STATES.jsonl.gz','POLICY_BUDGET.json']+[n for b in range(24) for n in ['policy/block%02d.jsonl.gz'%b,'policy/states-block%02d.json'%b]])
if __name__=='__main__':main()
