# DEV-009 runtime recovery decision

18 November 2026. Status: prepared options, not an approved runtime switch or advisory waiver. DEV-009 code passed independent review and 335 database-free tests; actual PostgreSQL resilience acceptance is held.

## Observed evidence

[Hosted skeleton run 44290189983](https://github.com/EldonsLogic/sebaverse/actions/runs/44290189983) failed at the unchanged pre-use gate before database execution. It reported eight High image matches (four CVEs across libcrypto3 and libssl3), two additional Medium image matches and one new Medium native match. New image versions are both 3.5.9-r0; the native match is libsasl2-2 2.1.28+dfsg1-5ubuntu3.1, CVE-2026-129483. No new finding was cleared or suppressed.

High IDs: CVE-2026-95692, CVE-2026-107496, CVE-2026-95691 and CVE-2026-88823. Medium image ID: CVE-2026-88822. [OpenSSL's release-specific advisory register](https://www.openssl-library.org/news/vulnerabilities-3.5/index.html) lists 3.5.10 as a fixed version for these issues. The publisher rates these issues Low while the captured scanner/NVD matches are High/Medium; that disagreement does not authorize overriding the project's scanner threshold or prove non-reachability.

The official Docker registry's latest 17-alpine index was read without pulling/executing an image. Its linux/amd64 manifest is still the exact pinned `sha256:005c5c37db96c1e6652a79ea31f9886402fba81ac95dc2db897739121dd7f8f2` (PostgreSQL 17.12). Refreshing the tag would not update this platform's files.

The official Alpine v3.24/main/x86_64 APKINDEX was then inspected as bounded data, without installing or running packages. Both libssl3 and libcrypto3 still resolve to 3.5.9-r0, Apache-2.0 declared license. Thus neither a tag refresh nor a compatible official package upgrade currently repairs the identified runtime. An upstream source release is not a reviewed drop-in Alpine package.

## Concrete safe choices

1. **Recommended: bounded assessment of an alternative official PostgreSQL 17 runtime.** Retain PostgreSQL 17, Django and the product architecture. Assess at most two immutable official image candidates (including a maintained Debian variant) for current OpenSSL/package status, notices, compatibility and the unchanged severity/KEV gate. Do not build OpenSSL from source or add another custom native patch. Prepare exact image pin/runtime recipe changes and an ADR amendment only if a candidate qualifies; independently review the source/artifact scope before database execution, then rerun migrations, all access/resilience probes and browser checks. If neither candidate qualifies, stop with evidence. Effort is greater than waiting and successful qualification is not guaranteed; this extends the current task's exhausted bounded repair assessment.
2. **Wait for a compatible official Alpine fix.** Keep the current runtime unchanged, DEV-009 in review and DEV-010 held. Resume after an immutable image/package update containing the vendor fix is available and passes the existing gate. The release date is unknown.

Neither choice waives High findings. AUTH-005 covers exact reviewed temporary synthetic-only exceptions and does not authorize these new High findings or a relaxed pre-use policy. The project quality-bar budget requires a founder decision before another runtime approach; no third unbounded native-remediation attempt is started here.

## Evidence retention

Failed full run: 44290189983 at 8b8bfda. [Dependency readiness 44290190074](https://github.com/EldonsLogic/sebaverse/actions/runs/44290190074) and [foundation 44290189893](https://github.com/EldonsLogic/sebaverse/actions/runs/44290189893) passed. Canonical scanner logs and f2-evidence remain in the hosted run. Downloaded evidence and metadata stay under ignored work/dev-009/failed-evidence and patch-assessment.

current-index.json SHA-256: `a77aa70e641402a21411b92b721c58d10f23b50ae5fdd2333efd22d166e1e5f7`.

alpine-packages.json SHA-256: `a34a89b2eb9a50192194ac561193b19e0f4ad72a49ea969cbf50349f6ba225ca`.

image-cves.json SHA-256: `8993bf746c5ab5ee5472eedf729f49a356c340b5b771742134bb36af205502da`.

## AUTH-006 assessment started

18 November 2026: founder selected option 1. Threat is the existing runtime's newly reported OpenSSL findings; no learner or production service is present. Budget: two official PostgreSQL 17 candidates, 17-bookworm and 17-trixie, static inspection first; no source build, custom native patch or threshold change. Existing checksum-pinned Syft/Grype tools will inspect immutable registry content without running images. Candidate qualification is not presumed.


## AUTH-006 result

The two authorized official candidates were statically cataloged/scanned in hosted run 44294630688. Neither qualifies: Bookworm has 9 Critical, 153 High and 24 unknown-severity matches; Trixie has 4 Critical, 166 High and 24 unknown-severity matches. These are matches, not unique vulnerabilities or exploits. No runtime pin or threshold changed and no database ran. See [bounded assessment](runtime-candidate-assessment.md) for exact hashes and continuity. The assessment budget is exhausted; no third candidate is started.
