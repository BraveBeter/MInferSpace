# 评测数据

这里保存固定版本的评测输入，供 E2E 与 Codec 评测配置引用。每次运行的冻结选样和输出保存在对应的 benchmark 运行目录。

## 组织形式

```text
datasets/
├── README.md
├── openaudiobench/
│   └── <revision>/
│       └── <原始 CSV 与音频文件>
└── seed-tts-eval/
    └── <revision>/
        ├── corpus.jsonl
        └── <原始音频文件>
```

以上数据目录仅为组织示例，目前尚未下载或准备数据。具体目录在确定来源和版本后创建。

- 按数据集及固定版本组织，保留原始数据布局，通过客户端配置指定实际文件路径。
- `<revision>` 使用来源提供的固定版本或完整 commit。预处理方式或清单内容变化时使用可区分的新准备版本目录，并记录原始来源版本与准备方式。
- 保留已有评测依赖的数据版本，避免同一路径中的内容被替换后影响复现或选样复用。

## 输入职责

### OpenAudioBench：E2E

包含 LLaMA Questions、TriviaQA、WebQuestions。使用客户端支持的原始 CSV 与对应音频，E2E 配置中的 `source` 指向 CSV，`audio_root` 指向相应音频目录，并提供固定 `revision`。配置格式见 [E2E 示例](../benchmark-client/examples/e2e.json)。

样本字段和数量校验沿用 [客户端协议](../benchmark-client/README.md)。每次运行由客户端生成 `selection.json`，保存在 `benchmark-results/<策略编号>/<run-id>/`；候选评测可以引用该清单复用选样。

### Seed-TTS-Eval：Codec

保存完整 EN1088、ZH2020 数据，共 3108 对 target/prompt，以及客户端要求的 `corpus.jsonl`。每条清单记录样本 ID、语言、文本、target/prompt 音频路径及对应 SHA-256；音频路径相对 `corpus.jsonl` 所在目录。

Codec 配置通过 `corpus` 引用清单，并记录 corpus 的固定 revision 和整个 JSONL 的 SHA-256。字段、完整性要求和配置格式以 [Codec 协议](../benchmark-client/CODEC_ONLY.md) 与 [配置示例](../benchmark-client/examples/codec.json) 为准。

## 数据登记

目前尚无已准备的数据集。确定来源后登记实际获取和准备进度，完成准备后更新状态；本地目录相对 `datasets/`。

| 数据集 | 用途 | 来源 | 固定版本 | 本地目录 | 准备状态 |
| --- | --- | --- | --- | --- | --- |
| 暂无 | — | — | — | — | — |

## 准备记录

需要转换数据或生成 Codec corpus 时，记录原始来源与固定版本、准备命令、脚本路径及版本、输出位置和必要的校验值。具体脚本及记录文件在确定准备步骤后落实，表格中可链接对应材料。

客户端配置中的相对路径按配置文件所在目录解析；准备配置时使用实际的数据路径。选样、内容哈希和完整性检查沿用客户端实现，具体来源与准备记录用于说明这些本地输入从何而来。
