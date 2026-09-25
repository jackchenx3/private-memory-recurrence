"""All81 estimates and complete adverse/fate bookkeeping from saved true outcomes."""
import collections,csv
from common import *
from analysis import *
def sign(x):return 'positive' if x>0 else 'negative' if x<0 else 'zero'
def fate(x):return 'extinct' if x==0 else 'fixed' if x==1 else 'polymorphic'
def main():
 assert not (P/'VALIDATION_CHECK.json').exists();verify_manifest('SCIENCE_SHA256SUMS');start=time.time();panel={}
 for row in rows(P/'TIME_SERIES.jsonl.gz'):
  key=row['block'],row['replicate'],row['cell'];cfg=row['configuration'];assert cfg not in panel.setdefault(key,{});panel[key][cfg]=row['series']
 assert len(panel)==768 and all(set(q)==set(CONFIGS) for q in panel.values())
 saved={(q['block'],q['replicate']):q['values'] for q in rows(P/'PAIRED_METRICS.jsonl.gz')};cols=collections.defaultdict(lambda:collections.defaultdict(list));signs=collections.defaultdict(collections.Counter);counts=collections.defaultdict(collections.Counter);neg=ties=disagreements=0
 with (P/'PATH_METRICS.jsonl').open('w') as po,(P/'FOUNDER_FATES.jsonl').open('w') as fo,(P/'EXPRESSION_FATES.jsonl').open('w') as eo,(P/'NEGATIVE_OUTCOMES.jsonl').open('w') as no,(P/'EXACT_TIES.jsonl').open('w') as zo,(P/'ORIENTATION_METRICS.jsonl').open('w') as oo,(P/'TRANSMISSION_ACCURACY_DISAGREEMENTS.jsonl').open('w') as do:
  for b in range(24):
   for r in range(8):
    cells={cell:base(panel[b,r,cell]) for cell in CELLS};vals=combine(cells);assert vals==saved[b,r]
    for cell in CELLS:
     for cfg,s in panel[b,r,cell].items():
      for i in (0,1) if cfg=='STAY' else (int(cfg[-1]),):
       f=s['founder'][str(i)];a=s['accuracy'];metrics=dict(D40=f[-1]-1/32,U=sum(a[1:])/40,U40=a[-1]);po.write(json.dumps(dict(block=b,replicate=r,cell=cell,configuration=cfg,placement=i,values=metrics))+'\n')
       assert f[0]==1/32
       for x,y in zip(f,f[1:]):assert x!=0 or y==0
       if cfg!='STAY':assert f==s['expression']['H']
       ep=fate(f[-1]);key=cell+'|'+cfg+'|placement'+str(i);counts[key][ep]+=1;fo.write(json.dumps(dict(block=b,replicate=r,cell=cell,configuration=cfg,placement=i,initial=f[0],terminal=f[-1],fate=ep,first_extinction=next((j for j,x in enumerate(f) if x==0),None),first_fixation=next((j for j,x in enumerate(f) if x==1),None)))+'\n')
      for role in ('H','F'):eo.write(json.dumps(dict(block=b,replicate=r,cell=cell,configuration=cfg,role=role,terminal=s['expression'][role][-1],fate=fate(s['expression'][role][-1])))+'\n')
    oriented=[]
    for i in (0,1):
     v=combine({cell:base(panel[b,r,cell],i) for cell in CELLS});oriented.append(v);oo.write(json.dumps(dict(block=b,replicate=r,placement=i,values=v))+'\n')
    for k,x in vals.items():
     assert abs(x-(oriented[0][k]+oriented[1][k])/2)<2e-15;cols[b][k].append(x);signs[k][sign(x)]+=1
     if x<0:no.write(json.dumps(dict(block=b,replicate=r,key=k,value=x))+'\n');neg+=1
     if x==0:zo.write(json.dumps(dict(block=b,replicate=r,key=k,structural_identity=False))+'\n');ties+=1
    for g in GROUPS:
     for m in ('U','U40'):
      founder=vals[g+'|EFFECT|D40'];accuracy=vals[g+'|EFFECT_POP|'+m]
      if sign(founder)!=sign(accuracy):do.write(json.dumps(dict(block=b,replicate=r,group=g,metric=m,founder_effect=founder,true_accuracy_effect=accuracy))+'\n');disagreements+=1
 blocks=[]
 for b in range(24):
  assert set(cols[b])==set(KEYS) and all(len(v)==8 for v in cols[b].values());blocks.append(dict(block=b,values={k:sum(v)/8 for k,v in cols[b].items()}))
 save('BLOCK_SUMMARIES.json',blocks);idx=read('BOOTSTRAP_INDICES.json');assert len(idx)==2000 and all(len(row)==24 and all(type(i)==int and 0<=i<24 for i in row) for row in idx);est={}
 for k in KEYS:
  xs=[q['values'][k] for q in blocks];mean,ci=interval(xs,idx);cl='positive' if ci[0]>0 else 'negative' if ci[1]<0 else 'observed_exact_zero' if all(x==0 for x in xs) else 'unresolved';scale=32 if k.endswith('D40') else 1024
  est[k]=dict(mean=mean,ci95=ci,classification=cl,mean_percentage_points=mean*100,ci95_percentage_points=[v*100 for v in ci],count_unit='expected_descendants' if scale==32 else 'expected_matching_bits',mean_count_units=mean*scale,ci95_count_units=[v*scale for v in ci],paired_signs=signs[k],block_signs=dict(collections.Counter(sign(v) for v in xs)))
 save('ESTIMATES.json',est);save('FOUNDER_FATE_COUNTS.json',counts)
 with (P/'ESTIMATES.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['key','mean','low','high','mean_pp','low_pp','high_pp','classification','count_unit','mean_count','low_count','high_count'])
  for k,q in est.items():w.writerow([k,q['mean']]+q['ci95']+[q['mean_percentage_points']]+q['ci95_percentage_points']+[q['classification'],q['count_unit'],q['mean_count_units']]+q['ci95_count_units'])
 decline=0;observation=collections.Counter()
 with (P/'DECLINES.jsonl').open('w') as out:
  for b in range(24):
   for row in rows(P/('raw/block%02d.jsonl.gz'%b)):
    rec=row['record'];interface=row['interface']
    for q in rec['initial_queries']:
     if q['observed_score']<0:observation[interface+'_below_zero']+=1
     if q['observed_score']>32:observation[interface+'_above_32']+=1
    for g,s in enumerate(rec['steps']):
     for x in s['candidate_observed_scores']:
      if x<0:observation[interface+'_below_zero']+=1
      if x>32:observation[interface+'_above_32']+=1
     decreased=rec['true_losses'][g+1]>rec['true_losses'][g]
     if decreased or s['S_true']<0:out.write(json.dumps(dict(block=b,replicate=row['replicate'],cell=row['cell'],configuration=row['configuration'],update=g+1,accuracy_declined=decreased,S_true=s['S_true'],W_true=s['W_true']))+'\n');decline+=1
 save('OBSERVATION_RANGE_COUNTS.json',observation)
 recurrence={interface:dict(estimate=est[interface+'_Q_HALF_MINUS_ZERO|EFFECT|D40'],plus_one_descendant=positive_scale(est[interface+'_Q_HALF_MINUS_ZERO|EFFECT|D40']['ci95'])) for interface in ('EXACT','NOISY')}
 save('ASSESSMENT.json',dict(primary=PRIMARY,estimate=est[PRIMARY],decisions=decisions(est[PRIMARY]['ci95']),recurrence=recurrence,interval_scope='exploratory approximate pointwise',reused_exact_preparations=True,independent_training_replication=False,cohort_pooling=False))
 save('VALIDATION_CHECK.json',dict(status='PASS',paths=2304,paired_replicates=192,blocks=24,estimates=81,structural_zeros=[],negative_records=neg,exact_ties=ties,transmission_accuracy_disagreements=disagreements,decline_records=decline,new_objective_calls=0,new_draws=0,elapsed_seconds=time.time()-start,raw_audit='Separate prospectively fixed96-path audit'))
 print(json.dumps(read('ASSESSMENT.json')))
if __name__=='__main__':main()
