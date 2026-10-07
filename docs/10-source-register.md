# Source register

Research date: **October 6, 2026**, using America/Los_Angeles for user-facing dates. Sources below are primary competition pages, dataset-provider documentation, or original research/method publications. Search-index recency and relative dates were not treated as exact event dates.

Historical access notes below describe the original planning inspection. Later ingestion and reproduction status for D1 and D4 is recorded in Documents 12–20. The new documentation refresh is recorded at the end of this register; raw data for its new candidates have not been inspected.

## Access and evidence labels

- **Live browser:** rendered page read in the browser, including asynchronously loaded content.
- **Web text:** source content returned by the web research tool; sometimes search extracts were needed where the full page was inaccessible.
- **Direct text:** small publicly linked text resource fetched and read; no full data ingestion.
- **Limited:** discovery/abstract/metadata evidence only, not a full methodology audit.

External pages can change. This register records what the review established and its limits; it is not an exhaustive archival copy. Read current rules again before entry and submission.

## Competition and organizers

| ID | Source | Access / evidence |
|---|---|---|
| K1 | [Kaggle overview](https://www.kaggle.com/competitions/ai-4-s-open-innovation-artificial-intelligence-for-life-scien/overview) | Live browser, full loaded sections: description, timeline, requirements, evaluation, data, awards, organization and judges |
| K2 | [Kaggle rules](https://www.kaggle.com/competitions/ai-4-s-open-innovation-artificial-intelligence-for-life-scien/rules) | Live browser: challenge-specific and foundational text, including their inconsistencies |
| K3 | [Model & Algorithm clarification](https://www.kaggle.com/competitions/ai-4-s-open-innovation-artificial-intelligence-for-life-scien/discussion/737840) | Live browser: host response allowing suitable public proxy datasets; reply timestamp August 27, 2026 in the displayed local tooltip |
| K4 | [Discussion of judging criteria](https://www.kaggle.com/competitions/ai-4-s-open-innovation-artificial-intelligence-for-life-scien/discussion/741126) | Live browser: host explanation of broad multidimensional assessment; participant criticism is opinion, not proof of bias |
| K5 | [ZHOU YINGTONG / aifckaggle](https://www.kaggle.com/aifckaggle) | Live browser: name, host badge, no public biography; no external identity match established |
| P1 | [Official Pazhou track page](https://www.aicompetition-pz.com/topic_detail/26) | Web text: distinct rubric, CNY awards, track focus and project-review format |
| P2 | [Pazhou expert pool](https://www.aicompetition-pz.com/expert) | Web text: six listed experts and organizer-stated roles; no track assignments |
| P3 | [Pazhou participation guidelines](https://www.aicompetition-pz.com/guidelines) | Web text: general registration, division, team, notification and ownership clauses |
| P4 | [Pazhou contact page](https://www.aicompetition-pz.com/contact) | Web text: official contact channel; no communication sent |

The registration-form URL in Document 01 comes from K1. The form was not opened or filled. No Google Drive account or files were accessed.

## Public competitor material

| ID | Source | Evidence boundary |
|---|---|---|
| C1 | [SynapTwin-OoC public announcement](https://www.kaggle.com/competitions/ai-4-s-open-innovation-artificial-intelligence-for-life-scien/discussion/746107) | Live browser: title and writeup filename; insufficient content to evaluate implementation |
| C2 | [HungDai AI BioLab public announcement](https://www.kaggle.com/competitions/ai-4-s-open-innovation-artificial-intelligence-for-life-scien/discussion/741153) | Live browser: self-described pipeline and results; no independent reproduction |

The [Writeups listing](https://www.kaggle.com/competitions/ai-4-s-open-innovation-artificial-intelligence-for-life-scien/writeups) showed a join prompt in the logged-out session. The review therefore does not cover every submission. No account was joined and no rules were accepted.

## Biological data and application research

| ID | Source | What was established / limit |
|---|---|---|
| D1 | Ewart et al., [Performance assessment and economic analysis of a human Liver-Chip for predictive toxicology](https://www.nature.com/articles/s43856-022-00209-1), Communications Medicine 2, 154 (2022); [PMC copy](https://pmc.ncbi.nlm.nih.gov/articles/PMC9727064/) | Original study and data-availability extracts: real-chip evaluation, study scale, public supplements and GEO pointer. Supplemental data files were not ingested. Some subsequent fetches hit access checks. |
| D1c | [Author correction](https://www.nature.com/articles/s43856-023-00249-1.pdf), Communications Medicine 3, 16 (2023) | Read PDF text: Table 3 had duplicated Table 2; corrected table provided. No biological conclusions inferred from an uninspected figure. |
| D2 | Sharf, [Extracellular Recordings from Human Brain Organoids Using High-density CMOS Arrays](https://zenodo.org/records/6578989); [Dryad DOI record](https://datadryad.org/dataset/doi:10.25349/D9031Z) | Dataset descriptions and file manifest read; raw signals not downloaded. File list reveals a duplicate checksum. |
| D2r | [Dataset README](https://zenodo.org/records/6578989/files/README_organoid_data.txt?download=1) | Direct text: array-to-organoid identities, four-organoid diazepam series, data formats and spike-sorting outputs. Decoded as Windows-1252 after UTF-8 failed. |
| D3 | Nebuloni, Do et al., [A fluid-walled microfluidic platform for human neuron microcircuits and directed axotomy](https://zenodo.org/records/11472099) | Provider record: source spreadsheets and linked code; record indicates a newer version. File contents and latest version not audited. |
| D4 | Yakavets et al., [Machine learning-assisted exploration of multidrug-drug administration regimens for organoid arrays](https://pubmed.ncbi.nlm.nih.gov/40737392/), Science Advances (2025), DOI 10.1126/sciadv.adt1851; [public data and README](https://datadryad.org/dataset/doi:10.5061/dryad.0vt4b8h8x); [author code repository](https://github.com/yakavetsiv/ml-mf_chemo) | Primary-source search extracts establish microfluidic ML-guided regimen work, data and Gryffin code availability. Full methods/code reproduction remains undone; not a validated baseline result for our task. |
| D5 | [BBBC021 provider documentation](https://bbbc.broadinstitute.org/BBBC021) | Read task, label counts, selected missing doses, recommended compound-level evaluation, and copyright notice. No image ingestion. |
| D6 | [JUMP hub](https://broadinstitute.github.io/jump_hub/), [dataset overview](https://broadinstitute.github.io/jump_hub/explanations/data_description.html), [FAQ](https://broadinstitute.github.io/jump_hub/explanations/FAQ.html) | Provider descriptions of multisite profiles/images, biological contexts, metadata and tools. Exact selected-data licenses and file preprocessing not audited. |
| D7 | [RxRx1 provider page](https://www.rxrx.ai/rxrx1) | Resource and displayed CC BY-NC-SA 4.0 license; no determination of compatibility with this submission. |

D2 references in other documents include the specific README evidence D2r. Broad data resources named by the organizer are treated as discovery pointers, not as validated training-ready benchmarks.

Follow-up source check: D4's rendered provider README was read directly through the web tool. It identifies candidate single-drug tables, replicate aggregation, and fitting exclusions recorded in Document 04. The archive has not been ingested; full methods and code reproduction remain pending.

## Mathematical and technical precedents

| ID | Source | Use / boundary |
|---|---|---|
| M1 | Kennedy & O'Hagan, [Predicting the output from a complex computer code when fast approximations are available](https://academic.oup.com/biomet/article-abstract/87/1/1/221217), Biometrika 87(1), 1–13 (2000) | Original multifidelity modeling precedent; applying it to heterogeneous biology requires additional assumptions |
| M2 | Kandasamy et al., [Multi-fidelity Bayesian Optimisation with Continuous Approximations](https://proceedings.mlr.press/v70/kandasamy17a.html), ICML (2017) | Original multifidelity acquisition precedent; not a proof for our proposed objective |
| M3 | Angelopoulos & Bates, [A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification](https://arxiv.org/abs/2107.07511) | Method reference for split conformal and marginal coverage; derivation in Document 05 explicitly states its assumptions |
| M4 | Gibbs & Candès, [Adaptive Conformal Inference Under Distribution Shift](https://proceedings.neurips.cc/paper/2021/hash/0d441de75945e5acbc865406fc9a2559-Abstract.html), NeurIPS (2021) | Distinguishes online coverage-frequency objectives from ordinary exchangeable calibration |
| M5 | [Conformal prediction under feedback covariate shift for biomolecular design](https://doi.org/10.1073/pnas.2204569119), PNAS (2022) | Original work identifying feedback-selection complications; not automatically applicable without its assumptions |
| M6 | Christiansen et al., [In Silico Labeling: Predicting Fluorescent Labels in Unlabeled Images](https://escholarship.org/uc/item/1g13v3wq), Cell (2018), DOI 10.1016/j.cell.2018.03.040 | Prior virtual-labeling work; useful counterexample to claiming basic virtual staining as new |
| M7 | Daulton et al., [Parallel Bayesian Optimization of Multiple Noisy Objectives with Expected Hypervolume Improvement](https://arxiv.org/abs/2105.08195) | Optional multiobjective extension, not necessary for the current single-decision specification |
| M8 | Ament et al., [Unexpected Improvements to Expected Improvement for Bayesian Optimization](https://arxiv.org/abs/2310.20708) | Numerical-stability precedent if later adopting EI-based acquisition; not implemented here |

## Research limits and exclusions

Searches also returned similarly named unrelated AI4S events, name-only person matches, and review articles with broad claims. These were not used to establish competition identity, judge identity, or our method's performance. No source proves that the proposed project will win or is globally novel.

The review covers publicly discoverable official pages, relevant host clarifications, the accessible competitor sample, and targeted data/method resources. The full judging panel, controlling rubric, complete participant field, individual eligibility, selected-data rights, and raw-data adequacy remain unresolved. These are specifically carried into the plan rather than hidden by the word “comprehensive.”

## Documentation refresh: October 6, 2026

K1 was reread in the rendered browser: the two-rubric discrepancy, registration form, required deliverables, category declaration and deadline remain as documented. K5 was reread: the named host/judge still has no public biography. P1 and P2 were reread through the web tool; no track-specific assignment of the general expert pool was established. No entry, form submission or organizer contact occurred.

| ID | Primary source | New use / access boundary |
|---|---|---|
| D8 | [Farin organoid-stroma data, v1](https://data.mendeley.com/datasets/fypp6xhkjy/1), DOI 10.17632/fypp6xhkjy.1 | Provider description and CC BY 4.0 label read. Candidate development data; files, donor counts and control mappings not audited. |
| D9 | [Metastatic colorectal cancer PDO data, v3](https://data.mendeley.com/datasets/hr94h42xdc/3), DOI 10.17632/hr94h42xdc.3 | Provider description and CC BY 4.0 label read. Candidate confirmation source; actual file completeness and biological independence not established. |
| M9 | Krause, Singh and Guestrin, [Near-Optimal Sensor Placements in Gaussian Processes](https://www.jmlr.org/papers/v9/krause08a.html), JMLR 9:235–284 (2008) | Publisher abstract and indexed PDF passages establish mutual-information/submodularity precedent. No theorem is transferred to our different variance-reduction objective; Document 22 supplies a direct counterexample. |
| M10 | Takeno et al., [Distributionally Robust Active Learning for Gaussian Process Regression](https://proceedings.mlr.press/v267/takeno25a.html), ICML (2025) | Publisher abstract read. Close prior art for target-distribution robustness; full-method review and reproduction pending. |
| M11 | Tang, Sloman and Kaski, [Representative, Informative, and De-Amplifying](https://proceedings.mlr.press/v300/tang26d.html), AISTATS (2026) | Publisher abstract read. Close prior art for acquisition under model misspecification; full-method review and reproduction pending. |

Documents 21–23 incorporate these sources as research directions and explicit limitations. Their availability is not evidence that a new method has been validated or that a top ranking is secured.


## Final contribution audit additions (October 6, 2026)

Document 29 records focused primary-source checks for Gorodetsky and Marzouk (2016), Wang et al. (2020), Tansey et al. (2022), Vasanthakumari et al. (2024), Takeno et al. (2025), and Tang et al. (2026). Links and access boundaries are retained there and in the technical report. The checks establish relevant precedents; they do not constitute reproduction of all cited algorithms or an exhaustive novelty search. The Wang PMC full-page fetch returned a browser challenge; its institutional repository record and indexed primary text supplied the scoped claim. No challenge was bypassed.
