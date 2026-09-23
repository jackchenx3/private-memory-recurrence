import os,pathlib,json,time,collections
from model import all_policy,stage,rebase
from io_utils import File,save,sha,telemetry
from make_inputs import validate_freeze
from analysis import LAWS,BACKGROUNDS
P=pathlib.Path(__file__).resolve().parent

def describe(rec):
 out={}
 for name,pop in [('initial',rec['populations'][0]),('terminal',rec['populations'][-1])]:
  out[name]=dict(unique_genotypes=len(set(q[0] for q in pop)),unique_founders=len(set(q[2] for q in pop)),founder_counts=dict(collections.Counter(str(q[2]) for q in pop)),unique_cached_genotypes=len(set(q[3][0] for q in pop)),cache_time_counts=dict(collections.Counter(str(q[3][1]) for q in pop)),cache_position_counts=dict(collections.Counter(str(q[3][2]) for q in pop)))
 return dict(raw_metrics=rec['utilities']['raw'],descriptions=out,raw_accuracy=rec['raw_accuracies'])
def main():
 os.chdir(P);assert os.environ.get('SLURM_JOB_ID') and not pathlib.Path('PREPARATION_STARTED.json').exists();q=validate_freeze('INPUT_FREEZE.json');start=time.time();assert q['freeze_unix']<start;save('PREPARATION_STARTED.json',dict(start_unix=start,input_freeze_sha256=sha('INPUT_FREEZE.json')));targets={g:json.loads(pathlib.Path('reused052_'+g+'_TARGETS.json').read_text())['blocks'] for g in LAWS};pathlib.Path('preparation').mkdir();n=0;summaries=[];stages=[]
 with File('reused052_streams.jsonl.gz','r') as src,File('reused052_fresh_probe_masks.jsonl.gz','r') as fresh,File('reused052_survival_streams.jsonl.gz','r') as surv,File('reused052_RESIDENT_STATES.jsonl.gz','r') as roots,File('RESIDENT_STATES.jsonl.gz','w') as states,File('PREPARATION_DESCRIPTIONS.jsonl.gz','w') as descriptions:
  for b in range(24):
   sums=collections.defaultdict(lambda:collections.defaultdict(float))
   with File('preparation/block%02d.jsonl.gz'%b,'w') as out:
    for r in range(8):
     row,fo,so,rr=next(src),next(fresh),next(surv),next(roots);assert all((x['block'],x['replicate'])==(b,r) for x in (row,fo,so,rr))
     for g in LAWS:
      ts=targets[g][b]['targets']
      for bg in BACKGROUNDS:
       rec=stage(ts,row['draws'],all_policy(rr['genotypes'],bg),0,fo['fresh'],so['survival']);rebased,provenance=rebase(rec['populations'][-1]);desc=describe(rec);out.write(dict(block=b,replicate=r,geometry=g,background=bg,record=rec));states.write(dict(block=b,replicate=r,geometry=g,background=bg,population=rec['populations'][-1],rebased_population=rebased,founder_rebase_map=provenance,last_preparation_target=ts[-1],last_two_preparation_targets=ts[-2:],source='new055 all-'+bg+' 40-update endpoint; unfiltered'));descriptions.write(dict(block=b,replicate=r,geometry=g,background=bg,**desc));n+=1
       for k,x in desc['raw_metrics'].items():sums[g,bg]['raw_'+k]+=x/8
       for k in ('unique_genotypes','unique_founders','unique_cached_genotypes'):sums[g,bg]['terminal_'+k]+=desc['descriptions']['terminal'][k]/8
    for (g,bg),vs in sums.items():summaries.append(dict(block=b,geometry=g,background=bg,paths=8,values=dict(vs)))
   stages.append(telemetry('preparation-block-%02d'%b));save('PREPARATION_PROGRESS.json',dict(blocks=b+1,paths=n,elapsed_seconds=time.time()-start));print('Prepared block',b,flush=True)
  assert all(next(s,None) is None for s in (src,fresh,surv,roots))
 assert n==1152 and len(summaries)==144;save('PREPARATION_BLOCK_SUMMARIES.json',summaries);save('RESIDENT_PROVENANCE.json',dict(status='PASS',source_genotype_arrays=192,new_preparation_paths=1152,all_states_included=True,outcome_filtering=False,cache_preservation='exact original cache tuples, times and positions',founder_rebase='current slots0..31 with complete reverse map',transfer_paths_per_prepared_state=3));save('PREPARATION_BUDGET.json',dict(paths=1152,updates=46080,candidate_queries=5898240,initial_queries=36864,underlying_loss_computations=5935104,state_measurements=47232,extra_diagnostic_loss_calls=0));save('PREPARATION_RUNTIME.json',dict(elapsed_seconds=time.time()-start,stages=stages))
 names=['RESIDENT_STATES.jsonl.gz','RESIDENT_PROVENANCE.json','PREPARATION_DESCRIPTIONS.jsonl.gz','PREPARATION_BLOCK_SUMMARIES.json','PREPARATION_BUDGET.json','PREPARATION_RUNTIME.json']+['preparation/block%02d.jsonl.gz'%b for b in range(24)];hs={n:sha(n) for n in names};pathlib.Path('RESIDENT_SHA256SUMS').write_text(''.join(h+'  '+n+'\n' for n,h in hs.items()));save('RESIDENT_FREEZE.json',dict(stage='all1152 complete endpoints before transfer; no filtering',freeze_unix=time.time(),files=hs,source_manifest_sha256=sha('SOURCE_SHA256SUMS'),resident_manifest_sha256=sha('RESIDENT_SHA256SUMS'),exogenous_input_freeze_sha256=sha('INPUT_FREEZE.json')))
if __name__=='__main__':main()
