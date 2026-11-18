# Requirements register v1.0

Authoritative structured form: requirements.json. All requirements retained; product functionality remains unimplemented. Technical decisions selected under U11; no test/gate approval inferred. U11 removes specific-curriculum dependence from architecture. Exact source catalog and research citations remain in sources/.

## R001 — Audit context completeness before final specifications

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P0; phase: Gates; owner: Founder.
- Dependencies: None.
- Acceptance: All 27 pack files inventoried and historical GAP-001 explicit.
- Specification: [docs/00-context-completeness-audit.md](../docs/00-context-completeness-audit.md).
- Disposition: Retained in named phase; no implementation claimed.

## R002 — Preserve research originals and citations

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P0; phase: Gates; owner: Founder.
- Dependencies: R001.
- Acceptance: 36 research/evidence files hash-verified and unchanged.
- Specification: [sources/source-catalog.md](../sources/source-catalog.md).
- Disposition: Retained in named phase; no implementation claimed.

## R003 — Trace every available founder requirement without silently dropping future scope

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P0; phase: Gates; owner: Founder.
- Dependencies: R001.
- Acceptance: Stable IDs have source, phase, priority, dependencies, acceptance and spec; historical limitation declared.
- Specification: [execution/roadmap-and-gates.md](../execution/roadmap-and-gates.md).
- Disposition: Retained in named phase; no implementation claimed.

## R004 — Product vision, target users and jobs

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Gates; owner: Founder.
- Dependencies: None.
- Acceptance: Student/guardian/educator/teacher/operator jobs and primary outcome reviewed.
- Specification: [docs/01-product-vision-prd.md](../docs/01-product-vision-prd.md).
- Disposition: Retained in named phase; no implementation claimed.

## R005 — Choose first Egypt curriculum/age/subject unit

- Source: U1, U2, U4; status: Specified; not implemented; Founder requirement.
- Priority: P0; phase: Gates; owner: Founder.
- Dependencies: None.
- Acceptance: German/national-language-school/uploaded-curriculum starting scope recorded; remaining grade, level, edition, reviewer and buyer resolved before full G1 approval.
- Specification: [docs/01-product-vision-prd.md](../docs/01-product-vision-prd.md).
- Disposition: Retained for real-content pilot readiness; not a dependency of subject-independent architecture finalization (U11).

## R006 — Solo-founder maintainability

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Gates; owner: Founder.
- Dependencies: None.
- Acceptance: Work breakdown includes educator/legal/support effort and bounded scope.
- Specification: [execution/roadmap-and-gates.md](../execution/roadmap-and-gates.md).
- Disposition: Retained in named phase; no implementation claimed.

## R007 — Affordability and pricing hypotheses

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Gates; owner: Founder.
- Dependencies: None.
- Acceptance: EGP 300/month and EGP 300–500/course/semester modeled separately, not asserted viable.
- Specification: [economics/README.md](../economics/README.md).
- Disposition: Retained in named phase; no implementation claimed.

## R008 — Preserve ~100 prospects and supervised family/friends pilot context

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R005, R058.
- Acceptance: Interest not counted as revenue; appropriate pilot permissions and cohort plan documented.
- Specification: [docs/01-product-vision-prd.md](../docs/01-product-vision-prd.md).
- Disposition: Retained in named phase; no implementation claimed.

## R009 — Brand naming strategy and candidate screening

- Source: U1, U2, U5; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Gates; owner: Founder.
- Dependencies: None.
- Acceptance: Candidate list plus language, similarity, mark/domain screening and founder decision.
- Specification: [design/brand-and-design-system.md](../design/brand-and-design-system.md).
- Disposition: Retained in named phase; no implementation claimed.

## R010 — Identity/design system

- Source: U1, U2, U5, U10; status: Brand system v1 documented; detailed founder review pending; no product implemented; Founder requirement.
- Priority: P1; phase: Gates; owner: Founder.
- Dependencies: R009.
- Acceptance: Bilingual direction, editable tokens, components/states and contrast review specified.
- Specification: [design/brand-and-design-system.md](../design/brand-and-design-system.md).
- Disposition: Retained in named phase; no implementation claimed.

## R011 — UX journeys

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Gates; owner: Founder.
- Dependencies: R004.
- Acceptance: Student, parent, upload, voice and teacher flows reviewed.
- Specification: [design/brand-and-design-system.md](../design/brand-and-design-system.md).
- Disposition: Retained in named phase; no implementation claimed.

## R012 — Use existing TBD project folder; rename after chosen brand

- Source: U3, U10; status: Completed: original repository renamed Sebaverse; legacy path is compatibility symlink; Founder requirement.
- Priority: P1; phase: Gates; owner: Founder.
- Dependencies: None.
- Acceptance: Documents/Sebaverse is canonical; Git/research preserved, no duplicate master; app registration compatibility documented.
- Specification: [README.md](../README.md).
- Disposition: Retained in named phase; no implementation claimed.

## R013 — Egyptian Arabic conversational text

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: None.
- Acceptance: Educator-scored dialect explanations pass agreed rubric.
- Specification: [docs/05-model-routing-and-voice.md](../docs/05-model-routing-and-voice.md).
- Disposition: Retained in named phase; no implementation claimed.

