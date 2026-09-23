import os,pathlib,json,time
import preparation_model
from io_utils import File,save,sha
from make_inputs import validate_freeze
P=pathlib.Path(__file__).resolve().parent

def extract(rec,b,r,pair):
 assert len(rec['populations'])==41 and len(rec['populations'][-1])==32
 return dict(block=b,replicate=r,geometry='RECUR',genotypes=[q[0] for q in rec['populations'][-1]],preparation_first_pair=pair,last_preparation_target=pair[1],boundary_change=pair[0]!=pair[1],source='new052 SHAM_C0 endpoint; physical order unchanged')
def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not pathlib.Path('PREPARATION_STARTED.json').exists();q=validate_freeze('INPUT_FREEZE.json');start=time.time();assert q['freeze_unix']<start;save('PREPARATION_STARTED.json',dict(start_unix=start,input_freeze_sha256=sha('INPUT_FREEZE.json')));targets=json.loads(pathlib.Path('PREPARATION_TARGETS.json').read_text())['blocks'];pathlib.Path('preparation').mkdir();n=0
 with File('prep_streams.jsonl.gz','r') as src,File('RESIDENT_STATES.jsonl.gz','w') as states:
  for b in range(24):
   with File('preparation/block%02d.jsonl.gz'%b,'w') as out:
    ts=targets[b]['targets'];assert ts==ts[:2]*20
    for r in range(8):
     row=next(src);assert (row['block'],row['replicate'])==(b,r);rec=preparation_model.sequence(ts,row['draws'],'SHAM_C0',None);assert all(q[0]==0 for q in rec['populations'][0]);out.write(dict(block=b,replicate=r,geometry='RECUR',policy='SHAM_C0',record=rec));states.write(extract(rec,b,r,ts[:2]));n+=1
   print('Prepared block',b,flush=True)
  assert next(src,None) is None
 assert n==192;save('RESIDENT_PROVENANCE.json',dict(status='PASS',source_states=192,new_preparation_calls=989184,new_preparation_paths=192,outcome_filtering=False,all_states_included=True,new_founder_ids='reset physical positions0..31',carrier_cache='own current genotype, timestamp0, actual position',same_preparation_transfer_first_pair=True));save('PREPARATION_BUDGET.json',dict(paths=192,updates=7680,candidate_queries=983040,initial_queries=6144,underlying_loss_computations=989184,state_measurements=7872,extra_diagnostic_loss_calls=0));save('PREPARATION_RUNTIME.json',dict(elapsed_seconds=time.time()-start))
 names=['RESIDENT_STATES.jsonl.gz','RESIDENT_PROVENANCE.json','PREPARATION_BUDGET.json','PREPARATION_RUNTIME.json']+['preparation/block%02d.jsonl.gz'%b for b in range(24)];hashes={n:sha(n) for n in names};pathlib.Path('RESIDENT_SHA256SUMS').write_text(''.join(h+'  '+n+'\n' for n,h in hashes.items()));save('RESIDENT_FREEZE.json',dict(stage='all192 endpoints before transfer; no filtering',freeze_unix=time.time(),files=hashes,source_manifest_sha256=sha('SOURCE_SHA256SUMS'),resident_manifest_sha256=sha('RESIDENT_SHA256SUMS'),exogenous_input_freeze_sha256=sha('INPUT_FREEZE.json')))
if __name__=='__main__':main()
