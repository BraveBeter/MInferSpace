# 源码仓库与工作副本

通用规则见 [source-management.md](../framework/workflows/shared/source-management.md) 与 [git.md](../framework/conventions/git.md)。本表路径相对 `worktrees/`。

## 仓库与工作副本登记

<!-- ws:worktrees:begin -->
| 仓库 / 工作副本 | 用途 | 本地目录 | 对应远端仓库及分支 | 固定 commit |
| --- | --- | --- | --- | --- |
| sglang-omni / baseline | moss-speech 优化的源码起点及基线对照 | `sglang-omni/baseline/` | [BraveBeter/sglang-omni](https://github.com/BraveBeter/sglang-omni)，分支 `fix/moss-speech-all-modalities-review-20261111` | [`f4cef25c0f6809483224913300d82358abc701d7`](https://github.com/BraveBeter/sglang-omni/commit/f4cef25c0f6809483224913300d82358abc701d7) |
<!-- ws:worktrees:end -->

## 固定的 baseline 起点

- 本地目录：`sglang-omni/baseline/`。
- `origin`：`https://github.com/BraveBeter/sglang-omni.git`。
- 本地分支：`fix/moss-speech-all-modalities-review-20261111`（跟踪 `origin/fix/moss-speech-all-modalities-review-20261111`）。
- 完整 commit：[`f4cef25c0f6809483224913300d82358abc701d7`](https://github.com/BraveBeter/sglang-omni/commit/f4cef25c0f6809483224913300d82358abc701d7)。

优化与适配工作副本均从上述固定 commit 创建，远端分支后续更新不替换本次记录的起点。`baseline/` 保存同项目 worktree 共享的 Git 元数据，需持续保留。

## 本地文件系统适配

检出后部分脚本曾出现 `100755 → 100644` 的执行位差异，文件内容与提交一致。在 `sglang-omni` 本地 Git 配置中设置 `core.filemode=false` 忽略挂载目录的执行位差异；运行脚本时显式使用 `bash script.sh` 或 `python script.py`。
