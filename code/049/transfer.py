import os,json,pathlib,time,collections
from model import sequence
from analysis import MET,MODES,LAWS
from signatures import first,prefix
from io_utils import File,save,sha,telemetry
from make_inputs import verify_inherited,SOURCE
P=pathlib.Path(__file__).resolve().parent

def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not pathlib.Path('TRANSFER_STARTED.json').exists();freeze=json.loads(pathlib.Path('INPUT_FREEZE.json').read_text());assert sha('SOURCE_SHA256SUMS')==freeze['source_manifest_sha256'] and sha('INPUT_SHA256SUMS')==freeze['input_manifest_sha256']
 for n,h in freeze['files'].items():assert sha(n)==h
 verify_inherited();start=time.time();assert freeze['freeze_unix']<start;save('TRANSFER_STARTED.json',dict(start=start,input_freeze_sha256=sha('INPUT_FREEZE.json'),job_id=os.environ['SLURM_JOB_ID']));targets={g:json.loads((P/(g+'_TARGETS.json')).read_text())['blocks'] for g in LAWS};pathlib.Path('raw').mkdir(exist_ok=True);blocks=[];nseq=nold=0;checks=collections.Counter();ops=collections.Counter();stages=[]
 with File('streams.jsonl.gz','r') as src,File('fresh_probe_masks.jsonl.gz','r') as freshsrc,File('RESIDENT_STATES.jsonl.gz','r') as residents:
  for b in range(24):
   sums={'RESIDENT40|'+g+'|'+m+'|'+k:0. for g in LAWS for m in MODES for k in MET}
   with File(SOURCE/('raw/block%02d.jsonl.gz'%b),'r') as controls,File('raw/block%02d.jsonl.gz'%b,'w') as out:
    for rep in range(8):
     stream=next(src);fresh=next(freshsrc);rr=next(residents);assert (stream['block'],stream['replicate'])==(fresh['block'],fresh['replicate'])==(rr['block'],rr['replicate'])==(b,rep) and rr['geometry']=='RECUR';prefixes={};seen=set()
     for _ in range(24):
      row=next(controls);assert (row['block'],row['replicate'])==(b,rep)
      if row['abundance']!='RESIDENT40' or row['geometry']!='RECUR':continue
      m=row['policy'];assert m in MODES and m not in seen;seen.add(m);r=row['record'];nold+=1;prefixes[m]=prefix(r)
      for k,x in r['utilities'].items():sums['RESIDENT40|FULL|'+m+'|'+k]+=x
      saved=dict(row,geometry='FULL',reuse_note='accepted047RESIDENT40/RECUR full numerical record unchanged');assert saved['record']==row['record'];out.write(saved);checks['reused_full_exact_records']+=1
     assert seen==set(MODES)
     for g in ('ZERO','HALF'):
      firsts={}
      for mode in MODES:
       rec=sequence(targets[g][b]['targets'],stream['draws'],mode,fresh['fresh'],rr['genotypes']);nseq+=1;assert prefix(rec)==prefixes[mode];checks['new_full_two_update_pairs']+=1
       if mode.startswith('ACTIVE'):firsts[mode[-2:]]=first(rec)
       elif mode.startswith('SHAM'):assert first(rec)==firsts[mode[-2:]];checks['active_sham_first_update']+=1
       for k,x in rec['utilities'].items():sums['RESIDENT40|'+g+'|'+mode+'|'+k]+=x
       for s in rec['steps']:ops.update(x['family'] for x in s['sources'][32:])
       out.write(dict(block=b,replicate=rep,geometry=g,policy=mode,abundance='RESIDENT40',record=rec,evidence_kind='new049target_law',cohort='reused047preparedRECUR'))
    assert next(controls,None) is None
   blocks.append(dict(block=b,values={k:x/8 for k,x in sums.items()}));save('BASE_BLOCKS.json',blocks);save('TRANSFER_PROGRESS.json',dict(blocks=b+1,new_sequences=nseq,reused_sequences=nold,elapsed_seconds=time.time()-start));stages.append(telemetry('block-%02d'%b));print('Block',b,flush=True)
  assert next(src,None) is None and next(freshsrc,None) is None and next(residents,None) is None
 assert nseq==2304 and nold==1152 and checks==dict(new_full_two_update_pairs=2304,active_sham_first_update=768,reused_full_exact_records=1152);assert ops==dict(probe=2949120,scout=2949120,local_child=2949120)
 save('PREFIX_CHECKS.json',dict(status='PASS',**checks));save('BUDGET.json',dict(new_sequences=2304,new_updates=92160,candidate_queries=11796480,initial_queries=73728,underlying_loss_computations=11870208,state_measurements=94464,nonparent_candidates=8847360,nonparent_sources=ops,old_paths_used=1152,old_paths_rerun=0,source_resident_states=192,preparation_previously_incurred_calls=989184,extra_diagnostic_loss_calls=0,new_seeds=48,innovation_getrandbits32=912,copy_getrandbits1=912,reference_optimization=0,pretraining=0,fixture_work='FIXTURE_WORK.json separate'));save('TRANSFER_RUNTIME.json',dict(elapsed_seconds=time.time()-start,stages=stages))
if __name__=='__main__':main()
