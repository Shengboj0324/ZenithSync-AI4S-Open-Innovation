# Confirmed team, skeptical rubric interpretation and review handoff

> Current status update: the user has verified registration, eligibility and licensing, and will handle publication. See [the current implementation handoff](35-implementation-completion-handoff.md). Earlier pending statements below preserve the audit history and no longer request those confirmations.

This document incorporates the user's resumed-goal instructions. It supersedes earlier pending team/category statements, not the historical experiment or its frozen claims. Team: **ZenithSync**. Sole member and main contributor: **Shengbo Jiang**. Confirmed category: **Tool & Platform**. Designated reviewer: **Shengbo Jiang**. This is contributor self-review; designation is not completed review or independent review. Publication and submission will be handled by the user after local implementation.

## Answers to the organizer questions: working interpretations

These are our evidence-based operating decisions, not invented organizer answers. On this continuation, the [Pazhou track page](https://www.aicompetition-pz.com/topic_detail/26) was retrieved successfully. It gives weights of 30/25/20/15/10 for innovation, completion/effectiveness, practical value, completeness and trust. Direct retrieval of the [Kaggle overview](https://www.kaggle.com/competitions/ai-4-s-open-innovation-artificial-intelligence-for-life-scien/overview) failed through the web tool; its previously captured 30/30/20/10/10 rubric remains historical evidence, not a fresh verification. Neither source retrieval nor our interpretation establishes which conflicting rubric controls every round.

1. **Controlling rubric:** prepare complete evidence under both, keeping their labels and weights separate. Do not average them or infer an organizer tie-break. Lead with a running measurement planner, the shared-control mechanism, the frozen comparison and its limitations. The strongest included greedy baseline must appear beside the random baseline.
2. **Interdisciplinary bonus:** assume zero. A one-person entry does not establish a qualifying interdisciplinary team; do not add a speculative bonus to any score.
3. **Registration:** a completed project and a named team do not prove registration or eligibility. The participant must verify the account and any applicable external form. No receipt or eligibility evidence has been supplied, and no entry/terms acceptance has been performed here.
4. **Public/private data:** the current empirical core uses public data, so a private-data exception is unnecessary. Preserve acquisition hashes, exclusions, transformations and attribution. Public accessibility is not by itself a redistribution license.
5. **Leaderboard provisions:** the inspected track page describes expert evaluation and a Writeup aggregating required materials. Present this as a participant-defined, frozen benchmark; do not invent leaderboard scores, test-label access or competition-provided labels. Generic provisions cannot be silently declared inapplicable.
6. **Ownership:** our technical interpretation cannot settle contractual rights. Retain third-party notices and separate original code from source data and historical derived artifacts. No project license has been selected on the user's behalf. The source-by-source unresolved rights inventory is in document 33.
7. **Judges and defense:** use the verified track instructions, not biographical guesses about name-matched people or an unconfirmed expert pool. Prepare to explain the endpoint, covariance, selection objective, comparison, costs and limitations. Exact defense format and any update permissions remain unverified.

## Mathematical scoring logic

For rubric r, write S_r = sum_j w_rj q_rj, where q_rj is the judge's normalized assessment of criterion j and the published weights sum to one. We observe artifacts and experiments, not q_rj. Therefore numerical self-scores, confidence intervals for a competition score and a probability of winning cannot be derived from the experimental MSE interval.

A conservative planning objective is to improve the weaker of the two rubric assessments, min(S_K, S_P). This is a decision principle, not a computable score without justified criterion ratings. The dimensions differ, so a shared vector of ratings cannot simply be inserted into both weight lists. Evidence that improves completeness and reproducibility without weakening scientific honesty is useful under both. A tradeoff is not provably favorable unless its effects on both scoring systems are supported.

Winning also depends on other entries and unknown judge assessments. Even a known score would not imply first place without comparator scores. We consequently make no rank guarantee. Exact optimization of a conditional GP variance objective does not imply optimal biological predictions or optimal judge scores.

## Evidence and skeptical objections

| Criterion family | Evidence to show | Strongest limitation to answer |
|---|---|---|
| Innovation / technical approach | Shared-reference covariance, controls as purchased actions, exact finite-pool selection, covariance ablation | GP regression and integrated variance are established; exact improves MSE only about 0.66% over included greedy selection |
| Results / effectiveness | Frozen study transfer, 100 patient IDs, patient-weighted analysis, complete outputs | Retrospective technical-plate evaluation; no proof of cross-study patient non-overlap |
| Impact / practical value | Prespecified 20-25% fewer wells with noninferiority criterion passed | Isolated-context counting, no shared-control amortization, no prospective savings or clinical benefit |
| Reproducibility / completeness | Fresh environment, 127 passing tests, 27 byte-identical artifacts, report, CLI and browser demo | Tested environment only; media dependencies differ; public links still require user action |
| Presentation / trust | Negative development results, uncertainty diagnostics, source attribution, visible assumptions | Nominal 90% intervals are conservative; no full accessibility certification or independent human review |

## Contributor self-review to complete

Shengbo Jiang should record actual findings and dates, rather than signing a prefilled approval:

- Run the measured-well example; check that the control and extreme doses are already measured, and that selected additional wells match the displayed budget.
- Explain why reusing a reference induces off-diagonal noise covariance; verify that exactness is conditional on fixed parameters and the finite feasible set.
- Compare exact against greedy as well as random; retain unfavorable development findings and the conservative coverage diagnostic.
- Check that 20-25% describes purchased wells under the registered accounting, not demonstrated lab-cost savings.
- Read the report and watch/listen to the entire video, including pronunciation and the labeled captured demo image. Record unclear statements and corrections.
- Verify personal registration/eligibility, attribution, applicable licenses, public links and final submission status before publishing.

No boxes are marked complete on the user's behalf. Self-review is the user's chosen review route; it does not satisfy the original M10 requirement for independent review. That remaining distinction is documented rather than silently changing the milestone.

## Local implementation versus release

The implemented numerical workflow and its bounded validation are documented in 27-33. Team attribution and category are now resolved. This change does not require retraining, a GPU or a hosted app. The current source does require public code, a video and a report in the final Writeup; an online app is optional. The user retains publication, account actions and submission. No outbound message, upload, terms acceptance or public release is authorized by this handoff.

The outstanding scientific extension is prospective operational validation or a genuinely new frozen development/confirmation cycle. It is not correct to retune on the known confirmation outcomes and retain the original confirmation label. No such retuning was performed.
