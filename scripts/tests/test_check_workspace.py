"""Regression checks for workspace links, profile indexing, and staged scanning."""

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

    def profile_run(self, commit, run_id="20261117T120000Z-nsys"):
        profiles = self.root / "profile-results"
        relative = Path(f"fix~example-{commit}") / run_id
        run = profiles / relative
        run.mkdir(parents=True)
        (run / "analysis.md").write_text("# Profile evidence\n")
        return relative.as_posix()

    def check_profiles(self, *rows):
        index = self.root / "profile-results/README.md"
        index.write_text(
            "| 源码分支 | 完整 commit | 采集目录 | 工具 | 用途 |\n"
            "| --- | --- | --- | --- | --- |\n"
            + "".join(
                f"| {branch} | {commit} | [采集]({directory}/) | nsys | Exploration |\n"
                for branch, commit, directory in rows
            )
        )
        problems = []
        CHECKER.check_profile_index(self.root, lambda *problem: problems.append(problem))
        return [message for _, _, message in problems]

    def test_profiles_without_strategies_allow_same_branch_and_run_id_at_multiple_shas(self):
        commits = ["a" * 40, "b" * 40]
        rows = [("fix/example", commit, self.profile_run(commit)) for commit in commits]
        self.assertEqual(self.check_profiles(*rows), [])

    def test_profile_directory_must_match_branch_and_full_commit(self):
        commit = "a" * 40
        directory = self.profile_run(commit)
        self.assertEqual(
            self.check_profiles(
                ("fix/other", commit, directory),
                ("fix/example", "b" * 40, directory),
                ("fix/example", commit[:8], directory),
            ),
            [
                "profile directory link must match the source branch and full SHA",
                "profile directory link must match the source branch and full SHA",
                "profile commit must be a full Git SHA",
            ],
        )

    def test_profile_run_id_and_duplicate_directory(self):
        commit = "a" * 40
        good = self.profile_run(commit, "20261117T120000Z-nsys-02")
        wrong_tool = self.profile_run(commit, "20261117T120000Z-perf")
        self.assertEqual(
            self.check_profiles(
                ("fix/example", commit, good),
                ("fix/example", commit, "./" + good),
                ("fix/example", commit, wrong_tool),
            ),
            [
                "duplicate profile directory in index",
                "profile run ID must contain the UTC start time and tool name",
            ],
        )


if __name__ == "__main__":
    unittest.main()
