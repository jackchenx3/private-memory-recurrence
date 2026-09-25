# Where the stationary recurrence effect enters

Jack Chen · 25 September 2026 · Post-v1.5.0 technical note (study 062)

In the separate two-individual, one-bit model, the known small increase in stationary historical-policy frequency has two positive components under a specified symmetric decomposition: **+0.429556589 percentage points from the next-target law at common state weights**, and **+0.028665888 points from different stationary state occupancy at common drift values**. This rules out an explanation based solely on occupancy under this decomposition. It does not identify unique causal shares.

This note accompanies the [v1.5.0 manuscript](../../paper/MANUSCRIPT.md) ([archived DOI](https://doi.org/10.5281/zenodo.22950710)). It is a main-branch addition, absent from that archived release. No manuscript, release tag or DOI version is changed.

Related follow-up: [continuity of historical-policy availability (study 063)](../policy-availability063/README.md). Average H frequency and uninterrupted availability are different quantities; the separate note reports small duration effects, frequent total absence and the adverse ZERO comparison.

## Six fixed quantities

| Quantity | Center (percentage points) | Certified sign |
|---|---:|---|
| ZERO pre-switch selection drift, per update | −0.003417265 | Negative |
| HALF pre-switch selection drift, per update | +0.062043089 | Positive |
| HALF minus ZERO selection drift, per update | +0.065460354 | Positive |
| Direct target-law component (primary) | +0.429556589 | Positive |
| State-occupancy component | +0.028665888 | Positive |
| Total stationary H-frequency contrast | +0.458222476 | Positive |

H denotes historical retrieval; F denotes fresh exploration. ZERO renews the target independently. HALF copies the target from two updates earlier with probability one half and otherwise renews it. Both policies and storage are supplied, and each surviving policy label switches with probability 1/16 per update.

The first three rows measure frequency change per update before policy switching. The last three measure stationary frequency differences. Display values are individually rounded. The exact rational values, radii, outward decimal bounds and signs are in [DECOMPOSITION.json](DECOMPOSITION.json). The direct and occupancy error radii are each less than 1.042 × 10⁻⁴⁹ in fraction units (1.042 × 10⁻⁴⁷ percentage points). These are **numerical enclosures, not confidence intervals**. The six derived quantities are separate from the release's 14 mathematical quantities and 15,284 statistical estimates; none is a new empirical replication.

## Defined accounting and error bounds

Let h(s) be the fraction of H labels, μ = 1/16, β = 1 − 2μ = 7/8, and Pq the already published transition kernel under target law q. Define the conditional selection drift before label switching by

```text
dq(s) = ((Pq h)(s) − μ) / β − h(s).
```

At the true stationary distribution πq, the balance identity gives πq h − 1/2 = 7 πq dq. Put π̄ = (πHALF + πZERO)/2 and d̄ = (dHALF + dZERO)/2. Then

```text
C = 7 π̄ (dHALF − dZERO)                  [direct target-law component]
O = 7 (πHALF − πZERO) d̄                  [state-occupancy component]
T = C + O = 7 (πHALF dHALF − πZERO dZERO).
```

The calculation uses saved integer kernels and normalized integer stationary weights. For an exact reward f and accepted total-variation bound E, expectation error is at most E × (max f − min f). Applying this rule to each displayed reward supplies exact rational enclosure radii. [IDENTITIES.json](IDENTITIES.json) retains all reward spans and error bounds; [STATE_TERMS.json.gz](STATE_TERMS.json.gz) contains the 256 derived state records.

The saved weights are rounded, so they are not exactly stationary. The calculated centers retain the **nonzero** correction

```text
T − saved study-061 H contrast = 8 (rHALF − rZERO),
rq = π̂q (Pq h − h).
```

Its value is approximately 4.714 × 10⁻⁶⁰ in fraction units. The total enclosure overlaps the accepted study-061 enclosure. A small residual has not been treated as zero.

## Evidence and limits

The accounting definitions were frozen before these component values were inspected, but the total was already known. This is **post hoc mathematical accounting**, not an independent confirmation, a uniquely identified mediation fraction, or an empirical experiment. The fixed symmetric weighting convention matters to the interpretation.

A separately written integer-weighted direct-sum checker reproduced the six centers, bounds and signs, all 256 derived state records, and exact identities in **2,619 checks**. It imported neither the producer nor scientific operator code. This was a second implementation by the supervisor, not an external independent reviewer. The earlier constructed two-state fixture passed 72 checks without reading study-061 data. See [AUDIT.json](AUDIT.json), the [frozen specification](specification/ORG-STATIONARY-FLOW-062.md), and [fixture receipt](specification/ORG-STATIONARY-FLOW-062-PROSPECTIVE_CHECK.json).

No transition row, stationary distribution or population trajectory was regenerated. Analysis and checking together took 0.871 seconds locally. The accepted checks were reused for publication after input and source identity verification; they were not run again just to package the note.

The effect remains small and model-specific. It does not establish stationary behavior of the larger 32-individual system, spontaneous memory origin, or a consequential costly advantage. Population accuracy was not analyzed here: the adverse ZERO accuracy result in study 061 and unresolved primary results in studies 059 and 060 remain unchanged. In particular, negative ZERO selection drift remains visible in the table.

## Reproduce from the public saved inputs

Use Python 3.9 or later (standard library only) and Git. A **Git checkout containing v1.5.0 history** is required because the analysis authenticates inputs against that commit's integrity manifest. A source ZIP without Git history is insufficient. From a new checkout:

```bash
git clone https://github.com/jackchenx3/private-memory-recurrence.git
cd private-memory-recurrence
python3 -B docs/stationary-flow062/source/flow062_analysis.py \
  --repository . \
  --task docs/stationary-flow062/specification/ORG-STATIONARY-FLOW-062.md \
  --fixture docs/stationary-flow062/specification/ORG-STATIONARY-FLOW-062-PROSPECTIVE_CHECK.json \
  --output ../flow062-recomputed
python3 -B docs/stationary-flow062/source/flow062_audit.py \
  --repository . --output ../flow062-recomputed
```

Choose a new output directory: the analysis refuses an existing directory, and the checker refuses to overwrite AUDIT.json. The commands derive quantities from saved inputs; they do not generate kernels or solve stationary distributions. Expected check output is PASS with six records, 256 state records and 2,619 exact checks. Source inspection, syntax, input identities and links were checked for this publication; the commands were not rerun in a fresh checkout. Execution timestamps differ on reproduction.

[SOURCE_BINDINGS.json](SOURCE_BINDINGS.json) identifies all six original input files. [PUBLICATION_PROVENANCE.json](PUBLICATION_PROVENANCE.json) authenticates the unchanged executed sources and archived outputs. [ANALYSIS_RECEIPT.json](ANALYSIS_RECEIPT.json) records acceptance; the [original result note](RESULTS_NOTE.md) is retained.

The executed analysis source and [EXECUTION.json](EXECUTION.json) retain a harmless metadata-label issue: `started_at_utc` was captured during final output writing, rather than at process start. The monotonic `elapsed_seconds` value measures runtime. This changes no input, quantity or certificate. The archived [prospective fixture source](source/check_flow062_prospective.py) uses its original workspace-relative output layout and is retained for provenance, not advertised as a portable command. The explicit-argument analysis and checker above are the reproduction interface.

Text and original data: [CC BY 4.0](../../LICENSE-CONTENT.md). Original code: [MIT](../../LICENSE-CODE). This note is AI-assisted; see the [disclosure](../AI_ASSISTANCE.md). Cite the manuscript for the model and this commit-pinned note for the additional accounting; do not attribute these new files to the older DOI archive.
