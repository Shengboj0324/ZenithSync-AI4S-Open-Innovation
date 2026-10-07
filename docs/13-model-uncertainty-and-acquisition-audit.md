# Model uncertainty and acquisition audit

Updated October 6, 2026. This supplements the initial implementation record with a second, executable research iteration. The previous goal turn was **progress**: it established an actual-data pipeline and reproducibility evidence. This iteration preserves that result and investigates its numerical and scientific weaknesses. The requested validated halfway milestone remains open.

## Changes implemented

### Decision-value integration

For latent target response F with current variance v and a candidate observation Y with variance t, Gaussian conditioning gives

\[
P(F<T\mid Z=z,D)=\Phi\!\left(\frac{a-bz}{s}\right),
\quad a=T-\mu_F,\quad b=\operatorname{Cov}(F,Y)/\sqrt t,
\quad s^2=v-b^2,
\]

where Z is the standardized candidate observation. For false-positive/negative costs, the optimal action changes when this probability crosses p*=C_FP/(C_FP+C_FN). The integration switch is therefore z*=(a-s Phi^-1(p*))/b when b is nonzero.

`decision_voi_adaptive` integrates conditional Bayes risk using that switch and additional points bracketing the probability transition. It integrates over [-10,10]; omitted tail risk is bounded by 2 Phi(-10) times the larger decision cost. QUADPACK's remaining error estimate is a numerical diagnostic, not a rigorous floating-point certificate.

**Failure found and repaired:** an initial adaptive integrator split only at the action switch. With observation variance 10^-6, it missed the narrow risk peak and returned VOI 0.5 instead of approximately 0.49968169. The closed-form test caught the error. Transition-width breakpoints fixed it; the failure log is preserved in `artifacts/logs/tests-adaptive-voi.txt`.

The corrected implementation passes scalar Gaussian sign-error identities over noise variances from 10^-6 to 10^6, asymmetric-loss simulation comparison, cost scaling, weighted-target and negative-correlation tests.

### Finite Bayesian model averaging

`src/zenithsync/mixture.py` implements a finite mixture of nine Matérn GP hypotheses: length scales {0.75,1.5,3} crossed with noise SDs {10,20,40}, equal prior mass, common mean 100 and amplitude 50. These are declared exploratory assumptions. They were specified after the initial dataset exploration and are not a preregistered confirmatory model.

Component weights update only from available training/revealed observations:

\[
w_k(D)=\frac{\pi_k p(D\mid k)}{\sum_l\pi_l p(D\mid l)}.
\]

Total predictive covariance retains both within-model and between-model uncertainty:

\[
\operatorname{Cov}(F\mid D)=\sum_k w_k\left[\Sigma_k+(\mu_k-\bar\mu)(\mu_k-\bar\mu)^\top\right].
\]

Threshold probabilities and interval quantiles use the actual mixture distribution, not a Gaussian with matched moments. Intervals remain Bayesian model-based intervals, with no distribution-free or donor-generalization guarantee.

Mixture acquisition uses the total-variance identity:

\[
\mathbb E_Y\!\left[\operatorname{Var}(F\mid D)-\operatorname{Var}(F\mid D,Y)\right]
=\operatorname{Var}_Y\!\left[\mathbb E(F\mid D,Y)\right].
\]

Hypothetical measurements update both each component's response curve and the posterior model weights. This captures information about model identity that a within-component-only acquisition would omit. Predictive-mixture Gaussian quadrature evaluates the expectation; successive orders are compared, with a 0.01 squared-response-unit-per-cost tolerance. This is established Bayesian mathematics implemented for this research workflow, not an asserted novel algorithm.

Tests verify reduction to the single-GP formula, sequential-versus-batch Bayes updates, retained between-model variance, mixture quantiles, learning model identity, the total-variance identity against Monte Carlo, and hidden audit-outcome isolation.

## Measured evidence

### Nine-setting sensitivity study

Configuration: `configs/sensitivity-v1.json`. Every noise/smoothness setting is retained, with no selection of a best setting as an independently validated winner.

