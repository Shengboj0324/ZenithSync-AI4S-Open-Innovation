# Uncertainty evaluation and completion audit

Updated October 6, 2026. The previous goal turn made progress by evaluating measurement policies and preserving reproduction logs. This iteration evaluates the uncertainty used in decisions and checks the requested outcome against current evidence.

## Measured uncertainty diagnostics

`scripts/uncertainty_audit.py` predicts every later concurrent-treatment generation from strictly earlier records, using the ridge model and fixed noise SD 0.1. Intervals concern new observed aggregate responses. Threshold-event probabilities also concern the observed response here; they are not the latent-event probabilities shown by the research workflow. This distinction prevents a noisy observation from being treated as exact latent ground truth.

| Context | Observed 90% interval coverage | Mean interval width | Ridge Brier | Training-prevalence Brier |
|---|---:|---:|---:|---:|
| FAC | 0.9286 | 0.3823 | 0.000011 | 0.000000 |
| OLA–IBET | 0.9250 | 0.3512 | 0.1303 | 0.2117 |

These pooled averages are descriptive. FAC generation three has only 5/7 covered outcomes (71.4%). OLA–IBET generation three has 8/10 covered outcomes. Overall coverage above 90% does not establish group-conditional, future-lab or independent-donor coverage.

FAC has zero below-0.5 outcomes in the 28 evaluated rows. Its almost perfect classification score cannot establish sensitivity to below-threshold events; an always-negative prevalence baseline scores perfectly on this selected sample. OLA–IBET has 11 such outcomes in 40 rows. Its improved Brier score relative to training prevalence is useful exploratory evidence, but neither threshold relevance nor biological independence has been established.

## Abstention tradeoff

The audit reports all operating points rather than choosing one using test performance. For OLA–IBET:

| Abstention cost | Fraction receiving a decision | Errors among accepted decisions |
|---|---:|---:|
| 0.01 | 27.5% | 0/11 |
| 0.05 | 40.0% | 0/16 |
| 0.10 | 50.0% | 1/20 |
| 0.20 | 77.5% | 4/31 |
| 0.30 | 87.5% | 4/35 |
| 0.50 | 100.0% | 7/40 |

Costs are illustrative, with equal unit error costs. Zero observed errors in a small accepted subset do not guarantee low future error, and aggressive abstention reduces usefulness. No row is selected here as a validated deployment operating point.

## Evidence files

- `artifacts/uncertainty_audit_v1/predictions.csv`: every prediction, observed outcome, interval, probability and standardized residual.
- `by_generation.csv`, `summary.csv`: coverage/width/Brier comparisons, including the prevalence reference.
- `selective_risk.json`: complete abstention grid, accepted counts, errors and realized losses.
- `protocol.json`: target, assumptions and forbidden claims.
- `artifacts/logs/uncertainty-audit-current.txt`: the full diagnostic output.
- `artifacts/logs/uncertainty-audit-reproduction.json`: five files reproduced byte for byte on a separate same-environment run. This is not mislabeled as a new clean-environment or biological replication. The previously verified 25-artifact clean-environment record remains separately available.

## Requirement-by-requirement completion assessment

| Requested or planned requirement | Current authoritative evidence | Status |
|---|---|---|
| Actual implementation | Executable `src/zenithsync/` modules and scripts | Implemented research core |
| Mathematical validation | 61-test suite, analytic identities, counterexamples, numerical repairs | Established for tested contracts; not a universal proof |
| Actual-data evaluation | Two study sources; dose-held-out and generation-aware predictions, policy traces | Completed exploratory evaluations |
| End-to-end workflow | Strict request CLI, real-data example, explicit support/abstention, code/request hashes | Working research workflow |
| Reproducibility | Fresh environment: 25 deterministic artifacts matched; current audit rerun: five matched | Established within documented machine/environment scope |
| Strong comparative result | Simple models often win; policy gains vary across budgets and contexts | Consistent superiority not established |
| Correct uncertainty for intended deployment | Current descriptive coverage and abstention audit; missing independent groups | Not established |
| Reduced real measurement cost at controlled error | Retrospective aggregate-record budgets only; no approved cost/error specification | Not established |
| Half-complete competition solution | Substantial computational functionality, but no agreed quantitative fraction or completed scientific gate | Cannot certify 50% from line counts or test counts |
| Guaranteed success / top position | No judging outcome, controlling panel/rubric resolution or evidence yielding such a guarantee | Cannot be guaranteed by implementation |
| Logs and implementation records | Documents 12–18, phase logs, manifests, traces, source checkpoints and archived reproduction runs | Available with disclosed historical logging gaps |
| Manual interventions identified | Pending data/collaborator question; endpoint/cost/metadata and independent-validation needs | Documented; user resources unconfirmed |

The implementation is therefore not marked complete. Additional unit tests alone cannot resolve the missing biological evidence or guarantee an externally judged competition outcome. The full objective has not been replaced by an easier software-only target.

## Next consequential work

Complete the remaining source-semantic admission and evaluate whether available public evidence can support a prespecified assay decision with adequate independent units. Integrate the uncertainty findings into the reviewer-facing evidence presentation. The implementation should retain the best simple baselines and explicitly distinguish engineering correctness, retrospective utility and prospective scientific validity.

No user action is needed to run existing artifacts. Independent metadata/data or a qualified biological collaborator would materially change the validation path; that question remains pending. Any future cost, threshold or generalization claim requires appropriate evidence rather than an optimistic interpretation of this audit.
