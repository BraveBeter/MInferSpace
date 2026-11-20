# {{ID}} {{TITLE}}

> 遵循工作流：[optimize.md](../../framework/workflows/optimize.md)｜门禁：[gates/optimize.md](../../framework/gates/optimize.md)

## 1. 状态与交接

<!-- ws:handoff:begin -->
| 字段 | 内容 |
| --- | --- |
| ID | {{ID}} |
| 类型 | OPT |
| 状态 | planned |
| 阶段 | O0 |
| 决定 | 待定 |
| 依赖 | 无 |
| 起点 commit | {{START_COMMIT}} |
| 实现分支 | 待填写 |
| 最后可信状态 | 尚未验证 |
| 下一步 | 完成 O0 起点固定，并建立或引用可比基线（O1） |
| 阻塞 / 待用户决定 | 无 |
| 更新时间（UTC） | {{UTC}} |
<!-- ws:handoff:end -->

## 2. 目标与验收

- **目标场景与指标**：待填写
- **验收口径**：默认采用 [PROJECT.md](../../PROJECT.md) 与 [defaults.md](../../framework/conventions/defaults.md) 中的 `opt.*`、`acc.*`、`perf.*`
- **工作项级覆盖**（须附用户确认记录）：无

## 3. 范围

- **做什么**：待填写（围绕单一假设）
- **明确不做什么**：待填写

## 4. 起点

- **源码仓库与起点**：待填写（引用 `worktrees/README.md`）
- **候选 worktree**：待填写
- **模型与数据**：待填写（引用 `checkpoints/README.md`、`datasets/README.md`）
- **环境快照**：待填写（引用 `envs/README.md`）
- **基线评测链接**：待填写
- **遵循的仓库规范条目**：待填写（动手改码前列出）

## 5. 瓶颈证据与假设

- **事实（profile 观察）**：待填写（附 `profile-results/` 链接）
- **推断与假设**：如果做 X，指标 M 改善约 Δ，因为 Y；当出现 Z 时假设被推翻。
- **收益上限估算**：瓶颈占比 × 可消除比例 = 待填写

## 6. 方案

- **改动范围**：待填写
- **先例与已知风险**：待填写（对照 `optimize-playbook.md` 与 `knowledge/lessons.md`）
- **回退方式**：待填写

## 7. 实验与验证日志

> 只追加，不改写历史。

| 轮次 | UTC 时间 | 阶段 | 候选 commit | 证据链接 | 性能与正确性摘要 | 下一步 |
| --- | --- | --- | --- | --- | --- | --- |
| 暂无 | — | — | — | — | — | — |

## 8. 门禁记录

> 运行 `python3 framework/tools/ws.py gate {{ID}} --write` 追加记录，并逐条回应 `[evidence]` 与 `[judgement]`。

## 9. 审查记录

> 自审通过后，由独立审查 Agent 按 [review.md](../../framework/templates/review.md) 追加意见，实现者逐条回应。

待执行。

## 10. 结论

- **实测收益与波动**：待填写（附对比报告链接）
- **正确性结果**：待填写（附验证链接）
- **关键场景回退检查**：待填写
- **适用范围与局限**：待填写
- **最终 commit**：待填写
- **决定与执行状态**：待定

## 11. 知识沉淀

- 写入 `knowledge/` 的条目：待填写
- 框架改进提议（如有）：无
