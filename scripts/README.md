# 工作区辅助脚本

这里存放实际工作中需要的辅助脚本，用于串联已有工具、减少重复操作。目前不预设必须实现的脚本；在出现明确需求后再编写和登记。

## 使用范围

- 环境信息采集、服务启动、profile 采集、数据准备或模型下载等操作，在频繁重复或容易出错时，可以通过辅助脚本完成。
- 环境可追溯、启动方式可复现等要求，可以先通过原有命令与执行记录满足，不要求额外编写包装脚本。
- 评测使用 `benchmark-client` 的原有入口和结果处理实现。辅助脚本负责必要的调用与流程串联。
- 脚本按实际需要明确源码路径、环境、配置和输出位置，以适用于不同基线、候选工作副本及运行条件。

## 脚本登记

新增脚本后更新下表，调用示例应说明执行目录及解释器或 shell，必要输入和输出位置应与实际行为一致。

| 脚本名称 | 用途 | 调用示例 | 必要输入 | 输出位置 |
| --- | --- | --- | --- | --- |
| [check_runtime.py](check_runtime.py) | 核对正式评测的运行时身份和 GPU 状态 | [运行前检查](../benchmark-results/README.md#运行前检查) | 服务或模型 Python、E2E deployment 或 Codec 配置、结果目录 | `execution/preflight-*.json` |
| [check_workspace.py](check_workspace.py) | 校验工作区链接、策略索引和待提交材料 | 从根目录执行 `python3 scripts/check_workspace.py` | Python 3.9+ 与 Git 工作树 | 标准输出及标准错误 |

本表的脚本名称链接到对应文件，路径相对本 README 所在的 `scripts/`。运行命令与产生的执行材料按各结果目录的约定留档。

## 工作区检查

阶段交付前运行 `python3 scripts/check_workspace.py`。脚本核对 Markdown 相对链接和索引；Git 忽略的本地产物通过随仓库保存的归档说明或 manifest 引用。检查使用工作树中的文档和文件，同时检查暂存变更的 blob 大小和文本凭据格式。

超过 10 MiB 的文件会报告路径。文本凭据检查覆盖私钥头、GitHub 和 Slack token 的高置信度格式，报告路径、行号和类型。发现问题时退出码为 1。

修改检查脚本后，在工作区根目录运行 `python3 -m unittest discover -s scripts/tests -v`。回归测试使用临时 Git 仓库和替身 GPU 遥测。
