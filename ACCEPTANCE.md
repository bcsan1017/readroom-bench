# ACCEPTANCE — v0.2 验收记录（2026-08-20，真实 API 轮）

上一轮（v0.1 mock 轮，2026-08-20 早）记录见 git 历史 `1ac8561`。本轮验收 v0.2 改造：整手切片 / EV 主指标 / 豆包时间轴真稿 / 标注工具 / 真跑。

| # | 项 | 结果 | 证据 |
|---|---|---|---|
| 1 | 切片=整手（发牌→收池） | 通过 | 窗口 468.0–582.5s（114.5s）：468=b-roll 后该手首个牌桌镜头（HAND 15），582.5=Deeb 收池完、583s 转场卡前；逐 5s 抽帧 + 两端逐秒抽帧人工确认（README 决策 12） |
| 2 | 整手打码无泄露 | 通过 | 新增两处泄露源均已处理：翻前多行面板/广角漂浮底牌标签（`player_panels_tall` [0,120,280,720] 按 mask_windows 0–28s 分段开启）、顶部 outs/blinds 条加宽到 [560,25,1280,78]；对 t=8/17/21/26/62/73（含全部广角与 outs 条出现点）全分辨率人工核验全覆盖；`mask_check/` 6 帧留档 |
| 3 | EV 主指标单测 | 通过 | `tests/test_scoring.py` 3/3：score_ev_bb 边界值（p=1/0/0.5、负 EV 扣分）、oracle 上界、hard 口径、合成 12 题读人增益>0、无知模型 EV≈0、CI 包含点估计、ev_capture∈(0,1]、recognized 剔除；`tests/test_equity.py` 7/7 不变 |
| 4 | 豆包时间轴真稿 | 通过（待人工校准） | `timeline_meta.json`：doubao-seed-2-1-pro-260628，46 事件，禁情绪词 0 命中，71k prompt tokens / 54s；密度合格（长考段 89–107s 每 1–2s 一条，两人都覆盖）；质量观感：六字段客观、无情绪词，但时间点有漂移（all-in 推筹码记在 t≈99，实际 89）→ 留给 annotator 校准（README 决策 21），item.json 标 human_verified=false |
| 5 | 标注工具①手牌信息核对 | 通过（API 自测） | GET/POST truth 回读一致、首次 POST 备份 .bak；recompute 调 pipeline.equity 返回 req=0.3401/ev=211.5bb 与真值一致；非法牌返回 error 不崩 |
| 6 | 标注工具②时间轴校准 | 通过（API 自测） | GET 46 条真稿+meta（旧格式宽容降级）；POST 按 t 排序写回、全行 human_verified=true、同步 timeline.txt 与 item.json timeline_text/is_mock；禁用词表 46 词从 prompt 解析；前端点行跳视频/插删行/实时禁词标红（代码审阅） |
| 7 | 标注工具③遮罩检查 | 通过（API 自测） | mask_review.json 缺省结构/POST 回读一致/updated_at；前端标记当前播放时间为泄露点 |
| 8 | 标注工具④cue 核验 | 通过（API 自测） | /api/hallucination 读回真跑 27 行；人工改判写回；覆盖率统计（human!=null 及 sampled_for_review 口径）；judge 明细逐条展示 |
| 9 | 标注工具视频播放 | 通过 | /video/hand_0001.mp4 Range 请求 206（bytes=0-99 / 100- / -50）、越界 416、进度条可拖；路径穿越 404 |
| 10 | deepseek-v4-pro 真跑 | 通过 | L0×3 + L1-text×3 全部 schema 合法（runs.jsonl）；p_call：L0 0.32/0.35/0.30，L1-text 0.38/0.25/0.32；两处坑已修：思维链 16k 推不完→thinking disabled（决策 15）、网关缓存→trial 去重标记（决策 16） |
| 11 | 豆包 L1-video 真跑（provisional） | 通过 | 3 trial 全部合法：p_call 0.35/0.28/0.25，每 trial 3–4 条带时间戳 cue（t=1/26/89/90/97/100 等，与画面事实对得上）；另跑 doubao L0×3 作同模型基线（0.35/0.70/0.30） |
| 12 | 幻觉 judge 真跑 | 通过 | 一次视频调用批判 27 条 cue（deepseek L1-text 17 + doubao L1-video 10），判 false 18 / true 9 / uncertain 0；抽检样本已标 15%（4 条）；spot-check：判定有区分度、evidence 具体（如"手放筹码旁未推出"） |
| 13 | 真实报表 | 通过 | `results/report.md`：EV 主表（deepseek L0 68.4 / L1-text 67.0；doubao L0 95.2 / L1-video 62.0 bb）、读人增益（deepseek L1-text −1.4bb；doubao L1-video −33.1bb）、幻觉率（0.71 / 0.60）、附录 Brier/ECE/一致性/结果口径 |
| 14 | 视频调用预算 ≤10 | 通过 | 实际 5 次：timeline 1 + doubao L1-video 3 + judge 1 |
| 15 | mock 链路仍可跑（无 key 环境） | 通过 | `runs_mock.jsonl` 42 条（L0×6+L1-text×5+L1-video×3 模型 ×3 trial）+ `report_mock.md`；dry-run 预览 14 个请求体 |
| 16 | key 不入库 | 通过 | .env 在 .gitignore；全仓 grep 无 key 明文；报表/预览无 key |

## 真跑数字摘要（1 题，链路验证性质）

- oracle EV = 211.5 bb（correct_call=True 的题，跟注全对才拿满）
- deepseek：L1-text 对 L0 读人增益 **−1.4 bb**（时间轴让它略更想弃牌；本题跟注才对，被扣）
- doubao\*：L1-video 对 L0 读人增益 **−33.1 bb**（看了视频更笃定弃牌——与 Nick 实际弃牌一致，但胜率口径下是错的；好题的意义所在）
- 幻觉率偏高（judge 口径）：deepseek L1-text 0.71、doubao L1-video 0.60 → 待人工抽检确认 judge 假阳性率后再定论

## 验收→修改→再验收记录

- R1：首版打码后抽查发现顶部 outs/blinds 条 y 实际 28–75（旧框 0–40 没盖住）、翻前左侧面板行高到 y≈130 → 加宽 top_strip、player_panels_tall 改 [0,120,280,720]，复检 6 个关键时刻全覆盖。
- R2：deepseek 首 probe reasoning 吃满 3000 token、content 空 → 提 16k 仍推不完（303s，输出退化）→ 改 thinking disabled（网关实测支持），3–7s/trial、输出正常。
- R3：deepseek 3 trial 输出全同（0.3s 返回，网关缓存）→ runner 加 trial-id 去重标记，重跑后 p_call 有正常方差。
- R4：annotator 全 API curl 自测（子任务执行），测试数据已恢复原状；对真跑数据二次冒烟（46 事件/27 cue/Range 206）通过。