## R014 — MSA text and academic terminology

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: None.
- Acceptance: Formal terms and understandable MSA tested separately.
- Specification: [docs/05-model-routing-and-voice.md](../docs/05-model-routing-and-voice.md).
- Disposition: Retained in named phase; no implementation claimed.

## R015 — English and code-switching text

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: None.
- Acceptance: Language switching preserves math meaning and source scope.
- Specification: [docs/05-model-routing-and-voice.md](../docs/05-model-routing-and-voice.md).
- Disposition: Retained in named phase; no implementation claimed.

## R016 — Egyptian Arabic/MSA/English voice

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: PoC then conditional Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R013, R014, R015.
- Acceptance: Each language meets speech fidelity, privacy and cost gates; text fallback remains.
- Specification: [docs/05-model-routing-and-voice.md](../docs/05-model-routing-and-voice.md).
- Disposition: Retained in named phase; no implementation claimed.

## R017 — Adaptive explanations

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R025.
- Acceptance: Explanations change with valid evidence and preference within allowed action.
- Specification: [docs/03-learning-intelligence.md](../docs/03-learning-intelligence.md).
- Disposition: Retained in named phase; no implementation claimed.

## R018 — Interactive lessons and visual manipulatives

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Future; owner: Founder + educator where learning/content is affected.
- Dependencies: R017.
- Acceptance: Reviewed interactive activities map to objectives with accessibility equivalents.
- Specification: [design/brand-and-design-system.md](../design/brand-and-design-system.md).
- Disposition: Retained in named phase; no implementation claimed.

## R019 — Guided problem-solving and hint ladder

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R025.
- Acceptance: Hints record assistance; learner can switch to independent check.
- Specification: [docs/03-learning-intelligence.md](../docs/03-learning-intelligence.md).
- Disposition: Retained in named phase; no implementation claimed.

## R020 — Exercises and quizzes

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R043.
- Acceptance: Reviewed item/rubric versions, independent mode and appeals work.
- Specification: [docs/03-learning-intelligence.md](../docs/03-learning-intelligence.md).
- Disposition: Retained in named phase; no implementation claimed.

## R021 — Timed mock exams

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Future; owner: Founder + educator where learning/content is affected.
- Dependencies: R020, R035.
- Acceptance: Syllabus blueprint, timing/accommodations, reviewed marking and post-exam plan.
- Specification: [docs/03-learning-intelligence.md](../docs/03-learning-intelligence.md).
- Disposition: Retained in named phase; no implementation claimed.

## R022 — Personalized exam preparation

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Future; owner: Founder + educator where learning/content is affected.
- Dependencies: R025, R035.
- Acceptance: Availability, objective coverage and delayed checks drive explainable plan.
- Specification: [docs/01-product-vision-prd.md](../docs/01-product-vision-prd.md).
- Disposition: Retained in named phase; no implementation claimed.

## R023 — Persistent progress across sessions

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R025.
- Acceptance: Resume and projection replay preserve valid learning evidence.
- Specification: [docs/03-learning-intelligence.md](../docs/03-learning-intelligence.md).
- Disposition: Retained in named phase; no implementation claimed.

## R024 — Mastery tracking with uncertainty

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R025.
- Acceptance: Unknown distinct from low; assisted success cannot promote status.
- Specification: [docs/03-learning-intelligence.md](../docs/03-learning-intelligence.md).
- Disposition: Retained in named phase; no implementation claimed.

## R025 — Immutable evidence ledger and correction lineage

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: PoC; owner: Founder + educator where learning/content is affected.
- Dependencies: R043.
- Acceptance: Duplicate/out-of-order/corrected evidence replays deterministically.
- Specification: [docs/03-learning-intelligence.md](../docs/03-learning-intelligence.md).
- Disposition: Retained in named phase; no implementation claimed.

## R026 — Misconception diagnosis

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R025.
- Acceptance: Wrong answer is hypothesis; distinguishing probe and expiry/review recorded.
- Specification: [docs/03-learning-intelligence.md](../docs/03-learning-intelligence.md).
- Disposition: Retained in named phase; no implementation claimed.

## R027 — Prerequisite knowledge graph

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R035.
- Acceptance: Reviewed edges/provenance, cycle detection and safe fallback.
- Specification: [docs/03-learning-intelligence.md](../docs/03-learning-intelligence.md).
- Disposition: Retained in named phase; no implementation claimed.

## R028 — Explainable adaptive learning paths

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R024, R027.
- Acceptance: Eligible next actions have stored reasons and override path.
- Specification: [docs/03-learning-intelligence.md](../docs/03-learning-intelligence.md).
- Disposition: Retained in named phase; no implementation claimed.

## R029 — Active recall and independent assessment

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R020.
- Acceptance: Unseen-family checks separate hinted/exposed answers.
- Specification: [docs/03-learning-intelligence.md](../docs/03-learning-intelligence.md).
- Disposition: Retained in named phase; no implementation claimed.

## R030 — Spaced repetition and delayed retention

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R029.
- Acceptance: Due reviews and independent delayed results recorded separately from completion.
- Specification: [docs/03-learning-intelligence.md](../docs/03-learning-intelligence.md).
- Disposition: Retained in named phase; no implementation claimed.

