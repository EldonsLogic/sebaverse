# DEV-010 independent direct digital-PDF adapter review

19 November 2026 at 20:09 UTC · AUTH-013 / ADR-014 · R039, R040, R041, R046. **Accepted as a disabled worker core with authored-fixture tests.** The review covered incorrect dispatch, scan or source binding, incomplete extraction, and mishandled parser resources. The current scope has no learner exposure. Review was limited to one focused code and test pass with scoped corrections. [Authorization](../APPROVALS.md#auth-013--founder-direct-pypdfium2-text-only-poc-direction-19-november-2026) · [Worker contract](../../workers/parser/digital-pdf-contract.md).

## Findings and corrections

- The initial adapter compared raw key bytes when enforcing separate job and scan signing keys. Distinct byte strings can represent the same effective HMAC-SHA256 key. The correction compares HMACs over a fixed, adapter-specific marker and rejects equivalent keys before the factory opens. Two authored regression cases cover short-key padding and long-key hashing.
- The initial output-size check converted its own `output_too_large` error into `invalid_result` because both are ValueErrors. The correction preserves a bounded, distinct output-size reason.

The implementation validates exact expected fields, job and scan signatures, independent expiry, scanner identity, clean status and source byte count, PDF header and SHA-256 before opening any document. The scan covers the same object, generation, dispatch, parser, media type, byte count, source and scope bindings. Envelope preflight rejects malformed payloads before HMAC serialization. With no factory, the runtime remains unavailable. The production broker, asset registry and backend configuration were unchanged in the reviewed diff. The broker still owns live authorization, quarantine, publication and withdrawal. [Adapter](../../workers/parser/digital_pdf.py) · [Broker](../../backend/modules/ingestion/service.py).

The exact cached wheel's `pypdfium2/_helpers/textpage.py` confirms that `get_text_range` accepts the bounded index and count with explicit strict decoding. Its documented UCS-2 and char-index mapping limits matter to real PDF fidelity. The adapter holds unequal-length or malformed native results and blank pages. It preserves returned text without normalization, applies page, chunk, aggregate and serialized limits, and emits the existing `needs_review` schema with stable anchors. Cleanup attempts all acquired handles in reverse order after success, exceptions or a soft timeout, including when an inner close fails. The fake failure cases check bounded errors and standard traceback redaction.

## Independent checks

| Check | Actual result |
| --- | --- |
| `make test-ingestion` | Exit 0. 96 passed, including 64 direct-adapter cases. |
| `make backend-check` | Exit 0. 431 passed, PostgreSQL integration deselected, Django checks clean. |
| `git diff --check` | Exit 0. |
| Diff against HEAD for ingestion service, backend settings and scanner approved assets | Empty. |

The independent reviewer was Codex agent `runtime_fix_recheck`, who authored neither implementation nor tests. Checks ran against the working tree based on `1378dc7`. The reviewed [adapter](../../workers/parser/digital_pdf.py) SHA-256 is `50a278e1cdf63feb3eb60212719fc514fb4da2c47192229fb7426d8d5a411adc`. The reviewed [tests](../../backend/tests/ingestion/test_digital_pdf.py) SHA-256 is `98aa6293701c953dae7b89432070d343e36bdf35fd3e2588eef0c9cf24ae4957`.

The ten-second monotonic limit checks calls that return. A qualified parent watchdog and OS resource limits must still bound a stalled native call and native allocations. Actual PDFium execution, scanner qualification, exact runtime security and rights, OS isolation, cancellation through worker transport, and Arabic/bilingual fidelity remain open. PostgreSQL integration and F3 exit were outside this review.
