"""Complete outcomes without survival conditioning; founder and expression fates separated."""
import collections,csv
from common import *
from analysis import *
def sign(x):return 'positive' if x>0 else 'negative' if x<0 else 'zero'
def fate(x):return 'extinct' if x==0 else 'fixed' if x==1 else 'polymorphic'
def main():
 assert not (P/'VALIDATION_CHECK.json').exists();verify_manifest('SCIENCE_SHA256SUMS');start=time.time();paths={};n=0
 for row in rows(P/'TIME_SERIES.jsonl.gz'):
  k=row['block'],row['replicate'];cfg=row['configuration'];assert cfg not in paths.setdefault(k,{})
  paths[k][cfg]=row['series'];n+=1
 assert n==960 and len(paths)==192
 blockcols=collections.defaultdict(lambda:collections.defaultdict(list));signs=collections.defaultdict(collections.Counter);osigns=collections.defaultdict(collections.Counter);counts=collections.defaultdict(collections.Counter);neg=ties=disagreements=0
 with (P/'PATH_METRICS.jsonl').open('w') as po,(P/'FOUNDER_FATES.jsonl').open('w') as fo,(P/'EXPRESSION_FATES.jsonl').open('w') as eo,(P/'NEGATIVE_OUTCOMES.jsonl').open('w') as no,(P/'EXACT_TIES.jsonl').open('w') as zo,(P/'TRANSMISSION_ACCURACY_DISAGREEMENTS.jsonl').open('w') as do:
  saved={(q['block'],q['replicate']):q['values'] for q in rows(P/'PAIRED_METRICS.jsonl.gz')}
  for (b,r),ps in sorted(paths.items()):
   vals=summarize(ps);assert vals==saved[b,r]
   for cfg,s in ps.items():
    for placement in (0,1) if cfg=='STAY' else (int(cfg[-1]),):
     xs=s['founder'][str(placement)];metrics=endpoints(s['accuracy'],xs);po.write(json.dumps(dict(block=b,replicate=r,configuration=cfg,placement=placement,values=metrics))+'\n')
     for a,z in zip(xs,xs[1:]):assert a!=0 or z==0
     for t in (1,40):
      value=xs[t];ep=fate(value);key=cfg+'|placement'+str(placement)+'|t'+str(t);counts[key][ep]+=1;fo.write(json.dumps(dict(block=b,replicate=r,configuration=cfg,placement=placement,update=t,frequency=value,fate=ep,first_extinction=next((i for i,v in enumerate(xs) if v==0),None),first_fixation=next((i for i,v in enumerate(xs) if v==1),None)))+'\n')
    for t in (1,40):
     for phase in ('selected','carried'):
      for role in ('H','F'):
       value=s['expression_'+phase][role][t];eo.write(json.dumps(dict(block=b,replicate=r,configuration=cfg,update=t,phase=phase,role=role,frequency=value,fate=fate(value),forced_identity=cfg.startswith('PULSE') and (phase=='carried' or t>1),interpretation='Expression status only; does not determine focal founder fate'))+'\n')
    if cfg.startswith('PULSE'):assert s['expression_carried']['F'][1:]==[0]*40 and s['expression_selected']['F'][2:]==[0]*39
   for k,x in vals.items():
    blockcols[b][k].append(x);signs[k][sign(x)]+=1
    if x<0:no.write(json.dumps(dict(block=b,replicate=r,key=k,value=x))+'\n');neg+=1
    if x==0:zo.write(json.dumps(dict(block=b,replicate=r,key=k,structural_identity=k in STRUCTURAL_ZEROS))+'\n');ties+=1
   for i in (0,1):
    own={a:endpoints(ps['STAY' if a=='STAY' else a+str(i)]['accuracy'],ps['STAY' if a=='STAY' else a+str(i)]['founder'][str(i)]) for a in ARMS}
    for group,(a,z) in CONTRASTS.items():
     effect={m:own[a][m]-own[z][m] for m in ENDPOINTS}
     for m,x in effect.items():osigns[str(i)+'|'+group+'|'+m][sign(x)]+=1
     if sign(effect['D40'])!=sign(effect['U40']):do.write(json.dumps(dict(block=b,replicate=r,placement=i,contrast=group,founder_D40=effect['D40'],population_U40=effect['U40']))+'\n');disagreements+=1
 blocks=[]
 for b in range(24):
  assert set(blockcols[b])==set(KEYS) and all(len(xs)==8 for xs in blockcols[b].values());blocks.append(dict(block=b,values={k:sum(xs)/8 for k,xs in blockcols[b].items()}))
 save('BLOCK_SUMMARIES.json',blocks);idx=read('BOOTSTRAP_INDICES.json');assert len(idx)==2000 and all(len(row)==24 and all(type(i)==int and 0<=i<24 for i in row) for row in idx);est={}
 for k in KEYS:
  xs=[q['values'][k] for q in blocks];mean,ci=interval(xs,idx);classification='structural_zero' if k in STRUCTURAL_ZEROS else 'positive' if ci[0]>0 else 'negative' if ci[1]<0 else 'observed_exact_zero' if all(x==0 for x in xs) else 'unresolved';unit=32 if k.endswith(('D1','D40')) else 1024 if k.endswith('U40') else None
  est[k]=dict(mean=mean,ci95=ci,classification=classification,mean_percentage_points=mean*100,ci95_percentage_points=[x*100 for x in ci],count_unit='expected_descendants' if unit==32 else 'expected_matching_bits' if unit==1024 else None,mean_count_units=mean*unit if unit else None,ci95_count_units=[x*unit for x in ci] if unit else None,paired_signs=signs[k],block_signs=dict(collections.Counter(sign(x) for x in xs)))
 save('ESTIMATES.json',est);save('FOUNDER_FATE_COUNTS.json',counts);save('ORIENTATION_SIGNS.json',osigns)
 with (P/'ESTIMATES.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['key','mean','low','high','mean_pp','low_pp','high_pp','classification','count_unit','mean_count','low_count','high_count'])
  for k,q in est.items():w.writerow([k,q['mean']]+q['ci95']+[q['mean_percentage_points']]+q['ci95_percentage_points']+[q['classification'],q['count_unit'],q['mean_count_units']]+(q['ci95_count_units'] or [None,None]))
 decline=0
 with (P/'DECLINES.jsonl').open('w') as out:
  for b in range(24):
   for row in rows(P/('raw/block%02d.jsonl.gz'%b)):
    rec=row['record']
    for g,s in enumerate(rec['steps']):
     decreased=rec['raw_losses'][g+1]>rec['raw_losses'][g]
     if decreased or s['S_raw']<0:out.write(json.dumps(dict(block=b,replicate=row['replicate'],configuration=row['configuration'],update=g+1,accuracy_declined=decreased,S_raw=s['S_raw'],W_raw=s['W_raw']))+'\n');decline+=1
 save('ASSESSMENT.json',dict(primary=PRIMARY,estimate=est[PRIMARY],decisions=decisions(est[PRIMARY]['ci95']),continuous_comparator=est['CONT_MINUS_STAY|U40'],pulse_minus_continuous=est['PULSE_MINUS_CONT|U40'],interval_scope='approximate pointwise',reused_preparations=True,independent_training_replication=False,cohort_pooling=False))
 save('VALIDATION_CHECK.json',dict(status='PASS',paths=960,paired_replicates=192,blocks=24,estimates=36,structural_zeros=STRUCTURAL_ZEROS,negative_records=neg,exact_ties=ties,transmission_accuracy_disagreements=disagreements,decline_records=decline,new_objective_calls=0,new_draws=0,elapsed_seconds=time.time()-start,raw_audit='Performed separately by audit_independent.py'))
 print(json.dumps(read('ASSESSMENT.json')))
if __name__=='__main__':main()
