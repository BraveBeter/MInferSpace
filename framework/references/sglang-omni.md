# sglang-omni 开发导航

> 核验状态：通用导航（2026-11-20）。sglang-omni 演进较快，修改代码前**必须**阅读目标仓库起点 commit 下的 `AGENTS.md`、`README.md` 与 `docs/developer_reference/`。

## 1. 与单阶段 LLM 引擎的主要差异

sglang-omni 面向多模态 / 语音 / 全双工等多阶段流水线推理，与纯文本 SGLang 相比需要额外关注：

- **多阶段流水线（Pipeline / Stages）**：通常拆分出前端预处理、多模态编码器、骨干 LM（Talker / Thinker）、声学 / 图像解码器（Codec / Vocoder / DiT）等多个 stage。
- **Stage 间通信与调度**：阶段间可能通过队列、IPC、共享显存或异步流传递 token / hidden states / codes / chunk；吞吐与首包延迟往往受限于 stage 间等待或跨进程拷贝，而不仅是单卡计算。
- **流式协议**：音频或全双工模型通常按 chunk 流式输出（文本片段 + 音频帧/codes），修改调度、批处理或解码路径时须确保流式事件顺序、边界与结束标记兼容。
- **独立权重与精度**：不同 stage 可能使用不同权重文件、精度、batch 策略甚至不同设备分配。

## 2. 适配检查点

1. 先核对 `docs/developer_reference/` 对新增模型、新增 stage、配置结构与接口协议的规定。
2. 在 `design.md` 中画出完整的 **Stage 数据流图**：每个 stage 的输入/输出张量形状、dtype、触发粒度（整句 / 按步 / 按 chunk）、跨 stage 传输方式。
3. 逐 stage 做数值对齐（先对齐各 stage 独立前向，再对齐串联后的端到端输出），不要直接从最终音频反推问题。
4. 明确多模态组合矩阵（纯文本、文本+音频输入、音频输出、流式/非流式等）的首版支持范围。

## 3. 优化关注点

- **端到端时间分解**：先分清时间花在哪个 stage，以及 stage 之间的等待/传输占比，再决定优化单个 stage 还是流水并行。
- **首包延迟（TTFA / First Chunk）**：重点关注首个音频 chunk 所需的预填长度、codec 最小窗口与 stage 启动延迟。
- **Codec / Vocoder 阶段**：小步长、频繁调用常表现为 CPU launch 瓶颈或 CUDA Graph 未覆盖，容易与骨干 LM 争抢 GPU 流或显存。
- **质量守门**：语音/多模态优化后除端到端指标外，需按项目套件同时验证 Codec 重建质量与声学/语义指标（WER、SIM、MOS 等）。
