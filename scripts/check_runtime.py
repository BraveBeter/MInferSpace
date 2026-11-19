"""Check and record the runtime identity before a formal benchmark."""

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys


class CheckError(Exception):
    """A check failed with a message safe to write to the run record."""


def require(condition, message):
    if not condition:
        raise CheckError(message)


def command(args, message, timeout=30):
    try:
        return subprocess.run(
            args, check=True, capture_output=True, text=True, timeout=timeout
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError, UnicodeError):
        raise CheckError(message) from None


def load_object(path, label):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise CheckError(f"Cannot read {label} JSON") from None
    require(isinstance(value, dict), f"{label} must be a JSON object")
    return value


def git_identity(root):
    def git(*args):
        return command(["git", "-C", str(root), *args], f"Git {args[0]} failed for source checkout")

    require(
        Path(git("rev-parse", "--show-toplevel")).resolve() == root,
        "Source path must be the root of the intended Git checkout",
    )
    status = git("status", "--porcelain=v1", "--untracked-files=all")
    return {
        "root": str(root),
        "commit": git("rev-parse", "HEAD"),
        "branch": git("branch", "--show-current"),
        "dirty": bool(status),
        "worktree_status": status.splitlines(),
    }


def e2e_identity(args, evidence):
    deployment = load_object(args.deployment, "deployment")
    expected = deployment.get("server")
    require(isinstance(expected, dict), "deployment.server must declare the service identity")
    commit = expected.get("commit")
    require(
        isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40}", commit),
        "deployment.server.commit must be a full Git SHA",
    )
    require(type(expected.get("dirty")) is bool, "deployment.server.dirty must be a boolean")
    hardware = deployment.get("hardware", {})
    require(isinstance(hardware, dict), "deployment.hardware must be a JSON object")
    if "gpu_count" in hardware:
        count = hardware["gpu_count"]
        require(type(count) is int and count == len(args.gpu),
                "Selected GPU count differs from deployment.hardware.gpu_count")
    root = args.source.resolve()
    identity = git_identity(root)
    evidence["source"] = identity
    probe_args = []
    if args.launcher:
        launcher = args.launcher.resolve()
        require(launcher.is_file(), "Cannot find the service's Python launcher")
        evidence["launcher"] = str(launcher)
        probe_args.append(str(launcher.parent))
    probe = (
        "import contextlib, io, sys\n"
        "if sys.argv[1:] and not getattr(sys.flags, 'safe_path', False):\n"
        "    sys.path[0] = sys.argv[1]\n"
        "with contextlib.redirect_stdout(io.StringIO()):\n"
        "    import sglang_omni\n"
        "print(sglang_omni.__file__)\n"
    )
    module = Path(command(
        [sys.executable, "-c", probe, *probe_args],
        "Cannot import sglang_omni with the service Python",
    ))
    require(module.is_file(), "Cannot determine the imported sglang_omni module file")
    module = module.resolve()
    identity["module_path"] = str(module)
    require(
        module.is_relative_to(root / "sglang_omni"),
        "Imported sglang_omni is outside the expected source package",
    )
    for key in ("commit", "dirty", "branch"):
        if key in expected:
            require(identity[key] == expected[key], f"Runtime {key} differs from deployment.server.{key}")
    return args.gpu


