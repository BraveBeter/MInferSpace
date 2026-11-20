# 运行配置

通用规则见 [layout.md](../framework/conventions/layout.md#configs)。本表路径相对 `configs/`。

## 本项目评测配置约定（示例）

以下为 `moss-speech-bench` 的预期配置文件及调用入口，实际准备后在下方登记：

| 配置文件（示例） | 用途 | 使用工具及调用参数 | 客户端格式参考 |
| --- | --- | --- | --- |
| `benchmark/e2e.json` | E2E 数据和服务能力配置 | `moss-speech-bench e2e run --config` | `benchmark-client/examples/e2e.json` |
| `benchmark/codec.json` | Codec 数据、模型、环境与设备配置 | `moss-speech-bench codec run --config` | `benchmark-client/examples/codec.json` |
| `benchmark/scoring.json` | E2E 离线质量评分配置 | `moss-speech-bench e2e score --score-config` | `benchmark-client/examples/scoring.json` |
| `benchmark/codec-scoring.json` | Codec 离线质量评分配置 | `moss-speech-bench codec score --score-config` | `benchmark-client/examples/codec-scoring.json` |
| `benchmark/deployment.json` | 被测服务代码身份与部署条件 | `moss-speech-bench e2e run --deployment` | `benchmark-client/examples/deployment.example.json` |

服务的实际启动配置放在 `server/`。评测客户端配置中的相对文件路径以配置文件所在目录为基准解析，复用示例配置时核对路径指向实际版本资产。

## 已登记配置

<!-- ws:configs:begin -->
| 配置文件 | 用途 | 使用工具 | 调用方式 |
| --- | --- | --- | --- |
| 暂无 | — | — | — |
<!-- ws:configs:end -->
