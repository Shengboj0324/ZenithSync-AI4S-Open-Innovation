# Data strategy and prior-art analysis

This document records the original planning review. Subsequent actual-file admission findings and correction checks are in [Document 12](12-implementation-record.md).

## Evidence acquisition status

This round inspected resource pages and one small dataset README. It did not ingest full datasets, train models, inspect every supplemental spreadsheet, or verify raw-data reproduction. “Public candidate” therefore does not mean “admitted benchmark.” The following is a ranked acquisition and audit plan.

## Candidate resources

| Resource | Verified content / suitability | Proposed use | Admission problem |
|---|---|---|---|
| Ewart et al. Liver-Chip study [D1] | Real chip study: 870 chips, 27 drugs, three donors; public supporting data | Primary real-chip feasibility/reanalysis candidate | Few drug-level units; inspect dose data, donor availability, controls, and raw versus aggregate values |
| Sharf organoid recordings [D2] | HDF5/MAT/CSV electrophysiology; README specifies four organoids for diazepam series | Neural response demonstration, group leakage tests, robustness | One compound; organoids rather than validated perfused OoC; no broad drug inference |
| Nebuloni/Do microfluidic axotomy [D3] | Neural microfluidic source-data spreadsheets and linked analysis repository | Actual-chip mechanistic case study | Source tables may support figures, not a general ML benchmark; raw images not established |
| Yakavets et al. regimen optimization [D4] | Microfluidic spheroid/organoid experiments, Gryffin-related code and data | Closest application baseline and measured candidate-pool study | Adaptive sampling, aggregate outcomes, and limited unobserved-action support |
| BBBC021 [D5] | MCF7 fluorescence; 113 compounds overall, 38 in labeled MoA subset | Phenotyping fallback and pipeline sanity check | Not neural/chip data; only subset labeled; missing doses are selected rather than random |
| JUMP / Cell Painting [D6] | Multisite morphology profiles, images and metadata | Site-shift benchmark; optional matched-compound representation | U2OS context; matched chemistry is not matched biology; preprocessing leakage audit needed |
| RxRx1 [D7] | Public perturbation-imaging resource with NC-SA terms on page | Optional batch-robustness comparison | Genetic perturbation is not a drug dose-response label; license suitability unresolved |

Other organizer references include CellNet, IDR, and CytoData [K1]. These are not interchangeable datasets: CellNet concerns cell identity/transcriptomic networks; IDR is a study repository; CytoData is a community resource. Select a concrete accession, assay, and label before proposing any training task. Do not infer paired bright-field/fluorescence availability from a generic microscopy link.

### Critical discoveries

**Corrected liver data:** the author correction replaces an erroneously duplicated Table 3 [D1c]. Use the corrected table and archive the exact source version. Treat inequalities such as greater-than assay limits as censored measurements, not exact numerical values. The paper points to supplementary data for plots and statistics, and GEO GSE207339 for RNA sequencing; this does not establish that all chip-level imaging or longitudinal raw observations are public. [D1]

**Neural identities:** the inspected README maps array identifiers to organoids consistently across experiment groups, so developmental/drug recordings from the same array must stay together when testing new-organoid transfer. The public file list also repeats an identical checksum for one seven-month recording and its developmental counterpart. De-duplicate by content, not just filenames. Four drug-treated organoids cannot be multiplied into thousands of independent subjects by windowing. [D2]

**BBBC labels:** MoA labels cover 103 compound–concentration pairs from 38 compounds. The provider specifically recommends holding out all doses and replicates of a compound. Some absent doses were removed because of inactivity, toxicity, or QC. Training on the retained subset is not an unbiased toxicity-screening experiment. [D5]

**Active-learning precedent:** organoid-regimen optimization is already published with code [D4]. “We apply AI to choose experiments” is not an original contribution by itself.

**Concrete dose-response candidates:** the D4 provider README identifies individual-drug curves in Supporting Data Fig S5a (MCF-7: DOX, 5-FU, CPA) and Fig S13 (PDO: OLA, IBET-762). These offer a bounded feasibility study. The README excludes 10,000 µM 5-FU and 100/2,000 µM IBET-762 from fitting: each has only one experiment and no SD. Preserve those exclusions. Reported SD is not a standard error; “at least three experiments” does not establish exact sample counts. Individual-experiment viability can itself average up to 100 spheroids, which must not become 100 independent observations. These are provider-described fields, not verified archive contents. [D4]

## Data-admissibility gate

For each candidate, create a data card before any model selection:

1. Exact accession, version, retrieval date, source URL, hashes, and correction history.
2. Rights for download, training, derived features, redistribution, public demos, and weights; record each separately.
3. Biological system: cell line/donor/species, organoid versus chip, geometry and perfusion where measured.
4. Observation hierarchy: lab → batch → donor → chip/well → treatment → time → image/cell.
5. Intervention identity, concentration units, sequence, duration, controls, washout and carryover.
6. Endpoint definition, measurement units, instrument and assay range; raw, normalized, censored, or derived status.
7. Available independent groups per class/condition; replicate count and whether variation is biological or technical.
8. Missingness and exclusions, including failed chips and missing doses.
9. Identifiability: which planned parameter/claim can this dataset distinguish?
10. Public reproduction path and overlap with other sources/pretraining corpora.

