"""Only 2,304 off-diagonal 056 paths. Never invoke diagonal or preparation propagation."""
import os,time,collections
from common import *
from io_utils import File
from model import stage,substitute,rebase
from lineages import extract,time_series
from analysis import base_estimands

def main():
 assert os.environ.get('SLURM_JOB_ID') and not (P/'TRANSFER_STARTED.json').exists()
 verify_manifest('SOURCE_SHA256SUMS');verify_manifest('INPUT_SHA256SUMS');start=time.time()
 save('TRANSFER_STARTED.json',dict(job_id=os.environ['SLURM_JOB_ID'],start_unix=start,source_sha256=sha(P/'SOURCE_SHA256SUMS'),input_freeze_sha256=sha(P/'INPUT_FREEZE.json')))
 st=states();streams=keyed('streams.jsonl.gz');fresh=keyed('fresh_probe_masks.jsonl.gz');oldfresh=keyed('reused052_fresh_probe_masks.jsonl.gz');surv=keyed('survival_streams.jsonl.gz');targets=read('TARGET_TABLE.json');(P/'raw').mkdir();n=0;used=set();ops=collections.Counter()
 with File(P/'NEW_TIME_SERIES.jsonl.gz','w') as tsout,File(P/'NEW_PAIRED_METRICS.jsonl.gz','w') as mout:
  for b in range(24):
   with File(P/('raw/block%02d.jsonl.gz'%b),'w') as out:
    for r in range(8):
     d=streams[b,r]['draws'];labels=d['labels']
     for p,q in [('ZERO','HALF'),('HALF','ZERO')]:
      cell='P_'+p+'_Q_'+q;tt=targets[cell][b];utils={};timelines={}
      for bg in ('F','H'):
       rr=st[b,r,p,bg];pop,prov=rebase(rr['population']);assert json.loads(json.dumps(pop))==rr['rebased_population'];assert prov==rr['founder_rebase_map'];assert rr['last_two_preparation_targets']==tt['preparation_terminal_targets'];used.add((b,r,p,bg));initials=[]
       for var in ('STAY','SWITCH0','SWITCH1'):
        cfg=bg+'_'+var;slot=None if var=='STAY' else labels[int(var[-1])];initial=substitute(pop,bg,slot)
        rec=stage(tt['targets'],d,initial,0,oldfresh[b,r]['fresh']+fresh[b,r]['fresh'],surv[b,r]['survival'],40,rr['last_preparation_target']);freq,u=extract(rec,labels,cfg);utils[cfg]=u;timelines[cfg]=dict(frequency=freq,accuracy=rec['raw_accuracies']);initials.append(rec['initial_raw_mismatches']);n+=1
        for step in rec['steps']:ops.update(s['family'] for s in step['sources'][32:])
        out.write(dict(block=b,replicate=r,preparation=p,future=q,cell=cell,configuration=cfg,background=bg,cost='C0',founder_ids=labels[:2],rare_founder_id=slot,preparation_founder_map=prov,role_frequencies=freq,record=rec,evidence_kind='new056 off-diagonal transfer'))
       assert initials[0]==initials[1]==initials[2]
      tsout.write(dict(block=b,replicate=r,cell=cell,values=time_series(timelines)));mout.write(dict(block=b,replicate=r,cell=cell,values=base_estimands(utils)))
   save('PROGRESS.json',dict(blocks_complete=b+1,new_paths=n,elapsed_seconds=time.time()-start))
 assert n==2304 and len(used)==768 and ops==dict(probe=2949120,scout=2949120,local_child=2949120)
 save('BUDGET.json',dict(new_paths=n,reused_paths=2304,new_preparations=0,new_draws=0,new_seeds=0,new_updates=n*40,candidate_evaluations=n*5120,initial_evaluations=n*32,total_objective_calls=n*5152,new_state_measurements=n*41,source_prepared_states_used=len(used),nonparent_sources=ops,extra_diagnostic_calls=0))
 save('TRANSFER_RUNTIME.json',dict(elapsed_seconds=time.time()-start))
if __name__=='__main__':main()
