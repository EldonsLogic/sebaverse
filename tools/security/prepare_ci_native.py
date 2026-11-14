"""Record a signed-index Ubuntu libc6 candidate and dry-run only; never install.

Run on the disposable Ubuntu24.04 CI runner AFTER a separately recorded
`sudo apt-get update --error-on=any`. No user host/global package changes.
The output requires phase-owner review; it is not native pre-use approval.
"""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
MINIMUM = "2.39-0ubuntu8.12"
FIXABLE_IDS = ["CVE-2026-8674", "CVE-2026-84243", "CVE-2026-97399", "CVE-2026-18374", "CVE-2026-95818", "CVE-2026-86805"]


def command(args):
    result = subprocess.run(args, capture_output=True, text=True, timeout=90)
    if result.returncode:
        raise RuntimeError("Metadata/dry-run command failed: " + args[0])
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", default="work/f2-security")
    output = Path(parser.parse_args().output_root).resolve()
    if not output.is_relative_to((ROOT / "work").resolve()):
        parser.error("Output must remain in this repository's ignored work directory")
    output.mkdir(parents=True, exist_ok=True)
    record = {"status": "blocked", "created_at_utc": datetime.now(timezone.utc).isoformat(),
              "package": "libc6", "minimum_fixed_version": MINIMUM, "reported_fixable_ids": FIXABLE_IDS,
              "scope": "Metadata and simulated transaction only; no install or gate approval",
              "metadata_api_reference": "https://apt-team.pages.debian.net/python-apt/library/apt.package.html#origin-information"}
    try:
        release = dict(line.split("=", 1) for line in Path("/etc/os-release").read_text().splitlines() if "=" in line)
        if sys.platform != "linux" or release.get("ID", "").strip('"') != "ubuntu" or release.get("VERSION_ID", "").strip('"') != "24.04":
            raise RuntimeError("This remediation review applies only to the observed Ubuntu24.04 baseline")
        # Use the runner's existing distro apt bindings; do not install a Python package.
        probe = '''
import apt, json
package = apt.Cache()["libc6"]
version = package.candidate
if version is None or package.installed is None:
    raise RuntimeError("Installed libc6/candidate metadata missing")
def field(name):
    try: return version.record[name]
    except KeyError: return None
print(json.dumps({"installed":package.installed.version,"candidate":version.version,"architecture":version.architecture,"uri":version.uri,"filename":field("Filename"),"sha256":field("SHA256"),"origins":[{"origin":o.origin,"label":o.label,"archive":o.archive,"site":o.site,"component":o.component,"trusted":o.trusted} for o in version.origins]}))
'''
        candidate = json.loads(command(["/usr/bin/python3", "-c", probe]))
        record["candidate_metadata"] = candidate
        if not re.fullmatch(r"[0-9a-f]{64}", candidate.get("sha256") or "") or not candidate.get("filename"):
            raise RuntimeError("Authenticated package checksum/path not recorded")
        allowed = [o for o in candidate["origins"] if o.get("trusted") is True and o.get("origin") == "Ubuntu"
                   and o.get("label") == "Ubuntu"
                   and o.get("archive") in {"noble-security", "noble-updates"} and o.get("component") == "main"]
        if not allowed:
            raise RuntimeError("Candidate lacks a trusted Ubuntu Noble security/updates origin")
        version = candidate["candidate"]
        if not re.fullmatch(r"[A-Za-z0-9.+:~_-]+", version):
            raise RuntimeError("Malformed candidate version")
        for older in [MINIMUM, candidate["installed"]]:
            if subprocess.run(["dpkg", "--compare-versions", version, "ge", older]).returncode:
                raise RuntimeError("Candidate is older than required/current runtime")
        record["apt_policy"] = command(["apt-cache", "policy", "libc6"])
        record["simulation_command"] = ["apt-get", "--simulate", "--no-install-recommends", "--only-upgrade", "install", "libc6=" + version]
        simulation = command(record["simulation_command"])
        record["simulation"] = simulation
        if any(line.startswith("Remv ") for line in simulation.splitlines()):
            raise RuntimeError("Simulation proposes removals; separate remediation review required")
        record["status"] = "candidate_recorded_review_required"
        record["next_action"] = "Phase owner reviews exact candidate, trusted-index evidence and every simulated companion package before any explicit CI-only upgrade; re-inventory/rescan afterward"
        record["limitations"] = ["APT trusted origin/checksum is observed, not an independent signature re-verification by this script.",
                                "Fresh apt-get update success must be recorded separately; this script does not refresh indexes.",
                                "Companion package provenance/notice checks are not automatically approved by the simulation.",
                                "No CVE or native/image policy pass is asserted."]
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as error:
        record["error"] = str(error)
    (output / "ubuntu-native-candidate.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({k: record[k] for k in ("status", "error") if k in record}))
    return 0 if record["status"] == "candidate_recorded_review_required" else 1


if __name__ == "__main__":
    raise SystemExit(main())
