---
name: sg-model-optimization
description: Diagnose and improve performance of an existing SGLang or SGLang Omni model path using a reproducible baseline, profiling, and controlled benchmarks.
---

# SG 模型优化

1. **固定起点和目标。** 读 [PROJECT.md](../../../PROJECT.md)、[任务约定](../../../tasks/README.md) 和目标 checkout 的开发说明。建立 `OPT` 任务，记录待改善场景、源码与资产版本。复用条件一致的已验收基线；缺少可比证据时先测基线，并记录测量波动。
2. **定位瓶颈并冻结验收。** 优先检查目标场景的 [profile 证据](../../../profile-results/README.md)，必要时采集，区分观测和假设。选定一个可验证的假设，记录改动范围、可比条件、性能目标与允许的正确性和质量变化。
3. **独立实现与回归。** 从固定起点创建工作副本，核对实际解释器、导入路径、源码状态、配置和设备。在保持公开行为和输出协议的前提下做最小改动，先跑相关正确性和质量检查。
4. **对照测量。** 用同一评测入口和冻结的输入、生成参数及环境比较基线和候选。评估收益、重复轮次的波动、质量覆盖和执行失败。利用 [benchmark 记录](../../../benchmark-results/README.md) 支撑结论。条件不一致时保存差异并尝试补测；受阻时如实记录可判断的范围和缺失条件。
5. **决定去向。** 按验证结果记录保留候选、放弃候选或推进基线。推进基线须能再次取回受测提交，并以实际评测和质量结果为依据。执行[共享收尾检查](../../../tasks/README.md#收尾检查)，包括项目声明的适用检查。

## 按需参考

使用所选 checkout 的开发文档和工具。构建基准和区分负载时查 [SGLang Benchmark and Profiling 指南](https://github.com/sgl-project/sglang/blob/main/docs/docs/developer_guide/benchmark_and_profiling.mdx)。分析 Omni 的分阶段瓶颈时查 [Omni Profiling Skill](https://github.com/sgl-project/sglang-omni/blob/main/.claude/skills/model-profiling/SKILL.md)。设计对照顺序、估计噪声时可参考[社区优化循环 Skill](https://github.com/sybil-solutions/inference-optimisation-skill/blob/main/skills/inference-optimisation/SKILL.md)。
