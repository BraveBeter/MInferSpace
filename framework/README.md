# SG Model Workspace Framework

版本：**0.1.0**（变更见 [CHANGELOG.md](CHANGELOG.md)）

本框架定义“模型适配 on SG”与“模型优化 on SG”的通用工作方式。SG 指 SGLang 及其衍生引擎（如 sglang-omni）。框架规定流程、门禁、约定、模板与参考，不包含任何具体项目的事实；项目事实由实例工作区的 `PROJECT.md` 及各目录登记表维护。

## 三层结构

| 层 | 位置 | 回答的问题 | 修改方式 |
| --- | --- | --- | --- |
| 框架层 | `framework/` | 怎么做才规范、高质量 | 只通过[框架改进流程](workflows/shared/retro.md#框架改进)修改，任务中只读 |
| 项目层 | `AGENTS.md`、`PROJECT.md`、`PLAN.md`、`work/`、`knowledge/`、资产目录 | 做什么、用什么、进行到哪 | Agent 按[同步矩阵](conventions/doc-sync-matrix.md)维护 |
| 证据层 | `benchmark-results/`、`profile-results/`、`validation-results/` | 实际跑了什么、结果如何 | 工具生成，Agent 补充分析，只追加 |

## 阅读顺序

实例的 `AGENTS.md` 是唯一入口。之后按需加载：

1. [principles.md](principles.md)：通用原则与规范优先级。
2. [workflows/intake.md](workflows/intake.md)：新任务的分类与建项；[workflows/session.md](workflows/session.md)：会话与交接协议。
3. [workflows/adapt.md](workflows/adapt.md)、[workflows/optimize.md](workflows/optimize.md)、[workflows/fix.md](workflows/fix.md) 或 [workflows/research.md](workflows/research.md)：主流程，每阶段列出“本阶段必读”。
4. 阶段引用的 [shared 子流程](workflows/shared/)、[gates](gates/README.md)、[templates](templates/)、[references](references/README.md)。

## 目录导览

| 路径 | 内容 |
| --- | --- |
| [principles.md](principles.md) | 通用原则、规范优先级 |
| [workflows/](workflows/) | intake、session、adapt、optimize、fix、research 与 shared 子流程 |
| [gates/](gates/README.md) | 各阶段门禁清单及格式 |
| [conventions/](conventions/) | 命名、工作项、文档、同步矩阵、目录布局、Git、证据、自主边界、默认验收口径 |
| [templates/](templates/) | 工作项、设计、分析、审查模板，以及新实例骨架 `templates/instance/` |
| [references/](references/README.md) | 通用知识库（SG 导航、适配手册、优化手册、profiling、benchmark 方法、常见陷阱） |
| [tools/](tools/README.md) | `ws` 命令行工具：建项、门禁、记录、校验、新建实例 |

## 分发与升级

采用 **git subtree** 分发，理由：框架文件直接存在于实例工作树中，Agent 无需额外初始化即可阅读；实例 clone 即完整可用；升级和回馈都有标准命令；不会出现 submodule 的游离 HEAD 或误改子仓库问题。

| 场景 | 做法 |
| --- | --- |
| 当前（0.x） | 框架在首个实例工作区的 `framework/` 中孵化 |
| 发布独立框架仓库 | `git subtree split --prefix=framework -b framework-release`，推送到框架仓库并打 tag |
| 新建实例 | 新工作区 `git subtree add --prefix=framework <框架仓库> <tag> --squash`，然后 `python3 framework/tools/ws.py init .` 生成实例骨架 |
| 升级框架 | `git subtree pull --prefix=framework <框架仓库> <新tag> --squash`，按 CHANGELOG 的迁移说明调整实例，并更新 `PROJECT.md` 中的框架版本 |
| 回馈改进 | 在实例中按框架改进流程修改并经用户批准后，`git subtree push` 或向框架仓库提交 PR |

推送、发布等远端操作均需用户授权。

## 可覆盖项

实例只能在框架明确允许的位置调整默认行为：

- 验收口径与阈值：见 [conventions/defaults.md](conventions/defaults.md)，在 `PROJECT.md` 中覆盖，单个工作项可在用户确认后进一步覆盖。
- 评测套件、关键场景、自主边界参数：在 `PROJECT.md` 中声明。
- 目录级的项目细则（客户端产物、数据字段等）：写在实例对应目录的 README 中，不改写框架规则。

## 设计决策记录

| 决策 | 结论 |
| --- | --- |
| 实例粒度 | 一个工作区一个项目（模型 × 引擎） |
| 分发方式 | git subtree（见上） |
| 独立审查 | 默认引入第二个 Agent 审查代码与结论，见 [code-review.md](workflows/shared/code-review.md) |
| 默认验收口径 | 采用 [defaults.md](conventions/defaults.md)，允许项目与工作项覆盖 |
| 文档语言 | 0.x 使用中文；标识符、命令、路径保留原文 |
