"""Compact outcome-driven report; two figures, no additional inferential endpoint grid."""
import collections
from common import *
from analysis import *
def main():
 assert read('VALIDATION_CHECK.json')['status']=='PASS' and read('INDEPENDENT_AUDIT.json')['status']=='PASS'
 est=read('ESTIMATES.json');a=read('ASSESSMENT.json');s=read('SCHEDULER_RECEIPT.json');assert s['status']=='COMPLETE'
 def fmt(k,scale=100):q=est[k];return '%.5f [%.5f, %.5f]'%tuple(scale*v for v in [q['mean']]+q['ci95'])
 verdict={'supports_positive':'supports the fixed positive directional prediction','contradicts_positive':'contradicts the fixed positive directional prediction','unresolved':'leaves the fixed positive directional prediction unresolved'}[a['decisions']['direction']]
 resolution={'above_one_matching_bit':'The primary interval lies wholly above the one-expected-matching-bit benchmark.','below_one_matching_bit':'The primary interval lies wholly below the one-expected-matching-bit benchmark.','overlaps_one_matching_bit':'The primary interval overlaps the one-expected-matching-bit benchmark, leaving that resolution criterion unresolved.'}[a['decisions']['benchmark']]
 text=['# ORG-PULSE-059: one update of fresh exploration','',
 'The primary result **'+verdict+'**. PULSE minus STAY terminal population accuracy is **'+fmt(PRIMARY)+' percentage points** (approximate pointwise95% interval), or '+fmt(PRIMARY,1)+' in fraction units. Across the32×32 population-target comparisons, this is '+fmt(PRIMARY,1024)+' expected additional matching bits.','',
 resolution+' The separate fixed benchmark is1/1024 accuracy =0.09765625 percentage points =one expected matching bit across the entire population. This is a model resolution scale, not a biological or practical threshold. It is separate from the sign criterion.','',
 'The continuous comparator CONT minus STAY at update40 is '+fmt('CONT_MINUS_STAY|U40')+' pp; PULSE minus CONT is '+fmt('PULSE_MINUS_CONT|U40')+' pp. These contrasts and all contrary or unresolved endpoints are retained. The primary is not replaced by a favorable secondary endpoint.','',
 'The192 prepared populations are reused, authenticated057 HALF/H endpoints, with no filtering by performance or fate. All transfer targets, proposals, placements, survival tapes and2,000 bootstrap rows are new. All five paths within a replicate share indexed inputs; target recurrence is HALF and continues from that preparation’s final two targets. This is a new intervention on reused preparations, not independent training replication. No057/058 outcomes or bootstrap rows are reused or pooled.','',
 'PULSE changes one selected founder’s H label to F before update1. Immediately after selection in that update, remaining F labels become H, preserving genotype, cache, founder ID and individual order. Updates2–40 express H throughout. CONT leaves inherited F expression active. STAY remains all-H. The accepted candidate, cache, donor and probabilistic survivor operators are unchanged; weights are2^(-Hamming loss), with zero cost. Each path has32 initial plus40×128 candidate queries. Equal objective-call budgets do not establish equal intervention overhead or real resource cost.','',
 'Pulse and continuous trajectories have exactly identical initial states, queried candidates, selection and post-selection states through update1. Their U1 and D1 contrasts are exact coupling identities. Forced disappearance of F expression is a design identity; it is not observed extinction of the founder. Founders remain tracked by their initial IDs, regardless of current expression. Neither inference nor reporting conditions on survival, extinction or establishment.','',
 '| Arm / contrast | U1 | U_LATE (updates2–40) | U40 | U_ALL (updates1–40) |','|---|---|---|---|---|']
 for g in GROUPS:text.append('| '+g+' | '+' | '.join(fmt(g+'|'+m) for m in ('U1','U_LATE','U40','U_ALL'))+' |')
 text+=['','Absolute arm accuracies are percentages; paired differences are percentage points. All intervals above are approximate pointwise95%. STAY population accuracy is counted once; the PULSE/CONT summaries average the two preselected placements.','',
 '| Arm / contrast | Founder D1 (pp) | Founder D40 (pp) | D40 expected descendants |','|---|---|---|---|']
 for g in GROUPS:text.append('| '+g+' | '+fmt(g+'|D1')+' | '+fmt(g+'|D40')+' | '+fmt(g+'|D40',32)+' |')
 check=read('VALIDATION_CHECK.json');primary=est[PRIMARY]
 text+=['','D1 and D40 are focal founder frequency minus1/32. For absolute arms, add1/32 to obtain terminal frequency; matched contrasts compare the same two founders. Founder transmission does not substitute for population accuracy. FOUNDER_FATES.jsonl and FATES_SUMMARY.md retain both placements separately at updates1 and40, with extinction, fixation and polymorphism. EXPRESSION_FATES.jsonl distinguishes pre-reversion selected expression from carried expression.','',
 'Primary replicate signs: '+json.dumps(primary['paired_signs'],sort_keys=True)+'; block signs: '+json.dumps(primary['block_signs'],sort_keys=True)+'. Across the fixed catalog, classifications are '+json.dumps(dict(collections.Counter(q['classification'] for q in est.values())),sort_keys=True)+'. There are '+str(check['negative_records'])+' negative metric records, '+str(check['exact_ties'])+' exact ties and '+str(check['transmission_accuracy_disagreements'])+' founder/accuracy sign disagreements. All are retained in machine-readable records. DECLINES.jsonl includes '+str(check['decline_records'])+' updates with declining selected-state accuracy or negative within-target selection improvement.','',
 'Inference averages placements, then eight replicates within each of24 blocks. New whole-block resampling uses2,000 shared rows and linear2.5/97.5 percentiles. Intervals are approximate and pointwise; there is no simultaneous family-wide guarantee. Only36 mean/interval pairs are estimated. The time curves are descriptive and add no interval grid.','',
 'Job '+s['job_id']+' completed with exit '+s.get('exit_code','unknown')+'. One production allocation:1CPU,4GiB,15minutes;960 new paths and4,945,920 objective calls, with no new preparations or extra score measurements. ACCOUNTING.psv and MEMORY_TELEMETRY.jsonl preserve measured resources. All36 estimates were independently recomputed. The prospective raw audit reconstructed206,080 recorded scores and the donor/selection/cache/founder transitions in40 block0 paths, including every scheduled reversion. No past study was replayed.','',
 'Interpretation is limited to this complete state intervention. Any later accuracy effect is caused by the one-update pulse and the state changes it induces under these matched inputs; the experiment does not identify which component—genotypes, caches, lineage composition or ordering—carries the effect. An unresolved contrast is not proof of no effect. It does not explain all earlier continuous-policy effects, estimate equilibrium behavior or establish a generally useful exploration schedule.','',
 'This finite experiment is complete. A manuscript update would require a separate judgment that these results add a substantive finding. No pulse-duration search, second cohort, parameter extension, publication or further variant follows automatically.','',
 '![Accuracy contrasts](figures/01_accuracy_contrasts.png)','', '![Descriptive population and lineage curves](figures/02_time_curves.png)']
 (P/'REPORT.md').write_text('\n'.join(text)+'\n')
 lines=['# All36 estimates','','Approximate pointwise95% intervals; fraction units.','','| Key | Mean [CI] | pp [CI] | Count units [CI] | Classification |','|---|---|---|---|---|']
 for k,q in est.items():
  scale=32 if k.endswith(('D1','D40')) else 1024 if k.endswith('U40') else None
  lines.append('| '+k.replace('|',' / ')+' | '+fmt(k,1)+' | '+fmt(k)+' | '+(fmt(k,scale) if scale else 'not applicable')+' | '+q['classification']+' |')
 (P/'COMPLETE_ESTIMATES.md').write_text('\n'.join(lines)+'\n')
 lines=['# Founder fates','','Each row counts192 prepared populations; placements remain separate, not independent trials. Expression reversion is not founder extinction.','','| Configuration / placement / update | Extinct | Polymorphic | Fixed |','|---|---|---|---|']
 for k,q in sorted(read('FOUNDER_FATE_COUNTS.json').items()):lines.append('| '+k.replace('|',' / ')+' | '+' | '.join(str(q.get(v,0)) for v in ('extinct','polymorphic','fixed'))+' |')
 (P/'FATES_SUMMARY.md').write_text('\n'.join(lines)+'\n');figures(est)
 print(json.dumps(dict(primary=PRIMARY,decisions=a['decisions'],main_figures=2)))

