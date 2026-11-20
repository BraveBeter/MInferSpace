# 工作区入口

本工作区基于 [SG Model Workspace Framework](framework/README.md)（v{{FRAMEWORK_VERSION}}），项目事实见 [PROJECT.md](PROJECT.md)。

## 每次会话必读

1. [PROJECT.md](PROJECT.md)：目标、范围、资产、评测套件与验收口径。
2. [PLAN.md](PLAN.md)：活动工作项；续接工作时先读对应 `item.md` 的“状态与交接”节。
3. [framework/principles.md](framework/principles.md) 与 [framework/workflows/session.md](framework/workflows/session.md)。

## 按任务路由

| 你要做的事 | 先读 |
| --- | --- |
| 接到新任务 | [framework/workflows/intake.md](framework/workflows/intake.md) |
| 模型适配 / 能力扩展 | [framework/workflows/adapt.md](framework/workflows/adapt.md) |
| 性能分析 / 优化 / 建立基线 | [framework/workflows/optimize.md](framework/workflows/optimize.md) |
| 缺陷修复 | [framework/workflows/fix.md](framework/workflows/fix.md) |
| 技术调研 | [framework/workflows/research.md](framework/workflows/research.md) |
| 环境、资产、源码、评测、profile、正确性、审查、交付、复盘 | [framework/workflows/shared/](framework/workflows/shared/) 对应子流程 |
| 同步文档 | [framework/conventions/doc-sync-matrix.md](framework/conventions/doc-sync-matrix.md) |
| 修改目标源码仓库前 | 目标仓库的 `AGENTS.md`、`README.md`、`CONTRIBUTING` 及 [PROJECT.md](PROJECT.md) 所列开发者规范 |

## 硬性规则

- 阶段推进前运行 `python3 framework/tools/ws.py gate <ID> --write`；会话结束或提交前更新交接节并运行 `python3 framework/tools/ws.py lint`。
- 每条结论必须链接证据；不得将未执行或未验证的事项写成完成。
- 产生代码或结论的工作项须经独立审查（[code-review.md](framework/workflows/shared/code-review.md)）。
- 远端操作（push、PR）、修改验收口径、修改 `framework/` 前须征得用户确认（[autonomy.md](framework/conventions/autonomy.md)）。
