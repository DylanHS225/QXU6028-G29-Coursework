# Model dependent electrical characterisation of a graphene wafer

QXU6028 Polymer Devices | Academic year 2026–27

Group number ____________________

Student names and IDs ____________________________________________________________

________________________________________________________________________________

## Context and question

Electrical characterisation combines a measurement with an extraction model. We analyse the supplied simulated graphene-on-sapphire wafer through carrier counting, joint Hall and sheet-resistance inversion, and spatial reconstruction. The decisions concern sensor calibration, material suitability and compliance with the announced 3.0% uniformity specification. Figure 1 identifies the material system and a polymer device to which these questions transfer. All calculations use the assigned regular dataset, with its original file hashes verified, and the practical procedure [1]. The regular wafer gives a carrier-count correction of 2.3232, a stable cone-model selection and a reconstructed maximum deviation of 2.7372%. These findings are conditional on the prescribed transport model and spatial resolution. The archived blind dataset provides a separate test of the analysis.

![Figure 1](assets/fig1_device_schematic.png)

*Figure 1. Conceptual graphene-on-sapphire structure and a bottom-gate, top-contact polymer OFET. The illustrated probe denotes electrical characterisation. Geometry and layer thicknesses are schematic. AI-generated illustration, checked against the lecture device structure [5].*

## L1 Carrier counting and mobility extraction

The two carrier counts use the same Fermi function f(E) and linear density of states cE. Their lower integration limits are 0 and E_F, respectively. We used N_A = 3.816 × 10¹⁵ cm⁻², k_B = 8.617333 × 10⁻⁵ eV K⁻¹, T = 300 K, c = 0.0371542 states atom⁻¹ eV⁻², and the 2.5 eV cutoff [1,2]. Trapezoidal integration used 20,001 points. The independent closed form is n_F = N_A c k_BT[E_F ln 2 + (π²/12)k_BT].

Figure 2 uses the supplied band-edge counts at the supplied sweep points and computed Fermi counts. At the exact metadata operating energy, 0.0878123 eV, n_B = 6.99353 × 10¹¹ cm⁻² and n_F = 3.01029 × 10¹¹ cm⁻². Their ratio is C = 2.32321. With the supplied sheet resistance 581.9396 Ω/□, μ = 1/(enρ) gives μ_B = 15,336 and μ_F = 35,629 cm² V⁻¹ s⁻¹. This is a change in the mobility inferred from a fixed resistance and a revised carrier count. The calculation establishes no change in microscopic scattering.

![Figure 2](figures/fig2_l1.png)

*Figure 2. Recomputed carrier populations and their ratio. Circles use the supplied sweep counts, lines evaluate the same models, and the star identifies the exact operating energy. The labelled crossings come from numerical root finding.*

At neutrality the integration limits coincide and C = 1. With positive doping, n_B accumulates occupied states below E_F, whereas n_F samples the population above E_F. At high E_F/k_BT, their leading dependences are quadratic and linear in E_F, respectively, explaining the increasing ratio. The crossings C = 2 and 4 occur at 0.072762 and 0.157347 eV. The numerical gate at 0.10 eV gives 2.59885, consistent with Chapter 3 [2]. Across the sweep, the closed-form discrepancy is below 1.19 × 10⁻⁶ relative, and doubling the integration grid changes either operating-point density by less than 1.92 × 10⁻⁷ relative. These quantify numerical consistency. The input file supplies no experimental uncertainty for c, T or ρ.

For a sensor with a stipulated response S proportional to 1/n, the revised prediction is 2.3232 times the band-edge prediction at this operating point. Calibration should therefore use the specified Fermi population and state the response law. The equal-mobility two-carrier relations used in L2 have their own population definition [2].

## L2 Density of states and Fermi level trajectory

The dataset contains 58 acquisition indices with three paired repeats at each index. We averaged repeats for the central estimate, located the signed Hall zero crossing between indices 28 and 29, and scaled the two measured channels independently. Each candidate curve was also normalised independently. The carrier integrals split at E_F, and the equal-mobility closure is R_H proportional to (p − n)/(p + n)² and R_s proportional to 1/(p + n). The cone and symmetric hard-gap V density of states follow the course definitions [1,3].

The model library uses 4,000 energy points over −2.5 to 2.5 eV, 400 candidate Fermi levels over −8 to 9 k_BT, and gaps from 0.50 to 8.00 k_BT in 0.25 k_BT increments. These grids match the prescribed generator. Each observed pair is matched to the nearest model point in the two-dimensional normalised channel space. A hard gap requires both r_gap < 0.85 r_cone and E_g ≥ k_BT [1].

![Figure 3](figures/fig3_l2.png)

*Figure 3. Independent channel overlays, assigned Fermi levels in acquisition order, and signed residuals. The comparison curve is the best hard-gap candidate. Shading is the pointwise 16–84% interval from 200 paired-repeat resamples.*

