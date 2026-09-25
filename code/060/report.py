"""Outcome-driven report; no endpoint changes or extra interval grids after execution."""
import collections
from common import *
from analysis import *
def main():
 assert read('VALIDATION_CHECK.json')['status']=='PASS' and read('INDEPENDENT_AUDIT.json')['status']=='PASS'
 est=read('ESTIMATES.json');a=read('ASSESSMENT.json');s=read('SCHEDULER_RECEIPT.json');assert s['status']=='COMPLETE'
 def fmt(k,scale=100):q=est[k];return '%.5f [%.5f, %.5f]'%tuple(scale*v for v in [q['mean']]+q['ci95'])
 verdict={'supports_negative':'supports the fixed negative-interaction prediction','contradicts_negative':'contradicts the fixed negative-interaction prediction','unresolved':'leaves the fixed negative-interaction prediction unresolved'}[a['decisions']['direction']]
 text=['# ORG-OBSERVATION-060: bounded measurement error','',
 'The primary **'+verdict+'**. The paired noise-by-recurrence interaction on the H-founder effect is **'+fmt(PRIMARY)+' percentage points** (exploratory pointwise95% interval), or '+fmt(PRIMARY,1)+' in fraction units and '+fmt(PRIMARY,32)+' expected descendants. This is the direct paired interaction, not a comparison of significance labels.','',
 'The primary interval is '+a['decisions']['minus_one_descendant']+' the−1-descendant threshold and '+a['decisions']['plus_one_descendant']+' the+1-descendant threshold. These thresholds are±1/32 founder fraction, or±3.125percentage points. They are model resolution scales, not biological or practical thresholds; overlap or inclusion within the band does not establish equivalence.','',
 'Under exact measurement, the HALF-minus-ZERO founder EFFECT is '+fmt('EXACT_Q_HALF_MINUS_ZERO|EFFECT|D40')+' pp ('+a['recurrence']['EXACT']['plus_one_descendant']+'). Under noisy measurement it is '+fmt('NOISY_Q_HALF_MINUS_ZERO|EFFECT|D40')+' pp ('+a['recurrence']['NOISY']['plus_one_descendant']+'). Each comparison uses the separate+1/32 scale. Attenuation must be interpreted relative to the exact effect observed here: a negative interaction alone does not establish loss of a positive advantage. The noisy recurrence effect is retained regardless of the primary.','',
 'All192 starting populations are the authenticated057 HALF-prepared F backgrounds, prepared under exact measurement. They are reused without filtering and are not an independent training cohort. Founder IDs and caches use their existing rebased states. H is introduced at each of two newly shuffled slots; STAY supplies the same two founder controls. All2304 transfer paths are new, with paired inputs across interfaces, future laws and placements. No057/058/059 outcomes or prior transfer tapes are reused or pooled.','',
 'Every initial/candidate query computes true Hamming loss once. EXACT returns that integer; NOISY returns h+(2u−1) using its frozen per-query uniform. Observations are not clipped below0 or above32. Duplicate genotypes are charged and measured separately. Donor choice and survivor choice use the same returned score. Initial observations do not influence later decisions, because parents are measured again at every update.','',
 'The real-score adapter computes race keys−log(open_uniform)×2.0**observed_score and selects the32 lowest(key,tie,index). It retains the accepted52-bit open-uniform conversion, candidate/cache rules and policy/founder inheritance. Accepted source files remain byte-identical. Zero-error fixtures reproduce the accepted057 donor choices, races, states and true metrics. Truth diagnostics use already recorded query values and do not remeasure candidates or enter decisions.','',
 '| Cell | Introduced H D40 (pp) | Unchanged F founder D40 (pp) | Matched founder effect (pp) |','|---|---|---|---|']
 for cell in CELLS:text.append('| '+cell+' | '+' | '.join(fmt(cell+'|'+kind+'|D40') for kind in ('SWITCH','STAY','EFFECT'))+' |')
 text+=['','Founder changes are relative to the initial1/32 frequency; add3.125pp to SWITCH/STAY D40 to obtain terminal frequency. Founder transmission is not population accuracy. All founder intervals also appear in fraction and expected-descendant units in ESTIMATES.csv.','',
 '| Paired contrast | Founder effect D40 (pp) | Expected descendants |','|---|---|---|']
 for g in GROUPS[4:]:text.append('| '+g+' | '+fmt(g+'|EFFECT|D40')+' | '+fmt(g+'|EFFECT|D40',32)+' |')
 text+=['','| Cell | Switch mean true accuracy (%) | Stay mean true accuracy (%) | Mean effect (pp) | Switch terminal true accuracy (%) | Stay terminal true accuracy (%) | Terminal effect (pp) |','|---|---|---|---|---|---|---|']
 for cell in CELLS:text.append('| '+cell+' | '+' | '.join(fmt(cell+'|'+kind+'_POP|'+m) for m in ('U','U40') for kind in ('SWITCH','STAY','EFFECT'))+' |')
 check=read('VALIDATION_CHECK.json');primary=est[PRIMARY]
 text+=['','Population accuracy is calculated from true losses, not noisy observations. All population contrasts also use1024×fraction for expected additional matching bits across the32×32 comparisons; for U this is averaged over post-selection updates. These units remain distinct from expected descendants. Both arms, including adverse or unresolved effects, are reported.','',
 'Primary replicate signs: '+json.dumps(primary['paired_signs'],sort_keys=True)+'; block signs: '+json.dumps(primary['block_signs'],sort_keys=True)+'. Fixed-catalog classifications: '+json.dumps(dict(collections.Counter(q['classification'] for q in est.values())),sort_keys=True)+'. All81 estimates are in COMPLETE_ESTIMATES.md and ESTIMATES.csv, including '+str(check['negative_records'])+' negative paired metric records and '+str(check['exact_ties'])+' exact ties. No algebraic zero is required by this catalog.','',
 'Founder fates and every placement-specific contrast remain in FOUNDER_FATES.jsonl, FATES_SUMMARY.md and ORIENTATION_METRICS.jsonl. Inference is not conditioned on survival, extinction or establishment. There are '+str(check['decline_records'])+' retained updates with absolute true-accuracy decline or negative within-target selection improvement, and '+str(check['transmission_accuracy_disagreements'])+' founder/accuracy sign disagreements. Observation range counts (charged queries, not independent samples): '+json.dumps(read('OBSERVATION_RANGE_COUNTS.json'),sort_keys=True)+'.','',
 'The two placements are averaged within each replicate; then eight paired values are averaged within each of24 independent blocks. There are2000 new shared whole-block resampling rows and linear2.5/97.5percentiles. Intervals are exploratory and pointwise, with no simultaneous family-wide guarantee. Unresolved effects are not evidence of equality.','',
 'Job '+s['job_id']+' completed with exit '+s.get('exit_code','unknown')+'. One allocation:1CPU,4GiB,15minutes. Exactly2304paths and11870208objective calls were used (73728initial+11796480candidate); there were no new preparation paths or extra diagnostic loss queries. There are1393new seed IDs and989184indexed noise uniforms, shared across paired paths. Equal query counts do not imply equal real computational or measurement costs. Actual resource records are in ACCOUNTING.psv and MEMORY_TELEMETRY.jsonl.','',
 'The prospective audit covered all96 raw block0 paths and reconstructed494592 queries, their true/returned scores, donor and race selection, cache/founder transitions and true endpoints. All81 estimates were independently recomputed from saved records. No scientific trajectory was rerun for verification.','',
 'This tests one bounded-error transfer interface after exact-observation preparation. Noise changes both donor and survivor decisions, so it is not an isolated test of either mechanism. It does not test noisy historical preparation, other noise magnitudes, practical measuring devices, universal robustness or biological adaptation. Study030 used noisy measurements in a different population-wide detector/prototype model; this task concerns an inherited private-memory founder estimand and does not establish literature-wide novelty.','',
 'This finite assignment stops here. The supervisor owns the next scientific decision and manuscript integration; no noise grid, extra cohort, landscape, cost, horizon or publication follows automatically.','',
 '![Founder contrasts](figures/01_founder_contrasts.png)','', '![Population accuracy](figures/02_population_accuracy.png)']
 (P/'REPORT.md').write_text('\n'.join(text)+'\n')
 lines=['# All81 estimates','','Exploratory pointwise95% intervals; count units are descendants for D40 and matching bits for accuracy.','','| Key | Fraction [CI] | pp [CI] | Count units [CI] | Classification |','|---|---|---|---|---|']
 for k,q in est.items():lines.append('| '+k.replace('|',' / ')+' | '+fmt(k,1)+' | '+fmt(k)+' | '+fmt(k,32 if k.endswith('D40') else 1024)+' | '+q['classification']+' |')
 (P/'COMPLETE_ESTIMATES.md').write_text('\n'.join(lines)+'\n')
 lines=['# Founder fates','','Counts out of192 per fixed cell/configuration/placement. Placements are paired, not independent trials.','','| Cell / configuration / placement | Extinct | Polymorphic | Fixed |','|---|---|---|---|']
 for k,q in sorted(read('FOUNDER_FATE_COUNTS.json').items()):lines.append('| '+k.replace('|',' / ')+' | '+' | '.join(str(q.get(x,0)) for x in ('extinct','polymorphic','fixed'))+' |')
 (P/'FATES_SUMMARY.md').write_text('\n'.join(lines)+'\n');figures(est);print(json.dumps(dict(primary=PRIMARY,decisions=a['decisions'],main_figures=2)))

