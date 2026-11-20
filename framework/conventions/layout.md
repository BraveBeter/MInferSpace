# 目录布局

实例工作区的标准布局如下。目录按实际需要创建；每个目录的 README 只写用途、项目细则和登记表，通用规则以本文件及 shared 子流程为准。

```text
<workspace>/
├── AGENTS.md              # 唯一入口，路由到 PROJECT.md、PLAN.md 与 framework
├── PROJECT.md             # 项目卡
├── PLAN.md                # 活动工作项看板（仅一张表）
├── framework/             # 框架层（git subtree，任务中只读）
├── work/                  # 工作项
├── knowledge/             # 项目知识：模型、引擎、lessons
├── worktrees/             # 源码仓库与工作副本（内容不进入工作区 Git）
├── envs/                  # 环境定义、快照、本地环境
├── checkpoints/           # 模型权重与配套资产
├── datasets/              # 评测数据、golden 数据
├── configs/               # 可复用的服务、评测、profile、验证配置
├── scripts/               # 项目辅助脚本
├── benchmark-results/     # 证据：统一评测
├── profile-results/       # 证据：profile 采集
├── validation-results/    # 证据：加载、对齐、golden、测试、特性验证
└── tmp/                   # 可丢弃的中间文件
```

## 目录职责

| 目录 | 职责 | 通用规则 |
| --- | --- | --- |
| `work/` | 工作项文档、设计文档 | [work-items.md](work-items.md) |
| `knowledge/` | 项目级参考与经验；通用部分经复盘晋升到框架 | [retro.md](../workflows/shared/retro.md) |
| `worktrees/` | 每个仓库一个目录：主 clone + 各工作项 worktree | [source-management.md](../workflows/shared/source-management.md) |
| `envs/` | `specs/`（如何重建）、`snapshots/`（实际用了什么）、`runtime/`（本地环境，不跟踪） | [env-setup.md](../workflows/shared/env-setup.md) |
| `checkpoints/`、`datasets/` | 按“名称 → 固定版本”保存原始布局；转换产物单独登记 | [asset-intake.md](../workflows/shared/asset-intake.md) |
| `configs/` | 见下文 | 本文件 |
| `scripts/` | 见下文 | 本文件 |
| `benchmark-results/` | 按“工作项 → 运行”分组 | [benchmark.md](../workflows/shared/benchmark.md)、[evidence.md](evidence.md) |
| `profile-results/` | 每次采集一个目录 | [profile.md](../workflows/shared/profile.md)、[evidence.md](evidence.md) |
| `validation-results/` | 按“工作项 → 验证运行”分组 | [correctness.md](../workflows/shared/correctness.md)、[evidence.md](evidence.md) |
| `tmp/` | 见下文 | 本文件 |

## configs/

- 保存可复用的配置，按 `server/`、`benchmark/`、`profile/`、`validation/` 分子目录；使用对应工具的原生格式。
- 每次运行实际使用的配置与命令副本保存在对应证据目录的 `execution/` 中；可复用配置本身不代表某次运行。
- 相对路径按各工具的规则解析；复用示例配置时核对其指向实际版本的数据、模型、源码和环境。
- 凭据通过外部环境提供，配置和留档只记录变量名。
- 实际存在的配置登记在 `configs/README.md`，写明用途、使用工具和调用方式。

## scripts/

- 存放项目需要的辅助脚本，用于串联已有工具、减少重复或易错操作；出现明确需求后再编写，不预设。
- 通用能力优先放进框架工具（经框架改进流程），项目特有的放在 `scripts/`。
- 评测使用项目评测客户端的原有入口，脚本只负责调用与串联，不重新实现指标。
- 脚本显式接收源码路径、环境、配置和输出位置，适用于不同基线、候选与条件。
- 登记在 `scripts/README.md`：名称（链接）、用途、调用示例（含执行目录与解释器）、必要输入、输出位置。

## tmp/

- 仅存放可重新生成或可丢弃的内容，按 `<task>-<UTC>/` 建子目录。
- 复现所需的模型、数据、配置、命令、日志或证据，及时移入正式目录并更新引用。
- 任务完成后可清理对应子目录；保留 `tmp/README.md`。

## 版本跟踪

工作区 `.gitignore` 遵循以下原则，具体规则见实例 `.gitignore`：

- 不跟踪：源码 worktree 内容、外部客户端仓库、本地环境、缓存、模型权重和大型二进制、原始音频与张量、profiler 原生产物、指定位置的运行日志、`tmp/` 内容。
- 跟踪：所有 README 与文档、环境定义与快照、配置、脚本、清单与校验值、证据目录中的执行材料、摘要、分析和对比报告。
