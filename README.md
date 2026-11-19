# MInferSpace

用于管理 SGLang 与 SGLang Omni 模型适配和优化的工作区。填写 [PROJECT.md](PROJECT.md) 后，描述当前任务即可从对应的仓库级 Skill 开始。

- 让目标仓库支持模型或扩展接口能力，使用 [sg-model-adaptation](.agents/skills/sg-model-adaptation/SKILL.md)。
- 改进已经可用的推理路径，使用 [sg-model-optimization](.agents/skills/sg-model-optimization/SKILL.md)。

[AGENTS.md](AGENTS.md) 维护通用约定。[PLAN.md](PLAN.md) 索引待结案任务，长期记录保存在 [tasks/](tasks/README.md)。

| 目录 | 职责 |
| --- | --- |
| [worktrees/](worktrees/README.md) | 源码 checkout、基线和任务工作副本 |
| [envs/](envs/README.md) · [checkpoints/](checkpoints/README.md) · [datasets/](datasets/README.md) · [configs/](configs/README.md) | 环境定义与快照、固定版本权重与数据、可复用配置 |
| [profile-results/](profile-results/README.md) · [benchmark-results/](benchmark-results/README.md) | 性能定位、验证和比较证据 |
| [scripts/](scripts/README.md) · [tmp/](tmp/README.md) | 工作区检查及辅助脚本、可丢弃中间文件 |
