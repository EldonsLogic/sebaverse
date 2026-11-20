# DEV-010 parser result transport test plan

20 November 2026 · AUTH-013 · R040/R046. A checked-in Python child can exit successfully and return bounded stdout containing ambiguous JSON. The byte transport preserves the output. The broker's existing result validator checks a decoded dictionary, so duplicate JSON members can disappear before provenance checks. Add a narrow decoder between those boundaries for the authored worker experiment. Runtime activation remains held. [Process guard](../../workers/parser/process_guard.py), [result contract](../../backend/modules/ingestion/contracts.py).

An ambiguous or replayed result could associate derived text with the wrong private upload or dispatch. The current fixture scope uses authored text only. The plan uses one bounded test pass with the existing checked-in child and no SDK, scanner, database, image or network.

## Observed gap

A local authored echo subprocess returned a result with two `quality` members, where the first said `approved` and the second said `needs_review`. The guard preserved the bytes. Python's ordinary JSON decoder kept the final member, and the current dictionary validator accepted that decoded shape. This reproduces the composition gap under the unactivated experiment. The live broker path currently accepts a fixture parser's dictionary directly. The existing tests already cover pipe floods, cancellation and child cleanup, and the staged PostgreSQL probe covers an otherwise valid result arriving after withdrawal. [Authored child](../../backend/tests/ingestion/fixtures/process_guard_child.py), [process tests](../../backend/tests/ingestion/test_process_guard.py), [dict tests](../../backend/tests/ingestion/test_contracts.py), [broker path](../../backend/modules/ingestion/service.py), [withdrawal fixture](../../backend/tests/ingestion/postgres_probe.py).

## Acceptance cases

| Boundary | Focused case |
| --- | --- |
| Valid output | An exact needs-review result from the authored echo child preserves Arabic, German and mathematical notation, page number, anchor and server-owned provenance. |
| Bytes and encoding | Reject oversized raw stdout before decode, invalid UTF-8, truncated or trailing records, and an alternate encoding that a permissive bytes decoder would accept. Existing transport tests already exercise actual pipe overflow. |
| Ambiguous JSON | Reject duplicate root and nested members even when the last value would pass the existing dictionary validator. Reject nonfinite numbers and fail with a bounded reason for malformed or excessively nested JSON. |
| Existing result rules | Reject reused or malformed anchors and an otherwise valid response bound to another object, dispatch or generation. Keep the server's expected identity independent of the child response. |
| Failure output | Return a bounded error without child output in the message or traceback. Reuse the existing authored echo child and bounded process guard. |

Use the existing result schema and its text, page, anchor, provenance and output limits. Keep authorization, consent, rights, late-result fencing and publication with the live broker. The test outcome will establish whether authored subprocess bytes reach the existing review-only result contract safely. Database state, native PDF quality and operating-system isolation remain separately gated.

## Local verification

20 November 2026. Darwin arm64, Python 3.12.13, working tree based on `0a9a3ff`. The focused suite exercises both acceptance and rejection of bytes from the existing authored echo child, alongside direct decoder tests. The inherited test file ran as written.

| Command | Result |
| --- | --- |
| `SEBAVERSE_ENV=local DJANGO_DEBUG=1 backend/.venv/bin/python -m pytest backend/tests/ingestion/test_result_transport.py -q` | Exit 0, 32 passed in 0.08 s. |
| `make test-ingestion` | Exit 0, 159 passed in 1.72 s. |

The tested SHA-256 was `e28cc2a0deef6d00e505213587de3c9d788a7ea842bd431478436f0460a51f53` for the [test file](../../backend/tests/ingestion/test_result_transport.py) and `7ebd82ea3c6887ff18f0e4d28817aa9d6661f5cfd48417a0d5e46190e55ad98e` for the [decoder](../../workers/parser/result_transport.py). This verification used synthetic fixtures and left the worker disconnected from the live broker. Hosted Linux, PostgreSQL, scanner, native PDFium and extraction fidelity remain outside these results. DEV-010 and F3 remain open.
