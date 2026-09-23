import os,json,pathlib,time,collections
from model import sequence
from analysis import MET,MODES,STARTS
from signatures import prefix,first
from io_utils import File,save,sha,telemetry
from make_inputs import verify_inherited
P=pathlib.Path(__file__).resolve().parent

def founder_counts(rec,labels):
 rows=[]
 for j,pop in enumerate(rec['populations']):
  counts=[0]*32
  for p in pop:counts[p[2]]+=1
  assert sum(counts)==32 and sum(x/32. for x in counts)/32==1/32.;assert counts[labels[0]]/32.==rec['frequencies'][j];rows.append(counts)
 return rows

def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not pathlib.Path('TRANSFER_STARTED.json').exists();freeze=json.loads(pathlib.Path('INPUT_FREEZE.json').read_text());assert sha('SOURCE_SHA256SUMS')==freeze['source_manifest_sha256'] and sha('INPUT_SHA256SUMS')==freeze['input_manifest_sha256']
 for n,h in freeze['files'].items():assert sha(n)==h
 verify_inherited();start=time.time();assert freeze['freeze_unix']<start;save('TRANSFER_STARTED.json',dict(start=start,input_freeze_sha256=sha('INPUT_FREEZE.json'),job_id=os.environ['SLURM_JOB_ID']));targets={g:json.loads((P/(g+'_TARGETS.json')).read_text())['blocks'] for g in ('IID','RECUR')};pathlib.Path('raw').mkdir(exist_ok=True);blocks=[];nseq=nold=0;checks=collections.Counter();ops=collections.Counter();stages=[]
 with File('streams.jsonl.gz','r') as src,File('fresh_probe_masks.jsonl.gz','r') as freshsrc,File('NEUTRAL_FOUNDER_COUNTS.jsonl.gz','w') as founderout,File('RESIDENT_STATES.jsonl.gz','r') as residents:
  for b in range(24):
   sums={a+'|'+g+'|'+m+'|'+k:0. for a in STARTS for g in targets for m in MODES for k in MET}
   with File('raw/block%02d.jsonl.gz'%b,'w') as out:
    for rep in range(8):
     stream=next(src);fresh=next(freshsrc);assert (stream['block'],stream['replicate'])==(fresh['block'],fresh['replicate'])==(b,rep);prefixes={}
     state={}
     for _ in range(2):
      rr=next(residents);assert (rr['block'],rr['replicate'])==(b,rep);state[rr['geometry']]=rr
     assert set(state)=={'IID','RECUR'}
     for startname in STARTS:
      for g in ('IID','RECUR'):
       activefirst={}
       for mode in MODES:
        rec=sequence(targets[g][b]['targets'],stream['draws'],mode,fresh['fresh'],[0]*32 if startname=='NAIVE' else state[g]['genotypes']);nseq+=1
        if mode.startswith('ACTIVE'):activefirst[mode[-2:]]=first(rec)
        elif mode.startswith('SHAM'):assert first(rec)==activefirst[mode[-2:]];checks['active_sham_first_update']+=1
        if mode=='SHAM_C0':
         fc=founder_counts(rec,stream['draws']['labels']);founderout.write(dict(block=b,replicate=rep,abundance=startname,geometry=g,selected_founder=stream['draws']['labels'][0],founder_counts=fc,conditional_mean=1/32.,not_independent_replicates=True));checks['neutral_founder_generations']+=41
        for k,x in rec['utilities'].items():sums[startname+'|'+g+'|'+mode+'|'+k]+=x
        for s in rec['steps']:ops.update(x['family'] for x in s['sources'][32:])
        out.write(dict(block=b,replicate=rep,geometry=g,policy=mode,abundance=startname,record=rec,evidence_kind='new047matched_start_challenge',cohort='reused046resident_states_new047futureinputs'))
   blocks.append(dict(block=b,values={k:x/8 for k,x in sums.items()}));save('BASE_BLOCKS.json',blocks);save('TRANSFER_PROGRESS.json',dict(blocks=b+1,new_sequences=nseq,reused_sequences=nold,elapsed_seconds=time.time()-start));stages.append(telemetry('block-%02d'%b));print('Block',b,flush=True)
  assert next(src,None) is None and next(freshsrc,None) is None and next(residents,None) is None
 assert nseq==4608 and nold==0 and checks==dict(active_sham_first_update=1536,neutral_founder_generations=31488);assert ops==dict(probe=5898240,scout=5898240,local_child=5898240)
 save('NEUTRAL_FOUNDER_CHECK.json',dict(status='PASS',paths=768,generations=31488,founders_per_path=32,conditional_mean_each_generation=1/32.,extra_objective_calls=0,additional_replicates=0));save('PREFIX_CHECKS.json',dict(status='PASS',**checks));save('BUDGET.json',dict(new_sequences=4608,new_updates=184320,candidate_queries=23592960,initial_queries=147456,underlying_loss_computations=23740416,state_measurements=188928,nonparent_candidates=17694720,nonparent_sources=ops,old_paths_used_as_initial_states=384,old_paths_rerun=0,preparation_previously_incurred_calls=1978368,extra_diagnostic_loss_calls=0,new_seeds=985,random_input_accounting='INPUT_GENERATION.json',reference_optimization=0,pretraining=0,fixture_work='FIXTURE_WORK.json separate'));save('TRANSFER_RUNTIME.json',dict(elapsed_seconds=time.time()-start,stages=stages))
if __name__=='__main__':main()
