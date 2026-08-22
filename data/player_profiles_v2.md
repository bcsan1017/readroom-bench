# 读人 Bench 选手画像库 v2（统一 schema）

生成：2026-08-21。基于 v1（`player_profiles.json`，原样保留）+ 自建 HHG 行为统计（`hhg_behavior_stats.{json,md}`）。完整结构化数据见 `player_profiles_v2.json`。

**Schema**：每人 = identity/record/style_public（v1 原样）+ **model_profile**（匿名化五维：松紧/激进/情绪外露/话痨/诈唬倾向，每维 level+一句话证据+信源级）+ **stats**（HHG recap 行为统计）+ **profile_depth**。

**profile_depth 评级规则**：rich = A/B 评价 ≥5 条 且报道手数 ≥20；thin = A/B 评价 ≤4 条 且报道手数 <10；其余 medium。

**统计口径限制**：recap 只报道每集精选手牌（每集 4-7 手），是有偏样本：偏向大池、all-in 对抗与戏剧性手牌，常规小池与无摊牌手基本不被记录。因此所有计数均为【下界】而非全量；『无记录』只说明 recap 未报道，不能推断该行为不存在。松紧度/入池率等频率类指标无法由本数据估计。续局集（Ep15/24/27/29/30 等）的 Profit 列为跨集累计口径，swing 记录时已尽量在证据中注明。所有统计严格取 recap 明文，不做推断。

**depth 分布**：rich ×7（Phil Hellmuth、Phillip Hellmuth III (P3)、Jennifer Tilly、Dan 'Jungleman' Cates、Kelly Minkin (Lucas)、'Texas' Mike Moncek、Randy '3Coin' Sadler）；medium ×6（Shaun Deeb、Xuan Liu、Erick Lindgren、Mike Matusow、DJ Washburn、Kane Kalas）；thin ×1（Nick Hellmuth）。

---

## Phil Hellmuth  `phil_hellmuth`  — profile_depth: **rich**

**匿名化画像**（喂模型用，v1 原文）：资深顶级职业牌手，多次世界级冠军，锦标赛战绩历史级。打法极紧且剥削型：前期只玩极少手牌，偏好小注、被动线与慢速节奏，把对手引入不熟悉的博弈分支后靠读人做非常规决定，自信读人能力极强。话极多，情绪外露到标志性程度，bad beat 后常当场发作、贬损对手；其好斗人设本身被分析者视为读牌工具——对手被激怒后的反应会泄露牌力。

**model_profile 五维**：

| 维度 | level | 证据 | 信源 |
|---|---|---|---|
| 松紧 looseness | 低 (low) | 极紧剥削型，前期只玩极少手数建立石头形象，被同行讥为'恐龙打法' | B |
| 激进 aggression | 低 (low) | 几乎总走被动线、小注、min-raise、极少 donk bet 的 trappy 风格 | B |
| 情绪外露 emotional | 高 (high) | 官方简介直书'脾气几乎和牌技一样出名'，bad beat 后当场发作是标志 | B |
| 话痨 table_talk | 高 (high) | 无解说节目'由其 table talk 撑起整档' | B |
| 诈唬 bluff_tendency | 中 (mid) | 本人自述曾单赛事'诈唬几百次'，但 HHG 30 集 recap 仅明文记录其诈唬 2 次（1 得手 1 被抓） | A/stats |

**stats（HHG，下界）**：出场 30 集 / 报道 56 手；全下 12 次、面对全下 17 次；诈唬被抓 1、诈唬得手(亮明) 1；hero call 0、大弃牌 2、长考 2；摊牌 17 胜 14 负。大额单集输赢：Ep5: +$17,575；Ep7: +$10,825；Ep8: +$25,525；Ep16: -20225；Ep22: 15275；Ep23: 12150；Ep24: 24600；Ep27: -20225；Ep30: -20000。

## Nick Hellmuth  `nick_hellmuth`  — profile_depth: **thin**

