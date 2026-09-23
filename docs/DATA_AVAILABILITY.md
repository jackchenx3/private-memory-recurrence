# Data availability and reproducibility boundary

The public release includes complete block-level numerical grids, frozen bootstrap indices, per-group endpoint-fate counts, configurations and seed rosters for studies 045–055. `scripts/reproduce_statistics.py` recomputes all reported means and intervals, including unfavorable and unresolved contrasts. `scripts/rebuild_figures.py` regenerates the eleven figures from these summaries.

Candidate-by-candidate population trajectories, full random-number tapes and site execution logs are retained in the original project archive. These multi-gigabyte files are not part of this compact release. No public download URL for the raw archive is implied. A reader can request a separate raw-data deposit through the GitHub repository's issue tracker, but availability of this compact release is not a promise that every raw file is already publicly hosted.

The source directories contain archived scientific operators and analysis modules. Some depend on omitted input tapes and predecessor layouts. They are inspectable source, not a claim of one-command full simulation reproduction. The standalone public scripts require only the included data.

Prior independent computational reconstruction receipts are included as provenance. For 055, all 1,152 preparations and 3,456 transfers were checked against the saved inputs and states before publication preparation. That check generated no new random numbers or scientific paths. The release-stage saved-table recomputation is a different, narrower check.

Administrative filesystem paths are normalized in exported text. The export map records the original hash, published hash and transformation. Normalizing a source path is not a scientific result modification. Original records remain unchanged outside this release.