## R031 — Individual adaptation loop

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R025.
- Acceptance: Only validated learner evidence changes that learner projection.
- Specification: [docs/03-learning-intelligence.md](../docs/03-learning-intelligence.md).
- Disposition: Retained in named phase; no implementation claimed.

## R032 — System-wide evaluated feedback loop

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R031.
- Acceptance: Human triage, frozen regressions, versioned releases and rollback.
- Specification: [docs/03-learning-intelligence.md](../docs/03-learning-intelligence.md).
- Disposition: Retained in named phase; no implementation claimed.

## R033 — Optional controlled model improvement

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Future; owner: Founder + educator where learning/content is affected.
- Dependencies: R032, R059.
- Acceptance: Authorized curated training corpus, lineage and held-out evaluation before release.
- Specification: [docs/03-learning-intelligence.md](../docs/03-learning-intelligence.md).
- Disposition: Retained in named phase; no implementation claimed.

## R034 — Compare rules/BKT/logistic/IRT/deep KT

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Future; owner: Founder + educator where learning/content is affected.
- Dependencies: R025, R076.
- Acceptance: Calibration and held-out learning outcomes justify complexity; no AUC-only promotion.
- Specification: [docs/03-learning-intelligence.md](../docs/03-learning-intelligence.md).
- Disposition: Retained in named phase; no implementation claimed.

## R035 — Built-in versioned Egyptian curricula

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R005, R041.
- Acceptance: Exact authority/year/grade/subject/term/language pinned and approved.
- Specification: [docs/04-curriculum-and-rag.md](../docs/04-curriculum-and-rag.md).
- Disposition: Retained in named phase; no implementation claimed.

## R036 — National/language/IGCSE/IB/American and global curricula

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Future; owner: Founder + educator where learning/content is affected.
- Dependencies: R035.
- Acceptance: Each system gets independent reviewed syllabus mappings and rights, not translation-only labels.
- Specification: [docs/04-curriculum-and-rag.md](../docs/04-curriculum-and-rag.md).
- Disposition: Retained in named phase; no implementation claimed.

## R037 — Student-uploaded materials/custom curriculum

- Source: U1, U2, U4; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R041, R058.
- Acceptance: Private upload, relationship/purpose scope, quarantine and reviewed mapping.
- Specification: [docs/04-curriculum-and-rag.md](../docs/04-curriculum-and-rag.md).
- Disposition: Retained in named phase; no implementation claimed.

## R038 — Parent-uploaded textbooks/notes/worksheets

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R037.
- Acceptance: Verified guardian scope; private source/version/progress state visible.
- Specification: [docs/04-curriculum-and-rag.md](../docs/04-curriculum-and-rag.md).
- Disposition: Retained in named phase; no implementation claimed.

## R039 — OCR/layout/math/table/diagram extraction

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: PoC; owner: Founder + educator where learning/content is affected.
- Dependencies: R040.
- Acceptance: Arabic and bilingual representative corpus checked for critical notation loss.
- Specification: [docs/04-curriculum-and-rag.md](../docs/04-curriculum-and-rag.md).
- Disposition: Retained in named phase; no implementation claimed.

## R040 — Safe upload ingestion and quotas

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: PoC; owner: Founder + educator where learning/content is affected.
- Dependencies: R060.
- Acceptance: Streaming caps, magic/MIME, malware/quarantine and bounded parser fixtures pass.
- Specification: [docs/04-curriculum-and-rag.md](../docs/04-curriculum-and-rag.md).
- Disposition: Retained in named phase; no implementation claimed.

## R041 — Content rights/provenance/permissions

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P0; phase: Gates; owner: Founder.
- Dependencies: None.
- Acceptance: Every published source has hash, permission scope, expiry and reviewer.
- Specification: [docs/04-curriculum-and-rag.md](../docs/04-curriculum-and-rag.md).
- Disposition: Retained in named phase; no implementation claimed.

## R042 — Versioning, curriculum mapping and supersession

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R035.
- Acceptance: New edition does not silently relabel old evidence; reviewed migration exists.
- Specification: [docs/04-curriculum-and-rag.md](../docs/04-curriculum-and-rag.md).
- Disposition: Retained in named phase; no implementation claimed.

## R043 — Original reviewed item bank/rubrics

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: PoC; owner: Founder + educator where learning/content is affected.
- Dependencies: R041.
- Acceptance: 100 clear plus 20 ambiguous/adversarial item cases with reviewed keys.
- Specification: [docs/03-learning-intelligence.md](../docs/03-learning-intelligence.md).
- Disposition: Retained in named phase; no implementation claimed.

## R044 — RAG retrieval architecture

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: PoC; owner: Founder + educator where learning/content is affected.
- Dependencies: R039, R041.
- Acceptance: ACL/edition/approval filters apply before ranking and citation resolution.
- Specification: [docs/04-curriculum-and-rag.md](../docs/04-curriculum-and-rag.md).
- Disposition: Retained in named phase; no implementation claimed.

