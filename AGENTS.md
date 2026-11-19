# moss-speech 工作区执行约定

本工作区用于优化 moss-speech on sglang-omni。所有开发、实验和文件管理动作均须遵循本文件及相关目录 README。

## 工作入口

- 开始任务前阅读 [PLAN.md](PLAN.md) 和相关目录 README。
- 开展 moss-speech 性能探索或优化时，使用 [moss-speech-opt-loop Skill](.agents/skills/moss-speech-opt-loop/SKILL.md) 掌握阶段动作和记录维护时点。

## 代码开发要求

- 修改源码前，必须阅读并遵循对应仓库的 `AGENTS.md` 和 `README.md`。  
- 修改源码前，必须阅读并遵循 sglang-omni 的[开发者参考规范](https://github.com/BraveBeter/sglang-omni/tree/f4cef25c0f6809483224913300d82358abc701d7/docs/developer_reference)。
- 管理源码、基线和优化工作副本时，必须遵循 [worktrees/README.md](worktrees/README.md)。  
- 实现范围围绕当前策略，避免混入无关修改。  
- 必须遵循最小改动原则，确保每个改动都是必要的，且范围最小。
- 优化须保持功能和输出协议正确。候选保留条件由用户说明，记入策略文档。
- 运行前核对实际源码路径、环境和加载版本。正式评测前执行 [运行前检查](benchmark-results/README.md#运行前检查)。
- 按改动范围执行必要的正确性检查，记录验证结果。

## 策略与计划要求

- 策略文档、策略索引及 PLAN.md 的字段和格式遵循 [strategies/README.md](strategies/README.md)。
- 策略结论以实际实现和评测证据为依据。推送和候选资源处置遵循用户授权。

## Profile 与评测要求

- 执行 profile 和管理采集结果时，必须遵循 [profile-results/README.md](profile-results/README.md)。  
- 评测执行、输入协议、指标和比较契约，必须遵循 [benchmark-client/README.md](https://github.com/BraveBeter/moss-speech-benchmark/blob/ce69ea7a1620b5d6bb93d5675aa3991f1e90b8a9/README.md)。
- 管理评测目录、结果索引和基线引用时，必须遵循 [benchmark-results/README.md](benchmark-results/README.md)。  
- 正式性能结论须来自统一 benchmark，profile 用于定位和验证瓶颈。  
- 实验结论须链接对应代码版本、运行记录和比较证据。

## 环境、数据与配置要求

- 准备、修改和登记环境时，必须遵循 [envs/README.md](envs/README.md)。  
- 获取、转换和登记模型时，必须遵循 [checkpoints/README.md](checkpoints/README.md)。  
- 准备、转换和登记评测数据时，必须遵循 [datasets/README.md](datasets/README.md)。  
- 编写、使用和留存配置时，必须遵循 [configs/README.md](configs/README.md)。

## 文档规范要求

- 文档按职责归属到对应目录，保持每条约定简短明确。  
- 已有细则由对应 README 维护，其他文档通过链接引用。  
- 新增或调整文件职责时，同步对应 README 和索引。  
- 重命名、移动或删除文件时，同步更新路径和引用。  
- 文档区分事实、假设、计划和结论。  
- 示例和占位内容必须标明，不登记为实际完成的工作。  
- 本地文档链接使用相对路径，并核对目标有效。  
- 进度与结果如实记录，不将未执行或未验证的事项写为完成。

## 辅助脚本与临时文件要求

- 新增、使用和登记辅助脚本时，必须遵循 [scripts/README.md](scripts/README.md)。  
- 使用和清理临时文件时，必须遵循 [tmp/README.md](tmp/README.md)。  
- 持久记录和复现材料须存放在相应正式目录。

## 版本管理与交付要求

- 工作区文件跟踪必须遵循 [.gitignore](.gitignore)。  
- 源码仓库保持独立 Git 历史，工作区维护管理文档与实验记录。  
- 结束一项工作前，核对代码与记录并运行 [工作区检查](scripts/README.md#工作区检查)。
- 交付时说明实际改动、验证结果和未完成事项。
