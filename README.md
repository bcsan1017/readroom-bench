# readroom-bench — 读人 Bench 工具链（v0.2 真跑版）

规范来源（唯一）：[`docs/framework.md`](docs/framework.md)（读人 Bench 评测框架 v0.2：§3 分层输入、§4 输出 JSON、§5 真值与 EV 打分、§6 样本与标注环节）。
本仓库实现端到端工具链，并用 1 手真实牌（`items/hand_0001`，整手切片）完成**真实 API 跑通**：
豆包时间轴初稿 → deepseek-v4-pro L0/L1-text 各 3 trial → 豆包（provisional）L1-video 3 trial → 豆包幻觉 judge → EV 报表。

## 数据获取（视频素材不随仓库分发）

视频素材（YouTube 片段的切片/打码产物 `clip_*.mp4`、抽帧图片）因版权原因**不随本仓库分发**。仓库提供完整复现所需的全部元数据与工具链：

- `data/clips_manifest_merged.{json,csv}`：每手牌的 YouTube 视频 id 与切片起止秒（首尾帧已人工核对）；
- `items/<hand_id>/hand.json`：手牌事实与 `timing_abs_sec`（相对原视频的绝对秒）；
- 复现步骤：`pipeline/fetch.py` 按 manifest 用 yt-dlp 下载窗口并 ffmpeg 精确切片 → `pipeline/mask.py` 按 `configs/mask_*.json` 与 `hand.json mask_windows` 打码 → `pipeline/timeline.py` 生成时间轴初稿（或直接使用仓库内已校准的 `items/*/timeline.jsonl`）→ `pipeline/build_item.py` 组装评测输入。一键入口见下方 `run_all.sh`。

> 注：批跑结果与 published-results 待今日晚些更新。

## 一键跑通

```bash
cd readroom-bench
# 首次：建环境（无 brew/ffmpeg 也行，ffmpeg 来自 pip 包 imageio-ffmpeg）
~/.local/bin/uv venv .venv --python 3.11
~/.local/bin/uv pip install --python .venv/bin/python imageio-ffmpeg "yt-dlp>=2026.8" pillow numpy

bash run_all.sh hand_0001                      # 下载窗口→整手切片→打码→时间轴→item→单测→mock 链路验证
bash run_all.sh hand_0001 --local /path/raw_window.mp4   # 已有窗口文件时复用（秒级）
```

真实 API（.env 里 ARK_API_KEY / SYNAPSE_API_KEY+SYNAPSE_BASE，已 gitignore）：

```bash
.venv/bin/python -m pipeline.timeline --hand hand_0001            # 豆包看整手视频出时间轴初稿（1 次视频调用）
python3 annotator/server.py --port 8765                            # → http://localhost:8765/ 人工校准（四页签）
.venv/bin/python -m pipeline.build_item --hand hand_0001
.venv/bin/python -m runner.run --models deepseek --layers L0 L1-text --trials 3 --only hand_0001 --out results/runs.jsonl
.venv/bin/python -m runner.run --models doubao --layers L0 L1-video --trials 3 --only hand_0001 --out results/runs.jsonl
.venv/bin/python -m scoring.hallucination --runs results/runs.jsonl   # 豆包 judge（每题 1 次视频调用）
.venv/bin/python -m scoring.report                                    # → results/report.md（EV 主指标）
```

## 标注/校准工具（annotator/）

```bash
python3 annotator/server.py --port 8765    # 纯标准库，无依赖；浏览器开 http://localhost:8765/
```

四页签（左侧视频播放器贯穿，支持拖进度条）：
① **手牌信息核对**——truth.json 逐字段确认/修改，可一键重算胜率/EV，保存标 `human_verified_truth`；
② **时间轴校准**——豆包初稿逐条编辑/删/补，点条目视频跳到对应秒，禁情绪词实时标红，保存写回 timeline.jsonl（标 human_verified）并同步 timeline.txt 与 item.json；
③ **遮罩检查**——播放打码视频，标记泄露时间点，写 mask_review.json；
④ **cue 核验**——逐条显示模型 cue 与豆包 judge 判定，人工可改判（人工优先于 judge），统计抽检覆盖率（目标 10–20%）。

## 目录