## R045 — Document-grounded answers and exact citations

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: PoC; owner: Founder + educator where learning/content is affected.
- Dependencies: R044.
- Acceptance: No fabricated source references; support/abstention gates pass per language.
- Specification: [docs/04-curriculum-and-rag.md](../docs/04-curriculum-and-rag.md).
- Disposition: Retained in named phase; no implementation claimed.

## R046 — Private upload isolation and deletion

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R044, R061.
- Acceptance: No cross-user chunks/cache leaks; withdrawal purges derived artifacts.
- Specification: [docs/04-curriculum-and-rag.md](../docs/04-curriculum-and-rag.md).
- Disposition: Retained in named phase; no implementation claimed.

## R047 — Parent dashboard and meaningful progress

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R024, R058.
- Acceptance: Evidence/uncertainty/next action plus plan and permissions, no default full chat.
- Specification: [design/brand-and-design-system.md](../design/brand-and-design-system.md).
- Disposition: Retained in named phase; no implementation claimed.

## R048 — WhatsApp progress reports

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Future; owner: Founder + educator where learning/content is affected.
- Dependencies: R047, R049.
- Acceptance: Verified opt-in recipient, minimal template, quiet hours, price/privacy review before send.
- Specification: [docs/06-safety-privacy-security.md](../docs/06-safety-privacy-security.md).
- Disposition: Retained in named phase; no implementation claimed.

## R049 — Notification preferences and revocation

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R058.
- Acceptance: Deduplication/quiet hours/opt-out; revoked relationships cancel jobs.
- Specification: [docs/06-safety-privacy-security.md](../docs/06-safety-privacy-security.md).
- Disposition: Retained in named phase; no implementation claimed.

## R050 — Future teacher/classroom functionality

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Future; owner: Founder + educator where learning/content is affected.
- Dependencies: R047, R060.
- Acceptance: Scoped roster, assignments, reviewed overrides and privacy-safe summaries.
- Specification: [design/brand-and-design-system.md](../design/brand-and-design-system.md).
- Disposition: Retained in named phase; no implementation claimed.

## R051 — Subscriptions/course-semester entitlements

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R007.
- Acceptance: Server-side grants/expiry/quotas; manual prepaid path while gateway unresolved.
- Specification: [architecture/system-and-data-model.md](../architecture/system-and-data-model.md).
- Disposition: Retained in named phase; no implementation claimed.

## R052 — Payment integration and refunds

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Commercial; owner: Founder + educator where learning/content is affected.
- Dependencies: R051.
- Acceptance: Signed idempotent webhooks, reversals and settlement reconciliation; actual terms verified.
- Specification: [architecture/system-and-data-model.md](../architecture/system-and-data-model.md).
- Disposition: Retained in named phase; no implementation claimed.

## R053 — Child safety and age-appropriate interactions

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P0; phase: Gates; owner: Founder.
- Dependencies: None.
- Acceptance: Three-language severe safety suite and named human escalation owner.
- Specification: [docs/06-safety-privacy-security.md](../docs/06-safety-privacy-security.md).
- Disposition: Retained in named phase; no implementation claimed.

## R054 — Accessibility and low-bandwidth/mobile UX

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R011.
- Acceptance: Critical journeys pass keyboard/screen-reader/zoom/slow-network checks.
- Specification: [design/brand-and-design-system.md](../design/brand-and-design-system.md).
- Disposition: Retained in named phase; no implementation claimed.

## R055 — RTL/LTR and accessible mathematics

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R054.
- Acceptance: Mixed equations/units/English terms preserve reading order and alternatives.
- Specification: [design/brand-and-design-system.md](../design/brand-and-design-system.md).
- Disposition: Retained in named phase; no implementation claimed.

## R056 — Child understandable notices and student agency

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R053.
- Acceptance: Explain AI uncertainty, independent checks, recording and help/appeal paths.
- Specification: [docs/06-safety-privacy-security.md](../docs/06-safety-privacy-security.md).
- Disposition: Retained in named phase; no implementation claimed.

## R057 — Guardian verification and consent lifecycle

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P0; phase: Gates; owner: Founder.
- Dependencies: None.
- Acceptance: Counsel-approved age/purpose method with withdrawal/dispute evidence.
- Specification: [docs/06-safety-privacy-security.md](../docs/06-safety-privacy-security.md).
- Disposition: Retained in named phase; no implementation claimed.

## R058 — Privacy/data processing and transfer review

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P0; phase: Gates; owner: Founder.
- Dependencies: R057.
- Acceptance: Purpose/data/processor register and current legal route signed before minors.
- Specification: [docs/06-safety-privacy-security.md](../docs/06-safety-privacy-security.md).
- Disposition: Retained in named phase; no implementation claimed.

## R059 — No automatic training on identifiable child chat

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P0; phase: Gates; owner: Founder.
- Dependencies: R058.
- Acceptance: Optional training requires separate rights/purpose review and deletion lineage.
- Specification: [docs/06-safety-privacy-security.md](../docs/06-safety-privacy-security.md).
- Disposition: Retained in named phase; no implementation claimed.

