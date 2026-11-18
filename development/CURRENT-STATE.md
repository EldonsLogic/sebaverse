# Current development checkpoint

18 November 2026. Canonical private repository: https://github.com/EldonsLogic/sebaverse. Verify actual Git HEAD and remote before trusting a named commit.

**F0–F2 passed. F3 is in progress; F4–F8 have not started. DEV-001–008 are done. DEV-009 is in review, held before actual database resilience execution by the runtime gate; DEV-010 and DEV-013 activation cannot start.**

DEV-009 at 8b8bfda passed independent code review, 25 resilience/335 database-free backend tests, dependency run 44290190074 and foundation 44290189893. Full run 44290189983 failed before database use on new image advisories; the 14-scenario actual PostgreSQL probe remains not run. Existing DEV-008 actual access tests passed earlier at b9da886. See [evidence/dev-009.md](evidence/dev-009.md).

AUTH-006 assessed exactly two alternative official PostgreSQL 17 images in static hosted run 44294630688 at 679adec. Neither qualifies: Bookworm has 9 Critical/153 High/24 unknown-severity matches; Trixie 4/166/24. Native blockers remain beyond Go tooling. No image/database ran and no runtime pin or threshold changed. The authorized assessment budget is complete; AUTH-007 now authorizes an exact OpenSSL synthetic-CI review; independent review and 163 helper tests passed, the exact exception is activated, and actual hosted execution is pending. Evidence: [runtime assessment](evidence/runtime-candidate-assessment.md).

U19 requires AG-UI integration via R105/ADR-013 and DEV-013 after its prerequisites/F3 exit. [Integration contract](../architecture/ag-ui-integration.md) and pinned SDK observations are documented; independent planning review passed. No SDK is installed and no AG-UI product code/activation is claimed. Minimal protocol adapter retains Django/React, validated content, server authority, live scope and durable replay/cancellation.

The visible local app is still the Arabic-first shell; no signup UI, upload, tutoring, grading or real model call exists. Its preview is http://127.0.0.1:8030 while the task-owned process is running. F3 exit tests remain not_run. AUTH-005's exact npm exception expires 20 November at 19:38:23 UTC; native reviews retain 21 November expiry and unresolved findings. Local macOS database use remains held. No paid calls, deployment, exposed service, copyrighted textbook ingestion or real-minor use is authorized.

AUTH-007 evidence: development/evidence/auth-007-openssl-review.md. Only the named eight High OpenSSL package matches can use the expiring exception; standard/production, Critical/unknown/KEV and all new/unreviewed findings still block. DEV-009 stays in review until the actual 14-scenario run passes.
