"""Four interface/law cells, three inherited-policy paths each; all endpoints retained."""
import os
from common import *
from model import stage,substitute
from analysis import series,base,combine,CONFIGS

def main():
 assert os.environ.get('SLURM_JOB_ID') and not (P/'TRANSFER_STARTED.json').exists();verify_manifest('SOURCE_SHA256SUMS');check_stage('INPUT');start=time.time();assert read('INPUT_FREEZE.json')['freeze_unix']<start
 save('TRANSFER_STARTED.json',dict(job_id=os.environ['SLURM_JOB_ID'],start_unix=start,source_manifest_sha256=sha(P/'SOURCE_SHA256SUMS'),input_freeze_sha256=sha(P/'INPUT_FREEZE.json')))
 st=states();ds=keyed('streams.jsonl.gz');fresh=keyed('fresh_probe_masks.jsonl.gz');surv=keyed('survival_streams.jsonl.gz');noise=keyed('noise_streams.jsonl.gz');targets=read('TARGET_TABLE.json');(P/'raw').mkdir();n=0
 with File(P/'TIME_SERIES.jsonl.gz','w') as ts,File(P/'PAIRED_METRICS.jsonl.gz','w') as pm:
  for b in range(24):
   with File(P/('raw/block%02d.jsonl.gz'%b),'w') as raw:
    for r in range(8):
     source=st[b,r];state=source['source_state'];d=ds[b,r]['draws'];labels=d['labels'];cells={}
     for interface in ('EXACT','NOISY'):
      for law in ('ZERO','HALF'):
       cell=interface+'_Q_'+law;paths={};tt=targets[law][b];assert state['last_two_preparation_targets']==tt['preparation_terminal_targets']
       for cfg in CONFIGS:
        slot=None if cfg=='STAY' else labels[int(cfg[-1])];pop=substitute(state['rebased_population'],'F',slot)
        rec=stage(tt['targets'],d,pop,fresh[b,r]['fresh'],surv[b,r]['survival'],noise[b,r]['noise'],interface,state['last_preparation_target']);values=series(rec,labels);paths[cfg]=values
        raw.write(dict(block=b,replicate=r,cell=cell,interface=interface,law=law,configuration=cfg,slot=slot,founder_ids=labels[:2],source_row_index=source['source_row_index'],source_founder_rebase_map=state['founder_rebase_map'],record=rec));n+=1
        ts.write(dict(block=b,replicate=r,cell=cell,configuration=cfg,founder_ids=labels[:2],series=values))
       cells[cell]=base(paths)
     pm.write(dict(block=b,replicate=r,values=combine(cells)))
   checkpoint('transfer',b,['raw/block%02d.jsonl.gz'%b],dict(paths=n));save('PROGRESS.json',dict(blocks_complete=b+1,new_paths=n,elapsed_seconds=time.time()-start))
 assert n==2304
 save('BUDGET.json',dict(new_paths=n,new_preparations=0,reused_preparations=192,updates=n*40,initial_evaluations=n*32,candidate_evaluations=n*5120,total_objective_calls=n*5152,state_measurements=n*41,extra_diagnostic_calls=0,scientific_paths=n,unique_noise_uniform_indices=989184))
 save('TRANSFER_RUNTIME.json',dict(elapsed_seconds=time.time()-start))
if __name__=='__main__':main()
