import os,json,pathlib,time,collections
from model import sequence
from analysis import MET,MODES,LAWS,STARTS
from signatures import first,prefix
from io_utils import File,save,sha,telemetry
from make_inputs import verify_inherited,SOURCE
P=pathlib.Path(__file__).resolve().parent

def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not pathlib.Path('TRANSFER_STARTED.json').exists();freeze=json.loads(pathlib.Path('INPUT_FREEZE.json').read_text());assert sha('SOURCE_SHA256SUMS')==freeze['source_manifest_sha256'] and sha('INPUT_SHA256SUMS')==freeze['input_manifest_sha256']
 for n,h in freeze['files'].items():assert sha(n)==h
 verify_inherited();start=time.time();assert freeze['freeze_unix']<start;save('TRANSFER_STARTED.json',dict(start=start,input_freeze_sha256=sha('INPUT_FREEZE.json'),job_id=os.environ['SLURM_JOB_ID']));targets={g:json.loads((P/(g+'_TARGETS.json')).read_text())['blocks'] for g in LAWS};pathlib.Path('raw').mkdir(exist_ok=True);blocks=[];nseq=nold=0;checks=collections.Counter();ops=collections.Counter();stages=[]
 with File('streams.jsonl.gz','r') as src,File('fresh_probe_masks.jsonl.gz','r') as freshsrc,File('RESIDENT_STATES.jsonl.gz','r') as residents,File('survival_streams.jsonl.gz','r') as survsrc:
  for b in range(24):
   sums={a+'|'+g+'|'+m+'|'+k:0. for a in STARTS for g in LAWS for m in MODES for k in MET}
   with File(SOURCE/('raw/block%02d.jsonl.gz'%b),'r') as controls,File('raw/block%02d.jsonl.gz'%b,'w') as out:
    for rep in range(8):
     stream=next(src);fresh=next(freshsrc);rr=next(residents);surv=next(survsrc);assert (surv['block'],surv['replicate'])==(b,rep);assert (stream['block'],stream['replicate'])==(fresh['block'],fresh['replicate'])==(rr['block'],rr['replicate'])==(b,rep) and rr['geometry']=='RECUR';prefixes={};seen=set()
     for _ in range(18):
      row=next(controls);assert (row['block'],row['replicate'])==(b,rep) and row['abundance']=='RESIDENT40';g=row['geometry'];m=row['policy'];assert (g,m) not in seen;seen.add((g,m));r=row['record'];nold+=1
      assert all(s['S_pen']>=0 for s in r['steps'])
      for k,x in r['utilities'].items():sums['BEST32|'+g+'|'+m+'|'+k]+=x
      saved=dict(row,abundance='BEST32');assert saved['record']==row['record'];out.write(saved);checks['reused_best32_exact_records']+=1
     assert seen==set((g,m) for g in LAWS for m in MODES)
     for g in LAWS:
      firsts={}
      for mode in MODES:
       rec=sequence(targets[g][b]['targets'],stream['draws'],mode,fresh['fresh'],rr['genotypes'],surv['survival']);nseq+=1;prefixes[g,mode]=prefix(rec)
       if mode.startswith('ACTIVE'):firsts[mode[-2:]]=first(rec)
       elif mode.startswith('SHAM'):assert first(rec)==firsts[mode[-2:]];checks['active_sham_first_update']+=1
       for k,x in rec['utilities'].items():sums['RACE32|'+g+'|'+mode+'|'+k]+=x
       for st in rec['steps']:ops.update(x['family'] for x in st['sources'][32:])
       out.write(dict(block=b,replicate=rep,geometry=g,policy=mode,abundance='RACE32',record=rec,evidence_kind='new050survival',cohort='reused047preparedRECUR'))
     for g in ('ZERO','HALF'):
      for mode in MODES:assert prefixes[g,mode]==prefixes['FULL',mode];checks['within_race_two_update_pairs']+=1
    assert next(controls,None) is None
   blocks.append(dict(block=b,values={k:x/8 for k,x in sums.items()}));save('BASE_BLOCKS.json',blocks);save('TRANSFER_PROGRESS.json',dict(blocks=b+1,new_sequences=nseq,reused_sequences=nold,elapsed_seconds=time.time()-start));stages.append(telemetry('block-%02d'%b));print('Block',b,flush=True)
  assert next(src,None) is None and next(freshsrc,None) is None and next(residents,None) is None and next(survsrc,None) is None
 assert nseq==3456 and nold==3456 and checks==dict(within_race_two_update_pairs=2304,active_sham_first_update=1152,reused_best32_exact_records=3456);assert ops==dict(probe=4423680,scout=4423680,local_child=4423680)
 save('PREFIX_CHECKS.json',dict(status='PASS',**checks));save('BUDGET.json',dict(new_sequences=3456,new_updates=138240,candidate_queries=17694720,initial_queries=110592,underlying_loss_computations=17805312,state_measurements=141696,nonparent_candidates=13271040,nonparent_sources=ops,old_paths_used=3456,old_paths_rerun=0,source_resident_states=192,preparation_previously_incurred_calls=989184,extra_diagnostic_loss_calls=0,new_seeds=192,survival_getrandbits52=983040,reference_optimization=0,pretraining=0,fixture_work='FIXTURE_WORK.json separate'));save('TRANSFER_RUNTIME.json',dict(elapsed_seconds=time.time()-start,stages=stages))
if __name__=='__main__':main()
