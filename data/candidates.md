# 读人 Bench — 候选手牌清单（Hellmuth's Home Game Ep.1–30）

生成日期：2026-08-20；**修订：2026-08-21**（T7/T8/T9/T10/F7/F10 六手经 Byron 判定 trivial 淘汰，从 29 篇 recap 全量重挖后换入替补，旧手移入文末"已淘汰(trivial)"一节）。素材：Poker Night in America《Hellmuth's Home Game》（RFID 上帝视角、无解说），手牌事实全部取自 PokerNews 各集 recap（29 篇全部通读）；胜率为蒙特卡洛模拟（20k iter，`estimated`），底池赔率按 recap 下注额估算（`estimated`）。

**Trivial 判定口径（2026-08-21，Byron 裁定，入主名单必过筛）**：只用 hero 视角信息（自己底牌+赔率+行动线，不看对手底牌），若标准牌理答案共识度 >90%（超对/三条+ 面对中小 jam=必call；无对无听面对大 jam=必fold；KK 翻前=必call；所需赔率 <15%=必call），则判 trivial、无读人增量，不入主名单。每手需在记录中写一句非 trivial 判定理由。

**villain 配额放宽记录（2026-08-21）**：Texas Mike=4（T2/F1/F2/T7）、Dan Cates=4（T5/F3/F6/T10），超出 ≤3 约束。原因：TRUE 侧非 trivial 高质量手（bluff-catch、大池、长考）几乎全部以 TM/Cates/3Coin 为对手，不放宽无法凑满 4 手非 trivial TRUE；两人 Hendon 均可查。

**筛选口径**：对手 all-in（或事实上全下，即对手下注/加注覆盖主角剩余筹码）→ 主角只剩 call/fold；双方底牌 RFID 可见（recap 已给出）。`estimated_correct_call` = 决策时刻主角对对手实际底牌的胜率是否高于所需底池赔率（与主角实际选择无关）。胜率与所需赔率差 ≤8pp 的手列入"备选（borderline）"，不计入主名单。

**已知数据限制**（详见文末缺口说明）：① 所有集的 YouTube 视频均无章节数据、描述无 FEATURED HANDS 时间戳（yt-dlp 抽查 Ep10/19/29 确认），`chapter_ts` 一律以 recap 小节名 + 当集出手顺序定位，精确时间戳需看片补；② recap 文字无法区分实体推筹码 vs 口头宣布 all-in，`allin_type` 除 recap 明示口头者外均标 unknown（待看片确认）；已知口头宣布的手（如 Ep13 3Coin "All in" 宣布、Ep6 Hellmuth dark all-in 口头）已尽量排出主名单。

---

## 主名单（20 手：correct_call 真/假各 10）

### estimated_correct_call = TRUE（10 手）

