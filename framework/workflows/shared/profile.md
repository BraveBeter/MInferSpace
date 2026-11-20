# 共享子流程：Profile

## 组织

```text
profile-results/<UTC>-<ID>-<tool>-<role>/
├── execution/     # 采集命令、工具版本与配置、代码身份、环境、负载、采集范围、日志
├── traces/        # profiler 原始产物，保留原文件名（不跟踪，保留说明与元数据文件）
├── exports/       # 按需：统计表、截图，可追溯到 trace 的事件或时间区间
└── analysis.md    # 采集目的、负载、关键区间、观察、假设，链接证据
```

没有导出材料时不创建 `exports/`。

## 步骤

1. 明确要回答的问题（例如“decode 阶段 GPU 空闲从哪里来”），据此按 [references/profiling.md](../../references/profiling.md) 选工具与采集范围。
2. `ws run-dir <ID> <tool> <role> --kind profile` 生成目录，`ws record` 记录身份。
3. 采集时控制范围（时间窗口、请求数、步数），避免 trace 过大；记录 profiler 开销对行为的可能影响。
4. 用 [templates/profile-analysis.md](../../templates/profile-analysis.md) 写 `analysis.md`：区分观察事实与推断；给出可被 benchmark 验证的假设。
5. 登记到 `profile-results/README.md` 索引，链接到 item.md。

## 规则

- profile 用于定位与验证机制，不用于正式性能结论；与 benchmark 分开运行，并注明二者条件是否相同。
- 优化前后对比 profile 时使用相同负载与采集范围。
