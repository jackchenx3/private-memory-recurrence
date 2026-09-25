# ORG-STATIONARY-061 — stationary use of supplied memory under ongoing policy switching

Revision 1. Sole scientific execution assignment under continuing user authorization. Acknowledge the ID, revision and SHA-256 before implementation. No production kernel, stationary vector or contrast was evaluated to choose this design. Preserve previous studies, handoffs and public releases.

## Question, prediction and scope

Does recurrence increase stationary use of an already available historical policy when symmetric switching lets absent alternatives return? The directional working prediction is a positive active HALF-minus-ZERO stationary H fraction. Negative, zero or numerically unresolved results are retained. Stationary true population accuracy is a separate outcome.

This is a new, minimal mathematical model, not an equilibrium analysis or independent replication of the published32-individual/32-bit model. Storage and H/F alternatives are imposed. No claim of spontaneous memory origin, biological mutation rates, a general costly advantage or practical optimizer usefulness follows. The stationary calculation has no sampled population paths, random seeds, burn-in, bootstrap or empirical confidence interval.

## Complete state and event order

Each of two ordered individuals has genotype g, private cache c and policy h, all bits; h=1 means H, h=0 means F. Let a,b be the two latest targets, with b the target used in the current state's population evaluation. Encode

`id = g0 + 2*c0 + 4*h0 + 8*g1 + 16*c1 + 32*h1 + 64*a + 128*b`.

Enumerate all256states in increasing ID. This is the state immediately after selection and policy switching at the end of an update. Caches carry no score, timestamp or founder identity; none enters the following operations. In the accepted source, retrieval reads cache genotype only; here the complete reduced state is defined directly. Do not import the32-bit simulator as the mathematical kernel.

1. Draw next target e. For q=0, each bit has probability1/2. For q=1/2, e=a has probability3/4 and e≠a has probability1/4. Advance the target pair to (b,e) only when writing the new state.
2. Independently draw two fair fresh-probe bits u0,u1, two fair scout bits s0,s1 and two local-flip bits v0,v1 with P(v=1)=1/4. Draw all variables even if a probe bit is unused. In ACTIVE, probe i is c_i for H and u_i for F. In NEUTRAL, every probe is u_i regardless of h; labels/cache rules are otherwise identical.
3. For each recipient i, choose the genotype with lowest mismatch to e among its current genotype, probe and scout. On a one-bit objective all tied minimum-score genotypes are equal, so tie order cannot alter the chosen genotype. The local child is that genotype XOR v_i. Its policy and new cache come from recipient i, never from a donor/source label. Donor source identity has no further role.
4. The eight separately charged candidate slots are ordered `[parent0,parent1,probe0,probe1,scout0,scout1,child0,child1]`. A parent candidate has record (g_i,c_i,h_i). Every nonparent candidate has its proposed genotype, cache g_i from the recipient's pre-update state, and policy h_i. Keep duplicate slots. There is no policy scoring cost and no extra diagnostic objective call; the model's budget is eight charged candidate slots per update.
5. Candidate j gets integer weight w_j=2 when its genotype equals e and1 otherwise. Select an ordered pair (j,k), j≠k, with probability `w_j*w_k / (W*(W-w_j))`, W=sum(w). This is sequential weighted sampling without replacement. Survivor order defines new physical order. It specifies an exact rational model; it does not assert floating exponential-race identity.
6. Independently flip each selected survivor's policy with probability1/16. This applies to retained-parent and nonparent survivors alike. Genotype/cache are unchanged by the flip. Write both survivor records and target pair (b,e). Thus switching is ongoing symmetric policy supply, not merely one rare initial introduction.

Four kernels only: ACTIVE_ZERO, ACTIVE_HALF, NEUTRAL_ZERO, NEUTRAL_HALF. The first two use ACTIVE probes at q=0,1/2; the other two use NEUTRAL probes at those laws. Do not change population size, bit count, costs, local-flip rate, switching rate, recurrence levels or candidate families.

