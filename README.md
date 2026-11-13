# QXU6028 G29 final report analysis

This package regenerates the regular-data numerical results and all five data figures in the accompanying report. Figure 1 is a retained, disclosed AI-generated conceptual illustration; both prompts and the corrected asset are supplied. It is not a simulated data result.

## Reproduce the analysis

Use Python 3.11 or newer. The tested interpreter was Python 3.14.4 with the exact packages in `requirements.txt`. No SciPy, proprietary software, network data source or hidden truth is required.

```sh
python -m pip install -r requirements.txt
python reproduce.py
```

After dependencies are installed, the second command performs the complete numerical reproduction. It validates raw-input hashes, calculates L1–L3 results, runs 200 paired L2 resamples and 500 L3 noise reconstructions, renders Figures 2–6, and checks the historical blind archive against a new calculation. Seeds are 20260923 for L2 and 20260924 for L3. All paths are relative to the script, so the working directory is immaterial. Runtime depends on the machine.

Outputs include:

- `results.json`: regular G29 result in the supplied schema, including the source commit.
- `figures/fig2_l1` to `figures/fig6_l3_checks`: PNG and vector PDF versions.
- `evidence/numerical_summary.json`: quantities cited in the report and figure captions.
- `evidence/l2_fit.csv`, `l2_bootstrap.csv`, `l3_regularisation.csv`, `l3_diagnostics.npz`: inspectable fits, resampling and spatial diagnostics.
- `evidence/blind_reproduction_check.json`: comparisons of numerical values, features and decisions with the original submission.
- `evidence/physics_checks.json`, `runtime.json` and `run_log.txt`: preventive unit/sign/schema checks, environment and execution record.

The program preserves the historical blind archive. It does not replace an earlier QMplus submission with a later run.

## Fresh checkout

The delivered archive contains `repository.bundle` beside this package. To recover the full final-report source history and reproduce without pre-existing outputs:

```sh
git clone repository.bundle fresh_report
cd fresh_report
python reproduce.py
```

Install dependencies first if needed. Generated outputs are deliberately untracked. The delivered snapshot includes `source_commit.txt` as a fallback for execution without Git; a checkout obtains the actual HEAD commit directly. No absolute original-machine data path is needed.

## Read the report and process records

The Word and PDF reports are supplied beside this package. `report.md` is the editable source text. A conservative whitespace count, including captions and references, is below 2,500 words. Transfer is below 200 words and the self-assessment is within 150–200 words. The figures and numbers are generated from the raw data; the report prose is a reviewed static interpretation of those outputs.

Required companion records are `AI_error_ledger.md`, `AI_usage_log.md`, `contribution_statement.md` and `PROVENANCE.md`. The self-assessment is in the main report. The ledger contains one verified contact-topology physics error and one verified uncertainty-interpretation error. Two additional physics safeguards are clearly labelled preventive checks and are not claimed as historical failures. The rubric's usual expectation of two genuine physics errors is not asserted as satisfied.

## Items for the group to complete

Fill in the blank group names and IDs in the report. Review the AI disclosures and add any use outside the available records. Complete actual contribution evidence and obtain all members' signatures. Provide a repository address accessible to the marker, including any earlier histories needed to substantiate the members' contributions. The local report history cannot establish distributed work retrospectively.

The original data manifests identify G29 and remain unchanged, even though the report's group-information fields are intentionally blank. Hidden-truth automated scores and individual contribution scores cannot be inferred from the available files.
