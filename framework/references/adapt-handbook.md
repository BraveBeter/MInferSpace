# 模型适配手册

> 核验状态：方法学手册（2026-11-20 初版）。

## 1. 常见架构差异检查表

A1 设计时逐项核对参考实现与最相近 SG 模型的差异：

| 维度 | 常见差异点 |
| --- | --- |
| Attention | MHA / GQA / MQA / MLA；sliding window；logit softcap；attention bias；scaling factor（非 $1/\sqrt{d}$）；QK Norm（位置在 RoPE 前还是后） |
| 位置编码 | RoPE base / theta、partial rotary factor、scaling（linear / dynamic / YaRN / Llama3 / mRoPE）、Neox 与 GPT-J 两种旋转配对顺序 |
| Norm | RMSNorm vs LayerNorm；`eps` 默认值；权重是否加 `+1`（如 Gemma）；Pre-Norm / Post-Norm / 混合 Norm |
| MLP / MoE | 激活函数（SiLU / GELU / approximate tanh）；gate+up 顺序；MoE router softmax 位置（top-k 前或后）、权重归一化、shared experts、router bias |
| Embedding | `tie_word_embeddings`；embedding scaling；词表 padding 与实际 `vocab_size` |
| 多模态与语音 | 采样率、mel 特征参数、音频 frame rate、special token 占位替换位置、codec codebook 数量与延迟模式（delay pattern） |
| Tokenizer / 模板 | BOS/EOS 是否自动添加、chat template 空白与换行、`stop_token_ids` |

## 2. 权重映射常见模式

- **合并参数（Stacked Params）**：参考实现分开存 `q_proj` / `k_proj` / `v_proj` 或 `gate_proj` / `up_proj`，SG 中合并为 `qkv_proj` / `gate_up_proj`。使用 SG 标准的 `stacked_params_mapping` 与参数 `weight_loader(param, loaded_weight, shard_id)`。
- **MoE 专家参数**：注意参考实现是按 expert 分开还是 3D 张量堆叠，以及 gate/up 顺序。
- **忽略与共享参数**：`rotary_emb.inv_freq`（若动态计算）、tied `lm_head.weight` 等在加载报告中须明确列出并解释，绝不静默丢弃未知键。
- **非标准名称前缀**：多模态模型常见 `language_model.`、`model.`、`audio_tower.` 等前缀，加载时统一剥离或按子模块转发。

## 3. 对齐排错

A4 阶段出现数值超差时，**按以下顺序**从输入到输出逐层排除，不要跳过前面的步骤：

| 顺序 | 检查点 | 常见根因 |
| --- | --- | --- |
| 1 | 输入 token ID 与多模态特征 | tokenizer 配置、BOS/EOS 重复或缺失、chat template 差异、音频重采样或归一化算法不同 |
| 2 | Config 与 dtype | 某个字段未从 `config.json` 读入而是用了默认值（如 `rms_norm_eps`、`rope_theta`）；参考与候选 dtype 不一致（FP32 vs BF16） |
| 3 | Embedding 输出 | 词表大小/padding、embedding scaling、多模态占位替换索引偏移 |
| 4 | 第 0 层 Norm 后 | Norm 实现差异（`eps`、FP32 归约、权重 `+1` 偏移） |
| 5 | 第 0 层 QKV 投影与 RoPE | QKV 合并顺序错位、bias 漏加载、RoPE 旋转配对方式（interleaved vs half-split）错误、QK Norm 与 RoPE 顺序反了、position_ids 偏移 |
| 6 | 第 0 层 Attention 输出 | scaling factor、causal/sliding mask、attention backend 数值差异（先切到最简参考 attention 排查） |
| 7 | 第 0 层 MLP / MoE 输出 | gate/up 顺序颠倒、GELU 近似模式不同、MoE top-k 归一化或路由顺序错误 |
| 8 | 末层与 lm_head | 末层 norm 漏加、tie embedding 未正确绑定、logit softcap |
| 9 | Prefill 对齐但 Decode 漂移 | KV Cache 写入/读取位置错位、Decode 的 `position_ids` 步进错误、sliding window cache 截断 |
| 10 | 最简配置对齐但开特性后漂移 | CUDA Graph 捕获了陈旧状态或动态值；前缀缓存哈希未包含多模态信息；TP 通信归约遗漏或重复加 bias |
