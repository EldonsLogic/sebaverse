# Backend dependency foundation

DEV-005 / F1 · Python 3.12, Django 5.2 LTS, Django REST framework, Uvicorn and Psycopg 3. The selected stack is unchanged. This directory currently contains dependency manifests/locks and an ignored local environment, not a Django project or product implementation. No database, server, model provider or real learner data is configured by this task.

## Exact direct dependencies

| Group | Package | Pin |
|---|---|---|
| Runtime | Django | 5.2.19 |
| Runtime | djangorestframework | 3.18.3 |
| Runtime | uvicorn, minimal extras | 0.54.0 |
| Runtime | psycopg[binary] | 3.3.8 |
| Development only | pytest | 9.2.0 |
| Development only | pytest-django | 4.14.0 |

`uv.lock` pins the complete Python 3.12 dependency graph with official PyPI artifact hashes. Project packaging is disabled; sync must not build/install an application package. Development test tools are a separate dependency group. Uvicorn's optional `standard` extras, ORM alternatives, provider SDKs, parser/model packages and all research repositories are absent.

## Reproduce locally

Run from the repository root with a reviewed `uv` installation. The observed resolution used uv 0.11.14 and project-local CPython 3.12.13 on macOS arm64. Keep the cache/runtime/virtualenv ignored. `--no-bin` prevents managed Python from creating a user-wide executable shortcut.

```bash
export UV_CACHE_DIR="$PWD/work/uv-cache"
export UV_PYTHON_INSTALL_DIR="$PWD/work/uv-python"
uv python install 3.12.13 --no-bin
uv sync --project backend --locked --no-build --no-install-project --python 3.12.13 --no-python-downloads --default-index https://pypi.org/simple
uv pip check --python backend/.venv/bin/python
backend/.venv/bin/python -m pytest --version
```

Use the locked graph for repeatability; do not run `uv lock --upgrade` as ordinary startup. A future patch update is a reviewed change with metadata/license/security checks and fresh phase evidence. A production-only environment omits the dev group with `--no-dev` while retaining `--locked --no-build`. Windows uses the equivalent environment executable path. Only the observed macOS arm64 installation is claimed tested here; Linux/container installation and real PostgreSQL connectivity require their own checks before use.

If a compatible wheel is unavailable, stop and record the blocker. Do not remove `--no-build`, execute a source-build backend or add an alternate registry to force progress. The documented Python bootstrap may download an official uv-managed standalone runtime; it does not compile Python or install product code.

## Replay the dependency smoke and advisory audit

After the locked wheel-only sync, this dependency probe needs no server or database:

```bash
backend/.venv/bin/python - <<'PYCODE'
import django, psycopg, uvicorn
from django.conf import settings
settings.configure(SECRET_KEY="synthetic-dependency-smoke-only", INSTALLED_APPS=["rest_framework"], USE_TZ=True)
django.setup()
from rest_framework import serializers
class Probe(serializers.Serializer):
    value = serializers.IntegerField(min_value=1)
assert Probe(data={"value": 2}).is_valid()
assert not Probe(data={"value": 0}).is_valid()
async def probe(scope, receive, send):
    pass
config = uvicorn.Config(probe, interface="asgi3", loop="asyncio", http="h11", log_config=None, lifespan="off")
config.load()
assert config.loaded and psycopg.pq.version() > 0
print(django.get_version(), psycopg.__version__, uvicorn.__version__, psycopg.pq.version())
PYCODE
```

Generate the complete fully pinned audit input directly from the reviewed lock, including platform-conditional packages. The audit utility is separate from backend runtime/dev groups:

```bash
backend/.venv/bin/python - <<'PYCODE'
from pathlib import Path
import tomllib
lock = tomllib.loads(Path("backend/uv.lock").read_text())
Path("work").mkdir(exist_ok=True)
Path("work/f1-backend-all.requirements.txt").write_text("".join(
    item["name"] + "==" + item["version"] + "\n"
    for item in lock["package"] if item["name"] != "sebaverse-backend"
))
PYCODE
export UV_TOOL_DIR="$PWD/work/uv-tools"
export UV_TOOL_BIN_DIR="$PWD/work/uv-tool-bin"
uv tool run --isolated --from pip-audit==2.10.1 --no-build --python 3.12.13 --no-python-downloads --default-index https://pypi.org/simple pip-audit --disable-pip --no-deps --requirement work/f1-backend-all.requirements.txt --format json --output work/f1-backend-audit.json --progress-spinner off
```

Review the actual JSON and exit status. `--disable-pip --no-deps` prevents the auditor from installing/resolving the scanned dependencies; exact names/versions are derived from the hashed lock. The isolated auditor itself uses reviewed official registry wheels. Its warning to hash pinned requirements does not mean a source build occurred; install integrity is supplied by the separate `uv.lock`/locked sync. Do not use an advisory scanner's optional repair operation to change pins silently.

## Verification and limits

The evidence files record exact commands, exits, metadata sources, lock hashes, installed notice hashes and audit results:

- [Official metadata inspected before install](../development/evidence/f1-backend-registry.json).
- [License and notice inventory](../third-party/backend-licenses.json).
- [Backend smoke and consistency evidence](../development/evidence/f1-backend-checks.json).
- [Vulnerability audit result](../development/evidence/f1-backend-audit.json) and [auditor execution](../development/evidence/f1-backend-audit-run.json).

Dependency smoke checks verify imports/versions, DRF serializer compatibility, Uvicorn configuration and the binary libpq binding. They do not prove an app, DB connection, authentication, tenant isolation, streaming, learner grading or educational correctness. `pytest --version` verifies tooling availability, not a passing product suite.

The isolated pip-audit tool is pinned separately and scans every locked third-party Python package, including platform-conditional graph entries, without installing those packages for dependency resolution. It does not scan the OS, CPython, bundled native library CVEs or arbitrary source code. Read the actual result and limitations; absence of published Python advisories is not a security certification. Unknown/failed required security checks or reported unresolved findings keep F1 unpassed.

Psycopg and psycopg-binary declare LGPL-3.0-only in their metadata. The observed wheel exposes its LGPL license but does not establish a complete separate native-library notice/version inventory. Preserve package and bundled-library notices, and resolve redistribution obligations for the actual image/distribution before release. This inventory records evidence; it is not legal clearance. No native source code is modified or vendored here.

F1 passing is recorded by the phase owner after independent review of all backend, web, parser/toolchain and shared checks. Nothing in this README advances F2 automatically or approves paid calls, deployment, external sends or real-minor use.
