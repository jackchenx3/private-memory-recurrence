"""Independent36-estimate arithmetic and prospectively selected40-path raw audit."""
import collections,math
from common import *
from raw_audit import audit_record,canon
from accepted_inputs055 import extend_targets
from seed_design import verify_roster

def recompute(panel,indices):
 # Coefficients and endpoint arithmetic deliberately do not call analysis.py.
 metrics=('U1','U_LATE','U40','U_ALL','D1','D40');arms=('STAY','PULSE','CONT')
 coefs={'STAY':(1,0,0),'PULSE':(0,1,0),'CONT':(0,0,1),'PULSE_MINUS_STAY':(-1,1,0),'CONT_MINUS_STAY':(-1,0,1),'PULSE_MINUS_CONT':(0,1,-1)};block=collections.defaultdict(list)
 for b in range(24):
  replicates=collections.defaultdict(list)
  for r in range(8):
   estimates=[]
   for arm in arms:
    values=[]
    for placement in (0,1):
     s=panel[b,r,'STAY' if arm=='STAY' else arm+str(placement)];a=s['accuracy'];f=s['founder'][str(placement)];assert len(a)==len(f)==41 and f[0]==1/32
     values.append((a[1],math.fsum(a[2:])/39,a[40],math.fsum(a[1:])/40,f[1]-f[0],f[40]-f[0]))
    estimates.append([(x+y)/2 for x,y in zip(*values)])
   for group,c in coefs.items():
    for j,m in enumerate(metrics):replicates[group+'|'+m].append(math.fsum(c[i]*estimates[i][j] for i in range(3)))
  for key,xs in replicates.items():block[key].append(math.fsum(xs)/8)
 weights=[collections.Counter(row) for row in indices];out={}
 for key,xs in block.items():
  ds=sorted(math.fsum(xs[i]*n for i,n in row.items())/24 for row in weights);ci=[]
  for p in (.025,.975):
   position=(len(ds)-1)*p;i=math.floor(position);w=position-i;ci.append((1-w)*ds[i]+w*ds[math.ceil(position)])
  out[key]=dict(mean=math.fsum(xs)/24,ci95=ci)
 assert len(out)==36
 return out

def main():
 verify_manifest('SOURCE_SHA256SUMS');verify_manifest('SCIENCE_SHA256SUMS');check_stage('INPUT');verify_references();verify_roster(read('SEEDS.json'),read('PRIOR_SEED_INVENTORY.json')['integers'])
 assert read('DESIGN_FREEZE.json')['freeze_unix']<read('INPUT_FREEZE.json')['freeze_unix']<read('TRANSFER_STARTED.json')['start_unix']
 st=states();ds=keyed('streams.jsonl.gz');fresh=keyed('fresh_probe_masks.jsonl.gz');surv=keyed('survival_streams.jsonl.gz');targets=read('TARGET_TABLE.json');hist=read('PREPARATION_TARGETS.json');td=read('TARGET_LAW_DRAWS.json')
 for b in range(24):
  assert targets[b]['targets']==extend_targets(hist[b]['targets'],td[b]['innovations'],td[b]['copy_bits'],'HALF')
  for r in range(8):assert st[b,r]['source_state']['last_two_preparation_targets']==hist[b]['targets'][-2:]
 panel={}
 for row in rows(P/'TIME_SERIES.jsonl.gz'):
  key=row['block'],row['replicate'],row['configuration'];assert key not in panel;panel[key]=row['series']
 assert len(panel)==960
 counts=collections.Counter();first={}
 for row in rows(P/'raw/block00.jsonl.gz'):
  b,r,cfg=row['block'],row['replicate'],row['configuration'];assert b==0;d=ds[b,r]['draws'];labels=d['labels'];state=st[b,r]['source_state'];slot=None if cfg=='STAY' else labels[int(cfg[-1])]
  initial=[(p[0],2 if i==slot else 1,p[2],p[3]) for i,p in enumerate(state['rebased_population'])];rec=row['record'];assert row['slot']==slot and row['founder_ids']==labels[:2] and row['source_row_index']==st[b,r]['source_row_index'] and row['source_founder_rebase_map']==state['founder_rebase_map']
  counts.update(audit_record(rec,targets[b]['targets'],d,initial,fresh[b,r]['fresh'],surv[b,r]['survival'],state['last_preparation_target']))
  s=panel[b,r,cfg];assert s['accuracy']==rec['raw_accuracies'] and s['expression_carried']==rec['expression_carried'] and s['expression_selected']==rec['expression_selected']
  for i,fid in enumerate(labels[:2]):assert s['founder'][str(i)]==[sum(q[2]==fid for q in pop)/32. for pop in rec['populations']]
  if cfg!='STAY':
   key=(r,int(cfg[-1]));value=dict(initial=rec['populations'][0],initial_queries=rec['initial_queries'],first_step=rec['steps'][0])
   if cfg.startswith('PULSE'):first[key]=value
   else:assert first[key]==value
 assert counts['paths']==40 and counts['recorded_scores']==206080 and counts['race_keys']==204800
 independent=recompute(panel,read('BOOTSTRAP_INDICES.json'));est=read('ESTIMATES.json');assert set(est)==set(independent);worst=0
 for k,q in independent.items():
  error=max([abs(q['mean']-est[k]['mean'])]+[abs(a-b) for a,b in zip(q['ci95'],est[k]['ci95'])]);assert error<2e-13,(k,error);worst=max(worst,error)
 for k in ('PULSE_MINUS_CONT|U1','PULSE_MINUS_CONT|D1'):assert independent[k]['mean']==0 and independent[k]['ci95']==[0,0]
 lo,hi=est['PULSE_MINUS_STAY|U40']['ci95'];dec=read('ASSESSMENT.json')['decisions'];assert dec['direction']==('supports_positive' if lo>0 else 'contradicts_positive' if hi<0 else 'unresolved');assert dec['benchmark']==('above_one_matching_bit' if lo>1/1024 else 'below_one_matching_bit' if hi<1/1024 else 'overlaps_one_matching_bit')
 assert read('BUDGET.json')['total_objective_calls']==4945920 and read('BUDGET.json')['new_paths']==960 and read('BUDGET.json')['new_preparations']==0
 save('INDEPENDENT_AUDIT.json',dict(status='PASS',raw_audit_block=0,raw_checks=counts,checked_estimates=36,maximum_absolute_discrepancy=worst,tolerance=2e-13,first_update_coupling_pairs=16,structural_zero_keys=['PULSE_MINUS_CONT|U1','PULSE_MINUS_CONT|D1'],recorded_score_reconstructions=206080,new_scientific_calls=0,new_paths=0,new_random_draws=0))
 print(json.dumps(read('INDEPENDENT_AUDIT.json')))
if __name__=='__main__':main()
