# Submission package and defense plan

These are proposed structures. The competition requirements are recorded in [Document 01](01-competition-intelligence.md). Existing exploratory results are recorded in Documents 12–20; the full proposed confirmatory experiments remain **not run**.

## One central statement

The eventual submission should state a result in this form:

“For [defined assay and population], our method achieved [measured change with uncertainty] relative to [strong baseline] under [held-out protocol], using [measurement cost], with [coverage/failure boundary].”

Until those fields have evidence, use a research hypothesis instead. Do not write an accomplished-result abstract from the planning target.

## Writeup layout

1. Category declaration and descriptive project title.
2. Public demonstration video.
3. Public source repository and immutable submission release/commit.
4. A 200–300-word project summary answering problem, contribution, result, value, and boundary.
5. Self-contained technical report or public PDF link.
6. Optional interactive demo with access requirements and backup.
7. Short contribution, data/license, prior-work, and AI-tool disclosure.

The report and repository must agree on dataset version, split, metric definitions, denominators, units, and results. Freeze an archival submission version; do not silently replace its results during review. Confirm the permitted update policy with the organizer.

## Proposed report structure

Aim for an approximately 18-page main report, within the organizer's recommended range. This is document design, not a work-time constraint.

| Section | Approximate pages | Required content |
|---|---:|---|
| Summary and context of use | 1 | User, decision, primary result and limits |
| Problem and scientific relevance | 1.5 | Assay bottleneck; why this endpoint matters |
| Prior art and contribution | 1.5 | Closest methods, exact difference, no priority inflation |
| Data and governance | 2 | Data cards, independent counts, licenses, corrections, exclusions |
| Method and mathematical assumptions | 3 | Model, uncertainty, decision objective, identifiability |
| Experimental design | 2 | Splits, baselines, cost accounting, hypotheses |
| Results | 3 | Primary comparison, interval, cost/error curve, ablations |
| Reliability and limitations | 1.5 | Shift, subgroup errors, abstention, unsupported cases |
| Reproduction and practical value | 1.5 | Rerun path, measured resources, operational impact |
| Conclusion and contributions | 1 | Supported conclusion and concrete remaining evidence |

Put full hyperparameter searches, split manifests, supplementary plots, mathematical derivations, and extra failure cases in appendices. Do not hide unfavorable primary results there.

## Essential figures

1. One assay workflow linking the actual user decision to observed data and model output.
2. Group-level data/split diagram showing what “unseen” means.
3. Main effect with group-aware uncertainty, including all comparison methods.
4. Cost-versus-error frontier with equal reliability/coverage constraints.
5. Calibration and width, including a shift failure or abstention case.
6. Component ablation and negative-transfer test.

Use real scientific plots generated from run artifacts in the implementation round. Screenshots of attractive synthetic curves are not experiment evidence.

## Five-minute demonstration storyboard

| Video segment | Show | Evidence discipline |
|---|---|---|
| 0:00–0:30 | Researcher's assay decision and a concrete bottleneck | State population and endpoint |
| 0:30–1:10 | Load a public, versioned real input and inspect QC | Display provenance and units |
| 1:10–2:10 | Run model; show response estimate, uncertainty and supported domain | Distinguish measured points from predictions |
| 2:10–3:00 | Rank feasible next measurements and reveal a genuinely measured held-out outcome | Label recorded replay versus live execution |
| 3:00–4:05 | Compare with strongest baseline at matched assay cost | Same split, metric and denominator |
| 4:05–4:35 | Failure/shift case with abstention | No cherry-picked success-only story |
| 4:35–4:55 | Reproduction entry point, measured contribution, limitation | End before five minutes |

This duration is a submission-format requirement, not a development time constraint. Use readable labels, captions, clear narration, and restrained transitions. Essential scientific claims should remain understandable without audio. If the final audience's language needs are unclear, confirm them; English report plus bilingual key labels is a proposal, not an official mandate.

## Claim ledger template

| Field | Required entry |
|---|---|
| Claim ID and exact sentence | The claim as it appears in report/video |
| Status | Hypothesis / observed / inferred / simulated / unsupported |
| Population and estimand | Assay, group, intervention, outcome, decision |
| Evidence | Run ID, source version, split hash, table/figure |
| Comparison | Baseline and fairness conditions |
| Uncertainty | Interval and resampling/analysis unit |
| Boundary | What the experiment does not establish |
| Reviewer | Person who verified the statement against artifacts |

No sentence containing a numerical gain should exist without this record. Literature results belong to their authors and must never be presented as ours.

## Judge questions and answer requirements

| Likely question | What the answer must show |
|---|---|
| What is new beyond a GP and active learning? | Closest prior algorithm, exact change, ablation and improvement |
| Why should this work on a chip? | Actual target-chip observations and documented exposure/assay context |
| Why this organ rather than the sponsor's neural focus? | Stronger available validation and decision importance; no unsupported organ transfer |
| How many independent samples are there? | Compounds/donors/chips, not image or window count alone |
| Did the same compound appear in training? | Split manifest including all doses, aliases and pretraining overlap |
| Are your intervals valid on a new lab? | Actual external audit; no unconditional guarantee under arbitrary shift |
| Did you really save experiments? | Prospective evidence or clearly bounded measured-pool replay; full cost accounting |
| What if the source assay is misleading? | Negative-transfer test and target-only fallback |
| Why not just fit a Hill curve? | Direct same-split comparison and failure regime that motivates advancement |
| Can a reviewer reproduce without your infrastructure? | Public inputs, weights/fitting path, clean environment and reference outputs |
| Is this clinically validated? | Precise research-only context and the missing clinical evidence |
| What was completed before the competition? | Prior-work inventory and exact new contributions |
| What are the weakest results? | Representative failures and resulting scope restrictions |

## Final inspection checklist

- Category and team information are consistent across required registration surfaces.
- Writeup is actually submitted, and all required links open without private access.
- Demo, report, repository and models resolve to the intended release.
- Report figures can be regenerated; every numerical claim has a ledger record.
- Full-data versus small-demo differences are explicit.
- License and AI-tool disclosures match actual use.
- No private data, secrets, or third-party assets lacking redistribution rights are embedded.
- A backup recorded demonstration and local execution path exist.
- Final-defense format and permitted submission updates have been clarified.

Nothing in this planning round has been registered, published, sent, or submitted.
