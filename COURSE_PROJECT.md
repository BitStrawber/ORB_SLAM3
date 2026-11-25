# Robust 6DoF Tracking — 课程项目入口

五人小组课程大作业，基于官方 ORB-SLAM3 的 RGB / RGB+IMU / RGB-D+IMU 能力，研究视觉、深度及惯性观测退化时的 6DoF 跟踪性能与短时降级策略。

> 本仓库 Fork 自 [UZ-SLAMLab/ORB_SLAM3](https://github.com/UZ-SLAMLab/ORB_SLAM3)。原有 SLAM 源码归属原作者并遵循仓库 GPLv3 许可证。课程改进尚处于规划/实施阶段；本文件不表示实验已完成或达到指标。

## 首先阅读

- [完整课题方案、PPT 叙事及五人详细分工](docs/PROJECT_PLAN.md)
- [ORB-SLAM3 官方说明](README.md)
- [TartanAir V2 数据集](https://tartanair.org/)
- [TartanAir 下载和读取工具](https://github.com/castacks/tartanairpy)
- [evo 轨迹评估工具](https://github.com/MichaelGrupp/evo)

## 并行开发分支

| 角色 | 分支 | 独立实验 |
|---|---|---|
| A | `experiment/a-baselines` | 纯视觉、视觉+IMU、RGB-D+IMU 基线与 ATE/RPE |
| B | `experiment/b-visual` | 视觉模糊、弱纹理和光照变化 |
| C | `experiment/c-depth` | 深度噪声、空洞和中断消融 |
| D | `experiment/d-imu-prediction` | 视觉中断后的 0.5–3 秒 IMU 预测 |
| E | `experiment/e-degradation` | 质量评估、降级状态机和策略消融 |

公共设置分支：`setup/common`，用于数据格式、标定、公共运行入口和统一评测协议。稳定成果通过 PR 合入 `master`。

## 统一协作约定

1. 每个人仅在自己的 `experiment/*` 分支修改实验代码与结果，公共接口改动从 `setup/common` 提 PR。
2. 每组实验必须提交可独立复现的 `README.md`、配置、运行脚本、结果 CSV/JSON、至少两张 PNG 图。
3. 使用同一 TartanAir V2 轨迹集和固定随机种子；报告 ATE/RPE 时同时报告有效跟踪覆盖率。
4. 不上传体积较大的原始数据、编译目录、运行缓存和虚拟环境；用数据下载说明和脚本复现。
5. `2 秒可靠预测`、`ATE 降低 30%`、`丢失率降低 50%` 是实验检验目标，不是预先取得的成果。

## 提交 PR 时填写

```text
研究问题：
输入数据与实验配置：
运行命令：
输出路径（结果、图、日志）：
主要发现（含失败结果）：
与其他分支的接口变化：
```

详细标准、每个角色的资源链接和验收要求均见 `docs/PROJECT_PLAN.md`。
