from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parents[1];P=R/'results/059'
read=lambda n:json.loads((P/n).read_text())
e=read('ESTIMATES.json');b=read('BLOCK_SUMMARIES.json');idx=np.asarray(read('BOOTSTRAP_INDICES.json'),dtype=int)
assert len(e)==36 and len(b)==24 and idx.shape==(2000,24)
worst=0.
for k,q in e.items():
 x=np.array([v['values'][k] for v in b]);ci=np.quantile(x[idx].mean(axis=1),[.025,.975],method='linear')
 error=max(abs(x.mean()-q['mean']),max(abs(ci-q['ci95'])));assert error<2e-13;worst=max(worst,float(error))
 classification='structural_zero' if k in ['PULSE_MINUS_CONT|U1','PULSE_MINUS_CONT|D1'] else 'positive' if ci[0]>0 else 'negative' if ci[1]<0 else 'observed_exact_zero' if np.all(x==0) else 'unresolved'
 assert q['classification']==classification
quoted=json.loads((R/'results/QUOTED_059_STATISTICS.json').read_text())
for q in quoted:assert q['value']==e[q['key']]
print(json.dumps(dict(status='PASS',estimates=36,quoted_statistics=len(quoted),maximum_absolute_discrepancy=worst,new_scientific_paths=0,new_random_draws=0)))