- At budget three, integrated variance reduction had the lowest reconstruction RMSE in eight of nine settings. Decision VOI had the lowest in the remaining setting.
- Corrected decision VOI beat random reconstruction in six of nine settings, but was worse in the other three.
- Fixed-node and corrected adaptive VOI produced different selected sets in 9 of 1,215 compared replay states. Small numerical differences can change acquisition order.
- The largest reported adaptive integration error estimate was approximately 5.01e-10. This estimate does not repair biological model misspecification.

All states and settings are retained in `artifacts/sensitivity_v1/traces.jsonl`; summaries and compound-level results are adjacent.

### Held-dose reconstruction and uncertainty

| Predictor | Macro RMSE | Observed 90% interval coverage | Mean interval width | Brier score |
|---|---:|---:|---:|---:|
| Fixed GP | 29.0687 | 0.9444 | 110.9625 | 0.07746 |
| Finite GP mixture | 28.5997 | 0.9167 | 112.2880 | 0.08257 |

All columns are compound-macro averages. Coverage refers to observed noisy assay rows under leave-one-dose-out evaluation, not latent curves, unseen donors, independent calibration, or a formal coverage guarantee. The mixture modestly improves RMSE but worsens Brier score and widens intervals. The work does not support a blanket claim of better uncertainty.

### Acquisition using the same mixture predictor

| Policy | Macro RMSE at budget 3 | Macro RMSE at budget 4 |
|---|---:|---:|
| Random, 20 computational seeds | 24.9913 | 24.2166 |
| Space filling | 24.2531 | 24.2212 |
| Mixture variance reduction | 23.8050 | 24.3885 |

At budget three, mixture variance reduction beats random on five of six compound curves. At budget four, its aggregate advantage disappears. This reversal remains visible; it cannot be omitted to claim consistent superiority. The initial fixed-GP variance policy had RMSE 24.1025 at budget three, so the new result is a modest exploratory gain, not evidence of a decisive competition advantage.

Only four of the 35 observed dose means fall below threshold 50. Threshold-error averages are unchanged across these policies. That threshold has not received qualified biological review. This sparse event population and small number of curves cannot establish reduced assay cost at controlled error.

## Engineering and reproduction

Thirty-six tests pass with warnings treated as errors. During development, macOS matrix multiplication emitted divide/overflow/invalid warnings despite finite bounded operands and finite outputs; a diagnostic compared the result against explicit weighted sums (maximum discrepancy about 5.82e-11). The production acquisition now uses explicit reductions and rejects nonfinite integrals; it does not suppress warnings. The earlier warning log remains in `tests-mixture-acquisition.txt`.

The fresh-environment verifier now covers both original benchmarks, the sensitivity grid, mixture reconstruction and mixture replay. Thirteen deterministic artifacts are compared byte for byte. See `artifacts/logs/reproduction.json` for authoritative pass/fail status and `fresh-environment.txt` for complete execution output. Earlier reproduction evidence is preserved as `initial-reproduction.json` and `initial-fresh-environment.txt`. The original source checkpoint is `artifacts/checkpoints/initial-source.tar.gz`.

Reproduce the added experiments with:

```sh
.venv/bin/python -m pytest -q -W error
.venv/bin/python scripts/sensitivity_benchmark.py
.venv/bin/python scripts/mixture_benchmark.py
.venv/bin/python scripts/mixture_replay.py
.venv/bin/python scripts/verify_reproduction.py
```

All experiments remain local. No public release, entry, paid compute or external communication occurred.

## Remaining work toward the requested milestone

The computational core now includes real-data baselines, numerical acquisition validation, finite model uncertainty, measured-pool evaluation and clean reproduction. This does not close the original gates for biological metadata, independent confirmation, credible operational cost/error benefit, tuned baseline comparison, robust abstention, or a reviewer-facing workflow.

The next scientific work must strengthen the data and task definition and evaluate the method against better-matched baseline tuning. Merely adding model complexity would not resolve four threshold-positive dose means, absent donor identities, or unknown control covariance. The same manual-intervention needs in Document 12 remain: authorized metadata/independent data, qualified endpoint/cost review, and organizer-rule resolution. None is currently required to continue local engineering.
