# Project selection and competitive positioning

## Selection principle

Choose the project with the strongest achievable scientific claim under both rubrics, conditional on admissible evidence. Unlimited planning time does not imply unlimited biological data, identifiable parameters, or permission to use restricted resources.

The repository contained only a title README at inspection. No existing implementation, dataset, or validated result was available to extend. No wet-lab access has been established in this round. The recommendation therefore starts from public resources and makes additional evidence acquisition an explicit work package.

## Alternatives

| Option | Scientific question | Strength | Main failure mode | Decision |
|---|---|---|---|---|
| A. Assay Planner | Can adaptive measurements resolve dose-response decisions with fewer assays at controlled error? | Direct scientific utility; testable model and decision contribution | Sparse data cannot support broad guarantees; logged adaptive data do not identify every counterfactual policy | Recommended conditional flagship |
| B. Reliable phenotype profiling | Can interpretable representations generalize across compounds/sites? | Established public benchmarks and clear baselines | Crowded field; 2D evidence may remain distant from OoC | Preferred fallback if target-chip data fails |
| C. Virtual staining | Can label-free imaging preserve downstream biological measurements? | Visually legible demonstration and plausible workflow value | Missing paired data, hallucinated markers, pixel metrics without biological validity | Only with paired target-domain data |
| D. Research agent / data platform | Can a tool reduce analyst errors and improve reproducible processing? | Useful software contribution; measurable workflow | Generic wrapper, unsupported biological reasoning, weak algorithmic novelty | Supporting interface, not current flagship |
| E. Neural digital twin | Can a dynamical model predict unseen chip responses to intervention? | Strong domain fit and technical depth | Unidentifiable dynamics, tiny independent sample size, organoid-to-chip leap | Conditional extension after intervention-data gate |

Do not combine all five into an untestable suite. A method can be packaged as a complete workflow while keeping one central scientific claim.

## Recommended context of use

**User:** an in-vitro pharmacology researcher evaluating a compound on a specified chip assay.

**Decision:** which dose/measurement to collect next, whether the observed response exceeds a prespecified assay threshold, and whether evidence is sufficient to stop or requires more measurement.

**Input:** compound identifier and optional structure; documented dose and exposure; chip/donor/batch metadata; observed assay endpoints; measurement quality and missingness.

**Output:** a dose-response estimate with uncertainty; a supported-domain decision or abstention; ranked feasible next measurements; an evidence record linking every displayed value to actual observations and a versioned model.

**Primary hypothesis:** a hierarchical probabilistic response model with decision-aware acquisition reduces measurement cost relative to the best matched baseline at a predefined error tolerance.

**Secondary hypothesis:** transfer from compatible lower-cost assays helps when overlap is sufficient, while explicit discrepancy modeling and a transfer-off option prevent harmful borrowing.

**Boundary:** assay-level research decision support. No patient-specific treatment recommendation, clinical drug-safety certification, or validated whole-organ digital twin is implied.

## Why the liver-chip route comes first

A published Liver-Chip study provides real chip context and public supporting data [D1]. It is a candidate for reproducing assay relationships, not a ready-made large training set. Its 27 compounds are a small drug-level population; chip replicates do not become independent compounds. Before adoption, inspect whether dose-level observations, identities, replicate hierarchy, and censoring support our estimand.

The neural public recording resource [D2] is attractive but its README identifies only four organoids in the diazepam series. It supports narrow within-study analyses and stress tests. It cannot by itself support drug-generalization, broad neurotoxicity, or claims about perfused neural chips.

A second useful source is the 2025 microfluidic organoid-regimen work [D4]. It supplies relevant experimental optimization precedent and data, but observed adaptive experiments are not an exhaustive oracle. Use it to reproduce the original study, evaluate prediction within documented support, and design a stronger prospective benchmark—not to claim retrospective performance on experiments that were never measured.

## Conditional category choice

Start with **Model & Algorithm** as the intended category because the primary contribution is statistical learning and experimental design. Provide a reproducible workflow and demonstration regardless. Choose End-to-End System only if the final evidence truly includes reliable ingestion, inference, decision output, and validated workflow integration. Category names are not multipliers in the published rubric.

## Scenario calculation

The following ratings are **illustrative assumptions about completed, evidence-backed projects**, not measured scores. They make our preference inspectable and falsifiable. The axis definitions are in [Document 02](02-judging-strategy.md).

| Option | K ratings (I,T,V,R,P) | Z ratings (N,E,U,C,X) | K /100 | Z /100 | Conservative minimum |
|---|---|---|---:|---:|---:|
| A, with strong real validation | 9,9,8.5,9,8.5 | 9,8.5,9,9,9 | 88.50 | 88.75 | 88.50 |
| B, rigorous phenotype model | 8,8,8.5,9,8 | 8,8.5,8,8.5,8.5 | 82.00 | 82.50 | 82.00 |
| C, validated virtual staining | 8.5,8.5,7.5,8,9 | 8.5,8,8.5,8,7.5 | 83.00 | 82.00 | 82.00 |
| D, generic platform | 8,6.5,6.5,9,9 | 6.5,8,8,8.5,7 | 74.50 | 75.25 | 74.50 |
| A, inadequate data | 9,8.5,4,8.5,8.5 | 8.5,5,8.5,7,5 | 77.50 | 70.50 | 70.50 |

The last row reverses the recommendation. It is the most important result in the table: the preference for A depends on validation, not attractive naming. No optimistic rating is presently earned.

For mixtures of the two modeled scores, A's strong-evidence case remains above B because both endpoint scores are higher. That is only robustness to rubric weighting **given the assumed ratings**, not robustness to incorrect assumptions. If each project's component ratings can independently move by ±1, each score can move by ±10; A's 6.5-point lead over B is not robust to that uncertainty. Obtain evidence rather than refining speculative decimals.

## Public competitor snapshot

Two public discussion announcements were inspected on October 6:

- **SynapTwin-OoC** advertises a neural-chip digital-twin suite. The accessible post primarily exposes its title and a writeup filename; model performance could not be assessed. [C1]
- **HungDai AI BioLab** describes virtual fluorescence, neural morphology, and toxicity prediction. It reports results, but this review did not reproduce its code, inspect splits, or validate its numerical claims. Treat it as a competitor's self-description, not an established benchmark. [C2]

The logged-out Writeups page did not expose submissions in the available session; no comprehensive competitor audit or ranking was possible. Do not infer quality from votes or assume those posts represent the full field.

**Strategic inference:** generic neural digital-twin and virtual-staining positioning is already represented publicly. Differentiate through falsifiable assay efficiency, group-level validation, data compatibility, and uncertainty behavior. This does not prove the proposed method is unique; the prior-art matrix remains essential.

## Decision gates

1. If dose-level chip data and sufficient groups are available, proceed with A.
2. If only published aggregate chip endpoints are available, limit the first study to reanalysis and uncertainty; acquire independent dose-response data before broad claims.
3. If no admissible target-chip dataset supports A, adopt B with explicit proxy-domain scope. Do not silently rename 2D microscopy as chip data.
4. If strong matched neural-chip interventions become available, compare neural and liver routes using the same evidence criteria; sponsor alignment alone is insufficient.
5. If the proposed model loses to simple baselines, retain the simpler method, report the negative finding, and reformulate the contribution around a genuinely improved decision rule or benchmark.

No branch is chosen to save time. Branches reflect identifiable science and supportable claims.