**匿名化画像**（喂模型用，v1 原文）：转职业不久的年轻牌手，公开战绩尚浅，明确偏好锦标赛胜过现金局。节目样本有限：敢于浅码全下，也出现过偏新手的激进操作（如中对领打后全下撞上超对被清空）；同时能在压力下做出大弃牌，且会当桌向更资深的牌手求教复盘。情绪低调温和，无失控记录，桌上话不多，输光离场时风度良好。风格画像整体样本量小，外推需谨慎。

**model_profile 五维**：

| 维度 | level | 证据 | 信源 |
|---|---|---|---|
| 松紧 looseness | 未知 (unknown) | 公开样本过小，无松紧口径评价 | B |
| 激进 aggression | 中 (mid) | 敢浅码全下（99 对 3-bet 直接推入），也有中对领打后全下撞超对的偏新手激进操作 | B |
| 情绪外露 emotional | 低 (low) | 低调温和，输光离场前拥抱对手，无失控记录 | B |
| 话痨 table_talk | 低 (low) | 桌上话不多，会当桌向资深者求教而非斗嘴 | B |
| 诈唬 bluff_tendency | 未知 (unknown) | 5 集样本无明文诈唬记录，样本不足定级 | stats |

**stats（HHG，下界）**：出场 5 集 / 报道 7 手；全下 4 次、面对全下 1 次；诈唬被抓 0、诈唬得手(亮明) 0；hero call 0、大弃牌 1、长考 0；摊牌 2 胜 3 负。大额单集输赢：Ep30: -10000。

## Phillip Hellmuth III (P3)  `p3_hellmuth`  — profile_depth: **rich**

**匿名化画像**（喂模型用，v1 原文）：金融行业多年后转型的牌手，公开战绩尚浅。敢打大池，有 limp-jam、超对顶到底等偏激进的操作记录；抓诈判断不稳定，既有自嘲式'我又要做一次可怕的 call'的倾向，也曾被对手桌面话术说动弃掉最好的牌。情绪整体克制冷静，媒体观察其无标志性发作做派，但本人承认极端 bad beat 下可能失控一次。性格直率敢言，有私局现金背景。

**model_profile 五维**：

| 维度 | level | 证据 | 信源 |
|---|---|---|---|
| 松紧 looseness | 中 (mid) | 敢打大池，有 limp-jam、超对顶到底记录，但非全场乱入型 | B |
| 激进 aggression | 中 (mid) | JJ 顶 set 三人全下扫双跑成当集最大赢家，敢于主动做大底池 | B |
| 情绪外露 emotional | 低 (low) | 媒体现场观察其'牌桌风格明显更冷静'，无标志性发作做派 | B |
| 话痨 table_talk | 中 (mid) | 性格直率敢言，会当桌自嘲'我又要做一次可怕的 call' | A |
| 诈唬 bluff_tendency | 未知 (unknown) | 21 集/29 手无明文主动诈唬记录（有被对手话术唬走的记录），偏样本下不定级 | stats |

**stats（HHG，下界）**：出场 21 集 / 报道 29 手；全下 7 次、面对全下 7 次；诈唬被抓 0、诈唬得手(亮明) 0；hero call 0、大弃牌 2、长考 2；摊牌 5 胜 8 负。大额单集输赢：Ep3-4: -$10,000；Ep20: 27925。

## Jennifer Tilly  `jennifer_tilly`  — profile_depth: **rich**

**匿名化画像**（喂模型用，v1 原文）：娱乐行业背景跨界的成名女牌手，有世界级赛事冠军头衔。自称行动型松凶玩家，偏爱现金局；把职业表演训练用于诈唬——诈唬时让自己'相信'手里是好牌以消除紧张 tell，读人依赖对肢体语言的长期职业观察。桌上话多且反击能力强，妙语连珠。公开自认弱点：对输大钱焦虑，可被大注压走；也曾自省因强行改打激进风格在关键局崩盘。

