# Research strategy: evidence needed for a top-position submission

Updated October 6, 2026. This document is a planning supplement. It introduces no new implementation or measured scientific result. Existing implementation records in Documents 12–20 are separate from the proposals below.

## Recommendation

Keep **ZenithSync Assay Planner** as the conditional flagship: help an assay researcher choose the next feasible measurement and decide when available evidence is sufficient. Make the central contribution a demonstrable improvement in measurement efficiency at controlled predictive or decision error. Do not make a broad digital-twin claim from interpolation experiments.

The decisive research question is whether accounting for experimental dependence, model uncertainty, and the actual decision improves acquisition over strong simple alternatives. A sophisticated posterior alone is insufficient. The method must beat a tuned baseline on the same observations, costs, initial measurements, and audit outcomes. If it does not, retain the stronger method and revise the scientific claim.

Read this alongside [project selection](03-project-selection.md), [mathematical specification](05-mathematical-specification.md), [validation protocol](06-validation-protocol.md), and the additional [mathematical audit](22-design-mathematical-audit.md). No development time constraint is imposed.

## What the live competition pages establish

The rendered [Kaggle overview and evaluation](https://www.kaggle.com/competitions/ai-4-s-open-innovation-artificial-intelligence-for-life-scien/overview/evaluation) were read again. Kaggle still assigns 30% to impact, 30% to technical approach, 20% to validation, and 10% each to reproducibility and presentation. The [Pazhou track page](https://www.aicompetition-pz.com/topic_detail/26) still gives innovation/completion/value/completeness/trust weights of 30/25/20/15/10. Neither page resolves the discrepancy.

Kaggle still requires a registration form before submission, a category declaration, and a Writeup containing a public video, public code and technical report. A video of at most five minutes and a self-contained report of approximately 15–20 pages are the relevant presentation design targets. The live deadline tooltip remains October 10, 2026, 08:59:59 PDT. This date is recorded as an entry condition, not used to reduce research ambition.

The refreshed judge section names only **ZHOU YINGTONG**. The linked [aifckaggle profile](https://www.kaggle.com/aifckaggle) still has no biography. The general [Pazhou expert pool](https://www.aicompetition-pz.com/expert) does not establish track assignments. Document 02 lists the organizer-provided expert information with that boundary. No personal expertise, affiliation, preferences, or likely scoring behavior should be inferred from a name match.

Prepare for four forms of scrutiny: biological relevance, mathematical validity, experimental fairness, and runnable engineering. These are review perspectives inferred from the criteria, not claims about four identified judges. Sponsor interest in neural chips supports discussing future transfer, but does not justify an unvalidated neural application or an assumed scoring bonus.

## Research packages, ordered by dependency

| Package | Concrete deliverable | Promotion condition |
|---|---|---|
| Context and admissibility | One assay decision; endpoint, units, experimental hierarchy, cost and license cards | The data can identify the claimed task |
| Reference evaluation | Frozen splits; strong simple models; standard acquisition policies | Same information and budget; no audit leakage |
| Precise contribution | Closest-method comparison and one mathematical difference | Difference has a testable mechanism, not only a new name |
| Development experiments | Full budget curves, ablations and misspecification stress tests | Improvement is not restricted to a selected seed/budget |
| Independent confirmation | Frozen protocol plus an untouched suitable public cohort | Claim survives without post-test tuning |
| Operational evidence | Feasible candidate set; real cost categories; uncertainty and abstention audit | Benefit remains at matched error and decision coverage |
| Judge-facing package | Technical report, actual workflow demo, claim ledger, public reproduction instructions | Every headline traces to a run and source |
| Release review | Rights, eligibility, controlling rules, independent review and access checks | No unresolved mandatory condition is described as satisfied |

These are evidence dependencies, not equal effort estimates or a development schedule. An unsuccessful confirmation remains a valid scientific result and cannot be repaired by silently replacing the holdout.

## Where technical advancement should concentrate

**Experimental dependence.** Shared controls, repeated wells and donor effects can make additional measurements redundant or make an additional control particularly valuable. Develop a joint observation model only where metadata identifies these relationships. Compare it with a diagonal-noise ablation. Document 22 specifies the covariance and acquisition calculations; it does not claim that these established Gaussian identities are new.

**Robust decisions under misspecification.** Do not rely solely on posterior variance when the response family may be wrong. Evaluate fixed and integrated hyperparameters, simple-model alternatives, and stress cases where the assumed shape fails. Recent work already addresses robust GP acquisition and model misspecification: [Takeno et al., ICML 2025](https://proceedings.mlr.press/v267/takeno25a.html) and [Tang et al., AISTATS 2026](https://proceedings.mlr.press/v300/tang26d.html). Their abstracts establish close prior art; a full method audit and task-compatible reproduction are prerequisites to an originality claim.

**The stopping decision.** Define whether the researcher needs accurate curve reconstruction, an assay-threshold decision, or a best-condition search. These objectives differ. Optimize and evaluate the chosen objective explicitly; do not select a favorable metric afterward. Count abstentions and required controls in operational cost.

**External confirmation.** Use suitable organoid cohorts to test transfer of the statistical procedure, while retaining an explicit boundary between organoids and perfused chips. The public-source admission plan is in [Document 23](23-public-confirmation-plan.md). Do not describe a new download of already evaluated data as independent confirmation.

## Evidence mapped to score

| Dimension | Strong evidence to prepare | Weak substitute to avoid |
|---|---|---|
| Impact / practical value | Named decision, baseline workflow and measured cost at matched reliability | General claims about accelerating drug discovery |
| Technical innovation | Exact prior-art difference, assumptions, derivation, fair ablation | Combining standard GP, conformal and UI modules |
| Results / effectiveness | Prespecified paired effect, uncertainty, external confirmation and failures | Best seed, pooled score or selected successful case |
| Reproduction / completeness | Clean public rerun and consistent report/code/data versions | A functioning interface without recoverable results |
| Presentation / trust | Early actual run, one clear contribution, visible uncertainty and limits | A large set of unsupported capabilities |

Optimize evidence that supports several dimensions at once. For example, a credible cost-versus-error experiment strengthens impact, validation and usefulness. Do not translate subjective internal ratings into a probability of winning.

## Decision rules before final testing

1. Choose the strongest baseline on development data; freeze its tuning procedure and the proposed method together.
2. Freeze one primary endpoint and comparison. Preserve secondary metrics and all failed runs.
3. Require a practically meaningful effect and an uncertainty interval supporting improvement at the actual independent biological unit. Document 06's 20% cost reduction is a proposed target, not an achieved result or official requirement.
4. Report measurement efficiency only within observed candidate support unless prospective evidence exists. No model-generated outcomes may serve as biological ground truth.
5. If the primary result fails, publish the limitation and restrict the claim. A post-hoc revised method needs a new confirmation cohort.
6. Keep a simpler model when it performs better. Technical ambition means better justified reasoning and evidence, not mandatory model complexity.

## Manual decisions required before eventual submission

The team must establish member eligibility, completed registration, contributor roles and permission to submit its work. The organizer must clarify conflicting rubrics, the interdisciplinary bonus and any material ownership or registration ambiguity. A domain reviewer should validate endpoint meaning, feasible experimental actions and realistic cost assumptions. An independent reviewer should reproduce and challenge the final claim.

Prepared organizer questions already appear in [Document 09](09-risks-and-clarifications.md); none were sent. These external facts do not prevent a complete technical plan, but a local implementation cannot resolve them by assertion. No ranking can be guaranteed from the public information available.

## Verification of this documentation update

All 24 Markdown documents in the README/docs set passed local-link, code-fence and display-math delimiter checks. Exact rational arithmetic confirmed Document 22's conditional variance reduction of 1000/2751 and shared-control variance ratio of 5.5. Git whitespace checks passed. These checks validate document consistency and the stated calculations; they do not validate an unimplemented research proposal or future empirical performance. No project source code, model configuration or benchmark result was changed in this update.
