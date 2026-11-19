"""Read-only checks for opt-loop documentation, strategy indexes, and files."""

from dataclasses import dataclass
from functools import lru_cache
import io
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit


STRATEGY_ID = r"OPT-[0-9]{4}"
STRATEGY_DIR = re.compile(rf"({STRATEGY_ID})-[a-z0-9]+(?:-[a-z0-9]+)*")
SHA = re.compile(r"[a-f0-9]{40}")
STATES = {"planned", "profiling", "implementing", "benchmarking", "decided", "blocked", "cancelled"}
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
INLINE_CODE = re.compile(r"(`+)(?!`)(.*?)\1(?!`)")
LINK_DESTINATION = r"(?:<([^>]+)>|([^\s()]+(?:\([^()\n]*\)[^\s()]*)*))"
INLINE_LINK = re.compile(r"(?<!\\)\]\(\s*" + LINK_DESTINATION + r"(?=\s|\))")
REFERENCE_LINK = re.compile(r"^ {0,3}\[[^\]]+\]:\s*" + LINK_DESTINATION)
STRATEGY_FIELDS = ("策略编号", "状态", "起点 commit", "前置策略", "决定", "执行状态")
STRATEGY_INDEX = ("策略编号", "名称", "策略简述", "状态", "起点 commit", "实现分支", "关键结果/结论")
PLAN_INDEX = ("策略编号", "策略简述", "状态进度", "引用 strategy.md", "起点 commit")
MAX_SIZE = 10 * 1024 * 1024
CREDENTIALS = {
    "private key": re.compile(rb"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----"),
    "GitHub token": re.compile(rb"\b(?:gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{80,255})\b"),
    "Slack token": re.compile(rb"\bxox[baprs]-[0-9]+-[A-Za-z0-9-]{10,}\b"),
}


@dataclass(frozen=True)
class Strategy:
    path: Path
    state: str
    commit: str
    predecessor: str
    closed: bool


def markdown_lines(text):
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = FENCE.match(line)
        if fence:
            if marker and marker[1].startswith(fence) and not marker[2].strip():
                fence = None
        elif marker:
            fence = marker[1]
        else:
            yield number, line


@lru_cache(maxsize=None)
def read_markdown(path):
    return tuple(markdown_lines(path.read_text(encoding="utf-8")))


def links(line):
    content = INLINE_CODE.sub("", line)
    for match in INLINE_LINK.finditer(content):
        yield match[1] or match[2]
    definition = REFERENCE_LINK.match(content)
    if definition:
        yield definition[1] or definition[2]