**model_profile 五维**：

| 维度 | level | 证据 | 信源 |
|---|---|---|---|
| 松紧 looseness | 高 (high) | 自称 action player，偏爱现金局与 six-max | A |
| 激进 aggression | 高 (high) | 画像口径 loose-aggressive、instinct-led，曾自省强行加档激进在决赛桌崩盘 | A |
| 情绪外露 emotional | 中 (mid) | 自认'对输钱焦虑、别人可以砸钱把我 bluff 走'，但受表演训练管理 tell | A |
| 话痨 table_talk | 高 (high) | 被评'能匹敌游戏中任何 talker 还经常反压过去' | B |
| 诈唬 bluff_tendency | 中 (mid) | 自述把表演训练直接用于诈唬（'bluff 时让自己相信手里是 AA'），但 HHG recap 33 手未记录其任何亮明诈唬（另有 3 次 hero call）——两源折中 | A/stats |

**stats（HHG，下界）**：出场 11 集 / 报道 33 手；全下 3 次、面对全下 14 次；诈唬被抓 0、诈唬得手(亮明) 0；hero call 3、大弃牌 1、长考 2；摊牌 9 胜 5 负。大额单集输赢：Ep14: 15075；Ep15: 43275；Ep16: 10075；Ep17: -11325；Ep26: 11925；Ep28: -14450；Ep30: 85125。

## Dan 'Jungleman' Cates  `dan_cates`  — profile_depth: **rich**

**匿名化画像**（喂模型用，v1 原文）：高额桌传奇职业牌手，线上线下均为顶级赢家，多次世界级冠军。极度激进，偏爱用投机连张 3-bet 诈唬，单挑风格是抢下一切可抢的底池；数据驱动、决策树记忆力极强。桌面形象怪异，曾多次角色扮演出镜；情绪外露极低，对巨额输赢淡然自嘲。会放话式垃圾话并兑现。读人重下注尺度与时序，认为物理 tell 不可靠但会观察对手的静止度、话量与脉搏变化。

**model_profile 五维**：

| 维度 | level | 证据 | 信源 |
|---|---|---|---|
| 松紧 looseness | 高 (high) | 自述爱用投机连张 3-bet；同桌职业选手当面吐槽其'打了 70% 的手牌' | A |
| 激进 aggression | 高 (high) | 自述单挑策略就是'尽量赢下所有能赢的底池'，极度激进 | A |
| 情绪外露 emotional | 低 (low) | 对巨额输赢淡然，输 $5M 仅发推自嘲 | B |
| 话痨 table_talk | 中 (mid) | 赛前放话式垃圾话与角色扮演式桌面形象，但非持续性话痨 | B |
| 诈唬 bluff_tendency | 高 (high) | 有专门讲诈唬的教学视频；HHG recap 明文记录其诈唬 4 次（1 得手 3 被抓），tank 7 次为全场最多 | A/stats |

**stats（HHG，下界）**：出场 23 集 / 报道 78 手；全下 11 次、面对全下 29 次；诈唬被抓 3、诈唬得手(亮明) 1；hero call 2、大弃牌 3、长考 7；摊牌 19 胜 13 负。大额单集输赢：Ep3-4: +$19,600；Ep5: -$26,700；Ep8: -$24,425；Ep9: 16525；Ep11: 14350；Ep13: -32275；Ep17: 53275；Ep18: 12350；Ep19: 94400；Ep27: 32475；Ep28: -18000；Ep29: -13650。

## Shaun Deeb  `shaun_deeb`  — profile_depth: **medium**

**匿名化画像**（喂模型用，v1 原文）：多次世界级冠军的全能型职业牌手，混合牌种专家，参赛量极大。超高强度激进加剥削型打法。话痨与挖苦是自我认证的武器：'永远在 needle、垃圾话、开玩笑'，公开宣称以此削减更强对手的优势；有慢摇激怒对手的著名场面，也与多名同行公开结仇互怼。读人自信极高，敢用极弱牌做英雄 call，自称巅峰期某牌种'地球最强'。输赢本身情绪淡定，表达偏自嘲。

