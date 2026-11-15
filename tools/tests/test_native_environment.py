"""Loader-environment guards; synthetic values and mocked downstream I/O only.

No subprocess is launched under a loader override. No database, Docker daemon,
scanner, ELF inspection or native binding is executed by this suite.
"""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


native = load("native_inventory_environment_test", "tools/security/native_chain.py")
runner = load("postgres_runner_environment_test", "tools/run_postgres_smoke.py")
OVERRIDES = (
    "LD_LIBRARY_PATH", "LD_PRELOAD", "LD_AUDIT",
    "DYLD_LIBRARY_PATH", "DYLD_FALLBACK_LIBRARY_PATH", "DYLD_INSERT_LIBRARIES",
    "DYLD_FRAMEWORK_PATH", "DYLD_FALLBACK_FRAMEWORK_PATH", "DYLD_ROOT_PATH",
    "DYLD_UNKNOWN_FUTURE_OVERRIDE",
)


class InspectionReached(Exception):
    """A mocked post-guard boundary, never real native inspection."""


class NativeEnvironmentTests(unittest.TestCase):
    def test_clean_environment_is_accepted_by_both_guards(self):
        for module in (native, runner):
            with self.subTest(module=module.__name__):
                self.assertIsNone(module.validate_loader_environment({}))
                self.assertIsNone(module.validate_loader_environment({"PATH": "/synthetic", "PSYCOPG_IMPL": "python"}))

    def test_empty_override_values_do_not_redirect_loader(self):
        for module in (native, runner):
            with self.subTest(module=module.__name__):
                self.assertIsNone(module.validate_loader_environment(dict.fromkeys(OVERRIDES, "")))

    def test_each_nonempty_override_is_rejected_without_echoing_value(self):
        for name in OVERRIDES:
            for module, exception in ((native, RuntimeError), (runner, ValueError)):
                with self.subTest(variable=name, module=module.__name__):
                    with self.assertRaisesRegex(exception, "Dynamic-loader overrides") as caught:
                        module.validate_loader_environment({name: "/synthetic/private-loader-location"})
                    self.assertNotIn("private-loader-location", str(caught.exception))

    def test_whitespace_is_nonempty_and_is_rejected(self):
        for module, exception in ((native, RuntimeError), (runner, ValueError)):
            with self.subTest(module=module.__name__):
                with self.assertRaises(exception):
                    module.validate_loader_environment({"LD_LIBRARY_PATH": " "})

    def test_inventory_rejects_overrides_before_file_or_native_inspection(self):
        for name in OVERRIDES:
            with self.subTest(variable=name), patch.dict(native.os.environ, {name: "/synthetic"}, clear=True), \
                    patch.object(native.Path, "read_text") as read, patch.object(native, "locate_libpq") as locate, \
                    patch.object(native, "run") as command:
                with self.assertRaisesRegex(RuntimeError, "Dynamic-loader overrides"):
                    native.inventory(Path("/synthetic/output"))
                read.assert_not_called()
                locate.assert_not_called()
                command.assert_not_called()

    def test_inventory_clean_environment_reaches_mocked_inspection(self):
        with patch.dict(native.os.environ, {}, clear=True), patch.object(native.sys, "platform", "linux"), \
                patch.object(native.Path, "read_text", side_effect=InspectionReached) as read, \
                patch.object(native, "run") as command:
            with self.assertRaises(InspectionReached):
                native.inventory(Path("/synthetic/output"))
            read.assert_called_once()
            command.assert_not_called()

    def test_preuse_rejects_each_override_before_reading_or_binding(self):
        for name in OVERRIDES:
            with self.subTest(variable=name), patch.dict(runner.os.environ, {name: "/synthetic"}, clear=True), \
                    patch.object(runner.Path, "read_text") as read, patch.object(runner, "sha256") as hashing, \
                    patch.object(runner, "run") as command:
                with self.assertRaisesRegex(ValueError, "Dynamic-loader overrides"):
                    runner.verify_preuse(ROOT)
                read.assert_not_called()
                hashing.assert_not_called()
                command.assert_not_called()

    def test_preuse_clean_environment_reaches_mocked_evidence_read(self):
        with patch.dict(runner.os.environ, {}, clear=True), \
                patch.object(runner.Path, "read_text", side_effect=InspectionReached) as read, \
                patch.object(runner, "run") as command:
            with self.assertRaises(InspectionReached):
                runner.verify_preuse(ROOT)
            read.assert_called_once()
            command.assert_not_called()


if __name__ == "__main__":
    unittest.main()
