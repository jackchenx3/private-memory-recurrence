"""Compact outcome-driven report and two figures; saved estimates only."""
import collections,hashlib
from common import *
from analysis import *
def main():
 assert read('VALIDATION_CHECK.json')['status']=='PASS';v=read('ESTIMATES.json');a=read('ASSESSMENT.json');s=read('SCHEDULER_RECEIPT.json');assert s['status']=='COMPLETE'
 def fmt(k):q=v[k];return '%.3f [%.3f, %.3f]'%tuple(100*x for x in [q['mean']]+q['ci95'])
 primary=v[PRIMARY];verdict='supports the predicted positive contribution' if a['supported'] else 'contradicts the positive directional prediction' if a['contradicted'] else 'leaves the predicted contribution unresolved'
 text=['# ORG-CROSSENV-056 — environmental history crossed with future recurrence','',
 'The primary contrast **'+verdict+'**. Holding HALF-prepared states fixed, changing future recurrence from ZERO to HALF changes the matched F-to-H founder effect by **'+fmt(PRIMARY)+' percentage points** (approximate pointwise 95%% interval). The mean is %.6f in frequency units, or %.3f expected terminal descendants per introduction.'%(primary['mean'],primary['mean']*32),'',
 'This separates future-law effects at fixed prepared states from preparation-history effects at fixed future law. Targets continue recursively from each preparation’s own final two targets. All genotypes, caches, founder placements, proposal tapes and survivor random words are held to their saved 055 definitions.','',
 'Job '+s['job_id']+' completed with exit '+s.get('exit_code','unknown')+'. One production allocation; 2,304 new off-diagonal paths and 2,304 exactly reused diagonal records. No new preparations, seeds or draws. New scientific objective calls: 11,870,208. Tests and deterministic output validation passed. See ACCOUNTING.psv for measured resources and VALIDATION_CHECK.json for recorded checks.','',
 'H uses the stored ancestry cache; F uses fresh variation while still maintaining a cache. Positive founder effects need not imply founder increase or better population adaptation. The two placements are paired, with eight continuations averaged within each of 24 independent blocks before using the unchanged 2,000 bootstrap rows. All 162 intervals are approximate and pointwise, not simultaneous. No algebraic structural zeros occur in this catalog.','',
 '| Preparation / future | H introduction change | F control change | F→H effect | F introduction change | H control change | H→F effect |','|---|---|---|---|---|---|---|']
 for cell in CELLS:text.append('| '+cell+' | '+' | '.join(fmt(cell+'|'+bg+'_BG_'+series+'|D40') for bg in ('F','H') for series in ('SWITCH','STAY','EFFECT'))+' |')
 text+=['','Founder entries are percentage-point changes or differences, with pointwise intervals. Every absolute founder starts at 3.125%; add that initial value to an absolute D40 to obtain terminal frequency. Effects compare the same founder under switched and unchanged policy.','',
 '| Paired contrast | F→H effect | H→F effect |','|---|---|---|']
 for g in GROUPS[4:]:text.append('| '+g+' | '+fmt(g+'|F_BG_EFFECT|D40')+' | '+fmt(g+'|H_BG_EFFECT|D40')+' |')
 text+=['','The interaction has no prespecified directional prediction. An unresolved future effect does not establish a preparation-only explanation. One expected descendant (1/32 frequency) is a descriptive scale, not a significance or publication threshold.','',
 '| Cell/background | Switch mean accuracy | Stay mean accuracy | Mean effect | Switch terminal accuracy | Stay terminal accuracy | Terminal effect |','|---|---|---|---|---|---|---|']
 for cell in CELLS:
  for bg in ('F','H'):text.append('| '+cell+' / '+bg+' | '+' | '.join(fmt(cell+'|'+bg+'_BG_'+series+'_POP|'+m) for m in ('U','U40') for series in ('SWITCH','STAY','EFFECT'))+' |')
 text+=['','Absolute accuracy entries are percentages; effect entries are percentage points. All base cells, future contrasts, preparation contrasts and interactions—including contrary and unresolved findings—are in ESTIMATES.csv/ESTIMATES.json and COMPLETE_ESTIMATES.md. Transmission–accuracy disagreements are retained per continuation, not selected after averaging.','',
 'Primary paired signs: '+json.dumps(primary['paired_signs'],sort_keys=True)+'; block signs: '+json.dumps(primary['block_signs'],sort_keys=True)+'. All classifications: '+json.dumps(dict(collections.Counter(q['classification'] for q in v.values())),sort_keys=True)+'.','',
 'FATES_SUMMARY.md and FATES.jsonl retain every extinction, fixation and polymorphic endpoint, including both stay founders. JOINT_ENDPOINT_COUNTS.json separates policy fixation from single-founder fixation. NEGATIVE_OUTCOMES.jsonl and DECLINES.jsonl preserve negative effects and performance declines.','',
 'This exploratory question was selected with knowledge of 055. It reuses the cohort, histories and random tapes and is not independent confirmatory replication. The result does not establish memory origin, costly invasion, equilibrium, or a universal prediction rule. No additional scientific variant is authorized by this contract.','',
 '![Founder effects](figures/01_founder_effects.png)','', '![Population effects](figures/02_population_effects.png)']
 # Absolute local paths render in Codex; relative copies also travel with the portable package.
 for i,line in enumerate(text):
  if line.startswith('!['):text[i]=line.replace('(figures/','('+str(P/'figures')+'/')
 (P/'REPORT.md').write_text('\n'.join(text)+'\n')
 lines=['# All 162 estimates','','Fraction units; approximate pointwise 95% intervals.','','| Estimand | Mean | Lower | Upper | Classification |','|---|---|---|---|---|']
 for k,q in v.items():lines.append('| '+k.replace('|',' / ')+' | '+' | '.join('%.12f'%x for x in [q['mean']]+q['ci95'])+' | '+q['classification']+' |')
 (P/'COMPLETE_ESTIMATES.md').write_text('\n'.join(lines)+'\n')
 lines=['# All founder and policy fates','','Counts per fixed configuration and role, out of 192; dependent placements are not pooled as independent trials.','','| Cell / configuration / role | Extinct | Polymorphic | Fixed |','|---|---|---|---|']
 for k,q in sorted(read('FATE_COUNTS.json').items()):lines.append('| '+k.replace('|',' / ')+' | '+' | '.join(str(q.get(x,0)) for x in ('extinct','polymorphic','fixed'))+' |')
 (P/'FATES_SUMMARY.md').write_text('\n'.join(lines)+'\n')
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 d=P/'figures';d.mkdir(exist_ok=True)
 fig,axes=plt.subplots(2,2,figsize=(13,8),constrained_layout=True)
 for col,bg in enumerate(('F','H')):
  for row,groups in enumerate((CELLS,('Q_HALF_MINUS_ZERO_AT_P_ZERO','Q_HALF_MINUS_ZERO_AT_P_HALF','INTERACTION'))):
   ax=axes[row,col]
   for i,g in enumerate(groups):
    q=v[g+'|'+bg+'_BG_EFFECT|D40'];ax.plot([x*100 for x in q['ci95']],[i,i],color='tab:blue');ax.plot(q['mean']*100,i,'o',color='tab:blue')
   ax.set_yticks(range(len(groups)));ax.set_yticklabels(groups,fontsize=8);ax.axvline(0,color='gray',lw=1);ax.set(title=('F→H' if bg=='F' else 'H→F')+' matched founder effect',xlabel='Percentage points; pointwise 95%')
 fig.savefig(d/'01_founder_effects.png',dpi=150);fig.savefig(d/'01_founder_effects.pdf');plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(14,6),constrained_layout=True)
 for ax,m in zip(axes,('U','U40')):
  labs=[]
  for g in CELLS:
   for bg,color in [('F','tab:blue'),('H','tab:orange')]:
    q=v[g+'|'+bg+'_BG_EFFECT_POP|'+m];i=len(labs);ax.plot([x*100 for x in q['ci95']],[i,i],color=color);ax.plot(q['mean']*100,i,'o',color=color);labs.append(g+' / '+('F→H' if bg=='F' else 'H→F'))
  ax.set_yticks(range(len(labs)));ax.set_yticklabels(labs,fontsize=8);ax.axvline(0,color='gray',lw=1);ax.set(title='Mean population effect' if m=='U' else 'Terminal population effect',xlabel='Accuracy percentage points; pointwise 95%')
 fig.savefig(d/'02_population_effects.png',dpi=150);fig.savefig(d/'02_population_effects.pdf');plt.close(fig)
 print(json.dumps(dict(primary=PRIMARY,estimate=primary,classification_counts=dict(collections.Counter(q['classification'] for q in v.values())),main_figures=2)))
if __name__=='__main__':main()