## Exact transition representation and fixed counts

Each kernel is256×256 with rows from states and columns to states. Every row must be nonnegative and sum exactly to one. Store integer numerator matrix A and a shared denominator

`L = lcm(W*(W-w): W=8..16, w in {1,2}) = 1441440`

`D = 4*16*16*256*L = 377864847360`, so `P=A/D`.

For an exhaustive branch, use target numerator2 for either target under ZERO, or3/1 under HALF, over denominator4. The joint fair probe/scout probability is1/16; the two local flips have numerator9,3,3,1 over16; the two policy flips have numerator225,15,15,1 over256. Multiply these numerators by `w_j*w_k*L/(W*(W-w_j))`. Accumulate the resulting exact integer in A. This includes unused fresh-probe branches under H. Equivalent exact caching/aggregation is allowed only with a documented identity and exhaustive constructed-fixture agreement; no approximate kernel construction or state truncation.

The literal branch count is2targets×4probe pairs×4scout pairs×4local-flip pairs×56ordered selections×4policy-flip pairs =28,672per row;7,340,032per kernel;29,360,128across four kernels. There are262,144stored transition numerators and1,024stationary probability entries. D is39bits; row accumulations fit signed64-bit integers, but stationary residual arithmetic uses arbitrary-precision integers. Never square the integer matrices using64-bit arithmetic.

## Uniqueness and an explicit numerical-error certificate

For any starting state and desired final state, construct two updates: select scout0 then scout1 at both updates; use first-update scout genotypes equal to the desired final caches, and second-update scouts equal to desired final genotypes. Choose the two successive targets equal to the desired final (a,b). First-update policy flips can set both policies F; second-update flips set the desired final policies.

At each update, specified scout bits have probability1/4, the specified target has probability at least1/4, the ordered scout selections have probability at least1/(16×15), and specified policy outcomes have probability at least1/256. Other proposal draws are unrestricted. Thus every entry of P² is at least

`b0 = (1/983040)^2 = 1/966367641600`.

All four kernels are therefore irreducible and aperiodic, with one stationary distribution. The uniform two-step minorization is `alpha=256*b0=1/3774873600`. Check the produced support graph for one strongly connected class and aperiodicity. A contradiction with this constructive argument is a technical discrepancy, not grounds to change the model or choose another recurrent class.

Solve the stationary equations using fixed80-decimal-digit arithmetic (standard-library Decimal or an explicitly pinned equivalent), with deterministic pivoting and sum-to-one normalization. The stationary solver is an approximation; certify its result against the exact integer kernel as follows. Round each computed component to the nearest multiple of10^-60, ties-to-even, giving integer k_i. Reject negative components or zero total K=sum(k); do not clip negatives. Set p_i=k_i/K. Save all k_i and K, and the exact residual numerator

`R = sum_j abs(sum_i k_i*A[i,j] - k_j*D)`.

Then `r=R/(K*D)` is the exact L1 stationary residual, and total variation from the true stationary distribution is bounded by `E=min(1,r/alpha)`. This follows from two-step contraction and `||pP²-p||1 ≤ 2r`. For any reward in[0,1], its expectation error is at most E. Require `r≤10^-30` as the fixed numerical-certification criterion. Use only the fixed80/60-digit calculation; do not increase precision in response to a contrast's sign. Preserve failure if the criterion is not met. Do not report a floating residual alone as certified stationary accuracy.

The NEUTRAL kernels are invariant under complementing both policy bits. Uniqueness implies stationary H fraction exactly1/2. Verify label-complement symmetry exactly for every neutral kernel entry and ensure the certified H interval includes1/2. Independently check global bit complementation of genotype/cache/targets (policies unchanged) for all four matrices. These are implementation checks, not additional empirical findings. Do not force the solver output to satisfy either symmetry.

## Fixed14-record outcome catalog

For each kernel report exactly two stationary means:

