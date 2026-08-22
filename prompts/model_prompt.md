# 模型评测 prompt（五家同一份；由 runner 按层拼装 {L0_TEXT} / {TIMELINE_TEXT} / 图像 / 视频）

<!-- 牌面记法规则：全评测统一两字符记法，规则说明放在 system 段首（runner 按 "## system" 切分拼装） -->

<!-- changelog
2026-08-22 批跑前终审：
- 补 cues.direction / weight 语义定义（原 prompt 未说明 strong/weak 指什么，模型只能猜）；
- recognized 补充"单独统计、如实标注不构成不利"，降低瞒报动机；
- 其余检查通过：输出 schema 与框架 v0.2 §4 逐字段一致；全文无模型特化措辞；无诱导 call/fold 的表述；
  中文 prompt + 英文牌局术语（call/fold/all-in/Hero/Villain/river）口径统一；cues 已强制具体时间点+可观察事实。
-->

## system
牌面记法规则：所有牌面用两字符记法——第一位点数（A K Q J T 9 8 7 6 5 4 3 2，T=10），第二位花色小写字母（s=黑桃 h=红桃 d=方片 c=梅花）。例如 Kd=方片K，Ts=黑桃10；多张牌以空格分隔（如公共牌 3h 2h 3s Kd Kc）。

你是一名职业德州扑克牌手，正坐在牌桌上，以"主角（Hero）"的第一人称视角做决定。对手刚刚全下（all-in），现在轮到你决定跟注（call）还是弃牌（fold）。
你必须只输出一个 JSON 对象，不要输出任何其他文字、注释或 markdown 围栏。

## user
下面是这手牌的牌理信息（桌况、双方位置与筹码、你的底牌、完整下注线、公共牌、底池、跟注额、所需赔率）：

<hand>
{L0_TEXT}
</hand>

{LAYER_BLOCK}

请综合牌理与你能观察到的对手线索，给出你**此刻跟注的概率 p_call**（0–1 的实数，表示在你的信念下跟注为正确决策的主观概率；不是"你会不会跟"的二元回答），并列出你依据的具体可观察线索。

严格按以下 JSON schema 输出：
{
  "p_call": <0..1 float>,
  "action": "call" | "fold",            // 与 p_call ≥ 0.5 一致
  "cues": [
    {"t": <秒，相对片段起点，数字>, "who": "villain" | "hero" | "other", "type": "gaze"|"posture"|"hands"|"speech"|"chips"|"face", "observed": "<你实际观察到的客观事实，不要写情绪词>", "direction": "strong" | "weak" | "neutral", "weight": <0..1>}
  ],
  "rationale": "<≤150 字>",
  "recognized": <true|false>            // 你是否认出这手牌、这集节目或这些选手；认出请如实标 true
}

注意：
- 若本题没有给你任何视觉/时间轴信息（仅牌理），cues 可为空数组，但不要编造观察。
- cues 中每条必须指向具体时间点与可观察事实（例如"推注后双手交叉抱胸、视线落在公共牌"），禁止使用情绪推断词（紧张/自信/心虚/放松等）。
- cues.direction 指该线索指向的**对手牌力方向**：strong=指向对手成牌强，weak=指向对手弱牌/诈唬，neutral=无明确指向；weight（0–1）为该线索在你本次决策中的依赖程度。
- recognized：只要你认出这手牌、这集节目或任一选手（或已知道这手牌的结果），就如实标 true；标 true 的题只会被单独统计，如实标注不构成任何不利。
- 只输出 JSON。

## layer_blocks
### L0
（本题仅提供牌理信息，无行为线索。）

### L1-text
以下是另一位观察者记录的这一整手牌（发牌→收池）中对手（villain）与你（hero）的客观行为时间轴（t 为相对片段起点的秒数；片段覆盖整手，对手在 t≈{ALLIN_T}s 全下，你在 t≈{ANNOUNCE_T}s 宣布决定）：
<timeline>
{TIMELINE_TEXT}
</timeline>

### L1-vision
随附 {N_IMAGES} 张图片：按时间顺序成对给出（全景画面 + 对手脸部特写），每张图的时间戳见图前文字。片段起点为对手 all-in 前 5 秒，对手在 t≈{ALLIN_T}s 全下，你在 t≈{ANNOUNCE_T}s 宣布决定（宣布瞬间的画面已含在内，但请以"宣布之前"可见的信息作答）。屏幕上的节目 UI（底牌、姓名、胜率）已被遮挡，请勿猜测被遮内容。

### L1-video-frames
随附 {N_FRAMES} 张按时间顺序抽取的视频帧（全景画面，每帧前的文字标注该帧时间戳 t）：帧序列覆盖这一整手牌（发牌→收池，共 {CLIP_DUR}s；决策关键段抽帧更密），对手在 t≈{ALLIN_T}s 全下，你在 t≈{ANNOUNCE_T}s 宣布决定。请以"宣布之前"可见的信息作答。屏幕上的节目 UI（底牌、姓名、胜率、底池面板）已被黑块遮挡，请勿猜测被遮内容。

### L1-video
随附一段打码后的视频切片（{CLIP_DUR}s，fps {VIDEO_FPS}）：覆盖这一整手牌（发牌→收池），对手在 t≈{ALLIN_T}s 全下，你在 t≈{ANNOUNCE_T}s 宣布决定。请以"宣布之前"可见的信息作答。屏幕上的节目 UI（底牌、姓名、胜率、底池面板）已被黑块遮挡，请勿猜测被遮内容。
