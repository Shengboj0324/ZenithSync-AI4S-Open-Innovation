# ZenithSync — AI4S Open Innovation

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

## Recommendation

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

## Evidence status

- **Verified:** directly read in a cited source.
- **Inference:** our interpretation, not an organizer commitment.
- **Proposal:** a design, target, threshold, or experiment to test.
- **Unresolved:** conflicting instructions or insufficient evidence.

No competition score, rank, biological benefit, or assay reduction has been achieved. Exploratory reconstruction and replay results are available. Score examples in the planning documents are internal scenarios, not predictions of actual judging. The official sites publish different rubrics. Kaggle names one track judge; the wider Pazhou expert pool is not a confirmed track panel.

## Scope

The original planning round covered research and documentation only. The subsequently authorized implementation round adds model primitives, measured-data adapters, tests, and exploratory evaluations. No registration, publishing, organizer contact, or submission has occurred. There is no development schedule or time-budget optimization.

**Next scientific gate:** resolve biological metadata and expand independent evidence before adopting a final claim. The initial replay does not demonstrate superiority of decision-aware acquisition.
