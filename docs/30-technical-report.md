# ZenithSync Assay Planner
## Control-aware finite-well design with frozen public-cohort confirmation

Technical report candidate, 6 October 2026 (Pacific). Local research artifact; not submitted or externally peer reviewed. Team: ZenithSync. Shengbo Jiang is the sole member and main contributor. Category: Tool & Platform. Designated reviewer: Shengbo Jiang (contributor self-review; completion not yet recorded).

We study a concrete assay question: after measuring a vehicle control and the two extreme drug doses, which additional wells should a researcher purchase to reconstruct a single-agent organoid response curve? The system accounts for the dependence introduced when several responses share a measured reference control. It uses a fixed Gaussian-process model and exact finite-pool variance minimization with verified symmetry reduction.

A model selected on a development study was frozen before evaluating a distinct public organoid cohort. In 6,496 paired drug contexts from 148 organoid samples and 100 source patient IDs, exact selection reduced mean squared log-response error by 32.82% relative to random selection under the same GP. The patient-bootstrap interval was 31.34% to 34.21%. The stronger greedy variance-reduction baseline nearly matched exact selection: the incremental MSE reduction was 0.66%.

A separate prespecified comparison used 20-25% fewer purchased wells than its random reference and achieved an aggregate MSE ratio of 0.89185, with 95% interval 0.86430 to 0.92127. This is retrospective evidence under an isolated-context well-count convention. It is not a prospective laboratory saving, clinical result or competition ranking guarantee. Established GP and design mathematics are credited rather than presented as new theory.

The accompanying repository preserves negative development results, pre-outcome freezes, the first failed evaluator attempt and its serialization-only repair, complete results, independent computational checks and a local browser/CLI workflow. The current test suite passes 127 tests with warnings treated as errors.

---PAGE---
# 1. Research question and intended use

The intended user is an assay researcher who has an existing single-agent dose design and a limited budget for additional measurements. The supported decision is the selection of treatment and vehicle-control wells from that finite design. The objective is reconstruction of raw log-signal contrasts over the designed positive doses. It does not optimize patient treatment, clinical benefit, drug discovery hit rate or a toxicity threshold.

A curve begins with three charged measurements: one reference control, the lowest treatment dose and the highest treatment dose. Candidate actions are the remaining recorded treatment wells and negative controls. Every purchased well costs one assay unit, including controls. The researcher supplies the feasible set; the implementation does not validate liquid handling, plate layout, solvent tolerances or biological suitability.

A reference control is not noise-free. Reusing it in several log contrasts creates correlation between their measurement errors. Consequently, another control can improve the entire curve estimate. The model represents that dependence jointly instead of assigning unrelated errors to already normalized responses.

The central hypothesis is deliberately narrow: with a fixed development model, exact subset selection improves held-out technical-plate reconstruction relative to random purchasing at the same budget. A second hypothesis tests a fixed reduction in purchased wells at a specified noninferiority margin. Neither hypothesis requires claiming a new GP or a learned stopping rule.

Organoids provide the empirical evidence in this report. They are not interchangeable with perfused organ-on-a-chip systems or neural chips. The original broader platform concept remains a future transfer question. The current interface labels its research scope, returns model-conditional uncertainty and rejects inputs outside its contract.

---PAGE---
# 2. Prior art and contribution

Integrated posterior variance has long been an experimental-design objective, including non-greedy joint optimization [3]. GP modeling of pharmacological response uncertainty is also established [4], as is Bayesian dose-response modeling for cancer drug studies [5]. Active learning for anticancer screening has compared multiple acquisition policies across cell-line/drug tasks [6]. These precedents rule out a generic claim that combining a GP, uncertainty and assay selection is itself a new algorithm.

The tasks differ. This study purchases individual controls and treatment wells within a curve; the cited screening work selects cell-line/drug response labels. Its greedy policy exploits predicted drug response, whereas our greedy comparator maximizes incremental variance reduction. The names alone do not make those policies equivalent.

