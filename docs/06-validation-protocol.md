# Validation protocol and acceptance gates

This is a preregistration-style plan. Numerical thresholds below are **proposed internal targets**, not official scoring criteria, achieved results, or guarantees. Freeze them after data feasibility and biological review, before inspecting final test outcomes.

## 1. Claims and tests

| Claim | Required experiment | Primary unit | Failure condition |
|---|---|---|---|
| Better response estimation | Held-out dose grid against strongest development-selected baseline | Biological group / compound appropriate to claim | Improvement interval includes no gain or errors fail practical tolerance |
| New-compound generalization | Compound/scaffold-disjoint outer evaluation | Compound | Any dose/replicate/alias leakage or missing supported test classes |
| Donor generalization | Donor-disjoint test; target group effects marginalized | Donor | Test donor information enters fit or calibration |
| Cross-lab transfer | Entire external lab held out | Lab/biological groups within lab | Only same-lab random split tested |
| Reduced assay requirements | Matched-budget policy comparison with independent audit outcomes | Independent assay campaign | Savings depend on surrogate-generated “truth” or different stopping criteria |
| Reliable uncertainty | Independent group-level calibration/audit | Exchangeable target group | Undercoverage hidden by pooled averages or useless interval widths |
| Mechanistic value | Correct ablation plus parameter sensitivity/identifiability | Independent experiment | Same accuracy without mechanism or implausible/unidentified parameters |

## 2. Split design

Create the split from stable biological identities before scaling, feature selection, augmentation, encoder fine-tuning, imputation, or batch correction. Hash the manifest and preserve it.

Use distinct training, development, calibration, and final-test roles where the sample size supports them. When too small, use nested group cross-validation for exploratory evaluation and explicitly acknowledge that it is not an independent confirmatory holdout. The final external/prospective set remains necessary for a strong generalization claim.

Not every axis can be held out simultaneously. Define separate protocols:

- **Dose interpolation:** same compound and assay context; hold out specified dose observations, while grouping biological dependence correctly. This tests interpolation only.
- **Compound transfer:** all doses, replicates, aliases, and derivative images of held-out compounds stay outside fitting and tuning.
- **Scaffold transfer:** group molecular scaffolds where meaningful; report group counts and chemical similarity. With 27 compounds, a credible large scaffold benchmark may be impossible.
- **Donor or batch transfer:** hold out complete donor/batch groups and report confounding with condition.
- **Laboratory transfer:** reserve an independently generated dataset; document endpoint and protocol comparability before combining.

A condition completely confounded with batch cannot be repaired by a clever split. Redesign the experiment or narrow the estimand. Do not “remove batch” by erasing real treatment differences.

## 3. Leakage audit

Check identical file hashes, image near-duplicates, overlapping temporal windows, reused controls, same organoid under different experiment labels, repeated compound synonyms/salts, and pretrained-data overlap. Fit transformations only on allowed training information.

Control normalization on a new plate may be legitimate if controls are part of the operational workflow; count them in assay cost and describe the procedure. Using all held-out treatment measurements to estimate plate normalization is a different, potentially transductive protocol and must not be hidden.

Attribution methods and biological explanations cannot use test labels to choose a favorable example set. Select demo cases by a preregistered rule: one representative success, one failure, one abstention, plus access to the full result population.

## 4. Baseline ladder

| Baseline | Why it is necessary |
|---|---|
| Constant/control-only predictor | Detect trivial predictability and endpoint scaling errors |
| Published assay rule, when reproducible | Establish added value over the original scientific workflow |
| Independent Hill curves / spline | Test whether dose shape alone suffices |
| Hierarchical Hill/mixed-effects model | Handle group effects without complex ML |
| Regularized linear and tree-based model | Strong tabular alternatives |
| Target-only GP | Test whether transfer is useful |
| Standard multifidelity GP | Isolate any new discrepancy/selection mechanism |
| Uniform, random, and space-filling acquisition | Basic assay-design alternatives |
| Maximum predictive uncertainty and information gain | Distinguish noise-chasing from informative selection |
| Relevant published optimization policy [D4] | Compare with actual application precedent when task compatible |

Match observed data, outcome definitions, usable features, preprocessing, tuning opportunity, initial measurements, and assay budget. Do not force an optimization method onto a different task merely to give it a weak score. A reproduction failure is a limitation, not evidence that the baseline is inferior.

## 5. Primary metrics

For response prediction, report MAE and RMSE in meaningful endpoint units, plus a normalized metric with denominator fixed from training controls or domain tolerance. R-squared alone is insufficient and can be unstable on small or narrow-range groups.

For interval predictions, report empirical coverage, mean/median width, group-wise behavior, and a proper interval score. For central (1-alpha) intervals [L,U], use

\[
IS_\alpha=(U-L)+\frac{2}{\alpha}(L-y)1\{y<L\}+\frac{2}{\alpha}(y-U)1\{y>U\}.
\]

This penalizes both wide intervals and missed observations. Reporting coverage without width rewards vacuous predictions.

For classification, report sensitivity, specificity, precision-recall behavior, Brier score, calibration, and confusion counts. Freeze thresholds on development data. Explain prevalence and the scientific source of labels. AUROC is not an estimate of the benefit of the next assay decision.