| # | Ep | hero | villain | hero_cards | villain_cards | board（决策时） | street | pot/bet 概况 | equity vs 所需赔率 | think | hendon | 定位（chapter_ts） |
|---|----|------|---------|-----------|---------------|------|--------|--------------|--------------------|-------|--------|--------------------|
| T1 | 24 | Phil Hellmuth | Randy "3Coin" Sadler | 6h4h（暗三条 6） | Jc8d（顶两对） | Js8h6s-6d | turn | 3Coin 秒推 all-in $12,950，追 $12,050 赢 ~$27,150 | **91%** vs ~44% | **long（8+ 分钟，全系列最长 tank；实际弃牌=错）** | partial（villain 无记录） | recap §"8+ Minute Tank"（当集第 2 手；有独立剪辑 ZWxOh8NkikI，含 Matusow 手机被打飞名场面） |
| T2 | 19 | Dan "Jungleman" Cates | "Texas" Mike Moncek | JhJc | AcQc（A 高诈唬） | 2s4dTc-Kd-8h | river | TM 河牌超额 all-in 覆盖，call $58,775 赢 $162,850 底池 | **100%** vs ~36% | **long（tank 后 call，Hellmuth："that hand's going viral"）** | both | recap §"That Hand's Going Viral"（当集第 4 手） |
| T3 | 23 | Phillip "P3" Hellmuth III | Randy "3Coin" Sadler | Td9c（一对 9） | As8c（A 高，听牌落空） | 6d7s9h-2c-Kc | river | 3Coin all-in $3,100，call $3,100 赢 ~$10,900 | **100%** vs ~28% | **long（"I need to think about this"，被话术弃掉最好牌=错）** | partial | recap §"It Gonna Do What It Do"（当集第 2 手；Phil 先弃，P3 长考后弃） |
| T4 | 22 | Kelly Lucas (=Minkin) | DJ Washburn | QsTh（第二对） | Qd9d（听牌全落空 Q 高） | Td4dKs-8c-3s | river | Washburn 长考后 all-in，call off $11,825 赢 $33,425 | **100%** vs ~35% | short（hero 秒 call；villain tank）| partial（villain 无记录） | recap §"Hellmuth Impressed"（当集第 3 手；本集 YouTube 标题即 "Kelly Stuns table with Hero Call"） |
| T5 | 3 | Xuan Liu | Dan "Jungleman" Cates | AcTc（两对 T8） | Jd9d（J 高诈唬） | Ts8s4d-8s-Kd | river | Cates 河牌超额 all-in（覆盖 Xuan $16,475），call $16,475 赢 ~$41,275 | **100%** vs ~40% | **long（深 tank，最终抛卡牌保护器决定，弃牌=错，Cates 亮诈唬）** | both | recap §"Xuan Flips a Coin"（Ep3 第 1 手） |
| T6 | 28 | Nick Hellmuth | Shaun Deeb | AhKd（顶对顶踢） | Ts9s（听牌落空 T 高） | 8dAd2c-7c-Qd | river | Deeb 河牌诈唬 all-in 覆盖，call $5,450 赢 ~$16,000 | **100%** vs ~34% | unknown（弃牌后问父亲意见；Phil："I would not have folded that"） | partial（hero Hendon 未直接命中，2026 WSOP 有参赛记录） | recap §"Deeb Pushes Around Young Hellmuth"（当集第 2 手） |
| T7 | 15 | Jennifer Tilly | "Texas" Mike Moncek | AcKd（顶对顶踢） | QhTc（卡顺落空，纯诈唬） | Ad8c4d-9c-4s | river | TM 河牌 all-in $19,550（UI 实测），决策时 pot $53,350，call 后 $72,900 | **100%** vs ~27%（实测） | **long（实测 tank ~80s；"I'm not happy about this"+要精确计数）** | both | recap §"I'm Not Happy About This"（当集报道第 6 手，位于 $94K 池 F1 手之前）。⚠︎ villain TM 配额放宽第 4 手。非trivial：TPTK 面对大额河牌 jam 只是 bluff-catcher（对手 rep 三条+），共识远低于 90%，全靠读 TM 失控状态 |
| T8 | 1 | Dan "Jungleman" Cates | Phil Hellmuth | JsTs | 9s9h | —（翻前） | preflop | Cates 3-bet $1,800 后 Hellmuth 口头 jam $4,100（看片确认 "All right, I'm all in"，VTT 4:01），call $2,300 争 $8,950（跑两次均输） | **48.5%** vs ~26%（面板读数 54/46 疑读反，以 MC 为准） | short | both | recap §"The Tone Had Been Set"（当集报道第 1 手、剧中第 2 手）。非trivial：JTs 拿 2.9:1 面对 jam，vs AA 仅 18%、vs 宽范围 >35%，取决于对 speech-play jam 范围的读 |
| T9 | 22 | John Cerasani | Kelly Lucas | 7h7c（低于板面 9 的口袋对） | KcQh（纯诈唬） | 9h4h3c-9c | turn | Cerasani 下 $1,000 后 Kelly check-raise all-in（$4,600）覆盖；决策时 UI POT $10,325、call $3,600=hero 全下（实际 fold=弃错） | **86%** vs ~26%（UI 实测；胜率面板 88/12） | unknown | partial（hero 无 Hendon 记录，降级） | recap §"Kelly's All-In Bluff"（当集报道第 2 手）。非trivial：77 在 9943 双对板面对 check-raise jam 是纯抓诈决策（vs 成手全输、vs 诈唬 86%），无共识 |
| T10 | 19 | "Texas" Mike Moncek | Dan "Jungleman" Cates | 9h9c | AcQc | —（翻前） | preflop | TM 4-bet $6,300，Cates 口头 5-bet jam $26,775 total（看片确认 "Hmm, I'll go all in"），call $20,475 争 $54,350（中 set 赢） | **53%** vs ~38%（面板读数 51/49 疑读反，以 MC 为准） | short（实测决策窗 2s） | both | recap §"Will Texas Mike Set the Record?"（当集报道第 1 手）。⚠︎ villain Cates 配额放宽第 4 手。非trivial：99 面对 5-bet jam 需 38%，vs QQ+/AK 约 40%、vs AA/KK 19%，经典分歧手 |

