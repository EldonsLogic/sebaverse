# Native operational decisions for bounded F2 CI —15 November2026

DEV-006; R054/R075/R078/R094/R097/R098. Root dependency-review decisions adopt per-ID proposals from f2-native-dispositions.md for the exact66 retained matches/27CVE IDs. The raw matches remain visible. Six patched libc6 advisories are absent; the remaining libraries are not declared globally fixed or harmless. No founder product gate, real-data, release or production approval is granted.

## New evidence and decisions

Actual Linux run43726715397 inspected106 ELF objects with retained raw readelf output. Only libkrb5.so.3.3 imports regcomp/regexec; no wide-scanf import was found. Seven objects have dynamic-lookup flags; available Python extension dependencies and internal calls are not a complete process call graph. Independent review narrowed the two previously held libc findings to conditional operational residual-risk acceptance under the restricted workload. Fixed regex inputs can still encounter allocation failure; memory limits are not a vulnerability fix. Wide-scanf symbol absence is supporting evidence rather than a proof of universal non-reachability.

Root accepts the residual crash/memory-safety risk only for the isolated, short-lived, authored synthetic CI test with no sensitive data or untrusted payloads. Every per-ID rationale retains its publisher status, trigger/component distinction and uncertainty. KDC/kadmind/GSS-RPC routines are not service roles of the SCRAM client; LDAP/SASL/GnuTLS certificate paths are excluded by exact invocation and empty service/plugin configuration. OpenSSL source-version exclusions are supporting publisher evidence; operational decisions rely on the absent QUIC/CMS/AES-GCM-SIV/certificate workload rather than claiming Ubuntu adjudicated every source backport.

## Deterministic boundaries

Scoped review rows require the replayed derived authority, exact archive/parent/COPY proof, no initdb inputs or Debian helper wrappers, live native/notice hashes, and actual static-symbol evidence. Each row expires within six days and binds the complete authored backend source/test set, locked Python manifests and runner bytes. Added or changed source/locks requires fresh review. New High/Critical/Unknown, KEV or unmatched findings still block; no report suppression is introduced.

The runner is CI-only, imports and inspects the exact scanned config/rootfs identity, uses no mutable tag/pull, verifies a task-owned internal network before startup, constrains resource use, passes a clean generated client environment and runs only the fixed synthetic migration/session/readiness test. Explicit SCRAM/noGSS/noTLS configuration is checked by the integration test; actual negotiation and migration results are still pending. Failing those conditions prevents phase closure.

The measured symbol report, raw text and inspected binary hashes are bound and re-parsed by the pre-use gate; changed importer coverage invalidates these scoped decisions. This is evidence-based bounded test risk acceptance. Broader data/model/upload/student use requires its own gates and reviews.

## Independent pre-run adoption review

2026-11-15, independent_reviewer. Confirmed70 retained review rows:66 native matches covering27 unique IDs plus4 image/core matches. Inspected adoption rationales against the earlier per-ID register and the focused two-libc reconsideration. They adopt bounded workload risk, preserve publisher uncertainty and distinguish role/component exclusion from source-version proof. OpenSSL decisions explicitly fall back to excluded workload rather than asserting unverified distribution backport status. This is a defensible operational distinction for the fixed disposable synthetic test, not blanket security clearance. No severity/KEV threshold reduction was identified.

Independently ran scoped-review tests3 passed and symbol-gate tests4 passed. Scoped validator now rejects absent derived authority, incorrect scope, stale/overlong review and changed workload file set/hashes, correcting the prior official-fallback gap.

One concrete evidence-integrity issue remains at this snapshot: symbol replay requires native libraries and the Python executable but does not compare the full available-extension/libpython object set with fresh discovery. Pruning those report rows can preserve a pass while weakening the106-object basis cited by the libc decisions. Root was asked to require the reviewed collector's expected object set or an exact bound equivalent plus a pruning regression. This is a requirement to preserve the measured evidence boundary, not a demand for whole-process proof. Final actual pre-use result and real negotiation/migrations remain pending; no database/phase approval is granted here.

### Focused correction verification

Independent targeted replay:5 symbol-gate tests and3 scoped-review tests passed. Shared offline discovery now reconstructs the reviewed native closure, backend Python executable/base, libpython and all available stdlib/venv extension .so paths; validates no system-site packages and expected venv home; gate requires exact equality with recorded object paths and rechecks every binary/raw-symbol hash. A dedicated pruning regression covers the reported gap. The earlier symbol-report pruning blocker is corrected for this defined discovery boundary; transitive/dynamic/internal-call limits remain as previously recorded. No new concrete blocker found in these two bounded corrections. Actual fresh Linux gate and database integration remain required.