For acquisition, plot **measurement cost versus decision error / curve error**, not just the best endpoint found. Define B_m(epsilon) as the cost method m requires to meet a fixed tolerance epsilon on an independent audit set. Then

\[
\mathrm{savings}=1-B_{proposed}(\epsilon)/B_{baseline}(\epsilon).
\]

If a method never reaches epsilon, record failure/right-censoring under the benchmark budget; do not drop the run or assign it a favorable finite cost.

## 6. Policy evaluation without a fictional oracle

**Best evidence:** prospectively randomize independent chip campaigns to the proposed policy and strong comparison policies, with identical resources and blinded endpoint analysis. Obtain appropriate data rights and institutional experimental oversight before conducting such work. This round only specifies the design.

**Measured-pool replay:** restrict recommendations to a pool whose outcomes are genuinely measured. Hide outcomes from the policy until selected, use the same initial information, and reserve a separate audit set. Group dependence and the original data's selection mechanism still constrain conclusions.

**Logged adaptive experiments:** only outcomes of chosen actions are observed. A new policy may choose unsupported actions. Off-policy estimators require defensible propensities/overlap and adequate support; a deterministic logging policy may violate positivity. Do not fill unmeasured actions with our own model and report that as real-data policy validation.

**Simulation:** can test algorithms under known mechanisms, shifts, failures, and noise. Use alternative simulator families and misspecification, not only the same equations used by the learner. Label all savings simulated and keep them separate from biological results.

## 7. Ablation matrix

Run targeted comparisons on identical outer splits:

1. Full method versus target-only model.
2. Discrepancy-aware transfer versus naïve pooling and standard transfer.
3. Hierarchical group effects versus flat observations.
4. Mechanistic mean versus unconstrained model of comparable capacity.
5. Decision-aware acquisition versus uncertainty-only acquisition.
6. Calibrated versus uncalibrated uncertainty at matched decision coverage.
7. Transfer selector enabled versus always-on transfer, including incompatible-source stress test.
8. Optional image/chemistry features versus endpoint-only model.

Add component interactions only when the main comparisons suggest them. Ablations that change model capacity, available information, or tuning budgets need explicit accounting.

## 8. Statistical design

For paired campaign-level improvement D, the rough normal approximation for detecting standardized effect delta/sigma_D at two-sided alpha=.05 and 80% power is

\[
n\approx(z_{.975}+z_{.8})^2\sigma_D^2/\delta^2.
\]

At effect size 0.5 this gives 32 independent pairs after rounding up. This is an illustrative planning calculation, not a sufficient sample-size determination for clustered, censored, sequential, or non-Gaussian designs. Estimate variability from a separate pilot and use appropriate simulation for final power.

If 1,000 observations arise from clusters of size 100 with intracluster correlation .2, the simple design effect is 1+99(.2)=20.8, yielding an approximate effective count of 48.1—not 1,000. This approximation concerns precision under its assumptions; ten biological groups remain ten groups for resampling and calibration.

Bootstrap or randomize at the independent assignment/group level, preserving pairing. Do not bootstrap individual cells when the intervention was assigned to a chip. Cross-validation folds and multiple random seeds are not independent biological samples. Report biological variability separately from training/policy randomness.

Use one prespecified primary endpoint/comparison. For a confirmatory family of multiple hypotheses, apply Holm correction or a justified hierarchical testing plan. Secondary results remain exploratory when the sample size is inadequate. Show effect sizes and intervals, not just p-values.

**Zero observed errors is not zero risk.** With n independent trials and no errors, a one-sided exact 95% upper error bound is 1-.05^(1/n). At n=27 it is about 10.5%; at n=4 it is about 52.7%. To bound error below 5% with zero observed errors requires at least 59 independent relevant trials. Sensitivity uses the number of positive cases, not all specimens.

## 9. Proposed promotion gates

| Gate | Pass evidence | If failed |
|---|---|---|
| Scientific admission | Correct units, identities, endpoint, license, sufficient support | Change dataset or narrow task |
| Baseline integrity | Reproduced reference and leakage-free splits | Repair evaluation before advancing |
| Algorithmic gain | Primary effect improves over strongest development-selected baseline with interval supporting gain | Keep simpler model or revise contribution |
| Practical gain | Proposed target: at least 20% lower assay cost at fixed prespecified error, with paired lower confidence bound above zero | Report smaller/uncertain gain honestly; no claim of decisive savings |
| Reliability | Coverage/width and selective error meet prespecified operational tolerances in supported domain | Recalibrate on independent data or abstain/narrow deployment |
| External evidence | Independent biological setting corroborates central claim | Keep claim retrospective and setting-specific |
| Reproduction | Independent person recreates main tables and demo with public artifacts | Submission is not evidence-complete |

The 20% target is a proposed meaningful-effect goal, not a universal biological standard. It may be revised with documented cost evidence before final testing. A failed statistical gate does not license repeated testing until significance appears.

## 10. Result table template

For every comparison record: dataset/version; target estimand; group counts; split hash; baseline; training inputs; model/config hash; seed; primary effect; uncertainty interval; coverage/width; cost accounting; failure/abstention rate; subgroup limitations; run artifact path. Leave result cells **not run**, never populate them with planning targets.
