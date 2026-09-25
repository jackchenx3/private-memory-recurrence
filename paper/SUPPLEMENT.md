# Supporting information: private memory and environmental recurrence

Jack Chen · Research preprint v1.5.0 · 25 September 2026

This document accompanies the [research manuscript](MANUSCRIPT.md). It identifies what each comparison measures, which populations are independently prepared, and what a reader can reproduce from this compact release. Population outcomes come from the abstract 32-individual bit-string model. Section S15 separately defines a two-individual stationary mathematical model.

## S1. What the findings establish

The original separate-introduction comparison supports opposite historical-minus-fresh carrier-frequency rankings under recurring and independent targets. Study 046 independently reproduces those two rankings and their direct interaction. Study 052 separately reproduces the later partial-recurrence direct-competition findings using independently prepared populations. These are distinct replication claims.

Studies 053–055 challenge other explanations using the study-052 genotype cohort. They change competitors, initial policy composition, and resident-policy preparation. New trajectories in those studies are not additional independent preparation cohorts. In particular, study 055 tests a policy substitution in a specific prepared population against the same unchanged founder. It does not generate memory storage from an initially memory-free individual: the fresh policy also carries an unused cache.

The 055 experiment and its saved-record reconstruction were complete before manuscript release preparation. The publication stage integrates the result and recomputes saved-table statistics. It introduces no new experiment, seed search, parameter search or outcome-dependent exclusion.

## S2. Study and dependence map

| Study | Scientific comparison | New work and reused evidence |
|---|---|---|
| 045 | One historical carrier versus one fresh-probe carrier, each against non-retrieving residents | 768 new fresh paths; historical controls and targets from earlier studies |
| 046 | Independent test of the separate-introduction ranking reversal | 2,304 new paths in an independent target/continuation cohort |
| 047 | Finite resident preparation versus matched naive starts | 4,608 new transfers; all eligible prepared states from 046 retained |
| 048 | Historical probe versus a random probe at the same parent–cache distance | 1,536 new paths; 4,608 authenticated controls from 047 |
| 049 | Exact, partial and zero lag-two copying after recurrent preparation | 2,304 new paths; 1,152 stored full-recurrence controls |
| 050 | Probabilistic versus deterministic global survival | 3,456 new probabilistic paths; 3,456 deterministic controls |
| 051 | H and F in the same population versus separate introductions | 4,608 new paths; 2,304 isolated controls; paired physical placements |
| 052 | Independent preparation replication of direct competition | 192 new preparations and 6,912 new transfers; no old/new cohort pooling |
| 053 | Historical versus fresh focal policy under each fixed competitor, at constant carrier density | 2,304 new HH/FF paths; 2,304 stored mixed controls from 052 |
| 054 | Rare H among F, or rare F among H, with all individuals retrieving | 2,304 new paths; genotype arrays and exogenous inputs reused from 052 |
| 055 | One policy substitution versus the same unchanged founder after resident-policy preparation | 1,152 new preparations and 3,456 new transfers; 192 source genotype arrays reused from 052 |
| 056 | Cross preparation history with future ZERO/HALF recurrence at identical prepared states | 2,304 new off-diagonal transfers; 2,304 saved diagonal controls from 055; no new cohort |
| 057 | Prospective new-cohort test of the crossed future-recurrence effect | 192 initial preparations, 768 policy preparations and 4,608 transfers; all stochastic inputs new; cohorts not pooled |
| 058 | Paired Hamming/four-bit-trap objective challenge | 384 initial preparations, 768 HALF policy preparations and 4,608 transfers; new cohort, objectives share indexed inputs |
| 059 | One-update fresh-expression pulse with label-only reversion | 960 new transfers on all 192 reused 057 HALF/H preparations; new inputs, terminal accuracy primary unresolved |
| 060 | Bounded measurement error crossed with future recurrence | 2,304 new transfers on all 192 reused 057 HALF/F preparations; primary interaction unresolved; exact and noisy founder recurrence effects positive |
| 061 | Separate stationary mathematical model with symmetric policy switching | Four exact 256-state kernels; 14 certified quantities; no sampled paths or independent population cohort |

The identifiers are archival study identifiers, not a count of independent experiments supporting every claim. A reused control can appear in several tables without becoming new evidence. All numerical grids are indexed in the [study catalog](../provenance/STUDIES.json). This revision also supplies the complete [056 estimates](../results/056/ESTIMATES.json) and [057 estimates](../results/057/ESTIMATES.json), their block aggregates and bootstrap rows.

## S3. State, objective and candidate budget

There are 32 individuals and 32 binary coordinates. At each update the target is a 32-bit value. Raw loss is normalized Hamming mismatch; raw accuracy is one minus mean normalized mismatch. Strategy, founder identity and cache are distinct fields. A cache records one ancestral state and its provenance. In the two-policy experiments, H and F both maintain caches, but only H reads the stored state as its probe.

