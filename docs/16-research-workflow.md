# End-to-end research workflow

Updated October 6, 2026. This iteration connects admitted input semantics, a fitted model, uncertainty, decision abstention, candidate acquisition and output provenance. It follows the earlier generation-aware evaluation, which was substantive progress. The active goal remains open; this is not a claim of a guaranteed competition result or verified 50% scientific completion.

## Running the actual-data example

From the repository root, after the README setup and downloads:

```sh
.venv/bin/python scripts/build_workflow_example.py
.venv/bin/python scripts/research_workflow.py examples/ola_ibet_request.json --output artifacts/workflow_v1/response.json
```

The example uses ten OLA–IBET generation-zero measured responses and ten generation-one candidate input coordinates. Candidate responses are deliberately absent. The threshold 0.5, unit measurement costs, equal error costs and abstention cost 0.1 are illustrative research assumptions, not expert-approved operational or biological values.

The output currently selects `source-row-15` among supported candidates for further measurement. Six candidates lie outside the observed input convex hull; they receive no prediction or acquisition ranking. One additional candidate receives a prediction but the decision rule abstains. These outcomes remain visible rather than being replaced with a success-like answer.

The JSON output is a computed research result, not a physical experiment instruction. Its request hash, implementation hashes, observation identities and assumptions allow inspection of the exact calculation.

## Request contract

Supported contexts are `yakavets_fac_concurrent` and `yakavets_ola_ibet_concurrent`. Feature order must match the context (`conc0`, `conc1`, and FAC's `conc2`), the unit must be `author_normalized_concentration`, and the endpoint must be `cv_exp`. These coordinates are not silently interpreted as micromolar values.

Every observation requires a unique ID, numeric feature vector and observed response. Every candidate requires a unique ID, feature vector and positive measurement cost. Candidate outcome fields are rejected. Unknown fields, unsupported endpoints, invalid units, nonfinite inputs, duplicate IDs and negative observations are rejected rather than repaired implicitly.

The request explicitly supplies the threshold, false-positive cost, false-negative cost, abstention cost, model noise SD and ridge penalty. A strict schema prevents unrelated assays or hidden response-derived predictors from entering this workflow. It does not establish biological validity of user-supplied records.

## Model and mathematical interpretation

The ridge model was retained because it outperformed the tested GP variants in both concurrent-assay contexts. For augmented design matrix A with an intercept, diagonal slope penalty Lambda and fixed observation variance sigma²,

\[
\hat\beta=(A^\top A+\Lambda)^{-1}A^\top y,\qquad
\operatorname{Cov}(\beta\mid D)=\sigma^2(A^\top A+\Lambda)^{-1}.
\]

The intercept has zero penalty (flat prior); slopes have positive penalty. At least one observation and positive slope penalties make this posterior proper. Prediction uses Cholesky solves, not an explicit numerical matrix inverse. This conditional uncertainty assumes linear response and the supplied noise model; it does not propagate unknown control covariance or prove empirical coverage.

For posterior probability p that the latent response is below the supplied threshold, the two classification risks are C_FP(1-p) and C_FN p. Abstention is chosen when its supplied cost is no greater than either classification risk. Returned classifications are explicitly provisional. The displayed 90% interval concerns a new noisy observation; the threshold probability concerns the latent conditional mean. These are deliberately labeled as different uncertainty targets.

Candidate acquisition computes expected reduction in integrated latent variance per supplied cost. The target grid comprises supported request candidates with equal target weights. Costs are relative caller inputs; no laboratory savings are inferred. The output does not pretend that a measurement-value objective and a classification-loss objective are identical.

## Support and failure behavior

Support is checked by a convex-combination feasibility problem using observed input coordinates. Membership is a geometric restriction, not proof of biological support or exchangeability. Points outside that region receive explicit abstention and null predictions/scores. Failed support optimization raises a computational error instead of returning false confidence.

All outputs identify themselves as research-only and requiring human review. Uncertainty is explicitly uncalibrated. The workflow does not issue clinical treatment advice, claim independent donor validation or invent experimental units.

Rejected requests exit with code 2 and write a rejection record to the requested output path. This replaces a stale earlier success file, so a caller cannot accidentally interpret it as the result of the failed request. No remote application or experiment is controlled by this CLI.

## Verification and artifacts

The suite has 57 tests, including new checks for ridge equivalence to regularized least squares, variance reduction with repeated observations, geometric support, hidden candidate-outcome rejection, unit/schema rejection, cost-dependent ranking, abstention behavior, request immutability and stale-output rejection. Warnings are treated as errors.

- `examples/ola_ibet_request.json`: complete inspectable real-data request.
- `artifacts/workflow_v1/response.json`: computed candidate outputs, ranking, assumptions and provenance.
- `artifacts/logs/tests-workflow-current.txt`: current test evidence.
- `artifacts/logs/workflow-current.txt`: CLI execution output.
- `artifacts/logs/reproduction.json` and `fresh-environment.txt`: authoritative fresh-environment verification, now including this workflow and comparing 21 deterministic artifacts.

## Remaining requirements and manual interventions

The implemented computational chain now runs end to end, but the broader goal still requires stronger policy evaluation, independently supported biological uncertainty, appropriate costs/thresholds, source-semantic completion and submission evidence. Neither a working interface nor passing tests demonstrates assay savings or secures a top rank.

A question about access to independent data or a biology collaborator is pending. Until such resources are established, development proceeds on public-data evidence. No manual action is required to execute the current example. Qualified threshold/cost review and independent biological evidence are needed before stronger deployment claims; those needs have not been silently removed from scope.
