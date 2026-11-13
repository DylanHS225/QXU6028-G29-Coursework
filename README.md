# QXU6028 G29 coursework analysis

This repository supports assessment of the G29 virtual-lab coursework. It reproduces the L1–L3 results and data figures for the regular dataset and verifies the archived blind-test results.

## Reproduction

From the repository root, install the pinned dependencies and run the analysis. The workflow was verified with Python 3.14.4.

```sh
python -m pip install -r requirements.txt
python reproduce.py
```

The script checks the supplied data against their SHA-256 manifests and generates the following outputs.

| Output | Contents |
| --- | --- |
| `results.json` | Regular G29 results in the supplied schema, including the Git commit used for the run |
| `figures/` | Report Figures 2–6 in PNG and PDF |
| `evidence/numerical_summary.json` | Numerical values cited in the report |
| `evidence/l2_fit.csv`, `evidence/l2_bootstrap.csv` | L2 fits and resampling diagnostics |
| `evidence/l3_regularisation.csv`, `evidence/l3_diagnostics.npz` | L3 sensitivity, resolution and noise diagnostics |
| `evidence/physics_checks.json`, `evidence/blind_reproduction_check.json` | Unit, sign and schema checks and comparison with the original blind-test results |
| `run_log.txt`, `evidence/runtime.json` | Execution log, dependency versions and random seeds |

The plots use Arial when available and DejaVu Sans otherwise. The numerical results are independent of the font.

## Data and evidence

- `data/regular_G29/` and `data/blind_G29/` contain the supplied G29 inputs, manifests and output templates.
- `evidence/blind_archive/` preserves the original blind result, run log and pipeline commit. `evidence/blind_pipeline_history.bundle` preserves the blind pipeline's Git history.
- `evidence/announced_specification.pdf` records the 3.0% wafer uniformity criterion.
- `assets/fig1_device_schematic.png` is the illustration used in report Figure 1. Its prompts and the AI correction evidence are in `assets/` and `evidence/ai_corrections/`.
- [PROVENANCE.md](PROVENANCE.md) identifies the earlier L1, L2 and blind-test code versions.

The final report, signed contribution statement and AI records are submitted through QMplus.
