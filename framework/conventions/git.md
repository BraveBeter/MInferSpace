# Git 约定

工作区与源码仓库各自保持独立的 Git 历史：工作区仓库管理文档、配置、脚本与证据记录；源码仓库在 `worktrees/<repo>/` 中独立管理，内容不进入工作区仓库。

## 工作区仓库

- 工作区自身的修改在独立分支上进行，从用户指定的起点（默认 `main`）切出，分支名 `<类型>/<name>`，例如 `docs/xxx`、`feat/xxx`。
- 提交信息使用 `<类型>: <摘要>`，类型取 `feat`、`fix`、`docs`、`chore`、`refactor`、`test`；一次提交只做一件事。
- 提交前运行 `ws lint`，错误清零。
- 修改 `framework/` 的提交单独成组，便于后续 `git subtree push` 回馈。

## 源码仓库

- 主 clone 位于 `worktrees/<repo>/baseline/`（或项目登记的名称），保存 Git 元数据，持续保留；工作项通过 `git worktree add` 创建工作副本。
- 工作项分支从**固定的完整 commit** 创建，不以可能移动的远端分支名代替起点。
- 每个候选 commit 必须在 item.md 实验日志中出现，对应运行目录的执行材料记录同一 commit。
- 提交信息遵循目标仓库的规范；没有规范时同上。
- 小步提交；调试代码不进入提交。必要的未提交修改在执行材料中保存 patch（`ws record` 自动完成）。
- 移除工作副本使用 `git worktree remove`，并更新登记表。
- 不改写已被证据引用的 commit 历史（rebase、force push 前须确认无引用并获用户授权）。

## 远端操作

push、开 PR、在远端评论、删除远端分支均须用户授权，见[自主边界](autonomy.md)。
