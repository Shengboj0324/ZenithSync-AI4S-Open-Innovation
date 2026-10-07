# ZenithSync — AI4S Open Innovation

**Local research implementation and presentation package are prepared:** the [first frozen independent confirmation](docs/27-independent-confirmation-results.md) passed its primary and assay-count tests on 100 patient IDs. Exact selection reduced MSE 32.8% versus random selection under the same GP, but only 0.66% versus greedy selection. The suite passes 127 tests. A [local measured-well planner](docs/28-integrated-well-workflow.md) is implemented and browser-checked. A 17-page report, narrated review video and Writeup candidate are prepared. A clean environment reproduced 27 expanded confirmation/demo artifacts byte for byte. External scientific review and release gates remain unfinished; no competition rank is guaranteed.

**Team:** ZenithSync; Shengbo Jiang, sole member and main contributor. Confirmed category: Tool & Platform. [Current rubric interpretation and review handoff](docs/34-team-rubric-and-review-handoff.md).

**Implementation handoff:** [Completion evidence and publication checklist](docs/35-implementation-completion-handoff.md). Registration, eligibility and licensing are user-confirmed; publication remains assigned to the user.

**Planning entry point:** [Research strategy and judging priorities](docs/21-strategy-refresh.md), with [additional mathematical back-checks](docs/22-design-mathematical-audit.md) and a [public-data confirmation plan](docs/23-public-confirmation-plan.md). Those strategy documents preserve their planning context; subsequent implementation and evidence are recorded below.

**Current acceptance plan:** the user authorized public-data-only development and self-determined milestone criteria. See [the halfway milestone](docs/20-halfway-acceptance.md). Earlier blocked-status notes are historical; independent private data is not a prerequisite for this route.

**M1–M5 accepted:** 61 tests passed and 30 result artifacts reproduced byte for byte from an isolated checkout, fresh environment and empty raw-data cache. This is the defined 50% delivery-stage milestone. Scientific superiority and competition placement remain unproven; stages M6–M10 are in progress and are not collectively accepted.

Research and competition strategy with an initial executable research pipeline, updated **October 6, 2026**. Scientific superiority and competition readiness are not established. See the [implementation record](docs/12-implementation-record.md) for current evidence and remaining work.

## Run the current pipeline