Each update evaluates 128 candidate slots: 32 current parents, 32 policy probes, 32 fresh scouts and 32 local descendants. Duplicate candidates are still charged. An H probe is its owner's cached genotype. An F probe is its current genotype XOR an independent uniform 32-bit mask. Scouts use the accepted fresh-variation rule for every parent. A local descendant is based on the best raw-scoring member of its parent's current/probe/scout set and flips each bit independently with probability 1/32. Zero and multiple flips are retained.

An unchanged surviving parent preserves its cache. A surviving nonparent carrier stores its recipient parent's previous current state, including when the candidate is a duplicate. Labels and founder identities follow the recipient parent. There is no spontaneous policy innovation or recombination.

The initial 32 evaluations plus 40 × 128 candidate evaluations yield 5,152 objective calls per stage. Study 055 has 4,608 stages, totaling 23,740,416 objective calls. Preparation and transfer calls are both counted. Equal objective-call budgets do not imply equal storage, runtime, diversity or biological energetic cost.

## S4. Survival and cost

Earlier studies retain the 32 candidates with smallest penalized mismatch, using saved priorities and deterministic index fallbacks for ties. Probabilistic studies use weighted sampling without replacement. A candidate with penalized mismatch s has weight 2^(-s), and its race key is -log(u) × 2^s. The 32 smallest keys survive, with saved priorities and indices breaking ties. Uniform values are constructed from stored 52-bit integers by u = (k + 1)/(2^52 + 1).

A carrier penalty of one mismatch bit is an explicit score convention, not a calibrated energetic cost. When only some individuals are carriers, it can alter their relative survival. When all candidates are carriers, the same one-bit penalty multiplies every race key by two and preserves the ordering; this is why studies 054–055 do not add a redundant common-cost arm. It does not overturn negative costly introductions against non-carriers.

Reported computational reconstruction permits at most two units in the last place for independently recomputed race keys while requiring exact selected indices and order. Study 055 observed differences no larger than one unit in the last place; genotype, score, ancestry and cache checks were exact. These are implementation checks, not a proof that a pseudorandom implementation samples an ideal continuous distribution.

## S5. Environmental laws

The original recurrent law alternates two independently drawn uniform targets. The original independent law draws a fresh uniform target each update. Later experiments use ZERO, HALF and FULL to denote lag-two copy probabilities 0, 1/2 and 1. Under HALF, a target copies its own lag-two predecessor when its fixed copy bit says to copy; otherwise it uses a fresh innovation. A parity chain can therefore include renewed targets that are subsequently copied.

Unconditionally, adjacent targets are independent uniform under these laws. That identity does not imply that each realized adjacent distance is matched across the finite sample, or that the target is independent of the prepared population. Study 049 retains a previously recurrent preparation and first target pair. Study 055 instead applies the assigned law during both additional resident-policy preparation and continuation. Those different treatment contexts must not be pooled into a single recurrence response curve.

## S6. Resident-policy intervention in study 055

Every one of the 192 study-052 genotype arrays is used. For each array, all-H and all-F populations begin with caches initialized to their own current states and undergo 40 additional updates under each law. No endpoint is excluded based on fitness, diversity or ancestry. The resulting 1,152 complete resident populations are frozen before transfer.

Genotypes and caches at transfer are preserved exactly. Founder labels are rebased to current physical positions, retaining a map to their preparation ancestry. Two fixed physical positions define paired single-policy substitutions. In each prepared background, the three paths are STAY, SWITCH0 and SWITCH1. One STAY path supplies both unchanged-founder controls. H-to-F changes only use of the cache; F-to-H activates an already present cache.

The target law continues across the stage boundary using the final two preparation targets. Transfer uses 1,200 prospectively fixed continuation seed records across innovation, copy and continuation families. New seeds and new paths do not remove dependence on the reused source genotype cohort.

For a given background, SWITCH is the mean of the introduced founder's outcomes in the two switched placements. STAY is the mean of those same two founders' outcomes in the unchanged population. EFFECT = SWITCH − STAY is formed within continuation and then averaged within block. Separate absolute SWITCH changes answer whether the introduced type increased in mean, rather than whether it exceeded its matched control.

All five fixed partial-recurrence criteria are supported individually: positive F-to-H EFFECT, negative H-to-F EFFECT, positive absolute H introduction, negative absolute F introduction, and positive HALF-minus-ZERO F-to-H EFFECT. These pointwise results do not confer simultaneous confidence on their conjunction. ZERO leaves F-to-H unresolved and supports H-to-F benefit. Under HALF, both terminal population-accuracy effects remain unresolved.

## S7. Endpoints and uncertainty