**model_profile 五维**：

| 维度 | level | 证据 | 信源 |
|---|---|---|---|
| 松紧 looseness | 中 (mid) | hyper-aggressive 剥削型混合游戏专家，松紧随对手调整 | B |
| 激进 aggression | 高 (high) | 媒体口径 hyper-aggressive，敢持续对新手施压 | B |
| 情绪外露 emotional | 低 (low) | 输赢淡定自嘲式，夺冠后称'手链只是垫脚石'转身赶场 | B |
| 话痨 table_talk | 高 (high) | 本人自述'永远在 needle、垃圾话、开玩笑'以削减对手优势 | A |
| 诈唬 bluff_tendency | 高 (high) | 3 集样本即有 1 次亮明诈唬得手（河牌全下唬走顶对顶踢） | A/stats |

**stats（HHG，下界）**：出场 3 集 / 报道 8 手；全下 3 次、面对全下 4 次；诈唬被抓 0、诈唬得手(亮明) 1；hero call 0、大弃牌 0、长考 0；摊牌 2 胜 4 负。大额单集输赢：Ep28: 21950；Ep30: -80000。

## Xuan Liu  `xuan_liu`  — profile_depth: **medium**

**匿名化画像**（喂模型用，v1 原文）：多个国际大赛深码战绩与冠军头衔的女性职业牌手。自述'不是被动型玩家'，能打激进但有纪律自觉，曾公开自省因以攻对攻卷入不适的战斗而失利；公开鼓励竞争性打法，'拿走筹码不代表你是坏人'。职业心态成熟，重视身心管理，自认这一行非常消耗。公开形象冷静低调，无垃圾话相关报道，情绪外露程度低。近年重心转向电视现金局与内容输出。

**model_profile 五维**：

| 维度 | level | 证据 | 信源 |
|---|---|---|---|
| 松紧 looseness | 中 (mid) | 自述'不是被动型玩家'但有纪律自觉，非乱入型 | A |
| 激进 aggression | 中 (mid) | 能打激进，曾自省'以攻对攻卷入不舒服的战斗'是败因 | A |
| 情绪外露 emotional | 低 (low) | 公开形象冷静低调，无情绪失控报道 | B |
| 话痨 table_talk | 低 (low) | 无垃圾话相关报道（宁缺毋滥口径下未检索到反例） | B |
| 诈唬 bluff_tendency | 低 (low) | 18 集/32 手仅 1 次明文诈唬记录（被抓），无亮明得手 | stats |

**stats（HHG，下界）**：出场 18 集 / 报道 32 手；全下 3 次、面对全下 8 次；诈唬被抓 1、诈唬得手(亮明) 0；hero call 0、大弃牌 3、长考 2；摊牌 3 胜 7 负。大额单集输赢：Ep13: -22125。

## Erick Lindgren  `erick_lindgren`  — profile_depth: **medium**

**匿名化画像**（喂模型用，v1 原文）：成名于扑克黄金年代的职业牌手，多项巡回赛冠军与年度最佳头衔。注册商标是松凶，但自述实际打 small-ball：常 limp、偷小池、以多手数慢慢积累，等强牌被支付，关键时刻会刻意换挡；擅长针对对手类型反向调整——对被动者施压、对激进者设陷阱，自称不会把整个筹码 bluff 出去。情绪内敛，'从来不高不低'。场外赌性极重，有巨额 prop bet 与公开的债务破产史。

**model_profile 五维**：

