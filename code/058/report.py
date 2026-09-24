"""Outcome-driven report from completed, independently checked saved outputs."""
import collections
from common import *
from analysis import *
def main():
 assert read('VALIDATION_CHECK.json')['status']=='PASS' and read('INDEPENDENT_AUDIT.json')['status']=='PASS'
 v=read('ESTIMATES.json');a=read('ASSESSMENT.json');s=read('SCHEDULER_RECEIPT.json');assert s['status']=='COMPLETE'
 def fmt(k,scale=100):
  q=v[k];return '%.4f [%.4f, %.4f]'%tuple(scale*x for x in [q['mean']]+q['ci95'])
 def label(k):return k.replace('|',' / ')
 direction={'supports_positive':'supports the fixed positive directional prediction','contradicts_positive':'contradicts the fixed positive directional prediction','unresolved':'leaves the fixed positive directional prediction unresolved'}[a['decisions']['direction']]
 benchmark={'supports_exceeding_one_expected_descendant':'The interval supports exceeding one additional expected descendant.','does_not_support_at_least_one_expected_descendant':'The interval does not support a contribution of at least one expected descendant.','unresolved':'The one-expected-descendant benchmark remains unresolved.'}[a['decisions']['benchmark']]
 lines=['# ORG-LANDSCAPE-058: recurrence under a four-bit-trap objective','',
 'The primary result **'+direction+'**. After HALF preparation under TRAP4, the HALF-minus-ZERO change in the matched F-to-H founder effect is **'+fmt(PRIMARY)+' percentage points**, or '+fmt(PRIMARY,1)+' in fraction units and '+fmt(PRIMARY,32)+' expected descendants (approximate pointwise 95% intervals).','',
 benchmark+' The fixed benchmark is 1/32 frequency =3.125 percentage points =one expected descendant per introduction. It is a model resolution scale, not a biological threshold. Direction and benchmark are assessed separately.','',
 'Within future HALF, the TRAP4 matched F-to-H founder effect is '+fmt('TRAP4|Q_HALF|F_BG_EFFECT|D40')+' pp, while the absolute introduced-H change is '+fmt('TRAP4|Q_HALF|F_BG_SWITCH|D40')+' pp. A positive difference between future laws does not establish that H is beneficial within HALF.','',
 'The paired HAM future-law effect is '+fmt('HAM|Q_HALF_MINUS_ZERO|F_BG_EFFECT|D40')+' pp. The direct TRAP4-minus-HAM interaction is '+fmt(CROSS+'|F_BG_EFFECT|D40')+' pp; this is the paired interaction itself, not an inference from differing significance labels. Neither secondary quantity has a fixed directional prediction.','',
 'Both objectives minimize integer losses0–32. HAM counts mismatches. TRAP4 sums eight fixed four-bit block losses [1,2,3,4,0] for 0–4 matching bits; x=target is the unique global optimum and there are256 strict single-bit local optima including that optimum. Utility is1−mean(loss)/32. TRAP4 utility is not matching-bit accuracy. Equal nominal score ranges do not equalize selection intensity. Cross-objective effects include prepared-state and score-distribution differences and do not isolate epistasis alone.','',
 'Each objective has its own192 zero-start genotype preparations and384 HALF policy preparations. The paired objectives use common indexed target, proposal, placement and survival tapes, with distinct families across stages. Initial selection remains elitist; policy preparation and transfer use the accepted exponential race with weights2^(-loss), cost0. All endpoints are retained; founders are rebased to physical slots and substitutions preserve genotype and cache. No survival conditioning, tuning, cohort pooling or outcome-preview pilot was used.','',
 'Job '+s['job_id']+' completed with exit '+s.get('exit_code','unknown')+'. One allocation:1CPU,4GiB,30minutes. There are5,760 new scientific paths,29,675,520 scientific objective calls and3,193 new seed IDs. The24 target blocks are independent units, with two placements and then eight replicates averaged before2,000 whole-block bootstrap resamples. All114 intervals are approximate and pointwise, with no family-wide or conjunction guarantee. ACCOUNTING.psv records actual scheduler usage.','',
 'The independent audit reconstructed every recorded objective score and candidate/donor/selection/cache/founder mapping in the prospectively selected block0:16 initial,32 policy and192 transfer paths. All114 estimates were independently recomputed from saved time series. Recorded-score reconstructions and deterministic correctness fixtures are separate from scientific objective calls.','',
 '| Objective / future / background | Switch D40 (pp) | Stay D40 (pp) | Matched effect (pp) |','|---|---|---|---|']
 for c in CELLS:
  for bg in ('F','H'):lines.append('| '+label(c)+' / '+bg+' | '+' | '.join(fmt(c+'|'+bg+'_BG_'+kind+'|D40') for kind in ('SWITCH','STAY','EFFECT'))+' |')
 lines+=['','All founder changes start from1/32. Add3.125pp to a switch/stay D40 to obtain terminal frequency. The F background introduces H; the H background introduces F. Every founder estimate and interval is available in fraction, pp and expected-descendant units in ESTIMATES.csv.','',
 '| Objective / future / background | Switch U (%) | Stay U (%) | Effect U (pp) | Switch U40 (%) | Stay U40 (%) | Effect U40 (pp) |','|---|---|---|---|---|---|---|']
 for c in CELLS:
  for bg in ('F','H'):lines.append('| '+label(c)+' / '+bg+' | '+' | '.join(fmt(c+'|'+bg+'_BG_'+kind+'_POP|'+m) for m in ('U','U40') for kind in ('SWITCH','STAY','EFFECT'))+' |')
 counts=dict(collections.Counter(q['classification'] for q in v.values()));validation=read('VALIDATION_CHECK.json')
 lines+=['','Population utilities use each objective’s own metric; no cross-objective utility difference grid is computed. Both arms and matched effects are shown, including lower performance or unresolved effects.','',
 'Primary replicate signs: '+json.dumps(v[PRIMARY]['paired_signs'],sort_keys=True)+'; block signs: '+json.dumps(v[PRIMARY]['block_signs'],sort_keys=True)+'. Classification counts across the fixed114-estimate catalog: '+json.dumps(counts,sort_keys=True)+'. Observed exact zeros are identified from stored outcomes; they are not labeled algebraic identities.','',
 'There are '+str(validation['negative_paired_records'])+' negative paired metric records and '+str(validation['transmission_accuracy_disagreements'])+' founder/utility sign disagreements. All negative records, orientation signs, full paths, block aggregates, founder fates, joint endpoints and utility declines are retained. DECLINES.jsonl covers transfer and PREPARATION_DECLINES.jsonl covers both preparation stages. The legacy filename TRANSMISSION_ACCURACY_DISAGREEMENTS.jsonl means objective-utility disagreements for this experiment.','',
 'FATES_SUMMARY.md retains every configuration and founder/policy role, including extinct or polymorphic introductions and opposite-direction outcomes. COMPLETE_ESTIMATES.md and ESTIMATES.csv contain all114 estimates. A favorable mean does not imply routine establishment, fixation, population benefit or universality across landscapes.','',
 'This finite challenge tests one fixed interacting objective in this model. It does not establish a general ruggedness law, memory origin, biological adaptation, costly invasion or equilibrium. Combined with the accepted earlier studies it can assess whether the earlier future-recurrence contribution survives this particular objective change; it cannot attribute a change uniquely to epistasis. No previous cohort is pooled. This assignment stops here: any manuscript supplement or new research direction requires a separate decision, and no further variant is automatically added.','',
 '![Founder results](figures/01_founder_results.png)','', '![Both population arms](figures/02_population_arms.png)']
 (P/'REPORT.md').write_text('\n'.join(lines)+'\n')
 allrows=['# All114 estimates','','Approximate pointwise95% intervals. Founder rows also include expected-descendant units.','','| Key | Fraction mean [CI] | pp mean [CI] | Expected descendants [CI] | Classification |','|---|---|---|---|---|']
 for k,q in v.items():allrows.append('| '+label(k)+' | '+fmt(k,1)+' | '+fmt(k)+' | '+(fmt(k,32) if k.endswith('|D40') else 'not applicable')+' | '+q['classification']+' |')
 (P/'COMPLETE_ESTIMATES.md').write_text('\n'.join(allrows)+'\n')
 fates=['# All founder and policy fates','','Counts out of192 per configuration and role; placements are dependent.','','| Cell / configuration / role | Extinct | Polymorphic | Fixed | Above initial | Below initial |','|---|---|---|---|---|---|']
 for k,q in sorted(read('FATE_COUNTS.json').items()):fates.append('| '+label(k)+' | '+' | '.join(str(q.get(x,0)) for x in ('extinct','polymorphic','fixed','above_initial','below_initial'))+' |')
 (P/'FATES_SUMMARY.md').write_text('\n'.join(fates)+'\n')
 figures(v)
 print(json.dumps(dict(primary=PRIMARY,assessment=a['decisions'],main_figures=2)))

