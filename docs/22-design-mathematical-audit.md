# Additional mathematical audit: controls, acquisition and stopping

This is a derivation and future evaluation specification. The identities below are established probability calculations, not a claim of algorithmic novelty or empirical superiority. They extend [Document 05](05-mathematical-specification.md).

## Shared controls change the likelihood

Suppose positive treatment and control measurements are modeled on the log scale. Let

\[
r_i=\log U_i-\overline{\log C},\qquad
\log U_i=\mu_i+\epsilon_i,
\]

where treatment errors are mutually independent with variances \(s_i^2\), and the shared control mean has error variance \(v_C\), independently of the treatment errors. Conditional on fixed latent means,

\[
\operatorname{Cov}(r_i,r_j)=\mathbf{1}_{i=j}s_i^2+v_C.
\]

Thus the observation-noise matrix is \(R=\operatorname{diag}(s_i^2)+v_C\mathbf1\mathbf1^T\). For multiple independent control groups it is block structured. Biological dependence requires additional justified covariance terms. The formula is exact for this log-measurement model; a log of the arithmetic mean of raw controls is a different statistic and cannot be substituted without a new derivation.

For n treatments with equal treatment variance s², the noise variance of their mean is \(s^2/n+v_C\). A diagonal approximation gives \((s^2+v_C)/n\), underestimating variance by \(v_C(1-1/n)\). For n=10 and s²=vC=1, the true value is 1.1 versus 0.2: a factor of 5.5. More treatment wells cannot remove the shared-control uncertainty floor.

This matters only when the source identifies shared controls and their measurement structure. Do not invent plate or donor identities from adjacent rows. If new control measurements are selectable actions, retain raw observations in a joint model; updating a control estimate changes all dependent normalized responses and must not be treated as an independent new treatment observation.

## General Gaussian acquisition update

Condition on current observations D and fixed model parameters. Let F be latent responses at the prespecified audit grid, Y_A the observations from a feasible candidate batch, and assume a jointly Gaussian conditional distribution. Write their conditional covariance as

\[
\begin{pmatrix}S_{FF}&S_{FA}\\S_{AF}&S_{AA}\end{pmatrix},\qquad S_{AA}\succ0.
\]

The posterior latent covariance after observing the batch is

\[
S_{FF\mid A}=S_{FF}-S_{FA}S_{AA}^{-1}S_{AF}.
\]

All blocks must include the appropriate conditioning on D. In particular, when future noise correlates with past noise, the familiar independent-noise shortcut may be wrong. The joint-covariance form avoids that hidden assumption.

For nonnegative audit weights W=diag(w), the integrated latent variance reduction is

\[
\Delta(A)=\operatorname{tr}(W S_{FA}S_{AA}^{-1}S_{AF})\ge0.
\]

Nonnegativity follows because the covariance reduction is positive semidefinite and W is positive semidefinite. It is bounded above by tr(W SFF). For one candidate with conditional variance v>0 and cross-covariance vector k, the reduction is \(k^TWk/v\). Independent observation noise belongs in v; irreducible future audit noise must not be described as removable latent uncertainty.

Numerical acceptance: solve linear systems rather than forming an inverse; compare batch and sequential conditioning on small cases; check symmetry, positive semidefiniteness within stated tolerance, and the reduction bounds. Duplicate noiseless measurements can make SAA singular. Remove true duplicates or use a documented singular-Gaussian treatment; adding arbitrary jitter changes the model.

When model parameters are uncertain, posterior component weights can change with acquired outcomes. The fixed-parameter covariance update does not capture that learning. Integrate the future observation distribution and recompute model weights, or explicitly label the acquisition conditional on fixed parameters. Compare numerical quadrature against analytic special cases and increasing resolution.

## Monotonic information does not imply greedy optimality

Consider independent standard-normal Z1 and Z2, target T=Z2, and observations X1=Z1+e1 and X2=Z1+Z2+e2, with independent errors of variance 0.1. Define F(A)=Var(T)−Var(T|X_A).

Observing X1 alone gives no information about T: its marginal gain is zero. After X2, however,

\[
\operatorname{Cov}(T,X_1\mid X_2)=-1/2.1,\quad
\operatorname{Var}(X_1\mid X_2)=1.1-1/2.1.
\]

The additional gain from X1 is

\[
\frac{(1/2.1)^2}{1.1-1/2.1}=\frac{1000}{2751}\approx0.363504>0.
\]

The marginal gain increased after another observation. This violates diminishing returns and disproves general submodularity of this variance-reduction objective, even with positive independent observation noise. The joint distribution is valid by its explicit construction from independent Gaussian variables.

Consequently, do not import a universal (1−1/e) greedy guarantee from [Krause et al.'s mutual-information sensor-placement work](https://www.jmlr.org/papers/v9/krause08a.html). The objective and assumptions must match the theorem. A minimum across model-specific utilities also requires its own analysis; taking a minimum does not automatically preserve submodularity.

For small feasible batches, compare the acquisition rule against exhaustive subset enumeration. For larger ones, report heuristic performance and computational cost honestly. An exact one-step posterior update does not prove globally optimal experimental design.

## Decision value and abstention

Let p be the probability that an assay condition meets a defined event, with false-positive cost CFP, false-negative cost CFN, and constant abstention cost CA, all nonnegative. The current Bayes risk is

\[
R(p)=\min\{C_{FP}(1-p),C_{FN}p,C_A\}.
\]

For an optional observation Y, its expected decision value is \(R(p)-E[R(p_Y)]\). Under a coherent posterior, \(E[p_Y]=p\); R is concave because it is the minimum of affine functions. Jensen's inequality therefore establishes nonnegative expected value before measurement cost. It does not prove a beneficial realized outcome for every Y, empirical calibration, or clinical utility.

Subtract acquisition cost only after converting decision loss and assay cost to compatible units. Dividing by cost provides a ranking heuristic; it does not solve a general multi-step stopping problem. If all one-step net values are nonpositive, a pair of complementary measurements may still be useful, as the preceding counterexample illustrates. Call such a stop rule myopic and test multi-step alternatives where feasible.

Freeze the event threshold and cost ratios independently of final-test outcomes. If the endpoint lacks a biologically justified threshold, use a curve-estimation target with an explicit tolerance rather than inventing a toxicity label.

## Operational cost and confirmation checks

A proposed batch cost is

\[
C(A)=\sum_{i\in A}c_i+\sum_b s_b\mathbf1\{A\text{ opens batch }b\}+C_{controls}(A)+C_{QC}(A).
\]

Define whether setup, mandatory controls, failed wells, repeats and staff effort are incremental or already incurred. Do not double count them. Equal weights are acceptable for a measured-row replay but must be called observation counts, not dollars, chips or lab hours.

Report complete cost/error curves and the proportion of campaigns reaching a prespecified error tolerance. If a baseline never reaches the tolerance, the ratio defining savings is not a known finite number. Preserve those failures, report restricted-budget summaries separately, and do not drop them when computing an average.

Audit errors must not feed candidate selection or operational stopping. Retrospective crossing of an audit-error threshold measures an oracle benchmark quantity, not an executable stopping policy. Report the policy's own stopping decisions and their independently audited errors separately.

For confirmation, freeze the target population, endpoint, audit weights, candidate support, initial observations, cost model, baselines, hyperparameter rules, seeds and inference method. Resample independent biological groups while keeping policies paired. Multiple doses, technical replicates and random seeds cannot inflate biological N. A second dataset establishes only the transfer that its actual assay and sampling support.
