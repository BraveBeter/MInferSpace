# opt-loop

用于优化 moss-speech on sglang-omni。每项优化从固定源码起点出发，先用 profile 定位瓶颈，再在独立 Git worktree 实现，最后用统一 benchmark 验收并归档结论。

## 开始工作

1. 阅读 [工作区执行约定](AGENTS.md) 和 [当前策略计划](PLAN.md)。
2. 按 [依赖初始化步骤](worktrees/README.md#初始化依赖) 检出固定版本的源码和评测客户端，并验证 CLI。
3. 准备并登记 [环境](envs/README.md)、[模型](checkpoints/README.md)、[评测数据](datasets/README.md) 和 [运行配置](configs/README.md)。
4. 按 [策略约定](strategies/README.md) 建立 `OPT-0000` 初始基线，按 [profile](profile-results/README.md) 和 [benchmark](benchmark-results/README.md) 约定归档运行证据。
