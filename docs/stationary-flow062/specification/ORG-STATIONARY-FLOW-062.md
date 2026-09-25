# ORG-STATIONARY-FLOW-062 — immediate target-law channel versus stationary occupancy

Revision1. Frozen before new component values are inspected. Sole finite mathematical analysis after PUB-PORTABLE-061. Supervisor-owned; no executor assignment or production job. This is post hoc mechanistic accounting of the known061total, not independent confirmation or empirical replication.

## Inputs and scope

Use only the unchanged publicv1.5.0 ACTIVE_ZERO and ACTIVE_HALF matrices and rounded stationary vectors/certificates under `results/061/`, their accepted `OUTCOMES.json` and saved-certificate receipt. Authenticate exact bytes against the v1.5.0 manifest/release commit651c4289b1ac34efb30d1a81560e88cd74b1609f. The new portable-tool main-branch commit changes none of these inputs. Do not regenerate transition rows, repeat raw audits, solve a stationary system or simulate trajectories. No new parameter, precision extension, binning search or outcome-dependent metric is authorized.

The061model remains two ordered one-bit individuals with supplied caches and symmetric switching probabilitymu=1/16. Its result is not stationarity evidence for the32-individual model or memory origin. This task does not analyze population accuracy or establish unique causal mediation.

## Exact definitions

Let h(s)=(((s>>2)&1)+((s>>5)&1))/2. Write beta=1-2mu=7/8 and P_Z,P_H for the two ACTIVE transition matrices normalized by their exact denominator. Let pi_Z,pi_H be the true stationary distributions; use normalized integer saved weights for computed centers and their accepted total-variation bounds E_Z,E_H for certification.

For q in Z,H define the pre-switch selection drift

`d_q(s) = ((P_q h)(s) - mu)/beta - h(s)`.

This follows from independent symmetric policy flips after selection. Conditional drift is an exact rational function of the saved kernel, not a local-offspring proxy. At true stationarity, `pi_q h - 1/2 = 7 pi_q d_q`.

Define `bar_pi=(pi_H+pi_Z)/2` and `bar_d=(d_H+d_Z)/2`. The two stationary-H-frequency contributions are

`C = 7 bar_pi (d_H-d_Z)` (direct target-law change at common averaged state weights),

`O = 7 (pi_H-pi_Z) bar_d` (state-occupancy change at common averaged drift).

Their sum equals the true stationary H-frequency contrast. These are a specified symmetric algebraic decomposition; different weighting conventions could attribute differently. Do not call O a uniquely identified mediator or interpret C as a universal effect across all states.

## Six fixed reported quantities

1. `ACTIVE_ZERO|SELECTION_DRIFT` = pi_Z d_Z.
2. `ACTIVE_HALF|SELECTION_DRIFT` = pi_H d_H.
3. `HALF_MINUS_ZERO|SELECTION_DRIFT` = pi_H d_H - pi_Z d_Z.
4. `RECURRENCE_DECOMPOSITION|DIRECT_TARGET_LAW` = C. **Primary.**
5. `RECURRENCE_DECOMPOSITION|STATE_OCCUPANCY` = O.
6. `RECURRENCE_DECOMPOSITION|TOTAL` = C+O.

Report exact rational centers and certified numerical enclosures, plus percentage-point displays with the drift-per-update versus stationary-frequency units explicit. No confidence intervals, bootstrap draws or additional independent-study count. A strictly positive primary enclosure means the immediate channel supports the known positive total; a strictly negative one means it opposes the total; an enclosure containing zero is uncertified. No directional component prediction or dominance threshold is claimed after seeing the known total.

## Certification and exact identity checks

For a bounded exact reward f, use `span(f)=max(f)-min(f)` and `|pihat f-pi f| <= E span(f)`. Thus drift radii are E_Z span(d_Z) and E_H span(d_H); the drift-difference radius is their sum. With f=7(d_H-d_Z), the direct-component radius is `(E_H+E_Z) span(f)/2`. With g=7bar_d, the occupancy-component radius is `(E_H+E_Z) span(g)`. Use the tighter exact drift-difference propagation for the total: `7[E_H span(d_H)+E_Z span(d_Z)]`. Retain zero and uncertified results. Decimal bounds must be outward rounded; display rounding is not the certificate.

For the saved approximate weights define `r_q=pihat_q(P_q h-h)`. Check exactly that computed `C+O=7(S_H-S_Z)` and that `(C+O) - (pihat_H h-pihat_Z h) = 8(r_H-r_Z)`. This residual correction must not be silently called zero. Check the resulting total enclosure against the accepted061H-frequency contrast enclosure. No new stationary solve or full residual audit is needed. Verify the balance algebra on a constructed small example before new component evaluation.

## Finite execution, audit and deliverable

Use one deterministic local analysis, one CPU, at most two minutes and8MiB of new analysis outputs. No HPC production allocation. Produce six records in DECOMPOSITION.json, a256-row source-bound STATE_TERMS.json.gz table, exact identities/certification details in IDENTITIES.json, source hashes, a concise RESULTS_NOTE.md and an honest completion receipt under `outputs/stationary-flow062/`. Preserve errors and partial output; do not retry with a changed model or metric.

Check all six records with an independently written direct-sum calculation and the exact identities; use constructed fixtures for signs/error propagation. Do not reread full task histories or repeat the061raw row reconstruction. Retain the primary even if adverse or uncertified. Archive the small result/code/receipts onHPC and verify hashes. Decide once whether these new component results warrant a substantive manuscript change; do not automatically create a paper, release or another experiment. Keep the broader continuation backstop active and select a justified next finite decision when this one closes; follow any later user pause.
