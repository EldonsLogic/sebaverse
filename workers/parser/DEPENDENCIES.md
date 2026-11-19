# Restricted parser dependency boundary

Docling remains selected for the isolated F3/A3 ingestion worker. F1 does not install/import this parser, its OCR engines, model assets or a scanner. No placeholder lockfile or fake clean scan is supplied. Backend/web runtime must not transitively pull these dependencies or auto-download weights.

Before DEV-010 (private safe upload integration), record the exact separately locked parser/scanner releases, transitive notices and vulnerabilities, model/asset license/processing rights, hashes and acquisition source. Then run clean isolated install, resource/egress limits, malicious input/scan-outage failures and manifest validation tests. Models are provisioned deliberately, never implicitly by first request. Ingestion stays disabled until that task and phase checks pass.

AUTH-013 / ADR-014 update (19 November 2026): direct PyPDFium2 is selected for the first authored digital-text PoC; Docling remains the advanced extraction direction. The adapter has no configured default factory and no native SDK import at module import. Implementing owned API calls and fake-engine unit tests does not qualify an artifact or authorize installing/importing/executing PyPDFium2. Existing rights, native advisory, scanner and isolation gates remain.
