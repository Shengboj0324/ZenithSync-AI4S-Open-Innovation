# Mathematical specification

Implementation status is tracked separately in [Document 12](12-implementation-record.md). The following remains the full research specification; implemented primitives alone do not establish the proposed scientific claims.

Everything here is a **proposed research design**, not an implemented method or established result. Established component methods are cited in [Document 04](04-data-and-prior-art.md). Novelty belongs only to a precise tested improvement, not to equations already used in Gaussian processes, conformal prediction, or experimental design.

## 1. Define the estimand before the architecture

Let g denote an independent biological experimental group, c a compound, d a nonnegative dose, t an exposure time, b a batch, and s an assay context. Let y be a documented assay endpoint, with larger values oriented as greater injury only when biologically justified.

The initial target is

\[
f_s(c,d,t,x_g)=E[Y\mid c,d,t,x_g,s],
\]

within the measured assay context. The primary decision may be whether an assay-specific endpoint crosses a prespecified threshold at a specified dose/exposure. This conditional prediction is not automatically a causal intervention effect. Causal language requires randomized intervention assignment or a justified identification strategy.

Choose **one primary endpoint**, for example an independently measured relative functional readout, after data inspection and biological review. Do not create a convenient toxicity label from the same features used as predictors and claim external toxicity prediction.

Distinguish three tasks:

1. **Response interpolation:** estimate unmeasured doses of a compound with some observed doses.
2. **New-compound transfer:** estimate a compound with no target response observations, using admissible chemistry/source information.
3. **Adaptive experiment selection:** choose measurements to resolve an assay decision.

They require different splits and evidence. Success in task 1 does not establish task 2; predictive accuracy alone does not establish task 3.

## 2. Units, controls, and transformations

Use a dimensionless dose coordinate

\[
x_d=\log(1+d/d_0),\quad d_0>0,
\]

where d and d0 use identical concentration units. Unlike log(d), this includes zero-dose controls. Fix d0 and all scaling rules using training data or prespecified domain units.

For a strictly positive endpoint, one possible response is a log ratio to a matched control. Shared controls induce correlation between normalized observations. Either jointly model raw measurements and controls, or propagate their uncertainty and covariance; do not pretend all ratios are independent. An epsilon inserted to handle zeros changes the estimand and needs sensitivity analysis. For bounded viability use a likelihood appropriate to the assay; do not force a Gaussian onto boundary-heavy fractions without checking residuals.

No model may receive a post-treatment measurement that would be unavailable at its claimed prediction time. Baseline measurements may be used only if they are genuinely available in the proposed workflow.

## 3. Strong mechanistic baseline

For a monotone increasing endpoint, a Hill curve is

\[
m(d)=E_0+(E_{max}-E_0)\frac{d^h}{EC_{50}^{h}+d^h},
\quad h>0,\ EC_{50}>0.
\]

Use positive parameterizations for h and EC50, and constrain endpoint direction only when appropriate. For decreasing endpoints, Emax may be below E0; monotonic direction must be explicit.

Back-checks:

- m(0)=E0 and m(d) tends to Emax as d tends to infinity.
- At d=EC50, m is halfway between E0 and Emax.
- A narrow dose range far below EC50 does not identify EC50 and Emax separately.
- Bell-shaped or hormetic responses violate this model; compare with an unconstrained GP/spline.
- If 50% response is never reached, EC50 is censored or unidentified, not a numerical extrapolation to report as measured fact.

Use this baseline even if the final method is neural. A deep model that cannot beat a well-fit hierarchical curve has not earned its complexity.

## 4. Hierarchical response model

A scalar-endpoint starting point is

\[
y_i=m_{\theta_g}(d_i,t_i)+f_s(c_i,x_{d_i},t_i,x_{g_i})+u_{g_i}+v_{b_i}+\epsilon_i,
\]

with group and batch effects, and an explicit noise model. For example, u_g and v_b may have zero-mean Gaussian priors. Include only components the data can identify: an unrestricted residual GP, per-group curve, and separate random intercept can confound one another. Start with a simple hierarchical mean plus one residual process; use shrinkage and posterior diagnostics before expanding.

An optional chemical kernel can use fixed molecular fingerprints with a documented similarity kernel. Chemical features do not create information about unseen assay biology. If compounds are too few, fit a target-only dose model and narrow the claim.