| 路径 | 内容 |
|---|---|
| `pipeline/fetch.py` | yt-dlp 按 `hand.json` 窗口下载（不分发）+ ffmpeg 精确切**整手**片段 `clip_raw.mp4`（发牌→收池） |
| `pipeline/mask.py` | ffmpeg drawbox/boxblur 打码；模板 `configs/mask_1280x720.json`；支持 `hand.json mask_windows` 按时间段开启区域（翻前多行面板/广角漂浮标签） |
| `pipeline/timeline.py` | 行为时间轴初稿：豆包 doubao-seed-2-1-pro-260628（Ark，video_url data URL + fps + thinking disabled）看整手打码视频出事件行；禁情绪词自动校验；无 key → mock |
| `pipeline/equity.py` | 纯 Python 胜率枚举 + `truth()`（required_equity / correct_call / ev_call_bb） |
| `pipeline/build_item.py` | 组装 `item.json`（L0 / L1-text / L1-video 三层）与 `truth.json`（只给打分用） |
| `pipeline/frames.py` | 抽帧调度——**v0.2 起不在主链路**，仅供标注/人工核验按需使用 |
| `runner/providers.py` | 统一调用层（stdlib urllib）：五家被评 + doubao（Ark；provisional）；deepseek 走 Synapse 网关（SYNAPSE_BASE） |
| `runner/run.py` | 各层拼装输入、JSON schema 校验、n trial、`--mock`/`--dry-run`/`--ping`、trial 去重标记防网关缓存 |
| `scoring/metrics.py` | **EV 主指标**（score = p×EV(call)）、读人增益（bb）、oracle 上界、bootstrap CI；附录 Brier/ECE/一致性 |
| `scoring/hallucination.py` | 豆包 judge 对照整手视频批量核验 cue（每题 1 次视频调用）→ `results/hallucination.jsonl`；抽检标记 |
| `scoring/report.py` | jsonl → `results/report.md`（EV 主表 + 读人增益头条 + 幻觉核验 + 附录） |
| `annotator/` | 本地可视化标注工具（见上） |
| `prompts/` | `model_prompt.md`（五家同一份）、`timeline_prompt.md`（豆包整手视频版+禁情绪词）、`judge_prompt.md`（批量核验版） |
| `items/hand_0001/` | `hand.json`、`clip_masked.mp4`（整手 114.5s）、`clip_masked_2fps.mp4`、`timeline.{jsonl,txt}`、`timeline_meta.json`、`item.json`、`truth.json`、`mask_check/`；原片已 gitignore |
| `results/` | `runs.jsonl`（真跑）、`hallucination.jsonl`、`report.md`、`runs_mock.jsonl`/`report_mock.md`（链路验证） |

## 样例手牌 hand_0001（v0.2 整手切片）

Poker Night in America《Hellmuth's Home Game》Ep.28（YouTube `7uTMKGaG0Aw`）：
Nick Hellmuth AhKd UTG limp → Deeb Ts9s HJ raise；翻牌 8dAd2c bet/raise/call；转牌 7c check/bet/call；河牌 Qd check → Deeb all-in $5,450 → Nick 弃牌。
真值：hero_equity=1.0，required=34.0%，correct_call=True，EV(call)=+211.5bb（实际弃牌 → 结果口径与胜率口径相反，好题）。
**切片（原视频秒）**：468.0（b-roll 后该手首个牌桌镜头，HAND 15）→ 582.5（Deeb 收池完、583s 转场卡前），114.5s；all-in 相对切片 t=89.0，宣布 t=107.5。

## 决策记录

1–11（v0.1，保留）：yt-dlp ≥2026.08；ffmpeg 来自 imageio-ffmpeg；打码宽于框架列举（底池面板/outs 条也打）；全桌面板区域可配；时间戳取叠层前移 0.5–1s；抽帧数量；L1-vision 图片顺序；L1-video data URL；EV soft/hard 两口径；recognized 剔除；不分发原片。

v0.2 新增：