def figures(est):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 folder=P/'figures';folder.mkdir(exist_ok=True)
 fig,axes=plt.subplots(2,2,figsize=(12,7),constrained_layout=True)
 for ax,m in zip(axes.flat,('U1','U_LATE','U40','U_ALL')):
  for i,g in enumerate(CONTRASTS):
   q=est[g+'|'+m];ax.plot([x*100 for x in q['ci95']],[i,i],color='tab:blue');ax.plot(q['mean']*100,i,'o',color='tab:blue')
  ax.set_yticks(range(3));ax.set_yticklabels(list(CONTRASTS),fontsize=8);ax.axvline(0,color='gray',lw=1);ax.invert_yaxis();ax.set(title=m+(' (coupling identity for pulse−continuous)' if m=='U1' else ''),xlabel='Accuracy percentage points; pointwise95%')
  if m=='U40':ax.plot([DELTA*100]*2,[-.2,.2],color='black',lw=2,label='Primary benchmark:1 matching bit');ax.legend(fontsize=8)
 fig.savefig(folder/'01_accuracy_contrasts.png',dpi=150);fig.savefig(folder/'01_accuracy_contrasts.pdf');plt.close(fig)
 ps={}
 for row in rows(P/'TIME_SERIES.jsonl.gz'):ps[row['block'],row['replicate'],row['configuration']]=row['series']
 fig,axes=plt.subplots(1,3,figsize=(15,5),constrained_layout=True)
 for arm,color in [('STAY','gray'),('PULSE','tab:orange'),('CONT','tab:blue')]:
  sums=[[0.]*41 for _ in range(3)]
  for b in range(24):
   for r in range(8):
    for i in (0,1):
     s=ps[b,r,'STAY' if arm=='STAY' else arm+str(i)]
     for j,xs in enumerate((s['accuracy'],s['founder'][str(i)],s['expression_carried']['F'])):
      for t,x in enumerate(xs):sums[j][t]+=x/384
  for ax,xs in zip(axes,sums):ax.plot(range(41),[100*x for x in xs],label=arm,color=color)
 for ax,title,ylabel in zip(axes,('Population accuracy','Focal founder lineage','Carried F expression'),('Matching bits (%)','Founder frequency (%)','F expression (%)')):
  ax.axvline(1,color='black',lw=.7,ls='--');ax.set(title=title,xlabel='Transfer update',ylabel=ylabel);ax.legend(fontsize=8)
 fig.savefig(folder/'02_time_curves.png',dpi=150);fig.savefig(folder/'02_time_curves.pdf');plt.close(fig)
if __name__=='__main__':main()
