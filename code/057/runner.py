"""057 production allocation only; reuse accepted failure-propagating memory guard."""
import os,sys,time,threading,traceback
from common import *
from resource_guard055 import Guard,monitor,stage

def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not (P/'RUN_STARTED.json').exists();start=time.time();save('RUN_STARTED.json',dict(job_id=os.environ['SLURM_JOB_ID'],start_unix=start,python=sys.version));guard=Guard();thread=threading.Thread(target=monitor,args=(guard,),daemon=True);thread.start();steps=[];success=False
 try:
  verify_manifest('SOURCE_SHA256SUMS');assert read('TEST_STATUS.json')['status']=='PASS';guard.check()
  for script,log in [('make_inputs.py','inputs.log'),('prepare_initial.py','initial.log'),('prepare_policy.py','policy.log'),('transfer.py','transfer.log')]:steps.append(stage(script,log,guard))
  files=['TRANSFER_STARTED.json','PROGRESS.json','NEW_TIME_SERIES.jsonl.gz','NEW_PAIRED_METRICS.jsonl.gz','BUDGET.json','TRANSFER_RUNTIME.json']+['raw/block%02d.jsonl.gz'%b for b in range(24)]
  files+=['INITIAL_STATES.jsonl.gz','RESIDENT_STATES.jsonl.gz','INITIAL_BUDGET.json','POLICY_BUDGET.json','INPUT_FREEZE.json','INITIAL_FREEZE.json','RESIDENT_FREEZE.json']+[folder+'/block%02d.jsonl.gz'%b for folder in ('initial','policy') for b in range(24)]
  (P/'SCIENCE_SHA256SUMS').write_text(''.join(sha(P/n)+'  '+n+'\n' for n in files))
  steps.append(stage('validate_analyze.py','validation.log',guard));steps.append(stage('audit_independent.py','independent_audit.log',guard));save('RUNTIME.json',dict(elapsed_seconds=time.time()-start,stages=steps));guard.check();success=True
 except BaseException as e:
  save('EXECUTION_FAILURE.json',dict(error=str(e),traceback=traceback.format_exc(),partial_outputs_preserved=True,completed_block_checkpoints=[str(x.relative_to(P)) for x in sorted((P/'checkpoints').glob('*.json'))],resume_policy='Preserve immutable inputs and completed blocks. Supervisor reviews recovery; no automatic replacement allocation or replacement seeds.'));raise
 finally:guard.stop.set();thread.join()
 if guard.error:raise RuntimeError('Monitor failure at shutdown: '+str(guard.error))
 assert success and not (P/'RESOURCE_STOP.json').exists() and not (P/'MONITOR_FAILURE.json').exists()
 excluded={x.split('  ',1)[1] for x in (P/'SOURCE_SHA256SUMS').read_text().splitlines()}
 excluded.update(['SOURCE_SHA256SUMS','RESULT_SHA256SUMS','COMPLETION.json'])
 files=sorted(f for f in P.rglob('*') if f.is_file() and str(f.relative_to(P)) not in excluded and '__pycache__' not in f.parts and not f.name.startswith('.') and not f.name.startswith('slurm-') and not f.name.startswith('submission') and not f.name.endswith('.tmp'))
 (P/'RESULT_SHA256SUMS').write_text(''.join(sha(f)+'  '+str(f.relative_to(P))+'\n' for f in files))
 save('COMPLETION.json',dict(status='COMPLETE_PENDING_ACCOUNTING',job_id=os.environ['SLURM_JOB_ID'],elapsed_seconds=time.time()-start,source_sha256=sha(P/'SOURCE_SHA256SUMS'),result_sha256=sha(P/'RESULT_SHA256SUMS'),validation='PASS',new_paths=4608,reused_paths=0,total_scientific_paths=5568,intervals=162))
if __name__=='__main__':main()
