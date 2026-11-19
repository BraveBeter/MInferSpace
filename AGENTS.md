# SG 工作区约定

本工作区管理 SGLang 和 SGLang Omni 的模型适配、优化及验证证据。项目的源码、模型和验证入口见 [PROJECT.md](PROJECT.md)。

- 模型接入和能力扩展使用 [sg-model-adaptation](.agents/skills/sg-model-adaptation/SKILL.md)。已有路径的性能改进使用 [sg-model-optimization](.agents/skills/sg-model-optimization/SKILL.md)。
- 修改目标源码前阅读该 checkout 的 `AGENTS.md`、`README.md` 和适用的开发文档。源码保留独立 Git 历史，工作副本遵循 [worktrees/README.md](worktrees/README.md)。
- 任务、待办索引和收尾记录遵循 [tasks/README.md](tasks/README.md)。各目录的 README 维护本目录的存放和登记约定，入口见 [仓库 README](README.md)。
- 文档区分事实、假设、计划和结论。使用相对链接，移动文件时同步引用。凭据留在外部环境，报告中只记录所用变量名。
- 交付前运行 [工作区检查](scripts/README.md#工作区检查)，报告实际改动、验证结果和仍待完成的事项。
