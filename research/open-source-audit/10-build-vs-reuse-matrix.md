# Build versus reuse decisions

Scope: narrow pilot first; commercial breadth later. “Build” means product-specific logic on established infrastructure, not reimplementing cryptography, speech models or databases.

| Major feature | Decision | Concrete boundary and reason |
|---|---|---|
| Identity, password hashing, sessions, admin | Adopt | Django established mechanisms; MFA for staff; no bespoke crypto |
| Object authorization and student isolation | Build | Central student/guardian/course permission policy; negative tests for every read/write/tool |
| Guardian verification and consent | Build | Verified relationship, consent version/scope/expiry/revocation; repository guardian links alone insufficient |
| Course/semester catalog | Build small | One system/year/subject first; do not import full LMS workflow burden |
| Academic years/curriculum versions | Build | Immutable published versions; map concepts explicitly across revisions |
| Enrollment | Build | Canonical learner/course grant and status; distinguish paid, invited and consented |
| Teacher authoring UI | Adopt admin then adapt | Django admin with educator approval; polished authoring suite deferred |
| Full gradebook, assignment submission, school rostering | Defer | Reconsider Moodle/LearnHouse if teacher-led workflow is validated |
| Text tutoring | Adapt | Bounded provider adapter and typed tools; DeepTutor application/orchestration as reference |
| Whole DeepTutor workspace | Reject for pilot | Unneeded tools/plugins/partners and runtime complexity |
| DeepTutor small modules | Adapt conditionally | Extract only after dependency closure, rights and isolation tests; keep provenance and upstream comparison |
| LearnHouse source in proprietary core | Reject absent rights/AGPL decision | AGPL changes cannot be silently treated as permissive |
| LearnHouse as whole LMS | Defer | Native AI overlaps with DeepTutor; enterprise/OSS boundaries affect payments and analytics |
| Learner memory | Build | Structured assessed state and source-linked preferences; no unrestricted persistent dossier |
| Mastery estimation | Build explicit baseline | Unknown/learning/provisional/secure plus evidence counts; BKT optional; no false calibrated percentage |
| Deep knowledge tracing | Defer | pyKT offline benchmark only once representative sequence data exists |
| Item Response Theory | Defer fit | Expert difficulty now, connected item-bank calibration later |
| EduStudio current revision | Reject/quarantine | Observed workflow secret-exposure mechanism; provenance unresolved |
| Misconception taxonomy | Build with educator | Evidence-linked hypotheses, confidence and review; generated labels cannot become permanent fact |
| Learning paths and adaptive selection | Build | Teacher-reviewed prerequisite DAG plus rules; no online RL exploration |
| Spaced revision | Adopt/adapt FSRS | Independent review cards and versioned rating mapping; not mastery itself |
| Curriculum ingestion | Adapt Docling | Async restricted parsing, provenance, versioning and publication approval custom |
| Arabic OCR / math OCR | Benchmark then adapt | Start one parser; fallback PaddleOCR only when it improves target corpus |
| RAG | Build small/adapt | Filtered retrieval and citations; no multiple overlapping agent/RAG frameworks |
| Student uploads | Build control flow | Quarantine, safe types/limits/scanning/private storage/ownership and deletion |
| Quiz generation | Adapt model + build workflow | Draft only; validated schema, answer proof, rubric, educator approval |
| High-stakes exam marking | Defer autonomous marking | Human adjudication and appeals; deterministic low-stakes marking first |
| Mathematical equivalence | Adapt SymPy safely | Restricted grammar/AST, domain and units, process resource limits |
| Lesson/exam preparation | Build policy | Use approved objectives/items, retrieval and due revisions; simple templates first |
| Egyptian Arabic/MSA/English | Build evaluations + adapt model | Separate language/dialect metrics and RTL accessibility; provider fluency unproven |
| Push-to-talk voice | Adapt supported provider | Explicit session/minute quota; privacy and math entity checks |
| Full duplex low latency voice | Defer then experiment | Pipecat or current hosted voice; interruption/cancellation/cost tests before rollout |
| Parent dashboard | Build minimal | Progress and uncertainty summary; verified relationship; exclude raw conversations by default |
| WhatsApp progress alerts | Adapt direct Cloud API | Private minimal message + authenticated portal link; template/opt-out/budget controls |
| Payment collection | Adopt gateway API | Verify Egypt merchant support/account enablement; no card storage |
| Course/semester entitlements | Build | Server-side idempotent grants, expiry, refunds and quotas independent of gateway |
| Cost attribution/rate limits | Build domain ledger; adopt metrics | Reserve/finalize/reconcile per request; retries and cancelled voice still count |
| Jobs and retry semantics | Build narrow durable worker | Postgres outbox initially; defer Celery/broker until measurable need |
| Learning analytics | Build SQL projections | Independent outcomes, retention/transfer and coverage, not minutes-only dashboard |
| Offline policy/prompt evaluation | Adapt Promptfoo + own fixtures | Human-reviewed Arabic datasets, rubric/version registry, regression gates |
| Operational traces | Adopt OTel | Pseudonymous metadata; redaction and deletion custom; defer full Langfuse stack |
| Self-improvement loop | Build controlled release process | Reviewed evidence, offline eval, shadow/canary, human approval, rollback |
| Automatic training on identifiable chat | Reject | No such pipeline; only separately approved deidentified datasets with provenance |
| Self-modifying production tutor | Reject | Policy/model/prompt updates are immutable reviewed releases |
| Backup/security/patching | Adopt infrastructure + build procedures | Restore drill, dependency scan and incident playbook required before real minors |

Evidence is in audits 02–05 and security report 08. Every “adopt” still requires a pinned implementation release, a dependency lock, security updates and license notices. No entire repository is certified production-ready by this matrix.
