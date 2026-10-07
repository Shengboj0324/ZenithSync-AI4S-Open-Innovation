# Reviewable implementation checkpoint

Updated October 6, 2026. This handoff consolidates the implemented research core and its limits. It is not a claim that the requested guaranteed-success or validated halfway milestone has been achieved.

## What works now

- Public-source acquisition with pinned hashes and original row provenance.
- Hill, interpolation, exact GP, finite GP-mixture and ridge baselines.
- Training-only nested selection and chronological generation evaluation.
- Gaussian decision-value and variance-based acquisition, including numerical stress tests and repaired failure cases.
- Retrospective measured-pool comparisons with hidden audit outcomes.
- Conditional uncertainty, coverage and abstention diagnostics, with explicit independence limits.
- A strict JSON research workflow that rejects unsupported requests, abstains where required and ranks candidate measurements.
- Recorded predictions, split identities, acquisition traces, source checkpoints and reproduction evidence.

The authoritative scientific findings are in Documents 14–18. Simple models often outperform more complex alternatives. Acquisition advantages vary by budget and assay. Current data does not establish prospective assay savings or independent biological calibration.

## Shortest inspection path

1. Read `README.md` and `docs/18-uncertainty-and-completion-audit.md`.
2. Inspect `examples/ola_ibet_request.json` and `artifacts/workflow_v1/response.json`.
3. Run the README environment/data setup, then:

```sh
.venv/bin/python -m pytest -q -W error
.venv/bin/python scripts/research_workflow.py examples/ola_ibet_request.json --output artifacts/workflow_v1/response.json
.venv/bin/python scripts/verify_reproduction.py
```

The full verifier reinstalls dependencies in a temporary environment and recreates the recorded benchmark/workflow artifacts. It compares 25 deterministic files byte for byte. The separate uncertainty audit has five files checked on a same-environment rerun; it is not represented as part of that 25-file comparison.

## Sequential-source admission result

`scripts/audit_sequential_semantics.py` checks the remaining 59 sequential records against their pinned hashes and records source-code evidence from the same immutable author revision. It does not execute author code.

- OLA–IBET's 27 records have t0+t1=48 in every generation.
- The author's initial GS0 script uses a 1–11 t0 range and t1=12−t0; later GS1–GS2 code uses a 1–47 range and t1=48−t0.
- FAC contains three-drug sequences but only two supplied timing columns; sequence mapping, residual timing and physical time units must be established before physical interpretation.

The code/table difference may reflect a conversion or a later workflow change. This audit does not establish an error in the experiment. It does establish that a universal physical-time conversion cannot be inferred safely from the files inspected so far. Those records remain preserved for source inspection, rather than being silently pooled with concurrent experiments.

Evidence: `artifacts/yakavets_admission/sequential_semantics.json` includes immutable URLs, source hashes, line-numbered excerpts and table statistics. `artifacts/logs/sequential-semantics.txt` records execution. Downloaded author code was not installed or run.

## Checkpoint archive

`scripts/package_checkpoint.py` creates a local ZIP under `artifacts/checkpoints/`. It includes code, configurations, tests, documentation, example requests, source manifests, result tables and available logs. `CHECKPOINT-MANIFEST.json` inside the archive lists each file's size and SHA256 hash. The packager verifies archive CRCs and every recorded content hash, checks for source-file or Git-HEAD changes during packaging, and writes an archive checksum alongside the ZIP.

Raw third-party downloads, virtual environments, IDE state, Git internals and previous archives are excluded. Fetch scripts and pinned manifests preserve the data-acquisition route. This local review package is not a public release; redistribution rights remain to be reviewed before publishing it. No user work or Git history is reset or rewritten.

The package captures current uncommitted work as well as the existing checkout baseline. Its manifest records the actual current Git commit rather than assuming the older planning-only state. Reproduction archives preserve retained transcripts. Historical logging gaps disclosed in Document 17 remain gaps; the package does not fabricate missing transcripts.

## Manual interventions and decisions

No manual intervention is needed to inspect or run the current local workflow. The pending question about a biological collaborator or independent data remains unanswered. The next scientific validation stage needs:

1. A qualified choice of assay decision, endpoint threshold, feasible actions and measurement costs.
2. Authorized donor/chip/batch/control metadata and independent validation observations sufficient for the intended claim.
3. Resolution of sequential timing semantics if those records are used for physical recommendations.
4. Eligibility, registration, controlling rubric and rights checks before submission or public release.

These are concrete dependencies for stronger claims, not additional permission requests for local development. No external messages, registration, publication, paid compute or physical experiments have been initiated.

## Confirmation that can be given

The research software runs, tested mathematical contracts hold, source-specific exploratory results are recorded, and the documented reproduction checks pass. Confirmation of a competition ranking, a numerical completion fraction, robust real assay savings or independent biological validity cannot yet be given honestly. The original objective remains intact and active.
