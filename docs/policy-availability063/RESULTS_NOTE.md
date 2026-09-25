# Study 063: uninterrupted availability of a supplied historical policy

25 September 2026. New post hoc mathematical estimands from the accepted study-061 kernels and certified stationary vectors. The question, 13-record catalog and checks were frozen before these quantities were inspected.

## Finding

The fixed primary recurrence-by-expression interaction in mean H-present spell length is **+0.244546296 updates**, with a strictly positive numerical enclosure. Under active retrieval, recurrence increases mean uninterrupted H presence from **12.577444923 to 12.822684302 updates**. The corresponding neutral-label change is also positive but much smaller. Thus the higher average H frequency in this model is accompanied by somewhat longer uninterrupted H availability, beyond the environmental change seen in neutral controls.

The result is small. Active retrieval slightly **shortens** H-present spells relative to its neutral control under ZERO, while lengthening them under HALF. Absence remains frequent: H is completely absent in approximately 39% of stationary observations under all four kernels. These are model-specific numerical quantities, not empirical replications or a claim of practical usefulness.

## All 13 outcomes

Each kernel contributes two primitive quantities: stationary H-absent probability and mean H-present spell length. Present spells are sampled at their stationary entries, not at arbitrary observation times.

| Kernel | Stationary H-absent probability | Mean H-present spell (updates) |
|---|---:|---:|
| ACTIVE_ZERO | 39.634569724% | 12.577444923 |
| ACTIVE_HALF | 39.173487561% | 12.822684302 |
| NEUTRAL_ZERO | 39.611988176% | 12.589322592 |
| NEUTRAL_HALF | 39.610671298% | 12.590015674 |

The remaining five quantities are duration contrasts:

| Contrast | Updates | Certified sign |
|---|---:|---|
| Active HALF minus ZERO | 0.245239379 | positive |
| Neutral HALF minus ZERO | 0.000693083 | positive |
| Active minus neutral under ZERO | -0.011877669 | negative |
| Active minus neutral under HALF | 0.232668628 | positive |
| Recurrence-by-expression interaction (primary) | 0.244546296 | positive |

All displayed centers are rounded independently. The saved exact fractions and asymmetric, outward-rounded enclosures are in OUTCOMES.json. The primary lies inside the conservative decimal interval **[0.244546296412, 0.244546296413] updates**; its stored enclosure is substantially narrower. These are certified **numerical enclosures, not confidence intervals**. A positive interaction alone would not establish a positive active HALF-minus-ZERO contrast; here that separate contrast is also certified positive. No new practical-effect threshold is introduced.

## Why these are spell lengths

Let B be states with both policy labels F and A its complement. The two independent post-selection switches occur with probability 1/16 each. Starting in B, every candidate's inherited policy is F before switching, so the probability of entering A is exactly alpha = 1 − (15/16)^2 = 31/256 under every kernel. All 256 relevant saved row sums confirm this identity.

Consequently, absence spells have a geometric duration with mean **256/31 updates**, identical across the four kernels. This is an exact identity, not four new observations. If b is the stationary B probability, the stationary entry flux into A is alpha*b. The ratio of stationary time in A to the number of A entries gives the mean duration sampled at those entries:

`L = (1-b)/(alpha*b)`.

This uses finite-chain occupation and transition frequencies. It does not assume independent present spells or geometric present durations, and does not equal the forward residual lifetime observed at an arbitrary time in A.

The accepted total-variation bound E gives an enclosure for b. Because L decreases strictly with b, evaluating the ratio at the reversed interval endpoints gives its numerical enclosure. The rounded stationary vectors have **nonzero** entry-minus-exit flux residuals in all four kernels, ranging in magnitude from about 3.52e-61 to 2.28e-60 per update. FLUX_CERTIFICATES.json retains each exact fraction and the identity `Fin − Fout = rA`. No rounded vector is silently treated as exactly stationary.

## Verification and scientific limits

A separately written integer-sum implementation verified all 13 quantities, enclosure endpoints and signs, the 256 saved B-to-A row sums, and all four exact flux corrections: **697 exact checks passed**. It imported neither the producer nor the scientific operator. This is a second implementation by the supervisor, not an external independent reviewer. The prospective 144-check constructed fixture included a case with higher average H frequency but shorter uninterrupted availability, establishing why the new estimand was not settled by the old mean-frequency result.

Analysis and audit used **0.267 seconds** of measured local elapsed time. No transition row was generated, stationary or hitting-time system solved, population trajectory simulated, or random seed drawn. The 13 new quantities are separate from the release's 14 mathematical quantities, 15,284 statistical estimates and study 062's six derived quantities.

H availability does **not** mean that a founder lineage, cache content or memory representation persisted. A newly supplied H label can restore availability after total loss, with different ancestry. The model still has only two individuals and one bit, supplied storage and continuing policy switching. It establishes neither the larger model's stationary behavior nor spontaneous memory origin, costly maintenance, useful population performance or a biological mechanism. Previously adverse ZERO population accuracy and unresolved study-059/060 primaries remain unchanged. The neutral comparison is a defined operator contrast, not unique causal mediation.

## Integration decision

This adds a distinct interpretation of maintenance: small increased mean use is accompanied by modestly longer episodes of availability, while total absence remains common and reappearance is imposed by switching. Publish it as one compact companion-note addition with exact records, executed code and reproducible commands, linked to the existing stationary-flow note. It does not justify another paper, full PDF revision or DOI version. Preserve the adverse ZERO comparison, the small scale, shared-input dependence and all previous publications. No next numerical variant is assigned by this result.