### estimated_correct_call = FALSE（10 手）

| # | Ep | hero | villain | hero_cards | villain_cards | board（决策时） | street | pot/bet 概况 | equity vs 所需赔率 | think | hendon | 定位（chapter_ts） |
|---|----|------|---------|-----------|---------------|------|--------|--------------|--------------------|-------|--------|--------------------|
| F1 | 15 | Dan "Jungleman" Cates | "Texas" Mike Moncek | AdQc（两对成船皮） | KsTc（runner-runner 葫芦） | 3h2h3s-Kd-Kc | river | TM all-in $30,350，call 输 $94,475 底池 | **0%** vs ~32% | **long（tank 后 call，输当日最大池之一）** | both | recap §"Texas Mike vs. Cates in $94K Pot!"（当集最后大手） |
| F2 | 17 | Jennifer Tilly | "Texas" Mike Moncek | As8c（两对 A8） | KcQs（三条 Q） | Ad8hQd-Qh-4c | river | TM all-in $19,850，需 call $19,850 赢 ~$47,400 | **0%** vs ~42% | **long（弹回椅背、要精确计数、tank 后弃="生日当和平主义者"；弃牌=对）** | both | recap §"It's My Birthday!"（当集第 3 手） |
| F3 | 10 | Xuan Liu | Dan "Jungleman" Cates | JhJc（顶 set） | Td8d（坚果顺） | Js2h9h-7s | turn | Cates check-raise all-in $36,475，call $28,475 输 **$78,875（HHG 史上最大池）** | **23%** vs ~36% | short（"quickly called"） | both | recap §"Jungleman Calls Xuan's Hand"（当集第 1 手；官方剪辑 0EdVThqNqBY） |
| F4 | 22 | Phillip "P3" Hellmuth III | Randy "3Coin" Sadler | QhQc（口袋 Q 低于 A） | Ac7d（顶对） | Ah6d5h-8h-3c | river | 3Coin all-in 覆盖，call off $4,750 输 $13,425 | **0%** vs ~35% | **long（"thought long and hard"后 call）** | partial | recap §"P3 Felted in First Hand"（当集第 1 手） |
| F5 | 25 | Kane Kalas | DJ Washburn | KhQd（顶对+K 高同花听） | 7h6h（已成同花） | Ks4h8h-Jh | turn | Washburn all-in $7,225 into $8,750，call 输 $23,200 | **14%** vs ~31% | medium（"thought for a bit"） | partial（villain 无记录） | recap §"Running It Twice"（当集第 5 手） |
| F6 | 29 | Shaun Deeb | Dan "Jungleman" Cates | Ac7d（对 7+对 Q） | KhKd | Qd7s4h-Td-Qh | river | Cates all-in $14,025，call 输 $46,350 | **0%** vs ~30% | medium（"didn't take too long"） | both | recap §"Monster Pot in Final Hand"（当集最后 1 手） |
| F7 | 25 | Randy "3Coin" Sadler | Mike Matusow | Jc9d（转牌中第二对） | AdKc（顶对顶踢） | 3d5sAs-9c | turn | Matusow jam 覆盖，call off $3,375 输 $9,475 | **11%** vs ~36% | short（"didn't take long to call off"） | partial（hero 无记录，降级） | recap §"3Coin Needs to Reload"（当集第 1 手，开场）。非trivial：转牌刚中第二对面对覆盖 jam，是抓半诈/Ax 价值的读人决策，不落入"无对无听必弃"模式 |
| F8 | 18 | "Texas" Mike Moncek | DJ Washburn | AdQd | AsKs | —（翻前） | preflop | Washburn all-in $16,550，quick call $14,350 赢 $33,725（实际逆转赢） | **28%** vs ~43% | short（"quickly called"） | partial（villain 无记录） | recap §"Texas Mike Getting Lucky"（当集最后 1 手） |
| F9 | 20 | Mike Matusow | Phillip "P3" Hellmuth III | Ah7h（坚果同花听） | JsJd（顶 set；另有 3Coin 6h5h 亦 all-in） | 5sJh2h | flop | P3 all-in $7,775 + 3Coin 跟进，call off $8,825 输 $26,100 | **23%（三人局）** vs ~34% | unknown | both（第三人 3Coin 无记录） | recap §"Action Flop"（当集第 3 手；**三人 all-in**，主决策为 Matusow 末位 call off） |
| F10 | 26 | Xuan Liu | Phillip "P3" Hellmuth III | KsTc | AhKh | —（翻前，$200 double straddle） | preflop | P3 口头 limp-jam $3,750 total（看片确认 verbal），call $2,850 输 $8,050（board 干净跑完） | **25%** vs ~35% | medium（实测 tank ~25s；recap 仅 "opted to call"） | both | recap §"Big Slick Does the Trick for P3"（当集第 1 手）。非trivial：KTo 拿 1.8:1 面对小额 limp-jam，vs 随机范围可 call、vs 紧 limp-jam 范围必 fold，读 P3 范围构成决定答案 |

