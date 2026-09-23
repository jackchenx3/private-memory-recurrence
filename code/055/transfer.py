import os,pathlib,json,time,collections
from model import stage,substitute,rebase
from lineages import extract,time_series
from analysis import LAWS,BACKGROUNDS,CONFIGS,paired
from io_utils import File,save,sha,telemetry
from make_inputs import verify_inherited,validate_freeze
P=pathlib.Path(__file__).resolve().parent

def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not pathlib.Path('TRANSFER_STARTED.json').exists();inputs=validate_freeze('INPUT_FREEZE.json');resident=validate_freeze('RESIDENT_FREEZE.json');assert resident['exogenous_input_freeze_sha256']==sha('INPUT_FREEZE.json');verify_inherited();start=time.time();assert inputs['freeze_unix']<resident['freeze_unix']<start;save('TRANSFER_STARTED.json',dict(start=start,input_freeze_sha256=sha('INPUT_FREEZE.json'),resident_freeze_sha256=sha('RESIDENT_FREEZE.json'),job_id=os.environ['SLURM_JOB_ID']));targets={g:json.loads((P/(g+'_TARGETS.json')).read_text())['blocks'] for g in LAWS};pathlib.Path('raw').mkdir();blocks=[];n=0;states_used=0;ops=collections.Counter();stages=[]
 with File('streams.jsonl.gz','r') as src,File('fresh_probe_masks.jsonl.gz','r') as fs,File('reused052_fresh_probe_masks.jsonl.gz','r') as oldfs,File('RESIDENT_STATES.jsonl.gz','r') as rs,File('survival_streams.jsonl.gz','r') as ss,File('TIME_SERIES_IDENTITIES.jsonl.gz','w') as tout:
  for b in range(24):
   sums=collections.defaultdict(float)
   with File('raw/block%02d.jsonl.gz'%b,'w') as out:
    for rep in range(8):
     stream,fresh,oldfresh,surv=next(src),next(fs),next(oldfs),next(ss);assert all((q['block'],q['replicate'])==(b,rep) for q in (stream,fresh,oldfresh,surv));rows={};timelines={};labels=stream['draws']['labels']
     for g in LAWS:
      for bg in BACKGROUNDS:
       rr=next(rs);assert (rr['block'],rr['replicate'],rr['geometry'],rr['background'])==(b,rep,g,bg);rebased,provenance=rebase(rr['population']);assert json.loads(json.dumps(rebased))==rr['rebased_population'] and provenance==rr['founder_rebase_map'];assert rr['last_two_preparation_targets']==targets[g][b]['preparation_terminal_targets'];states_used+=1;initials=[]
       for variant in ('STAY','SWITCH0','SWITCH1'):
        cfg=bg+'_'+variant;slot=None if variant=='STAY' else labels[int(variant[-1])];pop=substitute(rebased,bg,slot);rec=stage(targets[g][b]['targets'],stream['draws'],pop,0,oldfresh['fresh']+fresh['fresh'],surv['survival'],40,rr['last_preparation_target']);freq,u=extract(rec,labels,cfg);n+=1;rows[cfg]=u;timelines[cfg]=dict(frequency=freq,accuracy=rec['raw_accuracies']);initials.append((rec['initial_raw_mismatches'],rec['raw_losses'][0]))
        for st in rec['steps']:ops.update(x['family'] for x in st['sources'][32:])
        out.write(dict(block=b,replicate=rep,geometry=g,cost='C0',configuration=cfg,background=bg,logical_roles={'0':'R','1':'H','2':'F'},founder_ids=labels[:2],rare_founder_id=slot,rare_policy=None if slot is None else ('H' if bg=='F' else 'F'),role_frequencies=freq,preparation_founder_map=provenance,record=rec,evidence_kind='new055 matched substitution',cohort='reused052 genotypes;new055 policy preparation'))
       assert initials[0]==initials[1]==initials[2]
      tout.write(dict(block=b,replicate=rep,geometry=g,cost='C0',values=time_series(timelines)))
      for k,x in paired(rows).items():sums[g+'|C0|'+k]+=x
   assert len(sums)==312;blocks.append(dict(block=b,values={k:x/8 for k,x in sums.items()}));save('BASE_BLOCKS.json',blocks);save('TRANSFER_PROGRESS.json',dict(blocks=b+1,new_sequences=n,prepared_states_used=states_used,elapsed_seconds=time.time()-start));stages.append(telemetry('block-%02d'%b));print('Transfer block',b,flush=True)
  assert all(next(q,None) is None for q in (src,fs,oldfs,rs,ss))
 assert n==3456 and states_used==1152 and ops==dict(probe=4423680,scout=4423680,local_child=4423680)
 save('TRANSFER_PAIRING_CHECK.json',dict(status='PASS',prepared_states=states_used,paths_per_prepared_state=3,matched_initial_raw_scores=True,source_cache_rebase_maps_preserved=True,cross_law_prefix_assumption=False));save('TRANSFER_BUDGET.json',dict(paths=3456,updates=138240,candidate_queries=17694720,initial_queries=110592,underlying_loss_computations=17805312,state_measurements=141696,nonparent_sources=ops,extra_diagnostic_loss_calls=0));save('BUDGET.json',dict(new_preparation_paths=1152,new_transfer_paths=3456,total_paths=4608,new_updates=184320,candidate_queries=23592960,initial_queries=147456,underlying_loss_computations=23740416,state_measurements=188928,nonparent_candidates=17694720,nonparent_sources={s:5898240 for s in ops},old_paths_used=0,old_paths_rerun=0,source_genotype_arrays=192,new_seed_records=1200,extra_diagnostic_loss_calls=0,fixture_work='FIXTURE_WORK.json separate'));save('TRANSFER_RUNTIME.json',dict(elapsed_seconds=time.time()-start,stages=stages))
if __name__=='__main__':main()
