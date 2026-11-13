# AI error ledger

This record distinguishes an observed physics error from a methodological interpretation error. Both occurred during preparation of this final report and were corrected during review. No additional historical L1–L3 errors have been verified. Preventive checks below are not claimed as past failures or as two additional physics errors.

## E01 Contact topology in the generated schematic

**Tool and stage:** OpenAI image generation, first conceptual device illustration.

**Observed error:** The initial graphene panel joined the nominally separate gold contact pads with a continuous metallic perimeter. This would provide a conducting bypass between contacts and would not represent independent terminals for a transport measurement through the graphene.

**Detection:** Visual inspection of the generated topology revealed the connected gold rails. The submitted diagram must represent separated terminals; a metallic bypass changes the electrical circuit, rather than merely the appearance of the device.

**Correction:** The revision prompt explicitly required removing every inter-pad gold rail and leaving four isolated contact pads. The regenerated panel shows separated pads on the graphene. The source and drain in the polymer device remain separate, with the gate insulated by the dielectric.

**Evidence:** `evidence/ai_corrections/schematic_initial.png` is the retained first image. `assets/schematic_prompt.txt` and `assets/schematic_revision_prompt.txt` preserve both prompts. `assets/fig1_device_schematic.png` is the corrected illustration used in Figure 1. These files establish the before/after change. The picture is conceptual and does not specify an experimental wiring circuit or establish numerical measurement results.

**Verification:** Inspect the four corners of the graphene panel in the final asset: the pads are not connected by a metal rim. The caption identifies the image as AI-generated and schematic. The correction changes no calculated data.

## E02 Overstating what the repeat interval excludes

**Tool and stage:** Codex-assisted report drafting, critical self-assessment.

**Observed error:** The initial wording said that “normalisation uncertainty” remained outside the repeat-resampling interval. This statement was too broad: each resampled set is independently normalised before fitting, so the interval already propagates changes in the normalisation scales caused by selecting the observed repeats.

**Detection:** Code-to-text comparison of `analyse_l2`, `fit_l2` and `normalise` shows that normalisation is recalculated inside every resample. The old sentence contradicted that calculation and overstated the missing uncertainty.

**Correction:** The final self-assessment identifies unmodelled systematic channel-calibration errors, integration discretisation and alternative density-of-states shapes. Constant multiplicative channel factors cancel in the independent normalisation; offsets or index-dependent calibration errors need separate modelling. Repeat-induced variation in the scales is already included.

**Evidence:** The exact sentence before and after correction is retained in `evidence/ai_corrections/uncertainty_wording_before.txt` and `uncertainty_wording_after.txt`. The implemented resampling loop and the final report are supplied in the repository.

**Verification:** Every call to `fit_l2` calls `normalise` on its own sampled input. No numerical result was changed by this wording correction. This is an uncertainty-interpretation error, not an additional demonstrated device-physics or units error; its rubric classification is for the marker.

## Preventive physics checks

These are explicit validation examples, not accounts of mistakes that occurred.

1. **Mobility units:** Inserting a density in cm⁻² into `1/(e n rho)` already returns mobility in cm² V⁻¹ s⁻¹. Multiplying that result by another 10⁴ would be a units error. The script independently converts density to m⁻², calculates SI mobility and converts the result back. Both routes give approximately 35,629.02 cm² V⁻¹ s⁻¹.
2. **Hall sign:** Replacing signed Hall data with its absolute value would remove the observed neutrality crossing and lose the electron/hole imbalance information in `(p−n)/(p+n)²`. The script checks that positive and negative observations are present and that independent normalisation preserves every sign. The observed mean-data crossing is between acquisition indices 28 and 29.

The reproducible outcomes are saved in `evidence/physics_checks.json`. They demonstrate current safeguards, not a fabricated history of failures.