12. **整手切片窗口的定法**：从"b-roll 结束后该手首个牌桌镜头"到"收池完成、转场卡之前"（hand_0001 = 468.0–582.5s）。发牌动作本身在 b-roll 里没拍，以首个牌桌镜头为起点；含收池是为了让 L1-video 模型能自证"没用摊牌信息"（本手对手未亮牌，无泄露）。
13. **整手切片新增两处泄露区**（v0.1 短切片没有）：翻前左侧多行选手面板与广角镜头漂浮底牌标签（y≈130–720）、顶部 outs/blinds 条实际位于 y≈28–75（v0.1 的 0–40 框没盖住）。解法：`mask.py` 支持按时间段开区域（`hand.json mask_windows`，drawbox enable=between），`player_panels_tall` 只在 0–28s 开启，避免全程遮左侧人物；`top_strip` 加宽。打码后逐点抽帧人工核验通过。
14. **timeline 初稿输入用 2fps/960px 整手视频**（4.1MB，一次调用 71k prompt tokens）而非逐帧图：一次调用出全手时间轴，事件密度可控（长考段 1–2s/条），成本远低于 v0.1 的逐帧方案。fps 参数随 video_url 传给 Ark。
15. **deepseek-v4-pro 关思维链评测**（`thinking:{type:"disabled"}`，Synapse 网关实测支持）：开思维链时 16k token 都推理不完、content 为空、5 min/trial 且输出退化。现场如换官方 API 可重新评估。
16. **网关缓存防重**：相同请求 3 trial 会命中 Synapse 缓存（0.3s 返回、输出全同），runner 给每个 trial 的 user 文本追加一行 trial-id 去重标记（prompt 语义不变）。
17. **doubao 也跑 L0**：读人增益必须同模型对比，provisional 的 doubao L1-video 需要自己的盲答基线（纯文本调用，不占视频次数预算）。
18. **judge 每题一次视频调用批量核验全部 cue**（27 条一次判完），而非每 cue 一次；uncertain 不进幻觉率分母。
19. **视频调用预算**：本轮真跑合计 5 次（timeline 1 + doubao L1-video 3 + judge 1），上限 10。
20. **frames.py 退出主链路**：v0.2 删除 L1-vision 层，抽帧只在标注/人工核验需要时手动跑；hand_0001 旧抽帧产物已清理。
21. **timeline 初稿时间有漂移**（豆包把 all-in 推筹码记在 t≈99，实际 t≈89）：这正是人工校准环节要修的——初稿观感"结构可用、时间点需人工对齐"。

v0.2 批跑前冒烟（2026-08-22）新增：

22. **wodex 思考档位（赛规"最高档思考"）实测**：claude-opus-5 只认 OpenAI 风格顶层 `reasoning_effort`——带上后响应出现 `message.reasoning_content`；Anthropic 风格 `thinking:{type:"enabled",budget_tokens:N}` 被网关**静默忽略**（usage 与输出和 baseline 完全一致）。gpt-5.6-sol 对 `reasoning_effort:"high"/"xhigh"` 均不报错，但 usage 无 reasoning 细分、completion tokens 几乎不变，**无法证实档位真透传**——只能按"网关默认档位"对待。providers.py wodex 分支统一带 `reasoning_effort:"high"`，正式报告需注明 gpt 档位存疑这一限制。
23. **kimi-k3 视频输入：base64 data URL 直发即通**（T2 2fps 96.5s ≈2.8MB mp4，base64 后 body ≈3.8MB，prompt ≈34.7k tokens，实测通过）；moonshot 不认 `video_url.fps` 字段（kimi 分支已剥掉，仅 qwen/doubao 传 fps）；更大视频才需 `POST /v1/files`（purpose=video）→ `ms://<file_id>` 引用。k3 顶层 `reasoning_effort` 默认即 `max`，providers 已显式固定（temperature 恒为 1）。

## 已知问题 / 待办

- kimi L1-video 已实测通过（决策 23）；qwen 的 L1-video video_url 请求体仅 dry-run 组装、未实测。
- hand_0001 时间轴初稿**尚未人工校准**（human_verified=false，item.json 有标记）；正式跑分前须在 annotator 里过一遍（时间漂移见决策 21）。
- judge 判 false 比例较高（27 条里 18 条），需人工抽检确认 judge 自身的假阳性率（annotator 页签④，已标 15% 抽检样本）。
- 打码模板只针对该节目本赛季 1280×720 画面；换节目/换机位需重标坐标；mask_windows 时间段需每手人工定。
- 题数=1 时 bootstrap CI 退化；≥12 题才有意义。
- deepseek 关思维链的公平性问题（决策 15）现场再议。
