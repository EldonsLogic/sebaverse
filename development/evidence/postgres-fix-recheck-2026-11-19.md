# PostgreSQL official image fix recheck

19 November 2026 at 11:19:59 UTC. **Both official tags still point to the previously inspected Linux amd64 image, whose publisher inventory lists OpenSSL `3.5.9-r0`.** One metadata-only check assessed fix availability for disposable synthetic CI. Running the unpatched runtime would leave the AUTH-011 gate unresolved. [Previous evidence](postgres-official-fix-status-2026-11-19.json), [runtime gate result](integration-2026-11-19.md).

| Docker Hub tag | Last tag update UTC |
| --- | --- |
| [`17.12-alpine`](https://hub.docker.com/v2/repositories/library/postgres/tags/17.12-alpine) | 19 November 01:09:19 |
| [`17-alpine`](https://hub.docker.com/v2/repositories/library/postgres/tags/17-alpine) | 19 November 01:09:00 |

Both live tag responses reference index `sha256:526f86d93c6ea08fd3f1fe5605650cacc781b2c6013169a0ad8f42c7d3d84f32` and Linux amd64 manifest `sha256:e80acae3f1109e8e4533618b594918936f2858c63afc7204c4773148a673add8`, pushed on 18 November at 22:11:58 UTC. Recomputed the cached index and attestation hashes against their descriptors and confirmed the publisher SPDX subject matches that exact platform digest. SPDX `sha256:d6bd5d959dd4dfc3cfc3e74ea981f0c3be40c8120cdf5eef7e37c514f13f5c65` lists `libcrypto3`, `libssl3` and `openssl` at `3.5.9-r0`. [Official image source, `17/alpine3.24`](https://github.com/docker-library/postgres/tree/ac9627dcf544a8454f212a12ddeebfcdc0803d3e/17/alpine3.24).

The ignored metadata receipt is `work/postgres-17-alpine-fix-recheck/receipt.json`, SHA-256 `7f84fb151d44d9fed0839583be20e95ac527fe2ab39b33bfe5546c56fcb704a5`. The check fetched two tag responses and reused verified registry metadata. No image layers, scan, build, database execution or CI dispatch were involved. Both original runtime and latest supplier build remain held under the existing gate. No pin, review or approval changed.
