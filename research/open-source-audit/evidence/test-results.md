# Narrow execution evidence

Audit date 2026-11-10. These checks are not full upstream unit suites or proof of educational/security validity. No PoC/product was implemented.


## DeepTutor

# Reviewed isolated smoke

Date 2026-11-10; source 60fb3bdfddb30b7740c7ce3bd9b28d908f2af6db.

```python
# Run with python3.11 after inspecting the dependency-free module.
import runpy
f=runpy.run_path('work/repos/DeepTutor-sparse/deeptutor/learning/mastery.py')['compute_mastery']
for x,y in [([],0.0),([True],.5),([True,True],.8),([True]*3,1.0),([False]*5,0.0)]:
    assert f(x)==y,(x,f(x),y)
```

Actual output: PASS: five reviewed isolated compute_mastery assertions; Python 3.11; no package imports or provider calls. Exit 0. No package installation, source edits or network requests. This establishes numerical behavior only, not pedagogical validity. Older host python3 first failed on zip(strict=True); supported python3.11 resolved that runtime mismatch.


## LearnHouse

PASS: 10 isolated assertions: magic headers, invalid zip, valid zip, size guard, nested org-scope restoration. No app, DB, network, vendor calls, or repository writes.
CONFIRMED isolated behavior: arbitrary stripe-signature header exempts a non-webhook path from CSRF middleware. Browser exploitability not tested.


## Adaptive libraries

# Adaptive audit execution record — 2026-11-10

No upstream trees edited. Source code read from clones / selected partial-clone blobs. No package installation, unknown setup execution, paid service, training dataset or student data.

## FSRS smoke

Reviewed imports/source and upstream expected sequence in `tests/test_basic.py:31–49` before running. Ran from source with `PYTHONDONTWRITEBYTECODE=1`, Python 3.11 and existing typing-extensions from the system's Python 3.9 user site on the import path. Only pure scheduler imports used; optional optimizer not loaded.

Assertions: thirteen ratings `[Good]*6 + [Again]*2 + [Good]*5`, fixed first review UTC 2022-11-29 12:30, next review at preceding due date, fuzzing disabled; expected review intervals in days; final Card to_dict/from_dict equality.

Result: PASS — `[0,2,11,46,163,498,0,0,2,4,7,12,21]` and exact card dictionary round-trip.

Earlier environment probes: default Python 3.9 fails FSRS `match` syntax (requires >=3.10); Python 3.11 lacked typing-extensions until existing import path supplied. Neither failure implies a source defect.

## Not executed

- Full pytest suites: pytest absent in default interpreter.
- KT/BKT/IRT numerical training and inference: numpy, pandas, Torch and Pyro absent in default interpreter. No package installs attempted.
- EduStudio: intentionally no execution due to pinned workflow reading PYPI_API_TOKEN and emitting an encoded value to CI logs. Static observation only; actual secret exposure/package integrity not established.
- pyKT full clone initially stalled; partial-clone HEAD obtained and relevant blobs read; complete checkout still unavailable at audit time. `tests/test_dkt.py` requested as a possible test path and does not exist; actual tree lists `check_dataset.py`, `test.sh`, `test_opera_integration_config.py`.

No CVE/OSV scan, full dependency resolution, latency benchmark, representative Egyptian learning-outcome study or model calibration was completed. Source existence is not a production-readiness certificate.
