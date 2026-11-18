# Parser boundary — DEV-010 in progress

No parser runtime or model asset is installed/cleared yet. The selected Docling release candidate is 2.150.1; a binary-only minimal PDF feature closure is being resolved under ignored work/dev-010. Candidate metadata is not license/native/security/model-rights clearance.

A production worker must receive only a bounded signed job manifest and a private read-only input, no learner database credentials, broad filesystem access or egress. Enforce process CPU/RAM/time/output/page limits and offline assets before launch. The broker treats all output as untrusted and validates hash, object ID, generation, parser version, bounded page/anchor/text structure and current scope before review/publication. Source text is data, never a tool instruction.

Current tests may supply authored-fixture adapters through a server-owned registry restricted to exact fixture source hashes. They are not a malware scanner or OCR/Docling execution, and they cannot clear arbitrary uploads. Do not replace this boundary with unrestricted subprocess execution or a model download. Actual isolation, scanner signature lifecycle and Docling asset review/execution remain mandatory before DEV-010 completion or F3 exit.