| 维度 | level | 证据 | 信源 |
|---|---|---|---|
| 松紧 looseness | 中 (mid) | 注册商标是松凶，但自述实际打 small-ball：常 limp、偷小池、以多手数慢慢积累 | A |
| 激进 aggression | 中 (mid) | 反向适应型——对被动者施压、对激进者设陷阱，关键时刻刻意换挡 | A |
| 情绪外露 emotional | 低 (low) | 自述'我情绪从来不高不低'，夺冠才险些落泪 | A |
| 话痨 table_talk | 未知 (unknown) | 公开资料无桌面话量评价 | B |
| 诈唬 bluff_tendency | 低 (low) | 自称'不把整个筹码 bluff 出去、不过早摊牌' | A |

**stats（HHG，下界）**：出场 4 集 / 报道 8 手；全下 2 次、面对全下 1 次；诈唬被抓 0、诈唬得手(亮明) 0；hero call 0、大弃牌 0、长考 0；摊牌 2 胜 1 负。大额单集输赢：Ep28: 21700；Ep29: 17675；Ep30: 15200。

## Kelly Minkin (Lucas)  `kelly_minkin`  — profile_depth: **rich**

**匿名化画像**（喂模型用，v1 原文）：法律行业与扑克双轨的女性牌手，大型主赛多次深码战绩。以无畏英雄 call 和读人著称：敢用中对抓下大额诈唬全下，也敢用高牌 check-raise 全下反诈唬；整体偏松凶，宽范围防守，被评'桌上令人生畏'。对特定资深对手有多次戏剧性慢摇名场面，属娱乐性挖苦而非恶意。日常低调不喜聚光灯，公开自认利用'被低估'的形象优势，称本职工作与扑克的读人能力互相成就。

**model_profile 五维**：

| 维度 | level | 证据 | 信源 |
|---|---|---|---|
| 松紧 looseness | 中 (mid) | 偏松凶：敢用小连张 call 3-bet、straddle 位宽防守 | B |
| 激进 aggression | 中 (mid) | 敢用高牌 check-raise 全下反诈唬，被评'桌上令人生畏' | B |
| 情绪外露 emotional | 低 (low) | 自述不喜聚光灯、日常低调 | A |
| 话痨 table_talk | 中 (mid) | 对特定资深对手有多次戏剧性慢摇与娱乐性挖苦名场面 | B |
| 诈唬 bluff_tendency | 中 (mid) | 22 手样本有 1 次亮明诈唬得手（高牌 check-raise 全下）+ 1 次 hero call，抓诈比主动诈唬更突出 | B/stats |

**stats（HHG，下界）**：出场 14 集 / 报道 22 手；全下 7 次、面对全下 8 次；诈唬被抓 0、诈唬得手(亮明) 1；hero call 1、大弃牌 0、长考 1；摊牌 8 胜 4 负。大额单集输赢：Ep15: -17850；Ep16: 21025；Ep18: -20250；Ep19: 17450；Ep22: 28200；Ep24: -14400；Ep25: -14275；Ep26: -17700；Ep27: -20000。

## Mike Matusow  `mike_matusow`  — profile_depth: **medium**

**匿名化画像**（喂模型用，v1 原文）：老牌职业牌手，多次世界级冠军，多牌种技术底子公认被其公众形象低估。绰号直指其顶级话痨：垃圾话成名，曾在最高舞台怒喷对手。情绪极度外露，有以其名字命名的'崩盘'词条——关键节点容易因情绪连锁自爆，bad beat 后失去专注。策略高度依赖读对手物理 tell 与心理状态，在紧凶之间换挡。长期公开自认'run 得比谁都差'，并坦承过成瘾与心理健康史，公众形象两极。

**model_profile 五维**：

| 维度 | level | 证据 | 信源 |
|---|---|---|---|
| 松紧 looseness | 中 (mid) | 用 gears 系统在紧凶间切换，highly adaptive | B |
| 激进 aggression | 中 (mid) | 换挡型：依对手心理状态在紧凶间切换而非恒定高压 | B |
| 情绪外露 emotional | 高 (high) | 有以其名字命名的'崩盘'词条，bad beat 后失去专注、关键节点情绪连锁自爆 | B |
| 话痨 table_talk | 高 (high) | 绰号即来自顶级 trash-talk，曾在最高舞台怒喷对手 | B |
| 诈唬 bluff_tendency | 未知 (unknown) | 6 集/11 手无明文诈唬记录，样本不足定级 | stats |

