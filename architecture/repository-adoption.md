# Repository adoption plan — v1.0

U11/U12 · 11 November 2026. **No whole tutoring/LMS repository will be adopted as Sebaverse.** Ready libraries are selected through narrow interfaces; product-specific learning, consent, rights, authorization and cost authority are owned. No upstream code is copied or installed by this documentation release.

The 22 audited repositories are accounted for below; none silently omitted. Exact inspected SHAs and historical licenses are in [machine-readable register](repository-adoption.json) and original A01. Inspection pins prove what was reviewed, not production suitability. Blank release locks are an explicit install-time condition, not an invented ready deployment. License observations are not legal clearance; models/data/assets and transitive packages may differ from code licenses.

| Repository | Decision | Phase | Concrete use / exclusion |
|---|---|---|---|
| [DeepTutor](https://github.com/HKUDS/DeepTutor) | reference_only | A4 | No runtime dependency in baseline. Study durable turn service and provider/cancellation patterns; optional extraction experiment only. |
| [LearnHouse](https://github.com/learnhouse/learnhouse) | deferred_lms_alternative | A7 | No source in proprietary core; retain LMS fallback if school workflows justify rights/AGPL/EE decision. |
| [EduStudio](https://github.com/HFUT-LEC/EduStudio) | quarantined | none | Audited pin remains quarantined; do not run its workflows/install scripts. No proven compromise is asserted. |
| [pyKT](https://github.com/pykt-team/pykt-toolkit) | deferred_offline | A7 | Deep knowledge-tracing benchmark only after representative lawful sequence data. |
| [PyEdmine](https://github.com/ZhijieXiong/pyedmine) | not_selected | A7 | Research alternative; no role in baseline runtime. |
| [pyBKT](https://github.com/CAHLR/pyBKT) | deferred_offline | A4/A7 | Compare estimator only after adequate labeled evidence; no fitted baseline dependency. |
| [py-irt](https://github.com/nd-ball/py-irt) | deferred_offline | A7 | Item calibration only when connected item-bank data supports fitting. |
| [py-fsrs](https://github.com/open-spaced-repetition/py-fsrs) | selected_adapter_comparison | A3/A4 | Use package API behind ReviewScheduler; compare fixed intervals; no source fork or mastery authority. |
| [pgvector](https://github.com/pgvector/pgvector) | selected_extension | A3 | PostgreSQL extension for scoped dense retrieval; exact search first; no separate vector service. |
| [Docling](https://github.com/docling-project/docling) | selected_library_isolated | A3 | Document conversion API in sandboxed parser worker; no upstream service/UI/tool framework. |
| [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) | conditional_fallback | A4 | Separate OCR adapter only if targeted page benchmark improves extraction within rights/runtime limits. |
| [SymPy](https://github.com/sympy/sympy) | conditional_subject_adapter | A4/A7 | Restricted typed symbolic checker for supported quantitative activities; never raw untrusted parse_expr. |
| [NetworkX](https://github.com/networkx/networkx) | not_required_baseline | A4 | Optional offline graph validation utility; relational edge tables are canonical. |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | deferred_voice_comparator | A4/A7 | Benchmark local ASR only after eligible model weights and CPU/GPU economics. |
| [Pipecat](https://github.com/pipecat-ai/pipecat) | deferred_realtime | A7 | Optional separate realtime media runtime after voice benchmarks; not needed for push-to-talk. |
| [OpenTelemetry](https://github.com/open-telemetry/opentelemetry-python) | selected_library | A2 | Python instrumentation APIs and allowlisted metadata exporter; no child payload capture. |
| [Promptfoo](https://github.com/promptfoo/promptfoo) | selected_dev_tool | A3/A4 | Offline prompt/provider evaluation runner; core features only after exact release-license check. |
| [Langfuse](https://github.com/langfuse/langfuse) | deferred_ops_tool | A7 | No full self-hosted observability stack now; separate core/EE and data handling review. |
| [Celery](https://github.com/celery/celery) | deferred_queue | A7 | Add only when measured job/DB contention justifies broker operations. |
| [Moodle](https://github.com/moodle/moodle) | not_selected_lms_alternative | A7 | No baseline dependency; stable LMS/rights/integration review if school demand changes. |
| [FrappeLMS](https://github.com/frappe/lms) | not_selected_lms_alternative | A7 | No baseline dependency; avoid merging identity and application runtimes. |
| [Chatterbox](https://github.com/resemble-ai/chatterbox) | not_selected | none | Do not choose audited retired implementation as maintained default; any future revisit needs new provenance/maintenance review. |

## DeepTutor extraction boundary

Baseline deliberately has **no imported DeepTutor runtime**. Audited interfaces worth comparing: `deeptutor/app/service.py` TurnApplicationService start/subscribe/cancel/submit input; `app/engine.py`; `runtime/orchestrator.py`; `services/llm/provider_registry.py`, `provider_factory.py`, `types.py`, `traffic_control.py`, `request_cache.py`, `telemetry.py`. These are candidate reference locations from A02, not a claim that they form a dependency-free drop-in module.

If an A4 spike extracts anything, produce exact file hashes, source pin, diff, transitive closure, notices, behavior/isolation/cancel/receipt tests and maintenance comparison. Stop at three engineer-days or if full upstream runtime/tool registries become required. Keep custom owned implementation if extraction loses its benefit. Do not import upstream sessions/guardian/mastery stores as the canonical platform state; do not expose arbitrary workspace tools to learners. A02 smoke checks do not certify the application.

## Standard platform dependencies outside the tutoring audit

These are architectural selections rather than claimed audited applications: Django (`django/django`), DRF (`encode/django-rest-framework`), React (official React project), TypeScript (`microsoft/TypeScript`), Vite (`vitejs/vite`), React Router (`remix-run/react-router`), TanStack Query (`TanStack/query`), PostgreSQL, psycopg, Uvicorn, a private S3-compatible SDK, pytest and Playwright. Adopt published libraries/APIs, not forked applications. ClamAV is a separately deployed scanning process. Docker/OCI packaging and GitHub Actions are delivery choices, not open-source tutoring modules. Exact versions/licenses/notices/compatibility are captured in dependency locks/SBOM before install, including any UI primitive/icon library later requested. No new UI library is silently added by the design system.

## Reuse acceptance

Every adopted artifact needs owner, purpose, exact version/digest, checksum, original URL, SPDX/license expression and notice files, model/asset permissions, transitive dependency closure, vulnerability results and exceptions, data/egress review, minimum adapter tests, update/removal plan and release approval. Preserve modified-source history and avoid making the research manifest a product lockfile. Copyleft components require an explicit rights/integration decision; process separation is not asserted as automatic legal resolution. No empty vulnerability query or recent commit establishes security.


## Founder follow-up U19 — AG-UI

The original 22 audit rows and preserved packs are unchanged. AG-UI is a new founder-requested follow-up: [pinned assessment](candidates/ag-ui.md), [ADR-013](adr/ADR-013-ag-ui-integration.md), [integration contract](ag-ui-integration.md). Direction: a minimal protocol adapter in DEV-013, with exact schema/SDK/dependency review before reuse. No package, whole scaffold or hosted service is adopted at this checkpoint. Machine-readable followup_repositories records this separately from the historical audit rows.

## Founder follow-up U20 — ingestion resources

[Eight-repository discovery](../development/evidence/dev-010-github-resources.md) compares current activity, licenses and concrete parser/scanner/OCR/isolation benefits. CAND-PDFIUM-001 records pypdfium2 as one alternate Docling backend under AUTH-008, not an adopted release. [Exact assessment](../workers/parser/alternate-review.md) removes the original parser wheel from the candidate resolution but leaves native/runtime and fidelity qualification open. Official scanner candidates remain held; AUTH-010 authorizes one distribution-maintained package assessment. Historical audit rows and current technical selections remain unchanged until an evidence-backed amendment qualifies.

AUTH-013 / ADR-014 update, 19 November: the founder selected a direct PyPDFium2 adapter for the first authored text-only PDF PoC. The original Docling advanced extraction direction and feature requirements remain. No SDK, native runtime, scanner or real upload use is cleared; the owned logic is developed with fake-engine unit tests while the runtime gates remain held.

## Later reference review — Athar, 25 November 2026

The original 22-repository audit above remains unchanged. U28 adds Athar at `a2e52a22fcc9e639a08c2e2040ac58479676ee24` as **reference_only**, bringing the current register to 23 entries. [Source review](../research/athar-review/README.md) and [selected feature refinements](athar-derived-refinements.md) cover cited hypotheses, missing-evidence requests, reviewed imports/overlays and deterministic parent reports. No dependency, code, curriculum pack or model is adopted. Root Apache-2.0 does not clear source-content, transitive or model rights; original runtime and phase gates still apply.
