# ORG-AVAILABILITY-063 — continuity of supplied historical-policy availability

Revision 1. Supervisor-owned deterministic analysis under continuing research authorization. Definitions and output catalog are frozen before inspecting new event probabilities or durations. This follows the completed PUB-FLOW-062-NOTE; one assignment only. No executor message or scheduler job is needed.

## Scientific decision and scope

Does recurrence lengthen uninterrupted availability of at least one historical-policy individual, beyond its effect in label-neutral controls? The sole primary is `RECURRENCE_BY_EXPRESSION|PRESENT_SPELL`, the active HALF-minus-ZERO difference in mean H-present spell length minus the corresponding neutral difference. The working directional prediction is positive, but adverse, exact-zero and numerically uncertified outcomes must be retained.

This question is distinct from the accepted mean H frequency. A mean can increase while H-present spells become shorter. It is also distinct from persistence of a founder lineage, a specific cache, memory content, useful population accuracy, or spontaneous memory origin. Analyze only the separate two-individual, one-bit supplied-policy model at the existing switching probability 1/16. No extrapolation to stationarity of the larger model or practical importance is authorized. This is a new post hoc estimand of saved mathematical objects, not independent confirmation or empirical replication.

## Fixed inputs and state sets

Authenticate the following against the v1.5.0 manifest at commit `651c4289b1ac34efb30d1a81560e88cd74b1609f`: all four `results/061/matrices/{ACTIVE_ZERO,ACTIVE_HALF,NEUTRAL_ZERO,NEUTRAL_HALF}.json.gz`, their four `vectors` files, and `provenance/061_CERTIFICATES_CHECK.json`. Record exact hashes, frozen task hash and prospective-fixture receipt hash. Do not import the scientific kernel generator or stationary solver. The original source and accepted certificate are definitions and evidence, not code to rerun.

Use the published encoding `g0 + 2*c0 + 4*h0 + 8*g1 + 16*c1 + 32*h1 + 64*a + 128*b`. Let B be the 64 states with both policy bits zero: `(s & 36) == 0`. Let A be the other 192 states. A means at least one H label immediately after the update's policy switching.

A present spell is a maximal consecutive run of end-of-update states in A. Sample spells at their B-to-A entries in the stationary process and count the entering A state as duration one. Do not substitute a forward residual lifetime from an arbitrary stationary A observation, a maximum spell, a quantile, or a founder survival time. No sampled paths or convenient burn-in are needed.

## Exact identities and certification

Every candidate inherits an F label when the starting state is in B. The two independent post-selection switches then give the common B-to-A probability `alpha = 1-(15/16)^2 = 31/256`. Verify this by summing the saved integer row entries into A for all 64 B states in each of the four kernels: 256 exact row sums. This reads saved entries; it does not regenerate scientific transition rows. A mismatch is a concrete discrepancy and stops this analysis without choosing another state set.

The B sojourn has a constant departure hazard alpha, so its mean is exactly `1/alpha = 256/31` updates in all four kernels. This is an exact derived identity, not four additional measured outcomes. For the true stationary probability `b = pi(B)`, the B-to-A entry flux is `J = alpha*b`. Finite-chain ergodicity gives the asymptotic number of A observations per update as `1-b` and the number of A-spell entries per update as J. Their ratio is the entry-sampled mean present-spell duration:

`L = (1-b)/(alpha*b)`.

This does not assume independent spells or a geometric A duration. The accepted irreducibility ensures positive flux and finite mean duration. Do not solve an additional hitting-time system.

From each saved integer vector k and K=sum(k), calculate the rational center `bhat = sum_B k/K`. Reuse the accepted total-variation bound E. Set `blo=max(0,bhat-E)` and `bhi=min(1,bhat+E)`. The b record has center bhat and enclosure [blo,bhi]. If `0 < blo <= bhi < 1`, monotonicity gives L center `f(bhat)`, lower `f(bhi)` and upper `f(blo)`, where f(b)=(1-b)/(alpha*b). Do not force symmetric radii. If those strict bounds fail, retain an uncertified duration with the appropriate unbounded enclosure and report the limitation; no extra precision or second solve.

