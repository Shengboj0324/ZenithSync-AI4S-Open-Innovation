# First independent confirmation: results and limits

The frozen primary comparison and the separate measurement-efficiency test both passed. This establishes a bounded retrospective result on the admitted public organoid cohort. It does not establish clinical usefulness, a new Gaussian-process theory, prospective laboratory savings or a guaranteed competition rank. The complete M6–M10 delivery scope remains unfinished.

## Protocol integrity and population

The hypothesis, model parameters, cohort admission, patient grouping and analysis were frozen before response evaluation in `configs/kryeziu-confirmation-protocol.json`. The initial protocol freeze is timestamped **2026-10-07 03:38:30 UTC**. The model uses only parameters selected during Farin development. No Kryeziu response was used for fitting or tuning the prior.

The outcome-free implementation preflight covered 13,048 context/orientation pairs and eleven geometries. Unblinding began at **03:48:17 UTC**. The first evaluator attempt then stopped before calculating any results because a JSON list was compared with an equivalent Python tuple. The original program, manifest and failure trace were preserved. A technical amendment canonicalized manifest serialization and checked the old/new manifest chain. All design selections, prediction coefficient hashes and the scientific protocol were identical across the amendment. The subsequent run was the first completed response evaluation. No model or scoring rule was changed in response to outcomes.

There were 6,524 structurally admitted, patient-mapped drug contexts. The frozen nonpositive/nonfinite-signal rule excluded 28 contexts in each orientation, involving 48 distinct source rows. The analysis therefore includes **6,496 primary contexts, 148 organoid samples and 100 source patient IDs**. The reverse orientation uses the same validity requirement. There are 1,603,070 serialized method/budget/context/orientation records after averaging the twenty computational random seeds.

The confirmation data come from a distinct public study and were not used for model or hypothesis selection. Within that study, patient mapping uses the explicit PDO sample/patient fields. Cross-study patient non-overlap cannot be independently proved from deidentified identifiers; this is a public-study transfer claim with that limit. Parallel technical plates also do not establish transfer across institutions, clinical settings or new experimental protocols.

## Primary result

The endpoint is squared error in raw log treatment signal minus mean log negative-control signal on the separate audit plate. Each curve averages all registered budgets; contexts are averaged within samples, samples within patients, and patients equally. Random seeds are averaged before this hierarchy.

| Primary p1-to-p2 method | Mean MSE across budgets |
|---|---:|
| Exact selection, joint-noise GP | 0.069765 |
| Greedy IVR, joint-noise GP | 0.070226 |
| Exact selection, diagonal-noise GP | 0.078702 |
| Random selection, PCHIP | 0.085082 |
| Random selection, linear interpolation | 0.095216 |
| Random selection, joint-noise GP | 0.103845 |
| Random selection, diagonal-noise GP | 0.116787 |

The frozen primary contrast is **exact versus random selection under the same joint GP**:

- Paired mean-MSE difference: **-0.034081**, patient-bootstrap 95% interval **[-0.037035, -0.031305]**.
- Relative mean-MSE reduction: **32.82%**, interval **[31.34%, 34.21%]**.
- The registered requirements of at least 5% reduction and an entirely favorable difference interval are met.

This percentage describes MSE, not RMSE, clinical response accuracy or competition score. The reverse p2-to-p1 sensitivity gives a 33.08% MSE reduction. It corroborates the direction but does not replace or double the primary sample size.

The stronger greedy comparator nearly matches exact selection: the exact method's MSE is only **0.66% lower**, with a diagnostic paired difference interval [-0.000895, -0.000026]. Joint exact selection improves 11.36% over the diagonal exact ablation, which changes both estimation and selection. These are secondary contrasts without a multiplicity-adjusted claim. The large primary gain must not be presented as the gain over the strongest available method.

## Registered measurement-efficiency comparison

The reference uses ceil(0.75 times the full pool size) random measurements. The candidate uses floor(0.8 times that reference count) exact-design measurements. Initial controls and extreme-dose wells are included in both costs. Integer rounding produces **20–25% fewer purchased wells**, depending on pool size.