def figures(est):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 folder=P/'figures';folder.mkdir(exist_ok=True)
 fig,ax=plt.subplots(figsize=(12,7),constrained_layout=True)
 for i,g in enumerate(GROUPS):
  q=est[g+'|EFFECT|D40'];color='tab:red' if g=='NOISE_BY_RECURRENCE' else 'tab:blue';ax.plot([100*x for x in q['ci95']],[i,i],color=color);ax.plot(q['mean']*100,i,'o',color=color)
 ax.set_yticks(range(9));ax.set_yticklabels(GROUPS,fontsize=9);ax.axvline(0,color='gray',lw=1);ax.invert_yaxis();ax.set(title='Matched H-founder effects and paired contrasts',xlabel='Founder percentage points; exploratory pointwise95% intervals')
 for threshold in (-3.125,3.125):ax.plot([threshold,threshold],[7.75,8.25],color='black',lw=2)
 fig.savefig(folder/'01_founder_contrasts.png',dpi=150);fig.savefig(folder/'01_founder_contrasts.pdf');plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(13,6),constrained_layout=True)
 for ax,m in zip(axes,('U','U40')):
  for i,cell in enumerate(CELLS):
   for kind,offset,color in (('SWITCH',-.12,'tab:orange'),('STAY',.12,'tab:blue')):
    q=est[cell+'|'+kind+'_POP|'+m];ax.plot([100*x for x in q['ci95']],[i+offset]*2,color=color);ax.plot(q['mean']*100,i+offset,'o',color=color)
  ax.plot([],[],'o-',color='tab:orange',label='Switch F→H');ax.plot([],[],'o-',color='tab:blue',label='Stay all F');ax.set_yticks(range(4));ax.set_yticklabels(CELLS,fontsize=9);ax.invert_yaxis();ax.set(title='Mean true accuracy' if m=='U' else 'Terminal true accuracy',xlabel='Matching bits (%); pointwise95%');ax.legend(fontsize=8)
 fig.savefig(folder/'02_population_accuracy.png',dpi=150);fig.savefig(folder/'02_population_accuracy.pdf');plt.close(fig)
if __name__=='__main__':main()
