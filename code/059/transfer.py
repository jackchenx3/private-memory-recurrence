"""Exactly five new paths per authenticated HALF/H preparation, without filtering."""
import os,collections
from common import *
from model import stage,substitute
from analysis import lineage_series,summarize,CONFIGS

def main():
 assert os.environ.get('SLURM_JOB_ID') and not (P/'TRANSFER_STARTED.json').exists();verify_manifest('SOURCE_SHA256SUMS');check_stage('INPUT');start=time.time();assert read('INPUT_FREEZE.json')['freeze_unix']<start
 save('TRANSFER_STARTED.json',dict(job_id=os.environ['SLURM_JOB_ID'],start_unix=start,source_manifest_sha256=sha(P/'SOURCE_SHA256SUMS'),input_freeze_sha256=sha(P/'INPUT_FREEZE.json')))
 st=states();ds=keyed('streams.jsonl.gz');fresh=keyed('fresh_probe_masks.jsonl.gz');surv=keyed('survival_streams.jsonl.gz');targets=read('TARGET_TABLE.json');(P/'raw').mkdir();n=0
 with File(P/'TIME_SERIES.jsonl.gz','w') as ts,File(P/'PAIRED_METRICS.jsonl.gz','w') as pm:
  for b in range(24):
   with File(P/('raw/block%02d.jsonl.gz'%b),'w') as raw:
    for r in range(8):
     source=st[b,r];state=source['source_state'];d=ds[b,r]['draws'];labels=d['labels'];paths={};first={};initials=[]
     assert state['last_two_preparation_targets']==targets[b]['preparation_terminal_targets']
     for cfg in CONFIGS:
      arm='STAY' if cfg=='STAY' else cfg[:-1];slot=None if cfg=='STAY' else labels[int(cfg[-1])];pop=substitute(state['rebased_population'],slot)
      rec=stage(targets[b]['targets'],d,pop,fresh[b,r]['fresh'],surv[b,r]['survival'],arm,state['last_preparation_target']);freq=lineage_series(rec,labels);series=dict(accuracy=rec['raw_accuracies'],founder=freq,expression_selected=rec['expression_selected'],expression_carried=rec['expression_carried']);paths[cfg]=series;initials.append(rec['initial_raw_mismatches'])
      if arm in ('PULSE','CONT'):
       i=int(cfg[-1]);value=dict(initial=rec['populations'][0],initial_queries=rec['initial_queries'],step=rec['steps'][0])
       if arm=='PULSE':first[i]=value
       else:assert value==first[i]
      raw.write(dict(block=b,replicate=r,configuration=cfg,arm=arm,slot=slot,founder_ids=labels[:2],source_row_index=source['source_row_index'],source_founder_rebase_map=state['founder_rebase_map'],record=rec));n+=1
      ts.write(dict(block=b,replicate=r,configuration=cfg,founder_ids=labels[:2],series=series))
     assert all(x==initials[0] for x in initials)
     pm.write(dict(block=b,replicate=r,values=summarize(paths)))
   checkpoint('transfer',b,['raw/block%02d.jsonl.gz'%b],dict(paths=n));save('PROGRESS.json',dict(blocks_complete=b+1,new_paths=n,elapsed_seconds=time.time()-start))
 assert n==960
 save('BUDGET.json',dict(new_paths=n,new_preparations=0,reused_preparations=192,updates=n*40,initial_evaluations=n*32,candidate_evaluations=n*5120,total_objective_calls=n*5152,state_measurements=n*41,extra_diagnostic_calls=0,scientific_paths=960))
 save('TRANSFER_RUNTIME.json',dict(elapsed_seconds=time.time()-start,pulse_continuous_first_update_identity=True))
if __name__=='__main__':main()
