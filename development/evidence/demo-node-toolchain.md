# Local teaching demo toolchain notice check

25 November 2026 · AUTH-017 · one bounded metadata pass and independent signature recheck. The demo needs a qualified Node runtime for its build and local browser verification. At intake the checked-in pin was Node `24.22.1` and the package-manager pin was npm `10.8.2`. The historical F1 run used the then-bundled Node and a separate npm CLI. The integrator previously ran a version probe and reported bundled Node `24.22.3` and global Node `20.19` on this Apple Silicon host. No Node workload ran for this assessment. [Node pin](../../.node-version) · [Dependency procedure](../DEPENDENCIES.md#reproduce) · [Historical F1 evidence](f1-web-summary.md) · [Demo authorization](../../sources/local-teaching-demo-instruction.md)

**The exact older version is available, but routine restoration for demo execution is held.** The official Node project released `24.22.3` on 11 November 2026 to fix several High-severity findings in the 24.x line. A version match would reproduce the prior pin and leave those later fixes out. The historical npm dependency audit supplies no disposition for those Node runtime findings. [Official security notice](https://nodejs.org/en/blog/vulnerability/november-2026-security-releases) · [24.22.3 release](https://nodejs.org/en/blog/release/v24.22.3)

## Exact 24.22.1 metadata

The [official release note](https://nodejs.org/en/blog/release/v24.22.1#shasums) dates Node `24.22.1` to 21 October 2026 and publishes the following SHA-256 values in its clear-signed checksum block. The [official directory index](https://nodejs.org/download/release/v24.22.1/) lists these two archives and the signed checksum files.

| Official Darwin arm64 filename | Publisher SHA-256 |
| --- | --- |
| `node-v24.22.1-darwin-arm64.tar.xz` | `654ba79de6155647e22321932b45f2a1ccb705976cc337c9b8e278beb085a628` |
| `node-v24.22.1-darwin-arm64.tar.gz` | `89c682593d76cd44233fa53b1563264e7de9cbb189cad169135c5b4fadfbc0a7` |

This records advertised availability and checksum values. The browser did not open the direct plaintext checksum endpoint, so the values above come from the official release note. Archive bytes and checksum signatures were not acquired or verified. The exact tagged source lists MIT-style terms for Node core and publishes component notices for separately maintained libraries. The tagged npm metadata and release archive list `11.19.1`, which is distinct from Sebaverse's npm `10.8.2` pin. Any qualified workspace copy must retain the official notices and select the independently pinned npm CLI for npm commands. [Tagged license and component notices](https://github.com/nodejs/node/blob/v24.22.1/LICENSE) · [Tagged npm metadata](https://github.com/nodejs/node/blob/v24.22.1/deps/npm/package.json#L1-L4) · [Official archive](https://nodejs.org/en/download/archive/v24.22.1)

## Exact 24.22.3 candidates

The [official 24.22.3 release note](https://nodejs.org/en/blog/release/v24.22.3#shasums) publishes these Darwin arm64 checksums in its clear-signed block. The [official release index](https://r2.nodejs.org/download/release/v24.22.3/) lists both files and the signature metadata. The [24.22.3 tagged license](https://github.com/nodejs/node/blob/v24.22.3/LICENSE) contains the Node core grant and separate component notices. These are supplier metadata. The archive and its signature remain unverified by this pass.

| Official Darwin arm64 filename | Publisher SHA-256 |
| --- | --- |
| `node-v24.22.3-darwin-arm64.tar.xz` | `1d64136c8a43d648d1b3bad10797a4c995b1ca032d2bde8799de43b37f058fe5` |
| `node-v24.22.3-darwin-arm64.tar.gz` | `ff6e17d4874b76d272212b908cc020d6e815fba5a6c7eaaa06add725840307fd` |

The Codex workspace dependency connector identified bundle `26.1119.11507` and executable `~/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node`. Static inspection found a 126,851,808-byte arm64 Mach-O executable, SHA-256 `28cebeed86bc26f17b61537f157ed03f5632738a46ca2b96675bcf5ca037758e`. The runtime manifest identifies it as vendor build `24.22.3-cua.1`. The first strict macOS signature check in the restricted context exited 1 with signer authority unavailable. The independent recheck of the same executable with approved trust-service access exited 0, reported that the signature was valid on disk, and satisfied the designated requirement. The verified signer was OpenAI OpCo, LLC, TeamIdentifier `2DC432GLL2`, CDHash `d22709330fae9be29b8b401027c1f8e60c982f52`, signed 20 November. The earlier failure does not establish tampering. Signature verification identifies the vendor build and its signer. The vendor executable hash and the upstream archive hashes identify separate artifacts, and the vendor signature supplies no inventory of upstream changes or backports. [Independent signature and scope review](demo-node-patch-review.md#observed-publisher-and-host-evidence)

## Decision inputs

- The supplier marks CVE-2026-123863, CVE-2026-123864, CVE-2026-123865, CVE-2026-123866, CVE-2026-123872, CVE-2026-123874 and CVE-2026-126051 High in the release that follows `24.22.1`. The posted High cases involve HTTPS, TLS or HTTP/2 paths. Node's notice explicitly excludes cleartext HTTP from CVE-2026-123864. The proposed demo is cleartext loopback with authored data. This pass did not establish the actual reachability of every affected path through the combined build, npm, Vite and browser tooling. No actual exposure or compromise is inferred. [Security notice](https://nodejs.org/en/blog/vulnerability/november-2026-security-releases)
- The integrator selected the official `24.22.3` Darwin arm64 archive for verification as data. The independent scope review found that the same-component security patch can fit existing authority once exact provenance, applicable notices, security and compatibility checks are satisfied. Before running it, verify the signed checksum with trusted supplier keys, check the exact bytes and platform signature, and obtain independent acceptance. Retain the separately pinned npm `10.8.2` and select the runtime only in the workspace. This receipt does not change the pin, global Node selection, application dependencies, lockfiles, native database/scanner gates or release thresholds. [Independent patch scope review](demo-node-patch-review.md#authority-and-compatibility)

No official archive download, checksum signature verification, extraction, install, demo build, browser run, package-manager change or verification bypass was performed for this receipt.
