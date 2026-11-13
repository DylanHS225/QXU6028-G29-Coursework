# Data and code provenance

## Regular and blind data

`data/regular_G29/` contains the original G29 regular dataset from the QXU6028 student pack. `data/blind_G29/` contains the original G29 blind dataset. Both directories retain the supplied manifests. The analysis verifies all listed SHA-256 hashes before calculation.

## Earlier analysis versions

- [L1 carrier counting](https://github.com/DylanHS225/QXU6028-G29-L1/commit/005d012f6431f8747b035a8e8d079eb2c26989fc), commit `005d012f6431f8747b035a8e8d079eb2c26989fc`.
- [L2 density-of-states analysis](https://github.com/DylanHS225/QXU6028-G29-L2/commit/8bd0978d1c83aa35d38397fe632710cb351d9924), commit `8bd0978d1c83aa35d38397fe632710cb351d9924`.

The `main` branch records the integrated analysis used for the final report.

## Blind-test record

The original blind pipeline commit was `3304d6712795891e062c5bb2786b8455a4c407d8`. The helper `course_methods.py` is a byte-for-byte copy of that commit's `reproduce.py`.

The archived `blind_results.json`, `run_log.txt` and `pipeline_commit.txt` are in `evidence/blind_archive/`. The run log records 24 September 2026 at 03:46:22 UTC. QMplus holds the official upload timestamp. The final reproduction script compares a fresh calculation with the archived results.

The original blind Git history is preserved in `evidence/blind_pipeline_history.bundle` and can be inspected with Git.

```sh
git clone evidence/blind_pipeline_history.bundle blind-history
git -C blind-history log --all --oneline
```

## Wafer specification and illustration

`evidence/announced_specification.pdf` records the Session 3 acceptance criterion, maximum absolute reconstructed deviation of 0.030.

`assets/` contains the submitted device schematic and its two generation prompts. `evidence/ai_corrections/` contains the first illustration and the before-and-after L2 wording referenced in the AI Error Ledger.
