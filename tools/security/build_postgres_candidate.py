"""Build one authored static OCI candidate; never execute or clear the image."""
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
import hashlib
import json
import re
import subprocess
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
SHA = re.compile(r"sha256:([0-9a-f]{64})")
MAX_JSON = 4 * 1024 * 1024
MAX_ARCHIVE = 2 * 1024 * 1024 * 1024


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def recipe(root):
    context = root / "infra/local/postgres"
    proposal = read_json(context / "proposal.json")
    pin = read_json(root / "infra/images.lock.json")["postgres"]
    parent = proposal.get("parent_platform_manifest", "")
    require(SHA.fullmatch(parent) is not None and proposal.get("platform") == "linux/amd64", "Malformed proposal parent/platform")
    require(any(p.get("digest") == parent and p.get("platform") == {"os": "linux", "architecture": "amd64"} for p in pin["platforms"]), "Proposal parent differs from reviewed image pin")
    for path in context.iterdir():
        require(path.name in {"Dockerfile", "gosu-disabled.sh", "proposal.json", "README.md"} and path.is_file() and not path.is_symlink(), "Unexpected/symlink build-context input")
    dockerfile, stub = context / "Dockerfile", context / "gosu-disabled.sh"
    require(digest(dockerfile) == proposal.get("recipe_sha256") and digest(stub) == proposal.get("authored_replacement_sha256"), "Authored recipe/stub hashes changed")
    source = dockerfile.read_text()
    require(not re.search(r"(?im)^\s*#\s*(syntax|escape)\s*=", source), "Custom Dockerfile parser directives are forbidden")
    lines = [line.strip() for line in source.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    require(lines == ["FROM docker.io/library/postgres@" + parent, "COPY --chmod=0755 gosu-disabled.sh /usr/local/bin/gosu", "USER postgres"], "Only the exact reviewed FROM/COPY/USER recipe is allowed; no RUN")
    return context, proposal, pin


def fetch_parent(parent):
    """Metadata only: verify immutable public manifest/config and reject ONBUILD."""
    def get(url, token=None):
        headers = {"Accept": "application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json"}
        if token:
            headers["Authorization"] = "Bearer " + token
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
            data = response.read(MAX_JSON + 1)
        require(len(data) <= MAX_JSON, "Registry metadata exceeds bound")
        return data
    auth = json.loads(get("https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/postgres:pull"))
    base = "https://registry-1.docker.io/v2/library/postgres/"
    manifest_bytes = get(base + "manifests/" + parent, auth["token"])
    require("sha256:" + hashlib.sha256(manifest_bytes).hexdigest() == parent, "Parent manifest digest mismatch")
    manifest = json.loads(manifest_bytes)
    configuration = manifest["config"]["digest"]
    require(SHA.fullmatch(configuration) is not None, "Parent config digest malformed")
    config_bytes = get(base + "blobs/" + configuration, auth["token"])
    require("sha256:" + hashlib.sha256(config_bytes).hexdigest() == configuration, "Parent config digest mismatch")
    config = json.loads(config_bytes)
    require(config.get("os") == "linux" and config.get("architecture") == "amd64", "Parent platform mismatch")
    require(not config.get("config", {}).get("OnBuild"), "Parent ONBUILD could execute during static derivation")
    return manifest, config


def archive_member(path, name):
    with tarfile.open(path, "r|*") as archive:
        for member in archive:
            if member.name == name:
                require(member.isfile() and member.size <= MAX_JSON, "OCI JSON metadata is oversized/nonregular")
                return archive.extractfile(member).read()
    raise ValueError("OCI metadata member missing: " + name)


def inspect_archive(path, parent_manifest, parent_config):
    """Stream and hash every OCI blob without extracting paths or executing files."""
    require(path.is_file() and path.stat().st_size <= MAX_ARCHIVE, "OCI archive missing/oversized")
    archive_hash = digest(path)
    seen, sizes, total = set(), {}, 0
    with tarfile.open(path, "r|*") as archive:
        for member in archive:
            name = member.name
            require(name not in seen and len(seen) < 2000, "OCI duplicate/too many members")
            seen.add(name)
            require(not PurePosixPath(name).is_absolute() and ".." not in PurePosixPath(name).parts, "Unsafe OCI member path")
            if member.isdir():
                require(name.rstrip("/") in {"blobs", "blobs/sha256"}, "Unexpected OCI directory")
                continue
            require(member.isfile(), "OCI links/devices/nonregular members forbidden")
            blob = re.fullmatch(r"blobs/sha256/([0-9a-f]{64})", name)
            require(blob is not None or name in {"index.json", "oci-layout"}, "Unexpected OCI member")
            total += member.size
            require(0 <= member.size <= MAX_ARCHIVE and total <= MAX_ARCHIVE, "Expanded OCI content exceeds bound")
            value = hashlib.sha256()
            source = archive.extractfile(member)
            for block in iter(lambda: source.read(1024 * 1024), b""):
                value.update(block)
            require(blob is None or value.hexdigest() == blob[1], "OCI blob digest mismatch")
            sizes[name] = member.size
    require(json.loads(archive_member(path, "oci-layout")) == {"imageLayoutVersion": "1.0.0"}, "Unsupported OCI layout")
    index_bytes = archive_member(path, "index.json")
    index = json.loads(index_bytes)
    require(index.get("schemaVersion") == 2 and isinstance(index.get("manifests"), list) and len(index["manifests"]) == 1, "One OCI platform manifest required; no attestations/index ambiguity")
    descriptor = index["manifests"][0]
    require(descriptor.get("platform") == {"os": "linux", "architecture": "amd64"}, "OCI descriptor platform mismatch")
    def document(descriptor):
        match = SHA.fullmatch(descriptor.get("digest", ""))
        require(match is not None, "OCI descriptor digest malformed")
        name = "blobs/sha256/" + match[1]
        require(sizes.get(name) == descriptor.get("size"), "OCI descriptor size/blob mismatch")
        data = archive_member(path, name)
        require("sha256:" + hashlib.sha256(data).hexdigest() == descriptor["digest"], "OCI metadata digest changed")
        return json.loads(data)
    manifest = document(descriptor)
    require(manifest.get("schemaVersion") == 2 and isinstance(manifest.get("layers"), list), "OCI image manifest malformed")
    config = document(manifest["config"])
    require(config.get("os") == "linux" and config.get("architecture") == "amd64" and config.get("config", {}).get("User") == "postgres", "OCI config platform/User mismatch")
    parent_layers = parent_manifest.get("layers")
    require(isinstance(parent_layers, list) and len(manifest["layers"]) == len(parent_layers) + 1 and
            [(v.get("digest"), v.get("size")) for v in manifest["layers"][:-1]] == [(v.get("digest"), v.get("size")) for v in parent_layers], "Derived image must retain exact parent layers plus one authored COPY layer")
    for layer in manifest["layers"]:
        match = SHA.fullmatch(layer.get("digest", ""))
        require(match is not None and sizes.get("blobs/sha256/" + match[1]) == layer.get("size"), "OCI layer descriptor mismatch")
    for key in ("Entrypoint", "Cmd", "Env", "WorkingDir", "Volumes", "ExposedPorts", "StopSignal", "Healthcheck", "Shell", "OnBuild"):
        require(config["config"].get(key) == parent_config.get("config", {}).get(key), "Unexpected inherited config change: " + key)
    require(config.get("rootfs", {}).get("diff_ids", [])[:-1] == parent_config.get("rootfs", {}).get("diff_ids") and len(config["rootfs"]["diff_ids"]) == len(manifest["layers"]), "OCI rootfs lineage mismatch")
    require(digest(path) == archive_hash, "OCI archive changed during inspection")
    return {"index_digest": "sha256:" + hashlib.sha256(index_bytes).hexdigest(), "platform_manifest_digest": descriptor["digest"],
            "config_digest": manifest["config"]["digest"], "platform": {"os": "linux", "architecture": "amd64"}, "user": "postgres",
            "inherited_config_verified": True, "parent_layer_prefix_verified": True, "layer_count": len(manifest["layers"])}


def build(root=ROOT):
    root = Path(root).resolve()
    output = root / "work/f2-security"
    output.mkdir(parents=True, exist_ok=True)
    (output / "postgres-derived-build.json").unlink(missing_ok=True)
    context, proposal, pin = recipe(root)
    parent_manifest, parent_config = fetch_parent(proposal["parent_platform_manifest"])
    require(not parent_config.get("config", {}).get("OnBuild"), "Parent ONBUILD is forbidden")
    target = output / "postgres-derived.oci.tar"
    target.unlink(missing_ok=True)
    inputs = {str(path.relative_to(root)): digest(path) for path in [context / "Dockerfile", context / "gosu-disabled.sh", context / "proposal.json", root / "infra/images.lock.json"]}
    command = ["docker", "buildx", "build", "--platform", "linux/amd64", "--network", "none", "--provenance=false", "--sbom=false", "--output", "type=oci,dest=" + str(target), "--file", str(context / "Dockerfile"), str(context)]
    version = subprocess.run(["docker", "buildx", "version"], cwd=root, capture_output=True, text=True, timeout=30, check=True).stdout.strip()
    subprocess.run(command, cwd=root, check=True, timeout=600)
    require(all(digest(root / name) == value for name, value in inputs.items()), "Recipe/proposal/pin changed during build")
    result = inspect_archive(target, parent_manifest, parent_config)
    result.update({"schema_version": 1, "status": "built_static_not_cleared", "task": "DEV-006", "created_at_utc": datetime.now(timezone.utc).isoformat(),
                   "archive_path": str(target.relative_to(root)), "archive_sha256": digest(target), "input_hashes": inputs,
                   "recipe_sha256": proposal["recipe_sha256"], "authored_replacement_sha256": proposal["authored_replacement_sha256"],
                   "parent_platform_manifest": proposal["parent_platform_manifest"], "parent_index_digest": pin["index_digest"],
                   "parent_config_digest": parent_manifest["config"]["digest"], "buildx_version": version, "command": command,
                   "limitations": ["Static FROM/COPY/USER only; no RUN, image startup, DB connection or vulnerability gate pass.", "Replacing a merged path leaves original bytes in lower layers; no archive eradication/redistribution clearance.", "Entrypoint behavior, effective filesystem stub content/mode and native/core findings require separate actual review/scans before any image use."]})
    (output / "postgres-derived-build.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
