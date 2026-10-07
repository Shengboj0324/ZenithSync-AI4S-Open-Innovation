# Implementation record — initial executable research pipeline

For the subsequent model-uncertainty implementation, 36-test suite, sensitivity study and expanded reproduction evidence, see [Document 13](13-model-uncertainty-and-acquisition-audit.md). The results below preserve the initial milestone rather than replacing its findings.

Updated October 6, 2026, America/Los_Angeles. This record supersedes planning-only status statements in Documents 01–11; those documents remain the original scientific specification. This is substantive implementation progress, **not yet evidence that the requested validated halfway milestone has been reached**. No competition outcome can be guaranteed.

## Implemented capabilities and evidence

| Capability | Implementation | Evidence and limits |
|---|---|---|
| Public artifact acquisition | `scripts/fetch_public_data.py` | Two Liver-Chip workbooks downloaded; URLs, byte counts, retrieval timestamps and SHA256 hashes in `data/source_manifest.json` |
| Strict source adapter | `src/zenithsync/data.py` | Pinned workbook hash, exact column schema, preserved missing outcomes, original spreadsheet row provenance |
| Mechanistic baseline | `src/zenithsync/models.py` | Stable Hill evaluation and constrained multistart fitting; reports fit rank and active bounds; does not claim identified EC50 |
| Probabilistic baseline | `src/zenithsync/models.py` | Exact Matérn-5/2 GP conditioning with heteroscedastic diagonal observation variance; fixed initial parameters |
| Acquisition | `src/zenithsync/acquisition.py` | Integrated latent variance reduction and threshold-decision value of information per positive cost |
| Calibration primitives | `src/zenithsync/uncertainty.py` | Group-maximum residual scores and finite-sample rank with infinite interval when calibration groups are insufficient |
| Censoring primitive | `src/zenithsync/likelihoods.py` | Stable Gaussian interval probabilities in extreme tails; **not integrated into a censored-data fit** |
| Evaluation | `scripts/benchmark.py`, `scripts/replay_benchmark.py` | Leave-one-dose-out reconstruction and measured-pool acquisition with hidden audit outcomes |
| Execution evidence | `artifacts/logs/` | Test outputs, source-fetch output, benchmark results, dependency repair, fresh-environment reproduction |

The current implementation is a research baseline. It does not yet implement validated hierarchical donor effects, context transfer, externally calibrated uncertainty, experimentally justified costs, or a submission-ready interface. These remain part of the original objective rather than being removed to declare completion.

## Real-data admission result

Ewart Supplementary Data 8 contains 70 albumin rows, 68 observed responses, six compounds, and 35 compound–dose groups. Two Pioglitazone values are missing. The workbook contains no donor/chip identifiers; row adjacency is not used to invent them. Zero albumin values are preserved as source-reported observations; possible detection-limit interpretation needs clarification. The concentration column lacks an explicit unit, so the adapter retains its source coordinate and issues no physical-dose recommendation.

Albumin values are normalized assay readouts, not viability percentages. Values above 100 are retained. Shared-control normalization can induce covariance that cannot be recovered from this table. The initial GP uses a declared fixed noise SD of 20 response units; this is an exploratory setting, not an estimated measurement uncertainty. In replay, that same noise variance is assigned to each revealed dose mean without claiming a known independent replicate count.

**Admission:** exploratory within-compound reconstruction and measured-pool algorithm checks only. No donor-transfer, unseen-drug toxicity, prospective assay-savings, or clinical claim is admitted.