**YouTube URL 对照**（PNIA @Pokernight；Poker Brat TV 双发另注）：
Ep1 `0eoRd7AvZbY` · Ep3 `UDrb4M5MLKA` · Ep10 `0KBnOFtBXwg`（大手剪辑 `0EdVThqNqBY`）· Ep14 `gXLAM_iwgrg` · Ep15 `ohZ_QSDcXI8` · Ep17 `ktr12z8J3Ho`（PBTV 版 `FjTxfUoUw_s`；⚠︎ Tilly 生日手也可能在标题为 "Ep16" 的 `6bFs8KDB0BY` 内，YouTube 与 recap 集号疑有 ±1 错位，看片确认）· Ep18 `PAm_ci_ohz4` · Ep19 `Cs1ftCcWLng` · Ep20 `ifE0-Nfspso` · Ep22 `5ZOUgMDKYTs` · Ep23 `hpWIoK1lu9Q` · Ep24 `9TJWz24zhOw`（@Pokernight 补搜所得，原 TSV 缺）· Ep25 `LrNUV_Y8WfA` · Ep26 `V-0M0L_7tS0` · Ep27 `H1HJ0T6y1YE` · Ep28 `7uTMKGaG0Aw` · Ep29 `hyQuR-r-Owg`。

---

## 已淘汰（trivial，2026-08-21 Byron 判定）

原主名单 6 手因过不了 trivial 筛（hero 视角标准答案共识 >90%，无读人增量）被替换。完整字段保留于 `candidates.json` 的 `retired_trivial` 节。

| 原# | Ep | hero | villain | 概要 | equity vs 赔率 | trivial 判定理由 |
|----|----|------|---------|------|----------------|------------------|
| 旧T7 | 25 | Kelly Lucas | Phil Hellmuth | 6c4c 暗三条 call AA jam $4,750（slowroll 名场面） | 91% vs ~24% | 三条+面对中小 jam=必call，共识 >90% |
| 旧T8 | 29 | Shaun Deeb | Phil Hellmuth | TT call AQo 翻前 jam $2,350 | 57% vs ~43% | 中高口袋对面对翻前小额 jam 共识必 call，标准牌理无分歧 |
| 旧T9 | 14 | Jennifer Tilly | Kelly Minkin | AT 顶对+OESD call 转牌 jam，req ~10% | 32% vs ~10% | 所需赔率 <15%，任何两张牌必 call，纯赔率题 |
| 旧T10 | 27 | Erick Lindgren | Kelly Lucas | AA call 8c7c 翻牌 jam $2,350 | 68% vs ~35% | 超对面对中小 jam=必call，共识 >90% |
| 旧F7 | 24 | Phillip "P3" Hellmuth III | Mike Matusow | KK call AA 翻前 jam | 18% vs ~37% | KK 翻前=必call，读人无法翻转标准答案（纯 cooler） |
| 旧F10 | 23 | Randy "3Coin" Sadler | Kelly Lucas | ATo A 高 call off KK 翻牌 jam | 15% vs ~29% | 无对无听面对大 jam=必fold，共识 >90% |

对应旧切片文件在飞书 01 目录已重命名加前缀 `淘汰_`（未删除）。

## 备选表 A：borderline（胜率与所需赔率差 ≤8pp，不计入主名单）

