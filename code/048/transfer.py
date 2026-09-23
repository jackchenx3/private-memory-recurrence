import os,json,pathlib,time,collections
from model import sequence
from analysis import MET,MODES,NEW,OLD,STARTS,LAWS
from signatures import first
from io_utils import File,save,sha,telemetry
from make_inputs import verify_inherited,SOURCE
P=pathlib.Path(__file__).resolve().parent

def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not pathlib.Path('TRANSFER_STARTED.json').exists();freeze=json.loads(pathlib.Path('INPUT_FREEZE.json').read_text());assert sha('SOURCE_SHA256SUMS')==freeze['source_manifest_sha256'] and sha('INPUT_SHA256SUMS')==freeze['input_manifest_sha256']
 for n,h in freeze['files'].items():assert sha(n)==h
 verify_inherited();start=time.time();assert freeze['freeze_unix']<start;save('TRANSFER_STARTED.json',dict(start=start,input_freeze_sha256=sha('INPUT_FREEZE.json'),job_id=os.environ['SLURM_JOB_ID']));targets={g:json.loads((P/(g+'_TARGETS.json')).read_text())['blocks'] for g in LAWS};pathlib.Path('raw').mkdir(exist_ok=True);blocks=[];nseq=nold=0;checks=collections.Counter();ops=collections.Counter();stages=[]
 with File('streams.jsonl.gz','r') as src,File('probe_permutations.jsonl.gz','r') as directions,File('RESIDENT_STATES.jsonl.gz','r') as residents:
  for b in range(24):
   sums={a+'|'+g+'|'+m+'|'+k:0. for a in STARTS for g in LAWS for m in MODES for k in MET}
   with File(SOURCE/('raw/block%02d.jsonl.gz'%b),'r') as controls,File('raw/block%02d.jsonl.gz'%b,'w') as out:
    for rep in range(8):
     stream=next(src);direction=next(directions);assert (stream['block'],stream['replicate'])==(direction['block'],direction['replicate'])==(b,rep);firsts={};seen=set()
     for _ in range(24):
      row=next(controls);assert (row['block'],row['replicate'])==(b,rep);a,g,m=row['abundance'],row['geometry'],row['policy'];assert a in STARTS and g in LAWS and m in OLD and (a,g,m) not in seen;seen.add((a,g,m));r=row['record'];nold+=1
      if m.startswith(('ACTIVE','SHAM')):firsts[a,g,m]=first(r)
      for k,x in r['utilities'].items():sums[a+'|'+g+'|'+m+'|'+k]+=x
      out.write(dict(row,reuse_note='authenticated047control;not rerun'))
     state={}
     for _ in range(2):
      rr=next(residents);assert (rr['block'],rr['replicate'])==(b,rep);state[rr['geometry']]=rr
     assert set(state)==set(LAWS)
     for a in STARTS:
      for g in LAWS:
       for mode in NEW:
        rec=sequence(targets[g][b]['targets'],stream['draws'],mode,direction['permutations'],[0]*32 if a=='NAIVE' else state[g]['genotypes']);nseq+=1
        for m in ('ACTIVE','SHAM'):assert first(rec)==firsts[a,g,m+mode[-3:]];checks['radius_'+m.lower()+'_first_update']+=1
        for k,x in rec['utilities'].items():sums[a+'|'+g+'|'+mode+'|'+k]+=x
        for s in rec['steps']:ops.update(x['family'] for x in s['sources'][32:]);checks['radius_slots_verified']+=len(s['radius_probe'])
        out.write(dict(block=b,replicate=rep,geometry=g,policy=mode,abundance=a,record=rec,evidence_kind='new048radius_control',cohort='reused047'))
    assert next(controls,None) is None
   blocks.append(dict(block=b,values={k:x/8 for k,x in sums.items()}));save('BASE_BLOCKS.json',blocks);save('TRANSFER_PROGRESS.json',dict(blocks=b+1,new_sequences=nseq,reused_sequences=nold,elapsed_seconds=time.time()-start));stages.append(telemetry('block-%02d'%b));print('Block',b,flush=True)
  assert next(src,None) is None and next(directions,None) is None and next(residents,None) is None
 assert nseq==1536 and nold==4608 and checks==dict(radius_active_first_update=1536,radius_sham_first_update=1536,radius_slots_verified=1966080);assert ops==dict(probe=1966080,scout=1966080,local_child=1966080)
 save('PREFIX_CHECKS.json',dict(status='PASS',**checks));save('BUDGET.json',dict(new_sequences=1536,new_updates=61440,candidate_queries=7864320,initial_queries=49152,underlying_loss_computations=7913472,state_measurements=62976,nonparent_candidates=5898240,nonparent_sources=ops,old_paths_used=4608,old_paths_rerun=0,source_resident_states=384,preparation_previously_incurred_calls=1978368,extra_diagnostic_loss_calls=0,new_seeds=192,logical_permutation_shuffles=245760,reference_optimization=0,pretraining=0,fixture_work='FIXTURE_WORK.json separate'));save('TRANSFER_RUNTIME.json',dict(elapsed_seconds=time.time()-start,stages=stages))
if __name__=='__main__':main()