Recent robust GP active-learning work addresses uncertain target distributions [7], and robust Bayesian active learning addresses model misspecification [8]. We do not implement those guarantees or claim to outperform those methods. Our finite target weights and fixed prior are explicit limitations. This is a focused precedent audit, not an exhaustive systematic review or reproduction of every cited algorithm.

The defensible contribution is an auditable empirical study and tool: control-aware modeling, exact small-pool reference designs, public-study transfer with a frozen protocol, patient-level inference, honest control costs, and retained failures. Exact optimization provides a computational reference; its small advantage over greedy is reported alongside the larger random-policy contrast.

The study therefore offers evidence for a bounded measurement-design improvement. It does not establish broad state-of-the-art prediction, major new theory or guaranteed innovation points from judges. Document 29 contains the fuller claim audit and source-access boundaries.

---PAGE---
# 3. Development data and negative evidence

Development used the public Farin organoid-stroma drug-sensitivity source [1], with its source file pinned by SHA-256. The raw table contains 6,729 measurements, 280 curve contexts and 29 organoid identifiers. The adapter retains 235 author-excluded measurements and separately quarantines four ambiguous curves containing 99 rows; 6,398 rows remain eligible under the recorded rules.

For a strict replay, 136 curves from 28 organoid identifiers have a complete eight-dose by three-replicate rectangle. Replicate labels one and two form the selectable pool of sixteen wells, and label three supplies an audit of eight wells. The source does not establish plate/run identity or a verified patient map. These labels therefore support within-curve retrospective development, not a claim of independent experimental plates or patients.

Hyperparameters were selected by leaving one organoid identifier out and tuning only on other identifiers' pool observations. Each covariance variant considered 54 configurations. All folds selected amplitude 1, length 0.5, raw-log noise standard deviation 0.3 and mean slope 2. Audit measurements did not tune this prior.

At full budget, development MSE was 0.362401 for random linear interpolation, 0.336649 for random joint GP, 0.334610 for greedy joint GP and 0.330169 for exact joint GP. Relevant paired identifier-bootstrap intervals included zero. Development did not demonstrate superiority. Earlier liver-chip exploration likewise remains in the repository rather than being replaced by the later positive result.

The development study supplied parameters and implementation checks. The independent confirmation tested the registered hypothesis without tuning the model on confirmation outcomes. Keeping the negative result is essential: selecting only a favorable cohort or budget would make the scientific claim substantially weaker.

---PAGE---
# 4. Independent cohort and admission

The confirmation source is the Kryeziu public dataset, version 3 [2]. Data S4 supplies raw well measurements; Data S1 supplies explicit PDO sample-to-patient identifiers. Only design fields and the relevant identity fields were projected before the protocol freeze. Mutation and response fields were not used to choose the model or claim.

The raw workbook contains 191,030 rows: 157,810 single-agent measurements, 24,414 combinations, 5,474 negative controls and 3,332 positive controls. Single-agent contexts were paired across p1 and p2 using sample, run, library, drug and identical numeric dose support. Each admitted pair required at least four doses and at least two DMSO negative controls. Combinations and positive controls do not enter the selectable pool.

Structural admission yielded 9,231 paired contexts across 209 samples. Explicit patient mapping reduced the eligible confirmation set to 6,524 contexts from 148 samples and 100 patient IDs. The frozen rule then excluded 28 contexts per orientation for any nonpositive or nonfinite candidate/audit signal. The primary analysis contains 6,496 contexts. All excluded source rows and reasons are preserved.

Controls are recognized from source role and DMSO identity, including records with missing or inconsistent concentration annotations. Zero drug dose in our representation does not mean zero vehicle concentration. The source article describes seven lib2 concentrations, but the raw file commonly has eight positive dose values. We retain the pinned raw values and flag this unresolved discrepancy rather than silently deleting a dose.

This is transfer across distinct public studies. Deidentified identifiers cannot prove cross-study patient non-overlap. Within confirmation, explicit patient grouping prevents treating multiple samples as unrelated patients. Parallel technical plates do not establish clinical or multi-institutional generalization.

