"""Actual PostgreSQL check, opt-in only after the phase owner's native pre-use gate."""
import json
from pathlib import Path
import subprocess
import sys

import pytest


def test_postgres_integration_migrations_sessions_and_readiness(postgres_integration_environment):
    """Use the explicitly authorized local synthetic DB, never an ambient endpoint."""
    root = Path(__file__).resolve().parents[2]
    env = postgres_integration_environment
    migrated = subprocess.run(
        [sys.executable, "backend/manage.py", "migrate", "--noinput"],
        cwd=root, env=env, capture_output=True, text=True, timeout=60,
    )
    if migrated.returncode:
        pytest.fail(f"Synthetic PostgreSQL migration failed with exit {migrated.returncode}; connection details withheld.")
    probe = '''
import json, os, sys
sys.path.insert(0, "backend")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
import psycopg
assert psycopg.pq.__impl__ == "python", "Expected the reviewed system-libpq Python binding, not bundled wheel libraries."
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.contrib.sessions.backends.db import SessionStore
from django.test import Client
with connection.cursor() as cursor:
    cursor.execute("SHOW server_version_num")
    version = int(cursor.fetchone()[0])
assert 170000 <= version < 180000, "Expected the selected PostgreSQL17 family."
executor = MigrationExecutor(connection)
assert not executor.migration_plan(executor.loader.graph.leaf_nodes()), "Unapplied migrations remain."
session = SessionStore()
try:
    session["synthetic_skeleton_probe"] = True
    session.save()
    assert SessionStore(session_key=session.session_key).get("synthetic_skeleton_probe") is True
finally:
    if session.session_key:
        session.delete()
response = Client(HTTP_HOST="localhost").get("/api/v1/ready/")
assert response.status_code == 200 and response.json() == {"status": "ready"}
connection.close()
print(json.dumps({"migrations": "applied", "postgres_family": 17, "psycopg_impl": "python", "session_round_trip": "pass", "readiness": "ready"}))
'''
    verified = subprocess.run(
        [sys.executable, "-c", probe], cwd=root, env=env,
        capture_output=True, text=True, timeout=30,
    )
    if verified.returncode:
        pytest.fail(f"Synthetic PostgreSQL readiness/session probe failed with exit {verified.returncode}; connection details withheld.")
    result = json.loads(verified.stdout)
    assert result == {"migrations": "applied", "postgres_family": 17, "psycopg_impl": "python", "session_round_trip": "pass", "readiness": "ready"}
