"""Exactly052 SHAM_C0 cohort distribution; every zero-start endpoint retained."""
import os
from common import *
import preparation_model

def main():
 assert os.environ.get('SLURM_JOB_ID') and not (P/'INITIAL_STARTED.json').exists();q=check_stage('INPUT');save('INITIAL_STARTED.json',dict(start=time.time(),input_freeze_sha256=sha(P/'INPUT_FREEZE.json')));ts=read('INITIAL_TARGETS.json')['blocks'];(P/'initial').mkdir();n=0
 with File(P/'initial_streams.jsonl.gz','r') as src,File(P/'INITIAL_STATES.jsonl.gz','w') as states:
  for b in range(24):
   blockstates=[]
   with File(P/('initial/block%02d.jsonl.gz'%b),'w') as out:
    for r in range(8):
     d=next(src);assert (d['block'],d['replicate'])==(b,r);rec=preparation_model.sequence(ts[b]['targets'],d['draws'],'SHAM_C0',None);assert all(x[0]==0 for x in rec['populations'][0]);assert rec['query_counts']['total']==5152
     out.write(dict(block=b,replicate=r,record=rec,mode='SHAM_C0'));state=dict(block=b,replicate=r,genotypes=[x[0] for x in rec['populations'][-1]],last_initial_target=ts[b]['targets'][-1],first_pair=ts[b]['targets'][:2]);states.write(state);blockstates.append(state);n+=1
   save('initial/states-block%02d.json'%b,blockstates);checkpoint('initial',b,['initial/block%02d.jsonl.gz'%b,'initial/states-block%02d.json'%b],dict(paths=n))
   save('INITIAL_PROGRESS.json',dict(blocks=b+1,paths=n))
  assert next(src,None) is None
 assert n==192;save('INITIAL_BUDGET.json',dict(paths=n,total_objective_calls=n*5152,candidate_calls=n*5120,initial_calls=n*32,outcome_filtering=False));freeze_stage('INITIAL',['INITIAL_STATES.jsonl.gz','INITIAL_BUDGET.json']+[n for b in range(24) for n in ['initial/block%02d.jsonl.gz'%b,'initial/states-block%02d.json'%b]])
if __name__=='__main__':main()
