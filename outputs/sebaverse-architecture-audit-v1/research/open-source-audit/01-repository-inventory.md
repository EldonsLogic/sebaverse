# Repository inventory and evidence method

Audit date: **10 November 2026**, Cairo client date. This pack answers the supplied architecture mission; it is not the final product or a proof-of-concept implementation.

## Inventory

All 22 repositories below were cloned into the isolated `work/repos/` research directory. Primary repositories received deeper source review; supporting projects received focused source/interface/license review, not equivalent full audits. Sparse/partial clones were used to avoid bundled assets/datasets. SHAs identify exactly what was inspected; default branches are not necessarily stable deployment releases.

“Open items” is GitHub API `open_issues_count`, which includes pull requests; it is a dated snapshot, not a defect count or quality score. Last commit is the pinned commit's date, not the most recent repository push or proof of maintenance frequency. Metadata was fetched from public GitHub API endpoints and is preserved in evidence.

| Repository | Exact inspected commit | Commit date | Inspected license | Open items* | Relevance / disposition |
|---|---|---|---|---:|---|
| [DeepTutor](https://github.com/HKUDS/DeepTutor) | `60fb3bdfddb30b7740c7ce3bd9b28d908f2af6db` | 2026-11-06 | [Apache-2.0](https://github.com/HKUDS/DeepTutor/blob/60fb3bdfddb30b7740c7ce3bd9b28d908f2af6db/LICENSE) | 394 | Deep audit 02; reference/selective extraction |
| [LearnHouse](https://github.com/learnhouse/learnhouse) | `7dc39bc0e116437d564e4c7f96974397e913c338` | 2026-11-08 | [AGPL-3.0 / separate EE](https://github.com/learnhouse/learnhouse/blob/7dc39bc0e116437d564e4c7f96974397e913c338/LICENSE) | 15 | Deep audit 03; LMS fallback subject to rights |
| [EduStudio](https://github.com/HFUT-LEC/EduStudio) | `4acedad91be841a3c3c109944b4180997b8a7260` | 2026-10-27 | [MIT](https://github.com/HFUT-LEC/EduStudio/blob/4acedad91be841a3c3c109944b4180997b8a7260/LICENSE) | 3 | QUARANTINE pin: secret-exposure workflow; offline research only |
| [pyKT](https://github.com/pykt-team/pykt-toolkit) | `ccbaf37b07e3e7ff7b2415475b2faacb967d54ea` | 2026-10-18 | [MIT](https://github.com/pykt-team/pykt-toolkit/blob/ccbaf37b07e3e7ff7b2415475b2faacb967d54ea/LICENSE) | 54 | Later deep-KT harness; selected source inspected |
| [PyEdmine](https://github.com/ZhijieXiong/pyedmine) | `31e434ae5b2d3bf9823044a4bd4582b184c0190b` | 2026-10-22 | [MIT](https://github.com/ZhijieXiong/pyedmine/blob/31e434ae5b2d3bf9823044a4bd4582b184c0190b/LICENSE) | 0 | Canonical upstream verified via package/docs/source |
| [pyBKT](https://github.com/CAHLR/pyBKT) | `0f4ea412e18f6bcbd396fdf2be68fdd43aebebb6` | 2026-11-01 | [MIT](https://github.com/CAHLR/pyBKT/blob/0f4ea412e18f6bcbd396fdf2be68fdd43aebebb6/LICENSE) | 67 | BKT offline benchmark; no fitted pilot results |
| [py-irt](https://github.com/nd-ball/py-irt) | `d4f4dbda1e591f2b2f471556b9664c6b2829131c` | 2026-11-01 | [MIT](https://github.com/nd-ball/py-irt/blob/d4f4dbda1e591f2b2f471556b9664c6b2829131c/LICENSE) | 1 | Later offline item calibration |
| [py-fsrs](https://github.com/open-spaced-repetition/py-fsrs) | `9446cb06605c597a063aeee49f7d188d42e34dc2` | 2026-08-09 | [MIT](https://github.com/open-spaced-repetition/py-fsrs/blob/9446cb06605c597a063aeee49f7d188d42e34dc2/LICENSE) | 0 | Spaced review; deterministic smoke passed |
| [pgvector](https://github.com/pgvector/pgvector) | `bcbb135db5f6f7539965e18565ddd5990efcf165` | 2026-11-09 | [PostgreSQL License](https://github.com/pgvector/pgvector/blob/bcbb135db5f6f7539965e18565ddd5990efcf165/LICENSE) | 17 | One-database retrieval candidate; vector/index source |
| [Docling](https://github.com/docling-project/docling) | `1ae470a1f4580881ed73853f64e0bf178f623c5e` | 2026-11-10 | [MIT code; models separate](https://github.com/docling-project/docling/blob/1ae470a1f4580881ed73853f64e0bf178f623c5e/LICENSE) | 967 | Priority parser; converter and options reviewed |
| [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) | `dab3fe35379033fdcb2d0e9572fac0b36c9a9ebf` | 2026-09-16 | [Apache-2.0 code; models separate](https://github.com/PaddlePaddle/PaddleOCR/blob/dab3fe35379033fdcb2d0e9572fac0b36c9a9ebf/LICENSE) | 259 | Conditional Arabic OCR fallback benchmark |
| [SymPy](https://github.com/sympy/sympy) | `8424f95e5fd61df195d490b8f9a22f075e450f9b` | 2026-11-10 | [BSD-3-Clause + bundled notices](https://github.com/sympy/sympy/blob/8424f95e5fd61df195d490b8f9a22f075e450f9b/LICENSE) | 5804 | Bounded marking; unsafe raw parse_expr warning verified |
| [NetworkX](https://github.com/networkx/networkx) | `e59d71890e745effb3724dc4b5620b23f92e0ee3` | 2026-11-04 | [BSD-3-Clause](https://github.com/networkx/networkx/blob/e59d71890e745effb3724dc4b5620b23f92e0ee3/LICENSE.txt) | 316 | Optional offline prerequisite DAG validation |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | `3ec025c4b7526e3fa121e527724ac43afa275a95` | 2026-11-10 | [MIT code; weights separate](https://github.com/SYSTRAN/faster-whisper/blob/3ec025c4b7526e3fa121e527724ac43afa275a95/LICENSE) | 18 | ASR fallback benchmark; transcribe interface reviewed |
| [Pipecat](https://github.com/pipecat-ai/pipecat) | `36d53278fd296bb63a8a2f9a3ffbfbf16fa84112` | 2026-11-10 | [BSD-2-Clause](https://github.com/pipecat-ai/pipecat/blob/36d53278fd296bb63a8a2f9a3ffbfbf16fa84112/LICENSE) | 449 | Optional audio worker; PipelineWorker API reviewed |
| [OpenTelemetry](https://github.com/open-telemetry/opentelemetry-python) | `5546285fc885858ce580350563e861681aa642fb` | 2026-11-10 | [Apache-2.0](https://github.com/open-telemetry/opentelemetry-python/blob/5546285fc885858ce580350563e861681aa642fb/LICENSE) | 444 | Tracing API; no raw student data by default |
| [Promptfoo](https://github.com/promptfoo/promptfoo) | `b3603fab85bb331da98a8b68ca442e1f4af7e368` | 2026-11-09 | [MIT core; review any separately licensed additions](https://github.com/promptfoo/promptfoo/blob/b3603fab85bb331da98a8b68ca442e1f4af7e368/LICENSE) | 962 | Offline evaluation engine reviewed |
| [Langfuse](https://github.com/langfuse/langfuse) | `47a70342f1736561dfa157a654d011aac29db79d` | 2026-11-10 | [MIT core / commercial EE paths](https://github.com/langfuse/langfuse/blob/47a70342f1736561dfa157a654d011aac29db79d/LICENSE) | 1179 | Defer full self-hosted trace stack; EE exclusions |
| [Celery](https://github.com/celery/celery) | `40a3154d457f085770ee7ed85ee892b4608cfb94` | 2026-11-10 | [BSD-3-Clause](https://github.com/celery/celery/blob/40a3154d457f085770ee7ed85ee892b4608cfb94/LICENSE) | 773 | Optional later queue; task retry/rate-limit source reviewed |
| [Moodle](https://github.com/moodle/moodle) | `0580991669815767026aea115a2053e2040378af` | 2026-10-30 | [GPL-3.0-or-later](https://github.com/moodle/moodle/blob/0580991669815767026aea115a2053e2040378af/COPYING.txt) | 1 | Alternative LMS; audited default is alpha, not deployment choice |
| [FrappeLMS](https://github.com/frappe/lms) | `7f7c78b5c43698420ef5a3bc9871f29647e67e31` | 2026-11-10 | [AGPL-3.0](https://github.com/frappe/lms/blob/7f7c78b5c43698420ef5a3bc9871f29647e67e31/license.txt) | 101 | Alternative LMS; current Python 3.14 constraint |
| [Chatterbox](https://github.com/resemble-ai/chatterbox) | `ab55923c27757c90cfcc407baa57dc25a7d25217` | 2026-11-04 | [MIT code](https://github.com/resemble-ai/chatterbox/blob/ab55923c27757c90cfcc407baa57dc25a7d25217/LICENSE) | not queried | Arabic TTS source examined; upstream declares retired; reject maintained pilot default |

*Dynamic metadata snapshot 2026-11-10. Code and metadata can differ in date because open PRs/other branches advance after the pinned default commit. Repository API license labels sometimes return NOASSERTION; actual license files, not those labels, were used.

## Depth, source provenance and limitations

- **DeepTutor:** pinned default `main` at `60fb3bdf...`; source in `work/repos/DeepTutor-sparse`, application/session/auth/voice/memory/mastery/question/provider/CI/Docker files inspected. Five pure-function mastery assertions passed on Python 3.11. Full optional installation, frontend/browser, security and provider suites were not run.
- **LearnHouse:** pinned default `dev` at `7dc39bc0...`; sparse clone plus 43 exact-commit source copies. Selected copies were matched to Git blob hashes. Eleven isolated assertions covered upload/org-scope/CSRF behavior; full runtime unavailable. The tight Python 3.14.7 requirement and missing Bun/Docker in the inspected shell prevented a representative full launch without substantial setup.
- **EduStudio, pyKT, PyEdmine:** actual model/data/evaluation source reviewed, not just papers/README. No numerical training/inference tests; scientific dependencies were unavailable. EduStudio deliberately not executed due to its observed secret-exposure workflow.
- **pyKT:** original full clone stalled; filtered clone pin and selected `git show` source blobs established evidence. Incomplete checkout during inspection was not treated as a runnable installation; the original full clone completed later at the same pin, without additional runtime tests.
- **pyBKT, py-irt, FSRS:** manifests, interfaces, tests and algorithm source reviewed. Only the reviewed deterministic FSRS scheduling/serialization path ran; model fitting did not.
- **14 supporting projects:** selected source functions/controllers, runtime manifests where fetched, license files and API metadata inspected. These are shortlist audits, not full deployments, load tests or comprehensive security/maintenance reviews.

No upstream code was modified, no unknown setup/start script executed, no student data used, no deployment/paid infrastructure/model calls/messages/payments performed. Changing sparse-checkout metadata or saving separate research copies does not change upstream source. Mutable branches, star counts and README claims are not substitutes for a code pin.

Root or relevant repository AGENTS files were read when present as project context. Instructions about installation, contribution or publishing were not executed blindly and do not authorize actions beyond this mission. Supporting project guidance was inspected without contributing upstream.

## Maintenance and unresolved issues

DeepTutor's published recent release is v1.7.2 (Nov 6); LearnHouse release listings show app1.4.3 (Oct25) and CLI1.6.0 (Oct30). Active commits and automation are positive signals; no quantified bus factor, SLA, complete issue triage or live CI-success claim is made. Shallow clones do not prove historical responsiveness. See preserved [GitHub metadata](evidence/github-metadata.json).

Examples from the dated live issue/PR sample (reporter claims, not reproduced defects):

- [DeepTutor #2605](https://github.com/HKUDS/DeepTutor/pull/2605): mastery handling of a new reply after ungraded clarification; [#2606](https://github.com/HKUDS/DeepTutor/pull/2606): Anthropic tool-call ID normalization. These illustrate state/provider edge-case churn, not proven failures of the audited release.
- [LearnHouse #1240](https://github.com/learnhouse/learnhouse/issues/1240): audio model lifecycle/provider compatibility; [#1241](https://github.com/learnhouse/learnhouse/issues/1241): untranslated signup labels; [#1239](https://github.com/learnhouse/learnhouse/pull/1239): security dependency update. Scope releases around tested model/provider and RTL behavior.
- [pyKT issues](https://github.com/pykt-team/pykt-toolkit/issues): sampled training/hyperparameter/model questions; small community throughput and legacy constraints warrant a reproducible offline environment before adoption.
- [EduStudio #46](https://github.com/HFUT-LEC/EduStudio/issues/46): request for newer comparison models; maintenance recency does not make the suspicious CI revision safe.

Moodle uses its own development/security processes; GitHub issue count is particularly poor as a health proxy. A default branch that reports alpha maturity must not be presented as the stable alternative. Supporting libraries have recent pinned activity except where the recorded dates show a longer interval; none was rated healthy solely from recent commits or popularity.

## Discovery sources that are not repository audits

Cohere Transcribe Arabic and Arabic ASR/TTS papers are research/model discoveries, not cloned code audits or adopted weights. Model artifact commits, dataset/voice rights, commercial conditions and benchmark reproducibility remain adoption gates. They are explicitly not assigned invented Git SHAs. Meta WhatsApp and Paymob are service interfaces, not open-source software dependencies. Django/PostgreSQL proposed supported versions were checked through official documentation; their complete source trees were not audited in this pack.

No exhaustive search of every open-source product in every category is claimed. The shortlist favors fewer dependencies, owned learner evidence and clear exit paths. Where source/terms could not be inspected, the reports say so rather than classifying a claim as verified.

## Reproduction and evidence files

1. Fetch each listed upstream at its exact SHA into an isolated research directory; do not run repository hooks/workflows/install scripts automatically.
2. Open linked pinned source and license files. Some audits include repository-relative `file:line` locators in addition to immutable links.
3. Use [test-results.md](evidence/test-results.md) to reproduce the narrow smoke checks with supported runtimes, without installing full apps or using vendor keys.
4. Inspect [dependency-check.json](evidence/dependency-check.json): eight exact public manifest-version OSV queries only, not transitive assurance.
5. Recompute [cost-scenarios.json](evidence/cost-scenarios.json) from the explicit formulas in report09; model quality, prices, region and use must be revalidated before build.

The research scope deliberately separates **implemented**, **tested narrowly**, **unverified production suitability**, and **custom product requirements**. No feature is certified production-ready for Egyptian minors solely by this audit.

Final download status: original full DeepTutor/LearnHouse clones ended with HTTP/2 EOF errors; their successful pinned sparse replacements provide the audited trees. LearnHouse sparse source materialized later in the run; the 43 selected inspected files remain verified independently. The full pyKT download completed after its selected-source inspection. These network limitations did not change the source pins or passing narrow checks.

Additional TTS audit: [Chatterbox source review](evidence/chatterbox-source-audit.md) records Arabic interfaces, retired maintenance status and the separate model repository candidate HEAD `5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18`. Model weights were not downloaded; model-card MIT metadata is not treated as a complete weight/training/speaker-rights clearance. Its GitHub issue count was not queried; retirement is source-observed at the pinned README.
