import os
from pathlib import Path
import sys

import django
import pytest
from django.test import Client

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("SEBAVERSE_ENV", "local")
os.environ.setdefault("DJANGO_DEBUG", "1")
os.environ.setdefault("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
# This suite must not inherit an ambient database credential or open a connection.
_DATABASE_ENV = {}
for name in ("POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST", "POSTGRES_PORT"):
    if name in os.environ:
        _DATABASE_ENV[name] = os.environ.pop(name)
django.setup()


@pytest.fixture
def client():
    return Client(HTTP_HOST="localhost")


@pytest.fixture
def postgres_integration_environment():
    if os.environ.get("SEBAVERSE_TEST_POSTGRES") != "1":
        pytest.skip("PostgreSQL integration requires the phase owner's completed native pre-use gate and explicit opt-in.")
    if not all(_DATABASE_ENV.get(name) for name in ("POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST")):
        pytest.fail("Explicit synthetic PostgreSQL environment is incomplete.")
    if _DATABASE_ENV["POSTGRES_HOST"] not in {"localhost", "127.0.0.1", "::1"}:
        pytest.fail("F2 integration permits only an explicitly authorized loopback PostgreSQL endpoint.")
    return {**os.environ, **_DATABASE_ENV, "SEBAVERSE_ENV": "local", "DJANGO_DEBUG": "1", "DJANGO_ALLOWED_HOSTS": "localhost,127.0.0.1,[::1]", "PSYCOPG_IMPL": "python"}
