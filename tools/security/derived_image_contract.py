"""Offline identity/recipe replay for the explicitly selected static OCI source."""
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

POLICY_PATH = "infra/local/postgres/runtime-source.json"
PATHS = {
    "archive": "work/f2-security/postgres-derived.oci.tar",
    "build_receipt": "work/f2-security/postgres-derived-build.json",
    "files_receipt": "work/f2-security/postgres-derived-files.json",
    "parent_manifest": "work/f2-security/postgres-parent-manifest.json",
    "parent_config": "work/f2-security/postgres-parent-config.json",
}


def require(value, message):
    if not value:
        raise ValueError(message)


def load_tool(root, filename, name):
    spec = importlib.util.spec_from_file_location(name, root / "tools/security" / filename)
    require(spec is not None and spec.loader is not None, "Derived source helper unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(root, directory, bind):
    """Hash all inputs and independently replay archive/COPY checks; no writes/use."""
    root, directory = Path(root).resolve(), Path(directory).resolve()
    policy_file = root / POLICY_PATH
    bind(policy_file)
    policy = json.loads(policy_file.read_text())
    require(policy.get("schema_version") == 1 and policy.get("type") == "derived-oci", "Unsupported explicit runtime image authority")
    require(policy.get("platform") == {"os": "linux", "architecture": "amd64"} and policy.get("user") == "postgres", "Derived runtime platform/User authority mismatch")
    require(all(policy.get(key) == value for key, value in PATHS.items()) and directory == (root / "work/f2-security").resolve(), "Derived runtime artifact paths differ from scoped authority")
    paths = {key: root / value for key, value in PATHS.items()}
    for path in paths.values():
        bind(path)
    for name in ("derived_image_contract.py", "build_postgres_candidate.py", "inspect_postgres_files.py"):
        bind(root / "tools/security" / name)
    builder = load_tool(root, "build_postgres_candidate.py", "sebaverse_derived_builder")
    # The standalone inspector imports its reviewed sibling by its CLI module name.
    previous = sys.modules.get("build_postgres_candidate")
    sys.modules["build_postgres_candidate"] = builder
    try:
        inspector = load_tool(root, "inspect_postgres_files.py", "sebaverse_derived_files")
    finally:
        if previous is None:
            sys.modules.pop("build_postgres_candidate", None)
        else:
            sys.modules["build_postgres_candidate"] = previous
    context, proposal, pin = builder.recipe(root)
    for field in ("parent_platform_manifest", "recipe_sha256", "authored_replacement_sha256"):
        require(policy.get(field) == proposal.get(field), "Derived recipe/parent differs from committed runtime authority")
    receipt = json.loads(paths["build_receipt"].read_text())
    require(receipt.get("schema_version") == 1 and receipt.get("status") == "built_static_not_cleared", "Derived build receipt is missing or has unexpected status")
    require(receipt.get("archive_path") == PATHS["archive"] and receipt.get("archive_sha256") == builder.digest(paths["archive"]), "Derived archive differs from build receipt")
    expected_inputs = [context / "Dockerfile", context / "gosu-disabled.sh", context / "proposal.json", root / "infra/images.lock.json"]
    expected_hashes = {str(path.relative_to(root)): builder.digest(path) for path in expected_inputs}
    require(receipt.get("input_hashes") == expected_hashes, "Derived build input hashes changed or incomplete")
    for path in expected_inputs:
        bind(path, expected_hashes[str(path.relative_to(root))])
    for field in ("parent_platform_manifest", "recipe_sha256", "authored_replacement_sha256"):
        require(receipt.get(field) == policy[field], "Derived receipt does not match authorized recipe/parent")
    require(receipt.get("parent_index_digest") == pin["index_digest"], "Derived parent index changed")
    require(receipt.get("parent_manifest_path") == PATHS["parent_manifest"] and receipt.get("parent_config_path") == PATHS["parent_config"], "Raw immutable parent metadata paths missing")
    require("sha256:" + builder.digest(paths["parent_manifest"]) == policy["parent_platform_manifest"], "Raw parent manifest digest mismatch")
    parent_manifest = json.loads(paths["parent_manifest"].read_text())
    require("sha256:" + builder.digest(paths["parent_config"]) == receipt.get("parent_config_digest") == parent_manifest["config"]["digest"], "Raw parent config digest mismatch")
    parent_config = json.loads(paths["parent_config"].read_text())
    require(not parent_config.get("config", {}).get("OnBuild"), "Parent ONBUILD is forbidden")
    actual = builder.inspect_archive(paths["archive"], parent_manifest, parent_config)
    require(all(receipt.get(key) == value for key, value in actual.items()), "Derived archive identity/config/lineage differs from build receipt")
    files = json.loads(paths["files_receipt"].read_text())
    require(inspector.inspect_artifact(directory, write=False) == files, "Derived COPY/entrypoint proof differs on read-only replay")
    require(files.get("initdb_inputs") == [] and files.get("debian_wrappers") == [], "Unexpected inherited initdb/helper input")
    require(files.get("stub_sha256") == policy["authored_replacement_sha256"] and files.get("archive_sha256") == receipt["archive_sha256"], "Derived COPY proof identity mismatch")
    entrypoint = directory / "postgres-entrypoint-source.txt"
    bind(entrypoint, files["entrypoint_sha256"])
    config_bytes = builder.archive_member(paths["archive"], "blobs/sha256/" + actual["config_digest"].split(":", 1)[1])
    rootfs = json.loads(config_bytes)["rootfs"]["diff_ids"]
    return {"type": "derived-oci", "reference": "oci-archive:" + PATHS["archive"], "archive_path": PATHS["archive"],
            "archive_sha256": receipt["archive_sha256"], "platform_manifest_digest": actual["platform_manifest_digest"],
            "config_digest": actual["config_digest"], "rootfs_diff_ids": rootfs, "platform": actual["platform"], "user": actual["user"],
            "parent_platform_manifest": policy["parent_platform_manifest"], "parent_index_digest": pin["index_digest"]}


def validate_source(metadata, runtime, root):
    require(isinstance(metadata, dict), "Derived image metadata missing")
    require(metadata.get("manifestDigest") == runtime["platform_manifest_digest"] and metadata.get("imageID") == runtime["config_digest"], "Derived scanner source manifest/config identity mismatch")
    require(metadata.get("architecture") == "amd64" and metadata.get("os") == "linux", "Derived scanner source platform mismatch")
    source = metadata.get("userInput", "")
    if source.startswith("oci-archive:"):
        source = source[len("oci-archive:"):]
    require(bool(source), "Derived scanner archive source missing")
    path = Path(source)
    actual = path.resolve() if path.is_absolute() else (root / path).resolve()
    require(actual == (root / runtime["archive_path"]).resolve(), "Derived source was relabeled or substituted")
    for name, expected in (("manifest", runtime["platform_manifest_digest"]), ("config", runtime["config_digest"])):
        try:
            data = base64.b64decode(metadata[name])
        except (KeyError, TypeError, ValueError):
            raise ValueError("Derived scanner raw " + name + " is malformed") from None
        require("sha256:" + hashlib.sha256(data).hexdigest() == expected, "Derived scanner raw " + name + " digest mismatch")