The cone RMS is 0.0139733. The best hard-gap candidate, E_g = 0.50 k_BT, has RMS 0.0179514, which is larger and fails the selection criterion. The central classification is therefore cone, with E_g/k_BT = 0. The assigned Fermi level rises overall from −0.08345 to 0.16658 eV, with local irregularities retained in measurement order (Figure 3c). Both channels constrain each assignment. The high-energy wings become less informative because changes in the normalised signals become small.

![Figure 4](figures/fig4_l2_checks.png)

*Figure 4. Raw signed Hall repeats, residual scan and selected-gap distribution. The dotted line is the required residual-improvement boundary. All 200 resamples selected the cone.*

Resampling independently selected one complete Hall/resistance pair from the three repeats at every index, using seed 20260923. Repeating the full normalisation and selection procedure 200 times gives gap median 0 and a 16–84% interval [0, 0] k_BT, with hard-gap selection fraction 0. The widest pointwise Fermi-level interval spans 0.02864 eV. The degenerate gap interval expresses stability within this candidate set and decision rule. Thermal smoothing at k_BT = 25.852 meV and finite model grids still permit unresolved sub-thermal structure. The residuals also reveal finite-grid effects and measurement scatter. The evidence supports sensing or conducting-interconnect use under the assumed transport model. A large thermally robust off-state for switching would require additional evidence of a sufficiently resolved gap and suitable contacts.

## L3 Spatial reconstruction and process decision

The forward matrix A has 128 measurements and 100 map elements, corresponding to a 10 × 10 grid over a region six probe pitches wide. Three scans provide the mean data vector and channel-wise repeat noise. The largest absolute row sum is 1.67 × 10⁻¹⁶, confirming insensitivity to a uniform offset. Its numerical rank is 92, so the spatial inverse has further unresolved modes. We imposed mean(m) = 0 and minimised ‖Am − d̄‖² + η‖Lm‖², with L formed from all 180 horizontal and vertical nearest-neighbour differences [1,4].

We tested η/η₀ = 0.01, 0.1, 1, 10 and 100, where η₀ = 0.01‖A‖₂²/‖L‖₂² = 0.00133099. The existing regular analysis selected 0.01η₀, giving η = 1.33099 × 10⁻⁵. This choice remains defensible from the new sensitivity calculation. Its residual norm, 1.765 × 10⁻⁶, is closest among the prescribed candidates to the repeat-estimated mean-noise norm, 1.209 × 10⁻⁶. At η₀ the residual is 1.101 × 10⁻⁴. The solver includes the guide's 10⁻⁹ diagonal stabilisation. Every resolution and noise test uses this same operator.

![Figure 5](figures/fig5_l3.png)

*Figure 5. Zero-mean relative Hall-conductivity deviations and forward consistency. Circles identify the positive and negative extrema. Pixel centres span −2.7 to 2.7 probe pitches. Row zero is displayed at the top, with positive y upward.*

The reconstruction has a broad spatial gradient with its largest positive deviation, +2.7372%, at (−1.5, +2.1) probe pitches. The negative extremum is −2.1417% at (−2.7, −2.7). These are reconstructed extrema. The negative feature meets the measurement boundary, where localisation and shape are especially sensitive to the limited field of view. The mean map is zero to numerical precision. L3 uses A and the scan data directly. L1 establishes extraction-model dependence, L2 checks the material model, and L3 tests spatial uniformity within its own forward model.

![Figure 6](figures/fig6_l3_checks.png)

*Figure 6. Regularisation sensitivity, singular spectrum, central impulse response and simulated noise maxima. The expected mean-noise norm uses repeat standard deviations divided by √3. The detection-limit procedure uses the repeat standard deviations specified in the guide.*

A zero-mean unit feature was injected at central and off-centre pixels, forward-projected, and reconstructed. Positive-lobe second moments give equivalent FWHM values of 1.6664 and 1.7258 probe pitches. We report the larger value, 1.7258 pitches, using the guide's fallback for a coarse half-maximum contour. This is a local resolution test, with possible deterioration near other boundaries. For detection, 500 independent Gaussian noise vectors used the channel-wise repeat standard deviations and seed 20260924. The 95th percentile of their maximum absolute map deviations is δ₉₅ = 1.7753 × 10⁻⁵, or 0.001775 percentage points. It is a noise-based detection measure conditional on the operator and estimated noise.

The announced specification requires a = max|m| ≤ 0.030. Here a = 0.0273723 and a + δ₉₅ = 0.0273900, giving a clear pass by the prescribed rule. The envelope is 2.7355–2.7390%, below 3.0%. All five regularisation candidates give reconstructed maxima below the threshold. This decision applies to the resolved zero-mean reconstruction. Smoothing, unobservable modes and boundary truncation limit claims about the finest or absolute physical variations. Increasing measurement noise would increase the detection limit approximately linearly at fixed operator and could move the decision toward the threshold.

## Transfer to a polymer field effect transistor

