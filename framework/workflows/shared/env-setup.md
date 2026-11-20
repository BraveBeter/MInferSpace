# 共享子流程：环境准备

## 组织

```text
envs/
├── README.md                 # 登记表
├── specs/<env>/              # 如何重建：安装步骤、依赖文件或容器定义
├── snapshots/<UTC>-<env>/    # 实际用了什么：Python、依赖版本、CUDA、驱动、硬件、镜像 digest
└── runtime/<env>/            # 本地 venv 等实际环境，不跟踪
```

- 依赖文件沿用实际使用的 pip、uv、Conda 或容器方式，不同时维护多套格式。
- 外部 Conda 环境或容器保留原位置，在登记表中写明定位信息。
- 环境变更后生成新快照，保留旧快照（旧证据仍引用它们）；证据的执行材料引用所用快照。

## 隔离

按依赖冲突决定是否拆分环境，常见划分：

| 环境 | 用途 |
| --- | --- |
| SG 服务环境 | 运行被测引擎；基线与候选若因 editable 安装相互影响，各用独立环境 |
| 参考实现环境 | 运行 transformers 或官方实现，生成 golden |
| 评测 / 评分环境 | 评测客户端、离线质量评分模型 |

## 运行前核对

每次正式运行（benchmark、profile、验证）前确认并记录到执行材料：

- 实际加载的包路径指向预期的 worktree，例如 `python -c "import sglang, os; print(os.path.dirname(sglang.__file__))"`；多包引擎逐个核对。
- 关键包版本与快照一致；与快照不一致时先生成新快照。
- 模型、数据路径指向登记的版本目录。
- GPU 空闲状况与可见设备（`nvidia-smi`、`CUDA_VISIBLE_DEVICES`）。

## 登记

`envs/README.md` 登记表列：环境名、用途、Python 版本、实际路径或定位信息、安装说明（链接到 `specs/<env>/`）、最新快照。
