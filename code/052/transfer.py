import os,pathlib,json,time,collections
from model import sequence
from views import prefix
from analysis import LAWS,COSTS,CONFIGS,paired
from io_utils import File,save,sha,telemetry
from make_inputs import validate_freeze
P=pathlib.Path(__file__).resolve().parent

def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not pathlib.Path('TRANSFER_STARTED.json').exists();ex=validate_freeze('INPUT_FREEZE.json');freeze=validate_freeze('RESIDENT_FREEZE.json');start=time.time();assert ex['freeze_unix']<freeze['freeze_unix']<start and freeze['exogenous_input_freeze_sha256']==sha('INPUT_FREEZE.json');save('TRANSFER_STARTED.json',dict(start=start,resident_freeze_sha256=sha('RESIDENT_FREEZE.json'),input_freeze_sha256=sha('INPUT_FREEZE.json'),job_id=os.environ['SLURM_JOB_ID']));targets={g:json.loads((P/(g+'_TARGETS.json')).read_text())['blocks'] for g in LAWS};pathlib.Path('raw').mkdir();blocks=[];nseq=0;checks=collections.Counter();ops=collections.Counter();stages=[]
 with File('streams.jsonl.gz','r') as src,File('fresh_probe_masks.jsonl.gz','r') as fs,File('RESIDENT_STATES.jsonl.gz','r') as rs,File('survival_streams.jsonl.gz','r') as ss:
  for b in range(24):
   sums=collections.defaultdict(float)
   with File('raw/block%02d.jsonl.gz'%b,'w') as out:
    for rep in range(8):
     stream=next(src);fresh=next(fs);rr=next(rs);surv=next(ss);assert all((q['block'],q['replicate'])==(b,rep) for q in (stream,fresh,rr,surv));rows={};prefixes={}
     for g in LAWS:
      assert targets[g][b]['targets'][:2]==rr['preparation_first_pair']
      for c in COSTS:
       for cfg in CONFIGS:
        rec=sequence(targets[g][b]['targets'],stream['draws'],cfg,int(c[-1]),fresh['fresh'],rr['genotypes'],surv['survival']);nseq+=1;rows[g,c,cfg]=rec['utilities'];prefixes[g,c,cfg]=prefix(rec)
        for st in rec['steps']:ops.update(x['family'] for x in st['sources'][32:])
        out.write(dict(block=b,replicate=rep,geometry=g,cost=c,configuration=cfg,logical_roles={'0':'R','1':'H','2':'F'},record=rec,evidence_kind='new052independentpreparedcompetition',cohort='independent052'))
       for k,x in paired({cfg:rows[g,c,cfg] for cfg in CONFIGS}).items():sums[g+'|'+c+'|'+k]+=x
     for g in ('ZERO','HALF'):
      for c in COSTS:
       for cfg in CONFIGS:assert prefixes[g,c,cfg]==prefixes['FULL',c,cfg];checks['within_configuration_two_update_pairs']+=1
   assert len(sums)==624;blocks.append(dict(block=b,values={k:x/8 for k,x in sums.items()}));save('BASE_BLOCKS.json',blocks);save('TRANSFER_PROGRESS.json',dict(blocks=b+1,new_sequences=nseq,reused_sequences=0,elapsed_seconds=time.time()-start));stages.append(telemetry('block-%02d'%b));print('Block',b,flush=True)
  assert all(next(q,None) is None for q in (src,fs,rs,ss))
 assert nseq==6912 and checks==dict(within_configuration_two_update_pairs=4608);assert ops==dict(probe=8847360,scout=8847360,local_child=8847360)
 save('PREFIX_CHECKS.json',dict(status='PASS',**checks));save('BUDGET.json',dict(new_sequences=6912,new_updates=276480,candidate_queries=35389440,initial_queries=221184,underlying_loss_computations=35610624,state_measurements=283392,nonparent_candidates=26542080,nonparent_sources=ops,old_paths_used=0,old_paths_rerun=0,source_resident_states=192,new_preparation_calls=989184,total_scientific_paths=7104,total_updates=284160,total_loss_computations=36599808,total_states=291264,extra_diagnostic_loss_calls=0,new_seeds=1993,new_random_draws='INPUT_GENERATION.json exact API counts',fixture_work='FIXTURE_WORK.json separate'));save('TRANSFER_RUNTIME.json',dict(elapsed_seconds=time.time()-start,stages=stages))
if __name__=='__main__':main()
