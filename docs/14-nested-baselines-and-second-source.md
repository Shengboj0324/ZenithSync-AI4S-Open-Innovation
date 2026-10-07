# Nested baselines and second-source admission

Updated October 6, 2026. The preceding turn was substantive progress: model averaging, acquisition numerical repairs and actual-data sensitivity results were implemented and checked. This turn adds stronger baseline selection and retrieves a second source. The full goal remains active; no winning guarantee or validated halfway completion is asserted.

## Training-only tuning

The previous comparison used declared fixed model assumptions. `src/zenithsync/tuning.py` now selects a GP from 27 amplitude/length/noise combinations using inner leave-one-dose-out loss. All replicate rows at a dose are withheld together. Inner losses give equal weight to each dose group. The outer held dose is never passed into tuning. Ties resolve deterministically by candidate order.

`scripts/nested_baselines.py` evaluates that procedure against the fixed GP, finite GP mixture, Hill curve, constant mean, linear interpolation and shape-preserving cubic interpolation (PCHIP). Interpolation models average available replicates at each dose, work in the same log1p source coordinate, and use constant extension outside the training dose range. This extension is explicit; it does not pretend to identify an unmeasured toxicity cliff.

Tests check all-replicate fold separation, row permutation invariance, replicate averaging, and boundary extension. Forty tests now pass with warnings treated as errors. Full candidate losses and training/test row identities are retained in `artifacts/nested_baselines_v1/selections.json`.

## Results and consequence

| Model | Compound-macro RMSE | Compound-macro MAE |
|---|---:|---:|
| Linear interpolation | 28.0289 | 22.0282 |
| Finite GP mixture | 28.5997 | 22.9883 |
| PCHIP | 28.9939 | 22.9032 |
| Fixed GP | 29.0687 | 23.6018 |
| Hill | 29.2867 | 22.7967 |
| Nested tuned GP | 32.5367 | 26.0896 |
| Constant | 33.4860 | 27.2292 |

Linear interpolation wins this reconstruction comparison. The advanced mixture therefore has **not** earned an overall reconstruction-superiority claim. Inner tuning does not guarantee better performance; its small training folds produce unstable choices, with substantial outer error. The appropriate response is to retain these baselines and strengthen data/evidence, not remove the unfavorable comparison.

Separating interior from edge holds changes the story. Linear interpolation has interior macro RMSE 23.8724 versus mixture 24.4261. At the edges, Hill is better (28.7650) than linear (33.7848) or mixture (34.7273). Edge prediction and interpolation are distinct tasks. A future scientific claim must specify which is needed; choosing the better task after inspecting results is exploratory analysis, not confirmation.

These are still six previously inspected compound curves. Nested computation prevents direct outer-label leakage but does not make the data an untouched biological cohort, identify missing donors, or resolve shared-control covariance. This iteration does not tune the mixture against these outer results and then call that a fair test.

## Second-source retrieval

The [author repository for Yakavets et al.](https://github.com/yakavetsiv/ml-mf_chemo) provides data independent of the failing Dryad download route. `scripts/fetch_yakavets_repository.py` resolves and pins a commit on its first run, downloads only four CSV tables plus README/license, and records SHA256 hashes. Later runs reuse that exact revision and reject changed bytes. No author code was executed and no external software was installed from that repository.

| Author table | Rows | Generations |
|---|---:|---:|
| FAC concurrent | 35 | 5 |
| FAC sequential | 32 | 4 |
| OLA–IBET concurrent | 50 | 5 |
| OLA–IBET sequential | 27 | 3 |

The 144 rows are experimental-condition records, **not 144 independent donors**. This repository is a different artifact from the Dryad archive and is not claimed to contain the previously described individual-drug dose-response tables. Its root license is GPL-3.0; file-specific data reuse and public redistribution still require review. Raw files remain ignored by Git.

`scripts/audit_yakavets_repository.py` checks each downloaded CSV against its pinned hash, profiles fields, checks generation/sample-key duplication and records nonnumeric values without repairing them. The audit identified:

- Concurrent response fields use a different numerical scale from sequential `cv`; no automatic pooling or percent conversion is performed.
- Sequence labels are categorical and must not become arbitrary numeric distances.
- One OLA–IBET concurrent `cv_theor` cell contains ten space-separated numbers where other rows contain a scalar. It is retained as malformed, not coerced to a convenient number.
- Generation/sample keys have no duplicates within the inspected tables. These identifiers do not establish independent biological replication.
- Author timing code and the earlier provider description require reconciliation before using durations or inferring total exposure.

All four tables are admitted for **source inspection only** at this point. No model has been trained on them. Eventual evaluation must respect adaptive collection order, feasible measured support, context differences and aggregate-versus-replicate distinctions. A retrospective policy cannot claim outcomes for combinations the original study never measured.

## Files, logs and reproducibility

- `artifacts/nested_baselines_v1/`: all predictions, 27-candidate inner losses, subgroup comparisons and code hashes.
- `artifacts/logs/tests-nested-baselines.txt`: the 40-test run.
- `artifacts/logs/nested-baselines-v1.txt`: model comparison execution output.
- `data/yakavets_repository_manifest.json`: pinned repository revision, URLs and file hashes.
- `artifacts/yakavets_admission/initial_quality_audit.json`: field-level source audit.
- `artifacts/logs/yakavets-repository-fetch.txt` and `yakavets-repository-audit.txt`: acquisition and audit output.
- `artifacts/logs/reproduction.json`: expanded fresh-environment verification, now comparing 16 deterministic model/evaluation artifacts; the full subprocess output is `fresh-environment.txt`. The second-source fetch is separate and is not represented as covered by those 16 comparisons.

Added commands:

```sh
.venv/bin/python scripts/nested_baselines.py
.venv/bin/python scripts/fetch_yakavets_repository.py
.venv/bin/python scripts/audit_yakavets_repository.py
```

## Next requirements and manual intervention

Next work is to finish source-semantic admission, implement context-appropriate generation-aware evaluation, and build a transparent research interface with supported-domain checks and abstention. The intended outcome remains reliable assay planning; obtaining another dataset does not change that objective into an easier unrelated prediction task.

No manual intervention is required to continue this local work. Authorized donor/control metadata, qualified endpoint/cost review and independent confirmatory biology remain necessary for stronger claims. None of the numerical improvements establishes placement in the competition.
