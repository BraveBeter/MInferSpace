# 工作流：缺陷修复（FIX）

定位并修复一个正确性问题，交付带回归测试的最小修复。

| 阶段 | 状态 | 动作 | 产出 |
| --- | --- | --- | --- |
| F0 复现 | `analyzing` | 固定起点 commit、环境、输入，写出最小复现步骤；无法复现时记录尝试过的条件并向用户确认 | item.md 复现节；`validation-results/<ID>/<UTC>-<check>-baseline/` |
| F1 定位 | `analyzing` | 与参考实现或正确版本对比，必要时逐层对齐（[correctness.md](shared/correctness.md)）；写出根因，区分事实与推断 | item.md 分析节 |
| F2 修复 | `implementing` | 从起点 commit 开 worktree 与分支，最小改动修复根因（不只掩盖症状），补充能复现该问题的回归测试 | 候选 commit |
| F3 验证 | `validating` | 复现用例通过；相关对齐或精度不回退；必要时确认性能无明显回退 | `validation-results/<ID>/<UTC>-<check>-candidate/` |
| F4 交付 | `deciding` | 独立审查、决定与交付、复盘 | item.md 结论 |

门禁见 [gates/fix.md](../gates/fix.md)。代码要求同 [adapt.md](adapt.md#适配的代码质量要求)，必读材料按需引用 [references/adapt-handbook.md](../references/adapt-handbook.md#3-对齐排错)。
