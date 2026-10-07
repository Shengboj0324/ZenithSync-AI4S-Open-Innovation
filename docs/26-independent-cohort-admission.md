# Independent cohort: blinded admission and frozen confirmation protocol

Status: public source acquired, design and identifier admission completed, and the confirmation protocol frozen. **No response evaluation has occurred. M7 is not accepted.**

## Source and scientific alignment

The [Kryeziu/Sveen/Lothe dataset, version 3](https://data.mendeley.com/datasets/hr94h42xdc/3), DOI 10.17632/hr94h42xdc.3, provides raw drug-screening well measurements and is labeled CC BY 4.0. The provider's file hashes and byte counts are preserved in `data/kryeziu_candidate_metadata.json`. The original Data S4 and Data S1 workbooks are downloaded locally and verified against those pinned hashes. Their acquisition does not imply that all their contents were analyzed.

The [source paper's drug-screening methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC13293968/) describe two parallel technical replicates, plate-level DMSO/benzethonium controls and luminescence measurement after 96 hours. The authors calculate normalized viability using negative and positive control medians. Our registered endpoint instead uses raw log-signal contrasts, matching the development estimand; it must not be called the authors' normalized viability or DSS. These are organoid assays, not perfused chips or clinical validation. The article has a separate CC BY-NC license; no article figures are copied into the project.

## What was exposed

The Data S4 extractor emits fourteen allowlisted design fields plus worksheet/original-row references. Signal and viability are never emitted or summarized. The Data S1 extractor emits only sample_id, patient and sample_type, with no mutation fields. Original workbooks remain unchanged.

This is procedural outcome blinding. The local XLSX reader decodes source rows while projecting selected columns; raw files remain available locally. It is not a third-party sealed holdout or an access-control guarantee. Neither response values nor mutation values were exposed to the analysis or used to choose this protocol.

## Admission results

The raw design projection contains 191,030 records: 157,810 single-agent rows, 24,414 combination rows, 5,474 negative controls and 3,332 positive controls. It includes 211 sample IDs and 239 run IDs. Combination-component records can share a physical well, so row count must not be equated with independent assays. Combination rows are excluded from this single-agent experiment.

Pairing uses sample, run, library, drug and exact numeric dose support. It preserves p1/p2 plate identities, requires at least four matched doses, and requires at least two separately labeled DMSO controls on each plate. Single-agent/control physical well collisions cause an error.

| Gate | Result |
|---|---:|
| Single-agent sample/run/library/drug contexts | 9,720 |
| Structurally admitted paired contexts | 9,231 |
| Structurally admitted samples / runs / drugs | 209 / 237 / 56 |
| Different dose support across plates | 246 excluded contexts |
| Fewer than four paired doses | 119 excluded contexts |
| Missing paired plate | 84 excluded contexts |
| Unknown or non-nM concentration units | 40 excluded contexts |
| Admitted contexts with explicit PDO patient mapping | 6,524 |
| Mapped samples / source patient IDs | 148 / 100 |
| Structurally admitted samples lacking this mapping | 61 |

Data S1 contains both tumor and PDO identifiers. A many-to-one mapping check correctly failed before filtering by sample_type. Restricting to PDO records produces the unique source-supported mapping used for confirmation. Patient identities are not guessed from sample-name prefixes.

Negative controls consistently carry the source type control_negative and name DMSO, but their concentration annotations include 0.1 percent, zero and missing/NA values. These annotations are preserved rather than replaced. Control identity comes from the source type/name and plate association. Unknown drug-dose units are excluded independently of response values.

## Frozen experiment

`configs/kryeziu-confirmation-protocol.json` is the authoritative analysis specification. `artifacts/kryeziu_design_v1/protocol-freeze.json` records its pre-outcome timestamp and hashes of the model, admission code and cohort identities. Key commitments:

- Use p1 as the selectable pool and p2 as the separate technical-plate audit; reverse orientation is a sensitivity analysis.
- Keep the development GP fixed at amplitude 1, length 0.5, noise SD 0.3 and mean slope 2. No cohort-specific tuning.
- Compare exact fixed-budget selection with twenty random-selection seeds under the same joint estimator. Include greedy, diagonal-noise and interpolation comparisons.
- Charge every purchased treatment/control well. Use all available pool controls, with symmetry reduction permitted only after its mathematical equivalence is tested.
- Average errors over budgets and contexts, then samples within patients, then patients equally. Resample whole patients for paired uncertainty intervals.
- Require at least 5% mean-MSE reduction and an entirely favorable paired 95% interval for the primary improvement claim.
- Test 20% fewer purchased wells separately against a frozen random-reference budget, with a 5% MSE noninferiority margin. Passing the primary test alone does not establish assay savings.
- Record every post-unblinding invalid/nonpositive-signal exclusion. No filtering by activity, residual, DSS or favorable result.
- Preserve the first outcome evaluation. A subsequent revised model makes this cohort development data and requires another untouched confirmation cohort.

These are registered hypotheses and acceptance rules, not achieved results. Shared-control costs are charged separately for each isolated drug context; no plate-wide amortization, financial saving or sequential stopping guarantee is asserted.

## Reproduction and next gate

Use the bundled spreadsheet Python runtime for the read-only workbook projections:

```sh
python scripts/inspect_kryeziu_design.py
python scripts/inspect_kryeziu_patient_map.py
python scripts/audit_kryeziu_design.py
```

The exact runtime path and outputs are recorded in this step's execution logs. The existing repository environment runs the scientific tests:

```sh
.venv/bin/python -m pytest -q -W error
```

**99 tests pass.** New tests check disjoint plate partitions, exact numeric dose matching, missing/control/unit rejection and physical-well collisions. The scientific confirmation runner and symmetry-reduced optimizer still need implementation and blinded testing before opening response outcomes. No user intervention was needed for acquisition or admission, and no external publication or submission occurred.
