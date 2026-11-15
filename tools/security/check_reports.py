"""Validate pinned scanner evidence before native PostgreSQL use; never start a DB.

The JSON contracts follow Syft 1.57.1 (schema 16.1.13) and Grype 0.121.3.
A capture receipt binds actual scanner invocations to the exact input/output bytes.
This detects stale/incomplete evidence; it is not cryptographic attestation of CI.
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
VERSIONS = {"syft": "1.57.1", "grype": "0.121.3"}
SYFT_SCHEMA = "16.1.13"
REPORT_INPUTS = {
    "image-cves.json": "image-sbom.json",
    "system-native-cves.json": "system-native-sbom.json",
    "postgres-core-cves.json": "postgres-core.cdx.json",
}
REQUIRED = ["tools.json", "kev.json", "system-native.json", "image-sbom.json",
            "system-native-sbom.json", "postgres-core.cdx.json", *REPORT_INPUTS,
            "scan-execution.json"]
POLICY_FILES = ["infra/images.lock.json", "tools/security/check_reports.py",
                "tools/security/bootstrap.py", "tools/security/native_chain.py",
                "tools/security/postgres_core.py", "tools/run_postgres_smoke.py"]
HEX = re.compile(r"[0-9a-f]{64}")
MISSING = object()


def sha256(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def mapping(value, label):
    require(isinstance(value, dict), label + " must be an object")
    return value


def text(value, label):
    require(isinstance(value, str) and bool(value.strip()), label + " must be a nonempty string")
    return value


def timestamp(value, label):
    try:
        result = datetime.fromisoformat(text(value, label).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        raise ValueError(label + " must be an RFC3339 timestamp") from None
    require(result.tzinfo is not None, label + " must include timezone")
    return result.astimezone(timezone.utc)


def fresh(value, label, now, maximum):
    result = timestamp(value, label)
    require(now - maximum <= result <= now + timedelta(minutes=5), label + " is stale or in the future")
    return result


def digest(value, label):
    require(isinstance(value, str) and bool(HEX.fullmatch(value)), label + " must be SHA-256")
    return value


def file_digest(value, expected, label):
    path = Path(value)
    require(path.is_file(), label + " is missing")
    require(sha256(path) == digest(expected, label), label + " changed since inventory")
    return path


def resolved_path(value, root):
    path = Path(text(value, "source path"))
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def findings(report):
    """Missing/null/wrong-typed matches is never equivalent to a clean scan."""
    mapping(report, "Grype report")
    require(isinstance(report.get("matches"), list), "Grype matches must be an explicit array")
    if "ignoredMatches" in report:
        require(isinstance(report["ignoredMatches"], list), "ignoredMatches must be an array")
        require(not report["ignoredMatches"], "Suppressed/ignored findings are forbidden")
    return report["matches"]


def pin_platform(pin):
    require(isinstance(pin.get("platforms"), list), "Image platform pins missing")
    rows = [p for p in pin["platforms"] if p.get("platform") == {"architecture": "amd64", "os": "linux"}]
    require(len(rows) == 1, "One exact linux/amd64 image pin is required")
    selected = rows[0]
    for value in (pin.get("index_digest"), selected.get("digest")):
        require(isinstance(value, str) and value.startswith("sha256:") and HEX.fullmatch(value[7:]), "Malformed image digest")
    require(pin.get("reference") == "docker.io/library/postgres@" + pin["index_digest"], "Image reference/index mismatch")
    require(re.fullmatch(r"17\.\d+(?:\.\d+)?", str(selected.get("version", ""))) is not None, "PostgreSQL supplier version missing or not major17")
    return selected


def image_source(metadata, pin, selected):
    mapping(metadata, "Image metadata")
    require(metadata.get("manifestDigest") == selected["digest"], "Image SBOM/report does not identify pinned platform manifest")
    require(metadata.get("architecture") == "amd64" and metadata.get("os") == "linux", "Image architecture/OS mismatch")
    user = metadata.get("userInput", "")
    for prefix in ("registry:", "docker:"):
        if isinstance(user, str) and user.startswith(prefix):
            user = user[len(prefix):]
    repos = metadata.get("repoDigests", [])
    require(isinstance(repos, list), "Image repoDigests malformed")
    require(user == pin["reference"] or pin["reference"] in repos, "Image source is not bound to the selected index reference")


def syft_sbom(document, label):
    mapping(document, label)
    descriptor = mapping(document.get("descriptor"), label + " descriptor")
    require(descriptor.get("name") == "syft" and descriptor.get("version") == VERSIONS["syft"], label + " scanner identity/version mismatch")
    schema = mapping(document.get("schema"), label + " schema")
    require(schema.get("version") == SYFT_SCHEMA, label + " unsupported Syft JSON schema")
    require(schema.get("url") == f"https://raw.githubusercontent.com/anchore/syft/main/schema/json/schema-{SYFT_SCHEMA}.json", label + " schema URL mismatch")
    artifacts = document.get("artifacts")
    require(isinstance(artifacts, list) and bool(artifacts), label + " package identification missing")
    identities = {}
    for artifact in artifacts:
        mapping(artifact, label + " artifact")
        key = tuple(text(artifact.get(k), label + " artifact " + k) for k in ("id", "name", "version", "type"))
        require(key[0] not in identities, label + " duplicate artifact ID")
        identities[key[0]] = key[1:]
    source = mapping(document.get("source"), label + " source")
    text(source.get("id"), label + " source ID")
    mapping(source.get("metadata"), label + " source metadata")
    distro = mapping(document.get("distro"), label + " distro")
    text(distro.get("id"), label + " distro ID")
    text(distro.get("versionID"), label + " distro version")
    return identities


def os_release(path):
    values = {}
    for line in Path(path).read_text().splitlines():
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key] = value.strip().strip('"').strip("'")
    require(values.get("ID") and values.get("VERSION_ID"), "Native OS identity/version missing")
    return values


def scan_database(descriptor, now):
    require(descriptor.get("name") == "grype" and descriptor.get("version") == VERSIONS["grype"], "Grype identity/version mismatch")
    db = mapping(descriptor.get("db"), "Grype database")
    status = mapping(db.get("status"), "Grype database status")
    require(status.get("valid") is True and status.get("error") in (None, ""), "Grype DB is invalid or has an error")
    require(re.fullmatch(r"v?6(?:\.\d+){0,2}", str(status.get("schemaVersion", ""))) is not None, "Grype database schema is unsupported")
    fresh(status.get("built"), "Grype DB build", now, timedelta(days=5))
    require(isinstance(db.get("providers"), dict) and bool(db["providers"]), "Grype provider DB coverage missing")
    for name, provider in db["providers"].items():
        text(name, "Grype provider name")
        mapping(provider, "Grype provider metadata")
        text(provider.get("input"), "Grype provider input")
        fresh(provider.get("captured"), "Grype provider capture", now, timedelta(days=5))
    configuration = descriptor.get("configuration", {})
    mapping(configuration, "Grype configuration")
    for key in ("exclude", "only-fixed", "only-notfixed", "ignore-states", "ignore-wontfix"):
        require(configuration.get(key) in (None, False, [], ""), "Grype filtering/suppression configured: " + key)
    ignores = configuration.get("ignore", [])
    require(isinstance(ignores, list), "Grype ignore configuration malformed")
    defaults = {("kernel-headers", "rpm", "kernel"), ("linux(-.*)?-headers-.*", "deb", "linux.*"),
                ("linux-libc-dev", "deb", "linux"), ("linux-kbuild-.*", "deb", "linux.*")}
    require(len(ignores) <= len(defaults), "User-defined Grype suppression rules are forbidden")
    for rule in ignores:
        mapping(rule, "Grype ignore rule")
        package = mapping(rule.get("package"), "Grype ignore package")
        require((package.get("name"), package.get("type"), package.get("upstream-name")) in defaults,
                "User-defined Grype suppression rule is forbidden")
        require(rule.get("match-type") == "exact-indirect-match" and
                all(value in (None, "", False) for key, value in rule.items() if key not in {"package", "match-type"}) and
                all(value in (None, "") for key, value in package.items() if key not in {"name", "type", "upstream-name"}),
                "Grype suppression differs from pinned upstream defaults")
    return db


def tool_inventory(directory):
    tools = read_json(directory / "tools.json")
    require(isinstance(tools, list) and len(tools) == len(VERSIONS), "Security tool inventory must contain exactly the pinned tools")
    for name, version in VERSIONS.items():
        rows = [row for row in tools if isinstance(row, dict) and row.get("name") == name]
        require(len(rows) == 1 and rows[0].get("version") == version, "Pinned security tool inventory mismatch: " + name)
        digest(rows[0].get("archive_sha256"), name + " archive hash")
        require(rows[0].get("platform") == "linux_amd64", "Pre-use evidence requires Linux amd64 tools")
        require(rows[0].get("source") == f"https://github.com/anchore/{name}/releases/download/v{version}/{name}_{version}_linux_amd64.tar.gz", "Security tool source mismatch")
        require(isinstance(rows[0].get("notices"), list) and bool(rows[0]["notices"]), name + " notices missing")
    return tools


def capture_scans(directory, root):
    """Actual scanner execution only; safe to run while PostgreSQL remains gated."""
    import os
    directory.mkdir(parents=True, exist_ok=True)
    tool_inventory(directory)
    binary = root / ".local/security-tools/grype"
    version = subprocess.run([str(binary), "version", "-o", "json"], cwd=root, text=True, capture_output=True, timeout=30, check=True)
    require(read_version(version.stdout) == VERSIONS["grype"], "Executable Grype version does not match pin")
    receipt = {"schema_version": 1, "scanner_version": VERSIONS["grype"], "scanner_sha256": sha256(binary), "scans": []}
    environment = dict(os.environ, GRYPE_TIMESTAMP="true")
    config = directory / "grype-empty.yaml"
    config.write_text("{}\n")
    receipt["configuration_sha256"] = sha256(config)
    receipt_path = directory / "scan-execution.json"
    receipt_path.unlink(missing_ok=True)
    for report_name, input_name in REPORT_INPUTS.items():
        source = directory / input_name
        before = sha256(source)
        output = directory / report_name
        output.unlink(missing_ok=True)
        command = [str(binary), "--config", str(config), "sbom:" + str(source), "-o", "json", "--file", str(output), "--quiet"]
        started = datetime.now(timezone.utc).isoformat()
        result = subprocess.run(command, cwd=root, env=environment, text=True, capture_output=True, timeout=600)
        require(result.returncode == 0 and output.is_file(), "Actual Grype scan failed: " + report_name)
        require(sha256(source) == before, "SBOM changed during scan: " + input_name)
        receipt["scans"].append({"report": report_name, "input": input_name, "input_sha256": before,
                                 "report_sha256": sha256(output), "exit_code": result.returncode,
                                 "started_at_utc": started, "finished_at_utc": datetime.now(timezone.utc).isoformat(),
                                 "command": command})
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print("Actual pinned scanner receipts captured; PostgreSQL not executed.")


def read_version(output):
    value = mapping(json.loads(output), "Grype version")
    return value.get("version")


def evaluate(directory, root=None, now=None):
    root = Path(root or ROOT).resolve()
    directory = Path(directory).resolve()
    now = now or datetime.now(timezone.utc)
    errors, reports, hashes = [], [], {}
    pin, selected = {}, {}

    def bind(path, expected=MISSING):
        path = Path(path).resolve()
        if expected is not MISSING:
            file_digest(path, expected, str(path))
        require(path.is_file(), "Required evidence is missing: " + str(path))
        actual = sha256(path)
        hashes[str(path)] = actual
        return actual

    try:
        for name in REQUIRED:
            bind(directory / name)
        for path in POLICY_FILES:
            bind(root / path)
        reviews_path = root / "infra/security-reviewed-findings.json"
        if reviews_path.exists():
            bind(reviews_path)
            reviews = mapping(read_json(reviews_path), "Finding reviews")
            require(isinstance(reviews.get("findings"), list), "Reviewed findings must be an array")
        else:
            hashes[str(reviews_path.resolve())] = None
            reviews = {"findings": []}
        pin = mapping(read_json(root / "infra/images.lock.json").get("postgres"), "Image pin")
        selected = pin_platform(pin)
        tools = tool_inventory(directory)
        for tool in tools:
            for notice in tool["notices"]:
                bind(resolved_path(notice["path"], root), notice["sha256"])
        binary = root / ".local/security-tools/grype"
        binary_hash = bind(binary)
        syft_binary_hash = bind(root / ".local/security-tools/syft")
        receipt = mapping(read_json(directory / "scan-execution.json"), "Scanner execution receipt")
        require(receipt.get("schema_version") == 1 and receipt.get("scanner_version") == VERSIONS["grype"], "Scanner receipt identity/version mismatch")
        require(receipt.get("scanner_sha256") == binary_hash, "Scanner executable changed since scan")
        config_hash = bind(directory / "grype-empty.yaml")
        require(receipt.get("configuration_sha256") == config_hash and (directory / "grype-empty.yaml").read_text().strip() == "{}", "Scanner configuration binding mismatch")
        require(isinstance(receipt.get("scans"), list) and len(receipt["scans"]) == len(REPORT_INPUTS), "Scanner execution receipts incomplete")
        scans = {}
        for row in receipt["scans"]:
            mapping(row, "Scanner receipt row")
            require(row.get("report") in REPORT_INPUTS and row["report"] not in scans, "Unknown/duplicate scanner report receipt")
            name = row["report"]
            require(row.get("input") == REPORT_INPUTS[name] and type(row.get("exit_code")) is int and row["exit_code"] == 0, "Scanner receipt input/exit mismatch")
            require(row.get("input_sha256") == bind(directory / row["input"]) and row.get("report_sha256") == bind(directory / name), "Scanner input/output receipt hashes changed")
            start = fresh(row.get("started_at_utc"), "Scan start", now, timedelta(days=1))
            end = fresh(row.get("finished_at_utc"), "Scan finish", now, timedelta(days=1))
            require(start <= end <= start + timedelta(minutes=10), "Scanner execution time bounds invalid")
            command = row.get("command")
            require(isinstance(command, list) and len(command) == 9 and all(isinstance(arg, str) for arg in command), "Scanner receipt command mismatch")
            require(command[1] == "--config" and command[4:7] == ["-o", "json", "--file"] and command[8] == "--quiet" and command[3].startswith("sbom:"), "Scanner receipt command mismatch")
            require(resolved_path(command[0], root) == binary.resolve() and
                    resolved_path(command[2], root) == (directory / "grype-empty.yaml").resolve() and
                    resolved_path(command[3][5:], root) == (directory / row["input"]).resolve() and
                    resolved_path(command[7], root) == (directory / name).resolve(), "Scanner receipt command mismatch")
            scans[name] = (start, end)
        kev = mapping(read_json(directory / "kev.json"), "CISA KEV")
        fresh(kev.get("dateReleased"), "KEV release", now, timedelta(days=30))
        require(isinstance(kev.get("vulnerabilities"), list) and bool(kev["vulnerabilities"]), "KEV coverage missing")
        require(type(kev.get("count")) is int and kev["count"] == len(kev["vulnerabilities"]), "KEV catalog count mismatch")
        text(kev.get("catalogVersion"), "KEV catalog version")
        kev_ids = {text(v.get("cveID"), "KEV CVE ID") for v in kev["vulnerabilities"]}
        require(len(kev_ids) == kev["count"], "KEV duplicate IDs")
        native = mapping(read_json(directory / "system-native.json"), "Native manifest")
        require(native.get("schema_version") == 1 and native.get("status") == "identified" and native.get("binding") == "python/system-libpq", "Native identification incomplete")
        fresh(native.get("created_at_utc"), "Native inventory", now, timedelta(days=1))
        require(str(native.get("platform", "")).startswith("Linux"), "Native inventory is not Linux")
        require(isinstance(native.get("owners"), list) and bool(native["owners"]) and isinstance(native.get("libraries"), list) and bool(native["libraries"]), "Native owners/libraries missing")
        native_root = resolved_path(native.get("native_root"), root)
        require(native_root == (directory / "native-root").resolve(), "Native root is outside the evidence snapshot")
        bind(native_root / "var/lib/dpkg/status", native.get("minimal_status_sha256"))
        release_file = native_root / "etc/os-release"
        bind(release_file, native.get("os_release_sha256"))
        release = os_release(release_file)
        owners = {}
        for owner in native["owners"]:
            mapping(owner, "Native owner")
            key = text(owner.get("binary_package"), "Native binary owner")
            require(key not in owners, "Duplicate native owner")
            for field in ("name", "version", "architecture", "source_name", "source_version"):
                text(owner.get(field), "Native owner " + field)
            digest(owner.get("status_block_sha256"), "Native owner status block")
            require(key == owner["name"] + ":" + owner["architecture"], "Native owner/architecture mismatch")
            notice = text(owner.get("notice_path"), "Native copyright path")
            require(Path(notice).is_absolute() and ".." not in Path(notice).parts, "Native notice path malformed")
            bind(native_root / notice.lstrip("/"), owner.get("notice_sha256"))
            owners[key] = owner
        linked_owners = set()
        for library in native["libraries"]:
            mapping(library, "Native library")
            require(library.get("owner") in owners, "Native library has no identified owner")
            linked_owners.add(library["owner"])
            bind(resolved_path(library.get("canonical_path", library.get("path")), root), library.get("sha256"))
        require(linked_owners == set(owners), "Native owners and linked closure differ")
        image = read_json(directory / "image-sbom.json")
        image_ids = syft_sbom(image, "Image SBOM")
        require(len(image_ids) >= 5 and any(x[2] in {"deb", "apk", "rpm"} for x in image_ids.values()), "Image OS package coverage incomplete")
        require(image["source"].get("type") == "image", "Image SBOM source is not image")
        image_source(image["source"]["metadata"], pin, selected)
        system = read_json(directory / "system-native-sbom.json")
        system_ids = syft_sbom(system, "System native SBOM")
        require(system["source"].get("type") == "directory" and resolved_path(system["source"]["metadata"].get("path"), root) == native_root, "System SBOM source is not the native root")
        require(system["distro"].get("id") == release["ID"] and system["distro"].get("versionID") == release["VERSION_ID"], "Native SBOM OS source mismatch")
        require({(o["name"], o["version"]) for o in owners.values()} <= {(v[0], v[1]) for v in system_ids.values()}, "Native owner package coverage incomplete")
        core = mapping(read_json(directory / "postgres-core.cdx.json"), "Supplier core SBOM")
        require(core.get("bomFormat") == "CycloneDX" and core.get("specVersion") == "1.6" and core.get("version") == 1, "Unsupported supplier core SBOM")
        components = core.get("components")
        require(isinstance(components, list) and len(components) == 1, "Supplier core identity missing")
        component = mapping(components[0], "PostgreSQL supplier component")
        require(component.get("name") == "postgresql" and component.get("version") == selected["version"] and component.get("cpe") == f"cpe:2.3:a:postgresql:postgresql:{selected['version']}:*:*:*:*:*:*:*", "Supplier core version/CPE differs from selected platform")
        inventories = {"image-cves.json": image_ids, "system-native-cves.json": system_ids}
        reviewed = set()
        for row in reviews["findings"]:
            mapping(row, "Finding review")
            for field in ("report", "id", "package", "version", "rationale", "source", "reviewer"):
                text(row.get(field), "Finding review " + field)
            reviewed.add(tuple(row[k] for k in ("report", "id", "package", "version")))
        for name, input_name in REPORT_INPUTS.items():
            report = mapping(read_json(directory / name), name)
            matches = findings(report)
            descriptor = mapping(report.get("descriptor"), name + " descriptor")
            db = scan_database(descriptor, now)
            scan_time = timestamp(descriptor.get("timestamp"), name + " timestamp")
            start, end = scans[name]
            require(start - timedelta(minutes=1) <= scan_time <= end + timedelta(minutes=1), "Report timestamp differs from recorded scan execution")
            source = mapping(report.get("source"), name + " source")
            if name == "image-cves.json":
                require(source.get("type") == "image", "Image report source missing")
                image_source(source.get("target"), pin, selected)
                require(source["target"] == image["source"]["metadata"], "Image report/SBOM metadata differ")
            elif name == "system-native-cves.json":
                require(source.get("type") == "directory" and resolved_path(source.get("target"), root) == native_root, "Native report/SBOM source differ")
            else:
                require(source.get("type") == "sbom-file" and resolved_path(source.get("target"), root) == (directory / input_name).resolve(), "Core report is not bound to supplier SBOM file")
            if name in inventories:
                sbom = image if name == "image-cves.json" else system
                distro = mapping(report.get("distro"), name + " distro")
                require(distro.get("name") == sbom["distro"]["id"] and distro.get("version") == sbom["distro"]["versionID"], "Report/SBOM distro differs")
                require(sbom["distro"]["id"] in db["providers"], "Grype database lacks the scanned OS provider")
            else:
                require("nvd" in db["providers"], "Grype database lacks the supplier-core NVD provider")
            blocking = exploited = unreviewed = 0
            for match in matches:
                mapping(match, "Grype match")
                vuln = mapping(match.get("vulnerability"), "Grype vulnerability")
                artifact = mapping(match.get("artifact"), "Grype matched artifact")
                identifier = text(vuln.get("id"), "Vulnerability ID")
                severity = text(vuln.get("severity"), "Vulnerability severity").lower()
                require(severity in {"negligible", "low", "medium", "high", "critical", "unknown"}, "Unknown vulnerability severity label")
                package = text(artifact.get("name"), "Matched package name")
                version = text(artifact.get("version"), "Matched package version")
                if name in inventories:
                    artifact_id = text(artifact.get("id"), "Matched artifact ID")
                    require(inventories[name].get(artifact_id) == (package, version, artifact.get("type")), "Matched artifact is absent from input SBOM")
                else:
                    require((package, version) == ("postgresql", selected["version"]), "Matched artifact differs from supplier core")
                related = match.get("relatedVulnerabilities", [])
                require(isinstance(related, list), "Related vulnerability IDs malformed")
                identifiers = {identifier} | {text(mapping(row, "Related vulnerability").get("id"), "Related CVE") for row in related}
                blocking += severity in {"high", "critical", "unknown"}
                exploited += bool(identifiers & kev_ids)
                unreviewed += (name, identifier, package, version) not in reviewed
            if blocking:
                errors.append(name + ": unresolved high/critical/unknown advisories=" + str(blocking))
            if exploited:
                errors.append(name + ": known-exploited advisories=" + str(exploited))
            if unreviewed:
                errors.append(name + ": findings require explicit review=" + str(unreviewed))
            reports.append({"file": name, "input": input_name, "matches": len(matches), "blocking": blocking, "sha256": sha256(directory / name), "input_sha256": sha256(directory / input_name), "database": db})
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        errors.append("Incomplete or invalid pre-use evidence: " + str(exc))
    return {"schema_version": 2, "image_reference": pin.get("reference"), "platform_manifest_digest": selected.get("digest"),
            "created_at_utc": now.isoformat(), "policy": "No unresolved high/critical/unknown or KEV findings; no suppressed/unreviewed findings; exact versioned source coverage and immutable scan receipts required",
            "status": "fail" if errors else "pass", "errors": errors, "reports": reports, "input_hashes": hashes,
            "scope": "Linux system-libpq + pinned linux/amd64 image + supplier core; not hostOS, bundled-wheel, redistribution or application security certification"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", default="work/f2-security")
    parser.add_argument("--capture-scans", action="store_true")
    args = parser.parse_args()
    directory = Path(args.directory).resolve()
    if args.capture_scans:
        capture_scans(directory, ROOT)
        return 0
    output = evaluate(directory)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "preuse-result.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))
    return 0 if output["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
