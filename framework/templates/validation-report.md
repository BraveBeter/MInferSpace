# 正确性验证报告（模板）

> 验证目录：`validation-results/<ID>/<run-id>/`｜关联工作项：`<ID>`｜流程见 [workflows/shared/correctness.md](../../../framework/workflows/shared/correctness.md)

## 1. 验证条件

- **验证类型**：`load` / `golden` / `align` / `feature` / `unittest`
- **被测代码**：仓库、分支、完整 commit、配置（详见 `execution/`）
- **参照对象**：golden 版本或参考实现 commit、环境快照
- **适用口径**：引用 `defaults.md` 与 `PROJECT.md` 中的具体键与数值
- **非确定性说明**：dtype、设备、seed、已知非确定性来源

## 2. 结果明细

| 检查项 / 层 / 特性 | 实测值 | 口径要求 | 结果（PASS / FAIL） | 备注 |
| --- | --- | --- | --- | --- |
| 待填写 | — | — | — | — |

## 3. 结论与未解释差异

- **总体结论**：PASS / FAIL / 条件通过（写明条件）
- **未解释差异**：无（或逐条列出并说明下一步）