**stats（HHG，下界）**：出场 6 集 / 报道 11 手；全下 2 次、面对全下 3 次；诈唬被抓 0、诈唬得手(亮明) 0；hero call 0、大弃牌 0、长考 0；摊牌 5 胜 1 负。大额单集输赢：Ep24: 12725。

## 'Texas' Mike Moncek  `texas_mike_moncek`  — profile_depth: **rich**

**匿名化画像**（喂模型用，v1 原文）：富商出身的高调娱乐型选手，也持有正规世界级赛事冠军头衔。极松极凶：直播现金局入池率曾达九成以上，自称'有义务娱乐观众、不当 nit'；诈唬倾向极强，深码大诈唬成名，也会变速偷鸡式慢打让对手直呼被偷袭。不用理论工具，纯靠直觉与临场感。情绪外露：输急后会出现绝望式全下，输大后公开炮轰职业圈；自述大底池时有明显的生理紧张反应。单日多次 rebuy 的巨亏场面是其标志。

**model_profile 五维**：

| 维度 | level | 证据 | 信源 |
|---|---|---|---|
| 松紧 looseness | 高 (high) | 直播现金局单场 VPIP 89%-99%，自称'有义务娱乐观众、不当 nit' | A |
| 激进 aggression | 高 (high) | 签名 'all gas, no brakes'，53o 三 bet 反超口袋 A 式打法 | A |
| 情绪外露 emotional | 高 (high) | 输急后绝望式全下、输大后公开炮轰职业圈，自述大底池有生理紧张反应 | A |
| 话痨 table_talk | 高 (high) | 高调娱乐型，直播局以表演性互动为卖点，获'最具娱乐性玩家'提名 | B |
| 诈唬 bluff_tendency | 高 (high) | HHG recap 明文记录其诈唬 5 次（1 得手 4 被抓），主动全下 14 次、6 集内 26 手为超高频出镜 | B/stats |

**stats（HHG，下界）**：出场 6 集 / 报道 26 手；全下 14 次、面对全下 6 次；诈唬被抓 4、诈唬得手(亮明) 1；hero call 1、大弃牌 0、长考 0；摊牌 6 胜 9 负。大额单集输赢：Ep14: -47200；Ep15: -63475；Ep17: -38225；Ep18: 29300；Ep19: -64250。

## Randy '3Coin' Sadler  `randy_3coin_sadler`  — profile_depth: **rich**

**匿名化画像**（喂模型用，v1 原文）：出售企业致富的高龄网红业余玩家，纯现金直播局人物，无锦标赛记录，直播局累计亏损近百万美元量级。公开评价称其'对诈唬上瘾'：松凶且黏，入池率六成以上，惯用数倍底池的超额全下与桌面话术施压，曾用话术让对手弃掉更好的牌，也曾用高牌全下同时唬走两名对手。有'只跑一次'的标志性习惯与多句口头禅。做派夸张爱镜头，但输钱从不失态、自嘲式复盘，主动找强手过招。

**model_profile 五维**：

| 维度 | level | 证据 | 信源 |
|---|---|---|---|
| 松紧 looseness | 高 (high) | 松凶且黏，大局 VPIP 65%，A 高也 call off 全部 | B |
| 激进 aggression | 高 (high) | 惯用数倍底池的超额全下施压（$10K 池全下 $84.7K） | B |
| 情绪外露 emotional | 中 (mid) | 做派夸张爱镜头，但输钱从不失态、自嘲式复盘 | B |
| 话痨 table_talk | 高 (high) | 话术是武器：曾用桌面话术让对手弃掉更好的牌，口头禅成节目梗 | B |
| 诈唬 bluff_tendency | 高 (high) | 被专栏评'对诈唬上瘾'；HHG recap 明文记录 5 次亮明诈唬得手（0 被抓），主动全下 20 次全场最多 | B/stats |