## R060 — Secure data/tenant/object/tool isolation

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P0; phase: PoC; owner: Founder + educator where learning/content is affected.
- Dependencies: None.
- Acceptance: Zero unauthorized access across >=100 negative cases, including vectors/files/exports.
- Specification: [docs/06-safety-privacy-security.md](../docs/06-safety-privacy-security.md).
- Disposition: Retained in named phase; no implementation claimed.

## R061 — Retention/export/deletion/backups

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R058, R060.
- Acceptance: Approved schedule, derived-store purge and restore deletion reapplication demonstrated.
- Specification: [docs/06-safety-privacy-security.md](../docs/06-safety-privacy-security.md).
- Disposition: Retained in named phase; no implementation claimed.

## R062 — Provider-agnostic adapters

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: PoC; owner: Founder + educator where learning/content is affected.
- Dependencies: R058.
- Acceptance: Generate/stream/usage/cancel/error contracts survive provider substitution.
- Specification: [docs/05-model-routing-and-voice.md](../docs/05-model-routing-and-voice.md).
- Disposition: Retained in named phase; no implementation claimed.

## R063 — Benchmark OpenAI/Claude/Gemini

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: PoC; owner: Founder + educator where learning/content is affected.
- Dependencies: R062.
- Acceptance: Matched eligible tasks record quality, language, latency and actual bills.
- Specification: [docs/05-model-routing-and-voice.md](../docs/05-model-routing-and-voice.md).
- Disposition: Retained in named phase; no implementation claimed.

## R064 — Benchmark Qwen/DeepSeek/Chinese model options

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: PoC; owner: Founder + educator where learning/content is affected.
- Dependencies: R062.
- Acceptance: Same rubric/terms/rights gates, no adoption based solely on nominal token cost.
- Specification: [docs/05-model-routing-and-voice.md](../docs/05-model-routing-and-voice.md).
- Disposition: Retained in named phase; no implementation claimed.

## R065 — Open-weight/local inference path

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Future; owner: Founder + educator where learning/content is affected.
- Dependencies: R062, R072.
- Acceptance: Weight rights, dialect quality, utilization and full operations cost justify hosting.
- Specification: [docs/05-model-routing-and-voice.md](../docs/05-model-routing-and-voice.md).
- Disposition: Retained in named phase; no implementation claimed.

## R066 — Jev-style classifier experiment

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: PoC; owner: Founder + educator where learning/content is affected.
- Dependencies: R025, R062.
- Acceptance: Frozen labeled comparison against rules and small LLM; calibration/cost/error report.
- Specification: [docs/05-model-routing-and-voice.md](../docs/05-model-routing-and-voice.md).
- Disposition: Retained in named phase; no implementation claimed.

## R067 — Deterministic state/business authority

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P0; phase: PoC; owner: Founder + educator where learning/content is affected.
- Dependencies: R060.
- Acceptance: Models cannot overwrite grade/mastery/consent/entitlement or tool scopes.
- Specification: [architecture/system-and-data-model.md](../architecture/system-and-data-model.md).
- Disposition: Retained in named phase; no implementation claimed.

## R068 — Model routing and qualified fallback

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: PoC; owner: Founder + educator where learning/content is affected.
- Dependencies: R062, R067.
- Acceptance: Privacy/quality eligibility precedes cost; no unapproved provider on failure.
- Specification: [docs/05-model-routing-and-voice.md](../docs/05-model-routing-and-voice.md).
- Disposition: Retained in named phase; no implementation claimed.

## R069 — Token/context/cache optimization

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: PoC; owner: Founder + educator where learning/content is affected.
- Dependencies: R062.
- Acceptance: Bounded prompts and summaries, isolated versioned caches; savings from actual receipts.
- Specification: [docs/05-model-routing-and-voice.md](../docs/05-model-routing-and-voice.md).
- Disposition: Retained in named phase; no implementation claimed.

## R070 — Token/audio usage accounting and limits

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: PoC; owner: Founder + educator where learning/content is affected.
- Dependencies: R062.
- Acceptance: Atomic reservations, cached units, retries/cancel receipts reconciled.
- Specification: [architecture/system-and-data-model.md](../architecture/system-and-data-model.md).
- Disposition: Retained in named phase; no implementation claimed.

## R071 — Voice economics and quotas

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: PoC; owner: Founder + educator where learning/content is affected.
- Dependencies: R016, R070.
- Acceptance: Cascade vs realtime matched workloads, connected/input/output units distinguished.
- Specification: [economics/README.md](../economics/README.md).
- Disposition: Retained in named phase; no implementation claimed.

## R072 — GPU/self-hosting sensitivity at 100/1k/10k users

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Future; owner: Founder + educator where learning/content is affected.
- Dependencies: R062, R070.
- Acceptance: Measured throughput/peak utilization plus idle/redundancy/ops; explicit break-even.
- Specification: [economics/README.md](../economics/README.md).
- Disposition: Retained in named phase; no implementation claimed.

## R073 — Operating cost/unit economics sensitivity

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Gates; owner: Founder.
- Dependencies: R007.
- Acceptance: Usage/FX/cache/voice/support/fees/tax/paid-active ratios modeled transparently.
- Specification: [economics/README.md](../economics/README.md).
- Disposition: Retained in named phase; no implementation claimed.

