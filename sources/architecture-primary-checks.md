# Architecture primary-source checks — 11 November 2026

These are limited readable-page checks, not new source-code/security/runtime audits. Historical A01–A13 remain unchanged. Mutable pages are dated references, not deployment locks. No dependency installed or paid provider called.

| Evidence ID | Type / observed locator | Consequence |
|---|---|---|
| E22 | OBS: [Django supported versions](https://www.djangoproject.com/download/) lists 5.2 LTS and extended support through April 2028 | Select supported LTS family, resolve patched release at install; no claim currently locked |
| E23 | OBS: [Django 5.2 async docs](https://docs.djangoproject.com/en/5.2/topics/async/) explains ASGI async support and sync/async adaptation | Use native ASGI streams, keep transactions in short sync services; do not assume DRF or entire ORM is async |
| E24 | OBS: [React from-scratch guide](https://react.dev/learn/build-a-react-app-from-scratch) documents Vite, routing and query-layer choices; [framework guidance](https://react.dev/learn/creating-a-react-app) recommends frameworks generally | Select custom client app deliberately because Django owns backend; accept explicit router/query/toolchain work |
| E25 | OBS: [Docling repository license section](https://github.com/docling-project/docling#license) states MIT code and separately licensed model packages | Parser library chosen; exact model/asset rights still required |
| E26 | OBS: [pgvector filtering guidance](https://github.com/pgvector/pgvector#filtering) documents scoped exact search and ANN filtering considerations | Start exact authorized search; ANN requires filtered-recall/security testing |
| E27 | OBS: [py-fsrs license](https://raw.githubusercontent.com/open-spaced-repetition/py-fsrs/main/LICENSE) and [API docs](https://open-spaced-repetition.github.io/py-fsrs/) | Package API comparator for recall; no result validating learning improvement |
| E28 | OBS: [Promptfoo core license](https://raw.githubusercontent.com/promptfoo/promptfoo/main/LICENSE) contains permissive notice terms; [DRF license](https://raw.githubusercontent.com/encode/django-rest-framework/main/LICENSE.md) contains redistribution/notice conditions | Exact adopted releases/features/transitive notices still checked; no blanket commercial clearance |
| E29 | OBS: [ClamAV intro](https://docs.clamav.net/) describes GPLv2 scanning toolkit and limits of its endpoint protection role | Separate scanner boundary; clean scan does not establish file safety; distribution review remains |
| E30 | OBS: [PostgreSQL version policy](https://www.postgresql.org/support/versioning/) describes five-year major support and regular minor fixes | PostgreSQL 17 selected family; patch and upgrade planning required |
| E31 | OBS: [GitHub Actions secure use](https://docs.github.com/en/actions/reference/security/secure-use) describes least privilege and third-party action risks | Plan SHA-pinned actions, unprivileged PR jobs and gated deployment credentials |
| E32 | OBS: [DeepTutor root](https://github.com/HKUDS/DeepTutor) identifies Apache-2.0 | Corroborates code-license label only; A02 pin/source audit, not current README feature claims, governs extraction review |

INF: this stack reduces duplicate domain authority and operations for a solo founder while retaining rich UI boundaries. This is engineering judgment, not a measured stack comparison. DECISION: U11 authorizes final technical selection documented in ADRs. UNK: exact lockfiles, hosting/processor eligibility, production model endpoints, retention periods, all performance/quality benchmarks.
