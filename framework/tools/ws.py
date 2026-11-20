#!/usr/bin/env python3
"""SG Model Workspace Framework CLI (ws).

Python 3.9+ standard library only. Run from a workspace root:
    python3 framework/tools/ws.py <command> [args]
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib
import json
import os
import platform
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

FRAMEWORK_VERSION = "0.1.0"

TYPE_TO_PREFIX = {
    "adapt": "ADP",
    "opt": "OPT",
    "fix": "FIX",
    "res": "RES",
}
PREFIX_TO_TYPE_LABEL = {
    "ADP": "ADAPT",
    "OPT": "OPT",
    "FIX": "FIX",
    "RES": "RES",
}
TYPE_LABEL = {
    "adapt": "ADAPT",
    "opt": "OPT",
    "fix": "FIX",
    "res": "RES",
}
TYPE_TO_INITIAL_PHASE = {
    "adapt": "A0",
    "opt": "O0",
    "fix": "F0",
    "res": "R0",
}
TYPE_TO_VALID_PHASES = {
    "ADAPT": {f"A{i}" for i in range(8)},
    "OPT": {f"O{i}" for i in range(7)},
    "FIX": {f"F{i}" for i in range(5)},
    "RES": {f"R{i}" for i in range(3)},
}
TYPE_TO_GATE_FILE = {
    "ADAPT": "adapt.md",
    "OPT": "optimize.md",
    "FIX": "fix.md",
    "RES": "research.md",
}
TEMPLATE_EXPECTED_DEPTH = {
    "validation-report.md": 3,
    "item-adapt.md": 2,
    "item-opt.md": 2,
    "item-fix.md": 2,
    "item-res.md": 2,
    "design-adapt.md": 2,
    "profile-analysis.md": 2,
    "review.md": 2,
}

VALID_STATUSES = {
    "planned",
    "analyzing",
    "implementing",
    "validating",
    "deciding",
    "done",
    "blocked",
    "cancelled",
}
CLOSED_STATUSES = {"done", "cancelled"}
VALID_ROLES = ("baseline", "candidate", "reference", "comparison")

SLUG_PART = r"[a-z0-9]+(?:-[a-z0-9]+)*"
SLUG_RE = re.compile(rf"^{SLUG_PART}$")
ITEM_ID_RE = re.compile(r"^(ADP|OPT|FIX|RES)-(\d{4})$")
ITEM_DIR_RE = re.compile(rf"^((?:ADP|OPT|FIX|RES)-\d{{4}})-({SLUG_PART})$")
UTC_RE = re.compile(r"^\d{8}T\d{6}Z$")
SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
DECISION_RE = re.compile(
    r"^`?(push|pr-open|merged|keep-local|discard|n/a)`?(?:$|\s|[（(])"
)
BENCH_OR_VAL_RUN_RE = re.compile(
    rf"^\d{{8}}T\d{{6}}Z-{SLUG_PART}-(baseline|candidate|reference|comparison)(?:-\d{{2,}})?$"
)
PROFILE_RUN_RE = re.compile(
    rf"^\d{{8}}T\d{{6}}Z-((?:ADP|OPT|FIX|RES)-\d{{4}})-{SLUG_PART}-(baseline|candidate|reference|comparison)(?:-\d{{2,}})?$"
)

SECRET_PATTERNS: Tuple[Tuple[str, re.Pattern[str]], ...] = (
    ("OpenAI/API key", re.compile(r"\bsk-[A-Za-z0-9_-]{24,}\b")),
    ("HuggingFace token", re.compile(r"\bhf_[A-Za-z0-9]{24,}\b")),
    ("GitHub PAT", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{24,}\b")),
    ("AWS Access Key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def find_workspace_root(start: Optional[Path] = None) -> Path:
    cur = (start or Path.cwd()).resolve()
    for candidate in (cur, *cur.parents):
        if (candidate / "framework" / "README.md").is_file():
            return candidate
    return cur


def framework_root() -> Path:
    return Path(__file__).resolve().parent.parent


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------


def extract_marker_block(text: str, marker: str) -> Optional[Tuple[int, int, str]]:
    begin = f"<!-- ws:{marker}:begin -->"
    end = f"<!-- ws:{marker}:end -->"
    b_idx = text.find(begin)
    if b_idx == -1:
        return None
    e_idx = text.find(end, b_idx + len(begin))
    if e_idx == -1:
        return None
    inner_start = b_idx + len(begin)
    return inner_start, e_idx, text[inner_start:e_idx]


def split_md_row(line: str) -> List[str]:
    inner = line.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|") and not inner.endswith(r"\|"):
        inner = inner[:-1]
    parts = re.split(r"(?<!\\)\|", inner)
    return [p.replace(r"\|", "|").strip() for p in parts]


def sanitize_cell(value: str) -> str:
    return value.replace("|", r"\|").replace("\n", " ").strip()


def parse_md_table(block: str) -> Tuple[List[str], List[List[str]]]:
    lines = [ln.strip() for ln in block.splitlines() if ln.strip().startswith("|")]
    if len(lines) < 2:
        return [], []
    header = split_md_row(lines[0])
    rows: List[List[str]] = []
    for ln in lines[2:]:
        cells = split_md_row(ln)
        if len(cells) < len(header):
            cells.extend([""] * (len(header) - len(cells)))
        rows.append(cells[: len(header)])
    return header, rows


def format_md_table(header: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    out = [
        "| " + " | ".join(sanitize_cell(h) for h in header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for r in rows:
        out.append("| " + " | ".join(sanitize_cell(c) for c in r) + " |")
    return "\n" + "\n".join(out) + "\n"


def parse_handoff(item_md: Path) -> Dict[str, str]:
    text = read_text(item_md)
    block = extract_marker_block(text, "handoff")
    if not block:
        return {}
    _, rows = parse_md_table(block[2])
    data: Dict[str, str] = {}
    for row in rows:
        if len(row) >= 2:
            data[row[0].strip()] = row[1].strip()
    return data


def strip_md_code(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`[^`\n]+`", "", text)
    return text


def iter_md_links(text: str) -> Iterable[str]:
    cleaned = strip_md_code(text)
    for m in re.finditer(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", cleaned):
        yield m.group(1)


def rewrite_relative_md_links(text: str, from_dir: Path, to_dir: Path) -> str:
    def _repl(m: re.Match[str]) -> str:
        prefix, target, suffix = m.group(1), m.group(2), m.group(3)
        if target.startswith(("http://", "https://", "mailto:", "#", "/")):
            return m.group(0)
        if "{{" in target or "<" in target or ">" in target:
            return m.group(0)
        parts = target.split("#", 1)
        path_part = parts[0]
        frag = f"#{parts[1]}" if len(parts) == 2 else ""
        if not path_part:
            return m.group(0)
        resolved = (from_dir / path_part).resolve()
        new_rel = Path(os.path.relpath(resolved, to_dir.resolve())).as_posix()
        return f"{prefix}{new_rel}{frag}{suffix}"

    return re.sub(
        r"(!?\[[^\]]*\]\()([^)\s]+)((?:\s+\"[^\"]*\")?\))",
        _repl,
        text,
    )


def is_placeholder_row(row: Sequence[str]) -> bool:
    return bool(row) and row[0] in ("暂无", "待填写", "—", "")


def extract_id_from_cell(cell: str) -> Optional[str]:
    m = re.search(r"\b((?:ADP|OPT|FIX|RES)-\d{4})\b", cell)
    return m.group(1) if m else None


def extract_cell_path(cell: str) -> Optional[str]:
    c = cell.strip()
    if not c or c in ("暂无", "待填写", "—", "无"):
        return None
    m_link = re.search(r"\[[^\]]+\]\(([^)\s]+)\)", c)
    if m_link:
        target = m_link.group(1)
        if target.startswith(("http://", "https://", "mailto:", "#")):
            return None
        return target.split("#", 1)[0]
    m_code = re.search(r"`([^`]+)`", c)
    if m_code:
        val = m_code.group(1).strip()
        if "://" in val or " " in val:
            return None
        return val
    return None


def find_item_dir(ws: Path, item_id: str) -> Optional[Path]:
    work_dir = ws / "work"
    if not work_dir.is_dir():
        return None
    for child in sorted(work_dir.iterdir()):
        if child.is_dir() and child.name.startswith(item_id + "-"):
            return child
    return None


def decision_is_valid(value: str) -> bool:
    return bool(DECISION_RE.match(value.strip()))


def index_contains_run(index_text: str, run_name: str) -> bool:
    pat = re.compile(rf"(?<![A-Za-z0-9_-]){re.escape(run_name)}(?![A-Za-z0-9_-])")
    return bool(pat.search(index_text))


def get_index_text(readme_path: Path, marker: str) -> str:
    if not readme_path.is_file():
        return ""
    text = read_text(readme_path)
    blk = extract_marker_block(text, marker)
    return blk[2] if blk else text


def load_ignored_top_dirs(ws: Path) -> Set[str]:
    dirs: Set[str] = {"worktrees", "envs/runtime"}
    gi = ws / ".gitignore"
    if not gi.is_file():
        return dirs
    for raw in read_text(gi).splitlines():
        ln = raw.strip()
        if not ln or ln.startswith("#") or ln.startswith("!"):
            continue
        m = re.match(r"^/([A-Za-z0-9._-]+)/(?:\*/)?$", ln)
        if m:
            dirs.add(m.group(1))
    return dirs


# ---------------------------------------------------------------------------
# Subcommand: init
# ---------------------------------------------------------------------------


def cmd_init(args: argparse.Namespace) -> int:
    target = Path(args.target).resolve()
    tmpl_root = framework_root() / "templates" / "instance"
    if not tmpl_root.is_dir():
        print(f"ERROR: instance templates not found at {tmpl_root}", file=sys.stderr)
        return 1

    project_name = args.name or target.name
    created: List[str] = []
    skipped: List[str] = []

    for src in sorted(tmpl_root.rglob("*")):
        rel = src.relative_to(tmpl_root)
        dst = target / rel
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            continue
        if dst.exists() and not args.force:
            skipped.append(str(rel))
            continue
        content = read_text(src)
        content = content.replace("{{FRAMEWORK_VERSION}}", FRAMEWORK_VERSION)
        content = content.replace("{{PROJECT_NAME}}", project_name)
        write_text(dst, content)
        created.append(str(rel))

    print(f"Initialized workspace at {target} (framework v{FRAMEWORK_VERSION})")
    if created:
        print(f"Created ({len(created)}):")
        for p in created:
            print(f"  + {p}")
    if skipped:
        print(f"Skipped existing ({len(skipped)}, use --force to overwrite):")
        for p in skipped:
            print(f"  - {p}")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: new
# ---------------------------------------------------------------------------


def next_item_id(ws: Path, prefix: str) -> str:
    work_dir = ws / "work"
    max_num = 0
    if work_dir.is_dir():
        for child in work_dir.iterdir():
            m = ITEM_DIR_RE.match(child.name)
            if m and m.group(1).startswith(prefix + "-"):
                num = int(m.group(1).split("-")[1])
                if num > max_num:
                    max_num = num
    return f"{prefix}-{max_num + 1:04d}"


def cmd_new(args: argparse.Namespace) -> int:
    ws = find_workspace_root()
    kind = args.type.lower()
    prefix = TYPE_TO_PREFIX[kind]
    name = args.name.strip()
    if not SLUG_RE.match(name):
        print(
            f"ERROR: name '{name}' must match lowercase slug ^[a-z0-9]+(?:-[a-z0-9]+)*$",
            file=sys.stderr,
        )
        return 1

    if args.id:
        m = ITEM_ID_RE.match(args.id)
        if not m or m.group(1) != prefix:
            print(f"ERROR: --id '{args.id}' must match {prefix}-NNNN", file=sys.stderr)
            return 1
        item_id = args.id
    else:
        item_id = next_item_id(ws, prefix)

    if find_item_dir(ws, item_id) is not None:
        print(f"ERROR: work item {item_id} already exists", file=sys.stderr)
        return 1

    tmpl_path = framework_root() / "templates" / f"item-{kind}.md"
    if not tmpl_path.is_file():
        print(f"ERROR: template not found: {tmpl_path}", file=sys.stderr)
        return 1

    if args.from_commit and not SHA40_RE.match(args.from_commit):
        print("ERROR: --from-commit must be a 40-char lowercase hex SHA", file=sys.stderr)
        return 1

    now = utc_now()
    title = (args.title or name).strip()
    summary_text = (args.summary or title).strip()
    default_commit = "无（或填写参考源码 40 位 SHA）" if kind == "res" else "待填写（40位完整SHA）"
    start_commit = args.from_commit or default_commit

    content = read_text(tmpl_path)
    content = (
        content.replace("{{ID}}", item_id)
        .replace("{{NAME}}", name)
        .replace("{{TITLE}}", title)
        .replace("{{UTC}}", now)
        .replace("{{START_COMMIT}}", start_commit)
    )

    item_dir = ws / "work" / f"{item_id}-{name}"
    item_file = item_dir / "item.md"
    write_text(item_file, content)

    # Update work/README.md index
    work_readme = ws / "work" / "README.md"
    if work_readme.is_file():
        text = read_text(work_readme)
        blk = extract_marker_block(text, "work-index")
        if blk:
            header, rows = parse_md_table(blk[2])
            rows = [r for r in rows if not is_placeholder_row(r)]
            rel_link = f"[{name}]({item_id}-{name}/item.md)"
            rows.append([item_id, rel_link, TYPE_LABEL[kind], summary_text, "planned", "待定", "—"])
            new_text = text[: blk[0]] + format_md_table(header, rows) + text[blk[1] :]
            write_text(work_readme, new_text)

    # Update PLAN.md
    plan_file = ws / "PLAN.md"
    if plan_file.is_file():
        text = read_text(plan_file)
        blk = extract_marker_block(text, "plan")
        if blk:
            header, rows = parse_md_table(blk[2])
            rows = [r for r in rows if not is_placeholder_row(r)]
            phase = TYPE_TO_INITIAL_PHASE[kind]
            doc_link = f"[item.md](work/{item_id}-{name}/item.md)"
            commit_cell = f"`{start_commit}`" if SHA40_RE.match(start_commit) else ("无" if kind == "res" else "待填写")
            rows.append([item_id, TYPE_LABEL[kind], summary_text, f"{phase} / planned", doc_link, commit_cell])
            new_text = text[: blk[0]] + format_md_table(header, rows) + text[blk[1] :]
            write_text(plan_file, new_text)

    print(f"Created work item: {item_file.relative_to(ws)}")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: status
# ---------------------------------------------------------------------------


def git_info(repo_dir: Path) -> Optional[Dict[str, object]]:
    if not (repo_dir / ".git").exists():
        return None
    try:
        branch = subprocess.check_output(
            ["git", "-C", str(repo_dir), "rev-parse", "--abbrev-ref", "HEAD"],
            text=True,
            errors="replace",
            stderr=subprocess.DEVNULL,
        ).strip()
        commit = subprocess.check_output(
            ["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
            text=True,
            errors="replace",
            stderr=subprocess.DEVNULL,
        ).strip()
        porcelain = subprocess.check_output(
            ["git", "-C", str(repo_dir), "status", "--porcelain"],
            text=True,
            errors="replace",
            stderr=subprocess.DEVNULL,
        )
        dirty_files = [ln for ln in porcelain.splitlines() if ln.strip()]
        untracked = [ln[3:] for ln in dirty_files if ln.startswith("?? ")]
        return {
            "path": str(repo_dir),
            "branch": branch,
            "commit": commit,
            "dirty": bool(dirty_files),
            "dirty_count": len(dirty_files),
            "untracked_files": untracked,
        }
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def cmd_status(args: argparse.Namespace) -> int:
    ws = find_workspace_root()
    print(f"Workspace: {ws}")

    work_dir = ws / "work"
    items: List[Tuple[str, Dict[str, str]]] = []
    if work_dir.is_dir():
        for child in sorted(work_dir.iterdir()):
            item_md = child / "item.md"
            if child.is_dir() and item_md.is_file():
                items.append((child.name, parse_handoff(item_md)))

    print("\n== Work Items ==")
    if not items:
        print("  (none)")
    else:
        for dirname, h in items:
            print(
                f"  {h.get('ID', dirname):10s} [{h.get('类型', '?'):5s}] "
                f"{h.get('阶段', '?')}/{h.get('状态', '?'):12s} "
                f"next: {h.get('下一步', '—')}"
            )

    wt_root = ws / "worktrees"
    print("\n== Worktrees ==")
    found_wt = False
    if wt_root.is_dir():
        for repo_group in sorted(wt_root.iterdir()):
            if not repo_group.is_dir():
                continue
            for wt in sorted(repo_group.iterdir()):
                if not wt.is_dir():
                    continue
                info = git_info(wt)
                if info:
                    found_wt = True
                    rel = wt.relative_to(ws)
                    dirty_s = f"dirty({info['dirty_count']})" if info["dirty"] else "clean"
                    print(f"  {rel}: {info['branch']} @ {str(info['commit'])[:12]} [{dirty_s}]")
    if not found_wt:
        print("  (none checked out locally)")

    if args.check_pkg:
        print("\n== Packages ==")
        for pkg in args.check_pkg:
            try:
                mod = importlib.import_module(pkg)
                loc = getattr(mod, "__file__", "<namespace>")
                ver = getattr(mod, "__version__", "unknown")
                print(f"  {pkg}: {ver} ({loc})")
            except Exception as exc:
                print(f"  {pkg}: IMPORT FAILED ({exc})")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: run-dir
# ---------------------------------------------------------------------------


def cmd_run_dir(args: argparse.Namespace) -> int:
    ws = find_workspace_root()
    item_id = args.id
    if not ITEM_ID_RE.match(item_id):
        print(f"ERROR: invalid ID '{item_id}'", file=sys.stderr)
        return 1
    if find_item_dir(ws, item_id) is None:
        print(f"ERROR: work item {item_id} not found in work/", file=sys.stderr)
        return 1

    label = args.label.strip().lower()
    if not SLUG_RE.match(label):
        print(f"ERROR: label '{label}' must be lowercase slug", file=sys.stderr)
        return 1

    role = args.role.strip().lower()
    if role not in VALID_ROLES:
        print(f"ERROR: role must be one of {', '.join(VALID_ROLES)}", file=sys.stderr)
        return 1

    utc = args.utc or utc_now()
    if not UTC_RE.match(utc):
        print("ERROR: --utc must match YYYYMMDDTHHMMSSZ", file=sys.stderr)
        return 1

    kind = args.kind
    if kind == "benchmark":
        parent = ws / "benchmark-results" / item_id
        base_name = f"{utc}-{label}-{role}"
    elif kind == "validation":
        parent = ws / "validation-results" / item_id
        base_name = f"{utc}-{label}-{role}"
    else:
        parent = ws / "profile-results"
        base_name = f"{utc}-{item_id}-{label}-{role}"

    run_dir = parent / base_name
    suffix = 2
    while run_dir.exists():
        run_dir = parent / f"{base_name}-{suffix:02d}"
        suffix += 1

    (run_dir / "execution").mkdir(parents=True, exist_ok=False)
    print(run_dir.relative_to(ws).as_posix())
    return 0


# ---------------------------------------------------------------------------
# Subcommand: record
# ---------------------------------------------------------------------------


def capture_gpu_info() -> Optional[List[Dict[str, str]]]:
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=index,name,driver_version,memory.total",
                "--format=csv,noheader",
            ],
            text=True,
            errors="replace",
            stderr=subprocess.DEVNULL,
        )
        gpus = []
        for ln in out.splitlines():
            parts = [p.strip() for p in ln.split(",")]
            if len(parts) >= 4:
                gpus.append(
                    {
                        "index": parts[0],
                        "name": parts[1],
                        "driver_version": parts[2],
                        "memory_total": parts[3],
                    }
                )
        return gpus
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def cmd_record(args: argparse.Namespace) -> int:
    ws = find_workspace_root()
    run_dir = Path(args.run_dir)
    if not run_dir.is_absolute():
        run_dir = (ws / run_dir).resolve()
    exec_dir = run_dir / "execution"
    exec_dir.mkdir(parents=True, exist_ok=True)

    repos_out: List[Dict[str, object]] = []
    for raw_repo in args.repo or []:
        rpath = Path(raw_repo)
        if not rpath.is_absolute():
            rpath = (ws / rpath).resolve()
        info = git_info(rpath)
        if not info:
            repos_out.append({"path": raw_repo, "error": "not a git repository"})
            continue
        rel_path = raw_repo
        try:
            rel_path = rpath.relative_to(ws).as_posix()
        except ValueError:
            pass
        entry: Dict[str, object] = {
            "path": rel_path,
            "branch": info["branch"],
            "commit": info["commit"],
            "dirty": info["dirty"],
        }
        untracked = info.get("untracked_files") or []
        if untracked:
            entry["untracked_files"] = untracked
        if info["dirty"]:
            diff = subprocess.check_output(
                ["git", "-C", str(rpath), "diff", "HEAD"],
                text=True,
                errors="replace",
                stderr=subprocess.DEVNULL,
            )
            if diff.strip():
                safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "_", rel_path).strip("_")
                patch_file = exec_dir / f"dirty-{safe_name}.patch"
                write_text(patch_file, diff)
                entry["dirty_patch"] = patch_file.name
        repos_out.append(entry)

    pkgs_out: Dict[str, Dict[str, str]] = {}
    for pkg in args.pkg or []:
        try:
            mod = importlib.import_module(pkg)
            pkgs_out[pkg] = {
                "version": str(getattr(mod, "__version__", "unknown")),
                "file": str(getattr(mod, "__file__", "<namespace>")),
            }
        except Exception as exc:
            pkgs_out[pkg] = {"error": str(exc)}

    try:
        rel_cwd = Path.cwd().resolve().relative_to(ws).as_posix()
        cwd_recorded = "." if rel_cwd == "." else rel_cwd
    except ValueError:
        cwd_recorded = str(Path.cwd().name)

    record = {
        "recorded_at_utc": utc_now(),
        "cwd_rel": cwd_recorded,
        "cmd": args.cmd or "",
        "env_snapshot": args.env_snapshot or "",
        "env_var_names": list(args.env_var or []),
        "repos": repos_out,
        "packages": pkgs_out,
        "hardware": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "gpus": capture_gpu_info(),
        },
        "note": args.note or "",
    }
    out_file = exec_dir / "ws-record.json"
    write_text(out_file, json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    try:
        shown = out_file.relative_to(ws).as_posix()
    except ValueError:
        shown = str(out_file)
    print(f"Wrote execution record: {shown}")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: lint
# ---------------------------------------------------------------------------


def run_lint(ws: Path) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    # 1. Required files
    for req in ("AGENTS.md", "PROJECT.md", "PLAN.md", "framework/README.md", "work/README.md"):
        if not (ws / req).is_file():
            errors.append(f"缺少必备文件: {req}")

    # 2. Markdown relative links
    skip_dirs = {".git", "worktrees", "tmp", "__pycache__"}
    tmpl_root = ws / "framework" / "templates"
    inst_tmpl_root = tmpl_root / "instance"
    ignored_top = load_ignored_top_dirs(ws)

    for md in sorted(ws.rglob("*.md")):
        rel_parts = md.relative_to(ws).parts
        if any(p in skip_dirs for p in rel_parts):
            continue
        if len(rel_parts) >= 2 and rel_parts[0] == "envs" and rel_parts[1] == "runtime":
            continue
        is_inst_tmpl = inst_tmpl_root in md.parents
        is_doc_tmpl = (md.parent == tmpl_root) and (md.name in TEMPLATE_EXPECTED_DEPTH)
        text = read_text(md)
        for target in iter_md_links(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if "{{" in target or "<" in target or ">" in target:
                continue
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue
            if path_part.startswith("/"):
                errors.append(f"禁止绝对路径链接: {md.relative_to(ws)} -> {target}")
                continue

            resolved = (md.parent / path_part).resolve()
            if resolved.exists():
                continue

            # Instance templates resolve relative to instance root once instantiated
            if is_inst_tmpl:
                rel_in_inst = md.parent.relative_to(inst_tmpl_root)
                virt_resolved = (ws / rel_in_inst / path_part).resolve()
                if virt_resolved.exists():
                    continue
            # Document templates verify exact ../ depth matching their target location
            elif is_doc_tmpl:
                expected_prefix = "../" * TEMPLATE_EXPECTED_DEPTH[md.name] + "framework/"
                if path_part.startswith(expected_prefix):
                    rest = path_part[len(expected_prefix) :]
                    if (ws / "framework" / rest).exists():
                        continue

            try:
                rel_target = resolved.relative_to(ws).as_posix()
            except ValueError:
                rel_target = target
            first_seg = rel_target.split("/", 1)[0]
            if first_seg in ignored_top or rel_target.startswith("envs/runtime/"):
                warnings.append(
                    f"外部/未跟踪目录链接在本地不存在: {md.relative_to(ws)} -> {target}"
                )
            else:
                errors.append(f"死链: {md.relative_to(ws)} -> {target}")

    # 3. Work items, work/README.md, PLAN.md consistency
    work_items: Dict[str, Tuple[Path, Dict[str, str]]] = {}
    work_dir = ws / "work"
    if work_dir.is_dir():
        for child in sorted(work_dir.iterdir()):
            if not child.is_dir() or child.name.startswith("."):
                continue
            m = ITEM_DIR_RE.match(child.name)
            if not m:
                errors.append(f"工作项目录命名不规范: work/{child.name}")
                continue
            item_id = m.group(1)
            prefix = item_id.split("-")[0]
            if item_id in work_items:
                errors.append(f"重复的工作项 ID: {item_id}")
                continue
            item_md = child / "item.md"
            if not item_md.is_file():
                errors.append(f"缺少 item.md: work/{child.name}/item.md")
                continue
            handoff = parse_handoff(item_md)
            if not handoff:
                errors.append(f"缺少 ws:handoff 标记块: work/{child.name}/item.md")
            else:
                h_id = handoff.get("ID", "")
                if h_id != item_id:
                    errors.append(
                        f"item.md 交接节 ID 与目录不一致: '{h_id}' vs '{item_id}' (work/{child.name}/item.md)"
                    )
                expected_type = PREFIX_TO_TYPE_LABEL[prefix]
                h_type = handoff.get("类型", "")
                if h_type != expected_type:
                    errors.append(
                        f"item.md 交接节类型与 ID 前缀不一致: '{h_type}' vs '{expected_type}' (work/{child.name}/item.md)"
                    )
                h_phase = handoff.get("阶段", "")
                if h_type in TYPE_TO_VALID_PHASES and h_phase not in TYPE_TO_VALID_PHASES[h_type]:
                    errors.append(f"非法阶段 '{h_phase}': work/{child.name}/item.md")
                st = handoff.get("状态", "")
                if st not in VALID_STATUSES:
                    errors.append(f"非法状态 '{st}': work/{child.name}/item.md")
                if st == "done" and not decision_is_valid(handoff.get("决定", "")):
                    errors.append(f"已结项但决定未填写或非法: work/{child.name}/item.md")
            work_items[item_id] = (child, handoff)

    # Check work/README.md index
    work_readme = ws / "work" / "README.md"
    indexed_ids: Dict[str, str] = {}
    if work_readme.is_file():
        blk = extract_marker_block(read_text(work_readme), "work-index")
        if not blk:
            errors.append("work/README.md 缺少 ws:work-index 标记块")
        else:
            _, rows = parse_md_table(blk[2])
            for r in rows:
                if is_placeholder_row(r):
                    continue
                iid = extract_id_from_cell(r[0])
                if not iid:
                    errors.append(f"work/README.md 索引行缺少合法 ID: {r[0]}")
                    continue
                if iid in indexed_ids:
                    errors.append(f"work/README.md 索引存在重复 ID: {iid}")
                    continue
                indexed_ids[iid] = r[4] if len(r) > 4 else ""
                if iid not in work_items:
                    errors.append(f"work/README.md 登记了不存在的工作项: {iid}")
            for iid, (_, h) in work_items.items():
                if iid not in indexed_ids:
                    errors.append(f"工作项未登记到 work/README.md: {iid}")
                elif h.get("状态") and indexed_ids[iid] != h.get("状态"):
                    errors.append(
                        f"状态不一致 ({iid}): item.md='{h.get('状态')}' vs work/README.md='{indexed_ids[iid]}'"
                    )

    # Check PLAN.md
    plan_file = ws / "PLAN.md"
    if plan_file.is_file():
        blk = extract_marker_block(read_text(plan_file), "plan")
        if not blk:
            errors.append("PLAN.md 缺少 ws:plan 标记块")
        else:
            _, rows = parse_md_table(blk[2])
            plan_ids: Dict[str, str] = {}
            for r in rows:
                if is_placeholder_row(r):
                    continue
                iid = extract_id_from_cell(r[0])
                if not iid:
                    errors.append(f"PLAN.md 行缺少合法 ID: {r[0]}")
                    continue
                if iid in plan_ids:
                    errors.append(f"PLAN.md 存在重复 ID: {iid}")
                    continue
                plan_ids[iid] = r[3] if len(r) > 3 else ""
                if iid not in work_items:
                    errors.append(f"PLAN.md 列出了不存在的工作项: {iid}")
            for iid, (_, h) in work_items.items():
                st = h.get("状态", "")
                ph = h.get("阶段", "")
                if st in CLOSED_STATUSES and iid in plan_ids:
                    errors.append(f"已完结工作项应从 PLAN.md 移除: {iid} ({st})")
                if st and st not in CLOSED_STATUSES and iid not in plan_ids:
                    errors.append(f"活动工作项未列入 PLAN.md: {iid} ({st})")
                if iid in plan_ids:
                    plan_cell = plan_ids[iid]
                    tokens = [t.strip() for t in re.split(r"[/\s]+", plan_cell) if t.strip()]
                    if st and st not in tokens:
                        errors.append(
                            f"PLAN.md 状态与 item.md 不一致 ({iid}): PLAN='{plan_cell}' vs item='{st}'"
                        )
                    if ph and ph not in tokens:
                        errors.append(
                            f"PLAN.md 阶段与 item.md 不一致 ({iid}): PLAN='{plan_cell}' vs item='{ph}'"
                        )

    # 4. Evidence directories
    def check_grouped_evidence(root_name: str, marker: str, check_report: bool = False) -> None:
        ev_root = ws / root_name
        if not ev_root.is_dir():
            return
        idx_text = get_index_text(ev_root / "README.md", marker)
        for id_dir in sorted(ev_root.iterdir()):
            if not id_dir.is_dir() or id_dir.name.startswith("."):
                continue
            if not ITEM_ID_RE.match(id_dir.name):
                errors.append(f"证据目录第一层须为工作项 ID: {root_name}/{id_dir.name}")
                continue
            if id_dir.name not in work_items:
                errors.append(f"证据目录关联了不存在的工作项: {root_name}/{id_dir.name}")
            for run_dir in sorted(id_dir.iterdir()):
                if not run_dir.is_dir() or run_dir.name.startswith("."):
                    continue
                if not BENCH_OR_VAL_RUN_RE.match(run_dir.name):
                    errors.append(f"运行目录命名不规范: {root_name}/{id_dir.name}/{run_dir.name}")
                if not (run_dir / "execution").is_dir():
                    errors.append(f"运行目录缺少 execution/: {root_name}/{id_dir.name}/{run_dir.name}")
                if check_report and not (run_dir / "report.md").is_file():
                    errors.append(f"验证目录缺少 report.md: {root_name}/{id_dir.name}/{run_dir.name}")
                if not index_contains_run(idx_text, run_dir.name):
                    errors.append(f"运行目录未登记到 {root_name}/README.md: {id_dir.name}/{run_dir.name}")

    check_grouped_evidence("benchmark-results", "benchmark-index", check_report=False)
    check_grouped_evidence("validation-results", "validation-index", check_report=True)

    prof_root = ws / "profile-results"
    if prof_root.is_dir():
        idx_text = get_index_text(prof_root / "README.md", "profile-index")
        for run_dir in sorted(prof_root.iterdir()):
            if not run_dir.is_dir() or run_dir.name.startswith("."):
                continue
            pm = PROFILE_RUN_RE.match(run_dir.name)
            if not pm:
                errors.append(f"profile 采集目录命名不规范: profile-results/{run_dir.name}")
            else:
                prof_id = pm.group(1)
                if prof_id not in work_items:
                    errors.append(
                        f"profile 目录关联了不存在的工作项: profile-results/{run_dir.name} ({prof_id})"
                    )
            if not (run_dir / "execution").is_dir():
                errors.append(f"profile 目录缺少 execution/: profile-results/{run_dir.name}")
            if not (run_dir / "analysis.md").is_file():
                errors.append(f"profile 目录缺少 analysis.md: profile-results/{run_dir.name}")
            if not index_contains_run(idx_text, run_dir.name):
                errors.append(f"profile 目录未登记到 profile-results/README.md: {run_dir.name}")

    # 5. Asset & config/script registry checks
    # Tracked registries (configs, scripts): missing file is an ERROR.
    for reg_readme, marker, path_col in (
        ("configs/README.md", "configs", 0),
        ("scripts/README.md", "scripts", 0),
    ):
        p = ws / reg_readme
        if not p.is_file():
            continue
        blk = extract_marker_block(read_text(p), marker)
        if not blk:
            continue
        _, rows = parse_md_table(blk[2])
        for r in rows:
            if is_placeholder_row(r) or len(r) <= path_col:
                continue
            rel_p = extract_cell_path(r[path_col])
            if rel_p and not (p.parent / rel_p).exists():
                errors.append(f"已登记文件不存在: {reg_readme} -> {rel_p}")

    # Untracked local asset registries (worktrees, checkpoints, datasets): warn if absent locally;
    # checkpoints & datasets also fail on floating versions.
    for asset_readme, marker, ver_col, dir_col in (
        ("worktrees/README.md", "worktrees", None, 2),
        ("checkpoints/README.md", "checkpoints", 3, 4),
        ("datasets/README.md", "datasets", 3, 4),
    ):
        p = ws / asset_readme
        if not p.is_file():
            continue
        blk = extract_marker_block(read_text(p), marker)
        if not blk:
            continue
        _, rows = parse_md_table(blk[2])
        for r in rows:
            if is_placeholder_row(r):
                continue
            if ver_col is not None and len(r) > ver_col:
                ver = r[ver_col].strip().strip("`").lower()
                if ver in ("main", "master", "latest", "head"):
                    errors.append(f"资产登记使用了浮动版本 '{ver}': {asset_readme} ({r[0]})")
            if len(r) > dir_col:
                rel_p = extract_cell_path(r[dir_col])
                if rel_p and not (p.parent / rel_p).exists():
                    warnings.append(f"已登记资产在本地尚未准备或检出: {asset_readme} -> {rel_p}")

    # 6. Credential leak scan
    scan_exts = {".md", ".json", ".yaml", ".yml", ".toml", ".sh", ".py"}
    for f in sorted(ws.rglob("*")):
        if not f.is_file() or f.suffix not in scan_exts:
            continue
        rel = f.relative_to(ws)
        if any(p in skip_dirs for p in rel.parts):
            continue
        if len(rel.parts) >= 2 and rel.parts[0] == "envs" and rel.parts[1] == "runtime":
            continue
        if rel.as_posix() in ("framework/tools/ws.py", "framework/tools/tests/test_ws.py"):
            continue
        try:
            content = read_text(f)
        except UnicodeDecodeError:
            continue
        for label, pat in SECRET_PATTERNS:
            if pat.search(content):
                errors.append(f"疑似凭据泄露 ({label}): {rel.as_posix()}")

    return errors, warnings


def cmd_lint(args: argparse.Namespace) -> int:
    ws = find_workspace_root()
    errors, warnings = run_lint(ws)
    for w in warnings:
        print(f"WARN:  {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        print(f"\nws lint FAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"ws lint PASSED: 0 errors, {len(warnings)} warning(s)")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: gate
# ---------------------------------------------------------------------------


def parse_gate_phase(gate_file: Path, phase: str) -> Optional[Tuple[str, List[Tuple[str, Optional[str], str]]]]:
    text = read_text(gate_file)
    heading_re = re.compile(rf"^##\s+({re.escape(phase)}(?:\s+.*)?)$", re.MULTILINE)
    m = heading_re.search(text)
    if not m:
        return None
    title = m.group(1).strip()
    start = m.end()
    next_h = re.search(r"^##\s+", text[start:], re.MULTILINE)
    section = text[start : start + next_h.start()] if next_h else text[start:]

    items: List[Tuple[str, Optional[str], str]] = []
    for ln in section.splitlines():
        im = re.match(r"^\s*-\s+\[(auto(?::[a-z0-9_]+)?|evidence|judgement)\]\s+(.*)$", ln)
        if not im:
            continue
        tag = im.group(1)
        desc = im.group(2).strip()
        if tag.startswith("auto:"):
            items.append(("auto", tag.split(":", 1)[1], desc))
        elif tag == "auto":
            items.append(("auto", "lint", desc))
        else:
            items.append((tag, None, desc))
    return title, items


def run_auto_check(
    ws: Path,
    item_dir: Path,
    handoff: Dict[str, str],
    check: str,
    phase: str,
) -> Tuple[bool, str]:
    item_id = handoff.get("ID", item_dir.name[:8])
    if check == "lint":
        errs, _ = run_lint(ws)
        return (len(errs) == 0, "0 errors" if not errs else f"{len(errs)} lint error(s)")
    if check == "handoff":
        ts = handoff.get("更新时间（UTC）", "")
        nxt = handoff.get("下一步", "")
        ok = bool(UTC_RE.match(ts)) and bool(nxt) and "待填写" not in nxt
        return (ok, f"updated={ts}" if ok else "交接节更新时间或下一步未填写")
    if check == "start_commit":
        sha = handoff.get("起点 commit", "").strip("`")
        ok = bool(SHA40_RE.match(sha))
        return (ok, sha[:12] if ok else f"非法起点 commit: '{sha}'")
    if check == "branch":
        br = handoff.get("实现分支", "").strip("`")
        ok = bool(br) and br not in ("待填写", "无", "—")
        return (ok, br if ok else "实现分支未填写")
    if check == "design_exists":
        p = item_dir / "design.md"
        return (p.is_file(), "design.md 存在" if p.is_file() else "缺少 design.md")
    if check == "benchmark_indexed":
        bdir = ws / "benchmark-results" / item_id
        idx_text = get_index_text(ws / "benchmark-results" / "README.md", "benchmark-index")
        runs: List[Path] = []
        if bdir.is_dir():
            runs = [
                d
                for d in sorted(bdir.iterdir())
                if d.is_dir() and (d / "execution").is_dir() and index_contains_run(idx_text, d.name)
            ]
        if phase == "O5":
            cand = [d for d in runs if re.search(r"-candidate(?:-\d{2,})?$", d.name)]
            if cand:
                return (True, f"{len(cand)} 个已登记 candidate 运行")
            return (False, f"O5 要求 benchmark-results/{item_id}/ 下存在已登记的 -candidate 运行")
        if phase == "O1":
            base_runs = [d for d in runs if re.search(r"-baseline(?:-\d{2,})?$", d.name)]
            if base_runs:
                return (True, f"{len(base_runs)} 个已登记 baseline 运行")
            item_text = read_text(item_dir / "item.md")
            for ref_m in re.finditer(
                r"benchmark-results/((?:ADP|OPT|FIX|RES)-\d{4})/(\d{8}T\d{6}Z-[a-z0-9-]+)",
                item_text,
            ):
                ref_dir = ws / "benchmark-results" / ref_m.group(1) / ref_m.group(2)
                if (ref_dir / "execution").is_dir() and index_contains_run(idx_text, ref_m.group(2)):
                    return (True, f"引用已有基线 {ref_m.group(1)}/{ref_m.group(2)}")
            return (False, f"O1 要求 benchmark-results/{item_id}/ 存在已登记 baseline 运行或引用已有基线")
        if runs:
            return (True, f"{len(runs)} 个已登记运行")
        return (False, f"benchmark-results/{item_id}/ 下未找到已登记且含 execution/ 的运行")
    if check == "profile_indexed":
        pdir = ws / "profile-results"
        idx_text = get_index_text(pdir / "README.md", "profile-index")
        if pdir.is_dir():
            matches = [
                d
                for d in sorted(pdir.iterdir())
                if d.is_dir()
                and f"-{item_id}-" in d.name
                and (d / "execution").is_dir()
                and (d / "analysis.md").is_file()
                and index_contains_run(idx_text, d.name)
            ]
            if matches:
                return (True, f"{len(matches)} 个已登记采集")
        return (False, f"profile-results/ 下未找到关联 {item_id} 且含 analysis.md 的已登记采集")
    if check == "validation_indexed":
        vdir = ws / "validation-results" / item_id
        idx_text = get_index_text(ws / "validation-results" / "README.md", "validation-index")
        runs: List[Path] = []
        if vdir.is_dir():
            runs = [
                d
                for d in sorted(vdir.iterdir())
                if d.is_dir()
                and (d / "execution").is_dir()
                and (d / "report.md").is_file()
                and index_contains_run(idx_text, d.name)
            ]
        phase_filters: Dict[str, Tuple[str, str]] = {
            "A2": (r"-(?:golden|reference)(?:-|$)", "golden/reference"),
            "A3": (r"-load-(?:candidate|baseline|reference)(?:-\d{2,})?$", "load"),
            "A4": (r"-align-(?:candidate|baseline|reference)(?:-\d{2,})?$", "align"),
            "A5": (r"-feature-(?:candidate|baseline|reference)(?:-\d{2,})?$", "feature"),
            "F0": (r"-baseline(?:-\d{2,})?$", "baseline 复现"),
            "F3": (r"-candidate(?:-\d{2,})?$", "candidate 验证"),
        }
        if phase in phase_filters:
            pat, desc = phase_filters[phase]
            matched = [d for d in runs if re.search(pat, d.name)]
            if matched:
                return (True, f"{len(matched)} 个已登记 {desc} 验证")
            return (False, f"{phase} 要求 validation-results/{item_id}/ 下存在已登记的 {desc} 验证（含 report.md）")
        if runs:
            return (True, f"{len(runs)} 个已登记验证")
        return (False, f"validation-results/{item_id}/ 下未找到含 report.md 与 execution/ 的已登记验证")
    if check == "review_recorded":
        text = read_text(item_dir / "item.md")
        m = re.search(
            r"^##\s+(?:\d+\.\s+)?审查记录\s*$(.*?)(?=^##\s+|\Z)",
            text,
            re.MULTILINE | re.DOTALL,
        )
        if not m:
            return (False, "未找到审查记录节")
        body = re.sub(r"^>.*$", "", m.group(1), flags=re.MULTILINE).strip()
        ok = bool(body) and body not in ("待执行。", "待执行", "待填写", "无")
        return (ok, "已记录审查" if ok else "审查记录仍为占位内容")
    if check == "decision_recorded":
        dec = handoff.get("决定", "")
        ok = decision_is_valid(dec)
        return (ok, dec if ok else f"决定未填写或非法: '{dec}'")
    return (False, f"未知自动检查项: {check}")


def cmd_gate(args: argparse.Namespace) -> int:
    ws = find_workspace_root()
    item_dir = find_item_dir(ws, args.id)
    if not item_dir:
        print(f"ERROR: work item {args.id} not found", file=sys.stderr)
        return 1
    item_md = item_dir / "item.md"
    handoff = parse_handoff(item_md)
    item_type = handoff.get("类型", "")
    phase = args.phase or handoff.get("阶段", "")
    gate_filename = TYPE_TO_GATE_FILE.get(item_type)
    if not gate_filename:
        print(f"ERROR: unknown item type '{item_type}' in {item_md}", file=sys.stderr)
        return 1
    gate_file = framework_root() / "gates" / gate_filename
    parsed = parse_gate_phase(gate_file, phase)
    if not parsed:
        print(f"ERROR: phase '{phase}' not found in {gate_file}", file=sys.stderr)
        return 1

    title, items = parsed
    print(f"Gate {args.id} — {title}")
    auto_failed = False
    md_lines = [f"\n### Gate {title}（UTC：{utc_now()}）\n"]

    for kind, check_id, desc in items:
        rewritten_desc = rewrite_relative_md_links(desc, gate_file.parent, item_dir)
        if kind == "auto" and check_id:
            ok, detail = run_auto_check(ws, item_dir, handoff, check_id, phase)
            status = "PASS" if ok else "FAIL"
            if not ok:
                auto_failed = True
            print(f"  [{status}] [auto:{check_id}] {desc} — {detail}")
            box = "x" if ok else " "
            md_lines.append(f"- [{box}] `[auto:{check_id}]` {rewritten_desc} → **{status}**（{detail}）")
        else:
            print(f"  [TODO] [{kind}] {desc}")
            md_lines.append(f"- [ ] `[{kind}]` {rewritten_desc} → 待填写回应")

    if args.write:
        text = read_text(item_md)
        sec = re.search(r"^##\s+(?:\d+\.\s+)?门禁记录\s*$", text, re.MULTILINE)
        if not sec:
            print("WARN: 未找到门禁记录节，追加到文件末尾", file=sys.stderr)
            new_text = text.rstrip() + "\n" + "\n".join(md_lines) + "\n"
        else:
            next_h = re.search(r"^##\s+", text[sec.end() :], re.MULTILINE)
            insert_at = sec.end() + next_h.start() if next_h else len(text)
            block = "\n".join(md_lines) + "\n\n"
            new_text = text[:insert_at].rstrip() + "\n" + block + text[insert_at:].lstrip("\n")
        write_text(item_md, new_text)
        print(f"\nAppended gate record to {item_md.relative_to(ws)}")

    return 1 if auto_failed else 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ws", description="SG Model Workspace Framework CLI")
    sub = p.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Initialize a new workspace instance from templates")
    p_init.add_argument("target", help="Target directory")
    p_init.add_argument("--name", help="Project name for PROJECT.md")
    p_init.add_argument("--force", action="store_true", help="Overwrite existing files")
    p_init.set_defaults(func=cmd_init)

    p_new = sub.add_parser("new", help="Create a new work item and update PLAN & index")
    p_new.add_argument("type", choices=("adapt", "opt", "fix", "res"))
    p_new.add_argument("name", help="Lowercase slug name (e.g. codec-cuda-graph)")
    p_new.add_argument("--id", help="Explicit ID (e.g. OPT-0000 for initial baseline)")
    p_new.add_argument("--title", help="Display title")
    p_new.add_argument("--summary", help="One-sentence summary for PLAN and index")
    p_new.add_argument("--from-commit", help="40-char starting commit SHA")
    p_new.set_defaults(func=cmd_new)

    p_st = sub.add_parser("status", help="Show workspace items, worktrees and optional package paths")
    p_st.add_argument("--check-pkg", action="append", help="Python package to inspect __file__")
    p_st.set_defaults(func=cmd_status)

    p_rd = sub.add_parser("run-dir", help="Create standardized evidence run directory with execution/")
    p_rd.add_argument("id", help="Work item ID (e.g. OPT-0001)")
    p_rd.add_argument("label", help="Suite name, check name, or profiler tool")
    p_rd.add_argument("role", choices=VALID_ROLES)
    p_rd.add_argument("--kind", choices=("benchmark", "profile", "validation"), default="benchmark")
    p_rd.add_argument("--utc", help="Explicit UTC timestamp YYYYMMDDTHHMMSSZ")
    p_rd.set_defaults(func=cmd_run_dir)

    p_rec = sub.add_parser("record", help="Write execution identity record (ws-record.json)")
    p_rec.add_argument("run_dir", help="Evidence run directory")
    p_rec.add_argument("--repo", action="append", help="Source repository / worktree path to record")
    p_rec.add_argument("--cmd", help="Command executed")
    p_rec.add_argument("--env-snapshot", help="Path to env snapshot")
    p_rec.add_argument("--env-var", action="append", help="Environment variable NAME used (never value)")
    p_rec.add_argument("--pkg", action="append", help="Python package to record path & version")
    p_rec.add_argument("--note", help="Extra note")
    p_rec.set_defaults(func=cmd_record)

    p_gate = sub.add_parser("gate", help="Run phase gate checks for a work item")
    p_gate.add_argument("id", help="Work item ID")
    p_gate.add_argument("--phase", help="Override phase (default: current phase in item.md)")
    p_gate.add_argument("--write", action="store_true", help="Append result to item.md gate log")
    p_gate.set_defaults(func=cmd_gate)

    p_lint = sub.add_parser("lint", help="Validate workspace links, indexes, naming, and hygiene")
    p_lint.set_defaults(func=cmd_lint)

    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
