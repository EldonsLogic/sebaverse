#!/usr/bin/env python3
"""Inventory the trusted Linux system libpq closure; never connect to a DB.

Run only on the phase owner's signed, preinstalled Debian/Ubuntu runner baseline.
No ELF path is accepted from users/uploads. Scanner verdicts remain separate.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys


LOADER_OVERRIDES = ("LD_LIBRARY_PATH", "LD_PRELOAD", "LD_AUDIT")


def validate_loader_environment(environment=None):
    """Reject inherited loader redirection before inspecting the linked closure."""
    values = os.environ if environment is None else environment
    if any(values.get(name) for name in LOADER_OVERRIDES) or any(
        name.startswith("DYLD_") and value for name, value in values.items()
    ):
        raise RuntimeError("Dynamic-loader overrides must be absent for trusted native inspection.")


def run(*args, optional=False):
    result = subprocess.run(args, capture_output=True, text=True, timeout=30)
    if result.returncode and not optional:
        raise RuntimeError(f"Required system inspection failed: {args[0]}")
    return result.stdout if result.returncode == 0 else ""


def sha256(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def status_blocks(text):
    blocks = []
    for block in text.strip("\n").split("\n\n"):
        fields = {}
        for line in block.splitlines():
            if line and not line[0].isspace() and ":" in line:
                key, value = line.split(":", 1)
                fields[key] = value.strip()
        if fields:
            blocks.append((fields, block + "\n\n"))
    return blocks


def ldd_paths(text):
    paths, virtual = [], []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if "not found" in line:
            raise RuntimeError("A linked native library is missing.")
        if line.startswith(("linux-vdso.so", "linux-gate.so")):
            virtual.append(line.split()[0])
            continue
        match = re.search(r"(?:=>\s+)?(/\S+)\s+\(0x[0-9a-fA-F]+\)$", line)
        if not match:
            raise RuntimeError("Unrecognized ldd output; native closure is incomplete.")
        paths.append(Path(match.group(1)))
    if not paths:
        raise RuntimeError("No linked library paths were identified.")
    return paths, virtual


def system_path(path):
    resolved = path.resolve(strict=True)
    roots = [Path(p).resolve() for p in ("/lib", "/lib64", "/usr/lib", "/usr/lib64")]
    if not resolved.is_file() or not any(resolved.is_relative_to(root) for root in roots):
        raise RuntimeError("Native path is outside the trusted system library roots.")
    return resolved


def locate_libpq():
    tool = shutil.which("ldconfig") or "/sbin/ldconfig"
    machine = platform.machine().lower()
    arch = {"x86_64": "x86-64", "aarch64": "aarch64"}.get(machine)
    if arch is None:
        raise RuntimeError("Native architecture requires an explicit libpq selection rule.")
    candidates = {}
    for line in run(tool, "-p").splitlines():
        if line.strip().startswith("libpq.so.5 ") and arch in line.lower() and "=>" in line:
            candidate = Path(line.split("=>", 1)[1].strip())
            candidates[system_path(candidate)] = candidate
    if len(candidates) != 1:
        raise RuntimeError("A unique trusted libpq.so.5 for this architecture was not identified.")
    return next(iter(candidates.values()))


def package_owner(original, canonical):
    aliases = [canonical, original]
    for path in list(aliases):
        name = str(path)
        if name.startswith(("/lib/", "/lib64/")):
            aliases.append(Path("/usr" + name))
        elif name.startswith(("/usr/lib/", "/usr/lib64/")):
            aliases.append(Path(name.removeprefix("/usr")))
    for alias in dict.fromkeys(aliases):
        owners = set()
        for line in run("dpkg-query", "--search", str(alias), optional=True).splitlines():
            if ": " in line and not line.startswith("diversion"):
                header, _ = line.split(": ", 1)
                owners.update(value.strip() for value in header.split(","))
        if len(owners) == 1:
            return owners.pop()
        if owners:
            raise RuntimeError("Native file ownership is ambiguous.")
    raise RuntimeError("A native file has no installed dpkg owner.")


def inventory(output):
    validate_loader_environment()
    if sys.platform != "linux":
        raise RuntimeError("Linux/Debian-only inspection: native checks were not run on this platform.")
    database = Path("/var/lib/dpkg/status")
    blocks = status_blocks(database.read_text())
    libpq = locate_libpq()
    linked = run("ldd", str(libpq))
    paths, virtual = ldd_paths(linked)
    libraries, owners = [], {}
    for original in [libpq, *paths]:
        canonical = system_path(original)
        if any(row["canonical_path"] == str(canonical) for row in libraries):
            continue
        binary = package_owner(original, canonical)
        name, _, arch = binary.partition(":")
        matches = [(fields, block) for fields, block in blocks if fields.get("Package") == name
                   and (not arch or fields.get("Architecture") == arch)
                   and fields.get("Status") == "install ok installed"]
        if len(matches) != 1:
            raise RuntimeError("Exact installed owner metadata was not identified.")
        fields, raw = matches[0]
        if not fields.get("Version") or not fields.get("Architecture"):
            raise RuntimeError("Installed package version/architecture is missing.")
        key = name + ":" + fields["Architecture"]
        source = re.fullmatch(r"([a-z0-9+.-]+)(?:\s+\(([^)]+)\))?", fields.get("Source", name))
        if source is None:
            raise RuntimeError("Source-package provenance is malformed.")
        notice = Path("/usr/share/doc") / name / "copyright"
        if not notice.is_file():
            raise RuntimeError("A required installed owner copyright notice is missing.")
        owners[key] = {"name": name, "binary_package": key, "architecture": fields["Architecture"],
                       "version": fields["Version"], "source_name": source[1],
                       "source_version": source[2] or fields["Version"],
                       "source_field": fields.get("Source"), "status_block": raw,
                       "status_block_sha256": hashlib.sha256(raw.encode()).hexdigest(),
                       "notice_path": str(notice), "notice_sha256": sha256(notice)}
        libraries.append({"path": str(original), "canonical_path": str(canonical),
                          "sha256": sha256(canonical), "owner": key})
    root = output / "native-root"
    status = root / "var/lib/dpkg/status"
    status.parent.mkdir(parents=True, exist_ok=True)
    status.write_text("".join(owners[key]["status_block"] for key in sorted(owners)))
    os_release = root / "etc/os-release"
    os_release.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile("/etc/os-release", os_release)
    for owner in owners.values():
        target = root / owner["notice_path"].lstrip("/")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(owner["notice_path"], target)
        if sha256(target) != owner["notice_sha256"]:
            raise RuntimeError("Copied copyright notice hash changed.")
        del owner["status_block"]
    return {"schema_version": 1, "status": "identified", "binding": "python/system-libpq",
            "created_at_utc": datetime.now(timezone.utc).isoformat(), "platform": platform.platform(),
            "libpq_path": str(libpq), "libraries": libraries, "owners": list(owners.values()),
            "native_root": str(root), "source_status_sha256": sha256(database),
            "minimal_status_sha256": sha256(status), "os_release_sha256": sha256(os_release),
            "ldd_output": linked, "virtual_entries_without_files": virtual,
            "limitations": ["No DB connection, installation or vulnerability verdict is performed.",
                            "Installed dpkg provenance is not a fresh signature or upstream-file-integrity verification.",
                            "ldd identifies the current linked closure, not future optional dlopen plugins.",
                            "Scanner coverage must match every owner/version before any DB use."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", default="work/f2-security")
    output = Path(parser.parse_args().output_root).resolve()
    work = Path(__file__).resolve().parents[2] / "work"
    if not output.is_relative_to(work.resolve()):
        parser.error("Output must remain inside this repository's ignored work directory.")
    output.mkdir(parents=True, exist_ok=True)
    try:
        result = inventory(output)
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
        result = {"schema_version": 1, "status": "failed", "error": str(error), "platform": sys.platform}
    (output / "system-native.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("status", "error") if key in result}))
    return 0 if result["status"] == "identified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
