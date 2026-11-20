# 门禁：模型适配（ADAPT）

配合 [workflows/adapt.md](../workflows/adapt.md) 使用。

## A0 接入

- [auto:start_commit] 目标引擎仓库的起点 commit 为完整 40 位 SHA
- [evidence] 模型权重已在 `checkpoints/README.md` 登记固定版本
- [evidence] 参考实现源码已在 `worktrees/README.md` 登记固定 commit
- [evidence] `knowledge/model.md` 已记录模型概要与许可证
- [judgement] 许可证允许当前使用场景，目标硬件与首版能力范围明确

## A1 设计

- [auto:design_exists] 工作项目录下已编写 `design.md`
- [judgement] 已找到并引用 SG 中最相近的已支持模型
- [judgement] 每个组件均有复用、继承或新增决策及理由
- [judgement] 权重名映射表完整覆盖参考权重（含合并/拆分关系）
- [judgement] 首版特性矩阵清晰标明支持、后续与不支持项

## A2 参考与 golden

- [auto:validation_indexed] `validation-results/<ID>/` 存在 golden 验证记录且已入索引
- [evidence] golden 清单与生成脚本已登记到 `datasets/README.md`
- [evidence] 参考实现环境已生成快照并在 `envs/README.md` 登记
- [judgement] 重跑一次确认 golden 可复现，已记录 dtype、设备与非确定性来源

## A3 骨架实现

- [auto:branch] 实现分支与 worktree 已创建并登记
- [auto:validation_indexed] `validation-results/<ID>/` 存在加载验证记录且已入索引
- [evidence] 加载日志记录了 missing / unexpected 参数
- [judgement] 所有 missing / unexpected 参数均有合理解释；最简配置下服务可启动并返回结果

## A4 数值对齐

- [auto:validation_indexed] `validation-results/<ID>/` 存在对齐报告且已入索引
- [evidence] 对齐报告包含抽样层误差表、logits top-1 一致率与 greedy token 对比
- [judgement] 逐层余弦相似度、误差增长、logits 与 greedy 输出均满足口径（默认见 `corr.*`）
- [judgement] 调试用 hook / dump 工具位于工作区 `scripts/`，未混入目标仓库

## A5 特性扩展

- [auto:validation_indexed] 特性验证结果已留档并入索引
- [evidence] `design.md` 特性矩阵中每项首版支持特性均附验证证据链接
- [judgement] 每开启一项特性后已回归对齐与输出一致性
- [judgement] 声明不支持的特性会显式报错，不会静默产生错误输出

## A6 精度与基线

- [auto:benchmark_indexed] 精度与基线评测运行已留档并入索引
- [evidence] item.md 记录了质量套件与参考实现或官方数字的对比表
- [judgement] 任务级精度满足 `acc.*` 口径（或项目覆盖值）
- [judgement] 性能基线运行条件清晰，可供后续优化引用

## A7 测试、文档与交付

- [auto:review_recorded] 已完成独立审查并记录处理结果
- [auto:decision_recorded] 已记录交付决定与执行状态
- [auto:handoff] 交接节已更新
- [auto:lint] `ws lint` 无错误
- [evidence] 目标仓库的单元测试与模型测试运行结果已留档
- [judgement] [code-quality.md](code-quality.md) 清单全部满足
- [judgement] 模型文档、支持列表、启动示例已按仓库规范补齐；复盘已完成
