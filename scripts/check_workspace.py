"""Read-only checks for workspace links, task records, and repository files."""

from dataclasses import dataclass
from functools import lru_cache
import io
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit


TASK_DIR = re.compile(r"((?:ADP|OPT)-[0-9]{4})-[a-z0-9]+(?:-[a-z0-9]+)*")
STATES = {"planned", "in-progress", "blocked", "done", "cancelled"}
CLOSED_STATES = {"done", "cancelled"}
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
INLINE_CODE = re.compile(r"(`+)(?!`)(.*?)\1(?!`)")
LINK_DESTINATION = r"(?:<([^>]+)>|([^\s()]+(?:\([^()\n]*\)[^\s()]*)*))"
INLINE_LINK = re.compile(r"(?<!\\)\]\(\s*" + LINK_DESTINATION + r"(?=\s|\))")
REFERENCE_LINK = re.compile(r"^ {0,3}\[[^\]]+\]:\s*" + LINK_DESTINATION)
PLAN_HEADER = ("任务编号", "任务文档")
MAX_SIZE = 10 * 1024 * 1024
CREDENTIALS = {
    "private key": re.compile(rb"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----"),
    "GitHub token": re.compile(rb"\b(?:gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{80,255})\b"),
    "Slack token": re.compile(rb"\bxox[baprs]-[0-9]+-[A-Za-z0-9-]{10,}\b"),
}


@dataclass(frozen=True)
class Task:
    path: Path
    state: str


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
        yield number, tuple(cell.strip("`") for cell in cells)


def load_tasks(root, documents, report):
    tasks = {}
    seen = set()
    for path in documents:
        parts = path.relative_to(root).parts
        if parts[0] != "tasks" or path.name != "task.md":
            continue
        folder = TASK_DIR.fullmatch(parts[1]) if len(parts) == 3 else None
        if not folder:
            report(path, None, "task directory must use ADP-0001-short-name or OPT-0001-short-name")
            continue
        number = folder[1]
        if number in seen:
            report(path, None, f"duplicate task ID {number}")
            continue
        seen.add(number)
        fields = {}
        for line, (key, value) in table_rows(path, ("字段", "值"), report):
            if key in fields:
                report(path, line, f"duplicate task field {key}")
            fields[key] = value
        if fields.get("任务编号") != number:
            report(path, None, f"任务编号 must match directory ID {number}")
        state = fields.get("状态", "")
        if state not in STATES:
            report(path, None, "状态 must be planned, in-progress, blocked, done, or cancelled")
        tasks[number] = Task(path, state)
    return tasks


def check_plan(root, tasks, report):
    plan = root / "PLAN.md"
    seen = set()
    for line, (number, cell) in table_rows(plan, PLAN_HEADER, report):
        task = tasks.get(number)
        if task is None:
            report(plan, line, f"unknown task ID {number}")
            continue
        if number in seen:
            report(plan, line, f"duplicate plan row for {number}")
        seen.add(number)
        if task.state in CLOSED_STATES:
            report(plan, line, f"closed task {number} must be removed from PLAN.md")
        try:
            (target,) = (local_link(root, plan, url)[0] for url in links(cell))
        except (OSError, ValueError, RuntimeError):
            target = None
        if target != task.path:
            report(plan, line, f"plan link for {number} must target its task.md")
    for number, task in tasks.items():
        if task.state not in CLOSED_STATES and number not in seen:
            report(plan, None, f"missing plan row for {number}")


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


def check_workspace(root):
    read_markdown.cache_clear()
    markdown_anchors.cache_clear()
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
        return ["Cannot inspect workspace files with Git"]
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
    check_plan(root, load_tasks(root, documents, report), report)
    return list(dict.fromkeys(problems))


def main():
    root = Path(__file__).resolve().parents[1]
    problems = check_workspace(root)
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    print("Workspace checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
