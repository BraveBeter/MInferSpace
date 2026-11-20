# SGLang 开发导航

> 核验状态：通用导航（2026-11-20）。动手改源码前，须在当前起点 commit 核对实际目录与符号名，并先读目标仓库的 `AGENTS.md` / `CONTRIBUTING`。

## 1. 读代码的起点

适配或优化前，先在起点 commit 定位以下入口：

| 关注点 | 查什么 | 常见路径提示（以当前源码为准） |
| --- | --- | --- |
| 模型定义与注册 | `EntryClass` 导出与自动注册表 | `python/sglang/srt/models/`、`registry.py` |
| 基础层组件 | 并行线性层（QKV/Merged/Row/Column）、RMSNorm、RoPE、激活、MoE | `python/sglang/srt/layers/` |
| Attention Backend | `RadixAttention` 与不同 backend（FlashInfer、FA3、Triton 等）的适配要求 | `python/sglang/srt/layers/attention/`、`mem_cache/` |
| 权重加载 | `load_weights`、stacked params 映射、量化权重加载器 | 参照最相近的已支持模型 + `model_loader/` |
| 调度与前向 | `ForwardBatch`、prefill / decode / extend 路径、chunked prefill | `python/sglang/srt/managers/`、`model_executor/` |
| CUDA Graph | capture 与 replay 路径、静态 buffer 分配、padding 规则 | `model_executor/cuda_graph_runner.py` |
| 多模态 | image/audio processor、multimodal inputs、embedding 替换逻辑 | `multimodal/`、`layers/multimodal/` |
| 测试组织 | 与 HF 输出对比的模型测试、serving 集成测试 | `test/srt/` |

## 2. 模型前向生命周期

在 A1 设计和 A4 对齐时，按以下链路核对输入和中间态：

1. **输入与预处理**：tokenize → chat template → 特殊 token → 多模态特征提取与长度对齐。
2. **权重加载**：checkpoint 读取 → 参数名映射与合并/拆分（如 QKV、gate+up）→ 量化配置绑定 → tie word embeddings 处理。
3. **Embedding**：文本与多模态 embedding 拼接/替换；检查位置编码（含 mRoPE 等多维位置）。
4. **Transformer Blocks**：Attention（QKV 投影、QK norm、RoPE、KV cache 写入与读出、sliding window 或局部 mask）→ 残差与 Norm → MLP / MoE。
5. **输出头**：末层 Norm → `lm_head`（与 `logits_processor` 配合，只计算需要的位置）→ 采样。

## 3. CUDA Graph 对模型代码的约束

开启 CUDA Graph（A5 或 OPT）时，capture 路径中的模型前向必须满足：

- **禁止 host-device 同步**：不能在 `forward` 中调用 `.item()`、`.cpu()`、`.tolist()`、`torch.cuda.synchronize()` 或依赖张量值的 Python 分支。
- **静态地址与固定形状**：输入/输出 buffer 地址在 capture 后固定；动态形状的控制信息需通过预分配张量（如 `ForwardBatch` 中的元数据）传递。
- **不在前向中动态分配依赖运行时值的分支逻辑**：多模态或变长分支如不兼容 graph，应显式拆到 graph 之外（如 encoder 独立执行）或声明不支持。
- **与 RadixAttention / KV Cache 交互**：确保 cache 索引与 batch 元数据完全遵循 `ForwardBatch` 约定。

## 4. 并行与量化检查点

- **TP**：确认各线性层选择正确的并行类型（Column / Row / QKVParallel / MergedColumn），确认 head 数与 kv head 数能被 TP 整除或按仓库约定处理复制，确认输出 gather / reduce 语义。
- **量化**：权重加载必须走 `quant_config` 与层自带的 `weight_loader`，不手写绕过量化加载器的直接 `copy_`。
