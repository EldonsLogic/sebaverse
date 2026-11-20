# Independent authored PDF input review

20 November 2026 · DEV-010 / AUTH-013 · R039, R040, R041, R046. Reviewer: Codex subagent `input_review`, independent of the codec and fixture authors. Reviewed the final working tree based on `2ecb5c9bf3c5e39c054c9e60e378ffc67f94721a`. Verdict: ready to integrate for the authored synthetic input experiment.

| Review area | Observed behavior |
| --- | --- |
| Read and allocation bounds | The codec reads an eight-byte prefix, bounds header length to 1–4096 bytes, validates the exact object shapes and primitive types, and checks the source byte count before requesting its body from a blocking buffered binary stream. It requires exactly that many bytes and a one-byte EOF check before returning. The writer validates exact bytes and metadata before producing a bounded frame. |
| JSON and private failures | Strict UTF-8, duplicate-member rejection at all depths, bounded integer conversion, signed 64-bit field bounds, and rejection of floats and non-finite values precede source transfer to extraction. Malformed shapes, recursion and decoding/I/O failures are reduced to a content-free error. The fixture exits before writing a result on rejection. The guard returns bounded errors and discards stderr content. |
| Guard and child | Trusted caller code selects `pdf_fixture_v1`, with an absolute input ceiling of 8,392,712 bytes. Standard input retains its 1 MiB ceiling and both profiles default to 64 KiB. The frame has no profile selector. The child uses fixed checkout-relative import roots and a fixed authored factory, scanner ID, keys and timestamp. The owned PDF core still checks both envelopes and verifies source type, size and hash. A valid result for a different dispatch is rejected against the caller's separately created binding. |
| Regression review | The initial over-limit payload check exercised the caller's chosen cap. The test owner added a configured ceiling one byte over the profile maximum and an unknown caller profile. Both must fail before spawn. The suite also passes a frame at the exact profile ceiling through a real child and verifies cleanup on success, rejection, cancellation and deadline. |

Independent execution on Darwin arm64, Python 3.12.13, with PostgreSQL opt-in disabled:

- The input, process guard, result and owned PDF core suites reported **157 passed in 2.80s**, exit 0.
- `SEBAVERSE_TEST_POSTGRES=0 make test-ingestion` reported **199 passed in 2.87s**, exit 0.
- `git diff --check` returned exit 0. Reviewed SHA-256 prefixes are `4ea968512a52` for [codec](../../workers/parser/input_transport.py), `dc5a7e1e1854` for [guard](../../workers/parser/process_guard.py), `43aece13b358` for [fixture](../../backend/tests/ingestion/fixtures/pdf_worker_fixture.py) and `4fbf3c6b7f63` for [suite](../../backend/tests/ingestion/test_input_transport.py).

Public fixed fixture keys exercise binding behavior. HMAC verification also confers signing authority, so production needs a reviewed design that keeps both signing authorities outside the worker and preserves independent clean-scan verification. Buffered copies, immutable imports, filesystem/network/CPU/RAM/process limits and one-object credential provisioning remain open runtime concerns. Scanner and native parser qualification, actual Arabic and bilingual PDF extraction fidelity, PostgreSQL and live broker activation were outside review. F3 remains in progress and AUTH-014 still awaits a qualifying supplier update. [Authored input scope](dev-010-authored-input.md) · [Supplier hold](auth-014-recovery-checkpoint.md).
