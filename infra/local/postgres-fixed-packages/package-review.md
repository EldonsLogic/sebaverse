# AUTH-014 Alpine OpenSSL package review

**Founder clarification, 20 November:** AUTH-014 now expressly covers only the two installed libraries, libcrypto3 and libssl3 3.5.9-r1. Keep openssl CLI absent. Earlier references below to a pending scope choice describe the completed static pass; build-tool, assembly and artifact qualification remain open under the original budget.


20 November 2026 · DEV-010 · R040/R081. **Alpine's signed index and all three exact packages verified. Static assembly is held pending the founder's clarification of the replacement scope.** The original PostgreSQL parent contains `libcrypto3` and `libssl3` at `3.5.9-r0`. The exact parent has no `openssl` package or `/usr/bin/openssl`, so including the third package would add a command. [Machine-readable receipt](package-review.json), [authorized assessment](../../../development/APPROVALS.md#auth-014--founder-exact-fixed-package-database-derivative-assessment-20-november-2026).

Threat and budget. A mistaken overlay can misstate which native code runs or add an executable to disposable synthetic CI. This focused static pass checked only the three named Alpine v3.24 x86_64 main APKs, their index, the exact parent records and the applicable source and license metadata. No APK, package hook or parent-image program ran.

## Authentication and package contents

The original parent manifest was verified at `sha256:005c5c37db96c1e6652a79ea31f9886402fba81ac95dc2db897739121dd7f8f2`. All ten layer sizes and SHA-256 digests matched the retained blobs. The first layer's existing `/etc/apk/keys/alpine-devel@lists.alpinelinux.org-6165ee59.rsa.pub` supplied the trust anchor. Host LibreSSL 3.3.6 returned `Verified OK` for the original compressed index body and each package control segment using Alpine's APK v2 RSA/SHA-1 signature scheme. The signed `.PKGINFO` SHA-256 matched each compressed payload. The signed index's `C:Q1` control identity, archive size and package metadata matched each package. [Pinned parent manifest](../../../development/evidence/f2-passed-43730557172/security/postgres-parent-manifest.json), [Alpine index](https://dl-cdn.alpinelinux.org/alpine/v3.24/main/x86_64/APKINDEX.tar.gz), [Alpine APK v2 format source](https://gitlab.alpinelinux.org/alpine/apk-tools/-/blob/master/doc/apk-v2.5.scd).

| Exact archive | SHA-256 | Payload |
|---|---|---|
| `libcrypto3-3.5.9-r1.apk` | `042026082cc9bc7872d1baa81755c50efa70b05f03b5369fdc5f0a1303009720` | 10 files, 8 directories |
| `libssl3-3.5.9-r1.apk` | `18c5778cbe52e1991303f8531970b05d4e6e036ea08349322f7422f42a689dc7` | 1 file, 2 directories |
| `openssl-3.5.9-r1.apk` | `ed11241475e5757ce8eb9788b18116a804a579395d4813605df12989a2acbabf` | 1 file, 2 directories |

All payload entries are root-owned regular files or directories, with no symlinks, hard links or device entries. Every file matched its signed payload's per-file checksum. Each control archive contains only `.PKGINFO`, with no install, upgrade, removal or trigger metadata. The `APKBUILD` lists a post-install hook for the separate `openssl-fips` subpackage, which is absent from the parent and the three archives. The receipt records each payload path, mode, owner, hash and comparable parent file. [Pinned Alpine recipe](https://raw.githubusercontent.com/alpinelinux/aports/0f4c7e8d0f5f7cebbdc2156eca4391080b732bf2/main/openssl/APKBUILD).

## Dependency and parent impact

- `libcrypto3` requires only the musl SONAME provided by the parent's installed `musl 1.2.6-r3`. `libssl3` requires this same musl SONAME, `libcrypto3=3.5.9-r1` and the crypto SONAME it provides. The `openssl` command would additionally require the same-version SSL library and its SONAME. The two libraries' declared forward dependencies are closed by the pair plus already-installed musl, with no additional APK needed. Installed-database ownership, reverse dependencies, and exact filesystem assembly have separate review.
- For the two libraries, the only changed regular-file content found is `usr/lib/libcrypto.so.3` and `usr/lib/libssl.so.3`. The four `/etc/ssl` configs, four engine files and legacy module match the parent's SHA-256 values. No alternative config path, FIPS module or symlink is introduced by these packages.
- The original parent's single recorded trigger belongs to BusyBox and watches `/bin`, `/usr/bin`, `/sbin`, `/usr/sbin`, `/lib/modules/*` and `/usr/lib/modules/*`. The two libraries' payload paths are outside those patterns. The third archive would add `/usr/bin/openssl` inside a watched directory. Its inspection is retained as evidence and it remains outside any assembly while the founder choice is pending.

## Source and notices

The signed controls and index name Alpine aports commit `0f4c7e8d0f5f7cebbdc2156eca4391080b732bf2`. Its recipe declares upstream OpenSSL `3.5.9`, Apache-2.0 and the five Alpine backports for CVE-2026-88822, CVE-2026-88823, CVE-2026-95691, CVE-2026-95692 and CVE-2026-107496. These match Alpine's security database and the OpenSSL advisory. The receipt records the published source tarball and patch SHA-512 values. Source tarball and patch bytes were not acquired or rebuilt. [Alpine source commit](https://github.com/alpinelinux/aports/commit/0f4c7e8d0f5f7cebbdc2156eca4391080b732bf2), [Alpine v3.24 security database](https://secdb.alpinelinux.org/v3.24/main.json), [OpenSSL advisory](https://openssl-library.org/news/secadv/20261110.txt).

None of the three APK payloads includes a license file. The upstream source tag's root `LICENSE.txt` is retained in `work/runtime-fixed-packages/openssl-3.5.9-LICENSE.txt` with SHA-256 `7d5450cb2d142651b8afa315b5f238efc805dad827d91ba367d8516bc9d49e7a`. The retrieved bytes match the tagged Git blob `49cc83d2ee29d13453188217f0e4edd70c7f842f`. Preserve that text with any qualified derivative. The packages and index are signature-verified. The source and notice metadata were obtained over HTTPS and checked against their specified commit, tag or vendor records. [OpenSSL Apache-2.0 license](https://github.com/openssl/openssl/blob/openssl-3.5.9/LICENSE.txt).

Raw receipts and the static verifier are in `work/runtime-fixed-packages/`. `python3 work/runtime-fixed-packages/inspect_apks.py` exited 0 and reproduced the four signature checks, payload/index matches and exact-parent comparison. No image was assembled or executed in this pass. Fresh derivative inspection, advisory and KEV checks, PostgreSQL tests and DEV-010/F3 exit remain pending.
