# 共享子流程：评测

## 评测套件契约

框架不规定评测客户端实现，只规定契约。`PROJECT.md` 为每个套件声明以下字段：

| 字段 | 含义 |
| --- | --- |
| `suite` | 套件名，用于运行目录命名 |
| 类型 | `performance`、`quality` 或二者兼有 |
| 入口 | 实际命令或客户端 |
| 配置 | `configs/benchmark/` 中的文件 |
| 关键指标 | 用于验收的指标及优化方向 |
| 可比性条件 | 判定两次运行可比的条件 |
| 重复与噪声 | 预热、重复轮数、噪声阈值（默认见 [defaults.md](../../conventions/defaults.md#性能评测)） |
| 产物 | 客户端原生产物与对比报告的生成方式 |

接入的客户端须满足：输出到指定目录；记录代码身份、环境与配置；能生成基线与候选的对比。项目特有的客户端细则写在实例 `benchmark-results/README.md`。

## 执行步骤

1. 运行前核对（[env-setup.md](env-setup.md#运行前核对)）。
2. 生成运行目录：`ws run-dir <ID> <suite> <role>`，它会创建 `execution/`。若客户端要求运行目录为空，`execution/` 是唯一允许预先存在的内容。
3. 记录身份：`ws record <运行目录> --repo <源码路径> ... --cmd "<命令>"`。
4. 执行评测，命令与实际配置副本存入 `execution/`。
5. 候选复用基线的冻结选样（如客户端支持）；用客户端的对比功能生成对比报告。
6. 登记到 `benchmark-results/README.md` 索引，并在 item.md 日志中记录结果摘要与链接。

## 基线复用

- 已有基线可跨工作项引用，保留在原目录，在 item.md 与索引中链接，不复制。
- 重新测量才创建新目录。
- 可比性按客户端原生契约检查，不以目录名相同代替。

## 结果解读

- 报告关键指标的均值与波动（CV 或置信区间），按 [defaults.md](../../conventions/defaults.md#性能评测) 判定收益与回退。
- 失败、中断、未评分的运行保留并标注。
- 人工分析写在运行目录的 `analysis/` 中，不改写客户端生成的摘要。

方法学细节见 [references/benchmarking.md](../../references/benchmarking.md)。
