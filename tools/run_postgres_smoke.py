"""Run only the reviewed Linux/amd64 ephemeral PostgreSQL integration slice."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import re
import shutil
import secrets
import subprocess
import sys
import uuid
import time
import tarfile
import socket
import socketserver
import threading
import select
import ipaddress

ROOT = Path(__file__).resolve().parents[1]


LOADER_OVERRIDES = ("LD_LIBRARY_PATH", "LD_PRELOAD", "LD_AUDIT")


def validate_loader_environment(environment=None):
    """Recheck loader redirection before accepting reviewed native bindings."""
    values = os.environ if environment is None else environment
    if any(values.get(name) for name in LOADER_OVERRIDES) or any(
        name.startswith("DYLD_") and value for name, value in values.items()
    ):
        raise ValueError("Dynamic-loader overrides must be absent before PostgreSQL native use.")


def sha256(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def verify_preuse(root=ROOT):
    """Read-only gate replay. No Docker, DB connection, scanner or download."""
    validate_loader_environment()
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
    execution_scope = "synthetic-ci" if os.environ.get("SEBAVERSE_SECURITY_SCOPE") == "synthetic-ci" else "standard"
    current = checker.evaluate(directory, root=root, now=now, execution_scope=execution_scope)
    if current.get("status") != "pass" or current.get("input_hashes") != inputs:
        raise ValueError("Current native/image source coverage no longer passes; rerun review")
    for key in ("image_reference", "platform_manifest_digest", "image_runtime", "reports", "policy", "scope", "execution_scope", "temporary_exception"):
        if stored.get(key) != current.get(key):
            raise ValueError("Pre-use identity/findings differ from the approved snapshot")
    pin = json.loads((root / "infra/images.lock.json").read_text())["postgres"]
    runtime = stored.get("image_runtime")
    expected_source = runtime["reference"] if runtime else pin["reference"]
    if stored["image_reference"] != expected_source:
        raise ValueError("Pre-use image source changed")
    return stored, pin


def run(command, **kwargs):
    kwargs.setdefault("timeout", 120)
    return subprocess.run(command, cwd=ROOT, check=True, text=True, **kwargs)


def load_derived_image(runtime, root=ROOT, executor=None):
    """Static import only; refuse drift before any image/container execution."""
    root = Path(root).resolve()
    execute = executor or run
    if runtime.get("type") != "derived-oci" or not re.fullmatch(r"sha256:[0-9a-f]{64}", runtime.get("config_digest", "")):
        raise ValueError("Derived import authority/config identity missing")
    archive = root / "work/f2-security/postgres-derived.oci.tar"
    if runtime.get("archive_path") != str(archive.relative_to(root)) or sha256(archive) != runtime.get("archive_sha256"):
        raise ValueError("Derived archive changed before Docker import")
    with tarfile.open(archive, "r:*") as content:
        name = "blobs/sha256/" + runtime["platform_manifest_digest"].split(":", 1)[1]
        member = content.getmember(name)
        if not member.isfile() or member.size > 4 * 1024 * 1024:
            raise ValueError("Imported manifest metadata is invalid")
        data = content.extractfile(member).read()
        if "sha256:" + hashlib.sha256(data).hexdigest() != runtime["platform_manifest_digest"] or json.loads(data)["config"]["digest"] != runtime["config_digest"]:
            raise ValueError("Imported manifest/config linkage changed")
        index = content.extractfile("index.json").read(4 * 1024 * 1024 + 1)
        if "sha256:" + hashlib.sha256(index).hexdigest() != runtime.get("index_digest"):
            raise ValueError("Imported index identity changed")
    execute(["docker", "image", "load", "--input", str(archive)], capture_output=True)
    # Docker's containerd store addresses images by target (manifest/index)
    # digest, unlike the classic store's config-digest image ID. Each candidate
    # below is an immutable digest independently verified from this OCI archive.
    candidates = [runtime.get("platform_manifest_digest"), runtime.get("index_digest")]
    failures = []
    for target in dict.fromkeys(candidates):
        if not isinstance(target, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", target):
            raise ValueError("Derived imported target digest missing")
        try:
            response = execute(["docker", "image", "inspect", target, "--format", "{{json .}}"], capture_output=True)
        except subprocess.CalledProcessError as error:
            failures.append({"target": target, "lookup_exit_code": error.returncode})
            continue
        identity = json.loads(response.stdout)
        if not (identity.get("Id") == target and identity.get("Descriptor", {}).get("digest") == target and
                identity.get("Os") == "linux" and identity.get("Architecture") == "amd64" and
                identity.get("Config", {}).get("User") == "postgres" and
                identity.get("RootFS", {}).get("Layers") == runtime.get("rootfs_diff_ids")):
            raise ValueError("Docker imported manifest/platform/rootfs differs from scanned OCI artifact")
        if sha256(archive) != runtime["archive_sha256"]:
            raise ValueError("Derived archive changed during Docker import")
        evidence = {"status": "static_import_verified_not_started", "target_digest": target,
                    "platform_manifest_digest": runtime["platform_manifest_digest"],
                    "config_digest_verified_from_oci": runtime["config_digest"],
                    "archive_sha256": runtime["archive_sha256"], "docker_inspect": identity}
        folder = root / "work/f2-security"
        (folder / "docker-import.json").write_text(json.dumps(evidence, indent=2) + "\n")
        return target
    raise ValueError("Docker did not resolve either verified OCI target digest: " + json.dumps(failures))


class LoopbackRelay:
    """Owned localhost TCP relay to one verified internal-network endpoint."""
    def __init__(self, address, port):
        ip = ipaddress.ip_address(address)
        if ip.version != 4 or not ip.is_private or ip.is_unspecified or not 1 <= int(port) <= 65535:
            raise ValueError("Relay target must be an owned private IPv4 endpoint")
        self.target = (str(ip), int(port))
        self.stop = threading.Event()
        self.lock = threading.Lock()
        self.connections = set()
        relay = self
        class Handler(socketserver.BaseRequestHandler):
            def handle(self):
                with socket.create_connection(relay.target, timeout=5) as remote:
                    pair = (self.request, remote)
                    with relay.lock:
                        relay.connections.add(pair)
                    try:
                        while not relay.stop.is_set():
                            readable, _, _ = select.select(pair, [], [], .2)
                            for source in readable:
                                data = source.recv(65536)
                                if not data:
                                    return
                                (remote if source is self.request else self.request).sendall(data)
                    except OSError:
                        if not relay.stop.is_set():
                            raise
                    finally:
                        with relay.lock:
                            relay.connections.discard(pair)
        class Server(socketserver.ThreadingTCPServer):
            daemon_threads = True
            allow_reuse_address = False
        self.server = Server(("127.0.0.1", 0), Handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": .1}, daemon=True)
        self.thread.start()

    def close(self):
        self.stop.set()
        with self.lock:
            connections = list(self.connections)
        for pair in connections:
            for stream in pair:
                try:
                    stream.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


def internal_database_address(container_networks, network_name, network):
    endpoint = container_networks.get(network_name, {})
    address = ipaddress.ip_address(endpoint.get("IPAddress", ""))
    subnets = [ipaddress.ip_network(row["Subnet"]) for row in network.get("IPAM", {}).get("Config", []) if row.get("Subnet")]
    if (network.get("Internal") is not True or endpoint.get("NetworkID") != network.get("Id") or
            address.version != 4 or not address.is_private or address.is_loopback or
            not any(address in subnet for subnet in subnets if subnet.version == 4)):
        raise ValueError("Database endpoint does not belong to the verified internal network")
    return str(address)


def client_environment(root, suffix, password, port):
    """Explicit synthetic connection environment; no ambient service/plugin inputs."""
    root = Path(root).resolve()
    if not re.fullmatch(r"[0-9a-f]{10}", suffix) or not str(port).isdigit() or not 1 <= int(port) <= 65535:
        raise ValueError("Invalid task-owned synthetic environment identity")
    home = root / ".local/f2" / (suffix + "-home")
    home.mkdir(parents=True, mode=0o700, exist_ok=False)
    empty = home / "empty-config"
    empty.mkdir(mode=0o700)
    return {"PATH": os.defpath, "HOME": str(home), "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
            "PYTHONUTF8": "1", "SEBAVERSE_ENV": "local", "DJANGO_DEBUG": "1", "PSYCOPG_IMPL": "python",
            "POSTGRES_DB": "sebaverse_f2", "POSTGRES_USER": "postgres", "POSTGRES_PASSWORD": password,
            "POSTGRES_HOST": "127.0.0.1", "POSTGRES_PORT": str(port), "SEBAVERSE_TEST_POSTGRES": "1",
            "PGSYSCONFDIR": str(empty), "LDAPNOINIT": "1", "LDAPCONF": "/dev/null", "LDAPRC": "/dev/null",
            "KRB5_CONFIG": "/dev/null", "KRB5_KTNAME": "FILE:/dev/null", "KRB5CCNAME": "FILE:/dev/null",
            "SASL_PATH": str(empty), "OPENSSL_CONF": "/dev/null", "OPENSSL_MODULES": str(empty)}


def cleanup_owned_resources(relay, container, network, envfile, home, executor=None):
    """Attempt every task-owned cleanup even if an earlier teardown action fails."""
    execute = executor or run
    actions = []
    if relay:
        actions.append(("relay", relay.close))
    if container:
        actions.append(("container", lambda: execute(["docker", "rm", "-f", "-v", container], capture_output=True)))
    if network:
        actions.append(("network", lambda: execute(["docker", "network", "rm", network], capture_output=True)))
    actions.append(("credential_file", lambda: envfile.unlink(missing_ok=True)))
    if home.exists():
        actions.append(("client_home", lambda: shutil.rmtree(home)))
    errors = []
    for label, action in actions:
        try:
            action()
        except Exception as error:
            errors.append({"step": label, "error_type": type(error).__name__})
    return errors


def main():
    # Gate verification happens before allocating a password, starting a container,
    # importing Psycopg or asking a client to contact PostgreSQL.
    if not sys.platform.startswith("linux"):
        raise SystemExit("Reviewed system-libpq integration targets Linux; this platform remains gated")
    try:
        report, pin = verify_preuse()
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit("PostgreSQL remains gated: " + str(error)) from None
    runtime = report.get("image_runtime")
    if runtime and os.environ.get("GITHUB_ACTIONS") != "true":
        raise SystemExit("Derived F2 runtime authority is restricted to the disposable CI runner")
    suffix = uuid.uuid4().hex[:10]
    name = "sebaverse-f2-" + suffix
    password = secrets.token_urlsafe(24)
    envdir = ROOT / ".local/f2"
    envdir.mkdir(parents=True, exist_ok=True)
    envfile = envdir / (suffix + ".env")
    # Create secrets with restrictive permissions atomically, not after a write.
    fd = os.open(envfile, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as output:
        output.write("POSTGRES_DB=sebaverse_f2\nPOSTGRES_USER=postgres\nPOSTGRES_PASSWORD=" + password + "\nPGDATA=/tmp/pgdata\nPOSTGRES_HOST_AUTH_METHOD=scram-sha-256\n")
    container = None
    network = None
    relay = None
    result = None
    try:
        image = load_derived_image(runtime) if runtime else pin["reference"]
        network = "sebaverse-f2-net-" + suffix
        run(["docker", "network", "create", "--internal", "--driver", "bridge", "--label", "dev.sebaverse.task=DEV-006", network], capture_output=True)
        net = json.loads(run(["docker", "network", "inspect", network, "--format", "{{json .}}"], capture_output=True).stdout)
        if net.get("Internal") is not True or net.get("Labels", {}).get("dev.sebaverse.task") != "DEV-006":
            raise RuntimeError("Synthetic PostgreSQL network is not task-owned/internal")
        container = run(["docker", "run", "-d", "--name", name, "--pull=never", "--network", network, "--label", "dev.sebaverse.task=DEV-006",
                         "--user", "postgres", "--read-only", "--memory", "512m", "--pids-limit", "128", "--cpus", "1", "--tmpfs", "/tmp:rw,mode=1777",
                         "--tmpfs", "/var/run/postgresql:rw,mode=3777", "--cap-drop", "ALL",
                         "--security-opt", "no-new-privileges",
                         "--env-file", str(envfile), "--platform", "linux/amd64", image,
                         "postgres"], capture_output=True).stdout.strip()
        if not container:
            raise RuntimeError("Task-owned PostgreSQL container ID missing")
        ready = False
        for _ in range(60):
            probe = subprocess.run(["docker", "exec", container, "pg_isready", "-h", "127.0.0.1", "-U", "postgres", "-d", "sebaverse_f2"], capture_output=True, timeout=5)
            if probe.returncode == 0:
                ready = True
                break
            time.sleep(1)
        if not ready:
            raise RuntimeError("Ephemeral PostgreSQL did not become ready")
        endpoints = json.loads(run(["docker", "inspect", container, "--format", "{{json .NetworkSettings.Networks}}"], capture_output=True).stdout)
        address = internal_database_address(endpoints, network, net)
        relay = LoopbackRelay(address, 5432)
        port = str(relay.port)
        environment = client_environment(ROOT, suffix, password, port)
        run([str(ROOT / "backend/.venv/bin/python"), "-m", "pytest", "backend/tests/test_postgres_integration.py", "-q"], env=environment)
        result = {"status": "pass", "task": "DEV-006", "database": "PostgreSQL17 real instance",
                  "image": image, "source_reference": report["image_reference"], "platform_manifest_digest": report["platform_manifest_digest"],
                  "network": "task-owned internal Docker bridge; verified endpoint exposed only through owned127.0.0.1 relay",
                  "native_preuse_report": "work/f2-security/preuse-result.json",
                  "native_preuse_sha256": sha256(ROOT / "work/f2-security/preuse-result.json"),
                  "binding": "PSYCOPG_IMPL=python with reviewed system libpq",
                  "checks": ["actual framework migrations", "server major17", "no pending migrations",
                             "synthetic session roundtrip/cleanup", "database readiness200"], "teardown": "pending"}
    finally:
        primary_failure = sys.exc_info()[0] is not None
        cleanup_errors = cleanup_owned_resources(relay, container, network, envfile, envdir / (suffix + "-home"))
        cleanup_report = {"status": "fail" if cleanup_errors else "pass", "task": "DEV-006",
                          "errors": cleanup_errors, "scope": "Only task-owned relay/container/network/credential/home cleanup attempted"}
        (ROOT / "work/f2-security/postgres-teardown.json").write_text(json.dumps(cleanup_report, indent=2) + "\n")
        if cleanup_errors and not primary_failure:
            raise RuntimeError("Task-owned teardown failed; inspect postgres-teardown.json")
    if result is not None:
        result["teardown"] = "task-owned relay/container/volumes/internal network removed; synthetic env removed; static imported image cache remains only on disposable runner"
        (ROOT / "work/f2-security/postgres-integration.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
