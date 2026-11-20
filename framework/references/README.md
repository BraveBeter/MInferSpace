# 通用参考知识库

本目录保存跨项目复用的技术导航、排错手册、优化思路与方法学。

> [!WARNING]
> 代码路径和引擎接口会随版本变化。每个条目都标有核验状态；使用前必须在当前工作项起点 commit 的源码中核实。当本知识库与当前源码冲突时，以源码为准，并在复盘中提出更新。

## 索引

| 文件 | 内容 | 核验状态 |
| --- | --- | --- |
| [sglang.md](sglang.md) | SGLang 代码导航、模型生命周期、CUDA Graph 约束与测试组织 | 通用导航（使用前按起点 commit 核实） |
| [sglang-omni.md](sglang-omni.md) | sglang-omni 多阶段流水线、组件接入与流式协议导航 | 通用导航（以仓库 `docs/developer_reference/` 为准） |
| [adapt-handbook.md](adapt-handbook.md) | 常见模型架构变体、权重映射模式与逐层数值对齐排错表 | 方法学手册（2026-11-20 初版） |
| [optimize-playbook.md](optimize-playbook.md) | 性能瓶颈症状 → 优化手段 → 风险 → 验证方式 | 方法学手册（2026-11-20 初版） |
| [profiling.md](profiling.md) | profiler 选型决策树与常用采集/分析方法 | 方法学手册（2026-11-20 初版） |
| [benchmarking.md](benchmarking.md) | 推理指标定义、预热、重复、波动与可比性方法 | 方法学手册（2026-11-20 初版） |
| [pitfalls.md](pitfalls.md) | 跨项目常见陷阱与排查要点 | 持续维护（2026-11-20 初版） |
