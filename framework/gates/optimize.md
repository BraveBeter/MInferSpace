# 门禁：性能优化（OPT）

配合 [workflows/optimize.md](../workflows/optimize.md) 使用。`OPT-0000` 仅执行 O0、O1、O6。

## O0 起点

- [auto:start_commit] 源码起点 commit 为完整 40 位 SHA
- [evidence] `envs/README.md` 已登记所用环境与快照
- [evidence] 模型与数据版本已在对应 README 登记
- [judgement] 目标硬件、负载范围与验收口径（默认或覆盖）已写入 item.md

## O1 基线

- [auto:benchmark_indexed] 基线评测运行存在（或 item.md 明确引用已有可比基线目录）
- [evidence] 基线 `summary.md` 链接已写入 item.md
- [judgement] 预热、重复轮数与变异系数满足 `perf.*` 口径；基线可比条件已核验

## O2 Profile

- [auto:profile_indexed] 采集目录含 `analysis.md` 与 `execution/`，且已入索引
- [evidence] `analysis.md` 链接到原始 trace 说明及导出材料（如有）
- [judgement] 观察到的瓶颈有原始证据支撑，事实与推断区分明确
- [judgement] profile 与正式 benchmark 分开运行，并说明了条件异同

## O3 假设与方案

- [judgement] 假设写成可证伪陈述（做 X、指标 M 改善 Δ、原因 Y 及推翻条件）
- [judgement] 已给出收益上限估算；若低于 `perf.estimate_confirm_below`，已获用户确认
- [judgement] 已明确改动范围、风险、回退方式与量化验收标准
- [judgement] 已对照优化手册与 `knowledge/lessons.md` 检查先例

## O4 实现

- [auto:branch] 从起点 commit 创建的分支与 worktree 已登记
- [evidence] 候选 commit 已记录在 item.md 日志，且通过目标仓库 lint 与相关单元测试
- [judgement] diff 仅包含验证当前假设所需的最小改动，无调试残留

## O5 验证

- [auto:benchmark_indexed] 候选评测运行存在并已入索引
- [evidence] 对比报告（如 `comparison.md`）链接已写入 item.md
- [evidence] 正确性/精度验证结果链接已写入 item.md
- [judgement] 正确性满足 `opt.*` 与 `acc.*` 口径，输出协议保持兼容
- [judgement] 收益满足 `perf.gain_min`（超过测量噪声），给出均值与波动数值
- [judgement] `PROJECT.md` 关键场景回退不超过 `perf.regression_max`，逐项说明
- [judgement] 是否执行了候选 profile 验证机制生效（如未执行，说明理由）

## O6 决定

- [auto:review_recorded] 已完成代码与结论的独立审查并记录处理结果（`OPT-0000` 或 `discard` 无代码项仅审结论）
- [auto:decision_recorded] 已记录决定（`push` / `keep-local` / `discard`）及执行状态
- [auto:handoff] 交接节已更新
- [auto:lint] `ws lint` 无错误
- [judgement] 产生代码且非 `discard` 时，[code-quality.md](code-quality.md) 全部满足
- [judgement] 适用范围、波动与局限如实记录；复盘与 lessons 已更新
