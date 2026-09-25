"""One allocation with inherited failure-propagating memory guard and partial receipts."""
import os,sys,threading,traceback
from common import *
from resource_guard055 import Guard,monitor,stage

def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not (P/'RUN_STARTED.json').exists();start=time.time();save('RUN_STARTED.json',dict(job_id=os.environ['SLURM_JOB_ID'],start_unix=start,python=sys.version));guard=Guard();thread=threading.Thread(target=monitor,args=(guard,),daemon=True);thread.start();steps=[]
 try:
  verify_manifest('SOURCE_SHA256SUMS');verify_references();assert read('TEST_STATUS.json')['status']=='PASS';guard.check();steps.append(stage('production.py','production.log',guard))
  files=['PRODUCTION_STARTED.json','BUDGET.json','PRODUCER_CHECKS.json','OUTCOMES.json','ASSESSMENT.json','VALIDATION_CHECK.json','PRODUCTION_RUNTIME.json']+[str(f.relative_to(P)) for folder in ('matrices','vectors','solutions','receipts','partials') for f in sorted((P/folder).glob('*')) if f.is_file()];manifest('SCIENCE_SHA256SUMS',files)
  steps.append(stage('reference_check.py','reference_check.log',guard));save('RUNTIME.json',dict(elapsed_seconds=time.time()-start,stages=steps));guard.check()
 except BaseException as error:
  save('EXECUTION_FAILURE.json',dict(error=str(error),traceback=traceback.format_exc()[-12000:],partial_receipts=[str(f.relative_to(P)) for f in sorted((P/'receipts').glob('*.json'))],automatic_retry=False,precision_change_authorized=False));raise
 finally:guard.stop.set();thread.join()
 if guard.error:raise RuntimeError('Memory monitor failed: '+str(guard.error))
 assert not (P/'RESOURCE_STOP.json').exists() and not (P/'MONITOR_FAILURE.json').exists();size=package_bytes();save('DELIVERY_SIZE_CHECK.json',dict(status='PASS' if size<=64*1024*1024 else 'FAIL',bytes=size,limit_bytes=64*1024*1024,scope='This finite package including current logs; unrelated directories excluded'));assert size<=64*1024*1024
 source={line.split('  ',1)[1] for line in (P/'SOURCE_SHA256SUMS').read_text().splitlines()};source.update(('SOURCE_SHA256SUMS','RESULT_SHA256SUMS','COMPLETION.json'))
 files=[str(f.relative_to(P)) for f in sorted(P.rglob('*')) if f.is_file() and '__pycache__' not in f.parts and str(f.relative_to(P)) not in source and not f.name.startswith('.') and not f.name.startswith('slurm-') and not f.name.startswith('submission') and not f.name.endswith('.tmp')];manifest('RESULT_SHA256SUMS',files)
 save('COMPLETION.json',dict(status='COMPLETE_PENDING_ACCOUNTING',job_id=os.environ['SLURM_JOB_ID'],elapsed_seconds=time.time()-start,source_sha256=sha(P/'SOURCE_SHA256SUMS'),result_sha256=sha(P/'RESULT_SHA256SUMS'),scientific_status=read('VALIDATION_CHECK.json')['scientific_status'],kernels=4,outcomes=14,simulation_paths=0))
if __name__=='__main__':main()
