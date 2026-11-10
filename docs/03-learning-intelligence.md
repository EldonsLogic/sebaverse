# Learning intelligence and tutoring state machine

Proposed original design. Sources U1/U2, G04–G06, A04/A12. The learning evidence ledger is authoritative; narrative memory, a classifier's confidence and chat completion are not mastery.

## State and update semantics

Per learner/concept-version store status, independent evidence count, diverse item families, recent failures, assistance/exposure, last independent check, uncertainty, review due and projection version/event cursor. Statuses: unassessed, needs_support, developing, ready_for_review, retained. A no-evidence learner remains unassessed. Store student self-confidence separately. Misconceptions are expiring hypotheses with supporting/contradicting evidence and review state, never permanent deficit diagnoses.

Proposed baseline policy parameters, to be tested: two independent successes from distinct item families can move developing to ready_for_review; delayed success on a new family can mark retained. One later failure marks uncertainty and schedules a different probe; it does not erase prior success. These are design hypotheses, not validated psychometric thresholds. An invalidated item or grading correction appends a superseding event and replays affected projections. Repeated exposed questions, tutor-shown answers and uncertain speech do not qualify as independent success.

Grade using reviewed answer/rubric version. Deterministic arithmetic/symbolic checking uses validated typed AST/domain/units and resource limits, never raw untrusted expression execution. Open responses may receive model proposals, then schema/threshold validation; ambiguous/high-stakes results go to human review. Independent assessment does not reveal the answer key to the dialogue context. Wrong distractors prompt distinguishing follow-up questions; an identical wrong result can have several causes.

## Tutoring state machine

| State | Entry / action | Allowed exits | Evidence mutation |
|---|---|---|---|
| access_check | Resolve learner, consent, course grant and budget | diagnose, resume, blocked | None |
| diagnose | Reviewed short diagnostic; I don't know allowed | select, review_pending | Only validated independent attempts |
| select | Filter approved objectives/prerequisites and rank eligible actions | explain, practice, review, escalate | Store policy version and reason |
| explain | Short adaptive explanation/worked example with sources | guided, practice, clarify | Assistance/exposure only |
| guided | Ask a step, offer bounded hints, check reasoning | guided, prerequisite, practice, pause | Assisted evidence distinguished |
| prerequisite | Check a reviewed prerequisite or remediate | guided, practice, escalate | Valid checks only |
| practice | Announced unaided item, hint request ends independence | grade, guided, pause | Attempt pending validation |
| grade | Apply reviewed rubric, uncertainty checks | reflect, review_pending | Append once on valid grade |
| reflect | Explain result and invite correction | select, schedule, appeal | No model-written mastery |
| schedule | Due revision and bounded summary | done | Review events, not invented knowledge |
| review_pending / appeal | Hold uncertain grade; human adjudication | grade, invalidated | Corrections append lineage |
| safety_pause | Safe response and scoped human-owned escalation | approved_resume, end | Minimal restricted incident |
| paused / cancelled | Persist checkpoint, stop obsolete jobs/audio | access_check | No late answer can score wrong item |

All transitions validate session/item/turn IDs, role and expected state. Late streamed output from a cancelled turn is ignored for UI and state. Timeouts/retries are bounded; duplicate command keys replay results without double charge or evidence. Out-of-curriculum or insufficient-source requests clarify scope, abstain or offer reviewed general support clearly labeled, without forging curriculum alignment.

## Selection, memory and assessment

Eligible candidates satisfy current curriculum edition, age/accessibility, prerequisites, entitlement and content approval. Rank by assigned objective, diagnosed need, due review and uncertainty; expose reason codes and permit student choice among safe options. Empty/cyclic graphs fall back to reviewed content and authoring review. Teacher overrides choose activities without rewriting past evidence. Exam urgency may change scheduling, not falsify mastery.

Session memory holds current problem/checkpoint and a bounded summary with evidence references. Learner memory stores minimal volunteered preferences, not inferred emotion/disability/intelligence. Curriculum memory contains authorized source chunks. Safety records are separately restricted. A memory correction can be requested; expiry and deletion follow purpose-specific retention. No full transcript replay by default.

Assessment types: placement/diagnostic, low-stakes practice, independent near-transfer, delayed active recall and timed mock exam. Item bank includes objective/difficulty hypothesis, family, reviewed solution, rubric, language, accessibility variant, misconception distractors and exposure history. Mock exams need syllabus coverage blueprint, timer/accommodations, no hints during independent portion and separate post-exam remediation.

Fixed expanding review intervals are the baseline, with educator-adjustable due dates; FSRS is a comparison for recall scheduling, not a replacement for concept evidence. BKT/logistic comparisons use learner/time/item-family holdouts, calibration/log loss and sufficient pooled data. IRT needs item calibration. Deep KT/RL stays future unless it improves intended outcomes enough to justify data, risk and solo maintenance.

## Three controlled loops

Individual: validated attempt → evidence → deterministic versioned projection → reasoned next action. System: minimized failure categories → educator triage → original correction → frozen offline regressions → approved versioned release/flag/rollback. Model: optional authorized curated dataset → offline training → independent benchmark and rights/privacy review → release gate. Identifiable child chat and model-generated labels never become an automatic training corpus.

Each release manifest records code SHA, prompt/model snapshots, policy/grader versions, curriculum/item versions and retrieval/embedding index. Affected content can be quarantined and projections rebuilt. Evaluate independent delayed retention/transfer, not merely engagement or next-answer prediction. Tiny pilots support descriptive case review rather than causal marketing.