| Ep | hero | villain | 牌面概要 | equity vs 所需赔率 | 说明 |
|----|------|---------|----------|--------------------|------|
| 18 | Dan Cates | Kelly Lucas | 7c2d call Ah8h 翻前 jam $3,725 | 30% vs ~27% | "crying call"，72o 名场面，margin +3pp |
| 26 | Xuan Liu | P3 | KsTc call AhKh limp-jam $3,750 | 25% vs ~35% | 实为 clear-false（-10pp），但 recap 赔率细节粗，保守放备选 |
| 28 | Xuan Liu | Erick Lindgren | QhJh call AcJc 翻前 jam $5,500 | 31% vs ~28% | recap 自述 "2-to-1 dog"，margin +3pp |
| 23 | Randy "3Coin" Sadler | Phil Hellmuth | Ac3h（gutshot 轮+A 高）call KcKs 翻牌 jam $2,525 | 27% vs ~24% | margin +3pp |
| 1 | Dan Cates | P3 | Ad4d 面对 QsQh jam $2,625，长考后弃 | 33% vs ~33% | margin ~0，教科书边缘 |
| 21 | Randy "3Coin" Sadler | Mike Matusow | JcTc（对+多重听）call off AhAd | 24% vs ~26% | margin -2pp |
| 4 | P3 | Randy "3Coin" Sadler | AdKd 三条 A snap-call 4hAhAs-6c 上 44 葫芦 | 16% vs ~18% | margin -2pp |
| 12 | Phil Hellmuth | Randy "3Coin" Sadler | KdQs OESD call off $2,600（多人池，villain JdTd 两对） | 33% vs ~24% | margin +9pp 但多人池主池副池难精算，降为备选 |

## 备选表 B：清晰但因配额/多样性/人物记录让位的手

| Ep | hero | villain | 概要 | 判定 | 未入主因 |
|----|------|---------|------|------|----------|
| 9 | 3Coin | Cates | JsTs 中对面对 AA 转牌 jam $16,625，**长 tank 后弃（对）** | FALSE（12% vs ~31%） | 3Coin 无 Hendon（降级）；villain Cates 配额满 |
| 13 | Cates | 3Coin | AhKc 三条 A call TT 葫芦（**villain 口头宣布 all-in**） | FALSE（16% vs ~35%） | verbal all-in；villain 3Coin 配额满 |
| ~~19~~ | ~~Texas Mike~~ | ~~Cates~~ | ~~9h9c call AcQc 5-bet jam $26,775（$54,350 池）~~ | ~~TRUE（53% vs ~38%）~~ | **2026-08-21 已转正为新 T10** |
| 19 | Cates | Texas Mike | Ts8s 三条+顺听 snap-call $46,000（$103K 池，河牌 chop） | TRUE（~85%） | TRUE 配额满 |
| 15 | Tilly | Texas Mike | AcKh call off $18,600 vs Ah4h 翻前（$40,450 池） | TRUE（70% vs ~44%） | TRUE 配额满 |
| ~~15~~ | ~~Tilly~~ | ~~Texas Mike~~ | ~~AcKd 顶对顶踢 tank-call 河牌诈唬 jam $19,500（$53,350 池）~~ | ~~TRUE（100%，长 tank）~~ | **2026-08-21 已转正为新 T7（villain TM 放宽到 4）** |
| 16 | Kelly Lucas | Phil Hellmuth | KhKs call JsJd 翻前 jam $4,975（slowroll） | TRUE（81% vs ~42%） | hero/villain 组合与 T7 重复 |
| 17 | Cates | Texas Mike | Kc6d 两对 call 河牌 jam $19,550（$55,400 池） | TRUE（100%） | 配额满 |
| 11 | Nevada | 3Coin | KsKd 面对 7s6h 河牌诈唬 jam，tank 后弃（错） | TRUE（100% vs ~37%） | 双方均无 Hendon 记录（no_record，降级） |
| 27 | Phil Hellmuth | Cates | Ad6s 顶对 snap-call 坚果顺 jam $1,750 | FALSE（~4% vs ~17%） | FALSE 配额满、池小 |
| 8 | Cates | Alex | KdQh 两对 call 河牌 jam $8,525 vs 5c4s 葫芦 | FALSE（0% vs ~25%） | villain "Alex" 无全名无记录（no_record） |
| 25 | 3Coin | Matusow | Jd9d 对 9 call off $3,375 vs AK 顶对 | FALSE（11% vs ~36%） | hero 无记录；FALSE 配额满 |
| 25 | 3Coin | Kelly Lucas | 7c6s 顺+同花听 call $5,175 vs 已成同花（河牌反超） | FALSE（23% vs ~37%） | 同上 |
| 25 | DJ Washburn | "Gorjess" | JdTs 对 J call check-raise jam $3,975 vs 两对（**长考**） | FALSE（9% vs ~49%） | villain 纯路人 no_record |
| 14 | Texas Mike | "Pink" | AdJc call 翻前 jam vs Ac2d（$10,150 池） | TRUE（~72%） | villain 无记录 |
| 20 | Phil Hellmuth | 3Coin | 7-4 转牌顺子 call off $3,675（recap 未列 hero 具体花色） | TRUE（~91%） | hero_cards recap 缺失 |