Python 3.13 on macOS ARM was used for validation. From the repository root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python scripts/fetch_public_data.py
.venv/bin/python scripts/fetch_yakavets_repository.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/benchmark.py
.venv/bin/python scripts/replay_benchmark.py
.venv/bin/python scripts/generation_benchmark.py
.venv/bin/python scripts/verify_reproduction.py
```

The downloader retrieves two public Liver-Chip supplements and verifies pinned bytes on subsequent runs. Results and logs are in `artifacts/`. Replay budgets count revealed dose-group means, not chips or experimentally validated assay costs. Source concentration units and donor/chip identities remain unresolved; no physical experiment recommendation is issued.

## Run the integrated local demo

```sh
.venv/bin/python scripts/serve_demo.py
```

Open http://127.0.0.1:8765/. See [the workflow guide](docs/28-integrated-well-workflow.md) for the CLI, schema, source provenance and limitations.

## Original recommendation

Develop **ZenithSync Assay Planner**: an uncertainty-aware system that learns organ-on-a-chip dose–response relationships and selects informative follow-up measurements. Test whether it can reach a prespecified level of decision accuracy with fewer measurements than strong statistical and active-learning baselines.

Use liver-chip data as the initial real-chip evidence candidate, conditional on checking underlying measurements, independent sample counts, and licenses. A neural extension requires adequate independent neural-chip data. Public organoid recordings alone do not establish neural-chip or unseen-drug validity.

The contribution must be a demonstrable improvement in learning and decisions under small, heterogeneous experiments. The proposed methods combine established components; originality and superiority remain research hypotheses.

## Documentation

| Document | Purpose |
|---|---|
| [Competition intelligence](docs/01-competition-intelligence.md) | Requirements, eligibility, conflicts, awards |
| [Judging strategy](docs/02-judging-strategy.md) | Verified judges, both rubrics, evidence-to-score mapping |
| [Project selection](docs/03-project-selection.md) | Alternatives, sensitivity analysis, conditional pivots |
| [Data and prior art](docs/04-data-and-prior-art.md) | Suitability, sample limits, licenses, methodological precedents |
| [Mathematical specification](docs/05-mathematical-specification.md) | Models, estimands, uncertainty, acquisition, failure cases |
| [Validation protocol](docs/06-validation-protocol.md) | Leakage, baselines, ablations, power, acceptance gates |
| [Execution blueprint](docs/07-execution-blueprint.md) | Work packages and future engineering contracts |
| [Submission and defense](docs/08-submission-and-defense.md) | Writeup, report outline, demo, judge questions |
| [Risks and clarification](docs/09-risks-and-clarifications.md) | Unresolved issues and unsent organizer questions |
| [Sources](docs/10-source-register.md) | Primary links, access status, evidence boundaries |
| [Logical and numerical audit](docs/11-logical-and-numerical-audit.md) | Checked calculations and counterexamples |
| [Implementation record](docs/12-implementation-record.md) | Actual code, tests, measured results, logs, remaining gates and manual interventions |
| [Model uncertainty and acquisition audit](docs/13-model-uncertainty-and-acquisition-audit.md) | Bayesian model averaging, numerical repairs, sensitivity study and comparative results |
| [Nested baselines and second source](docs/14-nested-baselines-and-second-source.md) | Training-only tuning, stronger simple baselines and 144 additional source records |
| [Generation-aware evaluation](docs/15-generation-aware-evaluation.md) | Second-assay admission, temporal isolation and matched baseline results |
| [Research workflow](docs/16-research-workflow.md) | Run an actual-data request with predictions, abstention, acquisition and provenance |
| [Measurement-policy evaluation](docs/17-measurement-policy-evaluation.md) | Recorded-pool budget curves, isolated audit outcomes and conditional uncertainty |
| [Uncertainty and completion audit](docs/18-uncertainty-and-completion-audit.md) | Coverage, abstention tradeoffs and requirement-by-requirement evidence status |
| [Checkpoint handoff](docs/19-checkpoint-handoff.md) | Review path, packaged evidence, sequential-data decision and manual dependencies |
| [Halfway milestone](docs/20-halfway-acceptance.md) | Authorized acceptance criteria, cold-start evidence and the remaining five delivery stages |
| [Strategy refresh](docs/21-strategy-refresh.md) | Live rule/judge checks, score-to-evidence mapping and research priorities |
| [Additional mathematical audit](docs/22-design-mathematical-audit.md) | Shared controls, correlated acquisition, greedy counterexample and stopping limits |
| [Public confirmation plan](docs/23-public-confirmation-plan.md) | Two new candidate cohorts, admission and outcome-blinding protocol |
| [Second-half development](docs/24-second-half-development.md) | Implemented correlated design, audited public source, reproducible logs and remaining scope |
| [Correlated-well evaluation](docs/25-correlated-well-evaluation.md) | Group-held-out tuning, measured GP comparisons, exact batch design and explicit negative evidence |
| [Independent cohort admission](docs/26-independent-cohort-admission.md) | Blinded design projection, verified patient mapping and frozen confirmation hypotheses |
| [Independent confirmation results](docs/27-independent-confirmation-results.md) | First frozen evaluation, patient-weighted effects, assay-count test, conservative intervals and full limits |
| [Integrated measured-well workflow](docs/28-integrated-well-workflow.md) | Local API, CLI and browser demo; strict contracts, actual-data provenance and UI validation |
| [Contribution and prior-art assessment](docs/29-contribution-and-prior-art.md) | Established mathematics, precise empirical contribution and strongest-baseline limits |
| [Technical report source](docs/30-technical-report.md) | Self-contained scientific report; rendered PDF in `output/pdf/` |
| [Kaggle Writeup candidate](docs/31-kaggle-writeup-candidate.md) | Local draft with current evidence and pending team/publication facts |
| [Final local package and release gates](docs/32-local-package-and-release-gates.md) | Cold-start evidence, presentation checks, logs and remaining human decisions |
| [Accessibility and release audit](docs/33-accessibility-and-release-audit.md) | Keyboard repairs, maximum-dose UI check, contrast measurements and dependency/data-rights inventory |

## Evidence status

- **Verified:** directly read in a cited source.
- **Inference:** our interpretation, not an organizer commitment.
- **Proposal:** a design, target, threshold, or experiment to test.
- **Unresolved:** conflicting instructions or insufficient evidence.

No competition score, rank, biological benefit or prospective assay reduction has been achieved. Frozen retrospective confirmation supports a bounded well-count efficiency result; earlier exploratory and negative results remain available. Score examples in the planning documents are internal scenarios, not predictions of actual judging. The official sites publish different rubrics. Kaggle names one track judge; the wider Pazhou expert pool is not a confirmed track panel.

## Scope

The original planning round covered research and documentation only. The subsequently authorized implementation round adds model primitives, measured-data adapters, tests, and exploratory evaluations. No registration, publishing, organizer contact, or submission has occurred. There is no development schedule or time-budget optimization.

**Next delivery gates:** team attribution/category confirmation, external scientific review, resolution of material competition-rule ambiguities, and authorized public release/submission. The initial replay remains negative; the later frozen independent confirmation supports the narrower claims in document 27.
