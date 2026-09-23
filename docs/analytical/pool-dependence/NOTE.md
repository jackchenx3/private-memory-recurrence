# Matching each probe distance does not fix selection from the whole pool

Exact mathematical note, 2026-09-22. No random input or population trajectory is generated. This explains a limit of a possible distance-matched control; it does not change ORG-RESIDENT-047 or report a new population result.

For fixed n-bit candidates x and y, distance d=H(x,y), and a uniform target T independent of both, each unselected expected mismatch is n/2 and

`Cov(H(x,T), H(y,T)) = (n−2d)/4`.

Each agreeing bit contributes +1/4 to the covariance, each differing bit contributes −1/4, and independent target bits have zero cross-position covariance. The same per-pair distance also fixes the expected gain from choosing the better of x and y, as shown in the earlier two-candidate identity. These facts do not fix the joint relationships among all candidates in a population pool.

A complete two-bit counterexample uses two current candidates 00,00 and two probes. In pool A the probes are 01,01; in pool B they are 01,10. Each probe is exactly one bit from its corresponding parent in both pools. Four additional fixed candidates are identical in both pools: 00,00,00,01. Both pools therefore contain eight candidates, and the selector retains the two with the smallest mismatch. Targets are uniformly sampled from the four two-bit strings, independently of the entire fixed pool.

| Target | Mean mismatch of two selected candidates, A | Mean mismatch, B |
|---|---:|---:|
| 00 | 0 | 0 |
| 01 | 0 | 0 |
| 10 | 1 | 1/2 |
| 11 | 1 | 1 |
| Exact target average | 1/2 | 3/8 |

Every unselected candidate has expected mismatch one. Each parent–probe pair has the same distance, covariance and expected best-of-two gain. Nevertheless the expected selected-pool mean differs by 1/8 mismatch bit. The changed relationships among probes and the fixed background affect global selection, without any predictive information about the target.

Consequently, randomizing the placement of a historical probe while preserving its distance from its current parent is an informative restriction of historical information, but it does not preserve the full candidate pool's dependence structure. A nonzero population effect under IID would not contradict the local two-candidate identity. Such a future control would also retain history through its distance, and later states/caches could diverge. Its full-path effect would not be a unique percentage mediated by historical direction.

This counterexample is a fixed candidate-pool assay. It does not implement the research model's target-dependent donor/local-child generation, inherited types, cache updates or finite-horizon propagation. It is not evidence of a carrier advantage and does not predict the sign of a future experiment. The accompanying exact rational check verifies the covariance and local-gain identities for all distances in dimensions one through eight and enumerates every target in the counterexample; no Monte Carlo or new population study is involved. No novelty claim is made for these elementary identities.
