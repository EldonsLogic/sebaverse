"""Synthetic OCI/recipe guards; no Docker, image execution or network calls."""
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
import urllib.request
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("postgres_candidate_test", ROOT / "tools/security/build_postgres_candidate.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def encoded(value):
    return json.dumps(value, sort_keys=True).encode()


def descriptor(data):
    return {"digest": "sha256:" + hashlib.sha256(data).hexdigest(), "size": len(data)}


class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.context = self.root / "infra/local/postgres"
        self.context.mkdir(parents=True)
        for name in ("Dockerfile", "gosu-disabled.sh", "proposal.json", "README.md"):
            (self.context / name).write_bytes((ROOT / "infra/local/postgres" / name).read_bytes())
        (self.root / "infra/images.lock.json").write_bytes((ROOT / "infra/images.lock.json").read_bytes())
        self.archive = self.root / "synthetic.oci.tar"
        self.parent_config = {"os": "linux", "architecture": "amd64", "config": {"Entrypoint": ["/synthetic-entrypoint"], "Cmd": ["postgres"], "Env": ["SYNTHETIC=1"]}, "rootfs": {"type": "layers", "diff_ids": ["sha256:" + "a" * 64]}}
        self.layer = b"synthetic parent layer; not executable"
        self.parent_manifest = {"config": descriptor(encoded(self.parent_config)), "layers": [descriptor(self.layer)]}

    def tearDown(self):
        self.temp.cleanup()

    def write_archive(self, config_change=None, index_change=None, additional=None, tamper_blob=False):
        config = copy.deepcopy(self.parent_config)
        config["config"]["User"] = "postgres"
        config["rootfs"]["diff_ids"].append("sha256:" + "b" * 64)
        if config_change:
            config_change(config)
        config_bytes = encoded(config)
        stub = b"synthetic authored COPY layer; not executable"
        manifest = {"schemaVersion": 2, "config": descriptor(config_bytes), "layers": [*self.parent_manifest["layers"], descriptor(stub)]}
        manifest_bytes = encoded(manifest)
        image = {**descriptor(manifest_bytes), "platform": {"os": "linux", "architecture": "amd64"}}
        index = {"schemaVersion": 2, "manifests": [image]}
        if index_change:
            index_change(index)
        members = {"oci-layout": encoded({"imageLayoutVersion": "1.0.0"}), "index.json": encoded(index)}
        for value in (self.layer, stub, config_bytes, manifest_bytes):
            members["blobs/sha256/" + hashlib.sha256(value).hexdigest()] = value
        if tamper_blob:
            members["blobs/sha256/" + hashlib.sha256(stub).hexdigest()] = b"tampered synthetic bytes"
        with tarfile.open(self.archive, "w") as output:
            for name, value in members.items():
                info = tarfile.TarInfo(name)
                info.size = len(value)
                output.addfile(info, io.BytesIO(value))
            if additional:
                info = tarfile.TarInfo(additional)
                info.size = 1
                output.addfile(info, io.BytesIO(b"x"))
        return image

    def test_registry_redirect_does_not_forward_bearer_to_cdn(self):
        request = urllib.request.Request('https://registry-1.docker.io/v2/library/postgres/blobs/synthetic',
                                         headers={'Authorization': 'Bearer synthetic-test-token'})
        redirected = module.RegistryRedirect().redirect_request(request, None, 302, 'Found', {}, 'https://cdn.example.invalid/blob')
        self.assertIsNone(redirected.get_header('Authorization'))
        same = module.RegistryRedirect().redirect_request(request, None, 302, 'Found', {}, 'https://registry-1.docker.io/next')
        self.assertEqual(same.get_header('Authorization'), 'Bearer synthetic-test-token')
        with self.assertRaisesRegex(ValueError, 'HTTPS'):
            module.RegistryRedirect().redirect_request(request, None, 302, 'Found', {}, 'http://cdn.example.invalid/blob')

    def test_exact_authored_recipe_and_source_pin_pass(self):
        context, proposal, pin = module.recipe(self.root)
        self.assertEqual(context, self.context)
        self.assertEqual(proposal["platform"], "linux/amd64")
        self.assertIn(proposal["parent_platform_manifest"], [p["digest"] for p in pin["platforms"]])

    def test_changed_recipe_or_stub_fails(self):
        for filename in ("Dockerfile", "gosu-disabled.sh"):
            with self.subTest(filename=filename):
                original = (self.context / filename).read_bytes()
                (self.context / filename).write_bytes(original + b"\n# changed\n")
                with self.assertRaisesRegex(ValueError, "hashes changed"):
                    module.recipe(self.root)
                (self.context / filename).write_bytes(original)

    def test_run_is_rejected_even_if_proposal_hash_is_updated(self):
        path = self.context / "Dockerfile"
        path.write_text(path.read_text() + "\nRUN synthetic-forbidden-command\n")
        proposal = json.loads((self.context / "proposal.json").read_text())
        proposal["recipe_sha256"] = module.digest(path)
        (self.context / "proposal.json").write_text(json.dumps(proposal))
        with self.assertRaisesRegex(ValueError, "no RUN"):
            module.recipe(self.root)

    def test_custom_parser_is_rejected_even_with_matching_hash(self):
        path = self.context / "Dockerfile"
        path.write_text("# syntax=unreviewed/frontend\n" + path.read_text())
        proposal = json.loads((self.context / "proposal.json").read_text())
        proposal["recipe_sha256"] = module.digest(path)
        (self.context / "proposal.json").write_text(json.dumps(proposal))
        with self.assertRaisesRegex(ValueError, "parser directives"):
            module.recipe(self.root)

    def test_parent_substitution_fails(self):
        proposal = json.loads((self.context / "proposal.json").read_text())
        proposal["parent_platform_manifest"] = "sha256:" + "f" * 64
        (self.context / "proposal.json").write_text(json.dumps(proposal))
        with self.assertRaisesRegex(ValueError, "reviewed image pin"):
            module.recipe(self.root)

    def test_valid_synthetic_archive_has_bound_platform_config_and_user(self):
        image = self.write_archive()
        result = module.inspect_archive(self.archive, self.parent_manifest, self.parent_config)
        self.assertEqual(result["platform_manifest_digest"], image["digest"])
        self.assertEqual(result["user"], "postgres")
        self.assertTrue(result["parent_layer_prefix_verified"])

    def test_changed_blob_is_rejected(self):
        self.write_archive(tamper_blob=True)
        with self.assertRaisesRegex(ValueError, "blob digest mismatch"):
            module.inspect_archive(self.archive, self.parent_manifest, self.parent_config)

    def test_unsafe_tar_path_is_rejected_without_extraction(self):
        self.write_archive(additional="../../outside")
        with self.assertRaisesRegex(ValueError, "Unsafe OCI member"):
            module.inspect_archive(self.archive, self.parent_manifest, self.parent_config)
        self.assertFalse((self.root.parent / "outside").exists())

    def test_wrong_user_or_architecture_is_rejected(self):
        for key, value in (("user", "root"), ("architecture", "arm64")):
            with self.subTest(key=key):
                self.write_archive(config_change=lambda c: c["config"].update(User=value) if key == "user" else c.update(architecture=value))
                with self.assertRaisesRegex(ValueError, "platform/User"):
                    module.inspect_archive(self.archive, self.parent_manifest, self.parent_config)

    def test_inherited_entrypoint_change_is_rejected(self):
        self.write_archive(config_change=lambda c: c["config"].update(Entrypoint=["/different"]))
        with self.assertRaisesRegex(ValueError, "inherited config"):
            module.inspect_archive(self.archive, self.parent_manifest, self.parent_config)

    def test_multiple_platform_manifests_are_rejected(self):
        self.write_archive(index_change=lambda i: i["manifests"].append(copy.deepcopy(i["manifests"][0])))
        with self.assertRaisesRegex(ValueError, "One OCI platform"):
            module.inspect_archive(self.archive, self.parent_manifest, self.parent_config)

    def test_onbuild_parent_stops_before_docker_execution(self):
        parent = copy.deepcopy(self.parent_config)
        parent["config"]["OnBuild"] = ["RUN synthetic-forbidden-command"]
        with patch.object(module, "fetch_parent", return_value=(self.parent_manifest, parent)), patch.object(module.subprocess, "run") as command:
            with self.assertRaisesRegex(ValueError, "ONBUILD"):
                module.build(self.root)
            command.assert_not_called()

    def test_static_build_command_and_receipt_never_clear_image(self):
        image = self.write_archive()
        def fake_command(args, **kwargs):
            if args[-1] == "version":
                return type("Result", (), {"stdout": "synthetic buildx test version"})()
            target = self.root / "work/f2-security/postgres-derived.oci.tar"
            target.write_bytes(self.archive.read_bytes())
            self.assertIn("--network", args)
            self.assertIn("none", args)
            self.assertIn("--provenance=false", args)
            self.assertIn("--sbom=false", args)
            self.assertNotIn("--load", args)
            self.assertNotIn("run", args)
        with patch.object(module, "fetch_parent", return_value=(self.parent_manifest, self.parent_config)), patch.object(module.subprocess, "run", side_effect=fake_command):
            result = module.build(self.root)
        self.assertEqual(result["status"], "built_static_not_cleared")
        self.assertEqual(result["platform_manifest_digest"], image["digest"])
        self.assertEqual(result["archive_sha256"], module.digest(self.root / result["archive_path"]))


if __name__ == "__main__":
    unittest.main()