@lru_cache(maxsize=None)
def markdown_anchors(path):
    anchors = set()
    counts = {}
    previous = ""
    for _, line in read_markdown(path):
        anchors.update(re.findall(r'<a\s+(?:id|name)=[\'"]([^\'"]+)', line, re.IGNORECASE))
        atx = re.match(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        heading = atx[1] if atx else ""
        if previous.strip() and re.fullmatch(r" {0,3}(?:=+|-+)\s*", line):
            heading = previous.strip()
        previous = line
        if heading:
            plain = re.sub(r"<[^>]+>", "", heading).lower()
            slug = re.sub(r"[^\w\- ]", "", plain).replace(" ", "-")
            count = counts.get(slug, 0)
            candidate = f"{slug}-{count}" if count else slug
            while candidate in anchors:
                count += 1
                candidate = f"{slug}-{count}"
            counts[slug] = count + 1
            anchors.add(candidate)
    return anchors


def local_link(root, document, url):
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc:
        return None, ""
    path = unquote(parsed.path)
    target = Path(os.path.abspath(document.parent / path)) if path else document
    if path.startswith("/") or not target.resolve().is_relative_to(root):
        raise ValueError("local Markdown link must stay within the workspace")
    return target, unquote(parsed.fragment)


def check_links(root, document, available, report):
    for number, line in read_markdown(document):
        for url in links(line):
            try:
                target, anchor = local_link(root, document, url)
                if target is None:
                    continue
                if not target.exists():
                    report(document, number, "missing relative Markdown link target")
                elif target not in available or (target.is_symlink() and target.resolve() not in available):
                    report(document, number, "relative Markdown link target would be absent from a clone")
                elif anchor and target.suffix.lower() == ".md" and anchor not in markdown_anchors(target):
                    report(document, number, "missing relative Markdown heading or anchor")
            except (OSError, ValueError, RuntimeError):
                report(document, number, "invalid local Markdown link")


def table_cells(line):
    line = line.strip()
    if not line.startswith("|") or not line.endswith("|"):
        return ()
    return tuple(cell.strip() for cell in re.split(r"(?<!\\)\|", line[1:-1]))


def table_rows(path, header, report):
    try:
        lines = iter(read_markdown(path))
    except (OSError, UnicodeError):
        report(path, None, "cannot read required UTF-8 Markdown")
        return
    for number, line in lines:
        if table_cells(line) == header:
            break
    else:
        report(path, None, f"missing table with columns {' / '.join(header)}")
        return
    _, separator = next(lines, (number, ""))
    rules = table_cells(separator)
    if len(rules) != len(header) or not all(re.fullmatch(r":?-{3,}:?", rule) for rule in rules):
        report(path, number, "invalid Markdown table separator")
        return
    for number, line in lines:
        cells = table_cells(line)
        if not cells:
            break
        if len(cells) != len(header):
            report(path, number, "wrong number of Markdown table cells")
            continue
        if cells[0] != "暂无":
            yield number, tuple(cell.strip("`") for cell in cells)


def load_strategies(root, documents, report):
    strategies = {}
    seen = set()
    for path in documents:
        parts = path.relative_to(root).parts
        if parts[0] != "strategies" or path.name != "strategy.md":
            continue
        name = STRATEGY_DIR.fullmatch(parts[1]) if len(parts) == 3 else None
        if not name:
            report(path, None, "strategy directory must use OPT-0000-short-name")
            continue
        number = name[1]
        if number in seen:
            report(path, None, f"duplicate strategy document for {number}")
            continue
        seen.add(number)
        fields = {}
        for line, (key, value) in table_rows(path, ("字段", "值"), report):
            if key in fields:
                report(path, line, "duplicate strategy metadata field")
            fields[key] = value
        missing = [field for field in STRATEGY_FIELDS if not fields.get(field)]
        if missing:
            report(path, None, f"missing strategy fields {' / '.join(missing)}")
            continue
        if fields["策略编号"] != number:
            report(path, None, "strategy ID does not match the directory")
        state, commit, predecessor, decision, execution = (fields[key] for key in STRATEGY_FIELDS[1:])
        if state not in STATES:
            report(path, None, "invalid strategy state")
        if not SHA.fullmatch(commit):
            report(path, None, "starting commit must be a full Git SHA")
        if decision not in {"—", "push", "keep-local", "discard"} or execution not in {"—", "pending", "executed"}:
            report(path, None, "invalid decision or execution state")
        if (decision == "—") != (execution == "—") or (state == "decided" and decision == "—"):
            report(path, None, "strategy decision and execution state must agree")
        if execution == "executed" and state not in {"decided", "cancelled"}:
            report(path, None, "executed decision requires a terminal strategy state")
        closed = state == "cancelled" or (state == "decided" and execution == "executed")
        strategies[number] = Strategy(path, state, commit, predecessor, closed)
    for number, strategy in strategies.items():
        if strategy.predecessor != "—" and (
            strategy.predecessor not in strategies or strategy.predecessor == number
        ):
            report(strategy.path, None, "invalid predecessor strategy reference")
    return strategies


def strategy_reference(number, strategies, report, path, line):
    number = re.fullmatch(STRATEGY_ID, number)
    if not number or number[0] not in strategies:
        report(path, line, "invalid or unknown strategy reference")
        return None
    return strategies[number[0]]


def check_strategy_link(root, path, line, cell, expected, report):
    try:
        target, = (local_link(root, path, url)[0] for url in links(cell))
    except (OSError, ValueError, RuntimeError):
        target = None
    if target != expected:
        report(path, line, "strategy link must point to the matching strategy.md")


def check_status_index(root, path, header, columns, strategies, plan, report):
    seen = set()
    name_col, state_col, commit_col = columns
    for line, row in table_rows(path, header, report):
        number = row[0]
        strategy = strategy_reference(number, strategies, report, path, line)
        if not strategy:
            continue
        if number in seen:
            report(path, line, f"duplicate index row for {number}")
        seen.add(number)
        if row[state_col] != strategy.state:
            report(path, line, f"state differs from strategy.md for {number}")
        if row[commit_col] != strategy.commit:
            report(path, line, f"starting commit differs from strategy.md for {number}")
        if plan and strategy.closed:
            report(path, line, f"closed strategy {number} must be removed from PLAN.md")
        check_strategy_link(root, path, line, row[name_col], strategy.path, report)
    for number, strategy in strategies.items():
        if number not in seen and (not plan or not strategy.closed):
            report(path, None, f"missing index row for {number}")


def check_profile_index(root, report):
    path = root / "profile-results/README.md"
    header = ("源码分支", "完整 commit", "采集目录", "工具", "用途")
    seen = set()
    for line, (branch, commit, directory, tool, _) in table_rows(path, header, report):
        # Git forbids '~' in refs, which keeps slash escaping reversible.
        branch = branch.replace(r"\|", "|")
        try:
            git_output(root, "check-ref-format", f"refs/heads/{branch}")
        except subprocess.CalledProcessError:
            report(path, line, "profile source branch must be a valid Git branch name")
            continue
        if not SHA.fullmatch(commit):
            report(path, line, "profile commit must be a full Git SHA")
            continue
        try:
            (target, anchor), = (local_link(root, path, url) for url in links(directory))
        except (OSError, ValueError, RuntimeError):
            target, anchor = None, ""
        identity = f"{branch.replace('/', '~')}-{commit}"
        if (
            target is None
            or anchor
            or target.parent != path.parent / identity
            or not target.is_dir()
        ):
            report(path, line, "profile directory link must match the source branch and full SHA")
            continue
        run_pattern = rf"[0-9]{{8}}T[0-9]{{6}}Z-{re.escape(tool)}(?:-[0-9]{{2,}})?"
        if (
            not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", tool)
            or not re.fullmatch(run_pattern, target.name)
        ):
            report(path, line, "profile run ID must contain the UTC start time and tool name")
        if target in seen:
            report(path, line, "duplicate profile directory in index")
        seen.add(target)


def check_run_indexes(root, strategies, report):
    worktrees = root / "worktrees/README.md"
    seen_directories = set()
    for line, (number, directory, branch, _) in table_rows(
        worktrees, ("策略编号", "本地目录", "实现分支", "远端引用"), report
    ):
        if strategy_reference(number, strategies, report, worktrees, line):
            if not Path(directory).name.startswith(number + "-") or not branch.startswith(number + "-"):
                report(worktrees, line, "worktree directory and branch must start with the strategy ID")
            if directory in seen_directories:
                report(worktrees, line, "duplicate worktree directory in index")
            seen_directories.add(directory)
    benchmarks = root / "benchmark-results/README.md"
    seen = set()
    for line, (number, cell, *_run_links) in table_rows(
        benchmarks, ("策略编号", "策略文档", "关键基线", "关键候选", "结论或备注"), report
    ):
        strategy = strategy_reference(number, strategies, report, benchmarks, line)
        if strategy:
            if number in seen:
                report(benchmarks, line, f"duplicate index row for {number}")
            seen.add(number)
            check_strategy_link(root, benchmarks, line, cell, strategy.path, report)


def check_baseline_index(path, strategies, report):
    rows = list(table_rows(path, ("当前基线策略", "完整 commit", "已验收评测"), report))
    if len(rows) != 1:
        report(path, None, "current baseline table must have one row")
        return
    line, (number, commit, evidence) = rows[0]
    if (number, commit, evidence) == ("待建立（`OPT-0000`）", "—", "—"):
        return
    strategy_reference(number, strategies, report, path, line)
    if not SHA.fullmatch(commit) or not tuple(links(evidence)):
        report(path, line, "baseline registration requires a full SHA and an evaluation link")


def scan_credentials(path, stream, report):
    if b"\x00" in stream.read(8192):
        return
    stream.seek(0)
    for line, content in enumerate(stream, 1):
        for kind, regex in CREDENTIALS.items():
            if regex.search(content):
                report(path, line, f"possible credential ({kind})")


def scan_file(root, path, report):
    try:
        if path.stat().st_size > MAX_SIZE:
            attributes = git_output(root, "check-attr", "-z", "filter", "--", path.relative_to(root))
            if not attributes.endswith(b"\0lfs\0"):
                report(path, None, "file exceeds 10 MiB")
                return False
        with path.open("rb") as stream:
            scan_credentials(path, stream, report)
        return True
    except (OSError, subprocess.CalledProcessError):
        report(path, None, "cannot scan file")
        return False


def git_output(root, *args):
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True
    ).stdout