**stats（HHG，下界）**：出场 24 集 / 报道 66 手；全下 20 次、面对全下 16 次；诈唬被抓 0、诈唬得手(亮明) 5；hero call 0、大弃牌 2、长考 1；摊牌 14 胜 19 负。大额单集输赢：Ep3-4: -$14,050；Ep5: +$58,275；Ep11: -19600；Ep12: 12000；Ep14: -19225；Ep15: -24375；Ep17: -23500；Ep19: -22175；Ep20: -39000；Ep22: 28875；Ep23: -10425；Ep24: -11725；Ep25: 11475。

## DJ Washburn  `dj_washburn`  — profile_depth: **medium**

**匿名化画像**（喂模型用，v1 原文）：演艺/夜场行业背景的名人业余玩家，直播现金局常客，无锦标赛记录，累计小幅亏损量级。数据侧写偏松但比同桌娱乐型玩家克制（入池率四成多、加注率两成）；有跑桌式的激进日，也常打稳健价值路线，对乱全下的价值抓 call 能力在节目中多次可见。社区复盘提及其自信程度写在脸上——下注时表情随牌力变化，可能构成 tell。公开风格资料整体稀少，画像置信度较低。

**model_profile 五维**：

| 维度 | level | 证据 | 信源 |
|---|---|---|---|
| 松紧 looseness | 中 (mid) | 粉丝站数据 VPIP 46%/PFR 21%——偏松但比同桌娱乐型玩家克制 | C |
| 激进 aggression | 中 (mid) | 有跑桌式激进日，也常打稳健价值路线 | C |
| 情绪外露 emotional | 中 (mid) | 社区复盘称其自信写在脸上，下注表情随牌力变化（潜在 tell） | C |
| 话痨 table_talk | 未知 (unknown) | 公开资料无桌面话量评价 | C |
| 诈唬 bluff_tendency | 未知 (unknown) | 15 集/31 手仅 1 次明文诈唬（被抓），样本不足定级 | stats |

**stats（HHG，下界）**：出场 15 集 / 报道 31 手；全下 4 次、面对全下 9 次；诈唬被抓 1、诈唬得手(亮明) 0；hero call 0、大弃牌 1、长考 3；摊牌 7 胜 7 负。大额单集输赢：Ep3-4: +$41,750；Ep13: 14600；Ep17: 21850；Ep19: -26175；Ep21: 15250；Ep22: -47025。

## Kane Kalas  `kane_kalas`  — profile_depth: **medium**

**匿名化画像**（喂模型用，v1 原文）：播音与声乐背景的职业牌手兼赛事解说，高额现金局为主，曾参与创纪录量级的电视彩池。理论派技术型：公开形象是分析型而非表演型，制作过系统化教学内容。风格纪律性强、擅长设陷阱——强牌走被动线放对手开火、河牌快速 call；自述极度理性，把扑克当工作核算时薪、严格选桌，对输赢刺激本身不感兴趣。情绪外露低，无失控报道。口才是职业资产但桌上偏观察者，场外偶有大额 prop bet。

**model_profile 五维**：

| 维度 | level | 证据 | 信源 |
|---|---|---|---|
| 松紧 looseness | 低 (low) | 理论派 GTO 型，game selection 谨慎、把扑克当工作核算时薪 | B |
| 激进 aggression | 低 (low) | 纪律性强、擅长设陷阱：强牌走被动线放对手开火 | B |
| 情绪外露 emotional | 低 (low) | workman-like attitude，无公开 tilt/情绪失控报道 | B |
| 话痨 table_talk | 中 (mid) | 解说出身口才是职业资产，但桌上偏观察者形象 | A |
| 诈唬 bluff_tendency | 未知 (unknown) | 3 集/4 手无诈唬记录，样本极小 | stats |

