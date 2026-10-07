# Logical and numerical audit

This is the planning-round audit. Actual implementation tests and measured-data results are tracked in [Document 12](12-implementation-record.md).

Audit date: October 6, 2026. Arithmetic was checked with a short local calculation during documentation authoring. No project model, biological experiment, or implementation benchmark was run.

## Checked planning calculations

| Check | Result | Interpretation |
|---|---|---|
| Kaggle weights | .30+.30+.20+.10+.10=1 | Normalized rubric |
| Pazhou weights | .30+.25+.20+.15+.10=1 | Different normalized rubric |
| Strong A scenario | K=88.50; Z=88.75 | Assumed ratings, not achieved scores |
| B scenario | K=82.00; Z=82.50 | Strong baseline alternative |
| C scenario | K=83.00; Z=82.00 | Rubric-dependent comparison with B |
| D scenario | K=74.50; Z=75.25 | Illustrative generic-platform case |
| Weak-data A scenario | K=77.50; Z=70.50 | Data weakness reverses recommendation |
| ±1 uncertainty per component | ±10 total per project | The proposed lead is not robust to rating uncertainty |
| Paired normal power approximation | ceil((1.96+.8416212)^2/.5^2)=32 | Illustrative independent pairs for effect size .5 |
| Cluster design effect | 1+99(.2)=20.8 | Depends on exchangeable equal-cluster approximation |
| Effective count example | 1000/20.8=48.0769 | Does not create 48 biological groups |
| 90% conformal, n=4 | ceil(5×.9)=5>4 | Vacuous finite-sample interval |
| 90% conformal, n=19 | ceil(20×.9)=18 | Quantile rank 18 |
| Zero errors, n=4 | 1-.05^(1/4)=.527129 | 95% one-sided upper error bound 52.7% |
| Zero errors, n=27 | 1-.05^(1/27)=.105019 | Upper error bound 10.5% |
| Zero errors, n=59 | 1-.05^(1/59)=.049508 | Below 5% under independent Bernoulli assumption |
| Minimum n for that bound | ceil(log(.05)/log(.95))=59 | Use relevant positive/negative population as appropriate |
| Example cost threshold | C_FN=20, C_FP=1 gives p*=1/21=.047619 | Illustrative assay decision costs, not clinical guidance |

For scalar conformal calibration, n=9 is the smallest n allowing a finite 90% interval with this rank construction. That finite interval can still be too broad, poorly estimated for subgroups, or scientifically inadequate. “Finite” is not “useful.”

## Mathematical back-checks

**Covariance:** B=LL-transpose is positive semidefinite; sums/products of appropriate valid kernels preserve covariance validity. Numeric conditioning still requires checks and documented jitter.

**Hill model:** zero dose yields baseline, EC50 yields half-response, and high dose approaches the asymptote. These properties do not identify parameters when observed doses cover only a narrow range.

**Chamber mass balance:** V dC/dt, Q(Cin-C), and kloss VC all have amount/time units. The equilibrium with positive Q is Q Cin/(Q+kloss V). The model's dimensions are correct; biological validity remains an empirical question.

**Censored observation:** P(Y>L) is a survival probability, not a point density at L. Censoring at an assay limit cannot be repaired by clipping values to that limit.

**Decision threshold:** compare losses C_FP(1-p) and C_FN p to derive p*=C_FP/(C_FP+C_FN). This derivation assumes those two actions and correctly specified costs. Add abstention as a third action rather than quietly changing the threshold.

**Value of information:** an exact posterior decision-maker allowed to ignore data cannot have negative expected information value. Approximation can yield negative estimates; inspect convergence and definitions instead of declaring the result a biological effect.

**Acquisition cost:** information divided by positive cost has the intended units of information per cost. Nonadditive setup costs invalidate a simple independent-candidate ranking unless evaluated explicitly.

## Adversarial counterexamples

| Tempting conclusion | Counterexample | Repair in plan |
|---|---|---|
| 10,000 windows give a large calibration set | They came from four organoids | Calibrate at intended independent unit; narrow claim |
| A high pooled AUROC establishes unseen-drug performance | Same compound/doses appear in train/test | Compound-disjoint protocol |
| A low reconstruction error establishes toxicity prediction | Label derived from the reconstructed feature itself | Independent endpoint |
| A source assay improves validation, so transfer is always useful | New target context reverses source correlation | Negative-transfer test and target-only option |
| 90% calibration remains valid after choosing the most unusual dose | Acquisition changes the target distribution | Independent audit stream / justified adaptive method |
| Neural organoids validate neural chips | Geometry, flow and exposure differ | Explicit proxy/target evidence layers |
| A digital twin reproduces training trajectories, so it predicts interventions | Multiple parameter sets fit those trajectories | Identifiability and unseen-intervention tests |
| Offline active learning can evaluate any chosen action | Unmeasured action has no observed outcome | Measured support or prospective experiment |
| Zero observed false negatives proves safety | Small positive sample gives wide bound | Report exact uncertainty and research scope |
| More modules imply greater technical innovation | None improves the primary outcome | Component ablation and simpler baseline |
| A perfect demo establishes a finished system | Demo uses cached selected outputs | Recorded/live labels and independent rerun |
| Strong internal rubric score predicts first place | Panel, field and scoring calibration unknown | Treat it as a planning diagnostic only |

## Scope consistency audit

- Documentation recommends a **conditional** project; no dataset or architecture is falsely called adopted, validated, or final.
- Both official rubrics are retained; no conflict or bonus is silently resolved.
- The named Kaggle host/judge is separated from the general expert pool and sponsor personnel.
- Official dates are recorded but no schedule, effort cap, or “minimum viable” scope is imposed.
- Technical methods are distinguished from new contributions that still require empirical evidence.
- Claims about real experiments, proxy biology, simulations and prospective evidence are separated.
- No code implementation, model training, public posting, entry, or organizer contact occurred.

## What remains to verify later

Full selected-data contents and rights; controlling organizer instructions; true team resources; endpoint/cost choices; baseline reproductions; statistical power under the actual design; external/prospective evidence; full artifact execution and video accessibility. The current documentation is complete as a research-and-planning package, not as a competition submission.

## Documentation verification performed

The local verification covered all 12 Markdown documents: local link destinations, defined source identifiers, paired code fences, paired display-math delimiters, and selected numerical/limiting-case assertions. There were 28 defined source identifiers. Git whitespace checking passed. These checks establish document consistency and selected arithmetic, not live availability of every external resource or correctness of an unimplemented model.