---

## 统计（主名单 20 手，2026-08-21 换血后）

**correct_call**：TRUE 10 / FALSE 10 ✓（TRUE 中含 5 手主角实际弃牌=弃错：T1/T3/T5/T6/T9；FALSE 中 1 手主角实际弃牌=弃对：F2——覆盖"该跟没跟/不该跟跟了"四象限）

**hero 分布**（≤4 约束满足）：Cates、Xuan Liu ×3；P3、Jennifer Tilly、Texas Mike ×2；Kelly Lucas、Phil Hellmuth、Nick Hellmuth、Shaun Deeb、Kane Kalas、Mike Matusow、3Coin、John Cerasani ×1。共 13 位不同主角（Erick Lindgren 随旧 T10 移出；新增 Cerasani）。

**villain 分布**：**Texas Mike ×4、Cates ×4（两处显式放宽，理由见文件头）**；3Coin、DJ Washburn ×3；P3 ×2；Phil Hellmuth、Kelly Lucas、Deeb、Matusow ×1。

**allin_type**（2026-08-21 全部看片确认，与 manifest 同步）：chips ×11 / verbal ×9。新 6 手中 T7/T9/F7 为推筹码，T8/T10/F10 为口头宣布（T8 "All right, I'm all in"、T10 "Hmm, I'll go all in"、F10 P3 "all in"）。

**think_duration**：long ×8（T1/T2/T3/T5/T7/F1/F2/F4）、medium ×3（F5/F6/F10 实测 ~25s）、short ×6、unknown ×3（T6/T9/F9）。长考手已尽量优先（T1 为 8+ 分钟全系列之最；新 T7 实测 tank ~80s）。

**hendon_ok**：both ×10；partial ×10（成因：3Coin/Randy Sadler、DJ Washburn、John Cerasani 查无 Hendon 记录——均为现金局网红/名人非锦标赛玩家，按口径降级使用并标注；Nick Hellmuth 有 2026 WSOP 参赛报道但 Hendon 页未直接命中）。无 none。已确认档案：Phil Hellmuth n=117、Erick Lindgren n=534、Kelly Minkin/Lucas n=287722（**同一人，婚后改姓**）、Texas Mike (Michael Moncek) n=511811、Kane Kalas n=165510、Phillip Hellmuth III n=428256；Cates/Liu/Tilly/Deeb/Matusow 为知名锦标赛选手无需赘证。

## 数据缺口与补充建议

1. **时间戳全缺**：全部视频无 YouTube 章节、描述无 FEATURED HANDS（抽查 3 集确认）。补法：按 recap 出手顺序（多为当集第 1/2/最后手）在片中快速定位；或跑 yt-dlp 字幕/自动字幕按台词（如 "I call"、"that's going viral"）对齐。
2. **Ep24 全集已补搜到**（`9TJWz24zhOw`，@Pokernight，2026-08-20 切片时确认）；Ep30 全集 URL 仍缺（本名单未取 Ep30 手牌，其 Deeb vs Tilly all-in 手 Tilly 为 55% 边缘可作机动替补）。
3. **allin_type 需看片核**：若 bench 严格要求"实体推筹码"，优先核 T1（"instantly moving all in"）、F3（check-raise all-in）、T2/F1/F2（Texas Mike 推注习惯）；备选表 B 中 Ep15 Tilly tank-call 手是最佳替换弹药。
4. **FALSE 侧 partial 偏多**（9 手 partial 中 6 手涉 3Coin/Washburn）：若需提高 hendon=both 比例，可用备选 B 中 Ep27 Hellmuth vs Cates、Ep19 两手 TRUE 做置换，但会牺牲 FALSE 配额或人物多样性；根本解法是引入 PNIA Classic Replay（ciz21VwoaUg）或其他 PNIA 老季（全职业阵容）补 FALSE 手。
5. **Ep16/17 集号错位风险**：YouTube 标题与 recap 集号疑差 1（Tilly 生日内容两边都出现），F2 定位前先看 `ktr12z8J3Ho` 与 `6bFs8KDB0BY` 两支确认。
6. **Ep14 "Hellmuth vs Hellmuth"、Ep19 "Can't Resist"、Ep20 "Collide"** 等手 recap 未给一方底牌，已弃用；如需可看片补录。
