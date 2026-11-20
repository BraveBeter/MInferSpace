# 项目卡：<模型> on <引擎>

- **框架版本**：v0.1.0（见 [framework/README.md](framework/README.md)）
- **目标**：待填写（一句话描述：适配或优化 `<模型>` on `<引擎>`）
- **范围**：
  - 做什么：待填写
  - 明确不做什么：待填写

## 模型与源码

- **目标模型**：待填写（登记见 [checkpoints/README.md](checkpoints/README.md)）
- **目标引擎仓库与起点**：待填写（登记见 [worktrees/README.md](worktrees/README.md)）
- **目标仓库开发者规范**：待填写（源码仓库内路径或带固定 commit 的远端链接）
- **硬件**：待填写（GPU 型号 × 数量、驱动与 CUDA 版本）

## 评测套件

> 遵循 [benchmark.md](framework/workflows/shared/benchmark.md#评测套件契约)。

| suite | 类型 | 入口 | 配置 | 关键指标 | 可比性条件 | 重复与噪声 | 产物 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 待填写 | — | — | — | — | — | 采用框架默认 | — |

## 验收口径覆盖

> 未列出的键一律采用 [framework/conventions/defaults.md](framework/conventions/defaults.md) 默认值。修改须经用户确认。

| 键名 | 默认值 | 本项目值 | 理由 | 用户确认记录 |
| --- | --- | --- | --- | --- |
| 暂无 | — | — | — | — |

## 关键场景（防回退）

- 待填写（列出优化或适配变更后必须检查不回退的场景）

## 自主边界项目参数

- 下载确认阈值：沿用默认 `auto.download_max_gb`（或填写覆盖值）
- GPU 占用确认阈值：沿用默认 `auto.gpu_job_max_hours`（或填写覆盖值）
- 共享 GPU 调度约束：待填写
