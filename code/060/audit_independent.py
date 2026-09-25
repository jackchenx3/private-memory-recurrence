"""Independent81-estimate arithmetic and prospective96-path query/state audit."""
import math,collections
from common import *
from raw_audit import audit_record
from accepted_inputs055 import extend_targets
from seed_design import verify_roster

def recompute(panel,indices):
 cells=('EXACT_Q_ZERO','EXACT_Q_HALF','NOISY_Q_ZERO','NOISY_Q_HALF')
 coefs=((1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1),(-1,1,0,0),(0,0,-1,1),(-1,0,1,0),(0,-1,0,1),(1,-1,-1,1))
 groups=cells+('EXACT_Q_HALF_MINUS_ZERO','NOISY_Q_HALF_MINUS_ZERO','NOISY_MINUS_EXACT_AT_Q_ZERO','NOISY_MINUS_EXACT_AT_Q_HALF','NOISE_BY_RECURRENCE');blocks=collections.defaultdict(list)
 for b in range(24):
  reps=collections.defaultdict(list)
  for r in range(8):
   values=[]
   for cell in cells:
    out={};stay=panel[b,r,cell,'STAY'];switch=[panel[b,r,cell,'SWITCH'+str(i)] for i in (0,1)]
    for m in ('D40','U','U40'):
     if m=='D40':x=math.fsum(switch[i]['founder'][str(i)][40]-1/32 for i in (0,1))/2;y=math.fsum(stay['founder'][str(i)][40]-1/32 for i in (0,1))/2
     elif m=='U':x=math.fsum(math.fsum(s['accuracy'][1:])/40 for s in switch)/2;y=math.fsum(stay['accuracy'][1:])/40
     else:x=math.fsum(s['accuracy'][40] for s in switch)/2;y=stay['accuracy'][40]
     suffix='' if m=='D40' else '_POP'
     for kind,v in (('SWITCH',x),('STAY',y),('EFFECT',x-y)):out[kind+suffix+'|'+m]=v
    values.append(out)
   for group,cs in zip(groups,coefs):
    for m in values[0]:reps[group+'|'+m].append(math.fsum(cs[i]*values[i][m] for i in range(4)))
  for k,xs in reps.items():blocks[k].append(math.fsum(xs)/8)
 weights=[collections.Counter(row) for row in indices];est={}
 for k,xs in blocks.items():
  ds=sorted(math.fsum(xs[i]*n for i,n in w.items())/24 for w in weights);ci=[]
  for p in (.025,.975):a=(len(ds)-1)*p;i=math.floor(a);w=a-i;ci.append((1-w)*ds[i]+w*ds[math.ceil(a)])
  est[k]=dict(mean=math.fsum(xs)/24,ci95=ci)
 assert len(est)==81;return est

def main():
 verify_manifest('SOURCE_SHA256SUMS');verify_manifest('SCIENCE_SHA256SUMS');check_stage('INPUT');verify_references();verify_roster(read('SEEDS.json'),read('PRIOR_SEED_INVENTORY.json')['integers']);assert read('DESIGN_FREEZE.json')['freeze_unix']<read('INPUT_FREEZE.json')['freeze_unix']<read('TRANSFER_STARTED.json')['start_unix']
 st=states();ds=keyed('streams.jsonl.gz');fresh=keyed('fresh_probe_masks.jsonl.gz');surv=keyed('survival_streams.jsonl.gz');noise=keyed('noise_streams.jsonl.gz');targets=read('TARGET_TABLE.json');hist=read('PREPARATION_TARGETS.json');td=read('TARGET_LAW_DRAWS.json');assert len(noise)==192
 for b in range(24):
  for law in ('ZERO','HALF'):assert targets[law][b]['targets']==extend_targets(hist[b]['targets'],td[b]['innovations'],td[b]['copy_bits'],law)
  for r in range(8):assert st[b,r]['source_state']['last_two_preparation_targets']==hist[b]['targets'][-2:]
 panel={}
 for row in rows(P/'TIME_SERIES.jsonl.gz'):
  k=row['block'],row['replicate'],row['cell'],row['configuration'];assert k not in panel;panel[k]=row['series']
 assert len(panel)==2304;counts=collections.Counter()
 for row in rows(P/'raw/block00.jsonl.gz'):
  b,r,cell,cfg=row['block'],row['replicate'],row['cell'],row['configuration'];assert b==0;state=st[b,r]['source_state'];d=ds[b,r]['draws'];labels=d['labels'];slot=None if cfg=='STAY' else labels[int(cfg[-1])]
  initial=[(q[0],1 if i==slot else 2,q[2],q[3]) for i,q in enumerate(state['rebased_population'])];rec=row['record'];assert rec['interface']==row['interface'] and cell==row['interface']+'_Q_'+row['law'];assert row['slot']==slot and row['founder_ids']==labels[:2] and row['source_row_index']==st[b,r]['source_row_index'] and row['source_founder_rebase_map']==state['founder_rebase_map']
  counts.update(audit_record(rec,targets[row['law']][b]['targets'],d,initial,fresh[b,r]['fresh'],surv[b,r]['survival'],noise[b,r]['noise'],state['last_preparation_target']))
  s=panel[b,r,cell,cfg];assert s['accuracy']==rec['true_accuracies'] and s['expression']==rec['frequencies']
  for i,fid in enumerate(labels[:2]):assert s['founder'][str(i)]==[sum(q[2]==fid for q in pop)/32. for pop in rec['populations']]
 assert counts['paths']==96 and counts['queries']==494592
 got=recompute(panel,read('BOOTSTRAP_INDICES.json'));expected=read('ESTIMATES.json');assert set(got)==set(expected);worst=0
 for k,v in got.items():
  err=max([abs(v['mean']-expected[k]['mean'])]+[abs(a-b) for a,b in zip(v['ci95'],expected[k]['ci95'])]);assert err<2e-13,(k,err);worst=max(worst,err)
 lo,hi=expected['NOISE_BY_RECURRENCE|EFFECT|D40']['ci95'];a=read('ASSESSMENT.json')['decisions'];assert a['direction']==('supports_negative' if hi<0 else 'contradicts_negative' if lo>0 else 'unresolved')
 for threshold,key in ((-1/32,'minus_one_descendant'),(1/32,'plus_one_descendant')):assert a[key]==('below' if hi<threshold else 'above' if lo>threshold else 'overlaps')
 assert read('BUDGET.json')['total_objective_calls']==11870208 and read('BUDGET.json')['new_paths']==2304 and read('BUDGET.json')['new_preparations']==0
 save('INDEPENDENT_AUDIT.json',dict(status='PASS',raw_audit_block=0,raw_checks=counts,checked_estimates=81,maximum_absolute_discrepancy=worst,tolerance=2e-13,recorded_query_reconstructions=494592,new_scientific_calls=0,new_paths=0,new_random_draws=0));print(json.dumps(read('INDEPENDENT_AUDIT.json')))
if __name__=='__main__':main()