---PAGE---
# 5. Protocol freeze and leakage controls

The hypothesis, admission rules, patient hierarchy, model parameters, primary orientation and success criteria were frozen at 2026-10-07 03:38:30 UTC. The primary direction is p1 pool to p2 audit. The reverse direction is a prespecified sensitivity, not an alternative primary endpoint. No cohort outcome was used to retune the prior.

The outcome-free preflight covered 13,048 context/orientation pairs and eleven geometries. Selection plans and prediction coefficients were generated from dose/control geometry and the fixed model, with hashes retained before evaluation. Unblinding began at 03:48:17 UTC. The first evaluator attempt failed before calculating results because equivalent JSON lists and Python tuples were compared directly.

The original program, preflight manifest and error trace remain preserved. A documented amendment canonicalized serialization and verified the old/new manifest chain. It changed neither selection plans, prediction coefficients nor scientific scoring rules. The subsequent run was the first completed response evaluation. This repair is reported rather than hidden behind a successful final command.

The evaluator only supplies purchased signals to each predictor. Tests poison unpurchased values to detect leakage, compare batched prediction against direct Gaussian conditioning, verify shared initial information and check full-budget equivalence. No residual, activity or drug-sensitivity score filter was introduced after seeing outcomes.

The validity filter does inspect all relevant outcomes for finite positive values, because the endpoint requires a log transformation. It is a registered complete-context feasibility filter, not selective removal of poor predictions. Its exclusions are visible. The first-run markers use exclusive creation; reruns must preserve the original evidence and use a separate destination.

---PAGE---
# 6. Statistical model and endpoint

Let Y_i be the natural logarithm of a positive raw signal, modeled as a + f(x_i) + e_i. The plate intercept is a. Independent raw-log errors e_i have variance s squared. The drug-response function is pinned at f(0)=0, with prior mean -2x. The coordinate is log(1+d/d_min) divided by its maximum over the context, so the maximum designed dose has x=1.

The prior covariance is a Matern 5/2 kernel conditioned on its value at zero. If r is absolute coordinate distance divided by length, the unpinned correlation is (1+sqrt(5)r+5r squared/3) exp(-sqrt(5)r). The pinned covariance subtracts the product of the correlations to zero and multiplies by amplitude squared. The frozen amplitude is 1, length 0.5 and s=0.3.

Using a measured reference control Y_0 gives observations Z_i=Y_i-Y_0. Their noise covariance is s squared times (I+11-transpose): diagonal 2s squared and off-diagonal s squared. An independent-noise ablation keeps the same marginal variance but sets off-diagonals to zero. Additional measured controls inform the shared reference error, even though their latent treatment effect is fixed to zero.

The audit endpoint at a dose is log raw treatment RLU minus the mean log RLU of all negative controls on the separate audit plate. It is not the source authors' background-corrected normalized viability, DSS, IC50 or a clinical treatment effect. Audit noise is independent of purchased-plate noise under the model; audit dose errors share their own control mean.

A fresh audit contrast has conditional variance equal to latent variance plus s squared times (1+1/m), where m is its number of controls. The displayed 90% interval uses a normal quantile of 1.64485. Equal raw-log variance, independent plates and the GP prior are assumptions tested only indirectly by the reported diagnostics.

---PAGE---
# 7. Exact finite design and computation

Partition a conditional joint Gaussian into latent targets and available observations. For a selected observation subset A, conditioning reduces covariance by C[:,A] times inverse(C[A,A]) times C[A,:]. The target objective is the mean of the latent diagonal entries at the designed positive doses. The variance reduction is nonnegative in exact arithmetic; stable linear solves are used instead of explicit matrix inversion.

The fixed-cardinality optimizer examines every relevant subset class. Distinct budgets may have non-nested optimal sets, so each budget represents a separate campaign. These results must not be interpreted as one sequential trajectory whose earlier purchases can be undone. Greedy selection, by contrast, builds a nested sequence using the best one-step variance decrease.

