# What a zero-cost advantage can imply about smaller positive costs

Prepared 22 September 2026 while ORG-COMPETE-051 is being assembled. This is a mathematical sensitivity result for an explicitly defined ideal extension, not a new population experiment or a change to the active assignment. No publication novelty is claimed.

The accepted experiments distinguish zero cost from a one-bit score penalty. Negative outcomes at the latter do not establish failure at every positive real cost. Conversely, a favorable finite-sample estimate at zero cost does not prove a useful positive-cost advantage. The theorem below separates these statements and supplies a conservative conditional bound.

## Ideal model and scope

Extend the probabilistic survivor rule to a real score cost c. At a fixed candidate pool, entry i has weight w_i(c)=a_i exp(−βc I_i), where a_i>0, β=ln2, and I_i is one for a cost-bearing carrier and zero for a resident. In the current score convention a_i=2^(−h_i). Historical and fresh carriers pay the same cost. Draw K ordered distinct entries by independent, continuous-uniform exponential clocks, equivalently successive draws proportional to the weights of the remaining entries. This is the sequential-weight interpretation of sampling without replacement, not a claim that marginal inclusion probability is K times normalized weight. The established sampling distinction is described in [Efraimidis, *Weighted Random Sampling over Data Streams*, Definition 3 and section 3.2](https://arxiv.org/html/1012.0256v2).

Across T updates, the initial state and exogenous target/proposal laws are independent of c. Given the same structural history and the same exogenous inputs, candidate generation, raw scoring, donor choice and cache updates are identical at both costs. Cost acts only through the survivor weights. This assumption matches the intended continuous-cost extension of the accepted abstract operators; the recorded implementation itself accepts only the two integer costs.

The trajectory here contains ordered genotypes, types, founders, caches, selected indices and raw measurements. It excludes the numerical cost field, cost-dependent penalized scores, survival uniforms and clock values. Cost-dependent fields can differ even when every selected individual is the same, and the maximal coupling below need not reuse survival uniforms. Expectations below concern the same bounded function of this structural trajectory at both costs. They do not automatically apply to a statistic whose formula itself changes with c, such as penalized accuracy.

## Bound

At any identical ordered selection prefix, let A be the total remaining carrier base weight and B the total remaining resident base weight. The probability that the next entry is a carrier is

`p(c) = A exp(−βc) / [B + A exp(−βc)]`.

If either group is empty, this probability is constant. Otherwise `p′(c)=−β p(c)[1−p(c)]`, so `|p′(c)|≤β/4`. Conditional on which group is drawn, the item distribution within that group does not depend on c. Consequently the total variation distance between the two next-item distributions is exactly `|p(c)−p(d)|`, bounded by `β|c−d|/4`. Total variation uses the convention one half of the sum of absolute probability differences.

Couple the next draws maximally while their ordered prefixes agree. A union bound over K draws gives a mismatch probability at most `min{1, Kβ|c−d|/4}` for the ordered survivor lists. Keeping their order matters because later proposal arrays are indexed by population position. This is an existence-of-coupling argument; it does not assert that reusing the same saved clock uniforms realizes that optimal coupling.

Couple exogenous inputs identically and repeat this argument at each update while the structural histories agree. The per-update bound is uniform over their possible common histories. Therefore, writing P_c for the structural trajectory law,

`TV(P_c, P_d) ≤ min{1, TKβ|c−d|/4}`.

For any common bounded trajectory statistic g whose range has length R,

`|E_c[g] − E_d[g]| ≤ R min{1, L|c−d|}`, where `L = TK ln2 / 4`.

With T=40 and K=32, `L=320 ln2≈221.807098`. Endpoint carrier frequency, its change from a fixed initial frequency, and raw terminal or horizon-average accuracy have R=1. A within-population historical-minus-fresh endpoint contrast has R=2; subtraction of its fixed initial contrast leaves that range length unchanged. A difference of expected carrier changes from two separate introductions obeys the bound `2 min{1,L|c−d|}` by applying the one-arm inequality twice, regardless of how the two arms are paired.

Thus, **if the true ideal-model expectation G(0)=a is strictly positive**, the corresponding expectation stays positive for `0<c<a/(R L)`, using R=2 for either historical-minus-fresh contrast just described. This is conditional on a positive true expectation; substituting an observed mean or a pointwise bootstrap lower endpoint does not turn it into an unconditional theorem about the experiment. The bound is deliberately loose and supplies no scientifically meaningful cost scale. It is neither a predicted failure threshold nor an instruction to search for a sufficiently tiny favorable cost.

## Why the recorded implementation needs a separate bridge

The accepted RACE32 implementation draws 52-bit words and converts them to a finite grid of uniforms, then evaluates clocks in floating point. The continuous-clock proof does not establish the same continuity result for that discrete law. On a finite grid, cross-group clock ties can have positive probability, and infinitesimal changes of cost can resolve them differently. Even an ideal exact-arithmetic finite-grid expectation can therefore have jumps. With two equally weighted entries, one selected, and deterministic carrier-first tie breaking, the carrier-selection probability drops by 1/M immediately to the right of cost zero when both uniforms are independently drawn from the same M-point grid. The equal-word events account for the entire jump. This example is a logical boundary, not an estimate of the implementation error in the 128-entry assay.

A fixed saved stream can also produce a stepwise cost response. Continuity of an ideal expectation never implies smoothness or a particular sign on each realized trajectory. Bridging the theorem to the actual finite-grid, floating-point implementation would require an additional approximation or quantization bound. No such bound is supplied here, and no recorded population outcome is changed.

## Scientific decision

The tested one-bit negative result remains intact. The evidence has not exhausted every real positive cost; the ideal-model calculation explains why that larger conclusion would be unwarranted. It does not establish that any untested cost produces a consequential advantage, nor that memory covers a calibrated biological expense. Independent preparation and direct-competition evidence remain separate questions. No cost variant is assigned by this note.

The accompanying check uses exact rational arithmetic for the group-mixture identity, derivative bounds and complete ordered-sampling probability vectors for four abstract entries. A finite-grid counting example checks the continuity caveat. It generates no random numbers, objective evaluations or propagated population paths. Those finite checks validate the algebra at their stated cases; the general justification is the explicit coupling proof above.
