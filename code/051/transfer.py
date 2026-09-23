import os,pathlib,json,time,collections
from model import sequence
from views import view,prefix
from analysis import LAWS,COSTS,NEW,CONFIGS,paired
from io_utils import File,save,sha,telemetry
from make_inputs import verify_inherited,SOURCE
P=pathlib.Path(__file__).resolve().parent

def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not pathlib.Path('TRANSFER_STARTED.json').exists();freeze=json.loads(pathlib.Path('INPUT_FREEZE.json').read_text());assert sha('SOURCE_SHA256SUMS')==freeze['source_manifest_sha256'] and sha('INPUT_SHA256SUMS')==freeze['input_manifest_sha256']
 for n,h in freeze['files'].items():assert sha(n)==h
 verify_inherited();start=time.time();assert freeze['freeze_unix']<start;save('TRANSFER_STARTED.json',dict(start=start,input_freeze_sha256=sha('INPUT_FREEZE.json'),job_id=os.environ['SLURM_JOB_ID']));targets={g:json.loads((P/(g+'_TARGETS.json')).read_text())['blocks'] for g in LAWS};pathlib.Path('raw').mkdir(exist_ok=True);blocks=[];oldblocks=[];nseq=nold=0;checks=collections.Counter();ops=collections.Counter();stages=[]
 with File('streams.jsonl.gz','r') as src,File('fresh_probe_masks.jsonl.gz','r') as fs,File('RESIDENT_STATES.jsonl.gz','r') as rs,File('survival_streams.jsonl.gz','r') as ss:
  for b in range(24):
   sums=collections.defaultdict(float);oldsums=collections.defaultdict(float)
   with File(SOURCE/('raw/block%02d.jsonl.gz'%b),'r') as controls,File('raw/block%02d.jsonl.gz'%b,'w') as out:
    for rep in range(8):
     stream=next(src);fresh=next(fs);rr=next(rs);surv=next(ss);assert all((q['block'],q['replicate'])==(b,rep) for q in (stream,fresh,rr,surv));assert rr['geometry']=='RECUR';rows={};prefixes={}
     for _ in range(36):
      row=next(controls);assert (row['block'],row['replicate'])==(b,rep)
      if row['abundance']!='RACE32' or row['policy'].startswith('SHAM'):continue
      g=row['geometry'];c=row['policy'][-2:];cfg='H0' if row['policy'].startswith('ACTIVE') else 'F0';saved=dict(row,configuration=cfg,cost=c,logical_roles={'0':'R','1':cfg[0]},reuse_note='050 binary record unchanged; external logical-role mapping only');assert saved['record']==row['record'];assert (g,c,cfg) not in rows;rows[g,c,cfg]=view(saved)[1];out.write(saved);nold+=1;checks['old_exact_records']+=1
      for k,x in row['record']['utilities'].items():oldsums['RACE32|'+g+'|'+row['policy']+'|'+k]+=x
     assert len(rows)==12
     for g in LAWS:
      for c in COSTS:
       for cfg in NEW:
        rec=sequence(targets[g][b]['targets'],stream['draws'],cfg,int(c[-1]),fresh['fresh'],rr['genotypes'],surv['survival']);nseq+=1;rows[g,c,cfg]=rec['utilities'];prefixes[g,c,cfg]=prefix(rec)
        for st in rec['steps']:ops.update(x['family'] for x in st['sources'][32:])
        out.write(dict(block=b,replicate=rep,geometry=g,cost=c,configuration=cfg,logical_roles={'0':'R','1':'H','2':'F'},record=rec,evidence_kind='new051directcompetition',cohort='reused047preparedRECUR'))
       for k,x in paired({cfg:rows[g,c,cfg] for cfg in CONFIGS}).items():sums[g+'|'+c+'|'+k]+=x
     for g in ('ZERO','HALF'):
      for c in COSTS:
       for cfg in NEW:assert prefixes[g,c,cfg]==prefixes['FULL',c,cfg];checks['within_configuration_two_update_pairs']+=1
    assert next(controls,None) is None
   assert len(sums)==624 and len(oldsums)==312;blocks.append(dict(block=b,values={k:x/8 for k,x in sums.items()}));oldblocks.append(dict(block=b,values={k:x/8 for k,x in oldsums.items()}));save('BASE_BLOCKS.json',blocks);save('OLD_BASE_BLOCKS.json',oldblocks);save('TRANSFER_PROGRESS.json',dict(blocks=b+1,new_sequences=nseq,reused_sequences=nold,elapsed_seconds=time.time()-start));stages.append(telemetry('block-%02d'%b));print('Block',b,flush=True)
  assert all(next(q,None) is None for q in (src,fs,rs,ss))
 assert nseq==4608 and nold==2304 and checks==dict(within_configuration_two_update_pairs=3072,old_exact_records=2304);assert ops==dict(probe=5898240,scout=5898240,local_child=5898240)
 save('PREFIX_CHECKS.json',dict(status='PASS',**checks));save('BUDGET.json',dict(new_sequences=4608,new_updates=184320,candidate_queries=23592960,initial_queries=147456,underlying_loss_computations=23740416,state_measurements=188928,nonparent_candidates=17694720,nonparent_sources=ops,old_paths_used=2304,old_paths_rerun=0,source_resident_states=192,preparation_previously_incurred_calls=989184,extra_diagnostic_loss_calls=0,new_seeds=0,new_random_draws=0,fixture_work='FIXTURE_WORK.json separate'));save('TRANSFER_RUNTIME.json',dict(elapsed_seconds=time.time()-start,stages=stages))
if __name__=='__main__':main()