| Quantity | Meaning |
|---|---|
| F0, F1, F40 | Founder or policy frequency initially, after one update and after 40 updates, as identified by the series key |
| D40 | F40 − F0; this differs from final frequency when initial frequencies differ |
| F | Mean post-selection frequency across the 40 updates |
| FE1–FE8 | Mean frequencies within the eight fixed five-update windows |
| U0, U1, U40 | Initial, first-update and terminal raw population accuracy |
| U | Mean post-selection raw population accuracy across 40 updates |
| E1–E8 | Accuracy over the eight fixed five-update windows |
| MLOSS | Mean post-selection normalized mismatch across the 40 updates; equal to 1 − U |

Complete keys also identify study-specific regime, cost, policy, background and comparison. Read a key together with that study's `analysis.py` and `config.json`; similarly named series across studies need not have identical intervention contexts.

Eight paired continuations are averaged inside each of 24 independent target blocks. The stored 2,000 bootstrap rows resample whole blocks. Means and 2.5th/97.5th percentiles of resampled means use NumPy's linear quantile method. The intervals are approximate and pointwise across a large correlated grid. No family-wide error guarantee is claimed. A positive interval supports a positive mean for that comparison; an interval containing zero remains unresolved and does not establish equivalence.

Structural zeros follow an intervention identity. Observed exact zeros describe this finite sample. Their degenerate intervals do not prove a zero population probability. Likewise, the reported zero-event upper bound concerns any survivor among eight continuations in a new block, not a per-lineage long-run fixation probability.

## S8. Contrary outcomes and local mathematics

The full grids retain all costs, laws, windows and predefined comparisons. They preserve negative changes, endpoint disagreements, ties and missing crossings. In study 055, the partial-recurrence H-to-F second placement contains a fresh-founder fixation at block 8, continuation 1, update 14; the negative mean does not erase that event. Study 054's sampled extinction of every rare F introduction is not a theorem of impossible establishment.

The [local candidate calculation](../docs/analytical/cache-diversity/NOTE.md) and [fixed-pool counterexample](../docs/analytical/pool-dependence/NOTE.md) distinguish pairwise distance from whole-pool selection. The [parity-chain note](../docs/analytical/intermittent-recurrence/NOTE.md) describes an ideal target law. The [cost sensitivity](../docs/analytical/cost-sensitivity/NOTE.md) and [quantization notes](../docs/analytical/survival-quantization/NOTE.md) have explicit mathematical assumptions. They are not population observations and do not prove biological generality or certify floating-point logarithms and pseudorandom generators.

## S9. Public reproduction and raw-data boundary

From this unpublished revision root:

```bash
python -m pip install -r requirements.txt
python scripts/verify_release.py
python scripts/reproduce_statistics.py
python scripts/rebuild_figures.py
```

The statistics check recomputes all 15,284 intervals from the included block aggregates and exact saved bootstrap indices. It also verifies every registered manuscript/figure statistic against its source summary. Figure generation uses those same summaries. Both write to `_rebuilt/` by default and neither runs a population experiment.

Archived scientific modules in `code/045` through `code/060` preserve each study's operators and analysis. Site-specific Slurm and SSH launch scripts are omitted. Some archived modules require original input tapes, directory layouts or predecessor packages; they are provided for inspection, not advertised as a turnkey rerun interface. Do not infer successful raw-trajectory reproduction from a passing saved-table check.

The multi-gigabyte candidate-by-candidate paths, random tapes and complete execution logs remain in the project archive and are not included in this compact public package. The archived independent reconstruction receipts describe checks already performed against those files. The public source map retains original and exported hashes and labels administrative-path transformations. Public integrity manifests authenticate this release's files, not files that are absent from the release.

## S10. Research status

This preprint synthesizes a bounded computational result. Internal agent review is distinct from external peer review, and correct computation is distinct from independent validation of a model. Practical effect size, applicability beyond this model, the origin and maintenance of memory storage, equilibrium invasion and general costly advantage remain open. Studies 056 and 057 were performed after research resumed; no additional population simulation is used to typeset this revision.

## S11. Crossed environments and prospective replication

Study 056 reuses 2,304 diagonal paths from 055 and generates 2,304 off-diagonal paths. Both preparation and future law have ZERO/HALF levels. Each future sequence recurses from its own preparation's last two targets. The primary is the HALF-minus-ZERO future effect on matched F-to-H D40, holding HALF preparation fixed. The secondary uses ZERO preparation. Preparation contrasts, interactions, reciprocal substitutions and collective accuracy remain separate.

Study 057 applies the same design to a fully new cohort. The three stages comprise 192 initial genotype preparations (052 procedure), 768 policy preparations (055 procedure) and 4,608 transfers (056 procedure). Inputs use 3,193 new seed records; no genotype array, target sequence, stage tape, placement shuffle or bootstrap row is reused. All inputs precede the first trajectory, and every completed preparation is preserved before its dependent stage. No outcome filtering, replacement seed or sample expansion occurs. All 5,568 paths together use 28,686,336 scientific objective evaluations. Different stage families separate the initial, policy and continuation randomness, with the accepted common-random-number coupling retained within each stage.

