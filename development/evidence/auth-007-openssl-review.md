# AUTH-007 exact OpenSSL exception review

18 November 2026. Status: exact scope independently reviewed and activated; actual hosted execution remains pending. Budget: one review and at most two correction cycles. Threat: conditional OpenSSL flaws in a fixed disposable synthetic database workload; no real learner data, service exposure or production use is present. No new image, library/source build, custom native patch or SDK is introduced.

## Applicability and retained uncertainty

The OpenSSL 3.5 publisher register lists fixed 3.5.10 for the four newly blocking IDs. CVE-2026-95692 concerns invalid caller-supplied AES-GCM-SIV nonce lengths; CVE-2026-88823 concerns fragmented AES-GCM-SIV authenticated data; CVE-2026-95691 concerns QUIC client packet lifetime; CVE-2026-107496 concerns CMS encryption with an attacker-supplied EC certificate. Source: https://www.openssl-library.org/news/vulnerabilities-3.5/index.html (observed 18 November). Publisher severity differs from captured Grype/NVD severity; no scan severity is rewritten.

The pinned workload uses fixed synthetic SCRAM SQL on a verified task-owned internal bridge, an owned loopback relay, no user prompts/files/certificates, no TLS/GSS, no real secrets and no external provider. Existing actual PostgreSQL tests assert non-TLS/non-GSS negotiation, and clean environment checks bind service/Kerberos/LDAP/OpenSSL configuration. The derived recipe only replaces gosu with the existing fail-closed stub and runs nonroot; it cannot introduce a crypto replacement. The intended tests do not request QUIC, CMS or AES-GCM-SIV operations. This is a scoped applicability inference supported by source/controls, not a proof about all installed code or arbitrary workloads.

Package-wide findings remain unresolved. Review and negative tests must bind the exact original parent, recipe/runtime controls, complete backend/test/runner source and package/CVE/severity pairs. An explicit synthetic-CI scope and actual CI context are required; standard/production paths cannot inherit the exception. Critical/unknown severity and KEV blocks are unchanged. Any unsupported inference, drift or expired review must fail closed. Real data and production require patched artifacts and separate readiness.

## Additional Medium findings and source disagreement

CVE-2026-88822 (libcrypto3/libssl3 3.5.9-r0) concerns QUIC automated peer detection. The same no-QUIC workload rationale applies; no severity exception is needed for its captured Medium classification, but exact reviewed rows are still mandatory.

CVE-2026-129483 (libsasl2-2 2.1.28+dfsg1-5ubuntu3.1) concerns the Cyrus SASL SRP **server** mechanism accepting invalid public values. Ubuntu's current page reports Medium priority/Needs evaluation and a separate Critical CVSS score; the captured Ubuntu/Grype match is Medium. Both observations are retained, not recast as a fixed or universally low-risk package. The planned libpq client uses required SCRAM, not a Cyrus SRP server, with no LDAP/Kerberos/SASL server or untrusted peer outside the fixed isolated database. Applicability is a scoped inference, not a whole-package clearance. If a future scan classifies this finding High/Critical/unknown, the image-only OpenSSL exception cannot cover it. Source: https://ubuntu.com/security/CVE-2026-129483, updated/retrieved 18 November 2026.

## Proposed control and evidence scope

The standard gate remains the default. An explicit --scope synthetic-ci plus actual GitHub Actions context is required for the exception; replay by the database runner additionally requires its explicit synthetic-CI environment. The exact parent, recipe/runtime controls, workflow, backend and all authored Python tooling are hash-bound. Every raw advisory remains in the report, with explicit exception count/authority/expiry; KEV remains an independent blocking check. There is no new image, native patch or expiry extension to the earlier review rows.


## Independent adoption and actual local checks

Independent reviewer /root/independent_reviewer verified publisher descriptions and retained severity disagreement, reviewed the exact code/policy/proposed 11 finding rows, verified input bindings, independently ran 11 exception tests and all 163 helper tests, and allowed exact activation. It also allowed existing source-map rebinding for the reviewed runner replay change without extending original dates/expiry. No remaining concrete review blocker was identified.

The eight High image pairs and three additional Medium package matches were adopted only for their stated synthetic scope. The new High policy expires after two days (maximum allowed duration three days); original reviews retain their original expiry. New reviewed rows do not claim components are absent or fixed. Product/real-data/production use remains unapproved.

Local foundation/economics/artifact checks and 163 helper tests passed. The 14-scenario actual PostgreSQL probe, native gate replay and browser/regression run still must execute successfully on hosted CI before DEV-009 completion. No phase pass is inferred from policy tests.


## Actual hosted execution — passed, restricted scope only

At `bc2115581aa52d1dbaadcbc7ae4044f53618f8b5`, [full skeleton 44297534813](https://github.com/EldonsLogic/sebaverse/actions/runs/44297534813), [dependency readiness 44297534706](https://github.com/EldonsLogic/sebaverse/actions/runs/44297534706), [foundation 44297534679](https://github.com/EldonsLogic/sebaverse/actions/runs/44297534679) and [static remediation experiment 44297534686](https://github.com/EldonsLogic/sebaverse/actions/runs/44297534686) succeeded. Static experiment completion does not claim its affected packages are fixed.

The actual pre-use receipt reports pass in explicit synthetic-ci scope, AUTH-007 expiry 20 November 2026 at 11:39:06 UTC, eight exact High image exceptions, zero native/core High exceptions, and zero blocking findings after the scoped rule. Raw High findings remain in the unsuppressed scan. The PostgreSQL migration/readiness/teardown step, 14 durable-job resilience scenarios and all prior access assertions actually executed successfully, followed by browser checks and regressions.

Independent execution review /root/independent_reviewer verified the hosted head/status, raw gate/receipt hashes and image identity, teardown, frozen integration assertions and successful PostgreSQL/browser/regression steps. It returned PASS for DEV-009 acceptance and release of that task's hold only. F3 has not exited; production, real data and general package clearance remain prohibited. See [compact execution receipt](auth-007-execution.json); canonical raw evidence stays in hosted CI.
