# 变更记录

版本遵循语义化版本：不兼容的目录、模板或工作项格式变化升主版本（0.x 期间升次版本），并附迁移说明。

## 0.1.0 — 2026-11-20

首个版本，从 MInferSpace（moss-speech on sglang-omni 优化工作区）的目录约定中抽取并泛化。

- 新增三层结构：框架层 `framework/`、项目层、证据层。
- 新增工作流：intake、session、adapt（A0–A7）、optimize（O0–O6）、fix（F0–F4）、research（R0–R2）及 9 个 shared 子流程。
- 新增门禁清单与 `ws gate`；新增代码质量门禁与独立审查 Agent 流程。
- 新增约定：命名、工作项、文档、事件 → 文档同步矩阵、目录布局、Git、证据、自主边界、默认验收口径。
- 新增模板：四类工作项、适配设计、profile 分析、正确性验证报告、审查记录、实例骨架。
- 新增参考知识库首批条目（均标注核验状态）。
- 新增 `ws` 工具：`init`、`new`、`status`、`gate`、`run-dir`、`record`、`lint`。

迁移说明（对 MInferSpace 原结构）：

- `strategies/` → `work/`；`OPT-xxxx` 编号保持不变，`strategy.md` → `item.md`。
- 目录 README 中的通用规则移入 `framework/`，README 只保留用途、项目细则和登记表。
- profile 运行目录命名由 `<UTC>-opt0001-<tool>-<role>` 改为 `<UTC>-OPT-0001-<tool>-<role>`。
