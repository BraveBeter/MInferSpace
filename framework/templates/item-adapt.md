# {{ID}} {{TITLE}}

> 遵循工作流：[adapt.md](../../framework/workflows/adapt.md)｜门禁：[gates/adapt.md](../../framework/gates/adapt.md)

## 1. 状态与交接

<!-- ws:handoff:begin -->
| 字段 | 内容 |
| --- | --- |
| ID | {{ID}} |
| 类型 | ADAPT |
| 状态 | planned |
| 阶段 | A0 |
| 决定 | 待定 |
| 依赖 | 无 |
| 起点 commit | {{START_COMMIT}} |
| 实现分支 | 待填写 |
| 最后可信状态 | 尚未验证 |
| 下一步 | 完成 A0 接入：登记权重与参考实现源码，完善 knowledge/model.md |
| 阻塞 / 待用户决定 | 无 |
| 更新时间（UTC） | {{UTC}} |
<!-- ws:handoff:end -->

## 2. 目标与验收

- **目标**：待填写（适配的模型或能力、目标场景）
- **验收口径**：默认采用 [PROJECT.md](../../PROJECT.md) 与 [defaults.md](../../framework/conventions/defaults.md) 中的 `corr.*`、`acc.*`
- **工作项级覆盖**（须附用户确认记录）：无

## 3. 范围

- **做什么**：待填写
- **明确不做什么**：待填写

## 4. 起点

- **目标引擎仓库**：待填写（引用 `worktrees/README.md`）
- **参考实现仓库**：待填写（完整 commit）
- **模型权重**：待填写（引用 `checkpoints/README.md`）
- **评测与 golden 数据**：待填写（引用 `datasets/README.md`）
- **环境快照**：待填写（引用 `envs/README.md`）
- **遵循的仓库规范条目**：待填写（动手改码前列出）

## 5. 分析与设计

详细架构映射、权重映射与特性矩阵见 `design.md`（A1 阶段创建，模板见 [design-adapt.md](../../framework/templates/design-adapt.md)）。

- **事实**：待填写
- **推断与风险**：待填写

## 6. 方案

- **改动范围**：待填写
- **回退方式**：待填写

## 7. 实验与验证日志

> 只追加，不改写历史。每轮记录候选 commit、验证或评测目录链接、关键结果与下一步。

| 轮次 | UTC 时间 | 阶段 | 候选 commit | 证据链接 | 结果摘要 | 下一步 |
| --- | --- | --- | --- | --- | --- | --- |
| 暂无 | — | — | — | — | — | — |

## 8. 门禁记录

> 运行 `python3 framework/tools/ws.py gate {{ID}} --write` 追加记录，并逐条回应 `[evidence]` 与 `[judgement]`。

## 9. 审查记录

> 自审通过后，由独立审查 Agent 按 [review.md](../../framework/templates/review.md) 追加意见，实现者逐条回应。

待执行。

## 10. 结论

- **正确性与精度结果**：待填写（附证据链接）
- **性能基线**：待填写（附证据链接）
- **已支持特性与限制**：待填写
- **最终 commit**：待填写
- **决定与执行状态**：待定

## 11. 知识沉淀

- 写入 `knowledge/` 的条目：待填写
- 框架改进提议（如有）：无
