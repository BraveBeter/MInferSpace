---
name: sg-model-adaptation
description: Add model support or extend an existing model's supported interfaces, modalities, or execution paths in SGLang or SGLang Omni. Use for model integration and compatibility work.
---

# SG 模型适配

1. **确定入口与承诺。** 读 [PROJECT.md](../../../PROJECT.md)、[任务约定](../../../tasks/README.md) 和目标 checkout 的开发说明。固定目标提交、模型版本和参考实现，建立 `ADP` 任务。列清本次要支持的接口、输入输出形态和部署条件，把范围外能力留作后续工作。
2. **定位最相近的实现。** 从目标版本中找最接近的模型或流水线，逐项定位与本次接入有关的差异，例如注册与配置、权重加载、输入处理、执行路径、输出协议。优先复用同版本的既有扩展点和测试。
3. **先定义正确性证据。** 确定参考输出、最小请求和比较方法。按项目实际选择精确匹配、数值容差或任务指标，记录样本和适用覆盖。选好目标服务入口以及受改动影响的回归用例。
4. **实现并验证。** 从固定起点建立工作副本，保持改动范围最小。确认运行时加载目标 checkout 和模型版本，执行正常入口的 smoke、输出对齐与相关回归。必要时采集 profile 定位问题；遇到缺失条件时先完成可执行检查，并记录受阻部分。
5. **按证据交付。** 记录受测提交、通过的能力范围、失败或未覆盖的场景及复现命令。执行[共享收尾检查](../../../tasks/README.md#收尾检查)，包括项目声明的适用检查。

## 按需参考

优先看目标 checkout 对应版本的文档和代码。定位模型注册与接入时查 [SGLang 新模型接入指南](https://github.com/sgl-project/sglang/blob/main/docs/docs/supported-models/support_new_models.mdx)。涉及 Omni 执行与流水线时查 [Omni 开发者参考](https://github.com/sgl-project/sglang-omni/blob/main/docs/developer_reference/main.md)。做架构差异分析或设计验证矩阵时可参考[社区 Day-0 接入 Skill](https://github.com/BBuf/AI-Infra-Auto-Driven-SKILLS/blob/main/skills/model-optimization/sglang-model-day0-support/SKILL.md)。