def figures(v):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 folder=P/'figures';folder.mkdir(exist_ok=True)
 def draw(ax,k,y,color,marker='o'):
  q=v[k];ax.plot([x*100 for x in q['ci95']],[y,y],color=color);ax.plot(q['mean']*100,y,marker,color=color)
 fig,axes=plt.subplots(1,2,figsize=(13,6),constrained_layout=True)
 groups=list(CELLS)+['HAM|Q_HALF_MINUS_ZERO','TRAP4|Q_HALF_MINUS_ZERO',CROSS]
 for ax,bg in zip(axes,('F','H')):
  for i,g in enumerate(groups):draw(ax,g+'|'+bg+'_BG_EFFECT|D40',i,'tab:orange' if g.startswith('TRAP4') else 'tab:blue')
  ax.set_yticks(range(len(groups)));ax.set_yticklabels([g.replace('|',' / ') for g in groups],fontsize=8);ax.axvline(0,color='gray',lw=1);ax.invert_yaxis();ax.set(title=('F→H' if bg=='F' else 'H→F')+' matched founder effect',xlabel='Percentage points; pointwise95% intervals')
  if bg=='F':ax.plot([3.125,3.125],[4.7,5.3],color='black',lw=2,label='Primary benchmark:1 descendant');ax.legend(fontsize=8,loc='best')
 fig.savefig(folder/'01_founder_results.png',dpi=150);fig.savefig(folder/'01_founder_results.pdf');plt.close(fig)
 fig,axes=plt.subplots(2,2,figsize=(13,9),constrained_layout=True)
 for row,obj in enumerate(OBJECTIVES):
  for col,m in enumerate(('U','U40')):
   ax=axes[row,col];labels=[]
   for q in LAWS:
    for bg in ('F','H'):
     i=len(labels);labels.append(q+' / '+('F→H' if bg=='F' else 'H→F'))
     for kind,offset,color in [('SWITCH',-.12,'tab:orange'),('STAY',.12,'tab:blue')]:draw(ax,obj+'|Q_'+q+'|'+bg+'_BG_'+kind+'_POP|'+m,i+offset,color)
   ax.plot([],[],'o-',color='tab:orange',label='Switch');ax.plot([],[],'o-',color='tab:blue',label='Stay');ax.set_yticks(range(4));ax.set_yticklabels(labels);ax.invert_yaxis();ax.set(title=obj+(' mean utility' if m=='U' else ' terminal utility'),xlabel='Own-objective utility (%); pointwise95%');ax.legend(fontsize=8)
 fig.savefig(folder/'02_population_arms.png',dpi=150);fig.savefig(folder/'02_population_arms.pdf');plt.close(fig)
if __name__=='__main__':main()
