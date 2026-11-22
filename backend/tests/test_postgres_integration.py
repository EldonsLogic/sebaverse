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
    cursor.execute("SELECT ssl FROM pg_stat_ssl WHERE pid = pg_backend_pid()")
    assert cursor.fetchone() == (False,), "Synthetic connection unexpectedly negotiated TLS."
    cursor.execute("SELECT gss_authenticated, encrypted FROM pg_stat_gssapi WHERE pid = pg_backend_pid()")
    assert cursor.fetchone() == (False, False), "Synthetic connection unexpectedly used GSS."
assert connection.settings_dict["OPTIONS"]["require_auth"] == "scram-sha-256"
assert connection.settings_dict["OPTIONS"]["gssencmode"] == "disable"
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
    access_probe = subprocess.run(
        [sys.executable, "backend/tests/authorization/postgres_probe.py"], cwd=root, env=env,
        capture_output=True, text=True, timeout=60,
    )
    if access_probe.returncode:
        pytest.fail(f"Synthetic PostgreSQL authorization probe failed with exit {access_probe.returncode}; connection details withheld.")
    assert json.loads(access_probe.stdout) == {"negative_scope_cases": 120, "positive_cases": 24,
                                              "revocation_cases": 8, "constraint_cases": 3, "actor_specific_negative_cases": 8}
    resilience = subprocess.run(
        [sys.executable, "backend/tests/resilience/postgres_probe.py"], cwd=root, env=env,
        capture_output=True, text=True, timeout=90,
    )
    if resilience.returncode:
        pytest.fail(f"Synthetic PostgreSQL resilience probe failed with exit {resilience.returncode}; connection details withheld.")
    resilience_result = json.loads(resilience.stdout)
    assert resilience_result['count'] == 14 and resilience_result['provider_calls'] == 'mock-only'
    assert resilience_result['transactions_over_dispatch'] is False
    ingestion = subprocess.run(
        [sys.executable, "backend/tests/ingestion/postgres_probe.py"], cwd=root, env=env,
        capture_output=True, text=True, timeout=60,
    )
    if ingestion.returncode:
        pytest.fail(f"Synthetic PostgreSQL ingestion broker probe failed with exit {ingestion.returncode}; connection details withheld.")
    ingestion_result = json.loads(ingestion.stdout)
    assert ingestion_result['count'] == 36 and ingestion_result['injection_fixtures'] == 30
    assert {
        'retained-partial-manifest-failed-purge-and-single-refund',
        'clean-scan-after-withdrawal-does-not-dispatch-parser',
        'clean-scan-after-consent-withdrawal-does-not-dispatch-parser',
        'clean-scan-after-consent-regrant-does-not-revive-dispatch',
        'newer-dispatch-is-preserved-after-stale-scan',
        'newer-dispatch-is-preserved-after-stale-parse',
        'mutating-parser-cannot-redefine-expected-dispatch',
        'file-kind-drift-during-scan-withdraws-dispatch',
        'file-kind-drift-during-parse-withdraws-dispatch',
        'file-kind-drift-denies-review-and-private-resolution',
        'private-resolve-denies-consent-regrant-during-manifest-read',
        'private-resolve-denies-rights-expiry-during-manifest-read',
        'review-denies-grant-removal-during-manifest-read',
        'cleanup-intent-denial-and-transaction-rollback',
        'cleanup-intent-same-guardian-expired-and-reporting-withdrawals',
        'cleanup-intent-other-guardian-overlap-fences-access-without-purge',
        'cleanup-intent-last-grant-cutoff-survives-regrant-and-replay',
        'cleanup-consumer-overlap-and-regrant-preserve-exact-cohort',
        'cleanup-consumer-open-writer-does-not-starve-later-targets',
        'cleanup-consumer-partial-and-interrupted-purge-replay',
        'cleanup-consumer-stale-lease-loses-settlement-after-takeover',
        'cleanup-consumer-settlement-lock-excludes-expired-lease-claim',
    } <= set(ingestion_result['checks'])
    assert ingestion_result['actual_parser_scanner_or_sandbox'] is False
    result = json.loads(verified.stdout)
    assert result == {"migrations": "applied", "postgres_family": 17, "psycopg_impl": "python", "session_round_trip": "pass", "readiness": "ready"}
