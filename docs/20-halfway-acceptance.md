# Public-data halfway milestone: acceptance and delivery

The user authorized self-determined acceptance criteria and public-data-only development when resuming the goal. This supersedes the earlier unresolved choice of validation route. The exact criteria are frozen in `configs/milestone-acceptance.json`.

**Acceptance result: PASS for M1–M5.** The isolated cold start downloaded the public sources without a raw cache, passed all 61 tests, and reproduced 30 deterministic result artifacts byte for byte. The tested implementation was then checked against the current source, scripts, tests, configurations and example inputs. `artifacts/halfway-acceptance.json` records this audit. This confirms the defined 50% delivery-stage milestone, with the scientific and ranking limits below.

## Meaning of halfway

The plan now has ten delivery stages. The first five establish a usable, tested research system; the remaining five establish stronger scientific contribution and submission readiness. Completing stages M1–M5 is the **50% delivery-stage milestone**. It does not imply that stages require equal effort, that half of all eventual code is written, that scientific uncertainty is halved, or that there is a 50% probability of winning.

The scope remains assay planning for the competition. Negative results and unproven scientific claims are retained. The definition does not turn retrospective performance into prospective evidence or label software tests as biological validation.

| Stage | Acceptance evidence |
|---|---|
| M1: Traceable public-data foundation | Empty-cache source download, pinned hashes, strict adapters, exclusions and original row provenance |
| M2: Tested mathematical core | Scientific tests with warnings treated as errors, including analytic identities and outcome-isolation checks |
| M3: Comparative evaluation | Dose-group and chronological splits; strong simple baselines; complete policy curves and uncertainty diagnostics |
| M4: Working research workflow | Real-data JSON request produces predictions, uncertainty, support/abstention and measurement ranking with provenance |
| M5: Independent execution environment and handoff | Extracted checkpoint, fresh environment, no raw cache, successful public downloads, tests and 30 deterministic result matches |

M5 is verified by `scripts/verify_cold_start.py`, not inferred from an existing environment. The authoritative result is referenced by `artifacts/logs/latest-cold-start.json`; its timestamped record contains command exit codes, the empty-cache check and before/after result hashes. The adjacent transcript contains the full run output.

## Remaining half, with the original ambition preserved

M6 is a demonstrable technical contribution that survives tuned baselines and ablations. M7 is independent confirmation on suitable public cohorts not used to select the method or claim. M8 is a defensible operational cost/error result with justified endpoint, costs, feasible actions and uncertainty. M9 is the technical report, runnable demonstration, video and writeup. M10 is competition-rule, eligibility, redistribution-rights and release/submission readiness review.

Public-data-only is the adopted route. A private dataset or collaborator is no longer a prerequisite for progressing through the plan. Appropriate public evidence must still support each scientific claim; missing metadata cannot be invented, and a published aggregate table does not become independent biological replication by adding more random seeds.

## Results the milestone does and does not support

The software implements and tests Hill, interpolation, GP, model-mixture and ridge methods; exact Gaussian conditioning; uncertainty decomposition; acquisition; grouped and chronological evaluation; and a fail-explicit research workflow. It demonstrates reproducible retrospective analyses on real public records.

The comparisons also show that simple interpolation/ridge methods often win and acquisition gains vary. Current results do not establish a novel superior algorithm, calibrated deployment uncertainty, real laboratory savings, clinical utility or external biological generalization. Those are explicit remaining stages, not hidden failures or claimed achievements.

The assurance available at this milestone is verified functional behavior and reproducibility in the tested conditions. No implementation can guarantee a panel's future ranking. Top placement remains the strategic objective; the handoff must not promise it as an achieved or certain result.

## Manual interventions and execution

No manual intervention is required for the public-data research workflow beyond running the documented commands with internet access. No paid service, account credential, cloud GPU, private dataset or Google Drive access is required. No external messages, registration, publication or submission have been performed.

Before eventual submission, the participant must resolve eligibility/registration and authorize public release/submission. The team must also settle the scientific context-of-use choices required by M8, using evidence suitable to the public-data route. These remaining actions do not block the first-half software milestone.

Start with `README.md`, the actual-data request in `examples/ola_ibet_request.json`, and `artifacts/workflow_v1/response.json`. Documents 12–19 preserve the implementation history, numerical repairs, unfavorable comparisons and logging limitations. The latest checkpoint ZIP includes the source, configurations, tests, evidence and available logs with a per-file checksum manifest.