## R074 — Optimize cost per successful learning outcome

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R029, R070.
- Acceptance: All-cost numerator and valid independent-activity denominator; delayed endpoint tracked.
- Specification: [economics/README.md](../economics/README.md).
- Disposition: Retained in named phase; no implementation claimed.

## R075 — Domain/data model and API contracts

- Source: U1, U2, U11; status: Technical baseline v1 selected for audit; unimplemented and unbenchmarked; Founder requirement.
- Priority: P1; phase: Gates; owner: Founder.
- Dependencies: None.
- Acceptance: Entity authority, scopes, versions, idempotency and failure semantics reviewed.
- Specification: [architecture/system-and-data-model.md](../architecture/system-and-data-model.md).
- Disposition: Retained in named phase; no implementation claimed.

## R076 — QA/evals and language slices

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: PoC; owner: Founder + educator where learning/content is affected.
- Dependencies: R043.
- Acceptance: Frozen holdout, rubric agreement and per-language result counts; no leakage.
- Specification: [docs/07-qa-evals-and-operations.md](../docs/07-qa-evals-and-operations.md).
- Disposition: Retained in named phase; no implementation claimed.

## R077 — Architecture ADRs and decisions

- Source: U1, U2, U11; status: Technical baseline v1 selected for audit; unimplemented and unbenchmarked; Founder requirement.
- Priority: P1; phase: Gates; owner: Founder.
- Dependencies: R075.
- Acceptance: Selected stack, boundaries, tradeoffs and reversal triggers recorded in ADRs; execution/legal gates distinct from technical selection.
- Specification: [execution/roadmap-and-gates.md](../execution/roadmap-and-gates.md).
- Disposition: Retained in named phase; no implementation claimed.

## R078 — CI/CD and release lineage

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R076.
- Acceptance: Checks/artifact/manifest/staging/flag/rollback process reviewed and exercised.
- Specification: [docs/07-qa-evals-and-operations.md](../docs/07-qa-evals-and-operations.md).
- Disposition: Retained in named phase; no implementation claimed.

## R079 — Observability and redacted incident/cost metrics

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R070.
- Acceptance: Health/quality/spend/review dashboards without raw child data in labels.
- Specification: [docs/07-qa-evals-and-operations.md](../docs/07-qa-evals-and-operations.md).
- Disposition: Retained in named phase; no implementation claimed.

## R080 — Operational runbooks/recovery/support

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R061.
- Acceptance: Outage/leak/content/spend/deletion runbooks plus timed restore and workload budget.
- Specification: [docs/07-qa-evals-and-operations.md](../docs/07-qa-evals-and-operations.md).
- Disposition: Retained in named phase; no implementation claimed.

## R081 — Security/licensing source findings

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P0; phase: Gates; owner: Founder.
- Dependencies: R002.
- Acceptance: Audit findings retained with bounded confidence and adoption gates.
- Specification: [docs/06-safety-privacy-security.md](../docs/06-safety-privacy-security.md).
- Disposition: Retained in named phase; no implementation claimed.

## R082 — Quarantine inspected EduStudio revision

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P0; phase: Gates; owner: Founder.
- Dependencies: R081.
- Acceptance: Exact pin excluded from execution until independent provenance resolution.
- Specification: [docs/06-safety-privacy-security.md](../docs/06-safety-privacy-security.md).
- Disposition: Retained in named phase; no implementation claimed.

## R083 — Selective DeepTutor reuse only

- Source: U1, U2, U11; status: Technical baseline v1 selected for audit; unimplemented and unbenchmarked; Founder requirement.
- Priority: P1; phase: PoC; owner: Founder + educator where learning/content is affected.
- Dependencies: R081.
- Acceptance: Apache provenance/dependency closure; abandon extraction >3 repair days.
- Specification: [architecture/system-and-data-model.md](../architecture/system-and-data-model.md).
- Disposition: Retained in named phase; no implementation claimed.

## R084 — LearnHouse LMS fallback with AGPL/EE review

- Source: U1, U2, U11; status: Technical baseline v1 selected for audit; unimplemented and unbenchmarked; Founder requirement.
- Priority: P1; phase: Future; owner: Founder + educator where learning/content is affected.
- Dependencies: R081.
- Acceptance: Actual feature/license terms and combined-work analysis before use.
- Specification: [architecture/system-and-data-model.md](../architecture/system-and-data-model.md).
- Disposition: Retained in named phase; no implementation claimed.

## R085 — Framework choice remains reversible

- Source: U1, U2, U11; status: Technical baseline v1 selected for audit; unimplemented and unbenchmarked; Founder requirement.
- Priority: P1; phase: Gates; owner: Founder.
- Dependencies: R075.
- Acceptance: Django/DRF + React/TypeScript/Vite selected under U11; framework changes require an evidence-backed ADR amendment, not indefinite open comparison.
- Specification: [architecture/system-and-data-model.md](../architecture/system-and-data-model.md).
- Disposition: Retained in named phase; no implementation claimed.

## R086 — Roadmap/milestones/work breakdown

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Gates; owner: Founder.
- Dependencies: R003.
- Acceptance: Each milestone has dependencies, deliverable, owner, gate and stop condition.
- Specification: [execution/roadmap-and-gates.md](../execution/roadmap-and-gates.md).
- Disposition: Retained in named phase; no implementation claimed.

