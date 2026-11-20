# 项目卡：moss-speech on sglang-omni

- **框架版本**：v0.1.0（见 [framework/README.md](framework/README.md)）
- **目标**：在 `sglang-omni` 上持续优化 `moss-speech` 的推理性能与能力支持，保持功能、输出协议与语音质量正确。
- **范围**：
  - 做什么：建立可复现基线、性能分析与优化、必要的模型能力适配与缺陷修复。
  - 明确不做什么：修改未授权的远端分支；在不验证质量的前提下接受性能改动。

## 模型与源码

- **目标模型**：`moss-speech`（待下载并固定版本，登记见 [checkpoints/README.md](checkpoints/README.md)）
- **目标引擎仓库与固定起点**：`sglang-omni/baseline` — [BraveBeter/sglang-omni](https://github.com/BraveBeter/sglang-omni) 分支 `fix/moss-speech-all-modalities-review-20261111`，commit [`f4cef25c0f6809483224913300d82358abc701d7`](https://github.com/BraveBeter/sglang-omni/commit/f4cef25c0f6809483224913300d82358abc701d7)（详见 [worktrees/README.md](worktrees/README.md)）
- **目标仓库开发者规范**：本地 `worktrees/sglang-omni/baseline/docs/developer_reference/`，远端固定版本 [docs/developer_reference](https://github.com/BraveBeter/sglang-omni/tree/f4cef25c0f6809483224913300d82358abc701d7/docs/developer_reference)
- **硬件**：待首台运行机器确定后补全（GPU 型号 × 数量、驱动与 CUDA 版本）

## 评测套件

> 遵循 [benchmark.md](framework/workflows/shared/benchmark.md#评测套件契约)；客户端细则见 [benchmark-results/README.md](benchmark-results/README.md)。

| suite | 类型 | 入口 | 配置 | 关键指标 | 可比性条件 | 重复与噪声 | 产物 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `e2e` | performance + quality | `moss-speech-bench e2e run` / `score` / `report` | `configs/benchmark/e2e.json`、`scoring.json`、`deployment.json` | 延迟（TTFT/TTFA/E2E）、吞吐、E2E 质量评分 | 复用基线 `selection.json`、同生成参数、同硬件与客户端版本 | 采用框架默认 | `summary.md`、`manifest.json`、`selection.json`、`comparison.md` 等 |
| `codec` | performance + quality | `moss-speech-bench codec run` / `score` | `configs/benchmark/codec.json`、`codec-scoring.json` | 重建延迟/RTF、Codec 质量评分 | 同 `corpus.jsonl` revision 与 SHA-256、同设备与客户端版本 | 采用框架默认 | `summary.md`、`manifest.json`、`samples.json`、`generation.json`、`quality.*` 等 |

## 验收口径覆盖

> 未列出的键一律采用 [framework/conventions/defaults.md](framework/conventions/defaults.md) 默认值。修改须经用户确认。

| 键名 | 默认值 | 本项目值 | 理由 | 用户确认记录 |
| --- | --- | --- | --- | --- |
| 暂无 | — | — | — | — |

## 关键场景（防回退）

- OpenAudioBench E2E（LLaMA Questions、TriviaQA、WebQuestions）性能与质量不回退。
- Seed-TTS-Eval Codec（EN1088、ZH2020 共 3108 对）重建质量不回退。
- 流式与非流式输出协议保持兼容。

## 自主边界项目参数

- 下载确认阈值：沿用默认 `auto.download_max_gb`（50 GB）
- GPU 占用确认阈值：沿用默认 `auto.gpu_job_max_hours`（4 小时）
- 共享 GPU 调度约束：运行前核对 `nvidia-smi`，不与其他任务争抢同一张卡
