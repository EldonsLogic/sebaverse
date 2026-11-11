# 04 — Adaptive learning engine

## Decision

**H — proposed:** start with a reviewed skill graph, evidence ledger, interpretable mastery rules and a conservative revision queue. Compare BKT and logistic predictors only once reliable events exist. A next-answer predictor is not automatically a better teaching policy. The comparison must measure independent retention and transfer, not only prediction accuracy.

## Mechanism comparison

| Mechanism | What it estimates | Useful properties | Failure modes | Pilot decision |
|---|---|---|---|---|
| Explicit evidence/rule model | Evidence that a skill is ready, fragile or unassessed | Inspectable, inexpensive, easy corrections | Thresholds are assumptions; item exposure and difficulty matter | Start here; label thresholds experimental |
| Bayesian Knowledge Tracing | Hidden mastered/not-mastered state from response sequence | Small state, explicit guess/slip/learning parameters | Weak identifiability, single-skill assumptions, calibrated parameters need data | Evaluate against rules; avoid fitting each child separately |
| IRT / logistic skill model | Ability relative to item difficulty | Useful for placement and item calibration | Cold items lack calibration; one ability axis may hide concepts | Later, pooled parameters plus item metadata |
| Deep/attention knowledge tracing | Response prediction from richer histories | Can learn sequence effects at scale | Data hunger, leakage, weak interpretability, accuracy need not imply learning | Defer unless repeatable held-out gains justify maintenance |
| Prerequisite graph | Expert or learned relationships among concepts | Explains remediation and curriculum mapping | Wrong edges create dead ends; graphs do not estimate mastery alone | Small reviewed graph with provenance |
| Misconception model | Candidate explanations for errors | Makes intervention specific | Same answer can arise from different causes; wording/language confounds | Distractors plus worked steps and confirmatory probe |
| Spaced review model | Recall probability or next useful review time | Addresses forgetting explicitly | Formula can overfit; recognition differs from production | Fixed expanding intervals first, adapt using delayed results |
| Bandit / RL teaching policy | Expected reward for choosing an action | Potential strategy optimization | Confounding, delayed rewards, risky exploration and small samples | Defer; teacher-approved comparisons only |

These are conceptual comparisons, not claims that each competitor uses these algorithms. Public implementation examples and reusable research tools are indexed in [11](11-sources-and-evidence.md); individual competitor disclosures belong in [02](02-competitor-deep-dives.md).

## What is established for the primary six

| Provider | Strongest disclosed adaptive element | Important boundary |
|---|---|---|
| Eedi | Misconception-linked diagnosis [W01] | Production state equations U |
| CENTURY | Graphs plus knowledge-tracing predictor [W06] | Specific KT family U |
| Khan Academy | Published mastery-review rules [W15] | Separate from Khanmigo dialogue |
| Synthesis | Micro-assessment teaching description [A02] | Mathematical estimator U |
| Duolingo | Historical Birdbrain and HLR disclosures [A05–A07] | 2026 deployment equivalence U |
| Squirrel | Fine-grained diagnosis and error-analysis subsystem [A13,A15] | Whole-platform tracer U |

## Proposed state model

Keep curriculum identity separate from conceptual similarity. A canonical concept such as fraction equivalence can map to several syllabus objectives, but evidence collected under one qualification/year does not automatically certify another. Suggested key: education system → awarding body → qualification → syllabus/version → academic year → grade → subject → objective. Textbook edition, language and page references are provenance, not replacements for those keys.

For each student/skill, store: evidence count, independent successful probes, recent failures, assistance level, item diversity, last independent check, next review date, estimated readiness, uncertainty, candidate misconceptions and provenance. Keep self-reported confidence separate from demonstrated performance. Do not infer intelligence, emotion, disability or a fixed “learning style” from chat behavior.

Use statuses such as **unassessed**, **needs support**, **developing**, **ready for review** and **retained**. These names avoid implying a clinically precise hidden probability. If probabilities are introduced, report calibration and intended prediction horizon. A 90% next-answer chance is not 90% mastery.

### Update and inconsistency handling

1. Validate item version, skill tag, scoring validity and whether the response is independent.
2. Preserve the original observation. Corrections append a superseding event rather than silently rewriting history.
3. Discount or exclude hints, repeated copies, suspected answer exposure, ambiguous speech and invalid items from independent mastery evidence.
4. A wrong distractor proposes a misconception; a second distinguishing question or worked explanation can corroborate it.
5. One failure after success makes the state uncertain. Recheck with a different item before aggressive demotion.
6. Route repeated difficulties to a prerequisite probe, then a short intervention and an unaided near-transfer item.
7. Revisit after delay; success immediately after an explanation cannot establish retention.

Any numerical update coefficients are pilot parameters to evaluate, not published optimal values. Keep the evidence visible to the teacher and permit audited overrides.

## Proposed selection policy

Filter first for curriculum, prerequisites, accessibility, content validity and age appropriateness. Rank eligible candidates by a transparent combination of exam relevance, diagnosed need, review urgency and uncertainty reduction. Reserve some activities for student choice and confidence-building, then avoid repeating identical items. Store the reason for each choice: “checking retention,” “fraction prerequisite,” or “teacher assignment.”

A graph cycle, empty candidate set or conflicting curriculum mapping should fall back to a reviewed activity and flag authoring review. Never allow a conversational model to invent a syllabus objective to make progression possible. Teacher assignments constrain the pathway; they should not corrupt recorded evidence.

## Evaluation before complexity

Use student-disjoint and chronological splits; do not randomly split adjacent attempts from the same learner across training and testing. Hold out item families and content versions when checking generalization. Report calibration/Brier or log loss alongside discrimination, with comparisons to simple baselines. Assess separately by language, age, curriculum and assistance level.

For policies, compare equal-time conditions with independent delayed quizzes and unfamiliar transfer items. Log attrition and missing outcomes. With a small pilot, use descriptive intervals and case review; do not claim subgroup superiority from a handful of learners. A model advances only if it improves the intended educational measure enough to offset added cost, errors and maintenance.

## Learning-outcome evidence and its limits

Retrieval experiments provide a reason to include delayed checks: Roediger and Karpicke found benefits on delayed prose recall even when immediate performance favored restudy [G18]. That result supports a mechanism, not a specific tutor or a guarantee of mathematics transfer.

In a Turkish high-school RCT, unrestricted GPT assistance improved practice performance but reduced later unaided scores; the guardrailed version avoided that measured harm without a clear exam gain [T01]. Design safeguards and independent assessment therefore matter more than assisted completion rates. The population, short follow-up and intervention constrain generalization.

Tutor CoPilot reports gains when AI assisted human tutors [G19]. It is evidence for a human-supported arrangement, not proof that autonomous replacement works. Eedi, CENTURY, Squirrel, Synthesis and Duolingo outcome evidence is separately qualified in 02; this pack does not pool incompatible populations, interventions and outcomes into a single league table.

A newly discovered 2026 mastery-based study [T02] deserves full-text follow-up before planning conclusions rely on it; only its search abstract was accessible here.
