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

## F2 local application skeleton — 12 November 2026

DEV-006 / U16 / AUTH-003 adds the actual Django ASGI skeleton below. Earlier sections preserve F1 dependency facts and evidence; they do not describe the new application's verification or advance F2. The application has health/readiness, guarded local built-client serving, standard Django sessions/CSRF middleware and safe configuration. It has no tutoring, upload, learner-authority, provider, payment or real-user features yet.

### Configuration and startup

Configuration is read from process environment; arbitrary `.env` files are not loaded automatically. Default mode is production and fails closed when its required settings are absent. The documented local startup is explicitly local and debug-enabled, with a known development-only secret fallback restricted to loopback hosts and peers. Do not expose it through a public proxy or bind it to a public interface.

| Variable | Local skeleton behavior |
|---|---|
| `SEBAVERSE_ENV` | Explicit `local` for this scope; default `production` is not deployment approval |
| `DJANGO_DEBUG` | Explicit `1` enables local development fallback; production debug is rejected |
| `DJANGO_SECRET_KEY` | Independent 50+ character key required outside explicit local debug; never log it |
| `DJANGO_ALLOWED_HOSTS` | Local defaults: localhost, 127.0.0.1 and [::1]; local non-loopback/wildcard hosts rejected |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST` | Supply all together for the approved synthetic PostgreSQL instance; local host must be exactly localhost, 127.0.0.1 or ::1; partial or remote local-mode configuration fails closed |
| `PSYCOPG_IMPL` | Must be explicitly `python` whenever local PostgreSQL is configured; use only after the separately identified/scanned system libpq chain passes the native pre-use gate |
| `POSTGRES_PORT` | Defaults to 5432 only when a complete DB configuration exists; explicit invalid ports fail |

All PostgreSQL fields absent in local mode selects Django's **dummy/unconfigured backend**, not SQLite. Actual local DB use requires `PSYCOPG_IMPL=python`, which uses a separately reviewed system libpq chain. The installed binary extra remains only for isolated F1 import compatibility; it must not supply the native implementation for F2 DB/network tests. The current macOS environment has no approved system-libpq closure, so a local DB run remains held there. Clean Linux evidence must identify the actual loaded implementation and scanned native libraries before connection. The production binding choice remains a separately reviewed future decision. Liveness works without any DB connection; readiness returns 503. Production settings require complete PostgreSQL configuration and certificate-verified TLS; this is safe configuration behavior, not an approved or tested deployment. Standard session cookies are HttpOnly and SameSite=Lax, Secure outside local mode. Unsafe requests retain CSRF protection; errors do not echo credentials, request bodies, tracebacks or framework versions.

After the frontend owner's approved build, `web/dist` is served on the same origin by the local backend. Only exact shell routes `/`, `/materials`, `/practice`, `/progress` (and their explicit trailing-slash variants) return the shell. `/assets/**` and `/brand/**` allow approved JS/CSS/image/font suffixes, plus `OFL*.txt` notices under brand. Resolved paths must stay within the correct built namespace; control characters, traversal, outside symlinks, source maps, arbitrary repository files and source/env files are denied. Unknown APIs return JSON 404 rather than HTML. Local static serving is disabled outside local mode. Built files use bounded nonstreaming responses (2 MiB per file); oversized/unreadable files return safe JSON 503. This avoids synchronous-file-iterator warnings under ASGI without adding a dependency or claiming production static hosting.

```bash
SEBAVERSE_ENV=local DJANGO_DEBUG=1 backend/.venv/bin/python backend/manage.py check
SEBAVERSE_ENV=local DJANGO_DEBUG=1 backend/.venv/bin/python -m uvicorn config.asgi:application --app-dir backend --host 127.0.0.1 --port 8000 --no-server-header --no-access-log
```

Stop the foreground server with Ctrl-C. This command does not start PostgreSQL, run migrations, contact a provider or enable real data. Missing `web/dist/index.html` returns a safe 503. Build the client only after its applicable native-tool pre-use checks; do not execute a native binary or pull/start a container merely because a manifest exists.

### Health and response contract

- `GET /api/v1/health/` → `200 {"status":"ok"}`. Liveness does not query the DB or write a session.
- `GET /api/v1/ready/` → `200 {"status":"ready"}` only after a real `SELECT 1`; unconfigured/unavailable DB returns generic JSON 503 without connection detail.
- Non-GET health/readiness requests are denied; unsafe requests without CSRF may be rejected first with JSON 403. No state-changing action is exposed by a health route.
- Responses include no-store, nosniff, frame denial, no-referrer and same-origin CSP. Camera/microphone/geolocation are currently disabled; later voice permission behavior needs its own reviewed phase.
- Default logs contain severity/logger category only. Request/exception text, credentials and bodies are excluded from the formatter. This is a small privacy-preserving foundation, not the later complete observability/audit implementation.

### Actual DB-free verification and gated PostgreSQL check

The suite uses authored synthetic values and a dummy backend. It removes ambient PostgreSQL credentials for unit tests and mocks the readiness connection path explicitly. These checks do not establish a real PostgreSQL migration/readiness pass:

```bash
SEBAVERSE_ENV=local DJANGO_DEBUG=1 backend/.venv/bin/python -m pytest backend/tests -q -k 'not postgres_integration'
SEBAVERSE_ENV=local DJANGO_DEBUG=1 backend/.venv/bin/python backend/manage.py check
```

Observed during this backend work: **83 DB-free tests passed**, one separate PostgreSQL integration case deselected; Django system checks reported no issues. Coverage includes configuration failure modes, safe host/peer/method/error behavior, CSRF, response/log privacy, built routes/assets and traversal/symlink/source-file protections. The actual browser build, container/native closure, PostgreSQL and migration evidence are recorded by the phase owner separately; a mocked cursor is not a real database test.

**Only after the phase owner's required native/image notice/version/security checks and local synthetic DB startup are complete**, supply the explicit loopback PostgreSQL environment and opt in:

```bash
SEBAVERSE_ENV=local DJANGO_DEBUG=1 SEBAVERSE_TEST_POSTGRES=1 backend/.venv/bin/python -m pytest backend/tests/test_postgres_integration.py -q
```

After its explicit phase-owner opt-in and loopback checks, that integration case sets `PSYCOPG_IMPL=python` in its subprocess environment and asserts the actual loaded implementation. It invokes the real Django migrations against the supplied synthetic DB, verifies the PostgreSQL17 family and no pending migrations, creates/reads/deletes one synthetic Django session, and checks readiness 200. It rejects non-loopback endpoints and does not log credentials. The command is a test scaffold, **not a claim it already ran**. Missing opt-in skips it; missing required credentials fails it. Root records its actual result before F2 can pass. No PostgreSQL connection/migration was performed by the backend builder while that native pre-use gate remained held.
