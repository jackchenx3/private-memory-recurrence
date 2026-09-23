# A different candidate can help without predicting an independent target

Derived 2026-09-22T15:13:32.258416+00:00. This is an exact local mathematical baseline, not population evidence or a new algorithmic novelty claim. No random values, evolving population or experiment outcomes enter the calculation. It leaves ORG-NOVELTY-045 unchanged.

Let x and y be fixed n-bit current and cached candidates, and T a uniformly random n-bit target independent of both. Let H denote Hamming mismatch and d=H(x,y). Both unselected expected mismatches equal n/2. Selecting the better of the two nevertheless gives expected improvement over x of

`g(d) = 2^(-d) sum_(j=0)^d binom(d,j) max(2j−d,0)`.

For d≥1 this also equals `d binom(d−1,floor((d−1)/2)) / 2^d`; g(0)=0. The selected expected mismatch is n/2−g(d).

Proof: on the n−d positions where x and y agree, both candidates share K mismatches. On the d differing positions, if x has J mismatches, y has d−J. Thus their total mismatches are K+J and K+d−J, with J~Binomial(d,1/2). Improvement from choosing y when it is better is max(2J−d,0). Taking its finite binomial expectation gives the formula. Uniformity of T also gives the equal unselected means. No predictability of T is needed for a positive local gain when d>0.

For a fresh uniform candidate Y independent of x and T, its distance D from x is Binomial(n,1/2), so the expected gain is E[g(D)]. Equivalently H(x,T) and H(Y,T) are independent Binomial(n,1/2) variables. Their difference has the distribution B−n with B~Binomial(2n,1/2). Symmetry gives the same gain `E|B−n|/2 = g(2n)/2`. These are identities of ideal distributions, not assertions that a selected population or a fixed realized stream is uniform.

For n=32, the exact fresh-candidate gain is 916312070471295267/576460752303423488 = **1.589548060 mismatch bits**, or **4.967337687 percentage points of accuracy**. The expected best-of-two mismatch is 14.410451940 bits. A stored candidate's corresponding gain depends on its distance from the current candidate:

| Current–cache distance d | Exact local gain in bits | Accuracy gain in percentage points |
|---:|---:|---:|
| 0 | 0.000000000 | 0.000000000 |
| 1 | 0.500000000 | 1.562500000 |
| 8 | 1.093750000 | 3.417968750 |
| 16 | 1.571044922 | 4.909515381 |
| 24 | 1.934163094 | 6.044259667 |
| 32 | 2.239198945 | 6.997496705 |

The implication is limited but useful: an advantage over a duplicate-current probe under IID targets does not, on its own, identify predictive historical information. A cache can instead provide an alternative candidate; for this two-candidate assay, current–cache Hamming distance fully determines its expected IID advantage. A fresh candidate is therefore an informative budget-matched comparator.

This does not say which policy wins ORG-NOVELTY-045. Its actual algorithm also has an ordinary scout, local children, global selection, inherited state, rare loss and a finite horizon. Recurrent targets are not independent of history. Neither g(d), its average over visited states nor a matched unselected mean is a validated predictor of carrier-frequency or population-performance ranking. No extra predictor, endpoint, grouping of survivors or parameter has been added to the experiment.

Verification uses exact rational arithmetic. The direct formula is checked by exhaustive target enumeration for every distance in dimensions 1–10. The closed form is checked through distance 64. The fresh-candidate mixture and difference-distribution forms agree with exhaustive joint target/candidate enumeration in dimensions 1–7 and with each other at n=32. All finite identities passed; these checks are not Monte Carlo replication.

!Exact two-candidate IID-target gain; not a population ranking (original archive reference)