Admit a dataset only for claims supported by its measurement process. A small source can be admitted for feasibility while rejected for confirmatory generalization.

## Minimum evidence portfolio for the flagship

| Layer | Required evidence | Permitted claim |
|---|---|---|
| Mechanistic/unit checks | Simulations with explicit assumptions | Equations and algorithms behave correctly in specified simulations |
| Public chip reanalysis | Corrected, traceable measured endpoints | Retrospective performance on the sampled chip setting |
| Independent biological validation | Unseen donors/batches/compounds with prespecified endpoints | Transfer along the dimension actually held out |
| Policy evaluation | Measured pool with independent audit outcomes or prospective experiment | Measurement efficiency on that pool / prospectively tested workflow |
| External lab | Independently collected supported assay | Broader laboratory generalization within measured conditions |

No layer substitutes for the next. Without paired source/target compound and assay metadata, do not train a cross-modal fusion model pretending separate datasets are synchronized.

## Proposed canonical records

Each observation needs `study_id`, `source_version`, `lab_id`, `batch_id`, `donor_id`, `chip_id`, `well_id` where applicable, `compound_id`, `structure_id`, `dose_value`, `dose_unit`, `exposure_time`, `endpoint_name`, `endpoint_value`, `endpoint_unit`, `censoring_type`, `assay_limit`, `replicate_type`, `control_group_id`, `quality_flags`, `raw_artifact_hash`, `license_id`, and `split_group_id`.

Null means unknown or inapplicable with a documented reason. It must not become a fictional identifier or zero-valued measurement. Repeated patient/donor aliases must map to one protected group identifier. Never put personal identifiers in public manifests.

Store three conceptually separate quantities: nominal administered concentration, measured exposure, and any model-estimated effective concentration. Relabeling nominal dose as measured tissue exposure would undermine the mechanism claim.

## License triage

- D1 article reuse terms and supplementary-file notices need artifact-level checking; article access alone does not settle all third-party rights.
- D2 is hosted by Dryad/Zenodo; verify the record's actual reuse license and any bundled software license before redistribution. A rendered blank License field is not a license grant.
- D3 source version advertises a newer record. Resolve and pin the correct version before ingestion; do not silently use an outdated source table.
- D5 identifies AstraZeneca copyright; inspect collection terms and file-specific notices rather than assuming public domain.
- D6 is an umbrella resource; each selected dataset, code module, and checkpoint needs a recorded license.
- D7 displays CC BY-NC-SA 4.0. Keep it out of the core submission until its compatibility with intended use and competition obligations is established.

These are specific unresolved rights questions, not a claim that any dataset is prohibited.

## Prior-art matrix and novelty boundary

| Precedent | Established idea | Proposed advance to test | Required comparison |
|---|---|---|---|
| Kennedy–O'Hagan [M1] | Discrepancy-aware multifidelity modeling | Assay-context transfer with empirical negative-transfer controls | Target-only and ordinary multifidelity GP |
| Kandasamy et al. [M2] | Cost-sensitive multifidelity Bayesian optimization | Decision-resolution acquisition under grouped/censored chip observations | Standard uncertainty/cost acquisition and compatible BO baseline |
| Angelopoulos–Bates [M3] | Conformal uncertainty under exchangeability | Correct experimental-unit calibration and explicit abstention protocol | Uncalibrated intervals and standard split conformal |
| Gibbs–Candès / feedback-shift work [M4, M5] | Calibration complications under shift and adaptive selection | Independent audit-stream evaluation of adaptive assay policies | Frozen-calibration policy and shift stress tests |
| Ewart et al. [D1] | Real-chip predictive-toxicology study | Sample-efficient response estimation, not rebranding their assay result | Published assay rule plus held-out learned baselines |
| Yakavets et al. [D4] | Automated ML-guided regimen exploration | Controlled decision reliability and transfer under specified assay budgets | Original feasible optimization policy and random/space-filling policies |
| Christiansen et al. [M6] | In-silico fluorescent labeling | Only if pursuing C: biological-task-preserving uncertainty, not prettier synthesis | Matched U-Net/regression and downstream biological error |

The integration may be useful without being algorithmically novel. Before claiming novelty, inspect the closest complete papers and implementations, perform citation-forward searches, and formulate a precise difference that survives ablation. This round is a targeted prior-art study, not an exhaustive systematic review or proof of priority.

## Dataset choice decision record

**Proposed:** D1 first for real-chip suitability; D4 for optimization precedent and a second biological setting; D2 only for a bounded neural case; D5/D6 for the fallback and representation testing. No dataset has yet passed the full admission gate. The outcome of this audit, not a preferred architecture, determines the final experimental claim.
