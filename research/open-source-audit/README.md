# Open-source architecture audit

10 November 2026. Start with [the executive brief](13-executive-brief.md).

The pack contains 13 requested reports, 22 commit-pinned repositories, immutable code references, narrow smoke-test evidence, a limited dependency query and a reproducible cost model. The original requested location is `research/open-source-audit/`; an identical delivery copy is in `outputs/research/open-source-audit/`.

1. [Repository inventory](01-repository-inventory.md)
2. [DeepTutor audit](02-deeptutor-audit.md)
3. [LearnHouse audit](03-learnhouse-audit.md)
4. [Adaptive learning libraries](04-adaptive-learning-libraries.md)
5. [Additional components](05-additional-open-source-components.md)
6. [Compatibility matrix](06-compatibility-matrix.md)
7. [Architecture options](07-integration-architecture-options.md)
8. [Security and licensing](08-security-and-licensing.md)
9. [Infrastructure and economics](09-ai-infrastructure-and-economics.md)
10. [Build versus reuse](10-build-vs-reuse-matrix.md)
11. [PoC plan — not implemented](11-integration-proof-of-concept-plan.md)
12. [Recommended foundation](12-recommended-technical-foundation.md)
13. [Executive brief](13-executive-brief.md)

Recommendation: an owned modular monolith; neither primary product wholesale. DeepTutor is a reference/selective extraction candidate; LearnHouse is an LMS fallback subject to AGPL/EE terms. Current EduStudio pin is quarantined for an observed CI secret-exposure mechanism; no token/package compromise is asserted.

Limits: no full application deployments, model training, paid calls, student data or security certification. Passing smoke checks and empty limited OSV query results must not be read as production clearance. See evidence/ for scope and results.