Exchangeable controls can reduce computation. If swapping coordinates preserves the complete conditional Gaussian mean and covariance, selecting any k controls in the group gives an identical variance objective. The implementation checks generating transpositions rather than inferring exchangeability from labels. One representative per group count then suffices; singleton groups preserve every treatment choice.

Across 22 model/geometry combinations, 13,408 representatives cover 2,113,536 subsets. The claimed reduction concerns enumeration count, not measured wall-clock speed. Tests compare reduced enumeration with brute force and reject falsely declared symmetries. Exactness is restricted to a fixed Gaussian objective, unit costs, unrestricted subsets and numerical tolerance.

With frozen hyperparameters, posterior covariance depends on measured locations, not measured values. The batch design is therefore static conditional on geometry and the measured set. Current predictions do use values. This is not response-adaptive active learning or an optimal stopping policy. Lower model variance alone does not guarantee lower realized biological error; the separate audit supplies that empirical test.

---PAGE---
# 8. Baselines and fair comparisons

Seven methods are evaluated: exact joint GP, greedy joint GP, exact diagonal GP, random joint GP, random diagonal GP, random linear interpolation and random PCHIP interpolation. All begin with the same three charged seed wells. All respect the same finite candidate pool and use only purchased observations. Random policies average NumPy default_rng seeds 0 through 19.

Exact versus random joint GP isolates purchasing policy under the same estimator and is the frozen primary contrast. Exact versus greedy joint GP compares optimizers of the same variance objective. Joint versus diagonal exact changes both estimation and chosen subset; it cannot isolate acquisition alone. Random joint versus random diagonal more directly compares covariance handling under the same random purchasing policy.

Linear and PCHIP methods provide simple non-GP reconstruction alternatives. Their performance is evaluated rather than assumed inferior. All methods are compared against the same separate-plate log-response endpoint. Computational random seeds are averaged before biological grouping; twenty seeds do not create twenty independent experiments.

The comparison set is meaningful for this task, but it does not cover every dose-response model or experimental-design algorithm. Cited prior-art models were not reproduced merely by including a generic GP. No claim of superiority over the whole literature is supported. A new method developed after this confirmation would require another untouched cohort for a new confirmatory claim.

The strongest included comparator, greedy joint GP, nearly matches exact design. Both the absolute result table and the incremental 0.66% MSE reduction belong in any presentation. A headline containing only the 32.82% random-policy improvement would otherwise invite an exaggerated interpretation of algorithmic novelty.

---PAGE---
# 9. Estimand and patient-level inference

For each context, method and budget, squared prediction errors are averaged over its audit doses. All integer budgets from three through the full pool size receive equal weight within that context. Contexts are averaged within a sample, samples within a patient, and patients equally. The primary estimand therefore targets average patient-grouped reconstruction performance across the registered finite budget range.

The hierarchy matters. A patient with more samples or drug contexts does not receive proportionally more total weight. Different pool sizes yield different numbers of budgets, but each context first averages its own budget range. Random seeds are averaged before this hierarchy. Reverse orientations share the source population and do not double the independent sample count.

Inference uses 10,000 paired patient-cluster bootstrap resamples with default_rng seed 1729. Every method, sample, dose and budget belonging to a sampled patient stays together. The analysis reports percentile 95% intervals for the absolute paired MSE difference and the relative reduction in aggregate mean MSE. These intervals quantify sampling variation under this patient-resampling scheme, not all model, study-selection or laboratory uncertainty.

Primary success requires at least 5% relative MSE reduction and an absolute-difference interval entirely below zero. This threshold and the secondary efficiency comparison were frozen before unblinding. Subgroup and additional comparator intervals are diagnostic and not multiplicity-adjusted. They do not support separate confirmatory declarations for every drug.

An additional checker independently reaggregates the serialized records using ordinary dictionaries, repeats the primary bootstrap and integer-budget efficiency test, and checks method/budget/seed completeness and identical-information endpoints. This is an independent computational cross-check, not external scientific peer review. The full output contains 1,603,070 method/budget/context/orientation records after seed averaging.

