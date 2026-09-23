# A finite-grid bound for ordered survival

Prepared 22 September 2026. This is an exact-arithmetic mathematical result, with no new population experiment or claim of publication novelty. It addresses the random-number discretization gap identified in the earlier [cost-sensitivity note](../cost-sensitivity/NOTE.md). It does not certify the complete floating-point implementation.

## Statement and assumptions

For an integer M≥1, divide (0,1) into M equal cells. In cell k choose a representative q_k satisfying k/M≤q_k≤(k+1)/M, with every representative strictly between zero and one. In particular, q_k=(k+1)/(M+1) is admissible. Couple a continuous uniform U with its grid value q(U)=q_floor(MU). Independent uniforms then induce independent, equiprobable grid words.

For n candidates with arbitrary positive weights w_i, form continuous clocks C_i=−log(U_i)/w_i and exact-real-arithmetic grid clocks C_i^M=−log(q(U_i))/w_i. Rank the clocks from smallest to largest. Any grid ties use a fixed priority order, or an external priority order conditioned on independently of the hidden continuous uniforms. Both models use the same priority order. The bound is uniform over the weights; it does not assume nearly equal weights.

Under this coupling, the probability that the complete ordered candidate rankings disagree is at most

`min{1, n(n−1)/M}`.

Consequently, the same bound applies to any selected ordered prefix, including the first 32 of 128 candidates. Preserving order is necessary when future inputs are indexed by population position.

## Pairwise proof

For a pair i,j, let h(v)=v^(w_i/w_j). The continuous comparison C_i<C_j is equivalent to U_i>h(U_j). The function h is increasing, with h(0)=0 and h(1)=1.

First compare U_i>h(q(U_j)) with q(U_i)>h(q(U_j)), allowing the latter comparison to include equality when i wins a grid tie. Conditional on q(U_j), the threshold is fixed. Since q is nondecreasing and its representative remains inside each cell, replacing U_i by q(U_i) shifts the threshold cut by at most one cell width. This is true for either strict or weak grid comparison, including a threshold equal to a cell endpoint. The disagreement probability is therefore at most 1/M. Equality for the continuous U_i has probability zero.

Next compare U_i>h(U_j) with U_i>h(q(U_j)). Independence and uniformity of U_i make their disagreement probability E|h(U_j)−h(q(U_j))|. On cell k the absolute difference is bounded by h((k+1)/M)−h(k/M). Integrating over the cell and summing gives

`E|h(U)−h(q(U))| ≤ (1/M) Σ_k [h((k+1)/M)−h(k/M)] = 1/M`.

The two bounds imply at most 2/M disagreement for one pair. If two complete ordered rankings differ, at least one pair is ordered differently. A union bound over n(n−1)/2 pairs proves the stated n(n−1)/M bound. Independence between pair-disagreement events is unnecessary.

## Adaptive populations

Couple the two population processes with the same initial state and the same non-survival inputs. At each update, while their structural histories agree, candidate generation and weights agree. Use fresh independent continuous uniforms to couple the two survivor rules as above. The per-update bound holds conditional on every such common history. The probability of the first differing survivor list in at most T updates is therefore bounded by

`epsilon = min{1, T n(n−1)/M}`.

This gives total variation distance at most epsilon between the structural trajectory laws. The structural trajectory includes selected indices, ordered genotypes, policies, founders, caches and raw measurements. It excludes the uniforms and clock values: those numerical fields differ even when survivor identities agree. The statement also requires a common non-survival input law, or a common conditional input law while histories agree.

For n=128, T=40 and M=2^52, the per-update bound is 127/35184372088832 ≈ 3.609557097661309×10^−12. The trajectory bound is

`epsilon = 635/4398046511104 ≈ 1.4438228390645236×10^−10`.

For the same bounded structural statistic g with range length R, the grid and continuous expectations differ by at most R epsilon. This is a distributional bound under the stated ideal random-input assumptions, not a guarantee that every fixed saved stream gives the same trajectory.

## What this adds to the cost argument

Let P_c be the ideal continuous-clock structural law at real score cost c, and Q_c its exact-arithmetic grid counterpart. The earlier note proves TV(P_c,P_d)≤min{1,L|c−d|}, with L=TK ln2/4=320 ln2 for T=40 and K=32, when cost multiplies all cost-bearing weights by 2^(−c) and leaves candidate generation unchanged. Combining the two endpoint approximation bounds with that result gives

`TV(Q_c,Q_d) ≤ min{1, 2 epsilon + L|c−d|}`.

This is an error-floor bound, not continuity of the grid law. Positive-probability grid ties can still create jumps; the earlier two-entry jump of 1/M is consistent with this inequality.

Conditionally, if the true exact-grid expectation a=E_Q0[g] satisfies a>2R epsilon, then E_Qc[g]>0 for

`0<c<(a/R−2 epsilon)/L`.

This conclusion assumes the same statistic at both costs and a genuinely known positive expectation. A sampled mean or approximate bootstrap lower endpoint cannot simply be substituted as a proven a. Within-population historical-minus-fresh frequency has R=2; an individual frequency or change from a fixed starting frequency has R=1. Differences of expectations from separate populations require applying the one-population bound to each arm. No meaningful cost threshold or new positive-cost empirical result follows here.

## Remaining implementation boundary and checks

The accepted implementation uses finite random words, floating-point division, a library logarithm and floating-point clock arithmetic. The theorem covers exact clock arithmetic for in-cell representatives. It does not certify numerical logarithm error, rounding effects on weighted ordering, or that a deterministic pseudorandom generator supplies ideal independent words. Actual source and generator assumptions need a further numerical-kernel analysis before this bound can be claimed for the full program. The source comparison is documented in PROVENANCE.json.

The accompanying checker passed 12,982 exact rational checks. It tests the threshold-cut and integral inequalities for M=1,…,24, four representative rules and monotone powers 1,…,8, and verifies the stated numerical constants. Endpoint representative rules are used only to check the component inequalities; the clock theorem above requires representatives strictly inside (0,1). Finite checks support the algebra but do not replace the general monotonicity proof. No random draws, objective evaluations or population paths were generated.

The scientific decision is unchanged: the tested one-bit costly failures remain valid, and universal failure at every positive cost has not been established. This note closes the exact-arithmetic quantization part of the ideal-model comparison, while leaving machine arithmetic and generator assumptions explicit. It authorizes no cost sweep or extra experiment.