def git_paths(root, *args):
    return {root / os.fsdecode(name) for name in git_output(root, *args).split(b"\0") if name}


def available_link_targets(root, paths):
    targets = {root}
    for path in paths:
        if path.is_file() or path.is_symlink():
            targets.add(path)
            targets.update(parent for parent in path.parents if parent.is_relative_to(root))
    return targets


def check_staged_files(root, report):
    paths = git_paths(root, "diff", "--cached", "--name-only", "--diff-filter=ACMRT", "-z")
    for path in sorted(paths):
        blob = ":" + path.relative_to(root).as_posix()
        if git_output(root, "cat-file", "-t", blob).strip() != b"blob":
            continue
        if int(git_output(root, "cat-file", "-s", blob)) > MAX_SIZE:
            report(path, None, "file exceeds 10 MiB")
        else:
            scan_credentials(path, io.BytesIO(git_output(root, "cat-file", "blob", blob)), report)


def main():
    root = Path(__file__).resolve().parents[1]
    problems = []

    def report(path, line, message):
        location = str(path.relative_to(root))
        if line:
            location += f":{line}"
        problems.append(f"{location}: {message}")

    try:
        paths = git_paths(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
        check_staged_files(root, report)
    except (OSError, subprocess.CalledProcessError):
        print("Cannot inspect workspace files with Git", file=sys.stderr)
        return 1
    available = available_link_targets(root, paths)
    documents = []
    for path in sorted(paths):
        if path.is_symlink() or not path.is_file():
            continue
        if not path.resolve().is_relative_to(root):
            report(path, None, "workspace file resolves outside the workspace")
            continue
        if scan_file(root, path, report) and path.suffix.lower() == ".md":
            try:
                check_links(root, path, available, report)
            except (OSError, UnicodeError):
                report(path, None, "cannot read UTF-8 Markdown")
            documents.append(path)
    strategies = load_strategies(root, documents, report)
    registry = root / "strategies/README.md"
    check_baseline_index(registry, strategies, report)
    check_status_index(root, registry, STRATEGY_INDEX, (1, 3, 4), strategies, False, report)
    check_status_index(root, root / "PLAN.md", PLAN_INDEX, (3, 2, 4), strategies, True, report)
    check_profile_index(root, report)
    check_run_indexes(root, strategies, report)
    for problem in dict.fromkeys(problems):
        print(problem, file=sys.stderr)
    if problems:
        return 1
    print("Workspace checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
