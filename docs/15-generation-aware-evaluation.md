# Generation-aware evaluation on the second study

Updated October 6, 2026. The previous goal turn made progress by adding nested baselines and retrieving the second study's files. This iteration implements a second-context evaluation; it does not establish the requested validated halfway milestone or guarantee a rank.

## Scientific admission and scope

The pinned author repository's concurrent-treatment scripts identify `conc0`, `conc1`, and where applicable `conc2` as dimensionless concentration inputs bounded between zero and one. They identify `cv_exp` as an experimental objective; the corresponding utility maps concentration coordinates through logarithmic bounds. This supports use of the provided coordinates for within-context prediction, without guessing physical units or reconstructing dose conversions.

`src/zenithsync/yakavets.py` now admits the 35 FAC concurrent rows and 50 OLA–IBET concurrent rows for retrospective prediction of the **next logged experimental generation**. The two contexts remain separate. Response coordinates remain exactly as supplied; no clipping to [0,1] is imposed. Generation/sample identities are validated and original CSV row provenance is retained.

Only concentration inputs enter prediction. Derived synergy, theoretical viability, measured uncertainty and generation-specific results are excluded from predictor features. Thus the malformed `cv_theor` cell discovered earlier cannot silently contaminate fitting. The adapter rejects changed source hashes, invalid coordinates, missing required numeric values and duplicated generation/sample keys.

The 59 sequential-treatment records remain outside this modeling admission until timing/sequence semantics are reconciled. This is an outstanding part of source review, not an assertion that those records are unusable. Neither context establishes independent patient/donor generalization. Future-generation validation follows logged adaptive selection and cannot estimate arbitrary unmeasured interventions.

Source: [author repository](https://github.com/yakavetsiv/ml-mf_chemo), pinned revision and hashes in `data/yakavets_repository_manifest.json`. Original code was inspected for semantics, not executed or copied into the model implementation. Public redistribution rights remain an outstanding review item.

## Implemented model and evaluation

`src/zenithsync/multidimensional.py` implements exact Matérn-5/2 GP conditioning on multidimensional design coordinates. It validates dimensions, finite values and covariance behavior. Independent tests establish equivalence with the scalar implementation and invariance to feature-axis permutation.

`scripts/generation_benchmark.py` holds out each generation after generation zero, fitting only on earlier generations. It compares a training mean, nearest observation, fixed ridge regression, a fixed GP and a GP selected among 27 candidates using **only earlier expanding-generation folds**. When no inner generation is available, tuning returns the declared default rather than using the test generation. All outer row identities, inner candidate losses and chosen parameters are saved.

Ridge uses an unpenalized intercept and a fixed coefficient penalty of 0.1. The GP grid varies amplitude, length scale and observation-noise assumptions. Both remain research baselines; neither hyperparameter tuning nor generation separation supplies missing biological independence.

## Measured results

The table reports mean RMSE across four held-out generations in each context, in that context's original concurrent-response coordinate.

| Model | FAC | OLA–IBET |
|---|---:|---:|
| Training mean | 0.107969 | 0.179348 |
| Nearest observation | 0.180760 | 0.141774 |
| Fixed ridge | **0.100898** | **0.099044** |
| Fixed GP | 0.112670 | 0.117225 |
| Past-generation tuned GP | 0.109567 | 0.111251 |

Ridge performs best in both contexts. GP tuning improves the fixed GP modestly but does not beat ridge. These outcomes rule out a current claim that GP complexity consistently improves response prediction. They also identify a necessary strong comparator for the eventual assay planner.

The study measures prediction error on recorded experiments. It does **not** measure prospective measurement savings, compare new policies against the original optimizer under complete counterfactual support, or identify a clinically useful treatment regimen.

## Numerical and execution record

Forty-five tests pass with warnings treated as errors. A separate full-data run initially emitted macOS matrix-multiplication floating-point warnings during GP covariance contraction. The earlier analogous issue is documented in Document 13. This implementation now uses explicit tensor contractions, checks finite outputs and covariance eigenvalues, and completes the full benchmark with warnings promoted to errors. The original warning log is preserved rather than removed.

Evidence:

- `artifacts/generation_benchmark_v1/admission.json`: feature/target definitions, exclusions, source hashes and claim boundaries.
- `artifacts/generation_benchmark_v1/folds.json`: training/test row identities and all tuning losses.
- `artifacts/generation_benchmark_v1/predictions.csv`, `by_generation.csv`, `summary.csv`: actual predictions and results.
- `artifacts/logs/generation-benchmark-v1.txt`: original run and numerical warnings.
- `artifacts/logs/generation-benchmark-repaired.txt`: full-data run with warnings treated as errors.
- `artifacts/logs/tests-generation-current.txt`: current tests.
- `artifacts/logs/reproduction.json` and `fresh-environment.txt`: fresh-environment validation, expanded to 20 deterministic artifacts. The authoritative result is recorded in those files.

## Remaining work and manual needs

The next engineering work is to integrate supported inputs, model comparison, predictive uncertainty and abstention into a reviewable research workflow, while completing source admission. Policy comparisons must include simple curve/ridge predictors and use measured support. A complex model losing a fair benchmark is a research finding, not a reason to drop the comparator.

No user intervention is presently required to continue local implementation. Qualified endpoint/cost review, authorized biological metadata, independent confirmation and competition-rule resolution remain necessary before stronger scientific and submission claims. No external messages, registration, publication, paid resources or experiments were initiated.
