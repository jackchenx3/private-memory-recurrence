# Study 061: certified stationary-policy result

Accepted 2026-09-25T02:58:07.074274+00:00. Job 53355927 completed in 14 seconds with one CPU and 4 GiB requested memory. The 136-file delivery is verified locally and on HPC. Twelve preproduction tests passed. The supervisor independently reconstructed all 32 prespecified rows (8,192 numerators), checked all four exact residual certificates, all 1,024 rounded weights, matrix symmetries/support and all 14 outcomes without another stationary solve.

The fixed primary ACTIVE_HALF_MINUS_ZERO / H is **+0.458222 percentage points**, with a strictly positive certified numerical enclosure. Recurrence therefore increases stationary use of the supplied H policy in this defined two-individual/one-bit model at the fixed switching probability 1/16. This conclusion concerns a small directional effect: active H frequency is 49.976079146% under ZERO and 50.434301623% under HALF.

The contrary results matter. Active H lies 0.023920854 points below the neutral 50% reference under ZERO; under HALF it lies 0.434301623 points above. Active population accuracy relative to the label-neutral probe control is **-0.259358 points under ZERO** and **+0.702715 points under HALF**. The latter are distinct population-accuracy comparisons, not founder transmission or evidence that greater H frequency alone mediates accuracy. Neutral H equals exactly one-half by policy-complement symmetry and uniqueness.

All four exact residuals are below 6.31e-59; each mean's certified numerical-error radius is below 2.38e-49 in fraction units. The primary difference has a radius below 4.58e-49. Exact rational centers/endpoints and outward decimal strings are retained in OUTCOMES.json. These are numerical enclosures, not 95% confidence intervals or sampling errors. Reporting six to nine decimal places above is display rounding, not the certification calculation.

| Quantity | Value | Unit | Certified sign |
|---|---:|---|---|
| ACTIVE_ZERO / H | 49.976079146 | percent | positive |
| ACTIVE_ZERO / U | 67.222586967 | percent | positive |
| ACTIVE_HALF / H | 50.434301623 | percent | positive |
| ACTIVE_HALF / U | 68.775118376 | percent | positive |
| NEUTRAL_ZERO / H | 50.000000000 | percent | positive |
| NEUTRAL_ZERO / U | 67.481944961 | percent | positive |
| NEUTRAL_HALF / H | 50.000000000 | percent | positive |
| NEUTRAL_HALF / U | 68.072403064 | percent | positive |
| ACTIVE_HALF_MINUS_ZERO / H | 0.458222476 | percentage points | positive |
| ACTIVE_ZERO_MINUS_HALF_SHARE / H | -0.023920854 | percentage points | negative |
| ACTIVE_HALF_MINUS_HALF_SHARE / H | 0.434301623 | percentage points | positive |
| ACTIVE_HALF_MINUS_ZERO / U | 1.552531409 | percentage points | positive |
| ACTIVE_MINUS_NEUTRAL_ZERO / U | -0.259357994 | percentage points | negative |
| ACTIVE_MINUS_NEUTRAL_HALF / U | 0.702715312 | percentage points | positive |

The mathematical guarantee follows from a positive two-step transition kernel. Two consecutive selections of ordered scout candidates can set any destination's caches, genotypes, policies and target pair. Every two-step entry is at least 1/966367641600, giving uniform minorization alpha=1/3774873600. For a normalized nonnegative rational approximation p=k/K, the exact residual r=||pP-p||1 implies total-variation error at most r/alpha. The independent checker reconstructed transitions and certificates from saved records; it imported no producer implementation.

This is a new mathematical model with two ordered one-bit individuals, supplied private caches and ongoing symmetric policy supply. Population size, genotype dimension, candidate rule and the exact rational selection model are explicitly defined; it is not an equilibrium analysis or independent training replication of the published 32-individual/32-bit simulator. It does not show memory origin, a biological switching rate, a general costly advantage or practical optimization usefulness. No new sampled population trajectories were generated. Earlier unresolved study 059 and 060 primaries remain unresolved.

## Scientific decision and next deliverable

Accept the fixed primary's positive sign and all adverse comparisons within the mathematical model. The result answers the new stationary-use question; it does not close the larger model's long-run question. A coherent, explicitly separated mathematical section and supplement in the existing private-memory paper is justified. A fifth standalone paper is not established by this small calculation. The next finite task is MANUSCRIPT-STATIONARY-061: integrate this result and its proof/certificate, preserving the existing empirical record and public versions. No new experiment, parameter grid or further cohort is assigned.

Source package: PRIVATE_WORKSPACE/you-are-responsible-for-implementing-the/outputs/stationary_policy_v1

HPC package: PRIVATE_HPC/organized-variation-transfer/experiments/stationary_policy_v1

Audit: AUDIT.json. Quoted values: QUOTED_STATISTICS.json. Source bindings: SOURCE_BINDINGS.json.
