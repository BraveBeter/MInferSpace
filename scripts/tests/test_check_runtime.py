"""Regression checks for the E2E runtime CLI without an NVIDIA device."""

import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "check_runtime.py"


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.checkout = self.root / "checkout"
        self.install = self.root / "install"
        self.install.mkdir()
        self.add_package(self.checkout)
        self.git("init", "-q")
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")
        self.deployment = self.root / "deployment.json"
        self.write_deployment()
        smi = self.install / "nvidia-smi"
        smi.write_text(
            '#!/bin/sh\ncase "$1" in\n'
            "  --id=0) echo '0, GPU-SELECTED, 75, 1400, 1000';;\n"
            "  --id=1) echo '1, GPU-SECOND, 68, 1350, 1000';;\n"
            '  --query-compute-apps=*) printf "%s" "$FIXTURE_APPS";;\n'
            '  *) exit 1;;\nesac\n'
        )
        smi.chmod(0o755)

    def git(self, *args):
        return subprocess.check_output([
            "git", "-C", str(self.checkout), "-c", "user.name=Fixture",
            "-c", "user.email=fixture@example.test", *args,
        ], text=True).strip()

    @staticmethod
    def add_package(directory):
        package = directory / "sglang_omni"
        package.mkdir(parents=True)
        (package / "__init__.py").touch()

    def write_deployment(self, gpu_count=1):
        self.deployment.write_text(json.dumps({
            "server": {"commit": self.git("rev-parse", "HEAD"), "dirty": False},
            "hardware": {"gpu_count": gpu_count},
        }))

    def run_check(self, *args, processes=""):
        result = subprocess.run([
            sys.executable, str(SCRIPT), "--output-dir", str(self.root / "run"), "e2e",
            "--deployment", str(self.deployment), "--source", str(self.checkout), "--gpu", "0",
            *args,
        ], cwd=self.checkout, env={
            **os.environ, "PATH": str(self.install) + os.pathsep + os.environ["PATH"],
            "PYTHONPATH": "", "PYTHONDONTWRITEBYTECODE": "1", "FIXTURE_APPS": processes,
        }, text=True, capture_output=True)
        log = next((self.root / "run/execution").glob("preflight-*.json"))
        return result.returncode, json.loads(log.read_text())

    def test_module_launch_uses_checkout(self):
        code, record = self.run_check()
        self.assertEqual(code, 0, record)
        self.assertEqual(record["source"]["module_path"], str(self.checkout / "sglang_omni/__init__.py"))

    def test_console_script_import_shadowing_fails(self):
        self.add_package(self.install)
        launcher = self.install / "sgl-omni"
        launcher.write_text("import sglang_omni\n")
        code, record = self.run_check("--launcher", str(launcher))
        self.assertEqual(code, 1)
        self.assertIn("outside the expected source package", record["error"])
        self.assertEqual(record["source"]["module_path"], str(self.install / "sglang_omni/__init__.py"))

    def test_gpu_count_must_match_deployment(self):
        self.write_deployment(gpu_count=2)
        code, record = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("deployment.hardware.gpu_count", record["error"])

    def test_selected_service_pid_on_additional_gpu_fails(self):
        code, record = self.run_check(
            "--allow-gpu-pid", "42", processes="GPU-SELECTED, 42\nGPU-OTHER, 42\n"
        )
        self.assertEqual(code, 1)
        self.assertEqual(record["service_pids_on_other_gpus"], [{"uuid": "GPU-OTHER", "pid": 42}])

    def test_two_idle_gpus_before_launch_pass(self):
        self.write_deployment(gpu_count=2)
        code, record = self.run_check("--gpu", "1")
        self.assertEqual(code, 0, record)

    def test_ready_service_missing_from_second_gpu_fails(self):
        self.write_deployment(gpu_count=2)
        code, record = self.run_check("--gpu", "1", "--allow-gpu-pid", "42", processes="GPU-SELECTED, 42")
        self.assertEqual(code, 1, record)
        self.assertIn("No service worker on GPU 1", record["error"])

    def test_ready_service_on_both_gpus_passes(self):
        self.write_deployment(gpu_count=2)
        code, record = self.run_check(
            "--gpu", "1", "--allow-gpu-pid", "42", "--allow-gpu-pid", "43",
            processes="GPU-SELECTED, 42\nGPU-SECOND, 43",
        )
        self.assertEqual(code, 0, record)


if __name__ == "__main__":
    unittest.main()
