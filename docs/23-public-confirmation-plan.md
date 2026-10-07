# Public-data expansion and independent confirmation plan

Planning status, October 6, 2026. The two provider records below were read; their raw data were not downloaded or analyzed in this documentation update. Neither is currently an admitted benchmark or a verified independent confirmation cohort.

Subsequent implementation update: the Farin dose-series file has now been downloaded, hash-verified and audited as development data. See [Document 24](24-second-half-development.md) for counts, exclusions and limitations. The second candidate remains uninspected at the outcome level. The original planning statement above describes the earlier documentation update.

## Candidate evidence

| Candidate | Provider evidence | Proposed role and boundary |
|---|---|---|
| [Farin organoid-stroma biobank, v1](https://data.mendeley.com/datasets/fypp6xhkjy/1), DOI 10.17632/fypp6xhkjy.1 | Published August 24, 2023; CC BY 4.0. Provider describes raw luminescence, seven-point dose series, technical triplicates, and mono-/co-culture conditions. | Candidate development source for dose-response and context effects. These are organoids, not established perfused-chip measurements. |
| [Kryeziu, Sveen and Lothe metastatic colorectal cancer PDO data, v3](https://data.mendeley.com/datasets/hr94h42xdc/3), DOI 10.17632/hr94h42xdc.3 | Published April 20, 2026; CC BY 4.0. Data S4 is described as well-level screening with sample, run, assay, library, plate, concentration/unit, raw signal and normalized viability fields. | Candidate reserved confirmation source. Actual patient independence, control mapping, dose support and normalization must be audited before admission. |

The first record describes four drugs in the dose-series file and a separate chemogenomic screen. Treat those as different experimental designs. The second record includes derived drug-sensitivity scores; those must not become predictors for a model claiming to infer sensitivity from fewer raw measurements. Provider field descriptions alone do not verify that every row has usable metadata.

## Admission workflow

1. Retrieve and archive dataset metadata, version, license and exact file URLs. Record byte hashes after download. Keep third-party notices and required attribution.
2. Inventory schema, units, identity fields and documented exclusions before inspecting outcome patterns. Resolve patient/sample aliases using author metadata, not name guesses.
3. Count independent patients, organoid lines, experiments, plates, dose conditions and technical replicates separately. Define the analysis unit from the scientific claim.
4. Reconstruct normalization from raw controls where possible. Determine whether viability uses controls shared across candidate and audit rows. Count controls as available observations and costs according to the proposed workflow.
5. Check missingness, saturation, negative or zero signals, plate-edge effects, duplicated measurements and author exclusions. Preserve reasons for exclusions; do not remove inconvenient responses.
6. Verify public download accessibility and file-level rights. A provider-level CC BY label is useful evidence, but preserve any file-specific exception and attribution requirement. Do not bundle unrelated molecular or clinical data merely because it is co-hosted.
7. Establish whether any patients or samples overlap between sources. Distinct repository identifiers do not alone prove independent biological provenance.

If metadata cannot support a claimed task, reject that task/source pairing. A larger number of rows cannot repair missing donor identities or unsupported physical actions.

## Freeze before confirmation outcomes

Assign the first suitable source to development and reserve a separate suitable cohort for confirmation. This is a proposed allocation, conditional on admission; it is not a preregistration already executed.

Before revealing confirmation outcomes, save an immutable protocol with hashes for the source/version, admitted population, primary endpoint, comparison, practical-effect target, split, candidate pool, audit set, preprocessing rules, missingness handling, model configurations, stopping rule and statistics. Record who has already inspected which data. Blinding means hiding labels from both method selection and claim selection, not merely from a prediction function.

Schema-only inspection is permissible if it does not use outcome values to choose favorable groups. Any outcome-based eligibility rule must be fixed from development or scientific requirements and applied mechanically. If confirmation data have already informed model decisions, relabel them development and reserve another cohort; do not retroactively call them unseen.

Use the actual endpoint units within each assay. Do not directly pool albumin readouts, luminescence and normalized viability as interchangeable toxicity labels. Across sources, compare the prespecified procedure using compatible task definitions and explicitly justified normalized metrics. Report each source separately before any aggregate.

## What successful confirmation would establish

An independent organoid study can corroborate a narrow statistical measurement-planning result across the tested study settings. It does not validate neural physiology, arbitrary novel drugs, patient treatment, or a general digital twin. Real-chip results remain their own evidence layer.

Retrospective measured-pool replay evaluates selection among recorded conditions. It cannot establish performance on unmeasured concentrations or prospective operational savings. To claim actual saved experiments, obtain prospective experimental evidence or use wording explicitly limited to the replay setting.

The report must include an unsuccessful confirmation, if observed. Tuning after the failure converts that cohort into development evidence and creates a new confirmation requirement.
