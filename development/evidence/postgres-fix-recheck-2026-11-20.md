# PostgreSQL official image fix recheck

At 11:33:43 UTC on 20 November 2026, both original official tags still resolved to the same Linux amd64 image. Its publisher inventory lists `openssl`, `libssl3` and `libcrypto3` at `3.5.9-r0`. Alpine's released fix is `3.5.9-r1`. The AUTH-011 database hold for DEV-010 remains in effect. [Previous recheck](postgres-fix-recheck-2026-11-19-evening.md) · [Alpine fix evidence](postgres-official-fix-status-2026-11-19.json).

| Official Docker Hub tag | Last tag update UTC |
| --- | --- |
| [`17.12-alpine`](https://hub.docker.com/v2/repositories/library/postgres/tags/17.12-alpine) | 19 November 01:09:19 |
| [`17-alpine`](https://hub.docker.com/v2/repositories/library/postgres/tags/17-alpine) | 19 November 01:09:00 |

Both live responses matched OCI index `sha256:526f86d93c6ea08fd3f1fe5605650cacc781b2c6013169a0ad8f42c7d3d84f32` and Linux amd64 manifest `sha256:e80acae3f1109e8e4533618b594918936f2858c63afc7204c4773148a673add8`. The checker recomputed hashes for cached index, manifests and attestation payloads and verified the exact platform subject of the publisher provenance and SPDX. The SPDX digest is `sha256:d6bd5d959dd4dfc3cfc3e74ea981f0c3be40c8120cdf5eef7e37c514f13f5c65`. [Official image source at `ac9627d`](https://github.com/docker-library/postgres/tree/ac9627dcf544a8454f212a12ddeebfcdc0803d3e/17/alpine3.24).

This was one metadata-only check for the released fix in disposable synthetic CI, with no current learner exposure. The checker exited 0. Image layers, scanning, runtime execution and CI dispatch were outside this check. A supplier image with fixed packages still needs exact-image review before the database integration can run.

The ignored receipt at `work/postgres-17-alpine-fix-recheck-2026-11-20/receipt.json` has SHA-256 `b9be004fcf2e7e0d62d27555c6a7cfad9f392690b06f6e8a2a24d27ae86048aa`.
