# 命名约定

所有名称使用小写英文、数字和连字符，工作项 ID 除外。时间统一使用 UTC，格式为 `YYYYMMDDTHHMMSSZ`（例如 `20261120T060000Z`）。名称冲突时追加 `-02`、`-03` 等后缀，不覆盖已有内容。

## 工作项

| 对象 | 格式 | 示例 |
| --- | --- | --- |
| 工作项 ID | `<前缀>-<4位编号>`，前缀见[工作项约定](work-items.md#类型) | `OPT-0003` |
| 工作项目录 | `work/<ID>-<name>/` | `work/OPT-0003-codec-cuda-graph/` |
| 源码分支 | `<类型>/<4位编号>-<name>`，目标仓库另有规则时从其规则 | `opt/0003-codec-cuda-graph` |
| worktree 目录 | `worktrees/<repo>/<小写ID>-<name>/` | `worktrees/sglang-omni/opt-0003-codec-cuda-graph/` |

编号按前缀分别递增，不复用。`OPT-0000` 保留给项目的初始性能基线。

## 证据目录

| 对象 | 格式 | 示例 |
| --- | --- | --- |
| benchmark 运行 | `benchmark-results/<ID>/<UTC>-<suite>-<role>/` | `benchmark-results/OPT-0003/20261120T060000Z-e2e-candidate/` |
| 正确性验证 | `validation-results/<ID>/<UTC>-<check>-<role>/` | `validation-results/ADP-0001/20261120T060000Z-align-candidate/` |
| profile 采集 | `profile-results/<UTC>-<ID>-<tool>-<role>/` | `profile-results/20261120T060000Z-OPT-0003-nsys-baseline/` |

- `suite` 取自 `PROJECT.md` 的评测套件名。
- `check` 取值：`load`（权重加载）、`golden`（参考输出生成）、`align`（数值对齐）、`unittest`（测试运行）、`feature`（特性验证），可在 `PROJECT.md` 中扩展。
- `role` 取值：`baseline`、`candidate`、`reference`（参考实现）、`comparison`（仅含对比报告）。
- `tool` 填实际 profiler，例如 `nsys`、`torch`、`pyspy`、`ncu`。

## 资产与其他

| 对象 | 格式 |
| --- | --- |
| 模型 | `checkpoints/<model>/<revision>/` |
| 数据集 | `datasets/<dataset>/<revision>/` |
| golden 数据 | `datasets/golden-<model>/<准备版本>/` |
| 环境定义 / 快照 / 本地环境 | `envs/specs/<env>/`、`envs/snapshots/<UTC>-<env>/`、`envs/runtime/<env>/` |
| 可复用配置 | `configs/<server\|benchmark\|profile\|validation>/<name>.<ext>` |
| 临时目录 | `tmp/<task>-<UTC>/` |

`<revision>` 使用来源提供的不可变标识（完整 commit、版本号或内容哈希），不使用 `main`、`latest` 等浮动名称。
