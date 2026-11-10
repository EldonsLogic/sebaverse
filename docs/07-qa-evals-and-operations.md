# QA, evaluations, CI/CD and observability

Proposed engineering gates, not achieved product results. A11 supplies initial PoC targets; G04/G05 guide learning measurement. Docs checks in this repository validate the planning package only.

## Evaluation layers

| Layer | Fixtures / outcome | Proposed gate / response |
|---|---|---|
| Domain | duplicate/out-of-order attempts, invalidated items, hint/exposure, corrections | Reproducible projection; unknown not zero; no assisted promotion |
| Authorization | >=100 negative cases across tenants/roles/files/retrieval/streams/export | Zero unauthorized reads/writes; blocker |
| Retrieval/grounding | 100 teacher-labeled questions, exact evidence, wrong-edition/unanswerable cases | recall@5 >=90%, supported claims >=90%, abstention >=90%, no fabricated citations |
| Grading | 100 unambiguous +20 ambiguous/adversarial reviewed items | >=95% agreement on clear low-stakes items; all ambiguous/unsafe cases to review |
| Math | equivalence/domain/units/notation, answer leakage, unsafe expressions | Reviewed critical cases pass; severe errors block affected content |
| Safety | multilingual child-safety, injection, relationship disputes | Reviewed severe-risk suite passes; human protocol operational |
| Speech | adult initial corpus and matched sessions | Entity fidelity >=95%, intelligibility >=4/5; recorded latency/cancel profile |
| Performance | 10 simultaneous text turns with documented region/model/context | p95 first text <3s, short completion <12s proposed; report errors and actual profile |
| Reliability | stream cancellation, worker crash, retry/webhook replay | No double charge/evidence; cancellation app target <=2s with provider caveat |
| Cost | 20-turn baseline, p95 and heavy tails | Typical session <=$0.05 AI candidate gate; final total-cost ceiling founder-approved |
| Recovery | clean-environment restore plus deletion markers | Timed proposed RPO24h/RTO4h; no re-exposure of deleted data |
| Accessibility | keyboard/screen reader, zoom/RTL/math/mobile/low-bandwidth | Reviewed critical journeys pass; audit current AA criteria |

Always report counts/denominators, confidence intervals where useful, reviewer disagreement and each language/corpus slice. All percentages are proposed gates requiring G3 approval, not universal pedagogical standards. A small curated set can miss severe failures; monitor and expand from incidents.

Learning evaluation uses initial diagnostic, unaided near-transfer and delayed unseen-family checks. Record assistance, exposure, missing outcomes/attrition and time-on-task. Separate rule-vs-BKT prediction evaluation from teaching-policy outcomes. Freeze holdouts; split learner/time/item families; prevent eval answer keys entering retrieval/training. Model judges are tools calibrated against human error labels, not sole truth. With 10–20 learners report cases/descriptive uncertainty; no causal efficacy claim.

## Delivery pipeline design

Docs PR: requirement/decision/ADR updates, source links/hashes and generated register consistency; no paid calls needed. Product PR after gates: format/type/static checks; unit/domain/property tests; authorization and provider contracts with fakes; database migration tests; offline Arabic/math/safety regression; dependency/license/SBOM/secret scan; reviewed parser/container provenance; build immutable artifact. Smoke tests alone never approve release.

Staging: synthetic data only, deployment from exact artifact, expand/contract migration checks, end-to-end student/guardian/reviewer journeys and timed backup restore. Paid provider benchmark is a separately bounded job with approved data/budget; no keys in general PR CI. Promotion: founder and educator sign changed content/grading, privacy/security gate owner signs relevant changes; freeze manifest and feature flags; small cohort then monitor. Roll back code/prompt/policy/index; do not erase evidence. Practice rollback before pilot. CI provider/hosting/branch-protection details are open until repository platform selected.

## Observability and support

Append usage receipts with request/session/task, provider/model/version, uncached/cached/output tokens, input/output/connected audio units, embedding/OCR/tools, retries, reservation/final charge and rate-card version. Reconcile vendor totals daily; discrepancy alert and cap anomalies. Metrics: p50/p95 stage latency, errors/cancellation, grounding/abstention, grading review, language slices, source/index versions, independent activity completion, review workload and cost/activity. Avoid names/phones/prompts as metric labels.

Minimal dashboards: service health; learning/content incident queue; cost/quota; consent/rights/revocations; ingestion/OCR; support backlog; recovery. Alerts need owner, threshold, action and quiet-hours expectations; not every missed day alerts a parent. Proposed immediate alerts for isolation failures, severe unsafe content, unexpected spend growth and broken deletion; exact paging service/coverage remains open.

Runbooks: provider outage, parser failure, incorrect item/grade, safeguarding, suspected leak, spend runaway, payment reversal, content takedown, backup restore and deletion. Founder workload budget includes educator review, support, onboarding and incident coverage. At 1,000/10,000 active students staffing is a modeled cost and capacity decision, not assumed free solo work.
