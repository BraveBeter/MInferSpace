# Profiling 工具手册

> 核验状态：方法学手册（2026-11-20 初版）。具体工具版本与参数以目标机器环境为准，并记录到 `execution/`。

## 1. 选型决策树

按“由粗到细”的原则选择工具：

| 想回答的问题 | 首选工具 | 说明 |
| --- | --- | --- |
| 端到端时间花在哪个阶段？GPU 有没有空泡？多 stage 如何重叠？ | **Nsight Systems (`nsys`)** 或 **SG 内置 PyTorch Profiler** | 先看全局 timeline，不要一开始就钻单个 kernel |
| CPU 侧 Python 哪里最耗时？（调度、预处理、音频编码） | **`py-spy`** / `cProfile` / `nsys --trace=osrt,nvtx` | 低开销定位 Python 热点函数 |
| PyTorch 算子级耗时、显存分配与调用栈 | **Torch Profiler**（含 SG 服务端 profile 接口，如有） | 能把 GPU kernel 对应回 Python 算子名 |
| 单个 CUDA kernel 是计算受限还是带宽受限？ | **Nsight Compute (`ncu`)** | 开销极大，只在已确认单个热点 kernel 后定向采集 |

## 2. 常用采集模板

以下命令为参考起点，实际运行前核对本机版本并把完整命令写入 `execution/`。

### Nsight Systems（端到端与多进程）

```bash
# 示例：采集指定窗口，避免整段运行 trace 过大
nsys profile \
  --trace=cuda,nvtx,osrt \
  --sample=none \
  --capture-range=cudaProfilerApi \
  --output=profile-results/<run-id>/traces/run \
  <启动或压测命令>
```

导出基础统计表到 `exports/`（可文本检索与跟踪）：

```bash
nsys stats --report cuda_gpu_kern_sum,cuda_api_sum \
  --format csv \
  --output profile-results/<run-id>/exports/stats \
  profile-results/<run-id>/traces/run.nsys-rep
```

### PyTorch Profiler / SG 内置接口

- 优先使用目标引擎自带的 start/stop profile 接口（先在当前源码核对环境变量与 HTTP/CLI 参数），只采集预热后的少量步数（如 5–20 步）。
- 原始 `*.pt.trace.json(.gz)` 保存在 `traces/`（不入 Git），将 Top-K 算子表导出为 CSV/Markdown 存入 `exports/`。

### py-spy（CPU 侧 Python 热点）

```bash
# 示例：附加到服务进程采集 15 秒
py-spy record --pid <PID> --duration 15 --rate 100 \
  --output=profile-results/<run-id>/exports/cpu-flame.svg
```

### Nsight Compute（单 kernel 深入分析）

```bash
# 示例：按 kernel 名称过滤，只采 1–2 次调用
ncu --kernel-name regex:<kernel_pattern> --launch-skip 10 --launch-count 2 \
  --set full --output profile-results/<run-id>/traces/kernel \
  <最小复现脚本>
```

## 3. 解读要点

- **先看 GPU 空闲比例**：GPU 利用率低或 kernel 间有明显空白，优化单个 GPU kernel 几乎没收益，应优先查 CPU 调度、launch 与同步。
- **区分预热与稳态**：首次请求包含 JIT 编译、显存分配与 CUDA Graph capture，分析稳态性能时跳过预热区间。
- **注意 profiler 自身开销**：开启 stack trace、显存记录或 ncu 会显著改变时间分布，因此绝不用 profile 结果代替正式 benchmark。
