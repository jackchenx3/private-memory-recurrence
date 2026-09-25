# Portable access to the fixed study-061 model

This additive post-v1.5.0 tool removes the original launcher's Slurm and private-layout dependencies. It imports the unchanged public `kernel.py`, `numerics.py` and `outcomes.py`; the original 13 scientific modules, scientific results and release PDFs remain unchanged. It adds no scientific parameter, result, paper or DOI.

**Validation boundary:** the interface has been tested with constructed small fixtures and the existing saved-output checker. The full 256-state regeneration command below has **not been run end to end through this new wrapper**. The archived study-061 production run and its independent focused audit remain the scientific evidence. These interface tests are not a new independent reproduction of that run.

## Requirements and commands

Use CPython 3.9 or later, without `-O` or `PYTHONOPTIMIZE`. The wrapper and mathematical operators use only the Python standard library; no scheduler, credentials, network access or third-party packages are required. Run from the repository, using a **new** output directory. Existing directories, including empty ones, are refused. Paths under scientific source/evidence are refused; `_rebuilt/` subdirectories or directories outside the repository are allowed.

Default: a constructed two-state chain with known stationary probability 2/3, three encoding fixtures and a constructed unavailable-output check. No production transition row or 256-state stationary solve is evaluated:

```bash
python -B tools/stationary061.py --output ../stationary061-smoke
```

Verify the four saved matrices/vectors, residual certificates and 14 archived mathematical quantities, using the existing public checker. This does not regenerate kernels or solve stationarity:

```bash
python -B tools/stationary061.py --mode verify-saved --output ../stationary061-saved-check
```

For a reader who explicitly chooses full scientific regeneration, the following command constructs the four frozen 256-state kernels, runs one fixed-precision solve per kernel, and writes the 14 outcomes using the original operators:

```bash
python -B tools/stationary061.py --mode regenerate --output ../stationary061-regenerated
```

This full command is supplied for use, with the validation limitation above. It has no switching-rate, recurrence, precision or population-size option. It does not import the original Slurm launcher, fake a scheduler environment or reuse an original production marker. A single worker is stopped after 30 minutes. Output is capped at 64 MiB, including reserved space for terminal receipts. The original run requested 4 GiB; this portable tool does not impose an OS-specific memory limit. The original 14-second runtime is not a performance promise for other computers.

## Outputs and failures

Every invocation authenticates 15 fixed source/checker files against hashes derived from the published v1.5.0 manifest. `REQUEST.json` records those bindings, the wrapper hash, mode, Python version and limits. `STATUS.json` reports worker exit and timeout status. `RESULT.json` states the mode and its scope. The full mode additionally saves matrices, solutions, vectors/certificates, exact outcomes, assessment, matrix checks and per-kernel intent receipts in the chosen directory. JSON and compressed JSON values are reusable; gzip/archive byte identity with the original package is not promised.

Numerical rejection is retained in the vector and outcome records and produces a failing exit code. No automatic retry, alternative precision, clipping of a negative component or outcome-dependent extension is performed. Other failures preserve partial outputs and a failure record when possible. After failure or timeout, inspect that directory; this wrapper has no resume mode and will refuse to overwrite it. A successful regenerated result would still concern only this specified mathematical model.

The source binding is `tools/stationary061_sources.json`. The existing scientific saved-output check remains `scripts/check_061_certificates.py`. Interface tests can be run with:

```bash
python -B tools/test_stationary061.py
```

These tests use a two-state analytic chain, controlled failures and output-path checks. They do not import the original `test_focused.py`, whose setup would reconstruct production rows. Full-model saved-output verification is a separate explicit mode. See `docs/PORTABLE_STATIONARY061_VALIDATION.json` for the exact validation performed when the tool was published.

## Scientific interpretation stays unchanged

Study 061 is a separate two-individual, one-bit supplied-memory model with ongoing symmetric policy switching at 1/16. Its small positive stationary H-frequency recurrence contrast coexists with adverse active-minus-neutral accuracy under ZERO and positive accuracy under HALF. Its 14 certified numerical quantities are distinct from the 15,284 statistical estimates for the larger finite-population studies. Numerical error enclosures are not confidence intervals; this model does not establish stationary behavior of the published 32-individual system, spontaneous memory origin or a general costly advantage. The unresolved 059/060 primaries and all prior adverse outcomes remain.

[Version 1.5.0 publication](https://doi.org/10.5281/zenodo.22950710) · [Evidence registry](../EVIDENCE_REGISTRY.json) · [Data availability](DATA_AVAILABILITY.md)
