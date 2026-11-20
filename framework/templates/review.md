# 独立审查记录（模板）

> 遵循 [workflows/shared/code-review.md](../../framework/workflows/shared/code-review.md) 与 [gates/code-quality.md](../../framework/gates/code-quality.md)。将以下内容追加到 `item.md` 的“审查记录”节。

### 审查轮次 #1（UTC 时间：YYYYMMDDTHHMMSSZ）

- **审查对象**：工作项 `<ID>`｜diff `<起点commit>..<候选commit>`｜证据目录列表
- **审查结论**：`APPROVE` / `CHANGES_REQUESTED` / `COMMENT`

#### 意见清单

| 编号 | 级别（blocker / major / minor / nit） | 位置（文件与行号或文档节） | 问题描述与依据 | 实现者回应（commit / 理由） |
| --- | --- | --- | --- | --- |
| R1 | — | — | — | — |

#### 代码质量门禁复核

- 仓库规范：通过 / 不通过（说明）
- 最小改动：通过 / 不通过（说明）
- 复用与边界：通过 / 不通过（说明）
- 测试与静态检查：通过 / 不通过（说明）
- 结论与证据一致性：通过 / 不通过（说明）
