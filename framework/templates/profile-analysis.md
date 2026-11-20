# Profile 分析（模板）

> 采集目录：`profile-results/<run-id>/`｜关联工作项：`<ID>`｜采集方法见 [workflows/shared/profile.md](../../framework/workflows/shared/profile.md)

## 1. 采集目的与条件

- **要回答的问题**：待填写
- **被测代码**：仓库、分支、完整 commit、未提交修改（见 `execution/`）
- **工具与配置**：profiler 名称、版本、采集范围与参数
- **输入负载**：模型、数据、并发、请求数或步数；与正式 benchmark 条件的异同
- **环境与硬件**：环境快照引用、GPU 型号与数量

## 2. 观察事实

> 只写可从 trace 或导出统计直接核实的事实，并注明对应时间区间或事件名。

- 端到端时间分解（prefill / decode / stage 间等待 / CPU 调度 / GPU 空闲）：待填写
- 热点算子或阶段：待填写
- 原始证据位置：`traces/`（说明文件）、`exports/`（如有）

## 3. 推断与假设

> 明确标注为推断，给出可被 benchmark 或下一次 profile 证伪的预测。

- **推断**：待填写
- **待验证假设**：如果做 X，指标 M 改善约 Δ，因为 Y。
- **理论收益上限**：待填写

## 4. 下一步

- 待填写（关联工作项链接与相关 benchmark 链接）
