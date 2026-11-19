# opt-loop

用于优化 moss-speech on sglang-omni，保存源码检出、性能证据、评测结果和策略记录的约定。

## 开始工作

1. 阅读 [工作区执行约定](AGENTS.md) 和 [当前策略计划](PLAN.md)。
2. 按 [依赖初始化步骤](worktrees/README.md#初始化依赖) 检出固定版本的源码和评测客户端，并验证 CLI。
3. 准备并登记 [环境](envs/README.md)、[模型](checkpoints/README.md)、[评测数据](datasets/README.md) 和 [运行配置](configs/README.md)。
4. 使用 [moss-speech-opt-loop Skill](.agents/skills/moss-speech-opt-loop/SKILL.md) 开展性能探索和优化。相关产物的格式见 [profile](profile-results/README.md)、[策略](strategies/README.md) 和 [benchmark](benchmark-results/README.md) 约定。
