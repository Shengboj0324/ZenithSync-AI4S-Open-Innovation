# Second-half implementation: correlated design and additional development data

Status: implementation in progress. M6–M10 remain unaccepted. This record supersedes the earlier planning-only status for the specific components and source listed here. It does not declare the entire solution complete, scientifically superior or submission-ready.

## Implemented and exercised

`src/zenithsync/joint_design.py` provides a joint Gaussian law with separate latent targets and noisy observation coordinates. It validates covariance at its numerical scale, conditions all coordinates together, and handles shared-control observation covariance without assuming independent future noise. It computes batch variance reduction and enumerates feasible small subsets with positive measurement costs and optional batch setup charges. Large enumerations and singular observation blocks are rejected explicitly.

These are standard Gaussian identities implemented as a reliable foundation. The exact optimization statement concerns the finite supplied set, cost model and fixed Gaussian variance objective, subject to floating-point arithmetic. It is not a universal acquisition guarantee or a novelty claim. Source metadata must justify any proposed shared-control relationship.

`scripts/joint_design_audit.py` exercises design and estimator ablations over four shared-control variance settings and six budgets. The 72-row output separates choosing measurements with the wrong covariance from estimating responses with the wrong covariance. These are analytical synthetic calculations with zero biological campaigns.

For the declared synthetic case with control variance 1 and budget 3, expected target MSE is 0.544159 for joint design/estimation, 0.641629 for diagonal design with joint estimation, and 0.697564 for diagonal design/estimation. This illustrates the mechanism under a known Gaussian law; it is not an estimated biological effect, measured assay saving, or proof that the proposed model will work on real data.

## New public source acquired and audited