Each cohort has nine statistical groups and 18 metrics, for 162 pointwise intervals. Two founder placements are averaged inside each of eight replicates, then inside 24 blocks. Each cohort uses its own 2,000 stored whole-block bootstrap rows; no pooling or heterogeneity test is performed. The new-cohort result is prospective within the same model and implementation, not an independent implementation or a test in organisms.

The compact `results/056` and `results/057` directories preserve complete estimates and block summaries. They add 324 estimates to the 14,729 in the unchanged version 1.0 package. Fates, adverse effects and performance disagreements are included as compact tables, with large text tables losslessly compressed; the full raw execution archives remain separate. Both the producer's saved-record audit and the supervisor's separate arithmetic check preserve their actual scope. Raw block 0 was chosen before outcomes; it is a focused audit, not a second complete replay of every trajectory. No recorded-score recomputation creates a new scientific trajectory.

The unified statistics command in S9 now checks 15,284 estimates: 14,729 from the original package, 324 from 056/057, 114 from 058, 36 from 059 and 81 from 060. Native 056/057 estimates retain sign counts and effect scales; `summary.json` projects mean, interval and classification into the earlier release schema, and `BLOCK_SUMMARIES.jsonl` is a format-only copy of the native JSON array. Both transformations are recorded in the export map. Figures 12 and 13 can also be rebuilt separately:

```bash
python scripts/rebuild_extension_figures.py
```

