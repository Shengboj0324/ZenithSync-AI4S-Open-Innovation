# Judging strategy and verified judge information

## Known judges and boundaries

Kaggle names **ZHOU YINGTONG**, profile **aifckaggle**, as judge and competition host. The profile has no biography. No reliable affiliation, specialization, or publication identity was established. Name-only matches elsewhere were excluded. [K1, K5]

The host's replies confirm proxy-data eligibility with OoC relevance and defend multidimensional assessment for an open-ended hackathon. These statements do not reveal personal scoring preferences. [K3, K4]

The wider Pazhou expert pool lists the following people. **The page does not confirm any of them as judges of this track.** Roles are organizer-listed, not independently reverified employment claims. [P2]

| Person | Listed role |
|---|---|
| Fang Binxing / 方滨兴 | Chinese Academy of Engineering academician; honorary dean, Guangzhou University cybersecurity school |
| Tan Jianrong / 谭建荣 | Chinese Academy of Engineering academician |
| Chen Junlong / 陈俊龙 | European Academy of Sciences member; Russian engineering academy foreign member; Pazhou Laboratory deputy director; automation association leadership |
| Xiong Hui / 熊辉 | Associate vice president, HKUST (Guangzhou) |
| Wang Kai / 王凯 | PCI Tech chief AI scientist and central research institute head |
| Li Guanbin / 李冠彬 | Sun Yat-sen University computer-science school vice dean and professor |

CellShells is a supporting organization, not proof that any employee is a judge. Its stated neural-chip and predictive-simulation interests suggest application fit, not a published neural-project bonus. Prepare biological, technical, engineering, and application defenses based on the criteria rather than presumed personalities. [K1]

## Two published rubrics

| Kaggle dimension | Weight | Proposed evidence |
|---|---:|---|
| Problem importance / potential impact | 30% | Named user, consequential decision, measurable improvement |
| Technical approach / innovation | 30% | Contribution, assumptions, nearest methods, ablation |
| Results / validation | 20% | Independent groups, fair comparisons, uncertainty |
| Reproducibility / implementation | 10% | Public artifacts and independent rerun |
| Presentation | 10% | Understandable demonstrated workflow |

Source: [Kaggle evaluation](https://www.kaggle.com/competitions/ai-4-s-open-innovation-artificial-intelligence-for-life-scien/overview/evaluation).

The Chinese page instead gives **innovation 30%, completion/effectiveness 25%, practical value 20%, completeness 15%, interpretability/trustworthiness 10%**. [P1] These are distinct axes, not a reordering of the Kaggle table.

## Evidence chain

**Important assay decision → specified estimator → real experimental validation → measured assay savings at controlled error → reproducible output → honest report.**

| Artifact | Reviewer question it answers |
|---|---|
| Context-of-use card | Which researcher changes which decision? |
| Data/split manifest | What is the independent experimental unit? |
| Reproduced strong baseline | Does a simpler method already solve it? |
| Held-out effect with interval | How large and uncertain is the improvement? |
| Cost-versus-error curve | Are fewer measurements achieved at equivalent reliability? |
| Ablation / negative-transfer analysis | Which component produces the gain? |
| Failure and abstention demonstration | What happens outside the supported domain? |
| Clean reproduction log | Can a reviewer recreate the result? |
| Five-minute demonstration | Can they inspect the evidence easily? |

These are proposed team artifacts, not additional official requirements.

## Mathematical scoring abstraction

Use internal 0–10 ratings, without assuming that judges use that scale:

\[
S_K=3I+3T+2V+R+P.
\]

Here I=impact, T=technical contribution, V=validation, R=reproduction, P=presentation. Separately:

\[
S_Z=3N+2.5E+2U+1.5C+X,
\]

where N=novelty, E=effectiveness/completion, U=usefulness, C=completeness, X=trust. Each modeled score runs from 0 to 100.

The conservative planning objective is

\[
\max_{a\in\mathcal A_{eligible}}\min\{S_K(a),S_Z(a)\}.
\]

This is our heuristic, not an organizer aggregation formula. Do not average the rubrics and present the result as official. Do not add the team bonus without its scale and cap.

One internal Kaggle point in impact/innovation changes the modeled total by 3; validation by 2; presentation by 1. This does not establish effort allocation: an experiment can support several dimensions simultaneously, and those gains are correlated. Eligibility is a gate, not another weighted component.

## Internal review anchors

- **0–2:** absent or contradicted.
- **3–4:** asserted, illustrated, or synthetic-only despite real-world claims.
- **5–6:** functioning prototype, reasonable comparison, bounded evidence.
- **7–8:** strong held-out validation, useful effect size, reliable workflow.
- **9–10:** compelling original result, external/prospective evidence, robust uncertainty, frictionless reproduction.

These are demanding internal standards, not official scoring anchors. Have skeptical readers justify each rating with evidence and record disagreement. Reduce unsupported claims even if a hypothetical weighted total looks high.

## Limits of rank optimization

There is no defensible probability-of-winning estimate without calibrated historical judgments, the final panel and field, and the actual decision rule. Upvotes and participant counts are not substitutes. Every novelty claim needs a nearest method, a difference, a mechanism, and a falsification experiment. Every impact claim needs a measured operational quantity and a boundary.
