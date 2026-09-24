"""All4,608 new058 crossed transfers; no old states, trajectories or tapes."""
import os,time,collections
from common import *
from io_utils import File
from model import stage,substitute,rebase
from lineages import extract,time_series
from analysis import base_estimands

def main():
 assert os.environ.get('SLURM_JOB_ID') and not (P/'TRANSFER_STARTED.json').exists()
 verify_manifest('SOURCE_SHA256SUMS');check_stage('INPUT');check_stage('RESIDENT');start=time.time();assert read('INPUT_FREEZE.json')['freeze_unix']<read('INITIAL_FREEZE.json')['freeze_unix']<read('RESIDENT_FREEZE.json')['freeze_unix']<start
 save('TRANSFER_STARTED.json',dict(job_id=os.environ['SLURM_JOB_ID'],start_unix=start,source_sha256=sha(P/'SOURCE_SHA256SUMS'),input_freeze_sha256=sha(P/'INPUT_FREEZE.json')))
 st=states();streams=keyed('streams.jsonl.gz');fresh=keyed('fresh_probe_masks.jsonl.gz');oldfresh=keyed('policy_fresh_probe_masks.jsonl.gz');surv=keyed('survival_streams.jsonl.gz');targets=read('TARGET_TABLE.json');(P/'raw').mkdir();n=0;used=set();ops=collections.Counter()
 with File(P/'NEW_TIME_SERIES.jsonl.gz','w') as tsout,File(P/'NEW_PAIRED_METRICS.jsonl.gz','w') as mout:
  for b in range(24):
   with File(P/('raw/block%02d.jsonl.gz'%b),'w') as out:
    for r in range(8):
     d=streams[b,r]['draws'];labels=d['labels']
     for objective,q in [('HAM','ZERO'),('HAM','HALF'),('TRAP4','ZERO'),('TRAP4','HALF')]:
      p='HALF';cell=objective+'|Q_'+q;tt=targets['Q_'+q][b];utils={};timelines={}
      for bg in ('F','H'):
       rr=st[b,r,objective,bg];pop,prov=rebase(rr['population']);assert json.loads(json.dumps(pop))==rr['rebased_population'];assert prov==rr['founder_rebase_map'];assert rr['last_two_preparation_targets']==tt['preparation_terminal_targets'];used.add((b,r,objective,bg));initials=[]
       for var in ('STAY','SWITCH0','SWITCH1'):
        cfg=bg+'_'+var;slot=None if var=='STAY' else labels[int(var[-1])];initial=substitute(pop,bg,slot)
        rec=stage(tt['targets'],d,initial,0,oldfresh[b,r]['fresh']+fresh[b,r]['fresh'],surv[b,r]['survival'],40,rr['last_preparation_target'],objective=objective);freq,u=extract(rec,labels,cfg);utils[cfg]=u;timelines[cfg]=dict(frequency=freq,accuracy=rec['raw_accuracies']);initials.append(rec['initial_raw_mismatches']);n+=1
        for step in rec['steps']:ops.update(s['family'] for s in step['sources'][32:])
        out.write(dict(block=b,replicate=r,objective=objective,preparation=p,future=q,cell=cell,configuration=cfg,background=bg,cost='C0',founder_ids=labels[:2],rare_founder_id=slot,preparation_founder_map=prov,role_frequencies=freq,record=rec,evidence_kind='new058 independent-cohort transfer'))
       assert initials[0]==initials[1]==initials[2]
      tsout.write(dict(block=b,replicate=r,cell=cell,values=time_series(timelines)));mout.write(dict(block=b,replicate=r,cell=cell,values=base_estimands(utils)))
   checkpoint('transfer',b,['raw/block%02d.jsonl.gz'%b],dict(paths=n))
   save('PROGRESS.json',dict(blocks_complete=b+1,new_paths=n,elapsed_seconds=time.time()-start))
 assert n==4608 and len(used)==768 and ops==dict(probe=5898240,scout=5898240,local_child=5898240)
 save('BUDGET.json',dict(new_paths=n,reused_paths=0,initial_preparation_paths=384,policy_preparation_paths=768,new_seed_records=3193,new_updates=n*40,candidate_evaluations=n*5120,initial_evaluations=n*32,transfer_objective_calls=n*5152,total_scientific_paths=5760,total_updates=230400,total_candidate_evaluations=29491200,total_initial_evaluations=184320,total_state_measurements=236160,total_objective_calls=29675520,new_state_measurements=n*41,source_prepared_states_used=len(used),nonparent_sources=ops,extra_diagnostic_calls=0))
 save('TRANSFER_RUNTIME.json',dict(elapsed_seconds=time.time()-start))
if __name__=='__main__':main()