---PAGE---
# 10. Primary confirmation results

The primary comparison passed both registered requirements. Exact joint GP has patient-weighted mean-budget MSE 0.0697646; random joint GP has 0.1038453. Their difference is -0.0340807, with 95% patient-bootstrap interval -0.0370354 to -0.0313049. The relative MSE reduction is 32.82%, interval 31.34% to 34.21%.

[[RESULTS_TABLE]]

The reverse p2-to-p1 sensitivity yields a 33.08% relative reduction against random joint GP. It supports directional consistency without replacing the primary analysis. The percentages describe squared log-response error; they are not percentage improvements in RMSE, drug discovery success, clinical accuracy or judging score.

Exact design improves only 0.66% over greedy joint GP. The diagnostic paired difference interval is -0.000895 to -0.000026. Joint exact also has 11.36% lower MSE than diagonal exact. These secondary effects are not multiplicity-adjusted, and the diagonal comparison changes both predictor and design.

The confirmation is stronger than the development evidence, where relevant paired intervals included zero. Both results remain in the record. The difference between studies is not evidence that the method will improve every assay. The primary result supports transfer to this admitted public cohort under the frozen endpoint, hierarchy, budget range and assumptions.

---PAGE---
# 11. Measurement efficiency and real cost limits

The registered efficiency reference buys ceil(0.75 times full pool size) randomly selected wells. Exact design buys floor(0.8 times that reference count). Both budgets include the initial control and extreme doses. Integer rounding creates 20-25% fewer purchased wells for the exact policy. The test requires the upper 95% patient-bootstrap bound on candidate/reference aggregate MSE to be at most 1.05.

[[COST_TABLE]]

The primary MSE ratio is 0.89185, interval 0.86430 to 0.92127, so the fixed-budget noninferiority criterion passes. Reverse orientation gives 0.85073, interval 0.83198 to 0.87002. A ratio below one means lower aggregate squared error for the candidate at its smaller prescribed budget; it is not a claim that every context is better.

Costs count wells for isolated drug contexts. Shared plate controls are charged in full separately for each context. We do not amortize those controls across a multi-drug plate or optimize the full plate layout. Assay preparation, instrument overhead, historical development measurements and audit measurements are outside the purchased-pool count. No currency saving is calculated.

This is retrospective reuse of already measured candidate pools. A prospective experiment must validate feasibility, reference handling, plate effects and actual cost before a laboratory-saving claim. The experiment compares fixed campaigns rather than deciding adaptively when to stop. It does not prove an optimal stopping threshold, or that a researcher can reproduce the same savings on a different assay protocol.

---PAGE---
# 12. Uncertainty, heterogeneity and failure modes

Nominal 90% intervals from the exact joint GP cover 98.05% of primary audit responses under the registered weighting. Their mean width is 1.34169 natural-log units. Patient-level aggregate coverage ranges from 94.39% to 100%. These intervals are conservative on the admitted cohort, not exactly calibrated to 90%. No post-confirmation recalibration was applied.

Coverage concerns marginal audit contrasts. It does not imply simultaneous coverage of a whole curve, a guarantee for each patient, or distribution-free validity. Shared audit controls induce dependence among dose errors. Wide intervals can cover well while being less useful; width is therefore reported alongside coverage. A narrower method would require separate evaluation rather than an untested cosmetic adjustment.

Primary point-estimate MSE improves against random joint GP for 53 of 56 drugs. Crizotinib, Larotrectinib and Sotorasib have small unfavorable differences. Both source libraries improve on average. These are descriptive diagnostics, not 56 independently powered confirmation tests. The complete drug and library tables remain available.

Important failure modes include heteroscedastic raw-log noise, between-plate systematic shifts, an unsuitable prior mean or kernel, incomplete feasible-action metadata, nonpositive signals and extrapolation beyond the designed support. The implementation rejects nonpositive observations and unsupported requests; it does not solve the underlying assay problem by censoring them silently.

