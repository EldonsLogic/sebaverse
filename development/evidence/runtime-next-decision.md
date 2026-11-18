# Runtime policy decision after AUTH-006

18 November 2026. Proposal only. Neither of the two authorized alternative images qualifies. No third image, runtime execution or policy change is authorized by this document.

## Option A — Review one exact synthetic-only exception in the original runtime

Authorize one bounded independent applicability/residual-risk review for the four newly blocking OpenSSL CVEs in the existing derived Alpine image: CVE-2026-95692, CVE-2026-107496, CVE-2026-95691 and CVE-2026-88823, libcrypto3/libssl3 3.5.9-r0. Review the additional new Medium image/native findings separately. Budget: one review and at most two correction cycles, no more image hunting, source builds or custom native patches. No execution before a concrete review verdict and passing scoped tests.

The [OpenSSL publisher](https://www.openssl-library.org/news/vulnerabilities-3.5/index.html) describes conditional AES-GCM-SIV, CMS and QUIC issues and lists fixed 3.5.10. The current synthetic workload is fixed SCRAM SQL over a task-owned internal network, without TLS/GSS, untrusted certificates, user prompts/files, real credentials or production data. That suggests a bounded applicability review may be useful; it does not establish non-reachability or clearance by itself. Package-wide High matches remain facts in unsuppressed reports.

If and only if the independent evidence supports it, permit an exact expiring development-only exception for these IDs/package versions/artifact/source and fixed workload. This explicitly changes the current blanket High-image blocker for the reviewed entries; it cannot be inferred from AUTH-005/006 or “best practice.” Critical, unknown-severity and known-exploited findings remain blocked, all unreviewed/new/changed findings fail, raw evidence remains visible, expiry/source/artifact drift invalidates acceptance, and real-data/exposed-service/production/deployment use remains prohibited. Unapproved reviewed entries still block; authorizing review is not unconditional clearance.

Before activation, negative tests must prove production refusal, expiry, source/artifact/version drift, changed IDs/severity/KEV, TLS/GSS/workload changes, and that an arbitrary High cannot inherit this exception. The actual PostgreSQL access/resilience/migration/browser suite must then pass before DEV-009 completion or F3 advancement. Remove the exception when a qualified official patch is available. If the bounded review cannot support the scope, keep execution held.

## Option B — Keep the current blanket threshold and wait

Keep every existing High-image blocker unchanged, DEV-009 in review and later product implementation held. Resume when a compatible official patched artifact passes the unchanged gate, with fresh rights/source/advisory evidence. Availability date is unknown. AG-UI's approved integration contract and prerequisite checks remain in the roadmap, but activation cannot bypass F3.

Engineering recommendation: option A is a bounded review proposal aligned with the project's synthetic-stage proportionality goal; it still requires an explicit founder decision because AUTH-006 preserved all thresholds. No change or waiver has been made.
