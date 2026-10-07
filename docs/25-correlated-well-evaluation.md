# Correlated-well estimation and exact batch design

Status: implemented and evaluated on development data. No reliable assay-saving, independent-confirmation or algorithmic-novelty claim has been established. M6–M10 remain unaccepted.

## Observation model and its limits

Within one admitted curve, let the raw log signal at dose coordinate x be

$$
Y_i=a+f(x_i)+\epsilon_i,\qquad f(0)=0,\qquad
\epsilon_i\overset{\mathrm{model}}\sim N(0,\sigma^2).
$$

The unspecified baseline a is a nuisance parameter. One purchased control Y_0 defines contrasts Z_i=Y_i-Y_0. Thus

$$
Z_i=f(x_i)+\epsilon_i-\epsilon_0,\qquad
R=\sigma^2(I+\mathbf1\mathbf1^\top).
$$

The off-diagonal term follows from actually subtracting the same measured control. It does not require inventing a physical plate association. Independent equal-variance raw log errors remain an assumption; unknown plate effects or heteroscedasticity can invalidate it. A second measured control has f(0)=0 but contains information about the shared normalization error after treatment observations are available. The tests exhibit this conditional value explicitly.

Dose coordinates are log1p(d/minimum positive dose), divided by their maximum. All coordinates come from design metadata. With a Matérn 5/2 base covariance k and a mean -b x, the pinned shape covariance is

$$
k_0(x,x')=k(x,x')-\frac{k(x,0)k(0,x')}{k(0,0)}.
$$

This ensures f(0)=0 exactly. The model does not enforce monotonicity, and its slope parameter is not a measured biological potency. Conditioning updates the entire joint target/observation distribution, including noise dependence among future observations. A numerical test verifies agreement with a raw-log model as its baseline prior variance grows large. Gaussian regression and these conditioning identities are established methods; see [Rasmussen and Williams, Chapter 2](https://gaussianprocess.org/gpml/chapters/RW2.pdf). Their use here is not claimed as a new algorithm.

The diagonal ablation replaces R with 2 sigma-squared I, preserving each observation's marginal variance while removing the shared-denominator covariance. A matched-parameter ablation and an independently retuned diagonal model are both evaluated.

## Tuning and isolation

For each evaluated organoid ID, tuning excludes every curve with that ID. Training uses only other IDs' replicate labels 1 and 2; no label-3 audit response participates. The 54 configurations combine amplitudes {1,2}, length scales {0.2,0.5,1}, raw-log noise standard deviations {0.15,0.3,0.6}, and mean slopes {0,2,4}. The objective is Gaussian contrast negative log likelihood, averaged over curves within an ID and then equally over training IDs.

All 28 folds selected amplitude 1, length 0.5, noise SD 0.3 and slope 2, for both covariance models. Consequently, the matched and independently tuned diagonal results coincide. This is a grid result, not a continuous optimum or evidence that hyperparameter uncertainty vanishes. Historical training measurements are not charged to the online campaign budget; they must be counted separately in any deployment economics.

Tests alter the held-out ID's entire pool and all audit outcomes and verify that its selected parameters do not change. Further tests poison hidden candidate responses, establish audit isolation throughout the replay, and verify policy-invariant posteriors at complete information.

## Greedy versus exact fixed-budget selection

Greedy IVR selects the next well with the largest conditional reduction in equally weighted latent response variance. Each assay has unit cost. No shared-control submodularity guarantee is assumed.

For exact design, the same three initial wells leave thirteen available actions. All 8,192 subsets are enumerated once per unique fixed model/design. The best subset of each size is retained. Six exact-coordinate/model combinations occur in this dataset, allowing design-only caching. Each budget is a **separate campaign**: optimal sets can be non-nested. The implementation does not describe these sets as one realizable sequential stopping trajectory.

A suppressor test establishes a concrete case where the best one-action set is not contained in the best two-action set and greedy selection loses. Exact optimality concerns posterior variance under the supplied fixed Gaussian law and feasible well set. It does not guarantee minimum biological prediction error under model misspecification.

## Measured results

The existing 136-curve, 28-ID, complete-case replay and all fourteen budgets are retained. Random designs use twenty seeds, averaged before ID aggregation. The GP replay contains 129,472 result rows, including interpolation estimators on the joint-IVR selected observations. Exact fixed-budget replay contains 3,808 curve/method/budget rows.

| Method/design | Mean MSE over budgets 3–16 | Marginal empirical 90% interval coverage |
|---|---:|---:|
| Linear interpolation / random | 0.362401 | Not supplied |
| Diagonal GP / greedy IVR | 0.354939 | 0.881234 |
| Joint GP / random | 0.336649 | 0.908638 |
| Joint GP / greedy IVR | 0.334610 | 0.900785 |
| Joint GP / exact fixed-budget batches | 0.330169 | 0.901196 |

Coverage is averaged across doses, budgets and IDs. It is not simultaneous curve coverage, a per-ID guarantee, or distribution-free calibration. Predictive marginal variance includes two fresh raw-log error variances for the audit treatment/control contrast; ignoring this term would evaluate latent intervals against noisy outcomes incorrectly.

Paired-ID bootstrap diagnostics use 10,000 resamples with seed 1729. They remain exploratory because the source was used during method development, ID independence is unverified, and several contrasts were examined:

| Contrast, candidate minus reference | Mean-budget MSE difference | Exploratory 95% bootstrap interval |
|---|---:|---:|
| Joint versus diagonal at common random designs | -0.027840 | [-0.066047, 0.011019] |
| Joint greedy versus joint random | -0.002039 | [-0.014509, 0.013466] |
| Joint exact batch versus joint random | -0.006479 | [-0.016098, 0.002838] |
| Joint exact batch versus joint greedy | -0.004440 | [-0.015641, 0.002797] |
| Joint exact batch versus linear random | -0.032232 | [-0.067410, 0.002835] |

Every interval includes zero. The point estimates support further investigation; they do not establish a reliable superiority claim. In particular, a favorable known-covariance calculation must not be substituted for these weaker measured results. No 20% assay reduction has been demonstrated.

## Reproduction and remaining gates

```sh
.venv/bin/python -W error scripts/farin_gp_benchmark.py
.venv/bin/python -W error scripts/farin_exact_design.py
.venv/bin/python -W error scripts/summarize_farin_gp.py
.venv/bin/python -m pytest -q -W error
```

Outputs are in `artifacts/farin_gp_v1` and `artifacts/farin_exact_v1`. They retain tuning configurations, training-ID membership, per-curve losses, full budget summaries, source-row measurement orders and exact enumeration counts. **92 tests pass with warnings treated as errors.** No external confirmation outcomes have been inspected in this step.

The separate [Kryeziu/Sveen/Lothe cohort](https://data.mendeley.com/datasets/hr94h42xdc/3) remains a candidate. Its public version-3 metadata identifies raw well measurements with plate/run fields and labels the dataset CC BY 4.0. Metadata inspection is not evidence of compatible replicate structure or validated independence. Scientific claims, admissibility and a confirmation analysis must be frozen before evaluating its outcomes. Stronger misspecification comparisons, operational assumptions, independent confirmation and the final presentation/release gates remain necessary.