* `kernel|H`: expectation of `(h0+h1)/2`.
* `kernel|U`: expectation of `1-((g0 XOR b)+(g1 XOR b))/2`, the actual current population accuracy against its current target.

These are eight primitive records. Their centers are computed exactly from k/K and the half-integer rewards. Use radius E and intersect intervals with[0,1]. Report six contrasts:

1. **Sole primary:** `ACTIVE_HALF_MINUS_ZERO|H`.
2. `ACTIVE_ZERO_MINUS_HALF_SHARE|H` = ACTIVE_ZERO H−1/2.
3. `ACTIVE_HALF_MINUS_HALF_SHARE|H` = ACTIVE_HALF H−1/2.
4. `ACTIVE_HALF_MINUS_ZERO|U`.
5. `ACTIVE_MINUS_NEUTRAL_ZERO|U`.
6. `ACTIVE_MINUS_NEUTRAL_HALF|U`.

Use the sum of component error bounds for a difference; subtracting exact1/2 adds no error. Store exact rational centers/endpoints and outward-rounded decimal strings. A primary lower bound above zero supports the directional prediction in this model, an upper bound below zero contradicts it, and an enclosure containing zero leaves the sign uncertified unless an exact separate identity proves zero. This is numerical certification, not statistical uncertainty. Never label these bootstrap/95% intervals. Report fractions and percentage points, without importing the former one-descendant benchmark into this two-individual model. All14records and contrary signs must remain. NEUTRAL H=1/2 checks do not count as additional outcomes or replications.

## Execution and focused independent check

Use executor `outputs/stationary_policy_v1/` and HPC `PRIVATE_HPC/organized-variation-transfer/experiments/stationary_policy_v1`. One production allocation:1CPU,4GiB,30minutes. A second production job, extended timeout or changed precision/rates is not automatic after failure. Same-design technical corrections may be documented; never duplicate a pending or unknown submission. The four matrices/vectors are computed once, with durable partial-completion receipts. Package target: at most64MiB of scientific/source/report deliverables; use bounded logs and compressed integer JSON. Measure actual delivery size. This is a finite delivery budget, not a cumulative pre-write restriction across unrelated writers or Slurm streams.

Before production, fixtures cover: all256state encodings; exact target law and joint branch weights; duplicate candidate slots; tied-genotype donor invariance; retained-parent versus nonparent cache updates; policy flips and survivor order; sequential-selection normalization; neutral label symmetry; integer D divisibility; constructed small-chain stationary residual/error certification; all14keys and contrast orientations. Local tests may inspect constructed fixtures and the prespecified audit rows but must not solve production stationary contrasts as a pilot. Do not generate sampled scientific trajectories or seeds.

Prospectively select starting rows `[0,36,85,113,142,170,219,255]` from all four matrices for an independent reconstruction, for32complete rows and8,192numerators. The supervisor checker must implement those rows separately without importing the producer's kernel implementation. Independently recompute the exact residual, certificate and all14mean/contrast intervals from all four saved matrices/vectors, plus normalization and symmetry checks. It need not solve stationarity again. Expand row reconstruction only for an actual discrepancy.

Deliver source/configuration with task hash,256-row state index,four exact matrices,four stationary vectors/certificates,14estimates,fixtures and producer checks,the32audited rows,job/resource records,manifests and a compact report. One two-panel figure for stationary H and U is sufficient; identify numerical enclosures and show the1/2neutral reference, without hiding adverse directions. Preserve numerical failures and elapsed/resource records. No new manuscript or release is part of this execution.

The executor's last confirmed environment lacked SSH. Build and test locally, then write a genuine `LOCAL_HANDOFF.json` containing the frozen source hashes, resources, exact idempotent supervisor adapter command and actual submission state. Notify the supervisor directly. Do not repeat denied access probes or invent scheduler status. The supervisor can complete this same tested handoff using its available SSH access. Do not modify supervisor-owned coordination or original shared records. Stop execution after this finite assignment; the supervisor owns interpretation and the next decision.
