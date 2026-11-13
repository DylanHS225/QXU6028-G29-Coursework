# Source and history record

The regular raw files are the original G29 files from the supplied QXU6028 student pack. The blind raw files are the original G29 blind set. Each set retains its teacher-supplied manifest. Only the assigned group data are included. The analysis verifies those manifest hashes before calculation.

`course_methods.py` is a byte-for-byte copy of `reproduce.py` from the available historical blind pipeline. SHA-256: `386844cce04180ad83e0fd65dbb6b76e6741158220913691afc9ce0b3c3749d7`. The original pipeline commit is `3304d6712795891e062c5bb2786b8455a4c407d8`.

The complete available history of that local blind repository is retained as `evidence/blind_pipeline_history.bundle`. It contains its actual commits; no earlier history has been reconstructed or invented. Inspect it with:

```sh
git clone evidence/blind_pipeline_history.bundle /tmp/qxu6028-historical-blind
git -C /tmp/qxu6028-historical-blind log --all --oneline
```

The preserved submitted artifacts are `evidence/blind_archive/blind_results.json`, `run_log.txt` and `pipeline_commit.txt`. The user confirmed this archive is the QMplus submission. Its run log records 24 September 2026 at 03:46:22 UTC. This establishes the recorded local run, not independent proof of a pre-release freeze or the time QMplus accepted the submission.

Earlier project records identify the following repositories and commits:

- L1: https://github.com/DylanHS225/QXU6028-G29-L1 at `005d012f6431f8747b035a8e8d079eb2c26989fc`.
- L2: https://github.com/DylanHS225/QXU6028-G29-L2 at `8bd0978d1c83aa35d38397fe632710cb351d9924`.

These are provenance references from the available chats, not a claim that their complete histories are embedded in the final-report repository. The final-report commits describe work performed during this report preparation, with an assistant author identity. They do not establish distributed student contributions. Group members must link their genuine contribution evidence in the statement.

Course sources checked for the report:

- QXU6028 Assessment Overview 2026–27.
- QXU6028 Virtual Lab Group Coursework Assessment Brief 2026–27, particularly the submission rules and Section 9 rubric.
- QXU6028 Coursework Report Guidance 2026–27, all 15 pages.
- QXU6028 Virtual Lab Practical Methods Guide 2026–27 and session slides.
- Chapter 3, particularly PDF pages 7–9 and 12, for the counting derivation and OFET transfer.
- Chapter 5 for the prescribed joint transport inversion and model-selection rule.
- Chapter 6 for the spatial inversion and diagnostics.
- Chapter 7 PDF pages 79 and 82 for OFET structure and transport context.

`evidence/announced_specification.pdf` preserves the provided specification screenshot stating max|m| ≤ 0.030. It was retrieved from the user's earlier L3 chat attachment. The figure has been visually checked.

The original assessment brief includes an approximate L1 example near 0.10 eV that is inconsistent with the ideal-cone calculation. The later Chapter 3 slides explicitly give 2.60 at 0.10 eV and approximately 2.00 at 0.073 eV. The report uses the computed values and cites those slides. This source discrepancy is not claimed as an AI error.

The two primary research sources are cited in the report. Their abstracts/full text were checked at https://arxiv.org/abs/cond-mat/9802133 and https://pmc.ncbi.nlm.nih.gov/articles/PMC4792947/ .
