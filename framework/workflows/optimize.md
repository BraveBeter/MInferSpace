# 工作流：性能优化（OPT）

以可证伪的假设驱动优化，用统一 benchmark 证明收益、用正确性验证证明不回退。

```mermaid
flowchart LR
    O0["O0 起点"] --> O1["O1 基线"] --> O2["O2 Profile"] --> O3["O3 假设与方案"]
    O3 --> O4["O4 实现"] --> O5["O5 验证"] --> O6["O6 决定"]
    O5 -.未达标.-> O4
    O5 -.假设被推翻.-> O2
```

| 阶段 | 状态 |
| --- | --- |
| O0–O3 | `analyzing` |
| O4 | `implementing` |
| O5 | `validating` |
| O6 | `deciding` |

每个阶段结束运行 `ws gate <ID> --write`，门禁内容见 [gates/optimize.md](../gates/optimize.md)。`OPT-0000`（初始基线）只执行 O0、O1 和 O6。

---

## O0 起点

**动作**：固定源码仓库与完整 commit、环境快照、模型与数据版本、硬件，写入 item.md 起点节。

**本阶段必读**：[source-management.md](shared/source-management.md)、[env-setup.md](shared/env-setup.md)。

## O1 基线

**动作**

- 已有可比基线（同 commit、环境、资产、硬件、客户端版本）时直接引用其运行目录，无需复制。
- 否则用项目评测套件跑基线，按 `perf.repeats_min` 重复，检查 `perf.cv_max`。

**产出**：基线运行目录或引用链接。

**本阶段必读**：[benchmark.md](shared/benchmark.md)、[references/benchmarking.md](../references/benchmarking.md)。

## O2 Profile

**动作**

- 按 [references/profiling.md](../references/profiling.md) 选工具：先端到端时间线（CPU/GPU 占比、空泡、阶段间等待），再按需下钻到 kernel。
- 在 `analysis.md` 中写明负载、关键时间区间、瓶颈观察，区分事实与推断。

**产出**：`profile-results/<UTC>-<ID>-<tool>-baseline/`。

**本阶段必读**：[profile.md](shared/profile.md)。

## O3 假设与方案

**动作**

- 写成“如果做 X，指标 M 改善约 Δ，因为 Y”，并说明什么结果会推翻假设。
- 用 Amdahl 定律或 roofline 估算收益上限：瓶颈占比 × 可消除比例。上限低于 `perf.estimate_confirm_below` 时先与用户确认。
- 对照 [references/optimize-playbook.md](../references/optimize-playbook.md) 与 `knowledge/lessons.md` 查找先例和已知风险。
- 写明改动范围、风险、回退方式和量化验收标准。

**产出**：item.md 分析与方案节。

## O4 实现

**动作**

- 从起点 commit 创建 worktree 与分支，只实现当前假设所需的最小改动，小步提交。
- 运行目标仓库的 lint 与相关单元测试。

**本阶段必读**：目标仓库规范、[git.md](../conventions/git.md)、[gates/code-quality.md](../gates/code-quality.md)。

## O5 验证

**动作**

- 正确性：按 `opt.*` 与 `acc.*` 口径验证不回退（固定选样、同条件）。
- 性能：同条件运行候选，复用基线选样，生成对比报告；收益须满足 `perf.gain_min`。
- 检查 `PROJECT.md` 中的关键场景，回退不超过 `perf.regression_max`。
- 必要时用 profile 确认优化机制确实生效（单独运行，不与正式 benchmark 混合）。
- 未达标回到 O4；假设被推翻回到 O2，并在日志中记录证据。

**产出**：候选运行目录、对比报告、正确性证据。

## O6 决定

**动作**

- 自审后启动独立审查（[code-review.md](shared/code-review.md)），同时审查代码与结论。
- 记录决定 `push`、`keep-local` 或 `discard` 及理由；远端操作等待用户授权（[delivery.md](shared/delivery.md)）。
- 复盘（[retro.md](shared/retro.md)），更新 lessons；被推翻的假设同样结项，标记 `discard` 并写明证据。

## 额外规则

- 一个工作项只验证一个假设；组合多个优化时，先分别验证，再另开组合工作项。
- profile 与正式 benchmark 分开运行。
- 收益低于噪声或只在单一场景有效时，如实写明适用范围，不夸大结论。
- 基线代码推进（例如上游更新）后，旧对比仍按其各自起点解读；需要在新起点上的结论时重新测量。