Retain rounded-vector nonstationarity explicitly. Compute the exact center entry flux `Fin=alpha*bhat`, the center exit flux `Fout=sum_{s in A} phat(s)*P(s,B)`, and residual projection `rA=sum_s phat(s)*P(s,A)-(1-bhat)`. Verify `Fin-Fout=rA` exactly. Save all three fractions and whether the residual is zero. They are certificate diagnostics, not extra headline outcome records. The formula for L uses the true stationary identity with a certified b enclosure; it must not falsely assert exact flux balance for rounded weights.

Use Fraction/integer arithmetic for centers, enclosures and identities. Decimal display uses fixed 80 significant digits with outward rounding. Display b as both a fraction and percentage, and L in updates. Contrast lower bounds subtract upper bounds for negative terms; upper bounds subtract lower bounds. A strictly positive lower endpoint certifies a positive sign; a strictly negative upper certifies a negative sign. Exact zero requires both endpoints exactly zero; an enclosure containing zero otherwise means uncertified. These are numerical enclosures, never confidence intervals. There is no new practical-effect benchmark.

## Exactly 13 mathematical outcome records

For each kernel, save two primitive records:

1. `kernel|ABSENT_MASS` — b, the stationary probability of no H.
2. `kernel|PRESENT_SPELL` — L, the entry-sampled mean uninterrupted H-present duration.

These are eight records. Five duration contrasts complete the catalog:

9. `ACTIVE_HALF_MINUS_ZERO|PRESENT_SPELL`.
10. `NEUTRAL_HALF_MINUS_ZERO|PRESENT_SPELL`.
11. `ACTIVE_MINUS_NEUTRAL_ZERO|PRESENT_SPELL`.
12. `ACTIVE_MINUS_NEUTRAL_HALF|PRESENT_SPELL`.
13. **Primary:** `RECURRENCE_BY_EXPRESSION|PRESENT_SPELL` = record 9 minus record 10 = record 12 minus record 11.

Do not select another primary after inspecting outcomes. Report all 13 records. A positive interaction alone does not establish a positive absolute active recurrence effect; interpret its components separately. Preserve previous adverse population accuracy and unresolved 059/060 primaries. This does not change the 14 release mathematical quantities, 15,284 statistical estimates, or six separately published 062 quantities.

## Prospective fixture and bounded execution

Before reading new production values, check constructed three-state chains representing H counts 0/1/2, with fixed absence departure alpha, common present-to-absence probability beta, and a fixed mixture between states 1 and 2. Their stationary weights are analytic, so no stationary solve is needed. Cover exact flux identities, geometric absence and present durations, interval propagation for fixed rational perturbations, both contrast identities, outward rounding/sign handling, and a constructed increase in mean H accompanied by decreased present-spell length. The fixture must read no study-061 matrix/vector or new quantity. Save its genuine receipt before production.

One local analysis, one CPU, two minutes, at most 8 MiB of new files under `outputs/policy-availability063/`. No new production kernel, stationary solve, sampled path, random seed, switching-rate grid, precision escalation or horizon extension. Use a new output directory and durable receipts to avoid accidental repeat execution. Invalid input or identities yield a preserved failure, not a desired-sign variant.

Save authentic analysis source, 13 records, exact flux diagnostics, source bindings, frozen specification, fixture receipt, elapsed/resource record and one focused result note. Check all 13 records with a separately written integer-sum implementation that does not import the producer. Recompute the 256 B-to-A row sums, all four event masses/duration enclosures and residual flux identities from saved input bytes. Validate sign and outward display. Do not rerun the original 061 raw audit, kernel generator or stationary solver, or expand to new observables merely because the result is small or adverse.

Archive accepted code/results/receipts on HPC and update owned coordination. Decide once whether these quantities add enough interpretation for a compact manuscript/supplement or companion-note addition; do not automatically issue another DOI, publish a new paper, or launch another numerical variant. Keep all original handoffs and public versions unchanged.
