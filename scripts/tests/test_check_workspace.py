"""Regression checks for relocatable Markdown links and staged scanning."""

import importlib.util
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "check_workspace.py"
SPEC = importlib.util.spec_from_file_location("check_workspace", SCRIPT)
CHECKER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / ".gitignore").write_text("/run/raw/\n")
        (self.root / "run/raw").mkdir(parents=True)
        (self.root / "run/raw/trace.txt").touch()
        (self.root / "run/manifest.json").write_text("{}\n")
        self.readme = self.root / "README.md"

    def check_link(self, destination):
        self.readme.write_text(f"[Evidence]({destination})\n")
        paths = CHECKER.git_paths(self.root, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
        available = CHECKER.available_link_targets(self.root, paths)
        problems = []
        CHECKER.check_links(self.root, self.readme, available, lambda *problem: problems.append(problem))
        return problems

    def test_local_ignored_file_and_its_directory_are_rejected(self):
        for target in ("run/raw/trace.txt", "run/raw/"):
            with self.subTest(target=target):
                self.assertEqual(self.check_link(target), [
                    (self.readme, 1, "relative Markdown link target would be absent from a clone")
                ])

    def test_git_visible_manifest_and_its_directory_are_allowed(self):
        self.assertEqual(self.check_link("run/manifest.json"), [])
        self.assertEqual(self.check_link("run/"), [])

    def test_staged_credential_detected_with_clean_working_copy(self):
        path = self.root / "staged.txt"
        path.write_text("ghp_" + "x" * 36 + "\n")
        subprocess.run(["git", "-C", str(self.root), "add", path.name], check=True)
        path.write_text("redacted\n")
        problems = []
        CHECKER.check_staged_files(self.root, lambda *problem: problems.append(problem))
        self.assertEqual(problems, [(path, 1, "possible credential (GitHub token)")])


if __name__ == "__main__":
    unittest.main()
