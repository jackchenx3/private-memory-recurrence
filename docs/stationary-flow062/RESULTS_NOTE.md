# Study062: immediate target-law and stationary-state contributions

Completed25September2026. Post hoc mathematical accounting of the accepted061total; component definitions were frozen before their values were inspected.

## Finding

The fixed primary immediate target-law component is **+0.429556589 percentage points**, with a strictly positive certified numerical enclosure. The state-occupancy component is also positive, **+0.028665888 points**. Their exact rational sum is **+0.458222476 points**, recovering the small stationary H-frequency recurrence effect from study061 after retaining the rounded-vector residual correction.

| Fixed quantity | Center | Unit | Certified sign |
|---|---:|---|---|
| ZERO pre-switch selection drift | -0.003417265 | H-frequency percentage points per update | Negative |
| HALF pre-switch selection drift | +0.062043089 | H-frequency percentage points per update | Positive |
| HALF minus ZERO selection drift | +0.065460354 | H-frequency percentage points per update | Positive |
| Direct target-law component (primary) | +0.429556589 | Stationary H-frequency percentage points | Positive |
| State-occupancy component | +0.028665888 | Stationary H-frequency percentage points | Positive |
| Total | +0.458222476 | Stationary H-frequency percentage points | Positive |

Displayed values are rounded individually. The saved exact rational values satisfy the identities exactly. The primary and occupancy numerical-error radii are each below1.042e-49 in fraction units (1.042e-47percentage points); these are numerical enclosures, not confidence intervals. No new practical-importance threshold or independent-replication claim is introduced.

## What this changes

At the defined common averaged stationary-state distribution, changing the next-target law contributes positively to historical-policy selection. The positive total therefore does not arise solely from different frequencies of population states. Redistribution of stationary states makes an additional positive contribution under this same decomposition. The two displayed component magnitudes can be compared within this specified convention; they are not uniquely identified causal mediation shares.

The result is conditional on the separate two-individual, one-bit model, supplied private caches and ongoing symmetric policy switching at1/16. It does not extend the result to stationary behavior of the32-individual model or spontaneous memory origin. This task did not analyze population accuracy. The previously reported adverse ZERO active-minus-neutral accuracy and unresolved059/060primaries remain unchanged.

## Definitions and certification

For H frequency h(s), policy-flip probability mu=1/16 and beta=7/8, define exact conditional pre-switch drift as d_q(s)=((P_q h)(s)-mu)/beta-h(s). At true stationarity, pi_q h-1/2=7pi_q d_q. With bar_pi=(pi_HALF+pi_ZERO)/2 and bar_d=(d_HALF+d_ZERO)/2, the components are C=7bar_pi(d_HALF-d_ZERO) and O=7(pi_HALF-pi_ZERO)bar_d.

All arithmetic uses the already published integer transition matrices and normalized saved integer stationary weights. Accepted total-variation error bounds propagate through exact reward spans. The exact correction between the computed decomposition total and the saved061H-frequency center is 4.7138026903651903651903651903651903651903651903651903651903670006385975135975136E-60 in fraction units. It is nonzero and preserved: T-deltaH=8(r_HALF-r_ZERO), where r_q=pihat_q(P_q h-h). The new total enclosure overlaps the accepted061enclosure. A tiny numerical residual is not silently substituted for zero.

A separately written integer-weighted direct-sum check reproduced all six centers, error radii, signs, decimal bounds and256derived state records, passing2,619exact checks. It imported neither the producer nor scientific operator code. This was a second implementation by the supervisor, not an external independent reviewer. The previously frozen72-check two-state algebra fixture and three sign/display fixtures support the new calculation. No transition row was reconstructed, no stationary system solved, and no population path generated. Analysis and audit together took0.871seconds of measured local elapsed time.

## Integration decision

Publish a compact, reproducible technical note alongside the existing paper. This newly specified accounting answers the immediate-versus-occupancy question, but does not add an independent cohort, change the total effect or justify another full manuscript/DOI version on its own. Preserve v1.5.0 and all earlier versions. The technical note should expose the six quantities, exact identities, source bindings and the256-state term table, with the post hoc and attribution-convention limits explicit. No new numerical variant is assigned.

The execution receipt field named started_at_utc was recorded when output writing completed; it is an end-of-calculation timestamp. Its monotonic elapsed_seconds is the measured runtime. This metadata-label issue changes no input, quantity, certificate or decision and the original receipt is retained.
