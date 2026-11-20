# 阶段门禁

门禁用于确认当前阶段已经具备推进到下一阶段的条件。未满足时记为 `blocked` 并说明原因，不跳过。

## 检查项类型

每条检查项标注三种类型之一：

| 标记 | 含义 | `ws gate` 行为 |
| --- | --- | --- |
| `[auto:<check>]` | 可机械检查的规则 | 自动执行对应检查并输出 PASS / FAIL |
| `[evidence]` | 需要提供证据链接 | 提示 Agent 填写链接；写入 item.md 后由 `ws lint` 校验链接有效 |
| `[judgement]` | 需要 Agent 判断 | 提示 Agent 逐条给出结论与依据 |

`[auto:*]` 失败时，不得在文档中将该阶段标为通过。

## 自动检查项清单

| check | 检查内容 |
| --- | --- |
| `lint` | 工作区 `ws lint` 无错误 |
| `handoff` | item.md 交接节已更新（更新时间与下一步非占位） |
| `start_commit` | item.md 起点 commit 为完整 40 位 SHA |
| `branch` | item.md 实现分支已填写且非占位 |
| `design_exists` | 当前工作项目录存在 `design.md` |
| `benchmark_indexed` | `benchmark-results/<ID>/` 存在含 `execution/` 且已入索引的运行目录（O1 允许引用已有已登记基线；O5 要求 `-candidate`） |
| `profile_indexed` | `profile-results/` 存在关联 `<ID>` 且含 `analysis.md` 与 `execution/` 的目录，且已登记到索引 |
| `validation_indexed` | `validation-results/<ID>/` 存在含 `report.md` 与 `execution/` 的已登记目录，并按阶段匹配类型/角色（A2 golden/reference、A3 load、A4 align、A5 feature、F0 baseline、F3 candidate） |
| `review_recorded` | item.md 审查记录节已记录独立审查意见与处理结果 |
| `decision_recorded` | item.md 决定字段为合法取值且非占位 |

## 门禁文件

- [adapt.md](adapt.md)：模型适配（A0–A7）
- [optimize.md](optimize.md)：性能优化（O0–O6）
- [fix.md](fix.md)：缺陷修复（F0–F4）
- [research.md](research.md)：调研（R0–R2）
- [code-quality.md](code-quality.md)：代码质量通用清单（所有产生代码的工作项交付前必查）
