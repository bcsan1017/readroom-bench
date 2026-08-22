# cue 人工抽检清单（251/1673 ≈ 15%；每模型×层 ≥2 条，judge=false 优先）

> 口径（Byron 拍板，2026-08-23）：cue 真实性判定由豆包 judge 自动完成（true/false/uncertain 三档）；
> 标注人在时间轴人工校准过程中已核阅全部视频素材，未设置独立的 cue 抽检环节。本清单保留生成，供事后复核参考。

如需复核：在 annotator/ 页签④逐条核对，人工改判写回 hallucination.jsonl 的 human.exists（人工优先于 judge）。

| # | item | model | layer | trial | t | who/type | observed | judge | evidence |
|---|---|---|---|---|---|---|---|---|---|
| 1 | F1 | claude | L1-text | 1 | 168.5 | villain/posture | villain全下后恢复靠椅背坐姿，双手放桌沿，持续直视hero方向，无多余动作 | False | t≈168.5s时，villain没有靠回椅背、持续直视hero的动作，他仍低头看向桌面方向。 |
| 2 | F1 | claude | L1-video | 0 | 166 | villain/posture | all-in推筹码后身体保持稳定正坐，双手平放桌上，未出现后仰或侧倾 | False | t≈166s时villain正在推筹码，推完后没有保持正坐双手平放桌上，他低头朝向筹码。 |
| 3 | F1 | claude | L1-video | 1 | 168 | villain/face | Villain (orange T-cap, right side of split screen) stares st | False | t≈168s时戴橙帽的villain低头，并非直视前方公共牌区域，无法确认其表情固定中性严厉。 |
| 4 | F1 | claude | L1-video | 1 | 90 | hero/face | At the flop (3h 2h 3s visible on the board), Hero has a rela | False | t≈90s时hero单手撑头低头，无法观察到其放松的表情看牌面。 |
| 5 | F1 | claude | L1-video | 2 | 156 | villain/chips | villain将全部剩余筹码推入底池中央，执行all-in动作 | False | t≈156s时是转牌下注后刚要发河牌，villain尚未将全部筹码推入底池，全下在167s左右。 |
| 6 | F1 | claude | L1-video | 2 | 156 | villain/posture | villain推筹码后身体前倾，双手放在桌上，保持静止注视前方 | False | t≈156s时villain没有前倾双手放桌上静止注视前方的动作，他低头看向桌面。 |
| 7 | F1 | deepseek | L1-text | 2 | 79.5 | villain/face | hero跟注后，villain抬手用手背蹭了一下鼻子 | False | t≈79.5s时抬手的是戴橙帽的玩家（非蹭鼻子动作），花衬衫villain没有蹭鼻子动作。 |
| 8 | F1 | gpt | L1-text | 0 | 30.5 | villain/posture | villain双臂交叉，右手持续拨弄绿色筹码思考 | False | t≈30.5s时双臂交叉拨弄绿色筹码的是戴橙帽的玩家，该时段花衬衫villain单手撑头，没有双臂交叉拨筹码。 |
| 9 | F1 | gpt | L1-text | 0 | 100.0 | villain/gaze | villain先快速看向hero一眼，随后推出$2600下注 | False | t≈100s时推出筹码的是橙帽玩家，不是花衬衫villain，且没有看hero的动作。 |
| 10 | F1 | gpt | L1-text | 0 | 124.0 | villain/posture | villain身体前倾，双前臂贴在桌沿，分出一摞下注筹码 | False | t≈124s时是橙帽玩家在摆弄筹码，花衬衫villain单手撑头，没有前倾分筹码。 |
| 11 | F1 | gpt | L1-text | 0 | 172.0 | villain/hands | villain双手放在桌沿，持续看向hero方向，等待期间没有额外动作 | False | t≈172s时villain（橙帽）低头，没有双手放桌沿持续看hero无动作的状态。 |
| 12 | F1 | gpt | L1-text | 2 | 165.0 | villain/chips | 身体大幅前倾，用右手将全部剩余筹码拢到一起 | False | t≈165s时villain没有大幅前倾用右手拢起全部筹码的动作。 |
| 13 | F1 | gpt | L1-video | 2 | 166 | villain/chips | 视线下移，双手同时伸向面前筹码并开始归拢 | False | t≈166s时villain是单手伸向筹码拢筹码，并非双手同时伸向筹码开始归拢。 |
| 14 | F1 | kimi | L1-text | 0 | 100.0 | villain/gaze | flop下注前先快速看了hero一眼，随后推出筹码 | False | t≈100.0附近，villain推出筹码前没有快速看向hero的动作，视线朝下 |
| 15 | F1 | kimi | L1-text | 0 | 127.0 | villain/gaze | turn下注推出筹码后持续看向hero方向直至hero行动 | False | t≈127.0附近，villain推出筹码后低头，没有持续看向hero方向 |
| 16 | F1 | kimi | L1-text | 0 | 162.0 | villain/posture | 河牌发出后上身挺直端坐，双手放桌沿、左手手指搭在筹码上，全程未说话，面部无明显表情变化 | False | t≈162.0附近，villain上身前倾、手搭在筹码上，并非挺直端坐、双手放桌沿的状态 |
| 17 | F1 | kimi | L1-text | 0 | 165.5 | villain/chips | 大幅前倾，右手将面前全部剩余筹码收拢后一次性推出完成全下，动作连贯无停顿 | False | t≈165.5附近，villain没有大幅前倾收拢全部剩余筹码一次性推出的动作，仅单手推出筹码 |
| 18 | F1 | kimi | L1-text | 1 | 30.5 | villain/posture | 4-bet前双臂交叉、右手拨弄筹码思考约11秒后才数筹推出$5,600 | False | t≈30.5附近，villain没有双臂交叉、右手拨弄筹码思考11秒后推出$5600的动作，4-bet的筹码动作与描述不 |
| 19 | F1 | kimi | L1-text | 2 | 79.5 | villain/hands | 翻前hero跟注其4bet后，抬手用手背蹭了下鼻子 | False | t≈79.5附近，villain没有抬手用手背蹭鼻子的动作 |
| 20 | F1 | kimi | L1-text | 2 | 41.5 | villain/hands | 翻前面对$2500的3bet，双臂交叉拨弄筹码思考约11秒后数出筹码4bet到$5600 | False | t≈41.5附近，villain没有双臂交叉拨弄筹码思考11秒后数筹码4bet到$5600的动作，4bet动作发生时间与 |
| 21 | F1 | kimi | L1-video | 0 | 9 | villain/face | 翻前加注后右手抬至鼻/嘴部摩擦，视线落在自己筹码上 | False | t≈9s附近，villain（橙帽男子）没有右手抬至鼻/嘴部摩擦的动作，该动作是戴LA蓝帽的白胡子男子做出的 |
| 22 | F1 | kimi | L1-video | 0 | 35 | villain/chips | 面对hero的3-bet，双手反复整理、切量筹码约10秒后推出4-bet | False | t≈35s附近，villain没有双手反复整理、切量筹码约10秒后推出4-bet的动作，数筹码的是白胡子男子 |
| 23 | F1 | kimi | L1-video | 1 | 170 | villain/posture | 全下后 villain 前臂平放桌沿、双手静止、帽檐压低、视线固定在公共牌区域，此后 60 秒以上无姿势变化 | False | t≈170s之后，villain有手部动作，并非前臂平放桌沿、双手静止60秒以上无姿势变化，且视线并非固定在公共牌区域 |
| 24 | F1 | kimi | L1-video | 2 | 97 | villain/chips | 翻牌 3h2h3s 发出、hero 过牌后，villain 右手取码一次性前推下注（底池 $11,775→$14,375 | False | t≈97s附近，flop下注是villain用单手推出筹码，并非右手取码一次性前推动作连贯无停顿，且下注额对应底池变化时 |
| 25 | F1 | qwen | L1-text | 0 | 192.0 | villain/face | 听到别人问他有什么牌时微微一笑 | False | t≈192s时画面是全景桌景，villain（橙T帽）侧头和旁边女士说话，没有被拍到听到问牌后微微一笑的动作，且此时镜头 |
| 26 | F1 | qwen | L1-text | 1 | 172.0 | villain/posture | 保持靠椅背、双手桌沿无额外动作，持续看向hero方向 | False | t≈172s时villain没有靠椅背持续看hero，视线朝下。 |
| 27 | F1 | qwen | L1-text | 2 | 79.5 | villain/hands | hero完成跟注后，villain抬手用手背蹭了下鼻子 | False | t≈79.5s时做蹭鼻子动作的是hero，不是villain。 |
| 28 | F1 | qwen | L1-video | 0 | 167 | villain/chips | river 双手一次动作将整叠筹码推过下注线，未数筹、未口头声明 | False | t≈167s时villain仅推出部分筹码，没有双手推整叠筹码过下注线，也不是全下动作。 |
| 29 | F1 | qwen | L1-video | 0 | 190 | villain/gaze | Hero 长考期间对手视线停留在 Hero 方向，全程未低头翻看自己的底牌 | False | t≈190s全景画面里villain侧头和旁边女士说话，并非全程视线停留在hero方向，也无法确认他没看底牌。 |
| 30 | F1 | qwen | L1-video | 2 | 28 | villain/hands | 左手仍托头靠在扶手上，右手单手抓筹完成加注，全程未抬头看对手 | False | t≈28s时左手托头的是hero（花衬衫反帽），不是villain，此时加注的也不是villain。 |
| 31 | F2 | claude | L0 | 1 | 0 | hero/chips | 转牌回应对手下注$2,000，河牌面对$19,850全下仅剩决策筹码 | False | t=0处于手牌刚开始发牌阶段，远未到转牌、河牌，不存在转牌下注$2000、河牌全下的对应事实。 |
| 32 | F2 | claude | L1-text | 1 | 88 | hero/chips | hero在河牌自己的行动上双手不碰筹码保持静止，对对手的强势下注示弱 | False | t=88附近，hero的手放在筹码区域，并非双手不碰筹码静止，且“示弱”属于意图判断，无可观察对应事实。 |
| 33 | F2 | claude | L1-text | 2 | 91.0 | villain/chips | villain前倾，将整摞深色筹码全部推入底池 | False | t=91附近，是hero推出筹码，villain没有前倾推整摞深色筹码入池的动作。 |
| 34 | F2 | claude | L1-text | 2 | 145.0 | hero/hands | hero将自己的两张牌向前推出扣在桌面，做出开牌动作观察对手表情 | False | t=145附近，hero（戴橙色帽子的玩家）没有将自己的牌推出扣在桌面开牌，是villain摊开了自己的牌。 |
| 35 | F2 | claude | L1-video | 0 | 87 | villain/hands | Villain pushes a large stack of chips forward in a smooth co | False | t=87附近，没有观察到villain推大摞筹码做all-in的动作，推筹码的是hero。 |
| 36 | F2 | claude | L1-video | 1 | 85 | villain/posture | villain双手将面前筹码全部推过下注线，身体姿态保持前倾未变化 | False | t=85附近，没有观察到villain双手将面前筹码全部推过下注线、身体前倾的动作。 |
| 37 | F2 | claude | L1-video | 2 | 72 | villain/chips | villain在turn面对$2,000下注后正常跟注，双手平稳将筹码放入底池，未表现出犹豫或反复查看手牌 | False | t=72附近，跟注转牌下注推出筹码的是hero，不是villain，且喝水的是其他玩家。 |
| 38 | F2 | deepseek | L1-text | 2 | 90.6 | villain/speech | 说“All in”后前倾将整摞深色筹码全部推入底池 | False | t=90.6附近，villain没有说All in，也没有前倾推整摞深色筹码入池。 |
| 39 | F2 | gpt | L1-text | 0 | 103.0 | villain/face | 全下后转头看向Hero又转向左侧，嘴角上扬并露齿，同时开口回应 | False | t=103超出视频时长（视频总时长约91秒），不存在对应画面。 |
| 40 | F2 | gpt | L1-text | 1 | 93.0 | villain/face | 全下后持续保持嘴角上扬、露齿的表情 | False | t=93附近，villain没有持续保持嘴角上扬露齿的表情。 |
| 41 | F2 | gpt | L1-text | 1 | 122.0 | villain/chips | 前倾整理剩余筹码，并把部分筹码码齐在下注区旁 | False | t=122超出视频时长（视频总时长约91秒），不存在对应画面。 |
| 42 | F2 | kimi | L1-text | 0 | 103 | villain/face | 全下后hero长考期间保持露齿微笑，转头看向hero又转向左侧，左手轻敲桌沿并开口回应约2秒 | False | t=103附近戴黑帽的男子（Hellmuth）转头看向左侧，没有保持露齿微笑看向hero，也没有左手轻敲桌沿开口回应2秒 |
| 43 | F2 | kimi | L1-text | 1 | 14.0 | villain/face | 放下底牌后靠向椅背看向hero，嘴角上扬露齿，随后对hero的600加注做3-bet到1800 | False | t=14附近戴黑帽的男子放下底牌后没有靠向椅背看向hero露齿笑，且3-bet到1800的动作不是在t=14附近发生，此 |
| 44 | F2 | kimi | L1-text | 1 | 103.0 | villain/face | hero长考期间villain保持露齿微笑，转头看向hero，左手轻敲桌沿并开口回应约2秒 | False | t=103附近戴黑帽的男子没有保持露齿微笑看hero，也没有左手敲桌沿回应，此时他转头看向画面左侧，动作不符。 |
| 45 | F2 | kimi | L1-text | 2 | 14 | villain/face | 翻前查看底牌后靠向椅背，看向hero，嘴角上扬露齿 | False | t=14附近戴黑帽男子查看底牌后没有靠向椅背看向hero露齿笑，他此时低头，身体前倾。 |
| 46 | F2 | kimi | L1-video | 1 | 88 | villain/chips | 河牌 hero 过牌后，villain（橙色T帽）随即将全部筹码一次性推入池中，动作连贯、无停顿或迟疑 | False | t=88附近推全部筹码入池的是戴橙帽的hero，不是villain，且橙帽是hero不是villain，主体错误。 |
| 47 | F2 | kimi | L1-video | 1 | 79 | villain/chips | 转牌 hero 下注后，villain 推出两枚黄色筹码跟注，动作平稳、无多余动作 | False | t=79附近推出两枚黄色筹码跟注的是橙帽hero，不是villain，主体错误。 |
| 48 | F2 | kimi | L1-video | 1 | 150 | villain/face | 旁桌玩家说话引发笑声时 villain 跟着笑，随后恢复低头看筹码的姿势 | False | t=150附近笑的是橙帽男子和绿衣男子，戴黑帽男子在画面左侧没有跟着笑后低头看筹码，他转头看向左侧。 |
| 49 | F2 | kimi | L1-video | 2 | 90.5 | villain/chips | 河牌圈双手将面前全部筹码推入池中，底池显示由 $7,650 跳至 $27,700（约 2.6 倍底池的全下） | False | t=90.5附近推全部筹码让底池跳到$27,700的是橙帽hero，不是villain，主体错误。 |
| 50 | F2 | qwen | L1-text | 0 | 90.6 | villain/speech | 开口说 All in | False | t=90.6附近是戴橙色帽子的hero推出筹码下注，villain（黑衣女）未开口说All in，且视频总时长约171秒 |
| 51 | F2 | qwen | L1-text | 0 | 103 | villain/face | 转头看向hero后又转向左侧，左手轻敲桌沿，嘴角上扬露齿 | False | t=103附近，villain（黑衣女）转头看向左侧的黑衣帽男，左手轻敲桌沿、嘴角上扬露齿，但没有转头看向hero的动作 |
| 52 | F2 | qwen | L1-text | 1 | 87.0 | villain/hands | 左手放在筹码堆上，右手搭在桌沿，视线落在面前牌桌区域 | False | t=87附近，左手放在筹码堆、右手搭桌沿的是戴橙色帽子的hero，不是villain |
| 53 | F2 | qwen | L1-text | 1 | 122.0 | villain/chips | 将剩余黄色筹码码成三摞，把深色筹码拢堆，持续整理至约 136 秒 | False | t=122到136秒期间码放黄色、深色筹码的是戴橙色帽子的hero，不是villain |
| 54 | F2 | qwen | L1-text | 1 | 154.0 | villain/hands | 对 hero 摆手说话约 4 秒，随后靠回椅背 | False | t=154附近villain没有对hero摆手约4秒后靠回椅背的动作 |
| 55 | F2 | qwen | L1-text | 2 | 14.0 | villain/posture | 放回底牌后靠向椅背，看向hero，嘴角上扬露齿 | False | t=14附近画面中戴黑帽黑衣的男子放回底牌后靠向椅背，但该人物不是全下的villain（黑衣女），且未看向hero露齿笑 |
| 56 | F2 | qwen | L1-text | 2 | 87.0 | villain/hands | 左手放在自己筹码堆上，右手搭在桌沿，视线落在面前牌桌区域，未说话 | False | t=87附近左手放在筹码堆、右手搭桌沿的是hero，不是villain，无法确认villain未说话 |
| 57 | F2 | qwen | L1-video | 0 | 88 | villain/chips | river 将整摞筹码一次性连续推入底池完成全下，动作中途无停顿、无数筹 | False | t=88附近是戴橙色帽子的hero推出筹码，villain没有将整摞筹码一次性推入底池全下的动作 |
| 58 | F2 | qwen | L1-video | 1 | 80.0 | villain/chips | 单手推出筹码跟注 turn $2,000，动作一次完成，随即收回手放在自己筹码堆上 | False | t=80附近推出筹码跟注的是戴橙色帽子的hero，不是villain |
| 59 | F2 | qwen | L1-video | 1 | 88.0 | villain/chips | 将整堆筹码向前推过下注线（全下），随后上身靠回椅背，双臂搭在桌沿 | False | t=88附近推筹码全下的不是villain，villain也没有随后靠回椅背双臂搭桌沿的对应动作 |
| 60 | F2 | qwen | L1-video | 2 | 80 | villain/chips | turn 面对 $2,000 下注，单叠筹码前推跟注，未加注 | False | t=80附近推筹码跟注的是hero（戴橙帽男子），不是villain |
| 61 | F3 | claude | L1-text | 0 | 151.0 | villain/speech | villain 反复声称自己范围里有大量 nut 组合（pocket twos、nine-two suited、doub | False | t=151附近画面中villain在喝饮料，未出现声称自己有大量nut组合、说‘我觉得在这里我有点被冷落’的对应语音/字 |
| 62 | F3 | claude | L1-text | 2 | 286.5 | villain/chips | villain 开口说 all in 后，约1.5秒内右手将一摞筹码平稳推出至牌桌中央完成全下，动作利落无犹豫 | False | t=286.5附近villain推出筹码时，没有出现他先说all in的对应语音/字幕，推出筹码动作存在但前置说all  |
| 63 | F3 | claude | L1-text | 2 | 174.0 | villain/posture | villain 身体前倾看向 hero 推出的筹码，手指轻敲桌面后停止说话，低头看底牌、手指摩挲牌边 | False | t=174附近villain没有身体前倾看hero筹码、手指敲桌后停止说话再低头摩挲底牌的动作，此时他手放在底牌区域，没 |
| 64 | F3 | claude | L1-video | 1 | 90 | villain/posture | Villain leans back in chair and takes a long drink from a wa | False | t=90附近是翻牌圈hero下注后，不是转牌下注阶段，且此时villain在喝水但身体没有后仰靠在椅背上，是坐着喝水的姿 |
| 65 | F3 | claude | L1-video | 2 | 234 | villain/face | Villain maintains neutral facial expression after shoving al | False | t=234在全下之前，villain还在数筹码，没有完成全下，他低头看向筹码，无法确认中性表情、嘴唇闭合无笑意紧张的状态 |
| 66 | F3 | deepseek | L1-text | 0 | 100.0 | villain/speech | 说"all right i'll call"并完成翻牌跟注 | False | t=100附近画面中没有出现villain说"all right i'll call"的对应语音/字幕，此时他刚拧上水瓶 |
| 67 | F3 | deepseek | L1-text | 0 | 285.5 | villain/chips | 说"all in"，右手将一摞筹码推出至牌桌中央 | False | t=285.5附近villain正在推出筹码，但没有出现他说"all in"的对应语音/字幕 |
| 68 | F3 | deepseek | L1-text | 2 | 51.6 | villain/speech | villain说 'would you mean for bet pocket nines here jack nine | False | t=51.6附近画面中没有出现villain说'would you mean for bet pocket nines  |
| 69 | F3 | gpt | L1-text | 1 | 188.6 | villain/speech | 说“she's over betting she's betting basically the pot”，随后进入长时 | False | t=188.6附近没有出现villain说“she's over betting she's betting basic |
| 70 | F3 | gpt | L1-text | 2 | 180.0 | villain/hands | Hero下注后，Villain低头查看自己的底牌，并用手指摩挲牌边。 | False | t=180附近hero下注后，villain的底牌被遮挡，无法确认他低头查看底牌、手指摩挲牌边的动作 |
| 71 | F3 | gpt | L1-video | 2 | 246 | villain/posture | 黑色黄条纹外套男子保持坐姿，双手停在身体前方，未伸向筹码 | False | t=246附近穿黑色黄条纹外套的男子一只手插在衣服里，另一只手放在桌边，不是双手停在身体前方未伸向筹码的状态，他身体稍前 |
| 72 | F3 | kimi | L1-text | 0 | 34.2 | villain/speech | villain 跟注 4bet 后连续两遍说 'all right i'm gonna slow play' | False | t≈34s附近画面中hero正在下注，villain（黑皮衣男）未出现该段语音，也未说对应台词 |
| 73 | F3 | kimi | L1-text | 2 | 20 | villain/speech | 翻前桌谈中对hero说"you get fold"、"you can let it go if you uh you'r | False | t≈20s附近画面中没有听到villain对hero说这两句台词，此时两人在交谈但内容不符 |
| 74 | F3 | kimi | L1-video | 0 | 199.5 | villain/hands | villain低头用双手将面前筹码切分成多摞反复整理，期间数次抬眼看向hero | False | t≈199.5s附近villain没有低头用双手把筹码切分成多摞反复整理、抬眼看hero的动作，他此时单手拨弄筹码，动作 |
| 75 | F3 | kimi | L1-video | 1 | 193 | villain/hands | 右手抬起触碰鼻/嘴部约1秒后放下，恢复双手交叠 | False | t≈193s附近是中间戴黑帽的Phil Hellmuth抬手触碰鼻嘴部，不是villain做该动作 |
| 76 | F3 | qwen | L1-text | 0 | 188.6 | villain/speech | villain说 'she's over betting she's betting basically the pot | False | t≈188.6s附近画面中无对应台词的语音或字幕，villain未说出该句内容 |
| 77 | F3 | qwen | L1-text | 1 | 100.0 | villain/speech | villain核算'fifteen into twenty eight'后说'all right i'll call' | False | t≈100s附近无对应核算筹码及说i'll call的语音/字幕，villain此时在拧水瓶准备喝水 |
| 78 | F3 | qwen | L1-text | 1 | 150.0 | villain/speech | villain在转牌对话中说'i've got all these nut combos ... i could hav | False | t≈150s附近villain在喝饮料，未出现所述台词内容 |
| 79 | F3 | qwen | L1-text | 2 | 51.6 | villain/speech | 翻牌先说 'i check'，随后提到 'pocket nines here' 等牌型 | False | t≈51.6s翻牌阶段villain在喝水，未出现说i check及提到pocket nines的内容 |
| 80 | F3 | qwen | L1-text | 2 | 115.0 | villain/speech | 列举 'pocket twos'、'nine two suited' 等可能牌型，并称 hero 的 aces/king | False | t≈115s附近villain未列举pocket twos、nine two suited等牌型，也未说aces/kin |
| 81 | F3 | qwen | L1-text | 2 | 188.6 | villain/speech | 说 'she's over betting she's betting basically the pot' | False | t≈188.6s附近没有villain说该句台词的可观察证据 |
| 82 | F3 | qwen | L1-video | 0 | 194.0 | villain/hands | 面对 turn 大额下注长考期间抬手触碰鼻部后放下，呼吸节奏平稳 | False | t≈194s附近抬手碰鼻部的是中间戴黑帽的男子（Hellmuth），并非villain，villain此时手放在桌上未做 |
| 83 | F3 | qwen | L1-video | 1 | 283.0 | villain/chips | 一次性连续动作把整摞筹码推过下注线完成 all-in，无口头声明、未分堆清点 | False | t≈283s附近villain仍在触碰筹码清点，并未一次性连续推整摞筹码完成all-in，此前存在分堆清点动作 |
| 84 | F3 | qwen | L1-video | 2 | 252 | villain/gaze | 决策阶段视线多停留在 Hero 与邻座，未低头看自己筹码或反复看公共牌 | False | t≈252s决策阶段villain视线看向桌面/自己的筹码区域，并非多停留在hero与邻座、不看筹码和公共牌 |
| 85 | F3 | qwen | L1-video | 2 | 132 | villain/hands | flop 决策期缓慢拧瓶喝水后宣布跟注 | False | t≈132s附近拧瓶喝水的是中间戴黑帽的男子，并非villain，villain此时手持罐装饮料，没有拧瓶喝水后宣布跟注 |
| 86 | F4 | claude | L1-text | 1 | 110 | villain/speech | 转牌加注时以随意语气询问'what did you just bet'，随后逐枚清点筹码后完成加注到1400 | False | t=108-112s画面里花衬衫villain没有询问下注额，也没有逐枚清点筹码加注到1400，此时是戴白帽的玩家在摆弄 |
| 87 | F4 | claude | L1-text | 1 | 161 | villain/speech | 氛围语境中说出'i will be if i lose this hand'，表露预期获胜 | False | t=159-163s画面中没有听到任何人说出“i will be if i lose this hand”这句话 |
| 88 | F4 | claude | L1-text | 2 | 158 | villain/chips | 全下后多次短暂离开画面（约150s-188s期间反复） | False | t=150-188s期间戴白帽villain多次出现在画面中，没有反复离开画面补筹码 |
| 89 | F4 | claude | L1-video | 1 | 149 | villain/chips | Villain has pushed a large stack forward (all-in), sitting b | False | t=147-151s没有看到villain推出大堆筹码all-in，也看不到他坐直放松无小动作的姿态 |
| 90 | F4 | claude | L1-video | 2 | 120 | villain/hands | villain身穿花衬衫，右手将筹码拿在手中反复摆弄，头部略微低垂，视线停留在桌面 | False | t=118-122s花衬衫villain右手握拳放在桌沿，没有反复摆弄筹码，头部转向右侧，没有低垂看桌面 |
| 91 | F4 | deepseek | L1-text | 0 | 161 | villain/face | 全下后转向右侧玩家说话时露出笑容。 | False | t=159-163s露出笑容转向右侧说话的是花衬衫玩家，不是戴白帽的villain |
| 92 | F4 | deepseek | L1-text | 0 | 139 | hero/posture | hero 保持托腮后才推出筹码跟注转牌加注。 | False | t=137-141shero（深色连帽衫）托腮后推出筹码，但视频总时长到193s，此时是转牌跟注，并非在139s完成跟注 |
| 93 | F4 | deepseek | L1-text | 2 | 114 | villain/chips | 拿起一摞绿色筹码逐枚摆到桌沿清点 | False | t=112-116s拿起筹码逐枚摆放的是戴白帽玩家，不是花衬衫villain，且摆放的是黑红相间的筹码，不是绿色筹码 |
| 94 | F4 | deepseek | L1-text | 2 | 158 | villain/posture | 双臂交叠前倾身体看向hero | False | t=156-160s戴白帽villain双臂交叠前倾，但没有看向hero，而是看向右侧 |
| 95 | F4 | gpt | L1-text | 1 | 150.0 | villain/chips | Villain将身前剩余所有筹码向前推出 | False | t=148-152s没有看到villain推出身前所有剩余筹码，移动筹码的是荷官 |
| 96 | F4 | gpt | L1-text | 2 | 161 | villain/face | 转向右侧玩家说话并露出笑容 | False | t=159-163s转向右侧说话露笑容的是花衬衫玩家，不是戴白帽villain |
| 97 | F4 | gpt | L1-video | 1 | 149 | hero/hands | 戴眼镜的玩家身体前倾，右手伸向桌面前方的牌和筹码区域 | False | t=147-151s伸向桌面前方牌和筹码区域的是荷官的手，不是戴眼镜玩家（荷官）的右手做该动作，且荷官不是hero |
| 98 | F4 | gpt | L1-video | 2 | 132 | villain/gaze | 对手右手仍靠近脸部，视线朝向桌面筹码区域 | False | t=130-134s右手靠近脸部看向筹码的是hero，不是villain |
| 99 | F4 | kimi | L1-text | 1 | 110.0 | villain/speech | 转牌加注时语气自然报出"fourteen hundred"，并随意询问"what did you just bet" | False | 108-112秒画面中，没有可观察到的语音显示villain报出“fourteen hundred”或询问“what d |
| 100 | F4 | kimi | L1-video | 0 | 148.0 | villain/chips | Hero过牌后约2秒，villain双手将面前整摞筹码一次性推入池中（$4,750全下），动作连贯无停顿，推注时视线落在 | False | 146-150秒画面中，villain没有做出双手将整摞筹码一次性推入池中的动作，推筹码的是其他人，也无对应语音显示全下 |
| 101 | F4 | kimi | L1-video | 1 | 112 | villain/chips | 转牌圈对手低头用双手整理、点数面前绿色小筹码，随后把加注筹码推入池中 | False | 110-114秒画面中，villain没有低头用双手整理、点数绿色小筹码的动作，他面前的筹码多为粉黑相间，也未在该时段推 |
| 102 | F4 | kimi | L1-video | 2 | 64 | villain/posture | 翻牌圈跟注$300时以右拳撑头、身体后靠，动作无停顿 | False | 62-66秒画面中，villain（白帽玩家）没有以右拳撑头、身体后靠的动作，此时他身体前倾，手放在底牌上，花衬衫玩家才 |
| 103 | F4 | kimi | L1-video | 2 | 100 | villain/face | 转牌发出后左手持底牌，右手食指抵住太阳穴，嘴角上扬看向hero方向 | False | 98-102秒画面中，左手持底牌、右手食指抵住太阳穴嘴角上扬的是花衬衫玩家，不是villain（白帽玩家） |
| 104 | F4 | kimi | L1-video | 2 | 149 | villain/face | 全下后面部朝向hero，嘴角上扬露齿，头部微前倾 | False | 147-151秒画面中，全下后面部朝向hero、嘴角上扬的是花衬衫玩家，不是villain（白帽玩家），此时villai |
| 105 | F4 | qwen | L1-text | 0 | 148.5 | villain/speech | 说出“i'm all in” | False | 146.5-150.5秒画面中，没有可观察到的语音显示villain说出“i'm all in” |
| 106 | F4 | qwen | L1-text | 0 | 158.0 | villain/posture | 双臂交叠放在桌沿，前倾身体并看向hero | False | 156-160秒画面中，villain双臂交叠放在桌沿，但头靠在手臂上，没有前倾看向hero |
| 107 | F4 | qwen | L1-text | 1 | 150.0 | villain/chips | 将身前剩余所有筹码向前推出 | False | 148-152秒画面里，villain没有将身前剩余所有筹码向前推出，推筹码的是其他人 |
| 108 | F4 | qwen | L1-video | 0 | 133 | villain/posture | turn 下注结束后身体后靠椅背，单手托腮，与邻座保持交谈，嘴角多次上扬 | False | 131-135秒画面中，身体后靠椅背、单手托腮的是黑T恤戴银链的玩家，花衬衫玩家也有托腮动作，villain（白帽玩家） |
| 109 | F5 | claude | L0 | 2 | 0 | villain/chips | turn 公共牌 Jh 发出后，对手未经停顿直接将全部 7225 筹码推入底池 | False | t≈73s附近转牌Jh发出后，画面中没有对手直接推入全部7225筹码的动作，该时刻附近是hero在思考，全下动作发生在更 |
| 110 | F5 | claude | L1-text | 2 | 34.0 | villain/hands | 翻前轮到行动时先双臂交叉、手碰鼻子，约34s才前倾拨筹码，39s完成跟注 | False | t=34s附近蓝色花衬衫玩家没有双臂交叉手碰鼻子的动作，该时段他正前倾拨筹码，39s是推出筹码加注而非跟注 |
| 111 | F5 | claude | L1-video | 1 | 72 | villain/posture | 全下前坐姿前倾，右手托在下巴处，肘部支在桌沿，视线朝向公共牌方向 | False | t=72s±2s全下尚未发生，被指为villain的白衬衫玩家（hero）是左手托下巴，右手放在桌面，没有前倾右手托下巴 |
| 112 | F5 | claude | L1-video | 2 | 76 | villain/hands | 双手离开面部放到桌面并分开摊平，前臂平放于桌沿，未再触碰剩余筹码 | False | t=76s±2s没有出现双手离开面部摊平放在桌沿、不碰筹码的动作，白衬衫玩家一只手仍托着脸 |
| 113 | F5 | deepseek | L1-text | 1 | 82 | villain/gaze | 双肘撑桌身体前倾，视线在公共牌和筹码堆间移动准备筹码 | False | t=82s±2s被指为villain的黑帽黑衣玩家手持水瓶，没有双肘撑桌前倾视线移动准备筹码的动作，该姿态属于白衬衫he |
| 114 | F5 | deepseek | L1-text | 1 | 89 | villain/chips | 将身前大部分筹码堆一次性推入底池完成转牌圈全下 | False | t=89s±2s没有出现将大部分筹码一次性推入底池转牌全下的动作，蓝色花衬衫玩家是分多次拨筹码 |
| 115 | F5 | deepseek | L1-text | 2 | 52 | villain/hands | 翻牌圈身体前倾，手指按在底牌边缘查看底牌，随后完成翻牌加注 | False | t=52s±2s为第一人称视角，未拍到villain前倾按底牌看牌后加注的动作 |
| 116 | F5 | gpt | L1-video | 0 | 74.0 | villain/gaze | 保持双臂交叉，头部朝向牌桌和Hero一侧 | False | t=74s±2s白衬衫玩家（hero）没有双臂交叉，他是单手托脸，且他是hero不是villain |
| 117 | F5 | gpt | L1-video | 2 | 60 | villain/chips | 白衬衫对手右手伸向并推动面前筹码，随后手停在桌面中央附近 | False | t=60s±2s是hero（白衬衫）伸手推动筹码，而白衬衫是hero不是villain，描述对象错误 |
| 118 | F5 | gpt | L1-video | 2 | 88 | hero/gaze | 蓝色花纹衬衫的Hero低头看向牌桌，双手位于筹码和牌桌边缘附近 | False | t=88s±2s低头看牌桌双手在筹码附近的是蓝色花衬衫玩家，而hero是白衬衫玩家，此时白衬衫hero手托脸看向一侧，描 |
| 119 | F5 | kimi | L1-text | 1 | 89.0 | villain/chips | 将身前大部分筹码（$7,225，约0.83倍底池）一次性连贯推入底池完成全下 | False | t=89附近villain没有推筹码全下的动作，全下实际发生在约73秒，此时是蓝花衬衫玩家在摆弄筹码 |
| 120 | F5 | kimi | L1-text | 1 | 0.0 | villain/speech | 翻前以调侃语气主动说"so he's gonna play super tight the rest of the ga | False | t=0附近是发牌初始阶段，没有听到villain说出该句调侃台词，无对应字幕 |
| 121 | F5 | kimi | L1-text | 1 | 68.0 | villain/speech | hero翻牌跟注后持续说话期间，villain仅简短回应"i believe"，无其他言语 | False | t=68附近画面是全桌场景，没有听到villain回应“i believe”，无对应字幕 |
| 122 | F5 | kimi | L1-text | 2 | 52 | villain/hands | 翻牌圈加注前，身体前倾、手指按在底牌边缘重新查看底牌，随后才将筹码推入完成加注（双色面板上典型的核对花色动作，指向当时持 | False | t=52附近的手按底牌特写无法确认是villain，且没有出现加注到3600的动作，描述中关于持红心听牌、转牌成同花的推 |
| 123 | F5 | kimi | L1-text | 2 | 0.5 | villain/speech | 翻前以调侃语气说"so he's gonna play super tight the rest of the game | False | t=0.5附近是发牌初始阶段，没有听到villain说出该句调侃台词，无对应字幕 |
| 124 | F5 | kimi | L1-video | 0 | 5.5 | villain/chips | 翻前 villain 单手将跟注筹码一次性推入，跟注 $675 前无停顿、未再确认底牌 | False | t=5.5附近villain是弃牌动作，将自己的手牌扔出，没有单手推入跟注675筹码的动作 |
| 125 | F5 | kimi | L1-video | 0 | 52.0 | villain/chips | hero 翻牌下注后约 4 秒，villain 双手将加注至 $3,600 的筹码推入，加注前未低头看牌 | False | t=52附近是手按底牌的特写，无法确认是villain双手推筹码加注到3600，且加注额并非3600，画面中手是按在底牌 |
| 126 | F5 | qwen | L1-text | 1 | 70.0 | villain/speech | hero跟注翻牌加注后，villain说'i believe' | False | t=70附近是发转牌的时段，画面中没有villain说'i believe'的可观察证据，没有对应字幕或说话动作匹配 |
| 127 | F5 | qwen | L1-video | 1 | 78.0 | villain/hands | 说话间举起单手攥拳挥动两次，随后双手拧开水瓶盖 | False | t=78附近，戴黑帽黑衣的男子说话时是摊开手，没有攥拳挥动两次的动作，也没有拧开水瓶盖，他一直握着水瓶，描述不符 |
| 128 | T1 | claude | L1-text | 1 | 56.0 | villain/chips | 松开交叉双臂前倾，拿起多摞筹码宣告加注/随即在58.7s说"All in"，动作连贯无停顿 | False | 56秒左右villain确实前倾推筹码，但画面中没有其在58.7s说All in的对应口型/字幕，且视频到66秒时未出现 |
| 129 | T1 | claude | L1-text | 1 | 299.0 | villain/speech | 说"there's no bluff for me...we both know that"，随后多次接触整理筹码并摊手 | False | 299.0秒超出视频总时长66秒，画面不存在该内容 |
| 130 | T1 | claude | L1-text | 2 | 63.0 | villain/posture | 推注后靠回椅背，左手捏取一枚小筹码把玩后放回桌面，视线看向 hero 等待 | False | 63秒左右villain仍前倾，没有靠回椅背，也没有捏取小筹码把玩后放回、视线看向hero等待的对应动作 |
| 131 | T1 | deepseek | L1-text | 1 | 181.0 | hero/speech | Hero says he knows Villain told him what he has and that he  | False | 181.0秒超出视频总时长66秒，画面不存在该内容 |
| 132 | T1 | gpt | L1-text | 0 | 56.0 | villain/chips | 松开原先交叉的双臂并进一步前倾，拿起多摞筹码将下注加到900美元 | False | 56秒左右villain确实松开交叉双臂前倾拿筹码，但他是将筹码推出做下注/加注，并非将下注加到900美元，加注900是 |
| 133 | T1 | gpt | L1-text | 2 | 80.2 | villain/speech | 对手说“I've made my statement, play it how I've said it” | False | 80.2秒超出视频总时长66秒，画面不存在该内容 |
| 134 | T1 | gpt | L1-text | 2 | 342.0 | villain/speech | 对手说“let's get the game rolling”并催促继续流程 | False | 342.0秒超出视频总时长66秒，画面不存在该内容 |
| 135 | T1 | kimi | L1-text | 0 | 181.0 | hero/speech | hero 公开声明 'i do have trip sixes'，此后 villain 的言行全部建立在已知 hero  | False | t≈181s附近，画面中hero没有公开声明i do have trip sixes的语音/字幕，该时段无此内容 |
| 136 | T1 | kimi | L1-text | 0 | 281.0 | villain/speech | 说 'i would never do that with one jack and that ain't no lie | False | t≈281s附近，画面中没有villain说i would never do that with one jack an |
| 137 | T1 | kimi | L1-text | 1 | 172.6 | hero/speech | hero自述曾见对手拿葫芦时下很大的注，并说'i know you told me what you have and  | False | t≈172.6s附近，画面中没有hero自述曾见对手拿葫芦时下很大注、说i know you told me what  |
| 138 | T1 | kimi | L1-text | 2 | 64.7 | villain/speech | 全下后说"One time and I'll shuffle"（语速慢） | False | t≈64.7s附近，画面中没有villain说One time and I'll shuffle的语音/字幕，无法观察到 |
| 139 | T1 | kimi | L1-text | 2 | 75.5 | villain/speech | hero问筹码量后回答"More than I want to lose" | False | t≈75.5s附近，画面中没有villain回答More than I want to lose的语音/字幕，无法观察到 |
| 140 | T1 | kimi | L1-text | 2 | 287.0 | hero/speech | hero列举自己无法击败的牌型（67、更好的三条六），称"tough spot for me...you have me | False | t≈287s附近，画面中没有hero列举自己无法击败的牌型、说tough spot for me...you have  |
| 141 | T1 | qwen | L1-text | 0 | 181.0 | villain/speech | villain提到12050并要求旁人拍摄这手牌 | False | t=181.0附近画面中villain在说话摊手，但未出现提到12050、要求旁人拍摄的对应可观察内容/字幕 |
| 142 | T1 | qwen | L1-text | 1 | 75.5 | villain/speech | 说 More than I want to lose | False | t=75.5附近画面中无对应字幕，未观察到villain说出“More than I want to lose”的可观察 |
| 143 | T1 | qwen | L1-text | 1 | 281.0 | villain/speech | 说 I would never do that with one jack | False | t=281.0附近画面中无对应字幕，未观察到villain说出该句话的可观察证据 |
| 144 | T1 | qwen | L1-text | 2 | 63.0 | villain/posture | villain靠回椅背，左手捏取一枚小筹码把玩后放回桌面，看向hero | False | t=63.0附近villain左手放在筹码堆上，没有捏取小筹码把玩后放回的动作，也未靠回椅背看向hero |
| 145 | T1 | qwen | L1-text | 2 | 210.0 | villain/chips | villain用手指拨动面前3个筹码将其对齐，并请旁人用手机拍摄这手牌 | False | t=210.0附近villain在整理对齐筹码，但未观察到请旁人用手机拍摄的可观察动作/对应内容 |
| 146 | T1 | qwen | L1-video | 1 | 336.0 | hero/posture | hero 离座站立走动后返回，长考超过 8 分钟 | False | t=336.0附近hero坐在座位上双臂交叉，并未离座站立走动，长考计时显示为8分14秒但未观察到hero走动后返回的动 |
| 147 | T1 | qwen | L1-video | 2 | 208.0 | villain/posture | 身体前倾、双手交握抵住下巴，视线落在桌面，无护牌或收筹动作 | False | t=208.0附近villain身体前倾，右手放在筹码堆上，没有双手交握抵住下巴的动作 |
| 148 | T2 | claude | L1-text | 1 | 97.4 | other/speech | 荷官报出'$90,000'全下金额 | False | t=97.4s附近没有听到荷官报出'$90,000'全下金额的语音，画面也无对应播报内容 |
| 149 | T2 | claude | L1-text | 1 | 43.0 | hero/hands | 翻牌发出后hero视线从公共牌移向villain，右手轻碰筹码边缘 | False | t=43s附近画面中戴橙色T帽的hero手搭在筹码上，没有视线从公共牌移向villain、右手轻碰筹码边缘的对应动作，且 |
| 150 | T2 | claude | L1-video | 2 | 78 | villain/hands | villain在river阶段先用手触碰筹码堆，短暂调整后停顿数秒再全下 | False | t=78s附近是villain推出筹码跟注，没有先用手触碰筹码堆调整后停顿数秒再全下的动作，全下并非villain做出 |
| 151 | T2 | deepseek | L1-text | 0 | 67.0 | villain/chips | 转牌对手数出一摞不同颜色筹码推到前位，下注$13,500 | False | t=67s附近推出筹码下注的是戴橙色T帽的hero，不是villain，不存在villain数筹码推13500下注的动作 |
| 152 | T2 | deepseek | L1-text | 1 | 67.0 | villain/chips | 转牌Kd发出后数出一摞不同颜色的筹码向前推出，下注$13,500 | False | t=67s附近推出筹码的是hero，不是villain，不存在villain数筹码推13500下注的动作 |
| 153 | T2 | deepseek | L1-text | 1 | 104.0 | villain/face | 全下后墨镜后的视线正对Hero，下颌微抬，等待Hero决策 | False | t=104s附近villain视线未正对hero，不存在墨镜后视线正对hero、下颌微抬等待决策的情况 |
| 154 | T2 | deepseek | L1-text | 1 | 106.0 | hero/chips | Hero视线移向底池，将捏着的筹码向前推出与全下筹码对齐 | False | t=106s附近hero没有将捏着的筹码向前推出与全下筹码对齐的动作，手仍放在自身筹码区域 |
| 155 | T2 | gpt | L1-text | 0 | 92.0 | villain/chips | 对手身体稍向前倾，视线由公共牌移向筹码堆，分出大摞筹码并用力推出全下 | False | t=92s附近推出全下筹码的是hero，不是villain，villain没有前倾、移视线后推筹码的动作 |
| 156 | T2 | gpt | L1-text | 0 | 104.0 | villain/gaze | 对手等待决定时视线正对Hero，下颌微抬，保持托腮姿势 | False | t=104s附近villain虽然保持托腮姿势，但视线朝向桌面，没有正对hero、下颌微抬等待决策 |
| 157 | T2 | gpt | L1-text | 1 | 104.0 | villain/gaze | 对手在全下后保持托腮姿势，视线正对Hero，下颌抬起，等待Hero决策 | False | t=104s附近villain视线朝向桌面，没有保持托腮同时正对hero、下颌抬起等待决策的表现 |
| 158 | T2 | gpt | L1-text | 2 | 67.0 | villain/gaze | 对手视线在自身筹码堆和公共牌之间切换，数出一摞不同颜色筹码推出转牌下注 | False | t=67s附近是hero在操作筹码，不是villain，不存在villain切换视线后推出转牌下注的动作 |
| 159 | T2 | gpt | L1-text | 2 | 92.0 | villain/chips | 对手上身稍向前倾，视线从公共牌移向筹码堆，分出一大摞筹码并用力推到下注区中央完成全下 | False | t=92s附近推出全下筹码的是hero，不是villain，villain没有对应推筹码动作 |
| 160 | T2 | kimi | L1-text | 0 | 92.0 | villain/chips | 河牌发出后上身前倾，视线从公共牌移向自身筹码堆，分出一大摞筹码用力推入底池中央完成全下 | False | t=92s附近推出全下筹码的是hero，不是villain，villain没有前倾、分筹码推入底池的动作 |
| 161 | T2 | kimi | L1-text | 1 | 2.0 | villain/posture | 翻前双肘撑桌身体前倾，双手整理底牌，视线转向hero方向 | False | t=2.0s附近画面中是穿灰粉球衣的男子和黑衣女子，没有戴白帽墨镜的villain双肘撑桌整理底牌、视线转向hero的动 |
| 162 | T2 | kimi | L1-text | 1 | 92.0 | villain/chips | 上身前倾，从多色筹码堆中分出一大摞用力推入下注区中央，全下约1.3倍底池 | False | t=92s附近推出筹码的是hero，不是villain，villain没有前倾、分大摞筹码推入下注区的动作 |
| 163 | T2 | kimi | L1-text | 1 | 104.0 | villain/gaze | 右手从筹码堆移开平放桌沿，视线从公共牌移向hero面部，保持对视约2秒，下颌微抬 | False | t=104s附近villain右手仍放在脸侧，没有从筹码堆移开平放桌沿，也没有视线移向hero面部保持对视的动作 |
| 164 | T2 | kimi | L1-text | 2 | 49.0 | villain/chips | flop 2s4dTc 发出后 villain 拿起两枚黄色筹码推出，下注 $3,100（约1/4底池）并口头报出 31 | False | t=49s附近推出两枚黄色筹码下注3100的是hero，不是villain，也没有听到报3100的语音 |
| 165 | T2 | kimi | L1-text | 2 | 104.0 | villain/gaze | 全下后 villain 右手离开筹码平放于底牌旁桌沿，墨镜后视线正对 hero，下颌微抬，保持静止不说话等待 hero  | False | t=104s附近villain右手仍放在脸侧，没有离开筹码平放于底牌旁桌沿，也没有视线正对hero等待决策的表现 |
| 166 | T2 | kimi | L1-video | 0 | 51 | villain/face | hero 跟注翻牌时，对手出现一次短暂抿嘴微笑后恢复无表情 | False | t=51s附近villain戴着墨镜，无法观察到其抿嘴微笑的面部动作，不存在该表情 |
| 167 | T2 | kimi | L1-video | 1 | 44.0 | villain/gaze | 翻牌圈行动前，转头注视hero方向约2秒，随后低头看筹码 | False | t=44s附近villain戴着墨镜，无法确认其转头注视hero方向约2秒后低头看筹码的动作 |
| 168 | T2 | kimi | L1-video | 1 | 49.0 | villain/chips | 翻牌发出后数秒内即单手将$3,100（约1/4底池）筹码推过下注线，无停顿 | False | t=49s附近推出3100筹码的是hero，不是villain，不存在villain单手推注无停顿的动作 |
| 169 | T2 | kimi | L1-video | 2 | 107 | villain/face | 被 Hero 长时间盯视期间数次嘴角轻微上扬（闭口），面部无其他动作 | False | t=107s附近villain戴着墨镜和头套，面部大部分被遮挡，无法观察到数次嘴角轻微上扬的动作 |
| 170 | T2 | qwen | L1-text | 0 | 41.0 | villain/posture | 翻牌发出后直起上身靠回椅背，左手拉扯衣领，视线看向公共牌 | False | t=41.0s附近villain没有直起上身靠回椅背、左手拉扯衣领、视线看公共牌的动作 |
| 171 | T2 | qwen | L1-text | 0 | 49.0 | villain/chips | 视线从公共牌移向筹码堆，拿起两枚黄色高面值筹码向前推出，完成3100下注 | False | t=49s附近拿起两枚黄色筹码推出下注的是hero，不是villain |
| 172 | T2 | qwen | L1-text | 1 | 67.0 | villain/chips | 视线在自身筹码堆和公共牌间切换，数出一摞不同颜色筹码向前推出。 | False | t=67s附近推出筹码的是hero，不是villain，不存在villain数筹码推出的动作 |
| 173 | T2 | qwen | L1-text | 1 | 104.0 | villain/gaze | 红色反光墨镜后的视线正对hero，下颌微抬，面向hero等待决策。 | False | t=104s附近villain视线朝向桌面，没有红色反光墨镜后视线正对hero、下颌微抬面向hero等待决策的表现 |
| 174 | T2 | qwen | L1-text | 2 | 41.0 | villain/posture | flop发出后直起上身靠回椅背，左手拉扯衣领，视线看向公共牌 | False | t=41.0s附近villain没有直起上身靠回椅背、左手拉扯衣领看公共牌的动作 |
| 175 | T2 | qwen | L1-video | 0 | 70.5 | villain/chips | turn $13,500 由筹码堆一次切出完成下注，过程中未清点对手筹码、未抬头看对手 | False | t=70.5s附近下注的是hero，不是villain，不存在villain切出筹码下注、不清点对手筹码不抬头的动作 |
| 176 | T2 | qwen | L1-video | 0 | 94.5 | villain/posture | river 全下将整摞筹码一次推过下注线，随后前臂靠桌沿，视线停在公共牌 | False | t=94.5s附近推全下筹码的是hero，不是villain，不存在villain推筹码后前臂靠桌沿视线停公共牌的动作 |
| 177 | T2 | qwen | L1-video | 1 | 96.0 | villain/posture | 推注后上身保持直立静止，双手置于自身筹码边缘，未抬头看 Hero | False | t=96s附近推注的是hero，villain保持手托脸的姿势，没有上身直立静止、双手置于自身筹码边缘不抬头看hero的 |
| 178 | T2 | qwen | L1-video | 2 | 95.5 | villain/gaze | 推注后视线朝向 Hero 方向，未看公共牌或底池 | False | t=95.5s附近推注的是hero，villain视线朝向桌面，无法确认其视线朝向hero方向不看公共牌底池 |
| 179 | T3 | claude | L1-text | 0 | 105.4 | villain/speech | turn圈villain说"i mean i can't bet this i have to check" | False | 103.4-107.4秒转牌阶段画面中，未听到任何人说出“i mean i can't bet this i have  |
| 180 | T3 | claude | L1-text | 1 | 88.0 | villain/chips | 推出筹码完成call $600 | False | 86-90秒画面中，是戴迷彩帽的白胡子玩家（villain）推出筹码，底池从$3100变为$4900，下注额为$1800 |
| 181 | T3 | claude | L1-text | 2 | 126.8 | villain/speech | 说出「one time」 | False | 124.8-128.8秒画面中，未听到villain说出“one time”。 |
| 182 | T3 | claude | L1-video | 0 | 108 | villain/posture | Villain在后位（UTG区域）将双手叠放在桌面边缘，身体前倾，头部微微低垂注视公共牌区域 | False | 106-110秒画面中，该位置是光头黑衣男性，他右手托额头，左手放在桌上，并非villain（戴迷彩帽白胡子玩家）双手叠 |
| 183 | T3 | deepseek | L1-text | 0 | 68.5 | villain/hands | 翻牌圈下注前身体前倾掀起底牌一角查看后放回 | False | 66.5-70.5秒flop阶段画面中，戴迷彩帽的白胡子玩家（villain）没有身体前倾掀起底牌一角查看的动作。 |
| 184 | T3 | deepseek | L1-text | 0 | 105.4 | villain/speech | 说出'i mean i can't bet this i have to check' | False | 103.4-107.4秒转牌阶段画面中，未听到villain说出“i mean i can't bet this i h |
| 185 | T3 | deepseek | L1-text | 1 | 123.0 | villain/gaze | sits with elbows on table, hands clasped near chips, looking | False | 121-125秒画面中，villain右手搭在桌沿，左手放在筹码上，并非双肘搭桌、双手交握看向hero方向。 |
| 186 | T3 | deepseek | L1-text | 1 | 125.5 | villain/hands | looks down at chip stack, right hand against cheek, left han | False | 123.5-127.5秒画面中，villain右手搭在桌沿，左手整理筹码，并非右手抵脸颊、左手对齐筹码。 |
| 187 | T3 | deepseek | L1-text | 2 | 132 | villain/posture | 全下后双手交叠放在桌沿，看向其他人等待决定 | False | 130-134秒画面中，all-in后villain（戴迷彩帽白胡子玩家）双手没有交叠放在桌沿，也没有看向其他人等待决定 |
| 188 | T3 | gpt | L1-text | 0 | 88 | villain/chips | 面对翻牌加注至1200美元及Hero冷跟后，补入600美元跟注 | False | 86-90秒画面中，是戴迷彩帽的白胡子玩家（villain）推出筹码下注$1800，并非补入600美元跟注。 |
| 189 | T3 | gpt | L1-text | 0 | 129 | villain/chips | 将一整摞绿色筹码推入下注区，全下3100美元 | False | 127-131秒画面中，villain是用右手推出多摞绿色筹码，并非左手推出一整摞完成$3100 all-in。 |
| 190 | T3 | gpt | L1-text | 1 | 105.4 | villain/speech | villain说“i mean i can't bet this i have to check”，随后过牌 | False | 103.4-107.4秒转牌阶段画面中，未听到villain说出“i mean i can't bet this i h |
| 191 | T3 | gpt | L1-text | 1 | 126.8 | villain/speech | villain在推出筹码前说“one time” | False | 124.8-128.8秒画面中，未听到villain在推出筹码前说出“one time”。 |
| 192 | T3 | gpt | L1-text | 1 | 141.0 | villain/speech | villain转头看向左侧白衣男性，抬手做手势后交握双手并开口交谈 | False | 139-143秒画面中，villain转头和戴黑帽穿黑运动服的玩家交谈时抬手做手势后交握双手，但无法确认他开口交谈的具体 |
| 193 | T3 | gpt | L1-text | 2 | 123.0 | villain/gaze | Villain看向Hero方向，双肘搭在桌沿。 | False | 121-125秒画面中，villain右手搭在桌沿，左手放在筹码上，并非双肘搭在桌沿看向hero方向。 |
| 194 | T3 | gpt | L1-video | 0 | 128 | villain/hands | Villain的手仍在面部附近，另一只手靠近桌面上的筹码 | False | 126-130秒画面中，villain的右手搭在桌沿，左手在整理并推出筹码，没有手在面部附近。 |
| 195 | T3 | kimi | L1-text | 0 | 18.0 | villain/speech | 翻前加注时边说'it's so suspicious'、'don't even make a statement i'm | False | t=18s附近画面中戴黑帽黑衣的玩家推出筹码，但画面无字幕/声音可证实其说出对应台词，且该时刻是他跟注而非加注，底池从1 |
| 196 | T3 | kimi | L1-text | 0 | 105.4 | villain/speech | 转牌圈主动说'i mean i can't bet this i have to check'，随后过牌 | False | t=105.4s附近画面无字幕/声音可证实戴迷彩帽白胡子玩家说出对应台词，且该时段他没有过牌动作，转牌发出后无人下注直接 |
| 197 | T3 | kimi | L1-text | 0 | 125.5 | villain/hands | 低头看自己筹码堆，右手抵在脸颊边，左手把筹码重新摞齐 | False | t=125.5s附近villain右手搭在自己脸颊/下巴处，左手在摞筹码，但不是把筹码重新摞齐后立刻推注，后续才推注 |
| 198 | T3 | kimi | L1-text | 0 | 129.0 | villain/chips | 左手将一整摞绿色筹码推入下注区完成all-in $3,100，此时other尚未行动 | False | t=129s附近villain是用右手推出绿色筹码，且全下后底池变为8000，并非all-in 3100，此时其他玩家尚 |
| 199 | T3 | kimi | L1-text | 1 | 112.3 | villain/speech | 转牌过牌后说'it's just not the hand I want, it equals any other tw | False | t=112.3s附近无声音/字幕证实villain说出对应台词，无法确认该语音存在 |
| 200 | T3 | kimi | L1-text | 2 | 18.0 | villain/speech | 翻前3-bet时说"it's so suspicious"、"don't even make a statement i | False | t=18s附近不是villain做3-bet，是光头玩家加注，也无声音证实对应台词和自述动机 |
| 201 | T3 | kimi | L1-text | 2 | 129.0 | villain/chips | 左手将整摞绿色筹码一次性向前推入下注区完成all-in $3,100，自整理筹码到推出约6秒、动作连贯无停顿 | False | t=129s附近villain是分多次推出筹码，不是一次性推入，且全下后底池为8000，下注额3100但动作不是一次完成 |
| 202 | T3 | kimi | L1-video | 2 | 75 | villain/chips | 翻牌圈面对$1,200加注，右手切出筹码直接放入跟注，动作连贯无停顿 | False | t=75s附近翻牌圈面对1200加注，villain没有切筹码跟注，他之后弃牌了，是其他玩家跟注 |
| 203 | T3 | kimi | L1-video | 2 | 131 | villain/chips | 将整排筹码一次性平稳推过下注线（全下$3,100），无迟疑或二次调整 | False | t=131s附近villain不是一次性将整排筹码推过下注线，是分多次推出，有调整动作 |
| 204 | T3 | qwen | L1-video | 0 | 126.0 | villain/chips | river 在前两人 check 后分几次把筹码堆向前推并一次性推完整堆，动作连续无收回 | False | t≈126s时villain是分几次推筹码，但没有一次性推完整堆的动作，动作存在停顿 |
| 205 | T3 | qwen | L1-video | 2 | 127.5 | villain/chips | 用约 4 秒把筹码码成单一长列，一次动作将整叠推过下注线，中途未停顿或回手 | False | t≈127.5s时villain没有用约4秒把筹码码成单一长列、一次推过下注线且中途不停顿的动作 |
| 206 | T4 | claude | L1-video | 0 | 138 | hero/posture | Hero（花纹衬衫）低头注视牌桌，右手放在筹码区域附近，身体前倾，面部朝下持续约20秒 | False | t=138s附近，穿花衬衫的hero没有低头注视牌桌、右手放筹码区附近身体前倾持续20秒，此时镜头里他正和他人互动，且该 |
| 207 | T4 | claude | L1-video | 0 | 152 | hero/face | Hero微微摇头后低头看牌，随后拿起底牌准备动作，面部表情无明显笑容或放松迹象 | False | t=152s附近，穿花衬衫的hero没有微微摇头后低头看牌、拿起底牌准备动作的画面，他的手在筹码处，面部无明显该动作 |
| 208 | T4 | claude | L1-video | 1 | 108 | villain/posture | Villain in black cap cups his hand over his mouth/chin area, | False | t=108s附近，戴黑帽的villain（Phil Hellmuth）是手托下巴，不是用手捂住嘴/下巴区域，身体并非完全 |
| 209 | T4 | deepseek | L1-text | 1 | 156.5 | villain/chips | 双手从身前筹码堆拿起数枚筹码并宣布allin | False | t=156-159s，villain是用右手拿筹码，并非双手，且此时不是宣布allin |
| 210 | T4 | gpt | L1-text | 0 | 51.0 | villain/posture | 双肘撑在牌桌边缘，身体前倾，双手放在身前反复搓动手指 | False | t=51s附近，穿花衬衫的villain没有双肘撑桌前倾、双手反复搓动手指的动作，该姿势属于白帽男子 |
| 211 | T4 | gpt | L1-text | 1 | 93.5 | villain/speech | 完成转牌下注的同时持续说话，并说“this one's this one's gonna be for you” | False | t=93s附近，无法观察到villain说出“this one's this one's gonna be for yo |
| 212 | T4 | kimi | L1-text | 1 | 156.5 | villain/chips | 河牌发出约27秒后，左手右手从身前筹码堆拿起数枚筹码，宣布allin | False | t≈156-158s villain仅用右手推出筹码，并非双手拿筹码，且未在该时刻宣布all-in |
| 213 | T4 | kimi | L1-text | 2 | 144.5 | villain/speech | 河牌发出后右手在筹码上反复拨弄筹码，同时持续闲聊，语气自然 | False | t≈144.5s 可见villain拨弄筹码且嘴部动作，但无法听清其说话内容，无法确认是持续闲聊且语气自然 |
| 214 | T4 | kimi | L1-video | 0 | 143.0 | villain/hands | 全下后 villain 低头再次掀开自己的底牌查看约1-2秒，随后放回原位并用手指整理牌面 | False | t≈143s 画面中villain并未低头掀开底牌查看，此时他的手在拨弄身前筹码 |
| 215 | T4 | kimi | L1-video | 1 | 140 | hero/posture | Hero(粉色蕾丝上衣)长考中身体基本静止,右手搭在桌沿筹码旁,视线多次投向全下者 | False | t≈140s hero（粉色蕾丝上衣女性）右手搭在桌沿，但并未多次投向全下者，视线方向并非朝向villain，且此时她手 |
| 216 | T4 | qwen | L1-text | 0 | 156.5 | villain/chips | 双手从身前筹码堆拿起数枚筹码并宣布allin | False | t≈156-158s villain仅用右手推出筹码，并非双手拿筹码，且未在该时刻宣布all-in |
| 217 | T4 | qwen | L1-video | 0 | 133 | villain/speech | 推注后保持说话，视线停留在 Hero 方向，未二次查看公共牌或自家筹码 | False | t≈133s villain并未推注，此时他尚未全下，也未保持说话看向Hero方向 |
| 218 | T4 | qwen | L1-video | 0 | 150 | villain/gaze | Hero 长考期间 Villain 保持抬头坐姿，回应桌边谈话，无敲桌、催促或掩牌动作 | False | t≈150s villain并非保持抬头坐姿回应谈话，他低头看向筹码/底牌区域，存在手部动作 |
| 219 | T5 | claude | L1-text | 0 | 220 | hero/speech | hero说"this is so obnoxious"，并承认"i definitely had the best ha | False | t≈220s附近，hero在和villain对话，没有听到hero说“this is so obnoxious”以及“i |
| 220 | T5 | claude | L1-text | 0 | 292.5 | hero/chips | hero用抛硬币筹码方式决定call或fold，结果为fold | False | t≈292.5s附近，hero没有抛硬币/抛筹码决定call或fold的动作，也未出现fold结果的对应动作 |
| 221 | T5 | claude | L1-text | 1 | 147.7 | villain/speech | 对手低语速说"Yeah, this is a good trap, it's a good"，评论你转牌后位的过牌 | False | t≈147.7s附近是发牌/切镜头时段，没有听到villain说“Yeah, this is a good trap,  |
| 222 | T5 | claude | L1-text | 2 | 292.5 | hero/chips | 河牌长考后将跟注决策交付随机硬币翻转 | False | t≈292.5s附近，hero没有将决策交付随机硬币翻转的动作 |
| 223 | T5 | claude | L1-video | 1 | 120 | other/posture | 全景镜头显示桌上其他玩家对全下的反应较为安静，无人表现出惊讶或催促 | False | t≈120s附近还未发生全下（全下在约185s），全景镜头里其他玩家状态正常，不存在对全下的反应。 |
| 224 | T5 | deepseek | L1-text | 0 | 181.8 | villain/speech | 先问“Do you know what that size is?”，在hero说with an eight应overb | False | t≈181.8s附近，没有听到villain问“Do you know what that size is?”，也没有在 |
| 225 | T5 | deepseek | L1-text | 1 | 185.0 | villain/chips | 对手推出全部$16,475，下注约2倍底池$8,325。 | False | t≈185s附近，底池显示为$8325，villain推出筹码全下，但画面无法确认其下注额为$16,475（约2倍底池） |
| 226 | T5 | deepseek | L1-text | 2 | 96.0 | hero/chips | hero 3-bets flop to $3,700; hero holds Tc, reducing T8 and T | False | t≈96s附近，hero下注后底池显示为$6125，无法确认下注额是$3700，且hero底牌被遮挡，无法看到持有Tc。 |
| 227 | T5 | gpt | L1-text | 0 | 61.0 | villain/chips | Villain经过较长思考后推出筹码完成翻牌check-raise至1500 | False | t≈61s附近，底池显示为$2825，是villain跟注/加注后的额度，无法确认check-raise至1500，也未 |
| 228 | T5 | gpt | L1-text | 0 | 147.7 | villain/speech | 转牌双方check后，Villain说这是一个good trap，并在149秒重复类似表述 | False | t≈147.7s附近是转牌后发河牌的时段，没有听到villain说这是good trap，149s是河牌发出也无该重复表 |
| 229 | T5 | gpt | L1-text | 0 | 255.0 | villain/hands | 长考期间Villain数次将手指放在下注区筹码上，但没有移动筹码 | False | t≈255s附近，长考的是hero，villain的手没有放在下注区筹码上，也没有数次触碰筹码不移动的动作。 |
| 230 | T5 | gpt | L1-text | 1 | 61.0 | villain/chips | 翻牌圈在hero下注后推出筹码完成check-raise $1500 | False | t≈61s附近，底池显示为$2825，无法确认villain完成check-raise $1500，也未清晰看到vill |
| 231 | T5 | gpt | L1-text | 2 | 184.0 | villain/chips | 他身体前倾，从筹码堆中整理出一摞筹码。 | False | t≈184s附近，villain身体前倾，但没有从筹码堆中整理出一摞筹码的明确动作。 |
| 232 | T5 | gpt | L1-text | 2 | 186.1 | villain/speech | 在Hero说有8应该overbet后，他回答“I think you're right”。 | False | t≈186.1s附近，没有听到villain回答“I think you're right”。 |
| 233 | T5 | gpt | L1-text | 2 | 255.0 | villain/speech | 他询问Hero是否是T4同花，并说若Hero是T4同花就觉得欠钱。 | False | t≈255s附近，发言者是hero，没有听到villain询问hero是否是T4同花并说欠钱相关内容。 |
| 234 | T5 | gpt | L1-video | 0 | 184 | villain/gaze | Villain继续面向Hero，双手位于身体前方，尚未出现推筹动作 | False | t≈184s附近，villain面向hero，但他的手已经在筹码附近，随后很快出现推筹动作，并非尚未出现推筹动作。 |
| 235 | T5 | gpt | L1-video | 1 | 180 | villain/posture | 双臂交叉置于胸前，身体朝向Hero一侧 | False | t≈180s附近，villain没有双臂交叉置于胸前，他手臂放在桌面上。 |
| 236 | T5 | kimi | L1-text | 0 | 147.7 | villain/speech | 转牌双方check后主动说'this is a good trap… if this is a trap, it's p | False | 145.7-149.7秒画面中是发转牌8，双方均未下注，没有任何人说出该段台词 |
| 237 | T5 | kimi | L1-text | 0 | 266.0 | villain/posture | hero长考期间在手肘撑桌托腮与靠椅背右手遮嘴姿势间自然切换，手指搭在下注区筹码上未移动，低头看牌桌、面带笑容，无僵直或 | False | 264-268秒画面里villain（绿外套男子）手肘撑桌但没有托腮，也没有靠椅背右手遮嘴的切换，手指没有搭在下注区筹码 |
| 238 | T5 | kimi | L1-text | 1 | 123.0 | villain/chips | 翻牌圈 villain 加注后被 hero 再加注到 $3,700，villain 靠椅双臂交叉再前倾，最终推出筹码跟注 | False | 121-125秒画面里翻牌圈是绿外套男子推出筹码跟注，他没有靠椅双臂交叉再前倾的动作，跟注后底池为$8325，不是跟注$ |
| 239 | T5 | kimi | L1-text | 1 | 256.0 | villain/speech | 长考中 villain 开玩笑说 'if you have ten four suited I'd feel like  | False | 254-258秒画面里长考中没有人说该段玩笑话，白衣女子在拍手，绿外套男子在摆弄筹码 |
| 240 | T5 | kimi | L1-text | 1 | 262.0 | villain/hands | hero 长考期间 villain 交替出现靠椅右手遮挡嘴部、手肘撑桌左手托腮的姿势，手指放在下注区筹码上未移动 | False | 260-264秒画面里villain（绿外套男子）没有交替出现靠椅右手遮嘴、手肘撑桌左手托腮的姿势，他的手在筹码附近，手 |
| 241 | T5 | kimi | L1-text | 1 | 271.0 | villain/speech | villain 说 'if I'm playing GTO then I don't really care... bu | False | 269-273秒画面里没有人说该段台词，是白衣女子在说话，绿外套男子没有发言 |
| 242 | T5 | kimi | L1-text | 2 | 193.0 | villain/posture | 全下后对手靠回椅背、左手撑脸颊、面带笑容持续看向hero，姿态稳定无回避 | False | 191-195秒画面里全下后绿外套男子没有靠回椅背左手撑脸颊面带笑容持续看hero，他身体前倾，手放在桌沿 |
| 243 | T5 | kimi | L1-video | 1 | 154.0 | villain/speech | 河牌 K 发出后、下注前，villain 主动侧头与 Hero 交谈，面部带笑，随后双手整理面前筹码 | False | 152-156秒画面里河牌K发出后下注前，绿外套男子没有主动侧头和Hero交谈带笑，随后也没有双手整理面前筹码，他手放在 |
| 244 | T5 | kimi | L1-video | 2 | 265.5 | villain/speech | 持续开口回应 Hero 的问话，伴随手部比划，语速平稳 | False | 263.5-267.5秒画面里绿外套男子没有持续开口回应Hero的问话，也没有手部比划，他手放在筹码上，没有说话 |
| 245 | T5 | qwen | L1-text | 0 | 185.0 | villain/chips | 推出整摞筹码完成 allin $16,475 | False | 183-187秒画面里绿外套男子推出筹码下注，底池变为$24800，不是完成allin $16,475，他面前仍有剩余筹 |
| 246 | T5 | qwen | L1-text | 2 | 27.0 | villain/posture | 完成跟注后靠回椅背，双臂交叉 | False | 25-29秒画面里绿外套男子跟注后拿起易拉罐喝水，没有靠回椅背双臂交叉 |
| 247 | T5 | qwen | L1-text | 2 | 147.7 | villain/speech | 说'Yeah, this is a good trap, it's a good' | False | 145.7-149.7秒画面里没有人说'Yeah, this is a good trap, it's a good' |
| 248 | T5 | qwen | L1-text | 2 | 169.5 | villain/speech | 说'I can think of only one size I can bet if I have an eight. | False | 167.5-171.5秒画面里没有人说'I can think of only one size I can bet i |
| 249 | T5 | qwen | L1-text | 2 | 181.8 | villain/speech | 问'Do you know what that size is?' | False | 179.8-183.8秒画面里没有人问'Do you know what that size is?' |
| 250 | T5 | qwen | L1-text | 2 | 185.0 | villain/chips | 推出整摞筹码全下16475 | False | 183-187秒画面里绿外套男子推出筹码后底池为$24800，他面前仍有剩余筹码，不是全下16475 |
| 251 | T5 | qwen | L1-video | 0 | 311 | villain/gaze | Hero 伸手接触底牌时，Villain 视线跟随其手部动作，躯干姿势无变化 | False | 309-313秒画面里Hero没有伸手接触底牌，绿外套男子的视线也没有跟随手部动作，他面向hero说话 |

入样构成：judge=false 251 条 / true 0 条 / uncertain 0 条。