## R087 — Risks/unknowns/decision log

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Gates; owner: Founder.
- Dependencies: R001.
- Acceptance: Unknowns assigned owners/resolution evidence; no invented approval.
- Specification: [execution/roadmap-and-gates.md](../execution/roadmap-and-gates.md).
- Disposition: Retained in named phase; no implementation claimed.

## R088 — Codex instructions and phased prompts

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Gates; owner: Founder.
- Dependencies: R003, R077.
- Acceptance: Agents read authoritative docs; each prompt bounded by gates and evidence.
- Specification: [AGENTS.md](../AGENTS.md).
- Disposition: Retained in named phase; no implementation claimed.

## R089 — Version-controlled editable master artifacts

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Gates; owner: Founder.
- Dependencies: R002.
- Acceptance: Markdown/JSON originals and reproducible checks committed locally; no product code.
- Specification: [README.md](../README.md).
- Disposition: Retained in named phase; no implementation claimed.

## R090 — No premature implementation; bounded PoC after gates

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P0; phase: Gates; owner: Founder.
- Dependencies: R003, R077.
- Acceptance: G1–G3 approvals recorded before product code; PoC has budget/time/data limits.
- Specification: [execution/roadmap-and-gates.md](../execution/roadmap-and-gates.md).
- Disposition: Retained in named phase; no implementation claimed.

## R091 — Multimodal/photo/diagram tutoring

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Future; owner: Founder + educator where learning/content is affected.
- Dependencies: R039, R053.
- Acceptance: Authorized image interpretation cites source and confirms uncertain notation.
- Specification: [docs/04-curriculum-and-rag.md](../docs/04-curriculum-and-rag.md).
- Disposition: Retained in named phase; no implementation claimed.

## R092 — Independent assessment/grade appeal and teacher correction

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R025, R043.
- Acceptance: Disputed grades held/reviewed, correction lineage and affected replay.
- Specification: [docs/03-learning-intelligence.md](../docs/03-learning-intelligence.md).
- Disposition: Retained in named phase; no implementation claimed.

## R093 — Learning outcomes without unsupported efficacy claims

- Source: U1, U2; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R029, R030.
- Acceptance: Delayed retention/transfer, attrition and uncertainty reported separately from engagement.
- Specification: [docs/07-qa-evals-and-operations.md](../docs/07-qa-evals-and-operations.md).
- Disposition: Retained in named phase; no implementation claimed.

## R094 — Global-ready architecture without premature breadth

- Source: U1, U2, U11; status: Technical baseline v1 selected for audit; unimplemented and unbenchmarked; Founder requirement.
- Priority: P1; phase: Gates; owner: Founder.
- Dependencies: R036.
- Acceptance: Adding a supported subject uses reviewed content/profile/grader configuration without core schema or state-machine edits; specialist new capabilities use reviewed adapters; multi-subject fixture tests specified.
- Specification: [architecture/system-and-data-model.md](../architecture/system-and-data-model.md).
- Disposition: Retained in named phase; no implementation claimed.

## R095 — German tutoring using the learner-uploaded school curriculum

- Source: U4; status: Specified; not implemented; Founder requirement.
- Priority: P1; phase: Pilot; owner: Founder + educator where learning/content is affected.
- Dependencies: R037, R041, R045.
- Acceptance: Tutor uses the approved uploaded German unit as initial source; vocabulary/grammar/practice map to that version; no invented CEFR level or syllabus coverage.
- Specification: [docs/08-german-upload-first.md](../docs/08-german-upload-first.md).
- Disposition: Retained initial use case only; U11 explicitly excludes it as a platform-architecture dependency.

## R096 — Brand name, logo, slogan and guidelines before implementation

- Source: U5, U10; status: Brand system v1 documented; detailed founder review pending; no product implemented; Founder requirement.
- Priority: P1; phase: Gates; owner: Founder + educator where learning/content is affected.
- Dependencies: R009, R010.
- Acceptance: Founder reviews coherent name/logo/slogan concepts and selects a direction; screening limitations explicit; selected identity documented with usage rules.
- Specification: [design/brand-and-design-system.md](../design/brand-and-design-system.md).
- Disposition: Retained; no implementation claimed.

## R097 — Arabic-first brand/product experience

- Source: U8, U10; status: Brand system v1 documented; detailed founder review pending; no product implemented; Founder requirement.
- Priority: P1; phase: Gates; owner: Founder + Arabic design/native-language review.
- Dependencies: R010, R096.
- Acceptance: Arabic typography, RTL/mixed German content, Arabic messaging and parent/student tone lead all three identity trials; English is supported rather than the design default.
- Specification: [outputs/sebaverse-brand-system-v1/README.md](../outputs/sebaverse-brand-system-v1/README.md).
- Disposition: Retained in brand gate; no product implementation claimed.

## R098 — Latin-only Sebaverse logo

