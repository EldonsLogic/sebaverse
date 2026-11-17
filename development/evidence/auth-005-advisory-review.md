# AUTH-005 restricted development advisory review

17 November 2026. Status: independently reviewed and adopted for the exact restricted scope. This records residual-risk assessment, not a patch or general clearance. Founder authority is AUTH-005. Maximum exception lifetime is three days for npm; new native rows retain the earlier 21 November expiry.

The npm regex implementation executes in Vite build tooling. Exact source/config/lock bytes are bound, including all authored web source, and new/changed findings fail. No user text or uploads are present in this workload. The production scope always rejects advisory exceptions. The unsuppressed raw audit and policy receipt are retained. No claim is made that picomatch is safe in general or that all Vite paths have been proved unreachable. Existing dependency artifacts and licenses are unchanged.

The native workload remains the prior fixed synthetic SCRAM test on an internal task-owned network: no TLS/GSS authentication, no real credentials, no user SQL, KDC, kadmind or remote Kerberos service. Three descriptions below remain unknown at the publisher. Those are explicitly residual uncertainty, not a non-reachability determination. Medium availability/integrity risk is accepted only inside the disposable synthetic process boundary; production and real-data use remain held. No known-exploited or High/Critical/unknown-severity finding is exempted by these rows. The existing native checker still rejects those categories and requires every finding to be reviewed.

## Per-advisory publisher evidence

- [CVE-2026-107364](https://ubuntu.com/security/CVE-2026-107364): publisher description: [Unknown description]. Noble status is Needs evaluation. Retrieved page SHA-256: `d313dab1a63634c9cd32812762dd50fbb4579a32eeb55552f4f4b052fd512c45`.
- [CVE-2026-107884](https://ubuntu.com/security/CVE-2026-107884): publisher description: [Check for the lockdown_keys attribute when processing password change
protocol requests in kadmind]. Noble status is Needs evaluation. Retrieved page SHA-256: `5dd41563ac78b7275ca02ff81a7cd0dfb1f829d4845c5ce26b9e336320f8ff59`.
- [CVE-2026-111423](https://ubuntu.com/security/CVE-2026-111423): publisher description: [Fix a logic error when checking PAC server checksums]. Noble status is Needs evaluation. Retrieved page SHA-256: `29e1d197102896e51f7021260be0479b2d796c0b584da2a704bb5580e6bf82fb`.
- [CVE-2026-118380](https://ubuntu.com/security/CVE-2026-118380): publisher description: [Unknown description]. Noble status is Needs evaluation. Retrieved page SHA-256: `f5ee2d7a1af7f942eb17c179e26faa9471c328a55a6ca02cf513a5e9e198f747`.
- [CVE-2026-71199](https://ubuntu.com/security/CVE-2026-71199): publisher description: [Check for unkeyed checksums when validating CAMMAC verifiers]. Noble status is Needs evaluation. Retrieved page SHA-256: `333635b01afed081b0e260cf6ea1e1fde6e8877c998643aa9470220ba19fc5c5`.
- [CVE-2026-71200](https://ubuntu.com/security/CVE-2026-71200): publisher description: [Unknown description]. Noble status is Needs evaluation. Retrieved page SHA-256: `d3e9eb5912c9161064b454df3ce22c80190a5617e455a2c74c4fe50ce8f4c066`.

## Tests and activation

Ten negative/positive npm boundary tests cover production refusal, expiry/future dates, changed advisory/severity/versions, new findings, changed source, audit errors, incomplete reports and clean audits. Existing native negative fixtures remain required. Independent reviewer /root/independent_reviewer approved activation after correction 1: the checker enforces the three-day maximum and a negative overlong-duration test passes. All bound source hashes matched on independent verification; 10 tests passed. The exact npm policy and 24 native per-match rows were then adopted. This document does not approve F3 or restore dependency readiness without an actual passing hosted run.

## Actual local result

`python3 tools/check_npm_audit.py --scope synthetic-development` completed an actual registry audit and returned `pass_with_temporary_development_exception`, four propagated entries, expiry 20 November 2026 at 19:38:23 UTC. Raw report SHA-256: `1e47b8bdacc240f3960e2221855882325a550a172a7084ad00d662096ac6d313`. No advisory was removed from the report. Foundation checks passed with 152 helper/negative-fixture tests, economics and artifact validation; backend checks passed 116 tests, one database integration case deselected. Full hosted pre-use/database/browser checks remain pending until this commit is pushed.


## Hosted result — verified

All three workflows passed against `c38bb04c717d4e61a9ea4e9ea6188d15334ca4f1`: [dependency readiness 44161448859](https://github.com/EldonsLogic/sebaverse/actions/runs/44161448859), [foundation 44161448845](https://github.com/EldonsLogic/sebaverse/actions/runs/44161448845), and [full skeleton 44161448815](https://github.com/EldonsLogic/sebaverse/actions/runs/44161448815). The full skeleton's actual step results include native/image pre-use policy, real PostgreSQL migration/readiness/teardown, desktop/mobile browser checks and final regressions, all successful. This restores DEV-007 integration readiness only; F3 remains in progress with its four full exit suites not yet passed. The advisories remain unresolved, and temporary dispositions still expire.

Hosted run metadata SHA-256: `44ea0ea9034dd7c59ec71aff6bf23bb19c2a191d17a78ec08f0415f7f96dbf37`. Canonical metadata/logs/artifacts remain in the linked run.
