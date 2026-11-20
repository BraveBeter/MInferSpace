"""Unit tests for framework/tools/ws.py."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent
FRAMEWORK_DIR = TOOLS_DIR.parent
sys.path.insert(0, str(TOOLS_DIR))

import ws  # noqa: E402


class TestWS(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ws-test-"))
        shutil.copytree(FRAMEWORK_DIR, self.tmp / "framework")
        self.orig_cwd = Path.cwd()
        os.chdir(self.tmp)

    def tearDown(self) -> None:
        os.chdir(self.orig_cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run_ws(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(self.tmp / "framework" / "tools" / "ws.py"), *args],
            cwd=str(self.tmp),
            text=True,
            capture_output=True,
        )

    def test_init_and_lint_clean(self) -> None:
        r = self._run_ws("init", ".", "--name", "demo-model on sglang")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertTrue((self.tmp / "PROJECT.md").is_file())
        self.assertIn("demo-model on sglang", (self.tmp / "PROJECT.md").read_text(encoding="utf-8"))

        lint = self._run_ws("lint")
        self.assertEqual(lint.returncode, 0, lint.stdout + lint.stderr)

    def test_new_all_types_and_pipe_summary_passes_lint(self) -> None:
        self._run_ws("init", ".")
        sha = "a" * 40
        for kind, slug, summary in (
            ("opt", "codec-cuda-graph", "为 codec 开启 CUDA Graph | 首包优化"),
            ("adapt", "demo-base", "基础模型适配"),
            ("fix", "eos-bug", "修复提前输出 EOS"),
            ("res", "spec-decode", "调研投机解码可行性"),
        ):
            r = self._run_ws("new", kind, slug, "--summary", summary, "--from-commit", sha)
            self.assertEqual(r.returncode, 0, r.stderr + r.stdout)

        # Verify res also receives --from-commit
        res_md = self.tmp / "work" / "RES-0001-spec-decode" / "item.md"
        self.assertIn(sha, res_md.read_text(encoding="utf-8"))

        lint = self._run_ws("lint")
        self.assertEqual(lint.returncode, 0, lint.stdout + lint.stderr)

    def test_gate_write_rewrites_relative_links_and_keeps_lint_clean(self) -> None:
        self._run_ws("init", ".")
        sha = "b" * 40
        self._run_ws("new", "adapt", "demo-base", "--from-commit", sha)

        # A7 gate contains [code-quality.md](code-quality.md); writing must rewrite it cleanly
        self._run_ws("gate", "ADP-0001", "--phase", "A7", "--write")
        item_text = (self.tmp / "work" / "ADP-0001-demo-base" / "item.md").read_text(encoding="utf-8")
        self.assertIn("[code-quality.md](../../framework/gates/code-quality.md)", item_text)

        lint = self._run_ws("lint")
        self.assertEqual(lint.returncode, 0, lint.stdout + lint.stderr)

    def test_phase_aware_benchmark_and_validation_gates(self) -> None:
        self._run_ws("init", ".")
        sha = "c" * 40
        self._run_ws("new", "opt", "baseline", "--id", "OPT-0000", "--from-commit", sha)
        self._run_ws("new", "opt", "fast-path", "--from-commit", sha)

        # Create indexed baseline under OPT-0000
        b_dir = self._run_ws("run-dir", "OPT-0000", "e2e", "baseline", "--utc", "20261120T060000Z").stdout.strip()
        b_readme = self.tmp / "benchmark-results" / "README.md"
        b_readme.write_text(
            b_readme.read_text(encoding="utf-8").replace(
                "| 暂无 | — | — | — | — | — |",
                f"| OPT-0000 | [{Path(b_dir).name}](OPT-0000/{Path(b_dir).name}/) | e2e | baseline | ok | — |",
            ),
            encoding="utf-8",
        )
        # OPT-0001 references OPT-0000 baseline
        item_md = self.tmp / "work" / "OPT-0001-fast-path" / "item.md"
        item_md.write_text(
            item_md.read_text(encoding="utf-8").replace("- **基线评测链接**：待填写", f"- **基线评测链接**：`{b_dir}`"),
            encoding="utf-8",
        )

        # O1 should PASS via baseline reuse, but O5 MUST FAIL without a candidate run!
        g1 = self._run_ws("gate", "OPT-0001", "--phase", "O1")
        self.assertEqual(g1.returncode, 0, g1.stdout + g1.stderr)
        g5_fail = self._run_ws("gate", "OPT-0001", "--phase", "O5")
        self.assertNotEqual(g5_fail.returncode, 0)

        # Adding indexed candidate makes O5 PASS
        c_dir = self._run_ws("run-dir", "OPT-0001", "e2e", "candidate", "--utc", "20261120T070000Z").stdout.strip()
        b_readme.write_text(
            b_readme.read_text(encoding="utf-8").replace(
                "<!-- ws:benchmark-index:end -->",
                f"| OPT-0001 | [{Path(c_dir).name}](OPT-0001/{Path(c_dir).name}/) | e2e | candidate | ok | — |\n<!-- ws:benchmark-index:end -->",
            ),
            encoding="utf-8",
        )
        g5_ok = self._run_ws("gate", "OPT-0001", "--phase", "O5")
        self.assertEqual(g5_ok.returncode, 0, g5_ok.stdout + g5_ok.stderr)

        # FIX F0 (baseline) must not satisfy F3 (candidate)
        self._run_ws("new", "fix", "eos-bug", "--from-commit", sha)
        v_base = self._run_ws("run-dir", "FIX-0001", "align", "baseline", "--kind", "validation", "--utc", "20261120T060000Z").stdout.strip()
        (self.tmp / v_base / "report.md").write_text("# base\n", encoding="utf-8")
        v_readme = self.tmp / "validation-results" / "README.md"
        v_readme.write_text(
            v_readme.read_text(encoding="utf-8").replace(
                "| 暂无 | — | — | — | — | — |",
                f"| FIX-0001 | [{Path(v_base).name}](FIX-0001/{Path(v_base).name}/report.md) | align | baseline | FAIL | repro |",
            ),
            encoding="utf-8",
        )
        self.assertEqual(self._run_ws("gate", "FIX-0001", "--phase", "F0").returncode, 0)
        self.assertNotEqual(self._run_ws("gate", "FIX-0001", "--phase", "F3").returncode, 0)

    def test_run_dir_record_and_lint_evidence(self) -> None:
        self._run_ws("init", ".")
        self._run_ws("new", "adapt", "demo-base")

        rd = self._run_ws("run-dir", "ADP-0001", "align", "candidate", "--kind", "validation", "--utc", "20261120T060000Z")
        self.assertEqual(rd.returncode, 0, rd.stderr + rd.stdout)
        rel_dir = rd.stdout.strip()
        self.assertEqual(rel_dir, "validation-results/ADP-0001/20261120T060000Z-align-candidate")

        # Collision handling appends -02
        rd2 = self._run_ws("run-dir", "ADP-0001", "align", "candidate", "--kind", "validation", "--utc", "20261120T060000Z")
        self.assertEqual(rd2.stdout.strip(), rel_dir + "-02")
        shutil.rmtree(self.tmp / (rel_dir + "-02"))

        rec = self._run_ws("record", rel_dir, "--cmd", "python align.py", "--env-var", "HF_TOKEN", "--pkg", "json")
        self.assertEqual(rec.returncode, 0, rec.stderr + rec.stdout)
        rec_data = json.loads((self.tmp / rel_dir / "execution" / "ws-record.json").read_text(encoding="utf-8"))
        self.assertEqual(rec_data["cwd_rel"], ".")
        self.assertEqual(rec_data["env_var_names"], ["HF_TOKEN"])

        # Without report.md and index entry, lint must fail
        self.assertNotEqual(self._run_ws("lint").returncode, 0)

        (self.tmp / rel_dir / "report.md").write_text("# report\n", encoding="utf-8")
        v_readme = self.tmp / "validation-results" / "README.md"
        v_readme.write_text(
            v_readme.read_text(encoding="utf-8").replace(
                "| 暂无 | — | — | — | — | — |",
                "| ADP-0001 | [20261120T060000Z-align-candidate](ADP-0001/20261120T060000Z-align-candidate/report.md) | align | candidate | PASS | — |",
            ),
            encoding="utf-8",
        )
        lint_ok = self._run_ws("lint")
        self.assertEqual(lint_ok.returncode, 0, lint_ok.stdout + lint_ok.stderr)

    def test_lint_catches_errors_and_backtick_decision_valid(self) -> None:
        self._run_ws("init", ".")
        self.assertTrue(ws.decision_is_valid("`n/a`（调研项不交付代码）"))
        self.assertTrue(ws.decision_is_valid("keep-local（已执行）"))
        self.assertFalse(ws.decision_is_valid("待定"))

        self._run_ws("new", "opt", "test-item")
        # Mismatch phase in PLAN.md
        plan = self.tmp / "PLAN.md"
        plan.write_text(plan.read_text(encoding="utf-8").replace("O0 / planned", "O3 / planned"), encoding="utf-8")
        # Dead link + absolute path link
        (self.tmp / "knowledge" / "model.md").write_text(
            "[broken](does-not-exist.md)\n[abs](/etc/hosts)\n", encoding="utf-8"
        )
        # Floating version
        cp = self.tmp / "checkpoints" / "README.md"
        cp.write_text(
            cp.read_text(encoding="utf-8").replace(
                "| 暂无 | — | — | — | — |",
                "| demo | eval | https://example.com | main | demo/main/ |",
            ),
            encoding="utf-8",
        )
        # Missing registered config file
        cfg = self.tmp / "configs" / "README.md"
        cfg.write_text(
            cfg.read_text(encoding="utf-8").replace(
                "| 暂无 | — | — | — |",
                "| `benchmark/missing.json` | e2e | tool | cli |",
            ),
            encoding="utf-8",
        )
        # Orphan profile dir
        orphan_prof = self.tmp / "profile-results" / "20261120T060000Z-OPT-9999-nsys-baseline"
        (orphan_prof / "execution").mkdir(parents=True)
        (orphan_prof / "analysis.md").write_text("# a\n", encoding="utf-8")
        # Secret token
        fake_key = "hf_" + "A" * 30
        (self.tmp / "knowledge" / "engine.md").write_text(f"token = {fake_key}\n", encoding="utf-8")

        lint = self._run_ws("lint")
        self.assertNotEqual(lint.returncode, 0)
        for expected in (
            "PLAN.md 阶段与 item.md 不一致",
            "死链",
            "禁止绝对路径链接",
            "浮动版本",
            "已登记文件不存在",
            "profile 目录关联了不存在的工作项",
            "疑似凭据泄露",
        ):
            self.assertIn(expected, lint.stdout)


if __name__ == "__main__":
    unittest.main()
