"""Run only the reviewed Linux/amd64 ephemeral PostgreSQL integration slice."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import secrets
import subprocess
import sys
import uuid
import time

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def verify_preuse(root=ROOT):
    """Read-only gate replay. No Docker, DB connection, scanner or download."""
    root = Path(root).resolve()
    directory = root / "work/f2-security"
    stored = json.loads((directory / "preuse-result.json").read_text())
    if stored.get("schema_version") != 2 or stored.get("status") != "pass" or stored.get("errors") != []:
        raise ValueError("Native/image pre-use evidence has not passed")
    when = datetime.fromisoformat(stored["created_at_utc"].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    if when.tzinfo is None or not now - timedelta(days=1) <= when <= now + timedelta(minutes=5):
        raise ValueError("Native/image pre-use evidence expired")
    inputs = stored.get("input_hashes")
    if not isinstance(inputs, dict) or not inputs:
        raise ValueError("Pre-use evidence has no complete input binding")
    for filename, expected in inputs.items():
        path = Path(filename)
        if expected is None:
            if path.exists():
                raise ValueError("Pre-use policy/review presence changed; rerun review")
        elif not path.is_file() or sha256(path) != expected:
            raise ValueError("Pre-use evidence/policy/native bytes changed; rerun review")
    spec = importlib.util.spec_from_file_location("sebaverse_preuse_checker", root / "tools/security/check_reports.py")
    if spec is None or spec.loader is None:
        raise ValueError("Pre-use validator is unavailable")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    current = checker.evaluate(directory, root=root, now=now)
    if current.get("status") != "pass" or current.get("input_hashes") != inputs:
        raise ValueError("Current native/image source coverage no longer passes; rerun review")
    for key in ("image_reference", "platform_manifest_digest", "reports", "policy", "scope"):
        if stored.get(key) != current.get(key):
            raise ValueError("Pre-use identity/findings differ from the approved snapshot")
    pin = json.loads((root / "infra/images.lock.json").read_text())["postgres"]
    if stored["image_reference"] != pin["reference"]:
        raise ValueError("Pre-use image pin changed")
    return stored, pin


def run(command, **kwargs):
    kwargs.setdefault("timeout", 120)
    return subprocess.run(command, cwd=ROOT, check=True, text=True, **kwargs)


def main():
    # Gate verification happens before allocating a password, starting a container,
    # importing Psycopg or asking a client to contact PostgreSQL.
    if not sys.platform.startswith("linux"):
        raise SystemExit("Reviewed system-libpq integration targets Linux; this platform remains gated")
    try:
        report, pin = verify_preuse()
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit("PostgreSQL remains gated: " + str(error)) from None
    suffix = uuid.uuid4().hex[:10]
    name = "sebaverse-f2-" + suffix
    password = secrets.token_urlsafe(24)
    envdir = ROOT / ".local/f2"
    envdir.mkdir(parents=True, exist_ok=True)
    envfile = envdir / (suffix + ".env")
    # Create secrets with restrictive permissions atomically, not after a write.
    fd = os.open(envfile, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as output:
        output.write("POSTGRES_DB=sebaverse_f2\nPOSTGRES_USER=postgres\nPOSTGRES_PASSWORD=" + password + "\nPGDATA=/tmp/pgdata\n")
    container = None
    result = None
    try:
        container = run(["docker", "run", "-d", "--name", name, "--label", "dev.sebaverse.task=DEV-006",
                         "--user", "postgres", "--read-only", "--tmpfs", "/tmp:rw,mode=1777",
                         "--tmpfs", "/var/run/postgresql:rw,mode=3777", "--cap-drop", "ALL",
                         "--security-opt", "no-new-privileges", "--publish", "127.0.0.1::5432",
                         "--env-file", str(envfile), "--platform", "linux/amd64", pin["reference"],
                         "postgres", "-c", "unix_socket_directories=/tmp"], capture_output=True).stdout.strip()
        if not container:
            raise RuntimeError("Task-owned PostgreSQL container ID missing")
        ready = False
        for _ in range(60):
            probe = subprocess.run(["docker", "exec", container, "pg_isready", "-U", "postgres", "-d", "sebaverse_f2"], capture_output=True, timeout=5)
            if probe.returncode == 0:
                ready = True
                break
            time.sleep(1)
        if not ready:
            raise RuntimeError("Ephemeral PostgreSQL did not become ready")
        port = run(["docker", "port", container, "5432/tcp"], capture_output=True).stdout.strip().split(":")[-1]
        if not port.isdigit() or not 1 <= int(port) <= 65535:
            raise RuntimeError("Ephemeral PostgreSQL loopback port is invalid")
        environment = dict(os.environ, SEBAVERSE_ENV="local", DJANGO_DEBUG="1", PSYCOPG_IMPL="python",
                           POSTGRES_DB="sebaverse_f2", POSTGRES_USER="postgres", POSTGRES_PASSWORD=password,
                           POSTGRES_HOST="127.0.0.1", POSTGRES_PORT=port, SEBAVERSE_TEST_POSTGRES="1")
        run([str(ROOT / "backend/.venv/bin/python"), "-m", "pytest", "backend/tests/test_postgres_integration.py", "-q"], env=environment)
        result = {"status": "pass", "task": "DEV-006", "database": "PostgreSQL17 real instance",
                  "image": pin["reference"], "platform_manifest_digest": report["platform_manifest_digest"],
                  "native_preuse_report": "work/f2-security/preuse-result.json",
                  "native_preuse_sha256": sha256(ROOT / "work/f2-security/preuse-result.json"),
                  "binding": "PSYCOPG_IMPL=python with reviewed system libpq",
                  "checks": ["actual framework migrations", "server major17", "no pending migrations",
                             "synthetic session roundtrip/cleanup", "database readiness200"], "teardown": "pending"}
    finally:
        try:
            if container:
                run(["docker", "rm", "-f", "-v", container], capture_output=True)
        finally:
            envfile.unlink(missing_ok=True)
    if result is not None:
        result["teardown"] = "task-owned container/volumes removed; synthetic env removed"
        (ROOT / "work/f2-security/postgres-integration.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
