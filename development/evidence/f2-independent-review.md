# F2 independent review — 2026-11-15

Reviewer: independent_reviewer. Scope: static security evidence validator, PostgreSQL gate runner, scanner acquisition/core supplement, workflow ordering and bounded proposed image remediation. This is an independent review of code and retained scan evidence, not a phase approval or security certification. No database/container was started by this reviewer.

## Measured checks

`python3 -m unittest discover -s tools/tests -p test_security_reports.py` — **46 tests passed**, independently replayed 15 November. These are explicitly synthetic policy fixtures; they do not prove that the actual image/native advisories are resolved. An earlier fresh replay on 14 November ran 42 tests with 22 failures after provider-policy tightening; baseline fixtures lacked the required image OS provider. The current suite corrects that mismatch and tests provider rejection. Do not describe the earlier replay as passing.

Read: tools/security/check_reports.py, tools/run_postgres_smoke.py, tools/security/bootstrap.py, tools/security/native_chain.py, tools/security/postgres_core.py, tools/tests/test_security_reports.py, .github/workflows/skeleton.yml and development/F2-REMEDIATION.md. Prior static native provenance and actual CI scan inspection are documented separately in f2-native-research.md and the retained raw scan directories. No new hosted CI success or PostgreSQL migration result is asserted here.

## Findings corrected

The earlier validator treated absent `matches` as an empty clean scan and accepted arbitrary truthy database metadata. A reviewer-created synthetic in-memory reproduction returned a pass before correction; it was not scanner output. Current code requires explicit match arrays, pinned scanner/schema identities, nested valid/fresh database status and provider coverage, and rejects applied ignored matches. Optional omitted `ignoredMatches` remains valid, matching the actual Grype schema.

Image source metadata now binds the exact platform manifest, architecture and selected index. Native source/distro/package identities and on-disk library/notice hashes are checked. Scan receipts bind input SBOM bytes, output reports, scanner bytes, command and time bounds. Missing/stale evidence and unexpected severity labels fail closed. High/Critical/Unknown and KEV findings cannot be overridden by a finding-review row. Other findings require explicit component/version reviews.

The runner replays the validator and verifies complete input/policy bindings before allocating credentials, invoking Docker or contacting PostgreSQL. It uses a Linux-only pure-Psycopg/system-libpq scope, private atomic credential file creation, loopback port publication, nonroot/read-only container restrictions and task-owned teardown. Workflow scans and the policy check precede database execution; failed checks prevent later integration steps.

## Remaining holds and conditions

Actual original Debian scan contained 221 High/Critical matches. The subsequent official PostgreSQL17.12 Alpine candidate contained 35 High/Critical matches in Go1.24.6 embedded in `/usr/local/bin/gosu`. Neither candidate is cleared by nonroot startup plans. Native scan findings also remain subject to patching and exact applicability review; six fixable libc6 findings require the authenticated Ubuntu candidate transaction and a fresh installed-chain scan. Metadata/dry-run output alone is not an installed fix.

The supplier-core CPE supplement is supplier-declared coverage, not a measurement of engine bytes. CVE-2017-8806 concerns Debian postgresql-common helper scripts; an applicability decision needs exact primary-source/component evidence, retained with the finding. It does not clear image/native blockers.

Before any integration start, tighten loader-environment handling: native inventory rejects LD_PRELOAD/LD_AUDIT, but the runner inherits its environment and currently does not reject LD_LIBRARY_PATH or replay those exclusions. Either reject loader overrides at both inventory and use, or prove the actual loaded libpq/closure equals the reviewed bytes in the same process environment. This is an integrity requirement before a future passing gate, not evidence that the present controlled CI has loaded a different library.

## Proposed derived image assessment — conditional only

A local test-only derived image can remove the vulnerable executable from the effective root filesystem rather than suppress its findings: FROM the exact reviewed17.12 Alpine platform digest; COPY an authored executable stub over gosu that always exits126 with a clear unsupported-root-startup message; USER postgres; no RUN instruction, base execution or added dependency. This is a defensible bounded remediation proposal, pending actual implementation/review/scan.

Required evidence: reviewed Dockerfile/stub hashes and executable mode; exact base and derived platform/config digests; build-tool/version and source provenance; preserved base/component licenses/notices; retained original scan findings; actual merged derived filesystem inspection proving gosu resolves to the stub and no equivalent vulnerable Go payload remains elsewhere; fresh derived image/native/core scans under unchanged policy; gate and runner bound to the derived digest instead of the official-only reference contract; and actual nonroot entrypoint/integration checks only after pre-use pass. The current checker hardcodes the official image reference format, so supporting derived identity requires an explicit reviewed contract change and regression tests, not substituting a different reference after approval.

OCI replacement layers retain earlier bytes in lower layers. Describe this as replacement in the effective runtime filesystem; do not claim all archive bytes were removed or distribution/license obligations disappeared. If full archive erasure is required, a separately reviewed flatten/reconstruction process is needed. No broad new build chain or release clearance is approved by this recommendation.

**Disposition: F2 remains held.** The 46 policy tests pass; actual native/image remediation, fresh real scan receipts, remaining finding reviews, real PostgreSQL migration/readiness/cleanup and final integration evidence are outstanding. No F3, paid-provider, real-child-data, deployment or legal/commercial gate is approved.

## 15 November focused addendum — loader and local authentication hardening

Independently read the subsequent changes to native_chain.py, run_postgres_smoke.py, backend/config/environment.py and the associated fixture/boundary tests. The previously reported loader-environment gap is corrected: both inventory and pre-use replay reject nonempty LD_LIBRARY_PATH, LD_PRELOAD, LD_AUDIT and any DYLD_ override before evidence/native I/O. Empty values are permitted; error text does not echo the supplied value. Dedicated tests mock the downstream I/O boundary and verify it is never reached for hostile settings. Policy fixtures now establish an explicitly clean environment; hostile-environment behavior remains separately tested rather than silently removed from coverage.

Local loopback PostgreSQL options explicitly disable GSS encryption negotiation and require SCRAM-SHA-256 authentication. Production retains verify-full TLS. This narrows local negotiation; it does not remove installed native components or waive their vulnerability reviews. Real server compatibility/authentication remains an outstanding post-gate integration check.

Fresh independent commands:

- `python3 -m unittest discover -s tools/tests -p test_native_environment.py` — 8 passed.
- `python3 -m unittest discover -s tools/tests -p test_security_reports.py` — 46 passed.
- `SEBAVERSE_ENV=local DJANGO_DEBUG=1 backend/.venv/bin/python -m pytest backend/tests -q -k 'not postgres_integration'` — 83 passed, 1 deselected.

No additional blocker found in these bounded changes. These are unit/DB-free checks; no container, database, scanner or paid provider was invoked by this addendum. Existing actual image/native holds and F2 disposition remain unchanged. This addendum grants no phase approval.