**stats（HHG，下界）**：出场 3 集 / 报道 4 手；全下 0 次、面对全下 2 次；诈唬被抓 0、诈唬得手(亮明) 0；hero call 0、大弃牌 0、长考 0；摊牌 0 胜 1 负。大额单集输赢：Ep25: -12675。

---

## 外部量化数据源核实（2026-08-21，均未注册未购买）

| 数据源 | 覆盖结论 | 数据类型 | 价格 | URL |
|---|---|---|---|---|
| Hand2Note Live Poker Database | **确认覆盖 Poker Night In America**（官方频道列表 19 个频道明列 PNIA；HHG 由 PNIA 出品，但站方未逐节目列清单，HHG 单集是否已入库需购买后验证）；~99 万手、3.7 万选手，含全部底牌（含盖牌）与每手视频链接 | 行为（完整手史，可在 Hand2Note 4 客户端内算 VPIP/PFR 等全套指标；仅客户端内使用，非开放导出） | $499 一次性买断，含 1 年每日更新 + 1 个月 Pro（Pro 订阅本身不含此库） | https://hand2note.com/LivePokerDatabase |
| HighRollPoker Tracker（粉丝站） | **已在追踪 PNIA**：Cates 档案页有 Poker Night In America 分行（+$65,550 / 18 小时，PNIA 行未记 VPIP/PFR）；亦有 DJ Washburn（-$145K，VPIP 46%/PFR 21%）、3Coin（累计约 -$800K）等娱乐型选手页。HHG 是否并入 PNIA 行未标明 | 行为+盈亏（按节目分列 Net/VPIP/PFR/时长/时薪），站方自注"仅含直播局，非全量" | 免费 | https://highrollpoker.com/tracker/players/32 （Cates）；/players/1412（Washburn） |
| HighStakesDB | 覆盖 **Cates**（jungleman12/w00ki3z，线上现金 $11M+ 盈利口径即出自该库，2007 年起手史/重放）；Hellmuth/Deeb 非线上高额现金常客，无有价值档案 | 成绩（线上高额现金盈亏、手牌重放）+ 新闻 | 免费 | https://highstakesdb.com |
| SharkScope / PocketFives | **Deeb 可查**：PocketFives 档案存在（曾四度全球排名第一，ID shaundeeb/tedsfishfry）；SharkScope 为线上 MTT 追踪（免费每日限量查询，完整需订阅）；Hendon Mob 另有 Deeb "Online Results (472)" 页。对本节目其余 13 人无量化价值 | 成绩（线上锦标赛量/盈亏/ROI），非行为 | PocketFives 免费；SharkScope 免费限量/订阅制 | https://www.sharkscope.com ；https://www.pocketfives.com |
| GPI (Global Poker Index) | 职业 7 人均有档案页；现役量最大的 **Deeb 当前在 GPI-300 榜内（约 #120；PokerNews 快照曾列 38th）**，其余（Hellmuth/Cates/Tilly/Liu/Lindgren/Matusow）多数不在前列或积分低 | 成绩型排名（近 3 年锦标赛表现积分），无行为数据 | 免费查询 | https://www.globalpokerindex.com/gpi-300/ |
| Reddit / 粉丝统计贴 | **未发现**任何针对 HHG/PNIA 的独立粉丝统计项目（Reddit 搜索无 HHG VPIP/统计贴）；唯一近似物即上行 HighRollPoker Tracker | — | — | — |

**结论**：HHG 行为量化的最佳外部源是 Hand2Note LPD（$499，PNIA 在列但 HHG 覆盖待验证）；免费替代是 HighRollPoker Tracker（已有 PNIA 分行但粒度粗）。本仓库自建的 recap 统计（hhg_behavior_stats.json）仍是目前唯一按 HHG 逐集、逐行为口径的数据。
