# Local research package, validation and remaining release gates

> Current status update: the user has verified registration, eligibility and licensing, and will handle publication. See [the current implementation handoff](35-implementation-completion-handoff.md). Earlier pending statements below preserve the audit history and no longer request those confirmations.

## Current status

The bounded public-data research implementation, local demonstration, 17-page technical report, narrated review video and Kaggle Writeup candidate are prepared. The expanded confirmation workflow has passed fresh-environment reproduction. This is a local review candidate, not a completed public submission or a guarantee of placement. Team attribution is user-confirmed: ZenithSync, with Shengbo Jiang as sole member and main contributor. Tool & Platform is confirmed. Shengbo Jiang is the designated self-reviewer; review completion is not yet recorded. The user will handle publication after local implementation.

The strongest scientific result remains a frozen retrospective comparison: 32.82% lower MSE than random joint-GP purchasing, but only 0.66% lower MSE than greedy joint-GP selection. The registered well-count comparison passed at 20-25% fewer purchased wells under its isolated-context accounting. All limitations in documents 27-30 apply.

## What was implemented in this delivery

- Strict measured-well workflow, CLI and loopback HTTP/browser demonstration; explicit research scope, positive-signal requirement, real measured controls, charged budgets, uncertainty and provenance.
- Exact conditional subset search with verified symmetry groups, using the unchanged frozen scientific primitives. The interactive adapter caps enumeration at 10,000 representatives and rejects larger designs.
- Request validation for duplicate keys, invalid roles/units, malformed or oversized numbers, absent anchors and budgets. Tests cover actual HTTP requests and browser error recovery.
- Prior-art and contribution assessment distinguishing established GP/design methods from this empirical result.
- Scientific report, Writeup candidate, synthetic-narration video with the actual captured demo output and full on-screen narration.
- An isolated reproduction script and an expanded local archive builder that includes the demo, compressed results and presentation outputs while excluding raw downloads and environments.

## Validation records

The full suite passes **127 tests with warnings treated as errors**. Browser checks confirm budget-three and budget-one selections, duplicate-key errors, cleared stale results, reset recovery and copyable JSON. CLI and direct-workflow outputs agree. An oversized integer handling gap and an initial test-file syntax error were repaired before final validation; the record does not hide those repairs.

The workflow record is `artifacts/logs/second-half/20261007T041543526405Z/record.json`. Its hash checks confirm that the scientific protocol and frozen model/evaluator files are unchanged. `artifacts/well_workflow_v1/ui-verification.json` records browser checks and limitations. The browser download event timed out at ten seconds; file downloading is not claimed as verified. The CLI and copy field are verified alternatives.

The expanded clean-run record is `artifacts/logs/second-half/20261007T042659143183Z/record.json`. It created a fresh Python 3.13 virtual environment, installed pinned dependencies, started with no raw-data directory, downloaded the pinned Farin and Kryeziu files, regenerated source projections and admission decisions, rebuilt preflight plans, evaluated outcomes, reaggregated/checked results and rebuilt the example. All 127 tests passed and **27 deterministic artifacts matched byte for byte**. The original scientific artifacts were checked again for unchanged hashes.

Two historical records were copied as inputs: the protocol freeze and the extraction record carrying its original timestamp. Raw workbooks, response projection, decisions, plans and results were regenerated. This reproduces known results; it is not a second unseen-cohort confirmation. The new run's internal first-evaluation labels are scoped to its fresh directory. The historical first evaluation remains authoritative.

The local clean directory is recorded in the log and retained for inspection. It is not an independent human review or a claim of all-platform reproducibility. The report/video builders use the bundled document runtime; the synthetic narration builder additionally uses macOS speech and FFmpeg. Those media dependencies are distinct from the pinned numerical environment.

## Presentation artifacts

- `output/pdf/zenithsync-technical-report.pdf`: 17 pages; source `docs/30-technical-report.md`. All pages rendered and visually inspected. Result tables use the saved confirmation values.
- `output/video/zenithsync-review-video.mp4`: under five minutes, 1920x1080 H.264 with AAC audio. Nine scenes, synthetic macOS narration and full narration visible on screen. The demo scene is a labeled captured image, not falsely presented as live interaction.
- `output/video/transcript.txt` and `storyboard.json`: editable narration and content.
- `docs/31-kaggle-writeup-candidate.md`: review candidate with source links and truthful pending release fields.
- `output/pdf/verification.json` and `output/video/verification.json`: page/frame, duration, decode and hash records.

All source video frames were visually reviewed; the encoded demo frame was inspected and the full video/audio stream decoded without errors. Audio stream levels were checked for presence and clipping. No independent listener review or accessibility certification is claimed. A domain reviewer should review the scientific narrative, and the team should listen to the synthetic pronunciation before public use.

## Milestone interpretation

| Stage | Current evidence | Boundary |
|---|---|---|
| M6: technical contribution | Tuned development, frozen transfer comparison, greedy/simple baselines and covariance ablations | Narrow empirical contribution; major algorithmic novelty and universal superiority are not established |
| M7: independent confirmation | Frozen distinct-study evaluation with explicit patient grouping and 100 source patient IDs | Deidentified cross-study patient non-overlap cannot be proved |
| M8: operational reliability | Supported uncertainty diagnostics, finite feasible-set contract and registered well-count result | Retrospective isolated contexts; prospective feasibility, true costs and clinical utility not established |
| M9: judge-facing package | Report, runnable demo, Writeup and under-limit local video prepared | Team attribution/category confirmed; public-access compliance still pending |
| M10: release readiness | Local tests, mathematical checks, provenance and clean rerun completed | External review, controlling-rule facts, eligibility and authorized release/submission remain unresolved |

No equal-effort percentage or probability of winning is inferred from these stages. Successful tests do not replace external conditions.

## Manual interventions required

1. **Registration and eligibility:** verify Shengbo Jiang's eligibility and completed registration. Team name, sole-member attribution and Tool & Platform category are confirmed.
2. **Rule interpretation:** document 34 supplies the requested skeptical working answers. They permit preparation under both rubrics, but cannot establish organizer intent, registration status or ownership rights. The exact unsent questions remain in document 09.
3. **Review:** Shengbo Jiang is the designated contributor self-reviewer; use the review checklist in document 34. This is not independent review, and no completed review is recorded. For the original independent-review milestone, obtain a domain review of the raw-log endpoint, shared-control cost assumptions, source dose discrepancy and prospective feasibility; obtain an independent reproduction/scientific critique. The included computational audit does not substitute for a human review.
4. **Publication decision:** approve the specific repository/report/video destinations, ownership/license choices, attribution and public contents. This local archive includes diagnostic logs with local machine paths and must be reviewed before any public release. No public upload or access expansion has occurred.
5. **Final submission:** verify current submission requirements and public accessibility, then explicitly authorize the Kaggle submission. Terms acceptance, where required, belongs to the user. No registration, terms acceptance, payment or submission was performed.

These are release requirements or missing team facts, not permission needed to perform already completed local development. The technical work has not been reduced because of a development time limit.


## Subsequent local release checks

Document 33 records verified keyboard-focus repairs, selected contrast checks, the maximum-dose display boundary, and a 20-package dependency-license inventory. The frozen scientific files and all 27 reproduced artifacts remain unchanged. These checks extend the local package without closing the outstanding external release gates.
