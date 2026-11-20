# 事件 → 文档同步矩阵

每个阶段结束、每次会话结束前逐行对照本表。“自动校验”列标 ✅ 的项由 `ws lint` 检查。

| 事件 | 必须更新 | 自动校验 |
| --- | --- | --- |
| 新建工作项 | `item.md`、`work/README.md` 索引、`PLAN.md`（`ws new` 自动完成） | ✅ ID 唯一、无重复行、三处一致 |
| 工作项状态或阶段变化 | `item.md` 状态与交接、索引状态、`PLAN.md` | ✅ 状态与阶段一致、取值合法 |
| 工作项结项（done/cancelled） | `item.md` 结论与决定、索引、从 `PLAN.md` 移除、知识沉淀 | ✅ PLAN 不含已结项；`done` 须有合法决定 |
| clone 仓库、创建或移除 worktree / 分支 | `worktrees/README.md` 登记表、`item.md` 起点与实现分支 | ⚠️ 本地未检出时提示（不阻断干净克隆） |
| 新建或变更环境 | `envs/specs/<env>/`、新快照、`envs/README.md` | ✅ 登记的安装说明链接存在（外部路径仅提示） |
| 获取、转换模型或数据 | `checkpoints/README.md` 或 `datasets/README.md` 登记与准备记录 | ✅ 版本非浮动；本地未下载时提示 |
| 新增可复用配置 | `configs/README.md` | ✅ 登记文件存在 |
| 新增辅助脚本 | `scripts/README.md` | ✅ 登记文件存在 |
| 完成一次 benchmark | 运行目录（含 `execution/`）、`benchmark-results/README.md` 索引、`item.md` 日志 | ✅ ID 有对应工作项、命名规范、已入索引、`execution/` 存在 |
| 完成一次正确性验证 | 运行目录、`validation-results/README.md` 索引、`item.md` 日志；适配项更新特性矩阵 | ✅ 同上，`report.md` 存在 |
| 完成一次 profile | 采集目录与 `analysis.md`、`profile-results/README.md` 索引、`item.md` 日志 | ✅ 同上，`analysis.md` 存在 |
| 通过门禁 | `item.md` 门禁记录 | — |
| 完成独立审查 | `item.md` 审查记录 | — |
| 发现可复用经验或陷阱 | `knowledge/lessons.md`（带来源 ID） | — |
| 修改项目事实（硬件、套件、口径覆盖） | `PROJECT.md`（口径覆盖附用户确认记录） | — |
| 移动、重命名、删除文件 | 所有引用 | ✅ 相对链接死链与绝对路径检查 |
| 任何提交前 | 运行 `ws lint` | ✅ 含凭据扫描 |