The scripts use only included tables. They do not rerun population trajectories or constitute another independent cohort. [Version DOI](https://doi.org/10.5281/zenodo.22930084); earlier [version 1.0 DOI](https://doi.org/10.5281/zenodo.22907237) remains unchanged.

## S12. Fixed interacting objective in study 058

This prospective challenge uses eight consecutive four-bit blocks, with bit zero least significant. The loss for u target-matching bits in a block is [1,2,3,4,0] for u=0,1,2,3,4. HAM counts mismatching bits. Both objectives range from 0 to 32, with one global optimum at the target. TRAP4 has 256 strict single-bit local optima, including that optimum: each block can be at zero or four matches. Its local-optimum property is an exact property of the objective, distinct from any population outcome. The explicit evaluator uses the chosen loss in every evaluation, donor comparison and survival decision in all three stages. Legacy raw_mismatch fields contain the identified objective loss; raw_accuracies contain its normalized utility.

All 5,760 paths and 3,193 seed IDs are new. Initial preparation retains the accepted zero-start SHAM_C0 procedure under a new alternating pair, with 192 paths per objective. Each objective's resulting genotypes enter 384 HALF all-H/all-F policy preparations. Every endpoint is retained; founders are rebased to physical slots and switching changes the policy label while retaining genotype and cache. Each prepared background enters both future laws and STAY/SWITCH0/SWITCH1, giving 2,304 transfers per objective. Target recursion continues from the actual last two preparation targets. Objectives share indexed tapes, not selected populations. Distinct families separate initial, policy and transfer randomness. No objective identity enters a paired random family, no outcome changes random consumption, and no older trajectory is reused. The single allocation used 783 seconds, one CPU and 4 GiB requested memory; batch MaxRSS was 491,868 KiB.

The primary is TRAP4's HALF-minus-ZERO difference in the matched F-to-H D40 effect, holding HALF preparation fixed. Founder changes begin at 1/32; matched effects subtract the same founder's unchanged-policy control. Two placements are averaged before eight replicates within each of 24 target blocks. Multiplication by 32 gives expected-descendant units. The benchmark of one expected descendant is assessed separately from zero using the same pointwise interval. It applies to the difference between matched effects, not absolute terminal frequency or a typical founder. The frozen catalog has 108 objective-specific entries plus six direct paired objective contrasts in founder D40, for 114 total. There is no cross-objective utility contrast grid or multiplicity-wide coverage. The 2,000 new frozen bootstrap rows are shared across paired objectives; linear 2.5th and 97.5th percentiles are retained.

All unfavorable paths, fates and declines remain in the full execution archive. There are 5,618 negative paired metric records, 3,319 founder/utility sign disagreements and 21,787 preparation-decline or negative-selection records. These counts refer to overlapping records, not independent discoveries or trials. Individual loss under the primary's favorable future law remains common. Reciprocal terminal utility is unresolved in 058, whereas 057 supplied a positive interval for its own reciprocal Hamming endpoint; no between-study heterogeneity test is supplied.

Thirteen focused tests preceded execution. The producer saved-record audit checked the complete 114-estimate catalog and prospectively selected raw block zero: 16 initial, 32 policy and 192 transfer paths. It reconstructed 1,236,480 objective scores and all relevant donor, cache, selection and founder mappings. The supervisor audit imports no producer module and separately checks all estimates/classifications, recorded scores, stage linkage, rebasing, survival order and endpoints for the same block. The maximum statistical discrepancy is 2.220446049250313e-16. These are saved-output checks, not extra scientific trajectories, a new independent implementation or external peer review.

The compact release includes [all 058 estimates](../results/058/ESTIMATES.json), [block summaries](../results/058/BLOCK_SUMMARIES.json), [frozen bootstrap rows](../results/058/BOOTSTRAP_INDICES.json), [fate counts](../results/058/FATE_COUNTS.json) and [the supervisor audit](../results/058/SUPERVISOR_AUDIT.json). To check the 114 new estimates from the repository root:

```bash
python scripts/check_058_statistics.py
```

This command checks the 114 additions using included block summaries and resampling rows only; the unified script in S9 verifies all 15,284 estimates. Public 058 exports also include scientific operators, seed provenance, path metrics, fates, declines, negative records and founder/utility disagreements; larger text tables are losslessly compressed. Raw candidate trajectories and random tapes remain outside the compact release. The source map records every exported source and any administrative transformation. Rebuild figures 14 and 15 with `python scripts/rebuild_058_figures.py`, or use the top-level figure command for all 18. These scripts generate no scientific trajectories. [Version 1.2.0 DOI](https://doi.org/10.5281/zenodo.22933218); all earlier version records are preserved.

## S13. One-update pulse and persistent founder ancestry

Study 059 uses every HALF-prepared all-H state from 057. All genotypes, caches and rebased founder records are authenticated before transfer. It generates 1,201 new seed IDs, disjoint from the recorded inventory through 058, and new HALF targets, candidate/survival arrays, physical founder placements and 2,000 bootstrap rows. No preparation, cohort pooling or outcome filtering is added. All five configurations in a replicate share indexed exogenous arrays. The first 40 fresh-mask rows in the accepted absolute-index convention are unused zero placeholders; consumed transfer rows are new. Future target recursion starts from each preparation's actual last two targets.

PULSE permits F only during update 1, then changes every remaining F label to H. Genotype, founder ID, cache tuple and order stay fixed at reversion. CONT has the same first update but permits F thereafter. STAY uses H throughout and supplies both unchanged-founder controls from one trajectory. The reversion occurs even when the focal founder is already absent. Post-selection and post-reversion expression frequencies are separately recorded. Founder ancestry is not rebased or deleted at this boundary. The scheduled frequency jump is not a selection term.

The catalog crosses three arm summaries and three paired contrasts with six endpoints: post-selection accuracy at update 1 (U1); mean accuracy over updates 2-40 (U_LATE); terminal accuracy (U40); mean accuracy over updates 1-40 (U_ALL); and focal founder changes from 1/32 at updates 1 and 40 (D1 and D40). Two physical placements are averaged before the eight replicates within each of 24 blocks. STAY population accuracy is counted once. The 36 intervals are approximate pointwise block-bootstrap intervals with shared resampling rows and linear percentiles. Pulse-minus-continuous U1 and D1 are structural zeros under the common first-update coupling; they are not empirical equivalence findings.

The fixed primary PULSE_MINUS_STAY/U40 is unresolved. Its interval also overlaps the separate one-expected-matching-bit benchmark, 1/1024 accuracy. Every population-accuracy contrast other than the exact first-update pulse/continuous identity is unresolved. The positive pulse-minus-continuous D40 contrast is a secondary ancestry outcome, not a substitute primary. It does not imply superiority over unchanged H, since pulse-minus-STAY D40 is unresolved. The negative continuous-minus-STAY D40 effect and frequent founder loss remain. Two continuous-F founders remain polymorphic at update 40, one at each placement; these cases were retained. The two placements are paired treatments, not 384 independent trials.

All 1,817 negative metric records, 1,822 exact ties, 537 ancestry/accuracy sign disagreements and 18,058 decline or negative-selection records are preserved. These overlapping record counts do not count independent discoveries. Complete compact time series, founder/expression fates and adverse records accompany the compact release. The underlying full candidate records remain in the authenticated execution package on HPC.

Thirteen focused constructed-fixture tests passed before production. Job 53332539 completed once in 117 seconds with one CPU, 4 GiB requested memory and batch MaxRSS 228,536 KiB. There are 960 paths and 4,945,920 objective evaluations, with no extra diagnostic objective calls. The saved-output audit checks all 36 estimates and the prospectively selected 40 paths of raw block zero. The supervisor independently reconstructs 206,080 stored scores, 204,800 survival candidate orderings, 153,600 nonparent genotype/cache records, 16 scheduled reversion events and 16 first-update pair identities without importing producer modules. Maximum estimate/interval discrepancy is 2.220446049250313e-16. This is focused output verification, not external peer review or an independent full-model implementation.

The additions include [all 059 estimates](../results/059/ESTIMATES.json), [block summaries](../results/059/BLOCK_SUMMARIES.json), [frozen bootstrap rows](../results/059/BOOTSTRAP_INDICES.json), [founder fate counts](../results/059/FOUNDER_FATE_COUNTS.json) and [the supervisor audit](../results/059/SUPERVISOR_AUDIT.json). From the repository root, the study-specific saved-table check is:

```bash
python scripts/check_059_statistics.py
```

The study-specific check covers 36 new estimates; the unified command in S9 verifies all 15,284 estimates. Public exports include the scientific source through 059 and document each administrative transformation. Rebuild figure 16 using `python scripts/rebuild_059_figure.py`, or use the top-level command for all 18 figures. Raw candidate trajectories and random tapes remain outside the compact release. [Version 1.3.0 DOI](https://doi.org/10.5281/zenodo.22939403); all earlier version records are preserved.

## S14. Bounded measurement error in private-memory transfer

Study 060 uses all 192 HALF-prepared F-background states from 057, without changing genotypes, existing founder rebasing or caches. Preparation used exact observations. Each continuation starts from its actual last two preparation targets. ZERO and HALF share innovations and copy bits but apply their own lag-two recursion. All variants within a replicate share indexed proposals, noise, survival draws and a new physical-slot permutation. STAY provides the two founder controls from one trajectory; SWITCH0 and SWITCH1 change only the relevant F label to H. There are 1,393 new seed IDs disjoint from the archived inventory through 059, with 989,184 noise uniforms and 2,000 bootstrap rows frozen before outcomes. No prior transfer path or random tape is reused.

Every initial query and each of 128 candidate queries per update receives its own observation. EXACT returns true Hamming loss h; NOISY returns h + (2u - 1). Duplicate genotypes have different query indices and remain separately charged. Initial observations do not enter later decisions because current parents are queried again. Each candidate's one returned score is reused for donor and survivor decisions. Truth remains evaluator-only. Child cache content remains the current parent's genotype, absolute update and slot; retained parents keep their existing cache. No score is stored in a cache. The first 40 fresh-mask rows are unused zero placeholders; only newly generated rows for absolute indices 40-79 are consumed.

The accepted integer-only bit-shift survival kernel required an explicit real-score adapter. The adapter evaluates -log(v) times 2.0 raised to the observed score, retains the fixed survival coefficient, 52-bit open-uniform conversion and (key, tie, index) order, and does not round or clip scores. Zero-error fixtures match accepted donor choices, survival races, states and true performance. Bounded observation error changes donor and survivor decisions together; neither mechanism is separately identified.

The 81-entry catalog has nine endpoints per group: SWITCH, STAY and EFFECT founder change D40, plus their mean (U) and terminal (U40) true-accuracy versions. EFFECT is SWITCH minus STAY. The nine groups are the four observation/future-law cells; HALF minus ZERO separately in EXACT and NOISY; NOISY minus EXACT separately under ZERO and HALF; and their direct interaction. Two placements are averaged before eight replicates within each independent block. The primary is NOISE_BY_RECURRENCE/EFFECT/D40. Founder fractions are multiplied by 32 for expected descendants; accuracy fractions by 1,024 for matching bits across the whole population. U averages those bits over the 40 post-selection updates. These units are distinct.

The negative-interaction prediction is unresolved. Its interval is above minus one expected descendant but overlaps zero and plus one descendant. This is not an equivalence test. The positive noisy recurrence effect does not replace the primary. Mean absolute accuracy declines under noise in both arms under both future laws; terminal noise effects remain unresolved. All 4,710 negative paired records, 2,858 exact ties, 43,396 decline records and 2,389 transmission/accuracy disagreements are retained. These overlapping record counts are not independent discoveries. Founder losses and the two placement-specific results remain in the compact evidence; inference never conditions on establishment or survival.

Eleven constructed-fixture tests passed. One job completed in 352 seconds using one CPU and 4 GiB requested memory, with batch MaxRSS 319,956 KiB. The 2,304 paths used 73,728 initial and 11,796,480 candidate queries, 11,870,208 total, with no extra diagnostic objective calls. The supervisor recomputed all 81 estimates and 15,552 paired scalar metrics directly from saved time series without producer imports; maximum estimate discrepancy was zero. Preselected raw block zero contained 96 paths, 494,592 recorded queries, 122,880 donor choices and 491,520 race candidates. All selected orders, genotype/cache/founder transitions and true endpoints matched exactly.

The initial reviewer checker demanded bitwise race-key agreement across HPC and local arithmetic and stopped on a tiny difference. A recorded portability check found 486 keys differing by at most two units in the last place (maximum relative difference about 3.001e-16). The corrected checker records differences up to four such units but still requires identical survivor ordering and every subsequent state. All audited selections were identical. The initial checker/failure log, corrected checker and numerical record are preserved separately; scientific source and outcomes were not edited or rerun. This is focused stored-output verification, not independent full-model replication or external peer review.

The [81 estimates](../results/060/ESTIMATES.json), [block summaries](../results/060/BLOCK_SUMMARIES.json), [frozen resamples](../results/060/BOOTSTRAP_INDICES.json), [founder fates](../results/060/FOUNDER_FATE_COUNTS.json), [supervisor audit](../results/060/SUPERVISOR_AUDIT.json) and [portability record](../results/060/NUMERICAL_PORTABILITY.json) accompany this release. The original scientific source is archived for inspection; it may depend on original layouts and omitted input tapes and is not advertised as a turnkey rerun package. Raw candidate trajectories and random tapes remain outside the compact release.

```bash
python scripts/check_060_statistics.py
python scripts/rebuild_060_figure.py
```

The study-specific command checks 81 additions. The unified command in S9 checks all 15,284 estimates through 060. Figure 17 binds seven saved mean/interval pairs; no scientific trajectory or random draw is generated by either command. [Version 1.4.0 DOI](https://doi.org/10.5281/zenodo.22949032); public v1.3.0 and all earlier versions remain preserved.

## S15. A separate stationary model with supplied memory

### Complete state and update order

Each of two ordered individuals has genotype g, private cache c and policy h, all bits, with H=1 and F=0. The last two targets are a,b, where b is current. The complete post-update state has ID g0 + 2c0 + 4h0 + 8g1 + 16c1 + 32h1 + 64a + 128b, giving 256 states. There are no founder identities or timestamps in this model. The following order defines a different mathematical process from the 32-individual simulator.

First draw target e. ZERO gives each bit probability 1/2. HALF copies a with probability 1/2 and otherwise draws a fair bit, so P(e=a)=3/4 and P(e!=a)=1/4. Independently draw fair fresh-probe and scout bits for both recipients, and independent local-flip bits with probability 1/4. All variables are drawn even when unused. Under active probes, H reads its own cache and F uses its fresh bit; under neutral probes every label uses a fresh bit. Each local child starts from the genotype with lowest mismatch to e among its recipient's parent, probe and scout, then applies its local flip. On the one-bit objective, tied minimum-score genotypes are identical.

Eight candidate slots are ordered parent0, parent1, probe0, probe1, scout0, scout1, child0, child1. Duplicates are distinct slots. A retained parent keeps its (g,c,h); a nonparent has the proposed genotype, its recipient's old genotype as cache, and its recipient's policy. Donor/source labels are not inherited. All eight slots are charged, and no policy cost is imposed. Weight w is two for a match to e and one for a mismatch. For W equal to the sum of weights, ordered survivor slots j,k, j!=k, have probability w_j w_k/[W(W-w_j)]. This exact sequential sampling rule is defined directly, without a floating exponential-race identity. Each survivor then independently flips policy with probability 1/16; cache and genotype are unchanged. The final target pair is (b,e).

The four kernels cross active/neutral probes and ZERO/HALF recurrence. No rate grid or population-size extension was run. With rows and columns ordered by state ID, P=A/D uses nonnegative integer A and D=377864847360. Let L be the least common multiple of W(W-w) for W=8,...,16 and w in {1,2}; L=1441440. Then D=4 x 16 x 16 x 256 x L. These factors cover the target, fair probe/scout, local-flip and policy-flip probabilities; the selection denominator divides L. Every row sums exactly to D. Literal expansion has 28,672 branches per row, or 29,360,128 across all four kernels; 262,144 transition numerators are stored.

### Uniqueness and the residual certificate

From any starting state, reach any desired final state in two updates by selecting scout0 then scout1 at both updates. Choose first-update scout genotypes to equal the desired final caches, second-update scout genotypes to equal the desired final genotypes, and the successive targets to equal the desired final target pair. First-update switches can set both policies to F; second-update switches set any desired policies. Because nonparent caches store recipient genotypes, this also gives the desired final caches.

At each update the specified scout pair has probability 1/4, the specified target at least 1/4, the ordered scout selections at least 1/(16 x 15), and the specified policy pair at least 1/256. Other draws are unrestricted. Thus every entry of P squared is at least b0=(1/983040)^2=1/966367641600. All four finite chains are irreducible and aperiodic and have a unique stationary distribution pi. Uniform two-step minorization has alpha=256b0=1/3774873600. The computed support graphs each have one strongly connected class and period one, consistent with this argument.

For each exact kernel, fixed 80-decimal-digit elimination with deterministic pivoting solves the stationary equations and normalization. Each component is rounded to a multiple of 10^-60, ties to even, giving nonnegative integers k_i. Negative components or a zero total would be rejected, not clipped. Let K=sum(k_i), p_i=k_i/K and R=sum_j |sum_i k_i A_ij - k_j D|. Arbitrary-precision integer arithmetic gives r=R/(KD)=||pP-p||_1 exactly. The fixed acceptance criterion is r<=10^-30. No precision increase or fallback solve follows a result's sign.

Two-step minorization contracts total variation by at most 1-alpha. Moreover, ||pP^2-p||_1<=2r, because Markov multiplication cannot increase the L1 norm of a signed measure. Therefore ||p-pi||_1<=2r/alpha, and TV(p,pi)<=min(1,r/alpha)=E. For any reward in [0,1], the expectation error is at most E. Difference radii sum their component bounds; subtracting the exact one-half reference adds no error. Primitive enclosures are intersected with [0,1]. All four residuals are below 6.31 x 10^-59, and E is below 2.38 x 10^-49. These numerical bounds do not quantify uncertainty about assumptions or generalization.

Neutral matrices are invariant under complementing both policy bits. Uniqueness then implies stationary mean H=1/2 exactly. All matrices also satisfy joint genotype/cache/target complementation. These symmetries were checked entry by entry, without forcing solver symmetry. Ordered survivor sampling does not assume exchangeability of the output slots.

### Fixed outcomes, including adverse comparisons

The H reward is (h0+h1)/2. Current population accuracy U is 1-[(g0 XOR b)+(g1 XOR b)]/2. The eight kernel means and six fixed contrasts below constitute all 14 outcomes. The sole primary is active HALF-minus-ZERO H. A positive lower numerical bound certifies a positive sign; a negative upper bound certifies a negative sign. A zero-containing enclosure would not certify a sign without a separate exact identity. There is no sampling uncertainty, statistical confidence interval, one-descendant benchmark or equilibrium-invasion interpretation here. Values below are rounded for display; exact centers and outward-rounded bounds are in the saved table.

| Quantity | Value | Unit | Direction |
|---|---:|---|---|
| Active ZERO: H | 49.976079146 | percent | mean |
| Active ZERO: U | 67.222586967 | percent | mean |
| Active HALF: H | 50.434301623 | percent | mean |
| Active HALF: U | 68.775118376 | percent | mean |
| Neutral ZERO: H | 50.000000000 | percent | mean |
| Neutral ZERO: U | 67.481944961 | percent | mean |
| Neutral HALF: H | 50.000000000 | percent | mean |
| Neutral HALF: U | 68.072403064 | percent | mean |
| Active HALF - ZERO: H (primary) | 0.458222476 | points | positive |
| Active ZERO H - one-half | -0.023920854 | points | negative |
| Active HALF H - one-half | 0.434301623 | points | positive |
| Active HALF - ZERO: U | 1.552531409 | points | positive |
| Active - neutral ZERO: U | -0.259357994 | points | negative |
| Active - neutral HALF: U | 0.702715312 | points | positive |

The H-frequency effect is small: active ZERO is slightly below the neutral share, whereas active HALF is above it. Active accuracy is lower than neutral accuracy under ZERO and higher under HALF. These are separate outcomes; their co-occurrence does not establish causal mediation by H frequency. This minimal model supplies storage and policies, so it does not establish memory origin, biological rates, general costly advantage or practical optimizer usefulness. It also does not establish stationarity, equilibrium invasibility or evolutionary stability in the larger model. Studies 059 and 060 retain their unresolved primaries.

### Verification and archived source

Twelve preproduction constructed-fixture tests passed. One HPC job completed in 14 seconds with one CPU, 4 GiB requested memory and a 30-minute allocation limit. Four kernels and four stationary vectors were computed once; no sampled path, random seed, bootstrap or burn-in was used. The supervisor independently reconstructed the 32 prospectively selected rows (IDs 0,36,85,113,142,170,219,255 in each kernel), compared all 8,192 numerators, and checked all four residual certificates, all 1,024 rounded weights, support/symmetries and all 14 outcomes. It imported no producer implementation and did not solve stationarity again. All 136 delivery files match the local/HPC manifests. Verification is not external peer review or independent empirical replication.

The compact addition contains the full exact matrices, saved vectors/certificates, all outcomes, state index, frozen specification, scientific source and accepted audit. Administrative path substitutions are recorded in the export map. The original scientific modules are archived for inspection; original orchestration/layout dependencies are not advertised as a turnkey rerun. Saved-certificate verification and figure rebuilding are portable and require no new scientific execution:

```bash
python scripts/check_061_certificates.py
python scripts/rebuild_061_figure.py
```

The mathematical checker covers 14 certified records and their figure/quoted-value bindings. The unchanged population checker in S9 covers 15,284 statistical estimates through 060. These evidence counts remain separate in EVIDENCE_REGISTRY.json. [Version 1.5.0 DOI](https://doi.org/10.5281/zenodo.22950710); public version 1.4.0 and all earlier DOI versions remain unchanged.