A large posterior variance reduction can fail to improve realized error under misspecification. The source's lib2 concentration discrepancy and Farin's missing plate identity remain explicit. The local Farin example is a within-curve simulation. The independent confirmation's plate metadata is stronger, but neither source establishes clinical usefulness or transfer to neural/perfused chips.

---PAGE---
# 13. Runnable local research workflow

The local browser demonstration accepts a strict JSON request and a budget for additional wells. It returns selected IDs, roles and doses; current log-response estimates; model-conditional intervals; expected latent variances after the batch; fixed parameters; and a request fingerprint. It does not fabricate future measurements or claim to know future posterior means.

The public example is the first lexicographically complete Farin curve, O01:Coculture:F01:Gef. It reveals only a reference control and the two extreme doses. At budget three, the returned wells are farin:170 (vehicle control), farin:178 (0.1 uM) and farin:184 (1.1 uM). The model variance reduction is 0.1997884. Its missing source plate identity is explicitly labeled as an assumption.

Run the local server with `.venv/bin/python scripts/serve_demo.py` and open http://127.0.0.1:8765/. The CLI is `.venv/bin/python scripts/plan_wells.py examples/farin_wells_request.json --output plan.json`. The server binds only to loopback and does not save submitted requests. It is not a production multi-user service.

Inputs are bounded to one MiB, 64 wells and 10,000 enumeration representatives. The workflow rejects duplicate keys/IDs, nonfinite or nonpositive signals, oversized integers, unmeasured anchors, invalid roles and excessive budgets. It requires at least four distinct positive doses and a single nM or uM unit convention. Large searches are rejected rather than silently approximated.

Browser checks verified budget changes, error recovery, reset and copyable JSON. The CLI output matches the direct workflow output. Browser automation did not observe a download event within ten seconds; the copy field and CLI are verified alternatives. Semantic labels and numeric chart alternatives are present, but full accessibility and cross-browser certification remain pending.

---PAGE---
# 14. Reproduction and evidence integrity

The tested numerical environment is Python 3.13 on macOS ARM with pinned NumPy 2.2.6, SciPy 1.16.2, pandas 2.2.3, openpyxl 3.1.5, matplotlib 3.10.3 and pytest 8.3.5. Run `.venv/bin/python -m pytest -q -W error`; 127 tests pass in the current workspace. Numerical tests include analytic conditioning identities, reduced versus exhaustive enumeration, false-symmetry rejection and hidden-outcome isolation.

Source acquisition records retain URLs, exact bytes and SHA-256. Farin's text file is pinned to f9a9a51fd77ae1a5b19ad71fc236ce446223b3c2fcc66631ab304ab69bec78f0. Kryeziu Data S4 is pinned to 3847aa93b2a84c7d5d0b04c26494f39f35963fc41e96eae97d8a180fbc33d81c. The public dataset licenses were recorded as CC BY 4.0. Dataset and article licenses are distinct; no third-party article figures are reproduced here.

The protocol, source projections, model and evaluator hashes are saved. The amended preflight preserves a link to the first failed implementation. Source rows and exclusion reasons allow audit of admission and transformations. Scientific frozen files remained unchanged during the local-demo extension. Tests do not establish broader biological validity.

The prior first-half checkpoint reproduced thirty deterministic artifacts. The expanded confirmation has now also passed a fresh Python-environment run with an empty raw-data cache: pinned public files were downloaded again, all 127 tests passed, and 27 admission, confirmation and demo artifacts reproduced byte for byte. Historical freeze records were retained as inputs; projections, decisions, plans and results were regenerated. This reproduces known evidence, not a new unseen-cohort test. External review remains pending.

Saved results can be rechecked using scripts/audit_kryeziu_confirmation.py and scripts/summarize_kryeziu_diagnostics.py. Do not overwrite first-evaluation markers; use isolated destinations for new runs. Documents 24-29 map implementation, results and limitations. Immutable logs under artifacts/logs/second-half record commands, failures, hashes and checks.

---PAGE---
# 15. Claim ledger and release conditions

