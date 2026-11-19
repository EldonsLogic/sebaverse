# PostgreSQL official image fix recheck

At 19:48:38 UTC on 19 November 2026, both official PostgreSQL tags still resolved to the morning Linux amd64 image, whose publisher inventory lists OpenSSL `3.5.9-r0`. The released Alpine fix is `3.5.9-r1`. The AUTH-011 database hold for DEV-010 remains in effect. [Morning recheck](postgres-fix-recheck-2026-11-19.md) · [Alpine fix and original image evidence](postgres-official-fix-status-2026-11-19.json) · [Hosted integration result](integration-2026-11-19.md).

This single metadata-only check verified whether the supplier image for disposable synthetic CI still included the affected packages. This environment uses synthetic data and has no current learner exposure. The check was bounded to the two original tags in one attempt.

| Official Docker Hub tag | Last tag update UTC |
| --- | --- |
| [`17.12-alpine`](https://hub.docker.com/v2/repositories/library/postgres/tags/17.12-alpine) | 19 November 01:09:19 |
| [`17-alpine`](https://hub.docker.com/v2/repositories/library/postgres/tags/17-alpine) | 19 November 01:09:00 |

Both live tag responses matched the retained OCI index `sha256:526f86d93c6ea08fd3f1fe5605650cacc781b2c6013169a0ad8f42c7d3d84f32` and Linux amd64 manifest `sha256:e80acae3f1109e8e4533618b594918936f2858c63afc7204c4773148a673add8`, pushed on 18 November at 22:11:58 UTC. The checker recomputed hashes for the cached index, manifests and attestation payloads and verified the SPDX and provenance subjects against that platform digest. Publisher SPDX `sha256:d6bd5d959dd4dfc3cfc3e74ea981f0c3be40c8120cdf5eef7e37c514f13f5c65` lists `openssl`, `libssl3` and `libcrypto3` at `3.5.9-r0`. [Official image source at `ac9627d`](https://github.com/docker-library/postgres/tree/ac9627dcf544a8454f212a12ddeebfcdc0803d3e/17/alpine3.24).

The command `python3 work/postgres-17-alpine-fix-recheck-evening/recheck.py` exited 0. Its ignored receipt is `work/postgres-17-alpine-fix-recheck-evening/receipt.json`, SHA-256 `02a2d9068e0737b5c357d3cc761785abd6aca0e4d253df1c733ee01437a27218`. Evidence covers registry metadata and publisher inventory. Image download, scanning, runtime execution and CI dispatch were outside this check. A supplier build with the fixed packages is still needed for exact-image review before the database integration can be rerun.
