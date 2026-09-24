"""Check all 114 saved estimates; no RNG or population simulation."""
from pathlib import Path
import json, numpy as np
R=Path(__file__).resolve().parents[1];P=R/'results/058'
read=lambda n:json.loads((P/n).read_text())
est=read('ESTIMATES.json');blocks=read('BLOCK_SUMMARIES.json');idx=np.array(read('BOOTSTRAP_INDICES.json'),dtype=int)
assert len(est)==114 and len(blocks)==24 and idx.shape==(2000,24)
worst=0.
for k,q in est.items():
 x=np.array([b['values'][k] for b in blocks]);ci=np.quantile(x[idx].mean(axis=1),[.025,.975],method='linear')
 e=max(abs(x.mean()-q['mean']),max(abs(ci-q['ci95'])));assert e<2e-13,(k,e);worst=max(worst,float(e))
 kind='positive' if ci[0]>0 else 'negative' if ci[1]<0 else 'observed_exact_zero' if np.all(x==0) else 'unresolved'
 assert kind==q['classification']
quoted=json.loads((R/'results/QUOTED_058_STATISTICS.json').read_text())
for q in quoted:assert q['value']==est[q['key']]
print(json.dumps(dict(status='PASS',estimates=114,quoted_statistics=len(quoted),maximum_absolute_discrepancy=worst,new_scientific_paths=0,new_random_draws=0)))
