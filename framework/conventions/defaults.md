# 默认验收口径

本文件给出框架默认值。每项带一个键名，便于覆盖时引用。

## 覆盖规则

- 生效顺序：**工作项覆盖 > PROJECT.md 覆盖 > 本文件默认值**。
- 项目级覆盖写在 `PROJECT.md` 的“验收口径覆盖”表中：键名、默认值、本项目值、理由、用户确认记录（日期与要点）。
- 工作项级覆盖写在 item.md 的“目标与验收”中，格式同上，必须有用户确认记录。
- Agent 不得自行放宽口径。收紧口径可自主决定，但须写明理由。
- 默认值以 BF16 推理、单一硬件型号为前提；其他精度（FP8、INT4 等）或跨硬件对比时，项目应显式设定。

## 正确性：数值对齐（适配、修复）

| 键名 | 默认值 | 说明 |
| --- | --- | --- |
| `corr.layer_cosine_min` | 0.999 | 抽样层 hidden states 与 golden 的余弦相似度下限 |
| `corr.layer_error_growth` | 无突变 | 逐层相对误差随层数平缓增长；相邻层误差突增一个数量级以上视为异常 |
| `corr.logits_top1_match_min` | 99% | golden prompt 所有位置 logits top-1 一致率下限 |
| `corr.greedy_prefix_tokens` | 32 | 每个 golden prompt greedy 生成前 N 个 token 须与参考一致 |
| `corr.greedy_tie_margin` | 0.05 | 分叉处参考 top-1 与 top-2 的 logit 差小于该值时，可视为数值并列，须记录 |

## 正确性：任务级精度

| 键名 | 默认值 | 说明 |
| --- | --- | --- |
| `acc.accuracy_abs_gap_max` | 1.0 个百分点 | 准确率类指标（gsm8k、mmlu、mmmu 等）与参考的绝对差上限 |
| `acc.wer_abs_gap_max` | 0.5 个百分点 | WER/CER 与参考的绝对差上限 |
| `acc.sim_abs_gap_max` | 0.01 | 说话人相似度与参考的绝对差上限 |
| `acc.mos_abs_gap_max` | 0.05 | UTMOS 等 MOS 预测值与参考的绝对差上限 |

适配项的“参考”为参考实现或官方公布数字；优化项的“参考”为同条件下的基线运行。

## 正确性：优化不回退

| 键名 | 默认值 | 说明 |
| --- | --- | --- |
| `opt.greedy_identical` | 要求 | 基线路径可确定性复现时，候选在固定选样上的 greedy 输出须与基线一致；不一致时按任务级精度口径验收并说明原因 |
| `opt.protocol_compatible` | 要求 | 输出协议、接口与流式事件格式保持兼容 |

## 性能评测

| 键名 | 默认值 | 说明 |
| --- | --- | --- |
| `perf.warmup` | 客户端默认，至少 1 轮 | 预热结果不计入 |
| `perf.repeats_min` | 3 | 每个配置的重复轮数下限 |
| `perf.cv_max` | 5% | 关键指标的变异系数上限；超过时排查干扰或增加轮数 |
| `perf.gain_min` | 3%，且大于 2 × max(基线 CV, 候选 CV) | 收益成立的最低要求 |
| `perf.regression_max` | 3% | 关键场景的回退容忍上限（超出噪声且超过该值视为回退） |
| `perf.estimate_confirm_below` | 5% | O3 预估收益上限低于该值时，实施前须与用户确认 |

## 自主边界参数

| 键名 | 默认值 | 说明 |
| --- | --- | --- |
| `auto.download_max_gb` | 50 | 单次下载超过该体积须确认 |
| `auto.gpu_job_max_hours` | 4 | 单次 GPU 任务超过该时长须确认 |
