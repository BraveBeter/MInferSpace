# 共享子流程：源码管理

## 组织

```text
worktrees/
├── README.md
└── <repo>/
    ├── baseline/                 # 主 clone：保存 Git 元数据与基线源码
    ├── <小写ID>-<name>/          # 工作项的 git worktree
    └── ...
```

- 每个仓库一个目录；`baseline/` 由 `git clone` 创建，其余由 `git worktree add` 创建，共享提交历史。
- 本目录内容不进入工作区 Git；登记信息写在 `worktrees/README.md`。
- 适配工作的参考实现（如 transformers、官方仓库）同样放在本目录并登记固定 commit。

## 固定起点

- 为每个仓库登记固定起点：本地目录、`origin`、分支、完整 commit（附远端链接）。
- 起点记录的是源码起点；性能基线由 benchmark 确定。
- 远端分支之后可能移动，不能用其最新位置替换已登记的起点。推进起点时追加新登记并注明原因，旧登记保留（旧证据仍引用）。

## 工作项 worktree

```bash
# 在主 clone 中执行，示例
git -C worktrees/<repo>/baseline worktree add ../<小写ID>-<name> -b <类型>/<编号>-<name> <完整起点commit>
```

- 创建后登记：工作副本、用途（工作项 ID）、本地目录、分支、起点 commit。
- 工作项结项时按决定处置：保留（keep-local）、推送后保留或移除、放弃后移除。移除使用 `git worktree remove`，更新登记表；仍被证据引用的分支保留。

## 本地适配

文件系统差异（例如挂载目录的执行位）等本地 Git 配置调整，记录在 `worktrees/README.md` 的“本地适配”节，说明影响范围。