The supplementary table is linked by [the original publication](https://www.nature.com/articles/s43856-022-00209-1), whose article license is CC BY 4.0 with the stated third-party exceptions. No separate notice was present in the inspected data sheet. Raw downloads are excluded from Git; source acquisition and attribution are retained. Artifact rights still need final review before public redistribution.

A second correction, [January 2023](https://www.nature.com/articles/s43856-023-00235-7), changes the Table 5 spheroid specificity from 100 to 67. The February correction already recorded in Document 04 fixes Table 3. Neither corrected table is used as a label in this benchmark.

The optional Yakavets Dryad download returned HTTP 403 on both attempts. Its provider-described contents are not falsely reported as ingested. See `artifacts/logs/data-fetch-secondary.txt` for the retained failure.

## Initial measured results

All observations at a held-out dose are excluded from training together. These are exploratory folds from the same published study. All six compounds have now been inspected; they must not later be described as an untouched confirmatory cohort.

| Model | Compound-macro RMSE | Compound-macro MAE |
|---|---:|---:|
| Training-mean constant | 33.4860 | 27.2292 |
| Decreasing Hill curve | 29.2867 | 22.7967 |
| Fixed Matérn GP | 29.0687 | 23.6018 |

Response errors are in the normalized albumin coordinate. The GP has slightly lower macro RMSE than Hill, while Hill has lower macro MAE. No superiority claim follows. Troglitazone is especially difficult: the GP RMSE is about 58.95, and its abrupt high-dose response exposes a weakness of this initial smooth prior. See per-compound results rather than relying only on the average.

Measured-pool replay with three revealed dose means gives:

| Policy | Compound-macro audit RMSE |
|---|---:|
| Random, averaged over 20 seeds | 24.9765 |
| Space filling | 24.3217 |
| Integrated variance reduction | 24.1025 |
| Decision VOI | 25.3278 |

All four policies have the same observed threshold-error average at that budget, 0.1389, using an exploratory threshold of 50. This does **not** establish that VOI works better, that the probability model is calibrated, or that the threshold is biologically appropriate. Twenty seeds are computational repetitions, not twenty independent experiments. Budget counts revealed dose means, not chips, money, or elapsed laboratory effort. At budget five, only five compounds remain eligible, so comparisons across budget rows change population.

Every acquisition step, revealed value, selected row-group index, prediction, audit outcome and quadrature comparison is saved in `artifacts/measured_pool_replay/traces.json`. No unmeasured response is fabricated for evaluation.

## Mathematical validation

The test suite checks Hill limits and extreme doses; dose-unit transformation invariance; exact scalar Gaussian conditioning; repeated-input covariance behavior; noise-aware information selection; variance reduction against direct conditioning; decision VOI against an independent closed-form Gaussian sign-error result; conformal rank edge cases; group-level calibration counts; finite tail censoring probabilities; invalid input rejection; source-hash rejection; and audit/unrevealed-outcome isolation in acquisition.

Nineteen tests passed in the current environment. These protect specific mathematical and leakage contracts, not the entire scientific hypothesis. Decision VOI uses Gaussian quadrature with a successive-order tolerance of 0.003 in risk-per-cost units; this is a numerical diagnostic, not a certified bound on quadrature error. GP uncertainty is conditional on fixed hyperparameters. Conformal primitives are not applied to this dataset because the necessary independent calibration groups have not been established.

## Execution and repair record

1. Created a local Python 3.13 virtual environment and installed pinned direct dependencies. The initial installation output exists in the chat tool transcript; it was not captured to a local file. `requirements-lock.txt` records the final complete environment.
2. Downloaded and hashed the two primary workbooks. The optional secondary source failed with HTTP 403; primary-source work continued.
3. Initial test collection failed while loading the SciPy 1.15.3 macOS binary. Preserved `tests-initial.txt`; upgraded to SciPy 1.16.2 and retained `scipy-repair.txt`. No scientific code workaround bypassed the failure.
4. Baseline tests passed (12), then replay/leakage tests passed (17), then censoring/source-admission tests passed (19). The numbered logs retain these stages.
5. Ran both actual-data benchmarks. Full prediction tables, Hill diagnostics, data audit and acquisition traces were saved, including negative comparative findings.
6. Fresh-environment reproduction **passed**: the locked dependencies installed, all 19 tests passed, both benchmarks ran, and six deterministic artifacts matched byte for byte. `scripts/verify_reproduction.py` performed this check in a temporary virtual environment. See `artifacts/logs/reproduction.json` and the full `fresh-environment.txt` transcript. This is same-machine clean-environment reproduction, not independent laboratory replication.

## Remaining milestone requirements

The requested 50% milestone must represent a validated central computational workflow, not half of a checklist of small modules. Current work establishes executable baselines and initial policy evaluation, but these required elements remain open:

- Establish usable biological units, dose semantics, censoring and control covariance; obtain stronger target evidence where the public supplement cannot supply it.
- Lock a development/independent-confirmation boundary and analysis protocol. Existing explored data cannot become fresh test data again.
- Diagnose the abrupt-response and acquisition failures; evaluate advanced models and decision objectives against tuned strong baselines with matched budgets and ablations.
- Test sensitivity to noise, priors, thresholds and nonadditive assay costs; quantify uncertainty at a defensible biological level.
- Integrate justified uncertainty, supported-domain checks and abstention into an end-to-end reviewer workflow.

External/prospective validation, full scientific novelty assessment, report/video/writeup preparation and competition-rule resolution remain later requirements under the original plan. No percentage of winning probability is implied by implementation progress.

## Manual interventions

No manual action is needed to run the current pipeline beyond the README commands and internet access for dependencies/data. Scientific steps requiring external information are:

1. Supply authorized donor/chip/batch identities, concentration definitions, control measurements and detection-limit metadata if available through your collaborators; otherwise these must be requested from a legitimate source before stronger claims.
2. Arrange qualified review of the assay endpoint, threshold, feasible actions and experimental costs before any real experiment recommendation.
3. Resolve competition eligibility, registration, controlling rubric and submission rights before publication or entry. No forms were submitted, accounts changed, messages sent, paid services provisioned or public repository created.

The HTTP 403 secondary source is optional at this stage; it is not a reason to fabricate its contents or stop primary-data development. No user action is presently required to continue local implementation.
