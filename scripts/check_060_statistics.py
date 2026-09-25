"""Recompute81saved estimates and verify new manuscript/figure bindings; no simulation."""
from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parents[1];P=R/'results/060';read=lambda n:json.loads((P/n).read_text());e=read('ESTIMATES.json');b=read('BLOCK_SUMMARIES.json');idx=np.asarray(read('BOOTSTRAP_INDICES.json'),dtype=int);assert len(e)==81 and len(b)==24 and idx.shape==(2000,24);worst=0
for k,q in e.items():
 x=np.asarray([r['values'][k] for r in b]);ci=np.quantile(x[idx].mean(axis=1),[.025,.975],method='linear');err=max(abs(x.mean()-q['mean']),max(abs(ci-q['ci95'])));assert err<2e-14;worst=max(worst,float(err));assert q['classification']==('observed_exact_zero' if np.all(x==0) else 'positive' if ci[0]>0 else 'negative' if ci[1]<0 else 'unresolved')
quoted=json.loads((R/'results/QUOTED_060_STATISTICS.json').read_text())
for r in quoted:assert r['value']==e[r['key']]
fig=json.loads((R/'figures/FIGURE_060_DATA.json').read_text());assert len(fig)==7
for r in fig:assert r['mean_pp']==100*e[r['key']]['mean'] and r['ci95_pp']==[100*x for x in e[r['key']]['ci95']]
print(json.dumps(dict(status='PASS',estimates=81,quoted_statistics=len(quoted),figure_estimates=7,figure_numeric_bindings=21,maximum_absolute_discrepancy=worst,new_scientific_paths=0,new_random_draws=0)))
