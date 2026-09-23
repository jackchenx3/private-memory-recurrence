import os,pathlib,json,time,collections
from model import sequence
from lineages import extract,prefix,time_series
from analysis import LAWS,COSTS,NEW,CONFIGS,paired
from io_utils import File,save,sha,telemetry
from make_inputs import verify_inherited,SOURCE
P=pathlib.Path(__file__).resolve().parent

def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not pathlib.Path('TRANSFER_STARTED.json').exists();freeze=json.loads(pathlib.Path('INPUT_FREEZE.json').read_text());assert sha('SOURCE_SHA256SUMS')==freeze['source_manifest_sha256'] and sha('INPUT_SHA256SUMS')==freeze['input_manifest_sha256']
 for n,h in freeze['files'].items():assert sha(n)==h
 verify_inherited();start=time.time();assert freeze['freeze_unix']<start;save('TRANSFER_STARTED.json',dict(start=start,input_freeze_sha256=sha('INPUT_FREEZE.json'),job_id=os.environ['SLURM_JOB_ID']));targets={g:json.loads((P/(g+'_TARGETS.json')).read_text())['blocks'] for g in LAWS};pathlib.Path('raw').mkdir();blocks=[];nseq=nold=0;checks=collections.Counter();ops=collections.Counter();stages=[]
 with File('streams.jsonl.gz','r') as src,File('fresh_probe_masks.jsonl.gz','r') as fs,File('RESIDENT_STATES.jsonl.gz','r') as rs,File('survival_streams.jsonl.gz','r') as ss,File('TIME_SERIES_IDENTITIES.jsonl.gz','w') as tout:
  for b in range(24):
   sums=collections.defaultdict(float)
   with File(SOURCE/('raw/block%02d.jsonl.gz'%b),'r') as controls,File('raw/block%02d.jsonl.gz'%b,'w') as out:
    for rep in range(8):
     stream=next(src);fresh=next(fs);rr=next(rs);surv=next(ss);assert all((q['block'],q['replicate'])==(b,rep) for q in (stream,fresh,rr,surv));rows={};prefixes={};timelines={}
     for _ in range(36):
      row=next(controls);assert (row['block'],row['replicate'])==(b,rep)
      if row['configuration'] not in ('MIX0','MIX1'):continue
      g,c,cfg=row['geometry'],row['cost'],row['configuration'];freq,u=extract(row['record'],stream['draws']['labels']);saved=dict(row,founder_ids=stream['draws']['labels'][:2],founder_frequencies=freq,reuse_note='052 mixed record unchanged; no propagation');assert saved['record']==row['record'];rows[g,c,cfg]=u;timelines[g,c,cfg]=dict(founders=freq,accuracy=saved['record']['raw_accuracies']);prefixes[g,c,cfg]=prefix(row['record']);out.write(saved);nold+=1;checks['old_exact_records']+=1
     assert len(rows)==12
     for g in LAWS:
      for c in COSTS:
       for cfg in NEW:
        rec=sequence(targets[g][b]['targets'],stream['draws'],cfg,int(c[-1]),fresh['fresh'],rr['genotypes'],surv['survival']);nseq+=1;freq,u=extract(rec,stream['draws']['labels']);rows[g,c,cfg]=u;timelines[g,c,cfg]=dict(founders=freq,accuracy=rec['raw_accuracies']);prefixes[g,c,cfg]=prefix(rec)
        for st in rec['steps']:ops.update(x['family'] for x in st['sources'][32:])
        out.write(dict(block=b,replicate=rep,geometry=g,cost=c,configuration=cfg,logical_roles={'0':'R','1':'H','2':'F'},founder_ids=stream['draws']['labels'][:2],founder_frequencies=freq,record=rec,evidence_kind='new053homotypic',cohort='reused052'))
       tout.write(dict(block=b,replicate=rep,geometry=g,cost=c,values=time_series({cfg:timelines[g,c,cfg] for cfg in CONFIGS})))
       for k,x in paired({cfg:rows[g,c,cfg] for cfg in CONFIGS}).items():sums[g+'|'+c+'|'+k]+=x
     for g in ('ZERO','HALF'):
      for c in COSTS:
       for cfg in CONFIGS:assert prefixes[g,c,cfg]==prefixes['FULL',c,cfg];checks['new_prefix_pairs' if cfg in NEW else 'stored_prefix_pairs']+=1
    assert next(controls,None) is None
   assert len(sums)==546;blocks.append(dict(block=b,values={k:x/8 for k,x in sums.items()}));save('BASE_BLOCKS.json',blocks);save('TRANSFER_PROGRESS.json',dict(blocks=b+1,new_sequences=nseq,reused_sequences=nold,elapsed_seconds=time.time()-start));stages.append(telemetry('block-%02d'%b));print('Block',b,flush=True)
  assert all(next(q,None) is None for q in (src,fs,rs,ss))
 assert nseq==nold==2304 and checks==dict(new_prefix_pairs=1536,stored_prefix_pairs=1536,old_exact_records=2304);assert ops==dict(probe=2949120,scout=2949120,local_child=2949120)
 save('PREFIX_CHECKS.json',dict(status='PASS',**checks));save('BUDGET.json',dict(new_sequences=2304,new_updates=92160,candidate_queries=11796480,initial_queries=73728,underlying_loss_computations=11870208,state_measurements=94464,nonparent_candidates=8847360,nonparent_sources=ops,old_paths_used=2304,old_paths_rerun=0,source_resident_states=192,new_preparation_calls=0,extra_diagnostic_loss_calls=0,new_seeds=0,new_random_draws=0,fixture_work='FIXTURE_WORK.json separate'));save('TRANSFER_RUNTIME.json',dict(elapsed_seconds=time.time()-start,stages=stages))
if __name__=='__main__':main()
