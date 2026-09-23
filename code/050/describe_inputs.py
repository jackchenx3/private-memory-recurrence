"""Saved target inputs only; no RNG or fitness evaluations."""
import json,pathlib,collections
P=pathlib.Path(__file__).resolve().parent
out={}
for g in ('ZERO','HALF','FULL'):
 rows=json.loads((P/(g+'_TARGETS.json')).read_text())['blocks'];bs=[];tot=collections.Counter();hist={1:collections.Counter(),2:collections.Counter()}
 for row in rows:
  ts=row['targets'];q=dict(block=row['block'],initial_measurement_change=row['actual_changes'][0],boundary_change_from_preparation=row['boundary_change_from_preparation'],targets=40,distinct_targets=len(set(ts)))
  for lag in (1,2):
   ds=[bin(ts[j]^ts[j-lag]).count('1') for j in range(lag,40)];q['lag'+str(lag)]=dict(denominator=len(ds),distances=ds,exact_returns=ds.count(0),mean_distance=sum(ds)/len(ds));hist[lag].update(ds);tot['lag%d_pairs'%lag]+=len(ds);tot['lag%d_exact_returns'%lag]+=ds.count(0);tot['lag%d_distance_sum'%lag]+=sum(ds)
  q['actual_changes_after_initial']=sum(row['actual_changes'][1:]);tot['actual_changes_after_initial']+=q['actual_changes_after_initial'];tot['boundary_changes']+=int(q['boundary_change_from_preparation']);bs.append(q)
 out[g]=dict(blocks=bs,totals=tot,hamming_histograms=hist,full_denominators=dict(targets=960,lag1_pairs=936,lag2_pairs=912,boundaries=24))
raw=json.loads((P/'TARGET_LAW_DRAWS.json').read_text())['blocks'];copies=sum(sum(q['copy_bits']) for q in raw);assert 0<=copies<=912
(P/'ENVIRONMENT_SUMMARY.json').write_text(json.dumps(dict(laws=out,realized_copy_bits=dict(ones=copies,zeros=912-copies,total=912),interpretation='Descriptive sampled inputs, not required empirical identities; adjacent-pair law equality is unconditional, not independence from prepared states. Chance equalities retained.'),indent=2)+'\n')
