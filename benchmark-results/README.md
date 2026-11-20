# Benchmark 结果

通用规则见 [benchmark.md](../framework/workflows/shared/benchmark.md) 与 [evidence.md](../framework/conventions/evidence.md)。套件定义见 [PROJECT.md](../PROJECT.md#评测套件)。

## moss-speech-bench 接入细则

- 评测协议与原生产物定义以 `benchmark-client/README.md` 为准。
- 将最内层运行目录传给 `--output-dir`（如 `benchmark-results/OPT-0001/20261118T110000Z-e2e-candidate`），可用 `ws run-dir` 生成。一次客户端运行可包含多个数据集、模态、并发和重复轮次，由客户端内部管理，不按内部轮次另建外层运行目录。
- 首次推理前，运行目录应不存在、为空或仅含 `execution/`；不要预先放入 README 或 `analysis/`。
- 推理、离线评分与单次运行报告复用同一 `--output-dir`；E2E 显式 `--resume` 按客户端规则在原目录恢复，属于同一次运行。
- E2E 使用 `--deployment` 提供服务身份；候选优先通过 `--selection` 复用基线的 `selection.json`；对比使用 `e2e report --output-dir <候选目录> --baseline <基线目录>`，在候选目录生成 `comparison.md` 与 `comparison.json`。
- Codec 遵循 `benchmark-client/CODEC_ONLY.md`，不支持隐式恢复；对比汇总报告使用 `ws run-dir <ID> codec comparison` 在同工作项下生成 `<UTC>-codec-comparison/`（保留 `execution/` 记录对比命令与输入），将其链接写入下方索引对应运行的“关键对比 / 备注”列，不单起推理运行行。
- 原生产物（`summary.md`、`manifest.json`、`selection.json`、`plan.json`、`performance*.json`、`quality.*`、`samples.json`、`generation.json`、`execution/` 等）沿用客户端约定；人工分析写在 `analysis/` 中，不改写 `summary.md`。

## 运行索引

<!-- ws:benchmark-index:begin -->
| 工作项 | 运行目录 | 套件 | 角色 | 状态 | 关键对比 / 备注 |
| --- | --- | --- | --- | --- | --- |
| 暂无 | — | — | — | — | — |
<!-- ws:benchmark-index:end -->
