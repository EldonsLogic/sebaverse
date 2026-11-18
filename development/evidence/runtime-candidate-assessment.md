# AUTH-006-ASSESS-001 — Official PostgreSQL 17 candidate assessment

18 November 2026. Result: neither of the two authorized candidates qualifies; no runtime switch or database execution. Founder authorization: AUTH-006. Scope: static inspection only, unchanged severity and real-data restrictions.

## Actual execution and identity

[Hosted assessment run 44294630688](https://github.com/EldonsLogic/sebaverse/actions/runs/44294630688) completed both static scans successfully at 679adec. Workflow success means the assessment ran, not that either image passed the product/runtime gate. Existing checksum-pinned Syft 1.57.1 and Grype 0.121.3 were used with an explicit empty ignore policy. Each SBOM's linux/amd64 manifest and config digest matched the separately verified registry metadata. No image was built or executed, no host/runtime package was installed and no database was started.

The first local registry downloads/advisory update stalled. Only the three verified task-owned scanner processes were stopped. The same two candidates were retried on hosted CI; no third candidate was assessed. Local transport failure is not a vulnerability result.

## Scan results

Counts are package/advisory matches, not unique vulnerabilities or demonstrated exploits. No severity was downgraded based on reachability assumptions.

| Official candidate | Packages | Total matches | Critical | High | Unknown severity | Result |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 17-bookworm | 159 | 580 | 9 | 153 | 24 | Not qualified |
| 17-trixie | 149 | 515 | 4 | 166 | 24 | Not qualified |

Bookworm contains libssl3/OpenSSL 3.0.22-1~deb12u2; Trixie contains libssl3t64/OpenSSL 3.5.7-1~deb13u3. Blocking matches also occur in native libc/libxml/Kerberos and other packages; replacing the Go-based gosu helper alone would not clear either candidate. No broad per-symbol applicability review, source build, custom native patch or compatibility change was attempted. High/Critical/unknown matches are sufficient to withhold qualification; the remaining rights/compatibility/KEV review would still be required for any future candidate even if these blockers disappeared.

## Decision and continuity

Keep the existing runtime pin unchanged and DEV-009 in review; its 14-scenario actual PostgreSQL probe has not run. DEV-010/F3 exit and DEV-013 AG-UI product activation remain held by their dependencies. Existing DEV-009 code review and database-free results are retained. No scanner findings were suppressed, no High waiver was inferred from AUTH-005/006, and no third candidate is started under this exhausted assessment budget.

The current bounded assessment is complete. A future official patched artifact, or a separately authorized concrete runtime-remediation approach, is needed before resuming product database execution. No patch-release date or new runtime suitability is invented.

## Artifact identity

Raw SBOM/advisory evidence remains in hosted artifacts and ignored work/dev-009/runtime-assessment/hosted. The compact machine-readable assessment is [runtime-candidate-assessment.json](runtime-candidate-assessment.json); it contains exact immutable references, counts and hashes. Downloading/copying raw scanner dumps into Git is unnecessary.

Independent result review: /root/independent_reviewer verified raw counts, report/SBOM hashes, linux/amd64 manifest/config identities and non-Go blockers, and returned PASS for the assessment checkpoint with neither image qualified. No execution or further candidate was approved. [Prepared next decision](runtime-next-decision.md) separates an explicit new synthetic-only policy review from waiting for a compatible official patch; neither is authorized here.
