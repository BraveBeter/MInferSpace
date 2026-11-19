# 工作区辅助脚本

辅助脚本用于重复的环境准备、资料采集或工具调用。登记命令的工作目录、输入与输出，沿用实际工具的入口和原生格式。

| 脚本 | 作用 | 运行方式 |
| --- | --- | --- |
| [check_workspace.py](check_workspace.py) | 检查工作区链接、任务与计划索引，以及文件大小和可能的文本凭据 | 在工作区根目录运行 `python3 scripts/check_workspace.py` |

## 工作区检查

使用 Python 3.9+ 和 Git。脚本只读检查受 Git 管理及未忽略的文件，并检查暂存 blob。相对链接应指向可随仓库取回的内容，忽略的本地产物可通过归档说明或清单引用。任务编号、状态与待办索引按[任务约定](../tasks/README.md)校验。

普通 Git 文件和暂存 blob 的上限为 10 MiB。项目可选择 Git LFS，LFS 文件的工作树内容可超过此上限，暂存区保存指针。文本凭据扫描覆盖私钥头、GitHub 和 Slack token 的高置信格式。发现问题时返回非零退出码。

修改检查器后运行 `python3 -m unittest discover -s scripts/tests -v`。
