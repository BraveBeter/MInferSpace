# 共享子流程：正确性验证

正确性证据保存在 `validation-results/<ID>/<UTC>-<check>-<role>/`，结构为 `execution/`、原始输出、`report.md`。

## 验证层级

| 层级 | 方法 | 适用 | 口径 |
| --- | --- | --- | --- |
| 加载 | 记录 missing/unexpected 参数、形状与 dtype 检查 | ADAPT A3 | 无未解释项 |
| 逐层 | hook 抽样层 hidden states，与 golden 比较余弦相似度与相对误差 | ADAPT A4、FIX | `corr.layer_*` |
| 输出 | logits top-1 一致率、最大绝对误差 | ADAPT A4、FIX | `corr.logits_*` |
| 生成 | greedy token 序列逐个比较，记录首个分叉位置与 logit 间隔 | ADAPT A4/A5、OPT O5 | `corr.greedy_*`、`opt.greedy_identical` |
| 任务 | 项目质量套件（准确率、WER、SIM、MOS 等） | ADAPT A6、OPT O5、FIX F3 | `acc.*` |
| 测试 | 目标仓库的单元与模型测试 | 产生代码的工作项 | 全部通过 |

口径数值见 [defaults.md](../../conventions/defaults.md)，以项目和工作项覆盖为准。

## golden 生成

- 在参考环境中运行，固定 prompt 集合、greedy、seed、dtype、设备。
- 保存：抽样层 hidden states（首层、末层及均匀抽样的中间层）、logits、生成 token；音频模型保存 codes 与音频。
- 重跑一次确认可复现，差异写入报告。
- 存放与登记见 [asset-intake.md](asset-intake.md#golden-数据)。

## 对齐操作要点

- 参考与候选的输入必须完全一致：tokenize 结果、chat template、特殊 token、多模态预处理输出逐项比对。
- 从第一个超差层开始定位，不从输出端倒推；排查顺序见 [adapt-handbook.md](../../references/adapt-handbook.md#3-对齐排错)。
- 候选先在最简配置下对齐，再逐项开启优化特性，每项回归。
- 记录非确定性来源（atomic 归约、不同 kernel 选择、批次组成），区分“非确定性导致的差异”和“实现错误”。

## report.md

写明：验证对象（commit、配置）、golden 版本、口径及来源、逐项结果表、结论（通过/未通过/有条件通过及条件）、未解释差异。
