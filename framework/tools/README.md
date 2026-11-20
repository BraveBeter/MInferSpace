# 工具链：`ws`

`ws.py` 把工作区中可机械执行的规则（建项、门禁自动检查、运行目录与身份留档、一致性校验、实例初始化）工具化。仅依赖 Python 3.9+ 标准库。

从工作区根目录运行：`python3 framework/tools/ws.py <命令> [参数]`。

## 命令一览

| 命令 | 用途 | 示例 |
| --- | --- | --- |
| `init` | 在目标目录生成新实例骨架（基于 `framework/templates/instance/`） | `python3 framework/tools/ws.py init . --name "qwen-omni on sglang-omni"` |
| `new` | 分配编号、生成 `item.md`，并同步登记到 `work/README.md` 与 `PLAN.md` | `python3 framework/tools/ws.py new opt codec-cuda-graph --summary "为 codec 开启 CUDA Graph"` |
| `status` | 汇总活动工作项、worktree 状态与可选包导入路径 | `python3 framework/tools/ws.py status --check-pkg sglang` |
| `run-dir` | 生成规范的证据运行目录并仅预建 `execution/` | `python3 framework/tools/ws.py run-dir OPT-0001 e2e candidate` |
| `record` | 在 `<run-dir>/execution/ws-record.json` 记录代码身份（含 dirty patch）、包路径、硬件与命令 | `python3 framework/tools/ws.py record <run-dir> --repo worktrees/sglang-omni/opt-0001 --cmd "..."` |
| `gate` | 执行当前或指定阶段的门禁检查；加 `--write` 将结果追加到 `item.md` | `python3 framework/tools/ws.py gate OPT-0001 --write` |
| `lint` | 校验文档死链、工作项/索引/PLAN 一致性、证据命名与登记、浮动版本、凭据泄露 | `python3 framework/tools/ws.py lint` |

## 测试

```bash
python3 -m unittest discover -s framework/tools/tests -v
```
