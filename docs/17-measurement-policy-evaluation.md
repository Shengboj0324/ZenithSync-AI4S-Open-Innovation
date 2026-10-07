# Measurement-policy evaluation on recorded experiments

Updated October 6, 2026. The previous iteration was progress: an executable request-to-decision workflow was implemented and reproduced. This iteration tests the measurement-selection component against strong simple policies. The original goal remains active; no prospective assay savings or competition outcome is established.

## Protocol and separation

`src/zenithsync/linear_replay.py` starts from generation zero, reveals selected records from generations one through three, and evaluates predictions on generation four. Every policy uses the same ridge predictor, initial observations and final-generation audit. Fifty random seeds describe random-policy variability. Space filling and integrated ridge variance reduction are deterministic comparisons.

The final generation's outcomes enter scoring only. They never enter fitting or acquisition, and perturbation tests verify this isolation. A separate test changes unrevealed pool responses and checks that the first acquisition cannot change. The entire candidate pool consists of actual recorded experiments; unmeasured response values are never synthesized as benchmark truth.

This is **retrospective, exploratory replay**. Generation four was previously examined during model comparison, so it is not an independently untouched confirmatory cohort. The original experimental policy selected the recorded pool, which limits counterfactual interpretation. Historical feasibility permits comparison on these recorded candidates; unlike the interactive workflow, this replay does not impose a training convex-hull exclusion. Therefore these results are evidence about the acquisition component, not validation of every gate in the interactive workflow.

Budgets count additional revealed aggregate records. The initial seven FAC or ten OLA–IBET records are additional required information. A record is not assumed to equal one chip, one independent biological replicate or a known monetary laboratory cost.

## Results across budgets

| Context | Policy | RMSE at +5 | RMSE at +10 | RMSE at +15 |
|---|---|---:|---:|---:|
| FAC | Random mean | 0.080118 | 0.079516 | 0.082882 |
| FAC | Space filling | 0.070245 | 0.071207 | 0.076951 |
| FAC | Ridge variance | 0.079550 | 0.070741 | 0.073190 |
| OLA–IBET | Random mean | 0.120727 | 0.115030 | 0.112771 |
| OLA–IBET | Space filling | 0.118259 | 0.121926 | 0.123164 |
| OLA–IBET | Ridge variance | 0.112461 | 0.114936 | 0.113635 |

Lower error is preferable. Variance selection helps at some budgets, but space filling wins others. Adding observations sometimes increases audit error; under model misspecification and a changing experimental distribution, posterior variance reduction does not guarantee lower realized error.

To avoid relying on a favorable single budget, `scripts/summarize_linear_policy.py` also computes the trapezoidal average RMSE over every budget from zero through fifteen. This is a descriptive analysis added after observing the curves, not a preregistered primary endpoint.

| Context | Random mean | Space filling | Ridge variance |
|---|---:|---:|---:|
| FAC | 0.080285 | **0.075153** | 0.077438 |
| OLA–IBET | 0.118915 | 0.122130 | **0.115364** |

The random-policy mean has approximate 95% Student-t Monte Carlo intervals of [0.077842, 0.082728] for FAC and [0.116190, 0.121639] for OLA–IBET. These concern estimated performance over random selection seeds **conditional on this fixed dataset**. They are not biological confidence intervals and do not create fifty independent assays. Thirty percent of random seeds outperform ridge variance on FAC's whole curve; 42% do so on OLA–IBET. A modest mean advantage is not universal dominance.

No post-hoc threshold is chosen to convert these curves into a claimed percentage of assay savings. A meaningful cost-at-controlled-error result still needs an independently justified error target, real costs, appropriate uncertainty and independent validation.

## Implementation and execution evidence

- `artifacts/linear_policy_v1/protocol.json`: exact assumptions and scope differences.
- `splits.json`: original source-row membership for initial, pool and audit sets.
- `traces.jsonl`: all selected indices, audit predictions, observed audit values and budget-level errors.
- `summary.csv`: complete budget curves, including random seed ranges.
- `full_budget_metrics.csv`, `full_budget_comparison.json`: every seed's integrated error and conditional Monte Carlo comparison.
- `artifacts/logs/tests-linear-policy.txt`: 61 tests passing with warnings treated as errors.
- `artifacts/logs/linear-policy-v1.txt`, `linear-policy-comparison.txt`: execution and analysis output.
- `artifacts/logs/reproduction.json`, `fresh-environment.txt`: fresh-environment reproduction evidence, now comparing 25 deterministic artifacts.

Reproduction transcripts are now additionally archived by start timestamp under `artifacts/logs/reproductions/`, with protection against changing an existing archived run. The current run was archived and byte-checked. Earlier intermediate fresh-environment transcripts were not all retained separately; the initial and latest records, phase-specific command logs and chat tool history are available. Missing historical logs are not reconstructed or presented as originals.

Run:

```sh
.venv/bin/python scripts/linear_policy_benchmark.py
.venv/bin/python scripts/summarize_linear_policy.py
```

## Completion boundary and manual needs

The project has a functioning prediction/decision/acquisition chain, two assay-context evaluations, explicit negative comparisons, numerical tests and reproducibility records. The central strong claim—reliably reducing real measurement cost at a controlled error rate—remains unproven. These results support continued development, not confirmation of the user's requested guaranteed-success milestone.

Public-data development can continue. The pending question about access to independent data or a biological collaborator remains relevant. Qualified endpoint/cost specification, biological metadata and independent confirmation are still needed to cross the scientific validation gate. No external messages, experiments, publishing, registration or paid resources were initiated.
