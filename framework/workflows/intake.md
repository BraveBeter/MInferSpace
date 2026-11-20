# 任务接入

收到用户任务（通常只有一句话）后，按以下步骤进入工作流。会话的开始、阶段结束和中断动作见 [session.md](session.md)。

## 1. 分类

| 用户说法示例 | 类型 | 工作流 |
| --- | --- | --- |
| “把 X 接到 SG”“支持 X 的 TP / 量化 / 流式” | ADAPT | [adapt.md](adapt.md) |
| “优化 X 的吞吐 / 首包 / 显存” | OPT | [optimize.md](optimize.md) |
| “这里为什么慢” | OPT（可只做到 O2，结论写在 item.md） | [optimize.md](optimize.md) |
| “建立基线”“测一下当前性能” | OPT-0000 或现有 OPT 项的 O1 | [optimize.md](optimize.md) |
| “X 的输出不对”“修复 Y 报错” | FIX | [fix.md](fix.md) |
| “调研 Y 是否可行”“比较几种方案” | RES | [research.md](research.md) |
| 只涉及工作区文档、登记或工具维护 | 无需工作项 | 按[同步矩阵](../conventions/doc-sync-matrix.md)与 [git.md](../conventions/git.md) 直接执行 |

无法判断或跨多类时，向用户确认；跨多类的任务拆成多个工作项并注明依赖。

## 2. 对照项目卡

读 `PROJECT.md`，确认：

- 任务在项目目标与范围内；不在范围内时向用户确认。
- 所需仓库、模型、数据、环境已登记；缺失时先执行 [source-management](shared/source-management.md)、[asset-intake](shared/asset-intake.md)、[env-setup](shared/env-setup.md)。
- 评测套件与验收口径可用；缺失的关键口径（例如关键指标未确定）在开始实现前向用户确认并写入 `PROJECT.md`。

## 3. 对照看板

读 `PLAN.md` 与 `work/README.md`：

- 已有相关工作项：续接，读其状态与交接节。
- 没有：运行 `python3 framework/tools/ws.py new <adapt|opt|fix|res> <name>` 建项。

## 4. 补全任务定义

在 item.md 中写下：

- 目标与验收：默认引用 `PROJECT.md` 和 [defaults.md](../conventions/defaults.md)；需要覆盖时取得用户确认并记录。
- 范围：做什么、明确不做什么。
- 依赖：前置工作项或资产。

## 5. 进入工作流

把状态与阶段设为对应工作流的第一个阶段，同步索引与 PLAN，开始执行。