A printed polymer OFET, introduced in Chapter 7 (PDF page 79), makes the extraction problem concrete [5]. Chapter 3 derives μ = 1/(enρ) and explicitly connects mobility extraction to OFET disorder, traps and contacts (pages 9 and 12) [2]. L1 shows why an assumed carrier population changes inferred mobility. In an OFET, gate-induced charge and the mobile fraction require a gate-capacitance and trapping model. L2 motivates joint tests of transport assumptions. A disordered density of localised states and hopping transport can produce gate-voltage and temperature-dependent mobility [6]. Gaussian broadening and traps replace the ideal graphene cone as the relevant starting description. Contact voltage drops must also enter the extraction, since gated injection can strongly distort apparent field-effect mobility [7]. L3 transfers through film thickness, morphology and electrode uniformity, which influence channel current and device-to-device consistency. A transistor-specific sensitivity model is required to map these variations. The graphene correction factor and 3.0% wafer threshold apply to the present dataset, while OFET acceptance limits must follow its circuit requirements.

## Blind test and reproducibility

The confirmed submitted blind archive contains the result JSON, run log and commit 3304d6712795891e062c5bb2786b8455a4c407d8. Its logged run on 24 September 2026 at 03:46 UTC gives C = 2.26442, n_F = 3.18560 × 10¹¹ cm⁻² and μ_F = 33,804 cm² V⁻¹ s⁻¹. The 43-index series selects a hard gap of 3.25 k_BT. The blind map maximum is 3.66225%, with a 0.027443 percentage-point detection limit, giving a clear fail. Recomputing the archived method from its raw data reproduces the archived numerical fields. The retained log establishes the recorded local run. QMplus holds the submission timestamp. The new figures and report are subsequent analysis, with their own code and evidence records.

The accompanying reproduce.py validates input hashes and regenerates the regular JSON, numerical diagnostics and all data figures. AI assistance covered code, analysis checks, drafting and the conceptual illustration. The usage log and error ledger document a contact-topology error and an uncertainty-interpretation correction, with evidence. Group attribution and signatures are provided separately for completion by the members.

## Conclusion

Changing the prescribed carrier count increases extracted mobility by a factor of 2.3232 at fixed resistance. Joint transport inversion consistently favours the cone within the tested models and thermal resolution. The regular wafer passes the announced criterion with a reconstructed maximum of 2.7372%, subject to a spatial resolution of about 1.73 probe pitches and the stated noise assumptions. The blind data produce a distinct gapped-material decision and fail the uniformity criterion. Across the phases, the applicable forward model determines which device or process conclusions the measurements can support.

## Critical self assessment

Our first weakness is that L2 uncertainty samples only three observed repeats and a fixed model library. All resamples choose the cone, producing a zero-width gap interval, while integration discretisation, systematic channel-calibration errors and untested density-of-states shapes remain outside that interval. A remedy is to acquire more independent repeats, examine calibrated raw-channel noise and repeat the inference with a controlled grid-refinement study. Model comparisons with broadened or disordered states would test whether the cone remains sufficient. These changes should be reported alongside the prescribed baseline so their effects are traceable.

Our second weakness is the spatial coverage of L3 validation. Two impulse positions and a noise-only simulation do not fully quantify boundary bias or recovery of narrow, overlapping defects. The negative extremum lies on the map boundary, making this limitation consequential. Additional injections across the grid, with varied widths and amplitudes, would estimate position-dependent resolution and missed-feature risk. More repeats would improve the noise estimate, while independent probe placements would test the unresolved modes. The current pass decision therefore remains conditional on the reconstructed, resolved map and the stated forward operator.

## References

[1] Sun, Y. (2026). QXU6028 Virtual Lab Practical Methods Guide 2026–27, pp. 3–14. Queen Mary Engineering School.

[2] Sun, Y. (2026). QXU6028 Chapter 3 Carrier Counting and Mobility, PDF pp. 4, 6–12. Course lecture slides.

[3] Sun, Y. (2026). QXU6028 Chapter 5 Reading the DoS from Transport. Course lecture slides.

[4] Sun, Y. (2026). QXU6028 Chapter 6 Probe Measurements and Uniformity, PDF pp. 5–12. Course lecture slides.

[5] Sun, Y. (2026). QXU6028 Chapter 7 Display Technologies and Polymer Electronics, PDF pp. 79 and 82. Course lecture slides.

[6] Vissenberg, M. C. J. M. and Matters, M. (1998). Theory of the field-effect mobility in amorphous organic transistors. Physical Review B, 57, 12964–12967. https://doi.org/10.1103/PhysRevB.57.12964

[7] Bittle, E. G., Basham, J. I., Jackson, T. N., Jurchescu, O. D. and Gundlach, D. J. (2016). Mobility overestimation due to gated contacts in organic field-effect transistors. Nature Communications, 7, 10908. https://doi.org/10.1038/ncomms10908