For multiple measured endpoints, a linear model of coregionalization is one candidate:

\[
\operatorname{Cov}(f_a(x),f_b(x'))=\sum_{q=1}^{Q}B^{(q)}_{ab}k_q(x,x'),
\quad B^{(q)}=L_qL_q^\top.
\]

This construction is positive semidefinite when each kq is. Missing endpoints can be accommodated by conditioning only on observed values; missing-not-at-random measurements still require investigation. Keep Q small relative to independent groups. Additional endpoints are admitted only if their predictive gain survives ablation and their collection cost is counted.

### Censoring

If a latent value is reported only as Y>L, the likelihood contribution is

\[
P(Y>L)=1-\Phi((L-\mu)/\sigma),
\]

under a Gaussian observation assumption. For Y<U use the CDF, and for interval censoring use the CDF difference. Use numerically stable log-CDF/survival evaluations in future code. Replacing >1000 by exactly 1000 distorts the model and calibration.

## 5. Conditional transfer across assay contexts

Where matched inputs and scientifically compatible endpoints exist, consider

\[
f_H(x)=\rho f_L(x)+\delta(x),
\]

with independent priors for fL and discrepancy delta [M1]. H and L denote the target and lower-cost source context, not a declaration that the source is universally inferior. A cell-line morphology vector and a liver-chip albumin value are different observables; a mapping between them needs actual overlap and biological justification.

Under this model,

\[
\operatorname{Cov}(f_H(x),f_L(x'))=\rho k_L(x,x'),
\]

and target covariance is rho squared times kL plus the discrepancy kernel. If target/source overlap is absent, rho and discrepancy may be weakly identified. Do not claim trustworthy transfer merely because the posterior optimizer converges.

Required comparisons: target only; naïve pooled data; ordinary multifidelity GP; proposed context-aware variant. Include a deliberately incompatible source as a stress test. Enable transfer only when development-set evidence supports it; freeze that selection before test evaluation. A target-only fallback must remain available.

A learned image encoder is optional. Use frozen or carefully tuned representations only when data volume supports them. Pretrained corpus overlap with held-out compounds/images must be disclosed; unsupervised pretraining on the test cohort is a different transductive protocol, not a clean inductive test.

## 6. Exposure physics is conditional, not decorative

When flow and exposure measurements are available, a lumped chamber model might be

\[
V\frac{dC}{dt}=Q(C_{in}-C)-k_{loss}VC,
\]

where V has volume units, Q volume/time, C amount/volume, and kloss inverse time. Every term has amount/time units. At constant input,

\[
C^*=\frac{Q}{Q+k_{loss}V}C_{in}.
\]

If loss is zero and Q>0, the equilibrium is Cin. If Q=0, concentration decays from its initial condition; inlet changes do not instantaneously change a closed chamber. Nonnegative parameters and inputs should preserve nonnegative concentration.

This is a simplifying model, not a full description of adsorption, binding, metabolism, transport, or tissue exposure. Without measured Q, V, initial conditions, and enough concentration observations, different parameter combinations can fit the same endpoint. Do not market an unidentifiable loss parameter as a discovered mechanism. Use sensitivity ranges or omit this module.

## 7. Predictive uncertainty

The variance decomposition

\[
\operatorname{Var}(Y\mid x,D)=E_\theta[\operatorname{Var}(Y\mid x,\theta)]+\operatorname{Var}_\theta[E(Y\mid x,\theta)]
\]

separates observation variability from parameter/model uncertainty under the specified model. It is not an empirical guarantee that the uncertainty model is correct.

Check predictive residuals, calibration by supported group, interval width, and out-of-distribution behavior. An ensemble's variance alone is not a validated confidence interval. For new groups, integrate uncertainty in the new group effect instead of estimating it from hidden test outcomes.

### Split conformal at the correct unit

Fit predictor mu and scale sigma on training data, freeze them, then use an untouched calibration set. For n exchangeable independent calibration units,

\[
r_i=\frac{|y_i-\hat\mu(x_i)|}{\max(\hat\sigma(x_i),\epsilon)},\qquad
k=\lceil(n+1)(1-\alpha)\rceil.
\]

Take the kth ordered score; define q=infinity when k>n. The interval is

\[
[\hat\mu(x)-q\max(\hat\sigma(x),\epsilon),\ \hat\mu(x)+q\max(\hat\sigma(x),\epsilon)].
\]

The scale floor must be fixed without looking at calibration outcomes. Under the relevant exchangeability assumptions this gives marginal coverage, not guaranteed coverage for every compound, donor, or selected decision [M3].

This residual construction assumes the calibration outcome is observed. It cannot be applied unchanged to an assay-limit substitute for a censored outcome. Use a justified censoring-aware method or define an exactly observed endpoint and its target population; simply excluding censored cases may select an easier population and invalidate the intended claim.

Repeated measurements within a chip are not independent calibration units. For a fixed grid and simultaneous group-level coverage, define one score per group as the maximum standardized residual over that group's prespecified grid. Calibrate these group maxima and state the corresponding target: an entire new exchangeable group's grid. Variable/adaptively chosen grids require a different justified construction.

With four calibration groups and nominal 90% coverage, k=5: the distribution-free construction is vacuous. Thousands of image patches do not repair this. Cross-validation estimates and Bayesian intervals can still be reported with their own assumptions; they cannot be relabeled as finite-sample conformal guarantees.

### Shift and adaptation

New labs, scaffold shifts, selection of high-uncertainty candidates, and adaptive data acquisition can break exchangeability. Maintain an independent audit/calibration stream drawn from the claimed target distribution. If using an adaptive conformal or feedback-shift method, reproduce its assumptions and proof conditions [M4, M5]; a long-run coverage statement is not a guarantee for each experimental recommendation.

## 8. Decision rule and abstention

Let p be the calibrated probability that a specified assay endpoint exceeds a biologically prespecified threshold. Let C_FN and C_FP be costs of missed and falsely flagged responses. If the actions are flag versus do not flag, expected losses are C_FP(1-p) and C_FN p, so flag when

\[
p>\frac{C_{FP}}{C_{FP}+C_{FN}}.
\]

This is a mathematical decision threshold, not a clinical safety rule. Costs must come from the assay context, not be tuned on the test set to maximize our preferred result.

Allow a third action, **measure more / abstain**, with its own cost. Report selective risk at coverage c, where c is the fraction receiving a definitive decision. A method that abstains on everything has zero operational utility even if its accepted-case error looks good. Compare methods at matched coverage and count abstention costs.

## 9. Acquisition by value of information

Define posterior Bayes risk R(D) under the chosen decision loss and supported deployment distribution. For a feasible measurement e with cost C(e)>0, define

\[
VOI(e)=R(D)-E_{Y_e\mid D}[R(D\cup\{e,Y_e\})],
\]

and initially rank by VOI(e)/C(e). This is a one-step policy; it is not generally globally optimal. Under an exact coherent model with the option to ignore new data, expected information cannot increase optimal Bayes risk, so VOI is nonnegative. Negative estimates signal numerical approximation, inconsistent refitting, or definition problems and must be investigated.

An alternative objective for threshold/curve estimation is information gain:

\[
a(e)=\frac{I(Y_e;\psi\mid D)}{C(e)},
\]

where psi is the scientific quantity of interest. Do not substitute raw observation variance: high measurement noise may look uncertain while conveying little information about psi.

For parallel measurements, use joint information gain or sequential conditional selection; summing marginal values can repeatedly select redundant doses. Costs must include setup, controls, failure probability, and shared batch costs. Greedy ratios with nonadditive costs need explicit evaluation.

Feasibility constraints are experimental constraints: legal dose range, available assay, viable culture conditions, allowed batch size, and endpoint availability. An optimization constraint is not evidence of biological safety. Recommendations remain research proposals reviewed by the scientist.

## 10. Computational scale and escalation

An exact GP over N observations typically requires cubic factorization work and quadratic storage. Report N at the fitted observation level and the grouping used; do not inflate data by unnecessary windows. Use sparse/structured methods only when scale requires them, and measure their approximation error against exact fits on a tractable subset.

Advance to learned kernels, graph models, neural differential equations, or multimodal encoders only when they address a diagnosed baseline failure and pass matched validation. The user's priority of mathematical advancement is met by a correct, nontrivial, evidenced contribution—not by adding unidentifiable parameters.

## 11. Claims this specification does not establish

No proof of causal drug effect, universal calibration under shift, superior treatment selection, clinical utility, or real-world assay savings follows from this architecture. Those are separate empirical/identification questions. [Document 06](06-validation-protocol.md) defines the evidence needed.
