"""Synthetic native pre-use gate regressions; no real evidence or scanner is used.

Each CLI run uses a temporary repository/cwd, fake package bytes and fresh reports
shaped like the pinned Syft/Grype models. A synthetic pass is not phase evidence.
"""
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
REPORTS = {
    "image-cves.json": "image-sbom.json",
    "system-native-cves.json": "system-native-sbom.json",
    "postgres-core-cves.json": "postgres-core.cdx.json",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SecurityReportPolicyTests(unittest.TestCase):
    def setUp(self):
        # Synthetic receipt/replay fixtures use an explicit clean loader baseline.
        # Hostile loader behavior is tested independently in test_native_environment.
        clean = {k: v for k, v in os.environ.items()
                 if k not in {"LD_LIBRARY_PATH", "LD_PRELOAD", "LD_AUDIT"} and not k.startswith("DYLD_")}
        environment = patch.dict(os.environ, clean, clear=True)
        environment.start()
        self.addCleanup(environment.stop)
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.directory = self.root / "work/f2-security"
        self.directory.mkdir(parents=True)
        for name in ("check_reports.py", "bootstrap.py", "native_chain.py", "postgres_core.py"):
            target = self.root / "tools/security" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / "tools/security" / name, target)
        shutil.copyfile(ROOT / "tools/run_postgres_smoke.py", self.root / "tools/run_postgres_smoke.py")
        self.now = datetime.now(timezone.utc).replace(microsecond=0)
        self.image_digest = "sha256:" + "2" * 64
        self.image_metadata = {"manifestDigest": self.image_digest, "architecture": "amd64", "os": "linux",
                               "userInput": "docker.io/library/postgres@sha256:" + "1" * 64}
        self.write("infra/images.lock.json", {"postgres": {
            "reference": "docker.io/library/postgres@sha256:" + "1" * 64,
            "index_digest": "sha256:" + "1" * 64,
            "source": "https://hub.docker.com/_/postgres",
            "platforms": [{"platform": {"os": "linux", "architecture": "amd64"}, "digest": self.image_digest, "version": "17.11"}],
        }})
        self.make_tools()
        self.make_native()
        self.make_sboms_and_reports()
        self.write("work/f2-security/kev.json", {
            "title": "SYNTHETIC KEV fixture, not an advisory feed",
            "catalogVersion": self.now.strftime("%Y.%m.%d"),
            "dateReleased": self.stamp(), "count": 1,
            "vulnerabilities": [{"cveID": "CVE-2026-999998"}],
        })
        self.write("infra/security-reviewed-findings.json", {"schema_version": 1, "findings": []})
        self.receipt()

    def tearDown(self):
        self.temp.cleanup()

    def stamp(self, value=None):
        return (value or self.now).isoformat().replace("+00:00", "Z")

    def write(self, relative, data):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2) + "\n")
        return path

    def read(self, relative):
        return json.loads((self.root / relative).read_text())

    def mutate(self, relative, callback, receipt=True):
        data = self.read(relative)
        callback(data)
        self.write(relative, data)
        if receipt:
            self.receipt()

    def make_tools(self):
        tools = []
        for name, version in (("syft", "1.57.1"), ("grype", "0.121.3")):
            executable = self.root / ".local/security-tools" / name
            executable.parent.mkdir(parents=True, exist_ok=True)
            executable.write_text("SYNTHETIC non-executable scanner fixture " + name)
            notice = executable.with_name(name + "-LICENSE")
            notice.write_text("SYNTHETIC notice, not an upstream license")
            tools.append({"name": name, "version": version, "platform": "linux_amd64",
                          "source": f"https://github.com/anchore/{name}/releases/download/v{version}/{name}_{version}_linux_amd64.tar.gz",
                          "archive_sha256": "a" * 64, "sha256": digest(executable),
                          "binary_sha256": digest(executable),
                          "notices": [{"path": str(notice.relative_to(self.root)), "sha256": digest(notice)}]})
        self.write("work/f2-security/tools.json", tools)

    def make_native(self):
        native_root = self.directory / "native-root"
        os_release = native_root / "etc/os-release"
        os_release.parent.mkdir(parents=True)
        os_release.write_text('ID=ubuntu\nVERSION_ID="24.04"\n')
        owners, libraries, blocks = [], [], []
        for name, version, source in (("libpq5", "17.11-1", "postgresql-17"), ("libc6", "2.39-1", "glibc")):
            notice_path = f"/usr/share/doc/{name}/copyright"
            notice = native_root / notice_path.lstrip("/")
            notice.parent.mkdir(parents=True)
            notice.write_text("SYNTHETIC copyright for " + name)
            native_file = self.root / "synthetic-native" / (name + ".so")
            native_file.parent.mkdir(exist_ok=True)
            native_file.write_bytes(("SYNTHETIC non-ELF native bytes " + name).encode())
            block = f"Package: {name}\nStatus: install ok installed\nArchitecture: amd64\nVersion: {version}\nSource: {source} ({version})\n\n"
            blocks.append(block)
            owners.append({"name": name, "version": version, "binary_package": name + ":amd64",
                           "architecture": "amd64", "source_name": source, "source_version": version,
                           "source_field": f"{source} ({version})", "status_block_sha256": hashlib.sha256(block.encode()).hexdigest(),
                           "notice_path": notice_path, "notice_sha256": digest(notice)})
            libraries.append({"path": str(native_file), "canonical_path": str(native_file),
                              "sha256": digest(native_file), "owner": name + ":amd64"})
        status = native_root / "var/lib/dpkg/status"
        status.parent.mkdir(parents=True)
        status.write_text("".join(blocks))
        self.native = {"schema_version": 1, "status": "identified", "binding": "python/system-libpq",
                       "created_at_utc": self.stamp(), "platform": "Linux-synthetic", "native_root": str(native_root),
                       "libpq_path": libraries[0]["path"], "owners": owners, "libraries": libraries,
                       "source_status_sha256": digest(status), "minimal_status_sha256": digest(status),
                       "os_release_sha256": digest(os_release), "virtual_entries_without_files": []}
        self.write("work/f2-security/system-native.json", self.native)

    def artifact(self, name, version, identifier=None):
        return {"id": identifier or "synthetic-" + name, "name": name, "version": version, "type": "deb"}

    def syft(self, source, artifacts, distro):
        return {"artifacts": artifacts, "artifactRelationships": [], "files": [], "source": source,
                "distro": distro, "descriptor": {"name": "syft", "version": "1.57.1"},
                "schema": {"version": "16.1.13", "url": "https://raw.githubusercontent.com/anchore/syft/main/schema/json/schema-16.1.13.json"}}

    def grype(self, source, distro):
        return {"matches": [], "source": source, "distro": distro,
                "descriptor": {"name": "grype", "version": "0.121.3", "timestamp": self.stamp(),
                               "db": {"status": {"valid": True, "schemaVersion": "v6.1.10", "built": self.stamp()}, "providers": {name: {"captured": self.stamp(), "input": "xxh64:synthetic"} for name in ("ubuntu", "debian", "nvd")}}}}

    def make_sboms_and_reports(self):
        image_artifacts = [self.artifact(name, "1.0-1") for name in ("libc6", "libssl3", "bash", "coreutils", "ca-certificates")]
        image_source = {"id": "synthetic-image-source", "name": "synthetic-postgres", "type": "image", "metadata": self.image_metadata}
        image_distro = {"id": "debian", "versionID": "13"}
        self.write("work/f2-security/image-sbom.json", self.syft(image_source, image_artifacts, image_distro))
        self.write("work/f2-security/image-cves.json", self.grype({"type": "image", "target": self.image_metadata}, {"name": "debian", "version": "13"}))
        native_artifacts = [self.artifact(p["name"], p["version"]) for p in self.native["owners"]]
        native_source = {"id": "synthetic-directory-source", "name": "native-root", "type": "directory", "metadata": {"path": self.native["native_root"]}}
        self.write("work/f2-security/system-native-sbom.json", self.syft(native_source, native_artifacts, {"id": "ubuntu", "versionID": "24.04"}))
        self.write("work/f2-security/system-native-cves.json", self.grype({"type": "directory", "target": self.native["native_root"]}, {"name": "ubuntu", "version": "24.04"}))
        core = {"bomFormat": "CycloneDX", "specVersion": "1.6", "version": 1,
                "components": [{"type": "application", "bom-ref": "supplier-postgresql-17.11", "name": "postgresql", "version": "17.11",
                                "cpe": "cpe:2.3:a:postgresql:postgresql:17.11:*:*:*:*:*:*:*", "licenses": [{"license": {"id": "PostgreSQL"}}]}]}
        self.write("work/f2-security/postgres-core.cdx.json", core)
        self.write("work/f2-security/postgres-core-cves.json", self.grype({"type": "sbom-file", "target": str(self.directory / "postgres-core.cdx.json")}, {"name": "", "version": ""}))

    def receipt(self):
        config = self.directory / "grype-empty.yaml"
        if not config.exists():
            config.write_text("{}\n")
        binary = self.root / ".local/security-tools/grype"
        scans = [{"report": report, "input": source, "input_sha256": digest(self.directory / source),
                  "report_sha256": digest(self.directory / report), "exit_code": 0,
                  "started_at_utc": self.stamp(self.now - timedelta(seconds=1)), "finished_at_utc": self.stamp(),
                  "command": [str(binary), "--config", str(config), "sbom:" + str(self.directory / source),
                              "-o", "json", "--file", str(self.directory / report), "--quiet"]}
                 for report, source in REPORTS.items() if (self.directory / source).exists() and (self.directory / report).exists()]
        self.write("work/f2-security/scan-execution.json", {"schema_version": 1, "scanner_version": "0.121.3",
                   "scanner_sha256": digest(binary), "configuration_sha256": digest(config), "scans": scans})

    def run_checker(self):
        result = subprocess.run([sys.executable, str(self.root / "tools/security/check_reports.py"), "--directory", "work/f2-security"],
                                cwd=self.root, text=True, capture_output=True, timeout=15)
        output = self.directory / "preuse-result.json"
        self.assertTrue(output.is_file(), "Checker must emit a failure record rather than crash: " + result.stderr)
        return result, json.loads(output.read_text())

    def assert_pass(self):
        result, output = self.run_checker()
        self.assertEqual(result.returncode, 0, output)
        self.assertEqual(output["status"], "pass")
        self.assertEqual(output["errors"], [])
        return output

    def assert_fail(self, expected):
        result, output = self.run_checker()
        self.assertNotEqual(result.returncode, 0, output)
        self.assertEqual(output["status"], "fail")
        self.assertTrue(output["errors"])
        message = " ".join(output["errors"]).lower()
        for part in ([expected] if isinstance(expected, str) else expected):
            self.assertIn(part.lower(), message, "Failure did not reach the intended policy: " + str(output["errors"]))
        return output

    def match(self, severity="Medium", identifier="CVE-2026-999999", package="libpq5", version="17.11-1"):
        return {"vulnerability": {"id": identifier, "severity": severity},
                "artifact": self.artifact(package, version), "relatedVulnerabilities": []}

    def finding(self, match, report="system-native-cves.json", reviewed=False):
        self.mutate("work/f2-security/" + report, lambda data: data.update(matches=[match]))
        if reviewed:
            record = {"report": report, "id": match["vulnerability"]["id"], "package": match["artifact"]["name"],
                      "version": match["artifact"]["version"], "rationale": "SYNTHETIC review for unit tests only",
                      "source": "https://example.invalid/synthetic-review", "reviewer": "synthetic-independent-reviewer",
                      "reviewed_at_utc": self.stamp(), "reviewed_date": self.now.date().isoformat(),
                      "expires_at_utc": self.stamp(self.now + timedelta(days=1))}
            self.write("infra/security-reviewed-findings.json", {"schema_version": 1, "findings": [record]})

    def test_complete_synthetic_evidence_passes_and_records_actual_report_hashes(self):
        output = self.assert_pass()
        self.assertEqual({row["file"] for row in output["reports"]}, set(REPORTS))
        for row in output["reports"]:
            self.assertEqual(row["sha256"], digest(self.directory / row["file"]))
        self.assertTrue(output.get("input_hashes"), "Pre-use result must bind complete inputs for later replay.")

    def test_absent_optional_ignored_matches_is_valid(self):
        self.assert_pass()

    def test_empty_optional_ignored_matches_is_valid(self):
        self.mutate("work/f2-security/system-native-cves.json", lambda data: data.update(ignoredMatches=[]))
        self.assert_pass()

    def test_missing_required_report_fails(self):
        (self.directory / "system-native-cves.json").unlink()
        self.assert_fail('Required evidence is missing')

    def test_unreadable_json_report_fails(self):
        (self.directory / "image-cves.json").write_text("{not-json")
        self.receipt()
        self.assert_fail('Expecting property name')

    def test_missing_scanner_database_metadata_fails(self):
        self.mutate("work/f2-security/image-cves.json", lambda data: data["descriptor"].pop("db"))
        self.assert_fail('Grype database must be an object')

    def test_invalid_scanner_database_fails(self):
        self.mutate("work/f2-security/image-cves.json", lambda data: data["descriptor"]["db"]["status"].update(valid=False))
        self.assert_fail('Grype DB is invalid')

    def test_stale_scanner_database_fails(self):
        self.mutate("work/f2-security/image-cves.json", lambda data: data["descriptor"]["db"]["status"].update(built=self.stamp(self.now - timedelta(days=6))))
        self.assert_fail('Grype DB build is stale')

    def test_missing_matches_field_fails(self):
        self.mutate("work/f2-security/system-native-cves.json", lambda data: data.pop("matches"))
        self.assert_fail('Grype matches must be an explicit array')

    def test_wrong_type_matches_fails(self):
        self.mutate("work/f2-security/system-native-cves.json", lambda data: data.update(matches={}))
        self.assert_fail('Grype matches must be an explicit array')

    def test_wrong_type_ignored_matches_fails(self):
        self.mutate("work/f2-security/system-native-cves.json", lambda data: data.update(ignoredMatches={}))
        self.assert_fail('ignoredMatches must be an array')

    def test_suppressed_finding_fails(self):
        self.mutate("work/f2-security/system-native-cves.json", lambda data: data.update(ignoredMatches=[{"match": self.match("High"), "appliedIgnoreRules": []}]))
        self.assert_fail('Suppressed/ignored findings')

    def test_high_cannot_be_overridden_by_review(self):
        self.finding(self.match("High"), reviewed=True)
        self.assert_fail('unresolved high/critical/unknown advisories')

    def test_critical_cannot_be_overridden_by_review(self):
        self.finding(self.match("Critical"), reviewed=True)
        self.assert_fail('unresolved high/critical/unknown advisories')

    def test_kev_blocks_reviewed_low_severity(self):
        self.finding(self.match("Low", "CVE-2026-999998"), reviewed=True)
        self.assert_fail('known-exploited advisories')

    def test_related_kev_alias_blocks_reviewed_medium(self):
        match = self.match()
        match["relatedVulnerabilities"] = [{"id": "CVE-2026-999998"}]
        self.finding(match, reviewed=True)
        self.assert_fail('known-exploited advisories')

    def test_unreviewed_medium_fails(self):
        self.finding(self.match())
        self.assert_fail('findings require explicit review')

    def test_reviewed_medium_passes(self):
        self.finding(self.match(), reviewed=True)
        self.assert_pass()

    def test_review_for_wrong_package_version_does_not_authorize_finding(self):
        self.finding(self.match(), reviewed=True)
        self.mutate("infra/security-reviewed-findings.json", lambda data: data["findings"][0].update(version="different"))
        self.assert_fail('findings require explicit review')

    def test_review_without_rationale_fails(self):
        self.finding(self.match(), reviewed=True)
        self.mutate("infra/security-reviewed-findings.json", lambda data: data["findings"][0].update(rationale=""))
        self.assert_fail('Finding review rationale')

    def test_native_owner_missing_from_sbom_fails(self):
        self.mutate("work/f2-security/system-native-sbom.json", lambda data: data["artifacts"].pop())
        self.assert_fail('Native owner package coverage incomplete')

    def test_native_notice_missing_fails(self):
        self.mutate("work/f2-security/system-native.json", lambda data: data["owners"][0].pop("notice_sha256"))
        self.assert_fail('SHA-256')

    def test_unknown_native_version_fails(self):
        self.mutate("work/f2-security/system-native.json", lambda data: data["owners"][0].update(version=""))
        self.assert_fail('Native owner version')

    def test_changed_native_binary_fails(self):
        Path(self.native["libraries"][0]["canonical_path"]).write_bytes(b"different synthetic native bytes")
        self.assert_fail('changed since inventory')

    def test_changed_copied_copyright_fails(self):
        (Path(self.native["native_root"]) / self.native["owners"][0]["notice_path"].lstrip("/")).write_text("changed notice")
        self.assert_fail('changed since inventory')

    def test_image_inventory_too_small_fails(self):
        self.mutate("work/f2-security/image-sbom.json", lambda data: data.update(artifacts=data["artifacts"][:4]))
        self.assert_fail('Image OS package coverage incomplete')

    def test_wrong_image_digest_fails_even_when_report_matches_sbom(self):
        self.mutate("work/f2-security/image-sbom.json", lambda data: data["source"]["metadata"].update(manifestDigest="sha256:" + "3" * 64))
        self.mutate("work/f2-security/image-cves.json", lambda data: data["source"]["target"].update(manifestDigest="sha256:" + "3" * 64))
        self.assert_fail('pinned platform manifest')

    def test_wrong_image_architecture_fails(self):
        self.mutate("work/f2-security/image-sbom.json", lambda data: data["source"]["metadata"].update(architecture="arm64"))
        self.mutate("work/f2-security/image-cves.json", lambda data: data["source"]["target"].update(architecture="arm64"))
        self.assert_fail('Image architecture/OS mismatch')

    def test_report_distro_substitution_fails(self):
        self.mutate("work/f2-security/image-cves.json", lambda data: data.update(distro={"name": "ubuntu", "version": "24.04"}))
        self.assert_fail('Report/SBOM distro differs')

    def test_missing_scan_receipt_fails(self):
        (self.directory / "scan-execution.json").unlink()
        self.assert_fail('Required evidence is missing')

    def test_nonzero_scanner_exit_fails(self):
        self.mutate("work/f2-security/scan-execution.json", lambda data: data["scans"][0].update(exit_code=1), receipt=False)
        self.assert_fail('Scanner receipt input/exit mismatch')

    def test_stale_scan_receipt_fails(self):
        self.mutate("work/f2-security/scan-execution.json", lambda data: data["scans"][0].update(started_at_utc=self.stamp(self.now - timedelta(hours=26)), finished_at_utc=self.stamp(self.now - timedelta(hours=25))), receipt=False)
        self.assert_fail('Scan start is stale')

    def test_report_changed_since_scan_receipt_fails(self):
        self.mutate("work/f2-security/image-cves.json", lambda data: data.update(synthetic_changed_after_scan=True), receipt=False)
        self.assert_fail('Scanner input/output receipt hashes changed')

    def test_stale_kev_catalog_fails(self):
        self.mutate("work/f2-security/kev.json", lambda data: data.update(dateReleased=self.stamp(self.now - timedelta(days=31))))
        self.assert_fail('KEV release is stale')


    def runner(self):
        path = self.root / "tools/run_postgres_smoke.py"
        spec = importlib.util.spec_from_file_location("synthetic_postgres_runner", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_runner_replays_complete_approval_without_executing_commands(self):
        approved = self.assert_pass()
        runner = self.runner()
        with patch.object(runner.subprocess, "run", side_effect=AssertionError("Replay must not execute Docker, scanner or DB commands")):
            stored, pin = runner.verify_preuse(self.root)
        self.assertEqual(stored, approved)
        self.assertEqual(pin["reference"], approved["image_reference"])

    def test_runner_invalidates_each_changed_source_and_policy_input(self):
        self.assert_pass()
        runner = self.runner()
        files = ["work/f2-security/system-native.json", "work/f2-security/system-native-sbom.json",
                 "work/f2-security/kev.json", "infra/security-reviewed-findings.json",
                 "infra/images.lock.json", "tools/security/check_reports.py",
                 "work/f2-security/native-root/usr/share/doc/libpq5/copyright"]
        for name in files:
            with self.subTest(input=name):
                path = self.root / name
                original = path.read_bytes()
                try:
                    path.write_bytes(original + b"\n")
                    with self.assertRaisesRegex(ValueError, "evidence/policy/native bytes changed"):
                        runner.verify_preuse(self.root)
                finally:
                    path.write_bytes(original)
        runner.verify_preuse(self.root)

    def test_runner_invalidates_review_file_appearing_after_approval(self):
        path = self.root / "infra/security-reviewed-findings.json"
        path.unlink()
        approved = self.assert_pass()
        self.assertIsNone(approved["input_hashes"][str(path)])
        self.write("infra/security-reviewed-findings.json", {"findings": []})
        with self.assertRaisesRegex(ValueError, "policy/review presence changed"):
            self.runner().verify_preuse(self.root)

    def test_runner_rejects_expired_approval_without_starting_a_database(self):
        self.assert_pass()
        self.mutate("work/f2-security/preuse-result.json", lambda data: data.update(created_at_utc=self.stamp(self.now - timedelta(hours=25))), receipt=False)
        with self.assertRaisesRegex(ValueError, "pre-use evidence expired"):
            self.runner().verify_preuse(self.root)

    def test_runner_rejects_missing_input_hash_map(self):
        self.assert_pass()
        self.mutate("work/f2-security/preuse-result.json", lambda data: data.update(input_hashes={}), receipt=False)
        with self.assertRaisesRegex(ValueError, "no complete input binding"):
            self.runner().verify_preuse(self.root)

    def test_runner_rejects_pruned_input_hash_map(self):
        self.assert_pass()
        self.mutate("work/f2-security/preuse-result.json", lambda data: data["input_hashes"].pop(str(self.directory / "kev.json")), receipt=False)
        with self.assertRaisesRegex(ValueError, "source coverage no longer passes"):
            self.runner().verify_preuse(self.root)

    def test_runner_rejects_tampered_approved_report_summary(self):
        self.assert_pass()
        self.mutate("work/f2-security/preuse-result.json", lambda data: data["reports"][0].update(matches=999), receipt=False)
        with self.assertRaisesRegex(ValueError, "identity/findings differ"):
            self.runner().verify_preuse(self.root)

    def test_unapplied_pinned_upstream_ignore_default_is_not_a_suppressed_finding(self):
        rule = {"vulnerability": "", "include-aliases": False, "reason": "", "namespace": "",
                "fix-state": "", "package": {"name": "linux-libc-dev", "version": "", "language": "",
                "type": "deb", "location": "", "upstream-name": "linux"},
                "vex-status": "", "vex-justification": "", "match-type": "exact-indirect-match"}
        self.mutate("work/f2-security/system-native-cves.json", lambda data: data["descriptor"].update(configuration={"ignore": [rule]}))
        self.assert_pass()


    def test_malformed_scanner_provider_metadata_fails(self):
        self.mutate("work/f2-security/image-cves.json", lambda data: data["descriptor"]["db"].update(providers={"debian": []}))
        self.assert_fail("Grype provider metadata must be an object")

    def test_missing_scanned_os_database_provider_fails(self):
        self.mutate("work/f2-security/image-cves.json", lambda data: data["descriptor"]["db"]["providers"].pop("debian"))
        self.assert_fail("database lacks the scanned OS provider")

    def test_missing_supplier_core_nvd_provider_fails(self):
        self.mutate("work/f2-security/postgres-core-cves.json", lambda data: data["descriptor"]["db"]["providers"].pop("nvd"))
        self.assert_fail("supplier-core NVD provider")

    def test_stale_scanner_provider_metadata_fails(self):
        self.mutate("work/f2-security/image-cves.json", lambda data: data["descriptor"]["db"]["providers"]["debian"].update(captured=self.stamp(self.now - timedelta(days=6))))
        self.assert_fail("Grype provider capture is stale")


if __name__ == "__main__":
    unittest.main()
