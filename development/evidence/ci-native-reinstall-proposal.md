# CI native package transaction recovery proposal

19 November 2026. One focused review for run `44510517163`. The risk is letting PostgreSQL CI proceed on runner libraries whose installed bytes and provenance have failed the existing checks. The only target is disposable synthetic Ubuntu 24.04 amd64 CI.

The run's authenticated `libc6` candidate and installed version were both `2.39-0ubuntu8.12`. Its archive SHA-256 matched the existing approval. The current upgrade command then reported zero changes and the parser stopped at “No complete libc6 upgrade transaction.” The record captures only the installed main package. It does not establish the five companions or the installed binary bytes. [Run](https://github.com/EldonsLogic/sebaverse/actions/runs/44510517163).

[prepared patch](ci-native-reinstall-proposal.patch) adds a conditional path for the exact already-installed version. It asks for the same six packages at that version in a read-only APT simulation, requires all six installed and proposed versions to match, and rejects missing, extra, duplicate or drifted package rows. The apply helper can use `--reinstall` only under explicit committed approval. Existing checks still bind downloaded archives and notices by SHA-256, require a fresh six-package simulation over the local files, rehash them immediately before the operation, verify all six installed versions afterward and require the existing native inventory and advisory gate. The ordinary upgrade remains on its existing command. This keeps the current receipt contract. A no-op would need an additional proof that installed files match the approved archive payloads, plus a new accepted receipt path. [APT documentation](https://manpages.debian.org/unstable/apt/apt-get.8.en.html).

If authorized, independently review the two helper changes and the exact approval scope. Add Boolean `allow_same_version_reinstall: true` to `infra/local/native-patch-approval.json` with the explicit authorization and a condition restricting it to these six reviewed archives at `2.39-0ubuntu8.12`. Keep the existing version, archive and notice hashes. The scratch patch intentionally omits any approval or review policy file edits. Following explicit approval to update the source binding, change only these two entries in `infra/synthetic-openssl-review.json` `source_inputs`:

| Bound helper | Proposed SHA-256 |
| --- | --- |
| `tools/security/prepare_ci_native.py` | `349185414ecb90e197b4b05b7698fe7c9c187904e9156a6d4c6377b0c58a2d45` |
| `tools/security/apply_ci_native_patch.py` | `ebc97cfafcc027029ed825e2e07ee961bc44bfecc6987eac7c9323b6e9c7b167` |

The AUTH-007 dates, expiry, identities and severities stay unchanged. `infra/security-reviewed-findings.json` does not bind these two helpers and requires no update. The launcher, workflow, npm review and runtime pins stay unchanged. A fresh authorized Ubuntu runner must confirm that APT emits the exact six same-version rows from both signed-index and local-archive simulations. A missing, mixed-version or changed set keeps the job blocked. The existing fresh advisory, package and platform checks remain prerequisites for database execution.

Local evidence from the scratch copies only:

- `python3 -m unittest discover -s work/ci-idempotency-review/original/tools/tests -p 'test_ci_native_*.py'` passed 19 existing tests.
- `python3 -m unittest discover -s work/ci-idempotency-review/proposed/tools/tests -p 'test_ci_native_*.py'` passed 23 tests, including the real blocked receipt and synthetic negative cases for approval, missing/drifted companions, wrong versions and notice tampering.
- `git apply --check work/ci-idempotency-review/native-reinstall.patch` passed.
- No APT command, package install, database, or live helper, approval or review edit occurred. The expected six-row reinstall simulation is synthetic and actual hosted semantics remain unverified.

Founder choice required only because the explicit 19 November instruction forbids re-dating or rebinding existing security reviews. Applying this new bound-helper repair requires a narrowly scoped override for the two listed AUTH-007 source hashes, plus the committed same-version-reinstall approval. No review date, expiry, advisory, artifact pin or severity changes are proposed. Nothing is applied until that choice.

Approved by founder on 19 November as AUTH-012: “Apply the exact repair and two-hash update (recommended).” Applied only after that answer. Hosted execution is pending and no phase is approved.
