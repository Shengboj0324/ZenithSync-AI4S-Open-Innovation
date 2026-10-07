# ZenithSync: control-aware assay design

Status: local submission candidate. No public links, registration or submission have been created. The participating team must complete attribution, verify category and eligibility, and authorize publication before using this text.

## Project summary

ZenithSync helps an assay researcher choose additional treatment and vehicle-control wells from an existing single-agent organoid dose design. It models the uncertainty shared by responses that use the same measured control, then selects a finite batch to reduce mean latent log-response variance. The project includes source-audited public data, a frozen independent evaluation, an exact small-pool optimizer and a local browser/CLI demonstration.

## Why it matters

Assay controls carry uncertainty and cost. Treating normalized observations as unrelated can misrepresent how much an additional treatment or control measurement contributes. Our task makes both explicit: every purchased well counts, and prediction is checked against a separate technical plate. The intended benefit is better allocation of a fixed research measurement budget. Clinical decisions and prospective laboratory savings have not been established.

## Technical approach

A fixed Matern 5/2 GP models raw log-response contrasts. Subtracting the same measured reference induces covariance s^2(I+11^T), which the joint model retains. The batch optimizer minimizes mean latent posterior variance over the designed positive doses. Verified permutation symmetries reduce exact enumeration without dropping subset classes.

These are established mathematical components. The contribution is their audited application and frozen public-study transfer evidence, rather than a claim to new GP theory. With fixed parameters, design depends on measured locations; this is not a response-adaptive stopping system.

## Evaluation

The prior was selected on the Farin development study. Its development comparisons were inconclusive and remain reported. Before examining Kryeziu confirmation outcomes, we froze admission rules, parameters, comparison, patient grouping and success criteria. The final primary population contains 6,496 contexts, 148 samples and 100 source patient IDs.

Exact joint-GP selection reduced mean-budget MSE by **32.82% against random selection under the same estimator**, with patient-bootstrap 95% interval **31.34-34.21%**. The strongest included acquisition baseline was close: exact selection improved only **0.66% over greedy joint GP**. Both comparisons are shown to distinguish the practical random-policy contrast from the small algorithmic increment.

A prespecified fixed-budget comparison used **20-25% fewer purchased wells** than its random reference and achieved an MSE ratio of **0.89185**, interval **0.86430-0.92127**. This is retrospective isolated-context well-count evidence. Shared controls are charged in full per context; overhead, audit and historical training costs are not claimed as saved.

Nominal 90% intervals covered 98.05% of audit responses, with mean width 1.34169 natural-log units. They were conservative, not exactly calibrated or distribution-free. Three of 56 drugs had small unfavorable point estimates. Reverse-plate sensitivity supported the primary direction.

## Demonstration and reproduction

The local demonstration accepts measured wells, validates a strict request and returns selected wells, predictions, model-conditional intervals and a request fingerprint. Its example uses actual public Farin measurements with an explicit missing-plate limitation. The current suite passes 127 tests with warnings treated as errors. Mathematical identities, exact enumeration, hidden-outcome isolation and HTTP validation are checked.

The report and repository preserve source hashes, admission/exclusion records, protocol freezes, complete outputs and a serialization-only evaluator repair. A fresh environment and empty raw-data cache reproduced 27 admission, confirmation and demonstration artifacts byte for byte, with all 127 tests passing. Independent external review remains pending.

## Limitations and next validation

This study does not demonstrate clinical benefit, perfused-chip transfer, broad state-of-the-art superiority or prospective savings. Deidentified sources cannot establish cross-study patient non-overlap. The source's lib2 dose-count discrepancy remains flagged. A prospective domain-reviewed experiment is the next test of operational benefit.

## Assets to attach after release review

- Technical report: `output/pdf/zenithsync-technical-report.pdf` (17 pages).
- Local demonstration: `scripts/serve_demo.py`; instructions in document 28.
- Source, data provenance and reproduction records: this repository; public URL pending authorization.
- Video: `output/video/zenithsync-review-video.mp4`, a local narrated review candidate under five minutes. Public accessibility remains pending authorization.
- Team attribution, category declaration, registration status and contributor roles: team-supplied facts still required.

Source datasets: [Farin v1](https://doi.org/10.17632/fypp6xhkjy.1) and [Kryeziu v3](https://doi.org/10.17632/hr94h42xdc.3). Full references and claim boundaries are in report references and document 29.