Supported: the frozen exact-versus-random comparison passed on 100 source patient IDs; the fixed-budget retrospective well-count test passed; exact finite Gaussian optimization is verified in its bounded domain; the local workflow runs and rejects tested malformed requests. These are specific evidence-backed statements rather than a broad production or clinical endorsement.

Not established: major new GP/design theory, superiority over every published model, prospective wet-lab savings, monetary savings, adaptive stopping, clinical benefit, organ-on-chip or neural-chip transfer, exact nominal calibration, external peer review, public deployment, or a competition rank. The strongest included greedy baseline is nearly as accurate as exact selection.

The competition strategy records conflicting Kaggle and Pazhou rubrics. Kaggle's live record assigned 30/30/20/10/10 to impact, technical approach, validation, reproducibility and presentation; the organizer track record used a different five-part allocation. Both motivate evidence, but neither permits a deterministic score prediction. Only ZHOU YINGTONG was named in the checked Kaggle judge section; no biography or wider track-panel assignment was verified.

Team attribution and category are user-confirmed. Before release, the team must verify registration and eligibility, assess material rule/ownership ambiguities, review licenses and complete publication/submission. Domain and independent reviewers should challenge endpoint meaning, control accounting, source discrepancies and reproduction. The prepared organizer questions have not been sent.

The immediate scientific next step is prospective operational validation of the same bounded claim, or a new development/confirmation cycle for a materially revised method. Additional complexity without untouched evidence would weaken rather than strengthen the argument. The current package is a reviewable research candidate. Its readiness and judging outcome must remain distinct from its successful registered experiment.

---PAGE---
# References and evidence map

[1] Farin, public organoid-stroma drug-sensitivity dataset, version 1. https://doi.org/10.17632/fypp6xhkjy.1. Source files, provenance and admission: data/farin_manifest.json; artifacts/farin_v1/; documents 24-25.

[2] Kryeziu public dataset, version 3. https://doi.org/10.17632/hr94h42xdc.3. Associated article: https://pmc.ncbi.nlm.nih.gov/articles/PMC13293968/. Admission and freeze: artifacts/kryeziu_design_v1/; configs/kryeziu-confirmation-protocol.json. Results: artifacts/kryeziu_confirmation_v1/confirmation.json, verification.json and results.csv.gz; documents 26-27.

[3] Gorodetsky and Marzouk (2016). Mercer Kernels and Integrated Variance Experimental Design. SIAM/ASA Journal on Uncertainty Quantification 4:796-828. https://doi.org/10.1137/15M1017119.

[4] Wang et al. (2020). A statistical framework for assessing pharmacological responses and biomarkers using uncertainty estimates. eLife 9:e60352. https://eprints.whiterose.ac.uk/id/eprint/169449/.

[5] Tansey, Tosh and Blei (2022). A Bayesian model of dose-response for cancer drug studies. Annals of Applied Statistics 16:680-705. https://doi.org/10.1214/21-AOAS1485.

[6] Vasanthakumari et al. (2024). A Comprehensive Investigation of Active Learning Strategies for Conducting Anti-Cancer Drug Screening. Cancers 16:530. https://doi.org/10.3390/cancers16030530.

[7] Takeno et al. (2025). Distributionally Robust Active Learning for Gaussian Process Regression. ICML, PMLR 267. https://proceedings.mlr.press/v267/takeno25a.html.

[8] Tang et al. (2026). Representative, Informative, and De-Amplifying: Requirements for Robust Bayesian Active Learning under Model Misspecification. AISTATS, PMLR 300. https://proceedings.mlr.press/v300/tang26d.html.

Competition requirements and judge evidence: documents 01-02 and 21; Kaggle competition slug ai-4-s-open-innovation-artificial-intelligence-for-life-scien; https://www.aicompetition-pz.com/topic_detail/26. These are rule-source records, not scientific validation.

Local workflow and QA: document 28; artifacts/well_workflow_v1/. Prior-art claim audit: document 29. Every headline in this report traces to these records. Third-party sources inform context; all reported benchmark numbers are this repository's analyses of the cited public data.