- Source: U8, U10; status: Brand system v1 documented; detailed founder review pending; no product implemented; Founder requirement.
- Priority: P1; phase: Gates; owner: Founder + Arabic design/native-language review.
- Dependencies: R010, R096.
- Acceptance: All logo/wordmark proposals use Latin Sebaverse; RTL layouts do not mirror the mark and do not add an Arabic logo.
- Specification: [outputs/sebaverse-brand-system-v1/README.md](../outputs/sebaverse-brand-system-v1/README.md).
- Disposition: Retained in brand gate; no product implementation claimed.

## R099 — Subject-independent platform architecture and audit handoff

- Source: U11, U12; status: Technical baseline v1 selected for audit; unimplemented and unbenchmarked; Founder requirement; engineering decisions.
- Priority: P0; phase: Gates; owner: Engineering + founder/external auditor.
- Dependencies: R075, R077, R094.
- Acceptance: Full system/data/runtime maps, every feature/function and phase, all audited repo dispositions and build/reuse boundaries; curriculum-independent extension contracts and multi-subject PoC; no German upload prerequisite.
- Specification: [architecture/technical-baseline.md](../architecture/technical-baseline.md).
- Disposition: Retained in architecture gate; execution gates tracked separately.

## R100 — Shared private GitHub source of truth and verified milestone pushes

- Source: U13; status: Foundation controls documented and locally/hosted-CI verified; future product phase suites not run; Founder requirement U13/U14.
- Priority: P0; phase: Foundation; owner: Orchestrator + independent reviewer.
- Dependencies: R078, R089.
- Acceptance: Reviewed milestone commits preserve existing history in EldonsLogic/sebaverse; actual local/remote SHA checked; no force push, secrets or child data published.
- Specification: [development/GITHUB-WORKFLOW.md](../development/GITHUB-WORKFLOW.md).
- Disposition: Retained as cross-agent and development governance; no pilot/deployment authorization inferred.

## R101 — Agent-neutral roadmap, task graph and durable handover

- Source: U13; status: Foundation controls documented and locally/hosted-CI verified; future product phase suites not run; Founder requirement U13/U14.
- Priority: P0; phase: Foundation; owner: Orchestrator + independent reviewer.
- Dependencies: R086, R088.
- Acceptance: Stable tasks, owners, dependencies, file scopes, acceptance, actual verification and exact next action persist across Codex/Claude/Antigravity sessions.
- Specification: [development/HANDOVER.md](../development/HANDOVER.md).
- Disposition: Retained as cross-agent and development governance; no pilot/deployment authorization inferred.

## R102 — Pinned coding-discipline guidance in shared project rules

- Source: U13; status: Foundation controls documented and locally/hosted-CI verified; future product phase suites not run; Founder requirement U13/U14.
- Priority: P0; phase: Foundation; owner: Orchestrator + independent reviewer.
- Dependencies: R081, R088.
- Acceptance: Record requested upstream commit/file/license limitation; adopt four ideas in project wording without overriding architecture/security or unnecessary scope.
- Specification: [development/ENGINEERING_RULES.md](../development/ENGINEERING_RULES.md).
- Disposition: Retained as cross-agent and development governance; no pilot/deployment authorization inferred.

## R103 — Extract and execute bounded verifiable agent-team guidance

- Source: U13; status: Foundation controls documented and locally/hosted-CI verified; future product phase suites not run; Founder requirement U13/U14.
- Priority: P0; phase: Foundation; owner: Orchestrator + independent reviewer.
- Dependencies: R088, R101.
- Acceptance: Preserve original image/hash and transcription; 30 contracts in six functions, actual scoped roster, task/evidence loop, fresh review and honest measured/not-measured workflow changes.
- Specification: [sources/agent-guidance/agent-team-transcription.md](../sources/agent-guidance/agent-team-transcription.md).
- Disposition: Retained as cross-agent and development governance; no pilot/deployment authorization inferred.

## R104 — Tests and review must pass after every phase before progression

- Source: U14; status: Foundation controls documented and locally/hosted-CI verified; future product phase suites not run; Founder requirement U13/U14.
- Priority: P0; phase: Foundation / all phases; owner: Orchestrator + independent reviewer.
- Dependencies: R076, R086, R101.
- Acceptance: Every phase declares relevant required test suites and acceptance; actual passing results/evidence, cleared blockers and independent review required; checker rejects not-run/failing/missing evidence and early next-phase starts.
- Specification: [development/phase-gates.json](../development/phase-gates.json).
- Disposition: Retained as cross-agent and development governance; no pilot/deployment authorization inferred.

## R105 — AG-UI tutor/interface protocol integration

- Source: U19; status: Approved integration direction; implementation gated at DEV-013.
- Priority: P1 (engineering sequencing); phase: MVP; owner: Engineering; founder for scope decisions.
- Dependencies: R060, R062, R067, R075.
- Acceptance: Reviewed pinned AG-UI schema/SDK adapter preserves validated blocks, same-origin sessions/CSRF, live scope, durable replay/cancellation and deterministic authority; malformed events/state patches and cross-learner/stale output fail; Arabic/accessibility/bundle and comparative transport results recorded before activation.
- Specification: [integration contract](../architecture/ag-ui-integration.md).
- Disposition: Required in DEV-013 after dependencies/F3 exit; no installation or implementation claimed.
