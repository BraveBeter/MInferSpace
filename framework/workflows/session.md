# 会话协议

保证任意会话中断后，下一个 Agent 读少量文件即可续接。

| 时机 | 必做动作 |
| --- | --- |
| 会话开始 | 读 `AGENTS.md`、`PROJECT.md`、`PLAN.md`；续接时读工作项的“状态与交接”节；运行 `ws status` 核对 worktree 分支、commit、未提交修改 |
| 动手改源码前 | 读目标仓库的 `AGENTS.md`、`README.md`、`CONTRIBUTING` 及 `PROJECT.md` 列出的开发者规范；读要修改的代码及其相邻实现 |
| 运行前 | 核对实际加载的源码路径、环境与资产版本（见 [env-setup.md](shared/env-setup.md#运行前核对)） |
| 阶段结束 | 运行 `ws gate <ID> --write` 并逐项回应；按[同步矩阵](../conventions/doc-sync-matrix.md)更新文档；更新交接节 |
| 会话结束或中断前 | 交接节写明阶段、状态、最后可信状态（commit 或运行目录）、下一步、阻塞项、更新时间；运行 `ws lint` |
| 交付 | 按 [delivery.md](shared/delivery.md) 汇报 |

`ws` 指 `python3 framework/tools/ws.py`，用法见 [tools/README.md](../tools/README.md)。

## 交接节写法

- **最后可信状态**：已验证过的最新状态，例如“commit `<完整 sha>` 通过 A4 对齐，见 `validation-results/...`”。未验证的修改不能写为可信状态。
- **下一步**：一句可直接执行的动作，不写“继续优化”之类的泛称。
- **阻塞 / 待用户决定**：没有时写“无”。
