# 评测与验证数据

通用规则见 [asset-intake.md](../framework/workflows/shared/asset-intake.md#数据datasets)。本表路径相对 `datasets/`。

## 本项目数据集细则

### OpenAudioBench（E2E）

包含 LLaMA Questions、TriviaQA、WebQuestions。使用客户端支持的原始 CSV 与对应音频，E2E 配置中的 `source` 指向 CSV，`audio_root` 指向相应音频目录，并提供固定 `revision`（配置示例见 `benchmark-client/examples/e2e.json`）。每次运行由客户端生成 `selection.json` 保存在运行目录中，候选评测可通过 `--selection` 复用。

### Seed-TTS-Eval（Codec）

保存完整 EN1088、ZH2020 数据（共 3108 对 target/prompt）以及客户端要求的 `corpus.jsonl`。每条清单记录样本 ID、语言、文本、target/prompt 音频路径（相对 `corpus.jsonl` 所在目录）及对应 SHA-256。Codec 配置引用该清单并记录固定 revision 与整个 JSONL 的 SHA-256（协议见 `benchmark-client/CODEC_ONLY.md` 与 `benchmark-client/examples/codec.json`）。

## 已登记数据集

<!-- ws:datasets:begin -->
| 数据集 | 用途 | 来源 | 固定版本 | 本地目录 | 准备状态 |
| --- | --- | --- | --- | --- | --- |
| 暂无 | — | — | — | — | — |
<!-- ws:datasets:end -->

## 准备记录

暂无。
