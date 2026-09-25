# Research guide: mutation access, population state and memory

Jack Chen · 25 September 2026 · Documentation added after private-memory v1.5.0

These four preprints address related questions in different abstract models. Follow the version DOI for a fixed paper and its repository for supporting material. Private-memory versions1.0–1.5 belong to one work. The guide adds no experiment or peer review. [Machine-readable catalog](RESEARCH_CATALOG.json).

| Question | Model and measured outcome | Main finding and boundary |
|---|---|---|
| [Does access to more adjustable regulatory directions improve subsequent adaptation from the same starting state?](https://zenodo.org/records/22821444) | 16-trait developmental-network model; matched trained states and a fixed proposal budget. | More available directions improved the fixed primary and matched opening/freezing contrasts under the tested constraints. Tighter tested bounds attenuated some paired capacity contrasts. |
| [How does current population state change the transfer value of an inherited variation orientation?](https://zenodo.org/records/22907602) | Two-dimensional finite-population model; organized versus quarter-turned variation with equal covariance eigenvalues. | Both centroid and centered population configuration changed later rule effects. Prospective state-based choices improved on centroid-only choices in fresh histories. The improvement was below the prespecified usefulness target; unconditional switching was already strong and subgroup harms remained. |
| [When does retained history improve population search relative to current donors, new children or fresh scouts?](https://zenodo.org/records/22907634) | 32-bit, 32-individual changing-target model; a shared four-record cache and matched objective-query budget. | Memory value depended on the comparator and recurrence. A fixed hybrid benefited from historical rather than current donors with scouting held fixed. The independent cohort only partly reproduced the complete cumulative ranking-switch prediction. |
| [When does using an available private memory increase founder representation, and does population accuracy change in the same way?](https://zenodo.org/records/22950710) | 32-bit, 32-individual finite-budget model; private one-record caches, inherited policy labels and founder identities. | Future recurrence increased the matched historical-use founder effect at fixed prepared states; a new cohort reproduced its direction. A fixed interacting objective retained a positive recurrence effect. Frequent founder loss and adverse population outcomes remain; founder representation is distinct from collective accuracy. |

## Papers and evidence boundaries

### 1. Available regulatory mutation directions improve finite-budget adaptation from matched states in a developmental-network model

Verified version: **v1**. [Version DOI](https://doi.org/10.5281/zenodo.22821444) · [All-version DOI](https://doi.org/10.5281/zenodo.22821443) · [Repository](https://github.com/jackchenx3/regulatory-mutation-options).

**Interpretation.** Target attainment remained rare in difficult cases; cost and historical retention did not improve uniformly. The results do not establish spontaneous origin, maintenance by selection or a universal dimensionality advantage.

**Replication and reuse.** The record distinguishes an initial separate 48-unit cohort and a later 48-unit-per-family validation. Multiple endpoints and intervention contrasts are not independent replications.

**Reuse terms.** Zenodo lists CC-BY-4.0 for its deposited manuscript. The linked GitHub RIGHTS_STATUS.md says no project license is granted; no software license or tagged GitHub release was found. This catalog does not extend the deposit license to repository code. [Repository rights statement](https://github.com/jackchenx3/regulatory-mutation-options/blob/main/RIGHTS_STATUS.md).

### 2. Population state changes the transfer value of organized variation in a finite-population model

Verified version: **1.0.0**. [Version DOI](https://doi.org/10.5281/zenodo.22907602) · [All-version DOI](https://doi.org/10.5281/zenodo.22907601) · [Repository](https://github.com/jackchenx3/state-dependent-variation) · [GitHub release](https://github.com/jackchenx3/state-dependent-variation/releases/tag/v1.0.0).

**Interpretation.** More detailed local calculations improved one-step calibration but worsened terminal calibration. Neither a unique mediator nor a generally optimal policy is identified.

**Replication and reuse.** The prospective policy comparison uses 48 freshly trained histories. Independent continuations from fixed checkpoints test conditional responses; they are not additional independently trained cohorts.

**Reuse terms.** Manuscript, figures and data: CC-BY-4.0. Original code: MIT; third-party terms remain separate. [Code license](https://github.com/jackchenx3/state-dependent-variation/blob/v1.0.0/LICENSE-CODE).

### 3. Retained memory and fresh exploration under a matched evaluation budget in a changing-target population model

Verified version: **1.0.0**. [Version DOI](https://doi.org/10.5281/zenodo.22907634) · [All-version DOI](https://doi.org/10.5281/zenodo.22907633) · [Repository](https://github.com/jackchenx3/memory-and-fresh-search) · [GitHub release](https://github.com/jackchenx3/memory-and-fresh-search/releases/tag/v1.0.0).

**Interpretation.** Memory lost to random scouts under independent targets; terminal comparisons and individual failures qualify average gains. An imposed search policy does not demonstrate selection for memory or its spontaneous origin.

**Replication and reuse.** The second cohort supports the recurrence interaction and independent-target disadvantage but leaves recurrent cumulative superiority unresolved. Hybrid and retention comparisons reuse that already observed cohort.

**Reuse terms.** Manuscript, figures and data: CC-BY-4.0. Original code: MIT; third-party terms remain separate. [Code license](https://github.com/jackchenx3/memory-and-fresh-search/blob/v1.0.0/LICENSE-CODE).

### 4. Environmental recurrence changes the transmission advantage of private memory in a finite-budget population model

Verified version: **1.4.0**. [Version DOI](https://doi.org/10.5281/zenodo.22950710) · [All-version DOI](https://doi.org/10.5281/zenodo.22907236) · [Repository](https://github.com/jackchenx3/private-memory-recurrence) · [GitHub release](https://github.com/jackchenx3/private-memory-recurrence/releases/tag/v1.5.0).

**Interpretation.** The pulse population-accuracy primary and bounded-observation noise interaction remain unresolved. Noise lowered average true accuracy. No noise equivalence, equilibrium invasion, spontaneous memory origin or general costly advantage is established.

**Replication and reuse.** Studies046,052 and057 contain separately identified independent-cohort tests. Studies059 and060 reuse057 preparations;058 has new paired objective-specific inputs. Releases1.0–1.5 are versions of one work, not separate replications.

**Reuse terms.** Manuscript, figures and data: CC-BY-4.0. Original code: MIT; third-party terms remain separate. [Code license](https://github.com/jackchenx3/private-memory-recurrence/blob/v1.5.0/LICENSE-CODE).

## Read the outcomes separately

- **Adaptation or search performance:** the first three works study effects on objective performance under their own model and budget.
- **Founder transmission:** the private-memory work also follows policy labels and ancestry. Increased founder representation can coexist with worse population accuracy or frequent founder loss.
- **Mechanism and ideal models:** local expectations, mathematical bounds and saved-output checks have narrower claims than propagated population results. They are not new empirical replications.
- **Origin and generality:** supplying a strategy or mutation direction does not explain its spontaneous origin. No cross-paper comparison establishes a universal optimizer or a measured biological effect.

The last three deposits include compact evidence packages; large raw trajectories and random tapes are outside those releases. The first deposit contains its manuscript and links a separate source repository. Consult each paper’s availability statement before treating an archive as a complete raw rerun package.

Metadata and links were checked on25September2026. The first deposit’s displayed version isv1; its legacy API omits that label. The catalog records this distinction and does not invent a GitHub release. Its Zenodo license and repository rights statement differ in scope, as documented above.

This guide and catalog are CC BY4.0. Existing works and dependencies retain their own stated terms. Stable public identifiers and readable metadata make the work easier to access; they do not guarantee indexing, citations or inclusion in future AI training.

The v1.5.0 private-memory revision adds a distinct two-individual/one-bit stationary mathematical model with supplied storage and ongoing policy switching. Recurrence raises stationary H frequency by 0.458222476 percentage points. Active-minus-neutral accuracy is adverse under ZERO and positive under HALF. Its 14 certified mathematical quantities remain separate from 15,284 statistical estimates; numerical enclosures are not confidence intervals or replication of the 32-individual model.
