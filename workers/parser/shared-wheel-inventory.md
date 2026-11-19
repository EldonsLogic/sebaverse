# Shared parser wheel inventory

19 November 2026 · AUTH-008 · DEV-010 · R039/R040/R041/R046. Static archives only, no installation or execution. [Exact inventory](shared-wheel-inventory.json).

All eight selected archives passed static hash and notice verification. Bundled native code and redistribution obligations matter for any future parser runtime handling learner uploads. This follow-up used one bounded download of up to 110 seconds and local archive inspection.

| Package | Archive result | Native members | Notice files |
| --- | --- | ---: | ---: |
| charset-normalizer 3.5.2 | SHA-256 verified | 0 | 1 |
| lxml 6.1.3 | SHA-256 verified | 7 | 2 |
| numpy 2.5.5 | SHA-256 verified | 20 | 20 |
| pandas 3.1.1 | SHA-256 verified | 45 | 19 |
| pillow 13.0.0 | SHA-256 verified | 26 | 1 |
| pydantic-core 2.50.4 | SHA-256 verified | 1 | 1 |
| pyyaml 6.0.3 | SHA-256 verified | 1 | 1 |
| rpds-py 2026.9.1 | SHA-256 verified | 1 | 1 |

All eight archives match the saved exact-version PyPI metadata and prior resolver metadata. The inventory uses the published pure-Python charset-normalizer wheel as a proposed artifact selection. The recorded notice hashes and native filenames establish archive contents. Component versions, advisory applicability, redistribution rights and runtime qualification remain open.

The first NumPy transfer reached its deadline at 11,927,552 of 15,720,599 bytes. Automatic approval review hit a usage limit before the first resume command executed. After renewed authorization, one request to the same published URL returned HTTP 206 and the remaining 3,793,047 bytes. The completed wheel matched SHA-256 `704d819265e5d1064d932968e9ee85fff2103ccc78c05b878c06943ba27b8507`. The static inventory found 20 native members, including `numpy.libs/libscipy_openblas64_-4b78795a.so`, and 20 notice entries. [Exact PyPI release metadata](https://pypi.org/pypi/numpy/2.5.5/json), [candidate resolver hashes](candidate-requirements.txt#L463).

The exact PyPDFium2 5.15.2 wheel has no Requires-Dist entries in its METADATA. A direct adapter would avoid these shared Python packages for an initial text-only PoC. Proposed ADR-014 remains pending and retains the PDFium native review and existing gates. [ADR-014](../../architecture/adr/ADR-014-minimal-digital-pdf-poc.md).