def config_path(config, key, base):
    value = config.get(key)
    require(isinstance(value, str) and value.strip(), f"Codec config must declare {key}")
    return Path(os.path.abspath(base / value))


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as asset:
        for block in iter(lambda: asset.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def codec_identity(args, evidence):
    path = args.config.resolve()
    config = load_object(path, "Codec config")
    backend = config.get("backend")
    require(backend in ("hf-native", "sg-native"), "Unsupported Codec backend")
    gpu = config.get("physical_gpu")
    require(type(gpu) is int and gpu >= 0, "Codec config must declare a physical GPU index")
    python = config_path(config, "python", path.parent)
    evidence["codec"] = {"backend": backend, "config": str(path), "configured_python": str(python)}
    # Keep the venv path: resolving both binaries would hide two venvs sharing one interpreter.
    require(python == Path(os.path.abspath(sys.executable)), "Runtime Python differs from Codec config")
    codec_root = config_path(config, "codec_path", path.parent).resolve()
    require(codec_root.is_dir(), "Codec asset directory is missing")
    evidence["codec"]["codec_path"] = str(codec_root)
    if backend == "sg-native":
        source = config_path(config, "model_root", path.parent).resolve()
        identity = git_identity(source)
        evidence["source"] = identity
        require(
            identity["commit"] == config.get("model_sha") and not identity["dirty"],
            "Codec model checkout differs from the configured clean SHA",
        )
    else:
        source = config_path(config, "hf_source_root", path.parent).resolve()
        require(source.is_dir(), "HF Codec dependency source directory is missing")
        evidence["codec"]["hf_source_root"] = str(source)
    assets = config.get("assets")
    require(isinstance(assets, list) and assets, "Codec config must declare frozen assets")
    evidence["codec"]["assets"] = checked_assets = []
    for asset in assets:
        require(isinstance(asset, dict), "Each Codec asset must declare a path and SHA-256")
        asset_path = config_path(asset, "path", path.parent).resolve()
        require(asset_path.is_file(), f"Codec asset is missing: {asset_path}")
        actual = sha256(asset_path)
        checked_assets.append({"path": str(asset_path), "sha256": actual})
        require(actual == asset.get("sha256"), f"Codec asset SHA-256 mismatch: {asset_path}")
    return [gpu]


def gpu_snapshot(indices, evidence, allowed_pids):
    require(len(indices) == len(set(indices)), "GPU indices must be unique")
    options = "--format=csv,noheader,nounits"
    devices = []
    evidence["gpus"] = devices
    for index in indices:
        output = command(
            ["nvidia-smi", f"--id={index}",
             "--query-gpu=index,uuid,power.draw,clocks.current.sm,clocks.current.memory", options],
            f"Cannot read nvidia-smi telemetry for GPU {index}",
        )
        rows = list(csv.reader(output.splitlines(), skipinitialspace=True))
        require(len(rows) == 1 and len(rows[0]) == 5, f"Incomplete telemetry for GPU {index}")
        found, uuid, *telemetry = rows[0]
        require(found == str(index) and uuid.startswith("GPU-"), f"Cannot identify physical GPU {index}")
        try:
            power, sm_clock, memory_clock = map(float, telemetry)
        except ValueError:
            raise CheckError(f"Missing power or clock telemetry for GPU {index}") from None
        require(
            all(math.isfinite(value) and value >= 0 for value in (power, sm_clock, memory_clock)),
            f"Invalid power or clock telemetry for GPU {index}",
        )
        devices.append({
            "index": index,
            "uuid": uuid,
            "power_w": power,
            "sm_clock_mhz": sm_clock,
            "memory_clock_mhz": memory_clock,
            "compute_pids": [],
        })

    output = command(
        ["nvidia-smi", "--query-compute-apps=gpu_uuid,pid", options],
        "Cannot read nvidia-smi compute processes",
    )
    by_uuid = {gpu["uuid"]: gpu for gpu in devices}
    allowed_pids = set(allowed_pids)
    outside = []
    for row in csv.reader(output.splitlines(), skipinitialspace=True):
        require(len(row) == 2 and row[0].startswith("GPU-"), "Invalid GPU compute process listing")
        uuid, pid = row
        if uuid in by_uuid:
            require(pid.isdecimal() and int(pid) > 0, "Missing PID for a selected GPU compute process")
            by_uuid[uuid]["compute_pids"].append(int(pid))
        elif pid.isdecimal() and int(pid) in allowed_pids:
            outside.append({"uuid": uuid, "pid": int(pid)})
    if outside:
        evidence["service_pids_on_other_gpus"] = outside
        raise CheckError("Service GPU compute processes also use unselected GPUs")
    observed = {pid for gpu in devices for pid in gpu["compute_pids"]}
    unexpected = observed - allowed_pids
    require(not unexpected, "Unexpected GPU compute PIDs: " + ", ".join(map(str, sorted(unexpected))))
    missing = allowed_pids - observed
    require(not missing, "Service PIDs absent from selected GPUs: " + ", ".join(map(str, sorted(missing))))


def index_arg(value):
    if not value.isdecimal():
        raise argparse.ArgumentTypeError("expected a non-negative integer")
    return int(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    modes = parser.add_subparsers(dest="mode", required=True)
    e2e = modes.add_parser("e2e")
    e2e.add_argument("--deployment", type=Path, required=True)
    e2e.add_argument("--source", type=Path, required=True)
    e2e.add_argument("--launcher", type=Path, help="Python script used to launch the service, if any")
    e2e.add_argument("--gpu", type=index_arg, action="append", required=True)
    e2e.add_argument("--allow-gpu-pid", type=index_arg, action="append", default=[])
    codec = modes.add_parser("codec")
    codec.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    execution = args.output_dir / "execution"
    record = {
        "mode": args.mode,
        "timestamp_utc": now.isoformat(),
        "cwd": str(Path.cwd()),
        "python": sys.executable,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "allowed_gpu_pids": getattr(args, "allow_gpu_pid", []),
    }
    try:
        check = e2e_identity if args.mode == "e2e" else codec_identity
        gpu_snapshot(check(args, record), record, record["allowed_gpu_pids"])
        record["status"] = "passed"
    except (CheckError, OSError) as error:
        record.update(status="failed", error=str(error))

    try:
        execution.mkdir(parents=True, exist_ok=True)
        filename = execution / f"preflight-{now:%Y%m%dT%H%M%S%fZ}-{os.getpid()}.json"
        with filename.open("x", encoding="utf-8") as stream:
            json.dump(record, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    except OSError as error:
        print(f"Cannot write preflight evidence: {error}", file=sys.stderr)
        return 1
    if record["status"] == "failed":
        print(f"Preflight failed: {record['error']} ({filename})", file=sys.stderr)
        return 1
    print(f"Preflight passed: {filename}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