The [Farin organoid-stroma dataset](https://data.mendeley.com/datasets/fypp6xhkjy/1) file `Drug_sensitivity_all_lines.txt` was downloaded and verified against the SHA-256 displayed by the provider. Its file panel explicitly labels it CC BY 4.0. Attribution and source metadata are preserved in `data/farin_manifest.json`.

The raw file contains 6,729 measurement records plus three blank trailing lines. There are 280 distinct organoid/culture/fibroblast/drug curve contexts and 29 organoid identifiers. These are not 280 independent patients or confirmed chip campaigns. The file supplies no explicit plate/run identifier; patient independence remains unverified.

The adapter preserves every measurement, original row number, dose label, raw signal and author exclusion. It does not replace excluded observations with zero or invent corrected doses. Admission findings:

| Finding | Evidence | Consequence |
|---|---|---|
| Author exclusions | 235 rows marked cells lost or nonuniform seeding | Preserve raw values and annotations; exclude from eligible observations |
| Ambiguous dose labels | Eight non-DMSO rows have numeric dose zero | Quarantine affected curves; do not infer intended low dose from row order |
| Repeated replicate labels | O25 monoculture 5-FU controls repeat label 4; O28 co-culture Gef repeats zero-dose labels | Preserve unique source row IDs and quarantine the affected curves |
| Combined ambiguity quarantine | Four curves, 99 rows; overlaps author exclusions | 6,398 rows remain structurally eligible, not automatically scientifically admitted |
| Sparse/incomplete surviving curves | 272 contexts have at least two eligible controls and four nonzero doses; 136 contexts have exactly 24 rows, all eligible | Explicit population selection required for each benchmark |
| Experimental hierarchy incomplete | No plate/run fields or independently verified patient mapping | No plate transfer or independent-patient guarantee |

The four quarantined contexts are O06 monoculture/Gef, O19 co-culture F19/Gef, O25 monoculture/5-FU and O28 co-culture F28/Gef. All exclusions are reproducible in `artifacts/farin_v1/source_rows.csv`; `quality.json` records every curve's remaining controls and dose support.

This source is **development data** because its outcomes have been inspected. The separate candidate confirmation cohort in Document 23 has not been downloaded or evaluated in this implementation step. A frozen scientific claim and suitable independent data are still required for M7.

## Reproduce this step

From the repository root, after the existing environment setup:

```sh
.venv/bin/python scripts/fetch_farin.py
.venv/bin/python -W error scripts/audit_farin.py
.venv/bin/python -W error scripts/joint_design_audit.py
.venv/bin/python -m pytest -q -W error
```

The downloader refuses unexpected bytes or hashes. Python's default user agent received HTTP 403; the ordinary public download succeeded with a standard user-agent header, which the script now uses. No authentication or user intervention was needed. Browser downloads timed out, but its file preview exposed the source hash and file license. The alternate deepOrganoid source points to Google Drive; that route was not accessed.

## Verification and logs

**75 tests passed with warnings treated as errors**, including ten joint-design tests and four adapter tests. They verify the conditional-suppressor counterexample, correlated batch/sequential equivalence, shared-control variance floor, setup-cost selection, invalid covariance at small scales, duplicate/invalid actions, source hashes, preserved exclusions and ambiguous-curve quarantine.

The immutable run directory is [20261007T031147054590Z](../artifacts/logs/second-half/20261007T031147054590Z/record.json). It records commands, exit statuses and hashes of the new source, tests and result artifacts. Numbered text logs preserve stdout/stderr. The existing first-half checkpoint archive is unchanged and does not contain this subsequent work.

## Remaining work against the full goal

- M6: complete real-data comparisons with strong tuned baselines and ablations; establish a precise improvement and nearest-prior-art difference. Correct primitives and synthetic examples do not satisfy this stage.
- M7: freeze the model, claim and analysis before evaluating an admitted independent public cohort.
- M8: integrate justified costs, endpoints and feasible actions; validate uncertainty and measurement efficiency on actual assay evidence.
- M9: finish the actual runnable presentation, technical report, video and Writeup from the final evidence.
- M10: resolve controlling-rule, eligibility and release-rights questions; perform independent review and public-access checks before authorized submission.

No new manual action is needed to rerun this step. Eventual user actions include confirming team eligibility/registration and authorizing external publication/submission. Organizer clarification and independent scientific/reproduction review remain external dependencies. Work that can be completed locally continues; these dependencies are not grounds to stop implementation now.

## Counted-well development replay

The subsequent implementation adds `farin_replay.py`, an explicit well oracle, a complete-case admission ledger, and `configs/farin-replay-protocol.json`. Admission requires the complete eight-dose by three-replicate rectangle with no excluded measurements. There are **136 admitted curves across 28 organoid IDs**. This retrospective completeness/QC selection limits the target population; it is not a prospective missing-data solution.

Replicate labels 1 and 2 supply sixteen selectable wells; label 3 supplies eight separate audit wells. Labels do not establish separate plates, runs or patients. The endpoint is the seven natural-log treatment signals minus the held-out natural-log control signal. It is a noisy technical-replicate endpoint, not latent viability or clinical efficacy. All policies begin with the same three charged wells: a control and the lowest/highest nonzero dose. Every subsequent well, including the second control, costs one assay unit. Audit wells are evaluation overhead, not an asserted assay saving.

The oracle exposes only design metadata and purchased observations. Tests poison hidden pool and audit outcomes and verify that observed predictions remain unchanged. Baselines average observed log signals at repeated doses, normalize using only measured controls, and interpolate in `log1p(dose/minimum_positive_dose)` coordinates. Linear and PCHIP use constant extrapolation; a constant-response baseline is retained. Random selection uses twenty computational seeds, averaged before biological-ID aggregation.

The initial baseline run showed that random selection beat dose spacing at budget eight. A control-first spacing baseline was added **after inspecting that development result**. It is a diagnostic comparison, not a preregistered confirmation. All fourteen budgets from three through sixteen are reported. There are 125,664 result rows; algorithmic seeds and curve contexts are not counted as independent patients.

| Linear interpolation policy | RMSE at 3 wells | RMSE at 8 wells | RMSE at 16 wells | Mean MSE across all 14 budgets |
|---|---:|---:|---:|---:|
| Random, twenty-seed mean | 0.744623 | 0.594601 | 0.538101 | 0.362401 |
| Dose spacing | 0.744623 | 0.626223 | 0.538101 | 0.375085 |
| Control-first spacing | 0.744623 | 0.595020 | 0.538101 | 0.380041 |

Each squared error is first averaged over the seven audit doses, then over seeds, then over curves within an organoid ID, and finally over IDs equally. Table RMSE is the square root of that aggregated MSE. The full-information error measures remaining held-out disagreement; it is **not an estimated irreducible noise floor**.

Control-first spacing minus random linear interpolation has a paired mean-budget MSE difference of +0.017640. The exploratory paired-ID bootstrap interval is [-0.008409, +0.046754]. This supports no superiority claim. These resampling limits assume exchangeability of the available IDs, whose patient independence is unverified; six diagnostic contrasts receive no familywise significance claim. The synthetic known-covariance benefit above has therefore **not** been established on this real-data replay.

Outputs are in `artifacts/farin_replay_v1/`: admission decisions, complete measurement orders using original source rows, all result rows, ID-level results, full budget summaries and exploratory paired contrasts. Reproduce with:

```sh
.venv/bin/python -W error scripts/farin_replay_benchmark.py
.venv/bin/python -W error scripts/summarize_farin_replay.py
.venv/bin/python -m pytest -q -W error
```

**84 tests pass with warnings treated as errors.** The replay also checks finite losses and agreement across policies at the identical initial and complete-information endpoints. M6–M10 remain unaccepted. Joint Gaussian acquisition, tuned probabilistic comparisons and suitable uncertainty validation still need integration into this measured-well benchmark; the untouched confirmation cohort remains reserved.
