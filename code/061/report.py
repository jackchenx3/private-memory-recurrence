"""One two-panel figure and all14 outcomes; numerical certificates are not CIs."""
import csv
from common import *
from outcomes import KEYS,KERNELS,PRIMARY
from numerics import from_rational

def main():
 assert read('VALIDATION_CHECK.json')['status']=='PASS';audit=read('INDEPENDENT_CHECK.json');assert audit['status'] in ('PASS','PARTIAL_REJECTED_VECTORS');scheduler=read('SCHEDULER_RECEIPT.json');assert scheduler['status']=='COMPLETE'
 records=read('OUTCOMES.json');a=read('ASSESSMENT.json');checks=read('VALIDATION_CHECK.json');v={name:read('vectors/'+name+'.json.gz') for name in KERNELS}
 def fmt(key):
  q=records[key]
  if q['status']=='UNAVAILABLE':return 'unavailable: '+q['reason']
  return q['center_decimal']+' ['+q['lower_decimal']+', '+q['upper_decimal']+']'
 verdict={'supports_positive':'supports the positive directional prediction in this model','contradicts_positive':'contradicts the positive directional prediction in this model','sign_uncertified':'does not certify the predicted positive sign'}[a['decision']]
 text=['# ORG-STATIONARY-061: stationary use of supplied memory','',
 'The sole primary **'+verdict+'**. ACTIVE HALF-minus-ZERO stationary H fraction: '+fmt(PRIMARY)+'. The bounds are residual-based numerical enclosures, not statistical confidence intervals. No simulation burn-in, sampling uncertainty or bootstrap is involved.','',
 'Numerical certification status: **'+checks['scientific_status']+'**. Every kernel uses fixed80-decimal-digit elimination, deterministic pivoting and normalization, followed by ties-to-even rounding to the10^-60 grid. No precision or model parameter is changed after seeing an outcome. Negative/zero-total vectors are rejected without clipping; a failed residual criterion remains a numerical failure.','',
 '| Outcome | Center | Numerical enclosure | Sign / status |','|---|---|---|---|']
 for key in KEYS:
  q=records[key]
  text.append('| '+key.replace('|',' / ')+' | '+q.get('center_decimal','unavailable')+' | '+('['+q['lower_decimal']+', '+q['upper_decimal']+']' if 'lower_decimal' in q else q.get('reason','unavailable'))+' | '+q['sign']+' / '+q['status']+' |')
 text+=['','Exact reduced rational centers and endpoints, plus outward-rounded decimal strings and percentage points, are stored in OUTCOMES.json. The CSV preserves all14 records. Adverse and uncertified signs are not omitted. No one-descendant benchmark from the former model is applied here.','',
 'Stationary H and actual current population accuracy U are separate rewards. ACTIVE_ZERO and ACTIVE_HALF H are also compared with the exact1/2 reference. U is scored against the current target b, not the earlier target a or the next target. The H-fraction prediction does not imply an accuracy advantage.','',
 '| Kernel | Exact residual r | TV error bound E | r≤10^-30 |','|---|---|---|---|']
 for name in KERNELS:
  q=v[name]
  if q['status']=='REJECTED':text.append('| '+name+' | rejected | '+q['reason']+' | no |');continue
  c=q['certificate'];r=c['residual'];e=c['total_variation_bound'];text.append('| '+name+' | '+r['numerator']+'/'+r['denominator']+' | '+e['numerator']+'/'+e['denominator']+' | '+str(c['criterion_pass'])+' |')
 text+=['','For each saved nonnegative integer vector k, K=sum(k) and p=k/K. The exact residual numerator is R=sum_j|sum_i k_i A_ij−k_j D|; all arithmetic uses arbitrary-precision integers. With r=R/(KD) and alpha=1/3774873600, E=min(1,r/alpha) bounds total variation from stationarity and therefore each range-[0,1] reward error. Difference radii sum the component bounds; subtracting exact1/2 adds none. Primitive enclosures are intersected with[0,1].','',
 'Uniqueness is structural: selecting ordered scout0/scout1 on two successive updates can set any final caches/genotypes, targets and policies, with probability at least1/966367641600 per destination. This yields a positive two-step kernel and uniform minorization alpha. Produced supports are checked for one strongly connected class and period1. Every global genotype/cache/target-complement entry is checked; neutral policy-complement invariance is checked exactly. Neutral H=1/2 follows from that symmetry and uniqueness and must lie inside its certified enclosure; solver output is not forced to be symmetric.','',
 'This is a new two-individual/one-bit mathematical model with256 complete states. Each state contains ordered genotype/cache/policy records and the last two targets. Eight candidate slots retain duplicates; nonparents inherit recipient policy and store the recipient’s previous genotype as cache. Ordered weighted selection without replacement precedes independent1/16 policy flips for both survivors. ACTIVE H probes its private cache; NEUTRAL probes are fresh for every label. Storage and H/F alternatives are supplied, and symmetric switching continually lets absent policies return.','',
 'The four exact256×256 numerator matrices use D=377864847360. There are262144 stored transition numerators,1024 stationary weights and exactly14 outcome records. The literal event expansion has29360128 branches over the four kernels. Four matrices and four fixed-precision solve attempts are computed once; durable row-chunk, matrix and solve receipts preserve partial completion.','',
 'Job '+scheduler['job_id']+' completed with scheduler exit '+scheduler.get('exit_code','unknown')+'. The single allocation requested1CPU,4GiB and30minutes. Accounting, elapsed-time and resource-monitor records are retained. Scientific/source/report delivery is bounded at64MiB; DELIVERY_SIZE_CHECK.json records the measured production package, and FINAL_SIZE_CHECK.json records final delivery size.','',
 'The packaged standalone checker reconstructs the32 prespecified rows without importing the producer kernel, checks all four saved exact residual certificates and all14 saved outcome definitions, and never resolves stationarity. Its execution is a producer check; independent supervisor review is a separate responsibility. The audit rows are0,36,85,113,142,170,219,255 for every kernel. Raw reconstructed rows are retained in AUDITED_ROWS.json.gz.','',
 'These stationary results concern imposed memory storage and ongoing symmetric policy supply. They are not an equilibrium analysis or independent replication of the published32-individual/32-bit model. They do not establish spontaneous memory origin, biological mutation rates, a general costly advantage or practical optimizer usefulness. This finite assignment stops here; no parameter grid, second allocation, new manuscript or release is automatic.','',
 '![Stationary H and U](figures/01_stationary_H_U.png)']
 (P/'REPORT.md').write_text('\n'.join(text)+'\n')
 with (P/'OUTCOMES.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['key','status','center','lower_outward','upper_outward','center_pp','lower_pp_outward','upper_pp_outward','sign'])
  for key in KEYS:
   q=records[key];w.writerow([key,q['status']]+[q.get(k,'') for k in ('center_decimal','lower_decimal','upper_decimal','center_percentage_points','lower_percentage_points','upper_percentage_points')]+[q['sign']])
 figures(records)
 assert package_bytes()<=64*1024*1024
 print(json.dumps(dict(outcomes=14,decision=a['decision'],scientific_status=checks['scientific_status'],figure_count=1)))

def figures(records):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 folder=P/'figures';folder.mkdir(exist_ok=True);fig,axes=plt.subplots(1,2,figsize=(11,5),constrained_layout=True)
 for ax,reward,title in zip(axes,('H','U'),('Stationary H fraction','Stationary population accuracy')):
  for i,name in enumerate(KERNELS):
   q=records[name+'|'+reward]
   if q['status']=='UNAVAILABLE':ax.text(.5,i,'unavailable',ha='center');continue
   center=float(from_rational(q['center']));lo=float(from_rational(q['lower']));hi=float(from_rational(q['upper']));color='tab:blue' if q['status']=='CERTIFIED' else 'tab:red'
   ax.plot([lo,hi],[i,i],color=color,lw=2);ax.plot(center,i,'o',color=color)
  ax.set_yticks(range(4));ax.set_yticklabels(KERNELS,fontsize=9);ax.invert_yaxis();ax.set_xlim(0,1);ax.set(title=title,xlabel='Fraction; residual-based numerical enclosures')
  if reward=='H':ax.axvline(.5,color='gray',ls='--',label='Neutral exact H=1/2');ax.legend(fontsize=8)
 fig.suptitle('Numerical enclosures may be narrower than markers; no statistical intervals',fontsize=10)
 fig.savefig(folder/'01_stationary_H_U.png',dpi=160);fig.savefig(folder/'01_stationary_H_U.pdf');plt.close(fig)
if __name__=='__main__':main()
