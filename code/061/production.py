"""Single-allocation production: four exact kernels and fixed-precision solves once."""
import os,traceback
from common import *
from kernel import row,check_matrix,KERNELS,D,AUDIT_ROWS
from numerics import solve,rounded_weights,certify,from_rational
from outcomes import calculate,assess
from fractions import Fraction

def main():
 assert os.environ.get('SLURM_JOB_ID') and not (P/'PRODUCTION_STARTED.json').exists();verify_manifest('SOURCE_SHA256SUMS');start=time.time()
 save('PRODUCTION_STARTED.json',dict(job_id=os.environ['SLURM_JOB_ID'],start_unix=start,source_manifest_sha256=sha(P/'SOURCE_SHA256SUMS'),precision=80,rounding_grid=60))
 vectors={};checks={};completed=0;criterion_pass=0
 for name in KERNELS:
  intent='receipts/'+name+'-intent.json';assert not (P/intent).exists();save(intent,dict(kernel=name,matrix_attempts=1,stationary_solve_attempts=0,start_unix=time.time(),automatic_retry=False));A=[]
  for s in range(256):
   A.append(row(s,name))
   if (s+1)%32==0:
    chunk='partials/'+name+'-rows%03d-%03d.json.gz'%(s-31,s);save(chunk,dict(first_row=s-31,last_row=s,numerators=A[-32:],denominator=D));save('receipts/'+name+'-matrix-progress.json',dict(rows_complete=s+1,last_chunk=chunk,last_chunk_sha256=sha(P/chunk),automatic_retry=False))
  matrix_file='matrices/'+name+'.json.gz';save(matrix_file,dict(kernel=name,denominator=D,numerators=A,state_order='increasing ID0..255'));checks[name]=check_matrix(A,name);save('PRODUCER_CHECKS.json',checks)
  save('receipts/'+name+'-matrix-complete.json',dict(kernel=name,sha256=sha(P/matrix_file),rows=256,columns=256,completed_unix=time.time()))
  save('receipts/'+name+'-solve-intent.json',dict(kernel=name,attempts=1,precision=80,grid_digits=60,start_unix=time.time(),automatic_retry=False))
  try:
   solution=solve(A,D);save('solutions/'+name+'.json.gz',solution);k=rounded_weights(solution);certificate=certify(A,D,k)
   v=dict(status='COMPUTED',kernel=name,k=[str(x) for x in k],certificate=certificate,solution=solution);criterion_pass+=int(certificate['criterion_pass'])
   if name.startswith('NEUTRAL'):
    K=int(certificate['K']);center=Fraction(sum(x*(((s>>2)&1)+((s>>5)&1)) for s,x in enumerate(k)),2*K);E=from_rational(certificate['total_variation_bound']);assert center-E<=Fraction(1,2)<=center+E,'Neutral H symmetry/certificate contradiction'
  except Exception as error:
   v=dict(status='REJECTED',kernel=name,reason=str(error),traceback=traceback.format_exc()[-12000:],precision=80,grid_digits=60,automatic_retry=False)
  vector_file='vectors/'+name+'.json.gz';save(vector_file,v);vectors[name]=v;completed+=1
  save('receipts/'+name+'-complete.json',dict(kernel=name,matrix_sha256=sha(P/matrix_file),vector_sha256=sha(P/vector_file),vector_status=v['status'],criterion_pass=v.get('certificate',{}).get('criterion_pass',False),completed_unix=time.time(),stationary_solve_attempts=1))
  save('BUDGET.json',dict(completed_kernels=completed,stationary_solve_attempts=completed,accepted_vectors=sum(x['status']=='COMPUTED' for x in vectors.values()),certified_vectors=criterion_pass,transition_numerators=completed*65536,stationary_entries=sum(len(x.get('k',[])) for x in vectors.values()),literal_branches=completed*7340032,simulation_paths=0,random_draws=0,bootstrap_rows=0))
 records=calculate(vectors);save('OUTCOMES.json',records);save('ASSESSMENT.json',assess(records))
 science='ALL_CERTIFIED' if criterion_pass==4 else 'NUMERICAL_CERTIFICATION_FAILED';save('VALIDATION_CHECK.json',dict(status='PASS',integer_kernels_checked=4,outcomes=14,scientific_status=science,certified_vectors=criterion_pass,precision=80,grid_digits=60,all_failures_preserved=True))
 save('PRODUCTION_RUNTIME.json',dict(elapsed_seconds=time.time()-start,scientific_status=science,production_package_bytes=package_bytes()))
 assert package_bytes()<=64*1024*1024,'Scientific/source package exceeds64MiB budget'
 print(json.dumps(dict(kernels=4,scientific_status=science,assessment=read('ASSESSMENT.json')['decision'])))
if __name__=='__main__':main()
