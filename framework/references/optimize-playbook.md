# 性能优化手册

> 核验状态：方法学手册（2026-11-20 初版）。O3 提出假设时按瓶颈类型查阅；具体手段须先在当前起点 commit 核实引擎是否已支持。

## 瓶颈症状 → 优化手段

| 瓶颈症状（O2 Profile 观察） | 常见手段 | 适用条件 | 主要风险 | 如何验证机制生效 |
| --- | --- | --- | --- | --- |
| **GPU 空泡多、大量短 kernel、CPU 侧 Python/launch 耗时高** | 开启或扩展 CUDA Graph 覆盖；减少前向中的 host-device 同步（`.item()` / `.cpu()`）；算子融合（RMSNorm+残差、RoPE、激活） | Decode、小 batch、Codec 逐帧解码 | 静态形状限制；多模态/变长路径兼容性；隐蔽数值差异 | 对比 nsys 中 GPU 利用率与 kernel 间隙 |
| **CPU 调度成为瓶颈（batch 组装、tokenize、后处理阻塞 GPU）** | Overlap 调度；异步准备下一个 batch；将热路径 Python 循环改为向量化或 C++/Triton | 高并发、短请求、流式小 chunk | 异步状态竞态、取消/异常路径出错 | py-spy / nsys 中 CPU 线程与 GPU 流的重叠度 |
| **Decode 显存带宽受限（低算术强度，权重读取主导）** | 权重量化（FP8 / INT4 / AWQ）；KV Cache 量化；提高有效并发/batch；投机解码（如适用） | 带宽利用率接近硬件上限、batch 较小 | 精度下降，须严守 `acc.*`；量化 kernel 在特定硬件上可能反而变慢 | ncu 带宽利用率、tokens/s 与精度对比 |
| **Prefill 计算或 Attention 受限** | 切换更优 attention backend（FA3 / FlashInfer）；开启前缀缓存（Radix Cache）；chunked prefill 平衡延迟与吞吐 | 长上下文、重复前缀、混合负载 | 首字延迟与吞吐权衡；多模态前缀缓存需确认哈希正确 | 分场景对比 TTFT 与 ITL |
| **多阶段流水线（omni）Stage 间等待或拷贝耗时高** | Stage 间流水并行/重叠；减少 GPU↔CPU 往返拷贝；共享显存/零拷贝传递；调整 chunk 触发粒度 | nsys 显示一个 stage 工作时另一 stage 长时间空闲 | 显存峰值上升、流式顺序与背压问题 | 端到端 timeline 中各 stage 重叠比例与首包延迟 |
| **多卡通信占比高** | 通信-计算重叠；评估并行切分策略（TP vs DP vs 分 stage 放置）；检查 NCCL 拓扑与通信后端 | 跨卡 all-reduce / all-gather 占比显著 | 负载不均、实现复杂度高 | nsys 中 NCCL kernel 占比与并发吞吐 |
| **显存受限导致并发上不去** | 消除前向临时大张量、复用预分配 buffer、优化 KV Cache 配额与碎片、权重量化 | 显存接近 OOM 或 KV Cache 命中/并发受限 | buffer 复用引入数据覆盖 bug | 峰值显存与最大稳定并发对比 |

## 选型原则

1. **先算上限再动手**：用 Amdahl 定律估算最大收益（瓶颈耗时占比 × 预期消除比例）；上限小于 `perf.estimate_confirm_below` 时先和用户确认。
2. **先配置与复用，后改代码，最后写自定义 kernel**：能通过正确启用引擎已有能力（CUDA Graph、backend、overlap、cache）解决的，不另造轮子。
3. **单一变量**：一次只验证一个假设，避免把两个改动混在一起分不清收益来源。
