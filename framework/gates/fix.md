# 门禁：缺陷修复（FIX）

配合 [workflows/fix.md](../workflows/fix.md) 使用。

## F0 复现

- [auto:start_commit] 起点 commit 为完整 40 位 SHA
- [auto:validation_indexed] 复现记录已保存在 `validation-results/<ID>/` 并入索引
- [judgement] 复现步骤、输入、环境与现象清晰，可稳定触发

## F1 定位

- [evidence] 对比或对齐证据链接已写入 item.md
- [judgement] 根因定位明确，区分事实与推断，排除表层猜测

## F2 修复

- [auto:branch] 从起点 commit 创建的分支与 worktree 已登记
- [evidence] 候选 commit 包含能复现原问题的回归测试
- [judgement] 修改直击根因且范围最小，无调试残留

## F3 验证

- [auto:validation_indexed] 候选验证记录已留档并入索引
- [evidence] 复现用例与回归测试均通过
- [judgement] 相关对齐、精度与性能无明显回退（说明检查范围）

## F4 交付

- [auto:review_recorded] 已完成独立审查并记录处理结果
- [auto:decision_recorded] 已记录决定与执行状态
- [auto:handoff] 交接节已更新
- [auto:lint] `ws lint` 无错误
- [judgement] [code-quality.md](code-quality.md) 全部满足；复盘已完成