At these paired budgets, candidate/reference MSE is **0.89185**, with patient-bootstrap 95% interval **[0.86430, 0.92127]**. Its upper bound is below the frozen noninferiority limit of 1.05. Thus the registered retrospective assay-count criterion passed. Reverse orientation also passes, with ratio 0.85073.

| Full pool | Random reference wells | Exact candidate wells | Primary contexts |
|---:|---:|---:|---:|
| 18 | 14 | 11 | 3,590 |
| 22 | 17 | 13 | 2,515 |
| 21 | 16 | 12 | 231 |
| 15 | 12 | 9 | 86 |
| 19 | 15 | 12 | 74 |

These are separate fixed-budget campaigns, not a learned stopping rule. Costs are well counts for isolated drug contexts. Controls are charged separately per context; shared plate-wide controls are not amortized. Preparation, instrument overhead, audit measurements and historical training costs are not included. Prospective savings or currency savings require an additional operational study.

## Uncertainty and heterogeneity

The joint exact method's nominal 90% predictive intervals cover **98.05%** of primary audit responses under the registered averaging. Their mean width is **1.34169 natural-log units**. Patient-level aggregate coverage ranges from 94.39% to 100%. The intervals are conservative on this cohort; these results do not establish exact 90% calibration, simultaneous curve coverage or a distribution-free guarantee. No recalibration was performed after seeing these outcomes.

Primary point-estimate MSE improves versus random joint-GP selection for 53 of 56 drugs. Crizotinib, Larotrectinib and Sotorasib have small unfavorable differences. Both libraries improve on average. These subgroup diagnostics are reported in full and do not imply each drug has a separately powered confirmation result.

A source-description discrepancy remains: the article methods describe seven lib2 concentrations, while the current raw file commonly contains eight positive single-agent dose values. The analysis uses the pinned raw dose fields consistently, including the additional value; it does not silently infer or delete a dose to match prose. Source clarification remains useful for the final scientific review.

## Exact computation and tests

The optimizer checks that swapping members of a proposed control group leaves the full conditional Gaussian mean and covariance invariant, within numerical tolerance. These transpositions generate all permutations of the group. Consequently, the variance objective is unchanged for subsets differing only in which k group members they contain; one representative per k suffices. Singleton groups retain all treatment-subset choices.

Across 22 model/geometry combinations, the program evaluates **13,408 representatives covering 2,113,536 subsets**. This is a verified reduction in enumeration count, not a measured wall-clock speedup or a claim that symmetry reduction is newly invented. The result remains exact only for the fixed Gaussian variance objective, unit costs and unrestricted feasible subsets. Biological predictive error is evaluated separately.

**107 tests pass with warnings treated as errors.** Tests compare reduced search with exhaustive enumeration, reject false symmetries, compare batched prediction with direct conditioning, poison unpurchased responses, check full-information equivalence and verify patient weighting. An additional audit independently reaggregates the serialized CSV using ordinary dictionaries, reproduces the primary bootstrap interval and checks complete budget/method/seed coverage and identical-information endpoints. This is an independent computational cross-check, not an external human scientific review.

## Records and continuation

`artifacts/kryeziu_confirmation_v1/` contains the original and amended preflight manifests, original program and failure trace, unblinding marker, signal-projection hash, first evaluation marker, compressed complete results, source-row exclusions, patient results, all-budget tables, drug/library diagnostics, paired comparisons and verification record. The source XLSX files and signal projection stay in the ignored local data cache.

The acquisition and first evaluation intentionally use exclusive markers. A completed confirmation must not be silently overwritten. Reproduction should use an isolated checkout/output directory while preserving the first-run records. Audit and diagnostic scripts can be rerun against the saved results:

```sh
.venv/bin/python -W error scripts/audit_kryeziu_confirmation.py
.venv/bin/python -W error scripts/summarize_kryeziu_diagnostics.py
.venv/bin/python -m pytest -q -W error
```

Remaining work includes the final prior-art/contribution assessment, complete operational claim review, integration into the runnable demonstration, judge-facing technical report/video/Writeup, a fresh-environment reproduction of this expanded pipeline, external review and release/eligibility checks. No publication, registration, organizer message or submission was performed, and no user intervention was needed for this evaluation.
