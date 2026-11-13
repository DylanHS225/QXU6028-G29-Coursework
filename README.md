# QXU6028 G29 coursework analysis

This repository contains the analysis for the G29 virtual-lab coursework. It reproduces the regular L1–L3 results and data figures and checks the archived blind-test outputs.

## Reproduce the results

From the repository root, install the dependencies and run the analysis. Python 3.14.4 was used to verify the pinned dependencies.

```sh
python -m pip install -r requirements.txt
python reproduce.py
```

The script checks the supplied data hashes, performs the analysis and writes:

- `results.json` for the regular G29 dataset, with the commit used for the run.
- `figures/` with report Figures 2–6 in PNG and PDF format.
- `evidence/` with the numerical summary, fit and reconstruction diagnostics, physics checks and blind-test comparison.
- `run_log.txt` with the execution record.

The script uses fixed seeds for the L2 resampling and L3 noise simulations. The report plots use Arial when it is installed. The fallback font changes the typography only. Figure 1 is the retained device illustration in `assets/fig1_device_schematic.png`.

## Inputs and records

- `data/regular_G29/` and `data/blind_G29/` contain the supplied G29 inputs and manifests.
- `evidence/blind_archive/` contains the original blind results, run log and pipeline commit. The reproduction command reads these records and writes its comparison separately.
- `evidence/blind_pipeline_history.bundle` preserves the available original blind pipeline history. Run `git clone evidence/blind_pipeline_history.bundle blind-history` to inspect it.
- `PROVENANCE.md` links to the separate L1 and L2 repositories and identifies the earlier commits. The history on `main` covers the final integrated analysis and report preparation.
- `assets/` and `evidence/ai_corrections/` retain the prompts and before-and-after records. The final report, signed contribution statement and AI records are supplied through QMplus.
