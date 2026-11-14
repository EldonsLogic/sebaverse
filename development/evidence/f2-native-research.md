# F2 native research — 12 November 2026

Actual independent reviewer: /root/independent_reviewer. Scope: static supplier/source/API and installed macOS arm64 wheel inspection. No upstream script, DB connection or application service executed. This is identification/provenance evidence, not a CVE pass or F2 gate approval.

## Identified native components

| Component | Version | Installed static corroboration |
|---|---|---|
| libpq | 18.6 | PQlibVersion disassembly returns integer 180006; supplier release workflow also sets 18.6 |
| OpenSSL | 3.5.8 | libcrypto contains OpenSSL 3.5.8 version string; supplier workflow sets 3.5.8 |
| MIT Kerberos | 1.22.2 | libkrb5 brand string and source paths across the five Kerberos/com_err dylibs |
| OpenLDAP | 2.6.14 | Source build paths in both libldap and liblber; pinned supplier build script |

Exact wheel/native hashes, immutable upstream commits, blob/file hashes, source notices, linkage and evidence snippets are in [native provenance](../../third-party/f2-psycopg-native-provenance.json).

## Source and license observations

Psycopg tag 3.3.8 resolves to b9e2f3535777cffb679ce3e6dc7f2b758dc9ac06. GitHub reports its annotated tag signature valid; independent cryptographic verification was not performed. The exact build/cache and wheel workflows plus build_libpq.sh were read, never run. Source references resolve to immutable supplier commits. PostgreSQL COPYRIGHT, OpenSSL Apache-2.0 license, OpenLDAP Public License2.8 and the composite Kerberos NOTICE were inspected and hashed. The wheel ships its LGPL package notice. This does not establish complete native redistribution attribution or legal clearance.

PyPI integrity endpoint for the exact wheel returned404; no artifact-to-build attestation was established. Source configuration plus matching static binary strings is corroboration, not a reproducible-build proof. Two initial shell metadata queries failed because unquoted question marks were treated as zsh globs; corrected quoted/subprocess API requests succeeded. No build/install operation resulted from those failed reads.

## Blocking distinctions for the native pre-use gate

- Root must obtain actual scanner/advisory findings and identification coverage; this research supplies component identities only.
- Darwin observations cannot label Linux native components. The pinned build script builds Kerberos1.22.2 only for macOS; Linux wheels can bundle system-sourced Kerberos/other distro libraries. Scan the actual Linux wheel installed in CI before its DB connection.
- Cache keys include libpq/OpenSSL/PQ_FLAGS but not Kerberos/LDAP; source variables without binary corroboration are insufficient for an exact native inventory.
- Apple host-library dependencies are identified as external and are not certified by wheel/package scans.
- Keep unresolved version, coverage, notice or relevant vulnerability findings visible. Do not call an unidentified native package clean, or waive the mandatory F2 native/image pre-use condition.
