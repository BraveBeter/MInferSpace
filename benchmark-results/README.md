# Benchmark 结果

这里保存统一评测客户端的运行结果，按“策略 → 每次运行”分组。每次运行目录内的产物沿用 [benchmark-client 的原生约定](https://github.com/BraveBeter/moss-speech-benchmark/blob/ce69ea7a1620b5d6bb93d5675aa3991f1e90b8a9/README.md)。

## 组织与命名

```text
benchmark-results/
├── README.md
├── OPT-0000/                         # 初始基线
│   └── 20261117T120000Z-e2e-baseline/
└── OPT-0001/                         # 同一策略的各次评测
    ├── 20261118T100000Z-e2e-baseline/
    ├── 20261118T110000Z-e2e-candidate/
    └── 20261119T090000Z-codec-candidate/
```

以上目录仅为示例，目前没有评测记录。策略目录与运行目录在实际评测时创建。

- 第一层使用 `OPT-0000`、`OPT-0001` 等策略编号，对应策略文档。`OPT-0000` 用于初始基线；每项策略可以包含自己的基线和多个候选运行。
- 第二层使用 `<UTC开始时间>-<评测类型>-<角色>`，例如 `20261118T110000Z-e2e-candidate`。时间精确到秒，类型使用 `e2e` 或 `codec`，角色使用 `baseline` 或 `candidate`。
- 名称冲突时追加 `-02` 等后缀；重新运行使用新目录，已有结果继续保留。E2E 的显式 `--resume` 按客户端规则在原目录恢复，属于同一次运行。
- 日期写入运行名，同一策略跨天的结果仍放在同一个策略目录中。
- 一次客户端运行可以包含多个数据集、模态、并发和重复轮次，由客户端内部管理；不按内部轮次另建外层运行目录。

## 输出目录

将最内层运行目录传给 `--output-dir`。例如，从工作区根目录执行时，参数为：

```text
--output-dir benchmark-results/OPT-0001/20261118T110000Z-e2e-candidate
```

CLI 的相对输出路径以执行命令时的工作目录为基准。客户端支持创建多级父目录；无需预建策略或运行目录。

首次推理前，运行目录应不存在、为空，或仅含 `execution/` 目录。顶层的本 README 和策略层的资料不属于运行目录，不受此检查影响。不要提前在运行目录根下写 README、创建 `analysis/` 或放其他文件。

推理、离线评分和单次运行报告使用同一个 `--output-dir`，评分时复用已冻结的生成输出。

## 运行前检查

正式推理前运行 [check_runtime.py](../scripts/check_runtime.py)，通过后再调用客户端。将脚本路径、配置路径、源码路径和运行目录设置为绝对路径，确保检查与客户端指向同一份配置和结果目录。每次检查在 `execution/preflight-*.json` 保存身份、GPU 快照和通过或失败状态。失败时先排除原因并重新检查。

- E2E 在服务进程实际启动所用的解释器、工作目录、环境变量和容器内执行。用 `python -m sglang_omni.cli serve` 启动时可直接使用下方检查命令。用 `sgl-omni` 等 Python 脚本启动时，把实际脚本路径传给 `--launcher`，并使用该脚本实际使用的解释器。启动前核对导入路径、commit、工作树状态和已声明的分支，检出为 detached HEAD 时分支填写空字符串。服务就绪后、正式测量前用同一上下文再次执行，只把确认属于本次服务的 GPU worker PID 逐个传给 `--allow-gpu-pid`。`--gpu` 为 `nvidia-smi` 中的物理卡号，多卡逐个传入。启动上下文或资源发生变化时重新采集。

  启动前要求所有选中卡空闲。服务就绪后至少提供一个 worker PID，每张选中卡都须观察到本次服务的 worker。单卡示例：

  ```bash
  "$SERVER_PYTHON" "$WORKSPACE/scripts/check_runtime.py" --output-dir "$RUN_DIR" e2e \
    --deployment "$DEPLOYMENT" --source "$SERVER_CHECKOUT" --gpu "$GPU_INDEX"

  # 服务就绪后
  "$SERVER_PYTHON" "$WORKSPACE/scripts/check_runtime.py" --output-dir "$RUN_DIR" e2e \
    --deployment "$DEPLOYMENT" --source "$SERVER_CHECKOUT" --gpu "$GPU_INDEX" \
    --allow-gpu-pid "$WORKER_PID"
  ```

- Codec 用配置指定的 `python` 运行检查，脚本读取配置里的 `physical_gpu`，并核对 `sg-native` 的干净源码 SHA 或 `hf-native` 的依赖源码路径，再核验配置中声明的资产哈希。GPU 应空闲。客户端继续负责完整运行契约、语料校验及 worker 中的实际加载检查。

  ```bash
  "$CODEC_PYTHON" "$WORKSPACE/scripts/check_runtime.py" --output-dir "$RUN_DIR" codec \
    --config "$CODEC_CONFIG"
  ```

GPU 快照包含选定卡的 UUID、功耗、SM 和显存时钟、计算进程 PID。核对这些证据及运行期间观察到的资源争用或硬件异常；发现异常时记录原因，恢复可比条件后再测。

## 每次运行的产物

以下为原生产物的职责说明，不是要求手动创建的文件清单。具体文件随评测类型和执行阶段产生，以所用客户端版本为准。

| 产物 | 职责 |
| --- | --- |
| `summary.md` | 客户端生成的结果阅读入口；Codec 沿用自己的摘要结构 |
| `manifest.json` | 客户端记录的代码身份、运行契约及执行状态 |
| `selection.json` | E2E 冻结选样，用于后续候选复用 |
| `plan.json`、`inputs/`、`warmup-inputs/`、`cells/` | E2E 的计划、冻结输入、分组输出、预热和恢复尝试 |
| `performance.json`、`performance-averages.json`、`requests.jsonl` | E2E 原生性能与请求记录 |
| `quality.json`、`quality.md`、`quality/` | 按类型和评分阶段产生的质量结果及证据 |
| `samples.json`、`generation.json`、`codes/`、`audio/` | Codec 的冻结样本及原生重建产物 |
| `execution/` | 执行命令、配置、环境和日志；Codec 也在这里生成执行材料 |
| `analysis/` | 运行建立后的人工详细分析或客户端生成的分析产物 |

工作区不另行要求 `run.yaml`、`metrics.json` 或每次运行的 README。被测服务身份按客户端支持的方式提供：E2E 使用 `--deployment`，格式参考 [deployment 示例](https://github.com/BraveBeter/moss-speech-benchmark/blob/ce69ea7a1620b5d6bb93d5675aa3991f1e90b8a9/examples/deployment.example.json)；Codec 按其配置记录身份。实际服务进程加载的代码应与所填身份一致。

`summary.md` 会被报告命令重新生成，人工说明写在 `analysis/` 中，并链接原始证据。凭据通过外部环境传入，执行材料中保留所用变量名，不保存凭据值。

## 归档与恢复 E2E 冻结输入

冻结请求可能内嵌音频。`inputs/*.jsonl` 和 `warmup-inputs/*.jsonl` 通过仓库的 [Git LFS 规则](../.gitattributes) 跟踪，`summary.md` 继续链接原生路径。归档前在工作区根目录安装并启用 Git LFS（运行 `git lfs install --local`），再暂存运行材料并执行 [工作区检查](../scripts/README.md#工作区检查)。对已用普通 Git 跟踪的冻结输入，启用 LFS 后对这些路径运行 `git add --renormalize`。提交后运行 `git lfs fsck --objects HEAD` 核对对象，再用普通 `git push` 上传提交和 LFS 对象。

从新克隆或切换到目标提交后，在工作区根目录运行以下命令，将原始 JSONL 恢复到报告链接指向的位置。恢复完成后即可运行客户端的报告或离线评分命令。

```bash
git lfs install --local
git lfs pull
git lfs fsck --objects HEAD
```

## 基线复用与对比

- 已有基线可跨策略引用，保留在其原目录；在策略文档和下方索引中链接该次运行，无需复制结果。重新测量才创建新目录。
- 可比评测使用基线登记的运行环境、启动脚本、评测客户端版本或脚本、输入和负载。执行材料记录这些引用和传给启动脚本的实际源码路径。运行环境需要隔离时，按 [环境隔离约定](../envs/README.md#环境隔离) 记录各自环境。
- E2E 候选优先通过 `--selection` 复用基线的 `selection.json`。数据、生成参数和客户端指标实现等可比条件按原生契约检查，不以目录名相同代替可比性验证。
- E2E 对比使用 `e2e report --output-dir <候选目录> --baseline <基线目录>`，客户端在候选目录生成 `comparison.md` 和 `comparison.json`。
- 同一 E2E 候选需要做父基线和初始锚点比较时，分别执行报告命令。每次报告后将两份 `comparison.*` 保存到候选运行的 `analysis/parent/` 或 `analysis/anchor/`，再生成下一次报告。策略文档链接归档副本。
- Codec 的样本范围、评分和对比遵循 [Codec 协议](https://github.com/BraveBeter/moss-speech-benchmark/blob/ce69ea7a1620b5d6bb93d5675aa3991f1e90b8a9/CODEC_ONLY.md)。Codec 不支持隐式恢复；使用比较配置生成的汇总报告另放在同一策略下的新目录，例如 `20261119T100000Z-codec-comparison/`。该目录是对比报告，不登记为新的推理运行。
- 如果客户端契约或运行条件不满足可比性，记录差异，并在可比条件下重新测量涉及的版本。原运行继续保留，累计收益仍引用同一初始源码锚点。
- 失败、中断、预算耗尽和未评分的结果继续保留；状态以客户端记录为准。正式 benchmark 与 profile 分开运行。

## 可选评测指标

候选的保留条件由用户说明，并记录在 `strategy.md`。重复测量可用于说明稳定性和波动。以下是可选指标与阅读结果时关注的范围。

| 场景 | 指标示例 | 方向与覆盖 |
| --- | --- | --- |
| E2E 流式语音输出 | TTFA P95、播放欠载 P95、C50/C100 | 延迟和欠载越低越好，连续性通过率越高越好。关注连续性有效请求数。 |
| E2E 正确性与质量 | 语义准确率、适用的 UTMOS | 分数越高越好。关注计划分母和已评分数。 |
| Codec 重建 | 英文 WER、中文 CER、SIM | WER/CER 越低越好，SIM 越高越好。关注各指标的成功数与计划样本数。 |

用户采用某项指标时，明确其比较方向、绝对限值或相对对照的变化、覆盖要求和证据。按场景注明指标不适用或证据不足的原因，例如非流式运行缺少首事件数据。功能和输出协议的正确性独立验证。

## 策略索引

下表按策略登记实际评测。链接策略文档及关键运行的 `summary.md`；E2E 对比可另链接 `comparison.md`，Codec 对比链接对应报告。

| 策略编号 | 策略文档 | 关键基线 | 关键候选 | 结论或备注 |
| --- | --- | --- | --- | --- |
| 暂无 | — | — | — | — |

本表链接相对本 README：本策略内的摘要使用 `OPT-0001/<run-id>/summary.md`；策略文档使用 `../strategies/<策略目录>/strategy.md`。路径仅为填写形式，实际登记时替换为存在的目标。
