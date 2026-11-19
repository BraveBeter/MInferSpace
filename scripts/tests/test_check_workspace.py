"""Regression checks for workspace links, file scanning, and task indexes."""

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

    def test_lfs_worktree_size_exception_still_checks_credentials_and_staged_size(self):
        (self.root / ".gitattributes").write_text("/input.jsonl filter=lfs\n")
        path = self.root / "input.jsonl"
        path.write_bytes(b"x" * CHECKER.MAX_SIZE + b"\n" + b"ghp_" + b"x" * 36 + b"\n")
        problems = []
        report = lambda *problem: problems.append(problem)

        self.assertTrue(CHECKER.scan_file(self.root, path, report))
        self.assertEqual(problems, [(path, 2, "possible credential (GitHub token)")])

        problems.clear()
        subprocess.run(
            ["git", "-C", str(self.root), "-c", "filter.lfs.process=", "-c", "filter.lfs.clean=",
             "-c", "filter.lfs.required=false", "add", path.name],
            check=True,
        )
        CHECKER.check_staged_files(self.root, report)
        self.assertEqual(problems, [(path, None, "file exceeds 10 MiB")])


class TaskIndexTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.adaptation = self.write_task("ADP-0001", "support-model", "in-progress")
        self.optimization = self.write_task("OPT-0001", "reduce-latency", "blocked")

    def write_task(self, number, name, state, extra="", declared_number=None):
        task = Path("tasks") / f"{number}-{name}" / "task.md"
        destination = self.root / task
        destination.parent.mkdir(parents=True, exist_ok=True)
        stored_number = number if declared_number is None else declared_number
        destination.write_text(
            f"# Test task\n\n| 字段 | 值 |\n| --- | --- |\n"
            f"| 任务编号 | {stored_number} |\n| 状态 | `{state}` |\n\n{extra}",
            encoding="utf-8",
        )
        return task

    def write_plan(self, *rows):
        plan = "| 任务编号 | 任务文档 |\n| --- | --- |\n"
        for number, path in rows:
            plan += f"| {number} | [Task]({path.as_posix()}) |\n"
        (self.root / "PLAN.md").write_text(plan, encoding="utf-8")

    def write_active_plan(self):
        self.write_plan(("ADP-0001", self.adaptation), ("OPT-0001", self.optimization))

    def test_two_task_types_and_valid_evidence_pass(self):
        report = self.root / "benchmark-results" / "report.md"
        report.parent.mkdir()
        report.write_text("# Result\n", encoding="utf-8")
        self.write_task("ADP-0001", "support-model", "in-progress",
                        "[Evidence](../../benchmark-results/report.md#result)\n")
        self.write_active_plan()
        self.assertEqual(CHECKER.check_workspace(self.root), [])

    def test_duplicate_task_id_and_plan_row_are_reported(self):
        self.write_task("ADP-0001", "other-support", "planned")
        self.write_plan(("ADP-0001", self.adaptation), ("ADP-0001", self.adaptation),
                        ("OPT-0001", self.optimization))
        problems = "\n".join(CHECKER.check_workspace(self.root))
        self.assertIn("duplicate task ID ADP-0001", problems)
        self.assertIn("duplicate plan row for ADP-0001", problems)

    def test_missing_active_row_is_reported(self):
        self.write_plan(("ADP-0001", self.adaptation))
        self.assertIn("PLAN.md: missing plan row for OPT-0001", CHECKER.check_workspace(self.root))

    def test_closed_tasks_must_be_omitted(self):
        self.write_task("ADP-0001", "support-model", "done")
        self.write_task("OPT-0001", "reduce-latency", "cancelled")
        self.write_active_plan()
        problems = "\n".join(CHECKER.check_workspace(self.root))
        self.assertIn("closed task ADP-0001", problems)
        self.assertIn("closed task OPT-0001", problems)
        self.write_plan()
        self.assertEqual(CHECKER.check_workspace(self.root), [])

    def test_invalid_state_and_mismatched_id_are_reported(self):
        self.write_task("ADP-0001", "support-model", "finished", declared_number="ADP-0012")
        self.write_active_plan()
        problems = "\n".join(CHECKER.check_workspace(self.root))
        self.assertIn("任务编号 must match directory ID ADP-0001", problems)
        self.assertIn("状态 must be", problems)

    def test_wrong_plan_target_and_broken_evidence_link_are_reported(self):
        self.write_task("ADP-0001", "support-model", "in-progress", "[Evidence](missing.md)\n")
        self.write_plan(("ADP-0001", self.optimization), ("OPT-0001", self.optimization))
        problems = "\n".join(CHECKER.check_workspace(self.root))
        self.assertIn("plan link for ADP-0001 must target its task.md", problems)
        self.assertIn("missing relative Markdown link target", problems)


if __name__ == "__main__":
    unittest.main()
