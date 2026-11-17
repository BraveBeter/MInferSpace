# 运行配置

这里集中保存可复用的服务启动、评测与 profile 配置。每次运行的实际配置和执行命令保存在相应结果目录的 `execution/` 中。

## 组织形式

```text
configs/
├── README.md
├── server/                  # 服务启动配置
├── benchmark/
│   ├── e2e.json
│   ├── codec.json
│   ├── scoring.json
│   ├── codec-scoring.json
│   └── deployment.json
└── profile/                 # 各 profiler 的采集配置
```

以上配置文件和子目录为组织示例，在确定实际参数与使用工具后创建。目前尚未准备运行配置。

## 文件职责

- `server/`：服务启动配置，使用实际服务工具支持的原生格式。具体文件随启动方式确定。
- `benchmark/`：沿用评测客户端支持的 JSON 格式，参考其 `examples/` 填入实际数据、模型、环境等信息。并发、预热、轮数等 CLI 参数记录在执行命令中。
- `profile/`：使用实际 profiler 支持的原生配置格式，具体文件随采集方式确定。

评测配置的预期用途如下，文件名为填写示例：

| 配置文件 | 用途 | 使用工具及调用参数 | 客户端格式参考 |
| --- | --- | --- | --- |
| `benchmark/e2e.json` | E2E 数据和服务能力等配置 | `moss-speech-bench e2e run --config` | [e2e.json](../benchmark-client/examples/e2e.json) |
| `benchmark/codec.json` | Codec 数据、模型、环境和设备等配置 | `moss-speech-bench codec run --config` | [codec.json](../benchmark-client/examples/codec.json) |
| `benchmark/scoring.json` | E2E 离线质量评分配置 | `moss-speech-bench e2e score --score-config` | [scoring.json](../benchmark-client/examples/scoring.json) |
| `benchmark/codec-scoring.json` | Codec 离线质量评分配置 | `moss-speech-bench codec score --score-config` | [codec-scoring.json](../benchmark-client/examples/codec-scoring.json) |
| `benchmark/deployment.json` | 被测服务的代码身份与部署条件，作为评测元数据 | `moss-speech-bench e2e run --deployment` | [deployment.example.json](../benchmark-client/examples/deployment.example.json) |

`deployment.json` 用于向客户端提供服务身份与条件，服务的实际启动配置放在 `server/`。

## 路径与运行留档

- 相对路径按各工具的规则解析。评测客户端配置中的文件路径相对配置文件所在目录；Codec corpus 中的音频路径相对 corpus 所在目录。
- 示例配置在本工作区使用时需核对路径，指向实际版本的数据、模型、源码及环境。
- 每次运行在对应 `execution/` 中留存实际使用的配置与命令，包括 CLI 参数及必要的覆盖设置。留档副本若用于重跑，须核对相对路径解析后仍指向正确资产。
- 凭据通过外部环境等方式提供，配置和留档只记录所用变量名，不保存凭据值。

## 已有配置

下表只登记已准备的实际配置；文件路径相对 `configs/`，调用方式注明具体入口与配置参数。

| 配置文件 | 用途 | 使用工具 | 调用方式 |
| --- | --- | --- | --- |
| 暂无 | — | — | — |
