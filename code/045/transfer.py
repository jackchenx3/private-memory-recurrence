import os,json,pathlib,time,collections
from model import sequence
from analysis import MET,MODES,NEW,OLD as OLD_MODES
from signatures import prefix
from io_utils import File,save,sha,telemetry
from make_inputs import verify_inherited,OLD,BASE
P=pathlib.Path(__file__).resolve().parent

def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not pathlib.Path('TRANSFER_STARTED.json').exists();freeze=json.loads(pathlib.Path('INPUT_FREEZE.json').read_text());assert sha('SOURCE_SHA256SUMS')==freeze['source_manifest_sha256'] and sha('INPUT_SHA256SUMS')==freeze['input_manifest_sha256']
 for n,h in freeze['files'].items():assert sha(n)==h
 verify_inherited();start=time.time();assert freeze['freeze_unix']<start;save('TRANSFER_STARTED.json',dict(start=start,input_freeze_sha256=sha('INPUT_FREEZE.json'),job_id=os.environ['SLURM_JOB_ID']));targets={g:json.loads((BASE/(g+'_TARGETS.json')).read_text())['blocks'] for g in ('IID','RECUR')};pathlib.Path('raw').mkdir(exist_ok=True);blocks=[];nseq=nold=0;checks=collections.Counter();ops=collections.Counter();stages=[]
 with File(BASE/'streams.jsonl.gz','r') as src,File('fresh_probe_masks.jsonl.gz','r') as freshsrc:
  for b in range(24):
   sums={'RARE|'+g+'|'+m+'|'+k:0. for g in targets for m in MODES for k in MET}
   with File(OLD/('raw/block%02d.jsonl.gz'%b),'r') as controls,File('raw/block%02d.jsonl.gz'%b,'w') as out:
    for rep in range(8):
     stream=next(src);fresh=next(freshsrc);assert (stream['block'],stream['replicate'])==(fresh['block'],fresh['replicate'])==(b,rep);prefixes={}
     for _ in range(16):
      row=next(controls);assert (row['block'],row['replicate'])==(b,rep)
      if row['abundance']!='RARE':continue
      g,mode=row['geometry'],row['policy'];assert mode in OLD_MODES;r=row['record'];nold+=1
      for k,x in r['utilities'].items():sums['RARE|'+g+'|'+mode+'|'+k]+=x
      out.write(dict(row,reuse_note='authenticated stored044 RARE control; original evidence_kind preserved'))
     for g in ('IID','RECUR'):
      for mode in NEW:
       rec=sequence(targets[g][b]['targets'],stream['draws'],mode,fresh['fresh']);nseq+=1
       if g=='IID':prefixes[mode]=prefix(rec)
       else:assert prefix(rec)==prefixes[mode];checks['same_mode_full_two_update']+=1
       for k,x in rec['utilities'].items():sums['RARE|'+g+'|'+mode+'|'+k]+=x
       for s in rec['steps']:ops.update(x['family'] for x in s['sources'][32:])
       out.write(dict(block=b,replicate=rep,geometry=g,policy=mode,abundance='RARE',record=rec,evidence_kind='new045fresh_probe',cohort='reused041'))
    assert next(controls,None) is None
   blocks.append(dict(block=b,values={k:x/8 for k,x in sums.items()}));save('BASE_BLOCKS.json',blocks);save('TRANSFER_PROGRESS.json',dict(blocks=b+1,new_sequences=nseq,reused_sequences=nold,elapsed_seconds=time.time()-start));stages.append(telemetry('block-%02d'%b));print('Block',b,flush=True)
  assert next(src,None) is None and next(freshsrc,None) is None
 assert nseq==768 and nold==1536 and checks==dict(same_mode_full_two_update=384);assert ops==dict(probe=983040,scout=983040,local_child=983040)
 save('PREFIX_CHECKS.json',dict(status='PASS',**checks));save('BUDGET.json',dict(new_sequences=768,new_updates=30720,candidate_queries=3932160,initial_queries=24576,underlying_loss_computations=3956736,state_measurements=31488,nonparent_candidates=2949120,nonparent_sources=ops,old_paths_used=1536,extra_diagnostic_loss_calls=0,new_seeds=192,new_draws=245760,reference_optimization=0,pretraining=0,fixture_work='FIXTURE_WORK.json separate'));save('TRANSFER_RUNTIME.json',dict(elapsed_seconds=time.time()-start,stages=stages))
if __name__=='__main__':main()
