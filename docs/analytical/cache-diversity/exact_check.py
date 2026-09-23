"""Exact finite combinatorics for two-candidate IID-target selection; no RNG or population model."""
from pathlib import Path
from fractions import Fraction
from math import comb
import datetime,hashlib,json
P=Path(__file__).resolve().parent

def gain(d):
 return sum((Fraction(comb(d,j)*max(2*j-d,0),2**d) for j in range(d+1)),Fraction(0))
def fresh_gain(n):
 return sum((Fraction(comb(n,d),2**n)*gain(d) for d in range(n+1)),Fraction(0))
def pack(x):return dict(numerator=x.numerator,denominator=x.denominator,decimal=float(x))
checks=0;enumerated_targets=0;enumerated_fresh_pairs=0
for n in range(1,11):
 for d in range(n+1):
  y=2**d-1
  brute=Fraction(sum(max(bin(t).count('1')-bin(y^t).count('1'),0) for t in range(2**n)),2**n)
  enumerated_targets+=2**n
  assert brute==gain(d);checks+=1
for d in range(1,65):
 assert gain(d)==Fraction(d*comb(d-1,(d-1)//2),2**d);checks+=1
for n in range(1,8):
 brute=Fraction(sum(max(bin(t).count('1')-bin(t^y).count('1'),0) for t in range(2**n) for y in range(2**n)),2**(2*n))
 enumerated_fresh_pairs+=2**(2*n)
 assert brute==fresh_gain(n)==gain(2*n)/2;checks+=1
n=32;fresh=fresh_gain(n);assert fresh==gain(2*n)/2;checks+=1
rows=[dict(distance=d,expected_gain_bits=pack(gain(d)),expected_normalized_gain=pack(gain(d)/n),expected_best_mismatch_bits=pack(Fraction(n,2)-gain(d))) for d in range(n+1)]
q=dict(status='PASS',prepared_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),bits=n,exact_identity_checks=checks,enumerated_targets=enumerated_targets,enumerated_fresh_target_candidate_pairs=enumerated_fresh_pairs,fresh_expected_gain_bits=pack(fresh),fresh_expected_normalized_gain=pack(fresh/n),fresh_expected_best_mismatch_bits=pack(Fraction(n,2)-fresh),rows=rows,random_draws=0,population_paths=0,scope='Uniform target independent of fixed current/cache genotypes; best of these two candidates only. No scout, local offspring, global competition, costs, inheritance or longer horizon evaluated.')
(P/'EXACT_RESULTS.json').write_text(json.dumps(q,indent=2)+'\n')
text=f'''# A different candidate can help without predicting an independent target

Derived {q['prepared_at_utc']}. This is an exact local mathematical baseline, not population evidence or a new algorithmic novelty claim. No random values, evolving population or experiment outcomes enter the calculation. It leaves ORG-NOVELTY-045 unchanged.

Let x and y be fixed n-bit current and cached candidates, and T a uniformly random n-bit target independent of both. Let H denote Hamming mismatch and d=H(x,y). Both unselected expected mismatches equal n/2. Selecting the better of the two nevertheless gives expected improvement over x of

`g(d) = 2^(-d) sum_(j=0)^d binom(d,j) max(2j−d,0)`.

For d≥1 this also equals `d binom(d−1,floor((d−1)/2)) / 2^d`; g(0)=0. The selected expected mismatch is n/2−g(d).

Proof: on the n−d positions where x and y agree, both candidates share K mismatches. On the d differing positions, if x has J mismatches, y has d−J. Thus their total mismatches are K+J and K+d−J, with J~Binomial(d,1/2). Improvement from choosing y when it is better is max(2J−d,0). Taking its finite binomial expectation gives the formula. Uniformity of T also gives the equal unselected means. No predictability of T is needed for a positive local gain when d>0.

For a fresh uniform candidate Y independent of x and T, its distance D from x is Binomial(n,1/2), so the expected gain is E[g(D)]. Equivalently H(x,T) and H(Y,T) are independent Binomial(n,1/2) variables. Their difference has the distribution B−n with B~Binomial(2n,1/2). Symmetry gives the same gain `E|B−n|/2 = g(2n)/2`. These are identities of ideal distributions, not assertions that a selected population or a fixed realized stream is uniform.

For n=32, the exact fresh-candidate gain is {fresh.numerator}/{fresh.denominator} = **{float(fresh):.9f} mismatch bits**, or **{100*float(fresh)/n:.9f} percentage points of accuracy**. The expected best-of-two mismatch is {float(Fraction(n,2)-fresh):.9f} bits. A stored candidate's corresponding gain depends on its distance from the current candidate:

| Current–cache distance d | Exact local gain in bits | Accuracy gain in percentage points |
|---:|---:|---:|
'''
for d in [0,1,8,16,24,32]:text+=f'| {d} | {float(gain(d)):.9f} | {100*float(gain(d))/n:.9f} |\n'
text+='''
The implication is limited but useful: an advantage over a duplicate-current probe under IID targets does not, on its own, identify predictive historical information. A cache can instead provide an alternative candidate; for this two-candidate assay, current–cache Hamming distance fully determines its expected IID advantage. A fresh candidate is therefore an informative budget-matched comparator.

This does not say which policy wins ORG-NOVELTY-045. Its actual algorithm also has an ordinary scout, local children, global selection, inherited state, rare loss and a finite horizon. Recurrent targets are not independent of history. Neither g(d), its average over visited states nor a matched unselected mean is a validated predictor of carrier-frequency or population-performance ranking. No extra predictor, endpoint, grouping of survivors or parameter has been added to the experiment.

Verification uses exact rational arithmetic. The direct formula is checked by exhaustive target enumeration for every distance in dimensions 1–10. The closed form is checked through distance 64. The fresh-candidate mixture and difference-distribution forms agree with exhaustive joint target/candidate enumeration in dimensions 1–7 and with each other at n=32. All finite identities passed; these checks are not Monte Carlo replication.

![Exact two-candidate IID-target gain; not a population ranking](PLOT_PATH)
'''.replace('PLOT_PATH',str(P/'local_gain.png'))
(P/'NOTE.md').write_text(text)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(7.8,4.5));ds=list(range(33));ax.plot(ds,[100*float(gain(d))/n for d in ds],marker='o',markersize=3,label='Fixed cached candidate at distance d');ax.axhline(100*float(fresh)/n,color='#be5a27',linestyle='--',label='Independent uniform fresh candidate');ax.set(xlabel='Hamming distance between current and cached candidates',ylabel='Expected local accuracy gain (percentage points)',title='Best of two under an independent uniform target');ax.legend(frameon=False,loc='lower right');ax.grid(alpha=.18);fig.text(.5,.015,'Exact local expectation; no population, inheritance or long-horizon claim.',ha='center',fontsize=9);fig.tight_layout(rect=(0,.035,1,1));fig.savefig(P/'local_gain.png',dpi=180);fig.savefig(P/'local_gain.svg');plt.close(fig)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();(P/'SHA256SUMS').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(P.iterdir()) if p.is_file() and p.name!='SHA256SUMS'))
print(json.dumps({k:v for k,v in q.items() if k!='rows'},indent=2))
