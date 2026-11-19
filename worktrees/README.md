# 源码仓库与工作副本

这里统一存放优化所需的源码，以及可同时使用的基线和优化分支工作副本。

## 组织形式

每个项目一个目录，其下放基线与优化工作副本，计划结构如下：

```
worktrees/
├── README.md
└── sglang-omni/
    ├── baseline/               # 主克隆：保存 Git 元数据和基线源码
    ├── OPT-0001-xxx/           # 优化分支的 Git worktree
    └── OPT-0002-xxx/           # 另一项优化的 Git worktree
```

`baseline/` 通过 `git clone` 创建，其他优化工作副本通过该仓库的 `git worktree` 创建。各工作副本拥有独立的源码文件和分支，共享 Git 提交历史，不再单独设置 `repos/`。

本目录下的本地路径均相对 `worktrees/`。`xxx` 是优化内容的简短名称。从策略记录的完整起点 commit 创建优化分支，例如从工作区根目录执行：

```bash
git -C worktrees/sglang-omni/baseline worktree add -b OPT-0001-xxx ../OPT-0001-xxx <起点-SHA>
```

将 `<起点-SHA>` 替换为实际值。起点选择遵循 [基线推进规则](../strategies/README.md#基线推进)。

## 初始化依赖

两个依赖各自保留 Git 历史。以下命令从 `opt-loop` 根目录执行，使用已有的 GitHub SSH 访问权限。已有检出时，先确认远端、当前 commit 和工作树状态，再决定是否切换版本。

```bash
git clone --branch fix/moss-speech-all-modalities-review-20261111 --single-branch --no-checkout \
  git@github.com:BraveBeter/sglang-omni.git worktrees/sglang-omni/baseline
git -C worktrees/sglang-omni/baseline switch --detach f4cef25c0f6809483224913300d82358abc701d7
git -C worktrees/sglang-omni/baseline rev-parse HEAD

git clone --branch main --single-branch --no-checkout \
  git@github.com:BraveBeter/moss-speech-benchmark.git benchmark-client
git -C benchmark-client switch --detach ce69ea7a1620b5d6bb93d5675aa3991f1e90b8a9
git -C benchmark-client rev-parse HEAD
```

确认两条 `rev-parse` 的输出分别等于上方的固定 commit。获取分支用于下载提交历史，实际运行使用固定 commit；获取或核对失败时先解决依赖问题，再运行评测。

评测客户端需要 Python 3.10 或以上。使用选定解释器在独立环境验证 CLI；以下命令同样从工作区根目录执行。

```bash
python3 -m venv envs/runtime/benchmark-client
envs/runtime/benchmark-client/bin/python -m pip install -e ./benchmark-client
envs/runtime/benchmark-client/bin/python - <<'PY'
from moss_speech_bench.storage import source_identity

commit = source_identity()["commit"]
if commit != "ce69ea7a1620b5d6bb93d5675aa3991f1e90b8a9":
    raise SystemExit(f"评测客户端提交与固定版本不符：{commit}")
print(f"评测客户端提交：{commit}")
PY
envs/runtime/benchmark-client/bin/moss-speech-bench --help
```

## 当前已有工作副本

完成初始化后，`sglang-omni/baseline/` 是本地源码主克隆。下表用于登记实际创建的候选工作副本；新增、移除或推送后更新记录。

| 策略编号 | 本地目录 | 实现分支 | 远端引用 |
| --- | --- | --- | --- |
| 暂无 | — | — | — |

## 固定的 baseline 起点

初始化源码 commit 是 `OPT-0000` 的固定起点，其性能锚点由首次统一评测建立。主克隆保留该检出用于初始对照；对后续基线需要独立运行时，从相应策略的起点 commit 创建工作副本。

`baseline/` 内的 Git 元数据由同项目的优化 worktree 共享，需要持续保留；优化 worktree 的移除使用 `git worktree remove`。

## 策略结案与资源清理

先归档策略结论、受测 commit、执行材料和相关评测链接。核对 `git status --short`、其他策略和基线登记的引用、环境及缓存的共享情况。遇到未提交改动或仍被引用的资源时，保留对应资源并记录原因。

| 决定 | 结案时的资源处理 |
| --- | --- |
| `push` | 从登记的远端引用重新获取，确认已验收 commit 可取回后，再移除无其他用途的候选资源。 |
| `keep-local` | 保留指向最终 commit 的本地分支和复现所需的工作副本、环境及资产。 |
| `discard` | 归档实验结论和证据后，移除无其他引用的候选 worktree、专用环境及可重建缓存。 |

使用 `git worktree remove` 的默认检查移除干净的候选 worktree。共用环境、固定资产和作为基线或复现证据的提交按其引用保留。完成后更新工作副本登记，在策略中记录已执行的操作、保留项及原因。

## 本地文件系统适配

本次检出后，部分脚本出现 `100755 → 100644` 的执行位差异，文件内容与提交一致。已在该仓库的本地 Git 配置中设置 `core.filemode=false`，忽略挂载目录的执行位差异。该设置只影响本地 Git 对权限变化的判断，不恢复文件的执行权限；运行脚本时可显式使用 `bash script.sh` 或 `python script.py`。
