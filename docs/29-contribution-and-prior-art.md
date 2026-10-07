# Contribution assessment and final claim boundaries

## Defensible contribution

ZenithSync is a reproducible, control-aware finite-well design study and local research tool. Its strongest evidence is a frozen public-study transfer experiment: a model chosen on Farin data reconstructs held-out technical-plate log responses in a different organoid study with lower error than random purchasing, and meets a prespecified well-count efficiency criterion. The patient-weighted analysis, outcome-free design freeze, matched information budgets and retained negative development evidence make this an empirical contribution.

The work does not establish a new GP family, a new general experimental-design objective, or a state-of-the-art drug-response predictor. Its incremental advantage over the strongest included acquisition baseline is small. The report must describe the optimizer as an exact reference for a bounded design problem, not as a broadly superior replacement for greedy design.

## Closest relevant precedents

Sources checked October 6, 2026. This is a focused claim audit, not an exhaustive systematic review. Abstract-only checks do not constitute algorithm reproduction.

| Primary source | Established precedent and task difference | Consequence for our claim |
|---|---|---|
| [Gorodetsky and Marzouk, 2016, SIAM/ASA JUQ](https://doi.org/10.1137/15M1017119), [author repository record](https://dspace.mit.edu/entities/publication/6957ba1b-6d64-4bb5-a77e-23de149a8eef) | Integrated posterior variance is already an experimental-design objective, including joint continuous optimization rather than only greedy construction. | Finite integrated variance reduction and non-greedy design are not new inventions here. Our enumeration handles a small observed well pool and verified symmetries. |
| [Wang et al., 2020, eLife 9:e60352](https://eprints.whiterose.ac.uk/id/eprint/169449/) | GP dose-response uncertainty and downstream biomarker analysis are established. Repository abstract and indexed primary text checked; PMC full-page retrieval was challenged. | Uncertain dose-response fitting is not a sufficient novelty claim. Our endpoint is a raw log contrast and our task is selecting additional wells. No biomarker discovery is claimed. |
| [Tansey, Tosh and Blei, 2022, Annals of Applied Statistics](https://cjtosh.github.io/assets/pdf/bayesian_cancer.pdf) | A Bayesian dose-response model for cancer drug studies includes structured modeling of drug-screen observations. | Bayesian modeling of cancer dose-response is prior art. We have not reproduced or defeated this model; no universal predictor superiority is claimed. |
| [Vasanthakumari et al., 2024, Cancers 16:530](https://pmc.ncbi.nlm.nih.gov/articles/PMC10854925/) | Active learning for drug-specific cell-line response prediction and hit discovery compares multiple selection policies. Its labels are cell-line/drug response summaries, rather than individual control/treatment wells within a curve. | Active learning for anticancer screening is established. Its “greedy” policy exploits predicted response; our greedy baseline maximizes incremental variance reduction. Those labels must not be conflated. |
| [Takeno et al., ICML 2025](https://proceedings.mlr.press/v267/takeno25a.html) | Distributionally robust GP active learning targets worst-case expected prediction error over candidate target distributions. Abstract checked. | Our equally weighted finite-dose objective has no distributional robustness guarantee. No head-to-head comparison or dominance claim is made. |
| [Tang et al., AISTATS 2026](https://proceedings.mlr.press/v300/tang26d.html) | Addresses robust Bayesian active learning under model misspecification. Proceedings record checked; not reproduced. | Our fixed prior can be misspecified. Frozen external evidence narrows this concern but does not eliminate it or inherit another method's theoretical guarantees. |

No third-party implementation was copied for these comparisons. Citing a method does not establish license permission to redistribute its software; any later import would require a separate license check.

## What the ablations identify

Exact joint GP versus random joint GP changes the purchased subset while retaining the prediction model. It estimates the benefit of this selection rule relative to random purchasing. Exact joint versus greedy joint compares two optimizers of the same model objective. Exact joint versus exact diagonal changes both the posterior estimator and selected subset, so its effect cannot be attributed solely to acquisition. Random joint versus random diagonal uses the same random purchase policy and isolates the observation-covariance treatment more directly, subject to the fixed model choices.

Linear and PCHIP interpolation are included as strong simple reconstruction alternatives. All methods start with the same charged control and extreme-dose measurements. Random policies average twenty computational seeds, which are not independent patients. No prior-art model can be called defeated merely because its mathematical category resembles one of these baselines.

The frozen primary gain is 32.82% MSE reduction against random joint GP. Exact selection improves only 0.66% over greedy joint GP; the latter is the stronger comparison for algorithmic increment. Joint exact reduces MSE by 11.36% compared with the diagonal exact ablation. These secondary contrasts were not multiplicity-adjusted. They support mechanism analysis, not a new universal superiority claim.

## Mathematical back-checks

For raw log responses Y_i = a + f(x_i) + e_i with independent errors of variance s^2, reference contrasts Z_i = Y_i - Y_0 have covariance R = s^2(I + 11^T), after separating the latent process. Their diagonal entries are 2s^2 and their off-diagonal entries are s^2. Treating these contrasts as independent discards shared-reference uncertainty. An additional control reveals information about that shared reference error, explaining why it may have positive value even though its latent drug effect is fixed to zero.

Conditioning a joint Gaussian gives C_new = C - C[:,A] C[A,A]^{-1} C[A,:]. Thus the weighted latent variance reduction is nonnegative in exact arithmetic. The implementation uses stable solves and validates covariance properties; it does not invert arbitrary matrices explicitly. This model objective is distinct from realized audit error. Reducing model variance does not prove lower biological error under misspecification.

When a permutation of exchangeable coordinates preserves the entire conditional mean and covariance and the objective, all subsets in the same permutation orbit have equal objective value. Enumerating one subset per group count is therefore exact for this finite problem. The implementation verifies generating transpositions, checks all cardinalities are covered, and compares reduced search with brute force in tests. Equal labels alone are insufficient. Symmetry reduction is standard mathematical reasoning, not newly invented theory.

Because parameters and Gaussian covariance are fixed, posterior covariance and the chosen variance-minimizing batch do not depend on measured response values. Predictions do. This is a static design conditional on geometry and the measured set, not response-adaptive learning or an adaptive stopping policy. A future response-adaptive extension would need new development and untouched confirmation data.

## M6 decision and presentation

M6 has evidence for a narrow empirical improvement and component effects. It does not establish major algorithmic novelty or broad state-of-the-art performance. Keep that distinction explicit in scoring expectations: technical credibility is strong relative to unsupported complexity, but innovation scoring remains a material uncertainty. Do not retroactively enlarge the registered hypothesis to claim success on a stronger baseline.

Use this headline: **Control-aware assay design with frozen, patient-grouped public-cohort confirmation.** Immediately report the random and greedy comparators together. Present the exact optimizer as a small-design reference, the public-data evaluation as the scientific result, and the local tool as an implementation of that bounded result. A domain expert and an independent reviewer must still challenge the endpoint, control accounting and transfer assumptions before submission.
