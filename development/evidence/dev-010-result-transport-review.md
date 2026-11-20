# DEV-010 independent parser result transport review

20 November 2026 · AUTH-013 · R040/R041/R046. Accepted as an unconnected decoder for authored fixtures. The review covered ambiguous JSON, incorrect dispatch provenance, authority-expanding output and error messages that could expose private text. The current fixtures contain authored data. Review budget was one focused pass and the database-free ingestion suite, within 15 minutes. [Transport plan](../../workers/parser/transport-integration-plan.md) · [AUTH-013](../APPROVALS.md#auth-013--founder-direct-pypdfium2-text-only-poc-direction-19-november-2026)

The decoder caps raw bytes before parsing, accepts one strict UTF-8 JSON value and rejects duplicate keys at every object level, including escape-equivalent spellings. Floating-point values and non-finite constants fail during decoding. The six trusted job fields are copied before parsing. The existing result validator checks them and enforces the review-only result schema and its page, anchor and text bounds. Output cannot supply or alter scope or approval. A valid payload still requires the broker's existing live authorization and publication fences when a qualified transport is connected. [Decoder](../../workers/parser/result_transport.py) · [Result validator](../../backend/modules/ingestion/contracts.py) · [Broker](../../backend/modules/ingestion/service.py)

Ordinary exception formatting and the error text omitted the synthetic private marker. A separate test using explicit traceback-local capture did include raw bytes from the decoder frame. The default application formatter emits only level and logger name. When this boundary is connected, preserve metadata-only reporting and exclude local-variable dumps from error handling across the decoder and its callers. This observation does not block the unconnected authored-fixture increment. [Default formatter](../../backend/modules/core/logging.py)

## Independent checks

Codex agent `transport_review` reviewed the decoder and test changes without authoring either. The tested working tree was based on `0a9a3ff44663a2c733ee315d8aa2419ae9171ac9`. Test environment was Darwin arm64 with Python 3.12.13 from `backend/.venv`.

| Check | Actual result |
| --- | --- |
| `SEBAVERSE_ENV=local DJANGO_DEBUG=1 backend/.venv/bin/python -m pytest backend/tests/ingestion/test_result_transport.py -q` | Exit 0, 32 passed. Two cases used the reviewed authored echo subprocess, including the ambiguous result. |
| `make test-ingestion` | Exit 0, 159 passed. |
| Inline Python 3.12.13 boundary spot checks using authored data | Exit 0. Exactly 1 MiB of valid JSON plus whitespace passed. Eight invalid cases failed with the bounded reason, covering one excess byte, Boolean and exponential numeric types, oversized integer token, escape-equivalent duplicate member, page count, per-block text and total text. The traceback privacy checks reproduced the behavior above. |

## Reviewed file hashes

| Checked file | SHA-256 |
| --- | --- |
| [Decoder](../../workers/parser/result_transport.py) | `7ebd82ea3c6887ff18f0e4d28817aa9d6661f5cfd48417a0d5e46190e55ad98e` |
| [Transport tests](../../backend/tests/ingestion/test_result_transport.py) | `e28cc2a0deef6d00e505213587de3c9d788a7ea842bd431478436f0460a51f53` |
| [Process guard](../../workers/parser/process_guard.py) | `73b9835b3f0904120ac1833900875b026b9ee867d4afd229e178b2ae4911a5ea` |
| [Authored child](../../backend/tests/ingestion/fixtures/process_guard_child.py) | `aa43bfeb3d082cbfeaab166b47b043e42f9b30831c4a94bc5bf7cef2b5c669f7` |
| [Result validator](../../backend/modules/ingestion/contracts.py) | `f2a141e47425228c9798317044e268c1cee56a8bfc3abec0d28bec09a843abea` |

The increment tests worker stdout and provenance before a future broker connection. PostgreSQL, hosted Linux process execution, native PDFium, scanner, OS isolation and actual extraction fidelity remain unverified in this increment. DEV-010 and F3 remain in progress.
