# Data availability and reproducibility boundary

The public release includes complete block-level numerical grids, frozen bootstrap indices, per-group endpoint-fate counts, configurations and seed rosters for studies 045–057. `scripts/reproduce_statistics.py` recomputes all reported means and intervals, including unfavorable and unresolved contrasts. `scripts/rebuild_figures.py` regenerates the thirteen figures from these summaries.

Candidate-by-candidate population trajectories, full random-number tapes and site execution logs are retained in the original project archive. These multi-gigabyte files are not part of this compact release. No public download URL for the raw archive is implied. A reader can request a separate raw-data deposit through the GitHub repository's issue tracker, but availability of this compact release is not a promise that every raw file is already publicly hosted.

The source directories contain archived scientific operators and analysis modules. Some depend on omitted input tapes and predecessor layouts. They are inspectable source, not a claim of one-command full simulation reproduction. The standalone public scripts require only the included data.

Prior independent computational reconstruction receipts are included as provenance. For 055, all 1,152 preparations and 3,456 transfers were checked against the saved inputs and states before publication preparation. That check generated no new random numbers or scientific paths. The release-stage saved-table recomputation is a different, narrower check.

Administrative filesystem paths are normalized in exported text. The export map records the original hash, published hash and transformation. Normalizing a source path is not a scientific result modification. Original records remain unchanged outside this release.

Version 1.1 adds 324 estimates from studies 056/057, for 15,053 total. Native estimate tables retain paired and block signs. Compressed `.jsonl.gz` tables contain all recorded founder fates, declines, negative outcomes, path metrics and transmission/accuracy disagreements. The source map documents lossless gzip and normalized summary/JSON Lines projections. Study 056 reuses the 055 seed roster; 057 publishes its 3,193 new seed records and collision-check provenance. These are not new raw-trajectory deposits.

For 056, the supervisor independently reconstructed all 162 estimates and checked 96 raw paths in prospectively selected block 0 (494,592 recorded scores). For 057, that scope was all 162 estimates, 232 stage paths in block 0 and 1,195,264 recorded scores. These focused checks do not replace complete raw replay. The producer audit uses some production modules; the supervisor arithmetic script imports none. All independent-cohort evidence comes from 057 itself, not from checks on its saved records.
