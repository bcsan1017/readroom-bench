"""行动时间线：视频全程提取模式（v2）。

v1 的骨架来自 L0 betting_line，但多手 recap 只有最后一街下注线（data_gaps 已记录），
豆包在骨架只覆盖片尾时定位错乱（deal 被定到片尾）。v2 改为：
  豆包 doubao-seed-2-1-pro-260628 看 2fps 全程视频，直接输出完整动作序列
  （每街发牌 / check / bet / raise / call / fold / allin / showdown / pot_awarded），
  L0 已知信息（全下街、全下额、hero 最终行动、公共牌）作为"已知锚点"写进 prompt 约束对齐；
  产出后做时间单调性与街序校验（preflop<flop<turn<river，deal 在每街之首），
  再把 L0 锚点（全下额、hero 跟注额）硬对齐回事件。

用法：python -m pipeline.action_timeline --hand F1 [--fps 2] [--variant hided|masked] [--mode full|skeleton]
产物：
  items/<id>/action_timeline.jsonl（旧文件首次覆盖前存 .bak），每行：
    {"t": 秒|null, "street": "preflop|flop|turn|river", "actor": "hero|villain|dealer|other",
     "action": "deal|check|bet|raise|call|fold|allin|showdown|pot_awarded",
     "amount": 数字|null, "source": "doubao|human", "human_verified": bool}
  items/<id>/betting_line_extracted.json：按街结构化的下注线（source: video_extracted，供后续补 L0）
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from .common import load_json, hand_dir, Timer, load_env, video_duration, now_iso

load_env()

STREETS = ("preflop", "flop", "turn", "river")
SRANK = {s: i for i, s in enumerate(STREETS)}
ACTIONS = ("deal", "check", "bet", "raise", "call", "fold", "allin", "showdown", "pot_awarded")
BET_ACTS = ("check", "bet", "raise", "call", "fold", "allin")

ACT_ALIAS = {"all_in": "allin", "all-in": "allin", "allin": "allin", "jam": "allin", "shove": "allin",
             "deal_hole": "deal", "deal_flop": "deal", "deal_turn": "deal", "deal_river": "deal",
             "deal": "deal", "show": "showdown", "showdown": "showdown", "muck": "fold",
             "pot": "pot_awarded", "pot_awarded": "pot_awarded", "limp": "call"}


def board_by_street(board: str) -> dict:
    cards = re.findall(r"[2-9TJQKA][shdc]", board or "")
    out = {}
    if len(cards) >= 3:
        out["flop"] = " ".join(cards[:3])
    if len(cards) >= 4:
        out["turn"] = cards[3]
    if len(cards) >= 5:
        out["river"] = cards[4]
    return out


# ---------------- v2：全程提取 ----------------

def build_prompt(hand: dict, dur: float, fps: float) -> tuple[str, str]:
    system = (
        "你是一名扑克视频动作提取员。你将看到一段德州扑克电视节目的剪辑视频（完整一手牌，按给定 fps 抽帧，"
        "第 n 帧对应 n/fps 秒）。任务：提取这手牌从发底牌到收池的完整行动序列。\n"
        "每个动作输出一行 JSON：{\"t\": 秒数字, \"street\": \"preflop|flop|turn|river\", "
        "\"actor\": \"hero|villain|dealer|other\", \"action\": \"deal|check|bet|raise|call|fold|allin|showdown|pot_awarded\", "
        "\"amount\": 数字或null}\n"
        "规则：\n"
        "1. 覆盖视频里出现过的每条街；每条街的第一行必须是 dealer 的 deal"
        "（preflop=发底牌，flop/turn/river=发对应公共牌）。以桌面公共牌张数变化定位各街。\n"
        "2. 记录每个玩家的 check/bet/raise/call/fold/allin；多人局中非 hero/villain 的玩家 actor 填 other。\n"
        "3. amount 只在画面 UI 的下注额数字可读时填写，读不出填 null；不要凭空编造金额。\n"
        "4. t 必须单调不减，0 ≤ t ≤ 视频时长。\n"
        "5. 末尾包含 showdown（若有亮牌）和 pot_awarded（筹码推给赢家）。\n"
        "6. 下方给出的'已知锚点'是可靠事实，输出必须与之一致（金额以锚点为准）。\n"
        "7. 输出里绝不出现任何真实姓名，只用 hero/villain/other。\n"
        "8. 只输出 JSON 行，不要 markdown 围栏、不要解释。")
    players = hand.get("players", {})
    bs = board_by_street(hand.get("board", ""))
    anchors = []
    ast = hand.get("street_at_allin")
    if ast and hand.get("allin_amount"):
        anchors.append(f"- 全下发生在 {ast} 街：villain 全下 ${hand['allin_amount']:,}（此金额可靠，勿改）")
    for line in hand.get("betting_line", []):
        anchors.append(f"- 已知 {line.get('street')} 街下注线：{line.get('actions')}")
    final = (hand.get("actual") or {}).get("hero_action")
    if final:
        amt = f"（跟注额 ${hand['hero_to_call']:,}）" if final == "call" and hand.get("hero_to_call") else ""
        anchors.append(f"- hero 面对全下的最终行动：{final}{amt}")
    if hand.get("pot_before_allin"):
        anchors.append(f"- 全下前底池约 ${hand['pot_before_allin']:,}")
    for st in ("flop", "turn", "river"):
        if st in bs:
            anchors.append(f"- {st} 公共牌：{bs[st]}（该街 deal 时画面应出现这些牌）")
    user = (f"视频约 {dur:.0f} 秒，抽帧 fps={fps:g}。\n"
            f"玩家识别（仅用于在画面里认人，输出禁止出现姓名）：hero = {players.get('hero')}，"
            f"villain = {players.get('villain')}；参考已知锚点里双方的下注关系判断座位。\n"
            "已知锚点：\n" + "\n".join(anchors) +
            "\n请输出这手牌完整动作序列的 JSON 行。")
    return system, user


def parse_events(text: str, dur: float) -> list[dict]:
    evs = []
    for m in re.finditer(r"\{[^{}]*\}", text):
        try:
            d = json.loads(m.group(0))
        except Exception:
            continue
        st = str(d.get("street", "")).lower().strip()
        act = ACT_ALIAS.get(str(d.get("action", "")).lower().strip().replace("-", "_"), None) or \
            (str(d.get("action", "")).lower().strip() if str(d.get("action", "")).lower().strip() in ACTIONS else None)
        actor = str(d.get("actor", "")).lower().strip()
        if actor not in ("hero", "villain", "dealer", "other"):
            actor = "other"
        t = d.get("t")
        if st not in STREETS or act not in ACTIONS or not isinstance(t, (int, float)):
            continue
        amt = d.get("amount")
        amt = float(amt) if isinstance(amt, (int, float)) and amt > 0 else None
        evs.append({"t": round(min(max(float(t), 0.0), dur), 1), "street": st, "actor": actor,
                    "action": act, "amount": amt, "source": "doubao", "human_verified": False})
    return evs


def validate_repair(evs: list[dict], hand: dict) -> tuple[list[dict], list[str]]:
    """时间单调 + 街序单调 + deal 在每街之首 + L0 锚点硬对齐。"""
    fixes: list[str] = []
    evs = sorted(evs, key=lambda e: e["t"])  # 时间单调
    # 街序单调不减（回退的街强制归到当前街）
    cur = 0
    for e in evs:
        r = SRANK[e["street"]]
        if r < cur:
            fixes.append(f"街序回退：t={e['t']} {e['street']} → {STREETS[cur]}")
            e["street"] = STREETS[cur]
        else:
            cur = r
    # deal 在每街之首；去掉同街重复 deal
    out, seen_deal, seen_street = [], set(), set()
    for e in evs:
        st = e["street"]
        if e["action"] == "deal":
            if st in seen_deal:
                fixes.append(f"去重：{st} 重复 deal t={e['t']}")
                continue
            seen_deal.add(st)
            seen_street.add(st)
            out.append(e)
            continue
        if st not in seen_street:
            seen_street.add(st)
            if st not in seen_deal:
                seen_deal.add(st)
                out.append({"t": e["t"], "street": st, "actor": "dealer", "action": "deal",
                            "amount": None, "source": "doubao", "human_verified": False})
                fixes.append(f"补 {st} deal t={e['t']}")
        out.append(e)
    evs = out
    # 锚点硬对齐：villain allin 金额
    ast, amt = hand.get("street_at_allin"), hand.get("allin_amount")
    allin = next((e for e in evs if e["street"] == ast and e["action"] == "allin"), None)
    if allin is not None and amt:
        if allin["actor"] != "villain":
            fixes.append(f"allin actor {allin['actor']} → villain（L0 锚点）")
            allin["actor"] = "villain"
        if allin["amount"] != float(amt):
            fixes.append(f"allin 金额 {allin['amount']} → {amt}（L0 锚点）")
            allin["amount"] = float(amt)
    elif amt:
        fixes.append(f"WARNING 未提取到 {ast} 街 allin（L0 锚点缺失）")
    # hero 最终行动
    final = (hand.get("actual") or {}).get("hero_action")
    if final in ("call", "fold") and allin is not None:
        after = [e for e in evs if e["t"] >= allin["t"] and e["actor"] == "hero" and e["action"] in ("call", "fold")]
        if after:
            hf = after[0]
            if hf["action"] != final:
                fixes.append(f"hero 最终行动 {hf['action']} → {final}（L0 锚点）")
                hf["action"] = final
            if final == "call" and hand.get("hero_to_call"):
                hf["amount"] = float(hand["hero_to_call"])
            if final == "fold":
                hf["amount"] = None
        else:
            t_end = evs[-1]["t"] if evs else allin["t"]
            evs.append({"t": t_end, "street": allin["street"], "actor": "hero", "action": final,
                        "amount": float(hand["hero_to_call"]) if final == "call" and hand.get("hero_to_call") else None,
                        "source": "doubao", "human_verified": False})
            fixes.append(f"补 hero 最终 {final}（豆包漏提）")
            evs.sort(key=lambda e: e["t"])
    # 收池兜底
    if not any(e["action"] == "pot_awarded" for e in evs) and evs:
        evs.append({"t": evs[-1]["t"], "street": evs[-1]["street"], "actor": "dealer",
                    "action": "pot_awarded", "amount": None, "source": "doubao", "human_verified": False})
        fixes.append("补 pot_awarded（豆包漏提）")
    return evs, fixes


def check_report(evs: list[dict]) -> str:
    ts = [e["t"] for e in evs if e["t"] is not None]
    mono_t = all(a <= b for a, b in zip(ts, ts[1:]))
    ranks = [SRANK[e["street"]] for e in evs]
    mono_s = all(a <= b for a, b in zip(ranks, ranks[1:]))
    firsts = {}
    for e in evs:
        firsts.setdefault(e["street"], e["action"])
    deal_first = all(v == "deal" for v in firsts.values())
    streets = sorted(set(e["street"] for e in evs), key=SRANK.get)
    return (f"streets={'/'.join(streets)} n={len(evs)} t单调={'OK' if mono_t else 'FAIL'} "
            f"街序={'OK' if mono_s else 'FAIL'} deal居首={'OK' if deal_first else 'FAIL'}")


def betting_line_extracted(evs: list[dict], hand: dict) -> dict:
    bs = board_by_street(hand.get("board", ""))
    lines = []
    for st in STREETS:
        se = [e for e in evs if e["street"] == st and e["action"] in BET_ACTS]
        if not se:
            continue
        segs = []
        for e in se:
            a = f" ${e['amount']:,.0f}" if e.get("amount") else ""
            segs.append(f"{e['actor']} {e['action']}{a}")
        lines.append({"street": st, "board": bs.get(st, ""), "actions": "; ".join(segs),
                      "events": [{k: e[k] for k in ("t", "actor", "action", "amount")} for e in se]})
    known = {l.get("street") for l in hand.get("betting_line", [])}
    return {"hand_id": hand.get("hand_id"), "source": "video_extracted",
            "model": "doubao-seed-2-1-pro-260628", "generated_at": now_iso(),
            "note": "豆包全程视频提取；allin 金额已与 L0 锚点硬对齐；其余金额以画面 UI 可读为准，null=画面不可读",
            "streets_new_vs_l0": [l["street"] for l in lines if l["street"] not in known],
            "betting_line": lines}


def extract_full(hd: Path, hand: dict, fps: float, dur: float, stem: str) -> tuple[list[dict], list[str], dict]:
    from runner import providers as P
    from .timeline import low_fps_video
    vid = low_fps_video(hd, fps, stem)
    system, user = build_prompt(hand, dur, fps)
    with Timer("action_timeline.doubao_full"):
        text, usage = P.ark_call(
            [{"role": "system", "content": system},
             {"role": "user", "content": P.video_content(vid, fps, user)}],
            max_tokens=4000, temperature=0.1)
    evs = parse_events(text, dur)
    if not evs:
        raise RuntimeError(f"doubao 输出解析为空; raw head: {text[:300]}")
    evs, fixes = validate_repair(evs, hand)
    return evs, fixes, usage


# ---------------- v1 骨架模式（保留） ----------------

def _amount(seg: str):
    m = re.search(r"\$([\d,]+(?:\.\d+)?)", seg)
    return float(m.group(1).replace(",", "")) if m else None


def _actor(seg: str) -> str:
    s = seg.lower()
    ih, iv = s.find("hero"), s.find("villain")
    if ih < 0 and iv < 0:
        return "other"
    if iv < 0 or (0 <= ih < iv):
        return "hero"
    return "villain"


def parse_segment(seg: str, street: str) -> dict | None:
    s = seg.strip()
    if not s:
        return None
    low = s.lower()
    actor = _actor(s)
    amt = _amount(s)
    if "all-in" in low or "all in" in low or "allin" in low or "shoves" in low or "jams" in low:
        act = "allin"
    elif "check" in low:
        act, amt = "check", None
    elif "limp" in low or "call" in low:
        act = "call"
    elif "raise" in low or "3-bet" in low or "3bet" in low:
        act = "raise"
    elif "bet" in low:
        act = "bet"
    elif "fold" in low:
        act, amt = "fold", None
    else:
        return None
    return {"street": street, "actor": actor, "action": act, "amount": amt}


def build_skeleton(hand: dict) -> list[dict]:
    tm = hand.get("timing_abs_sec", {})
    t0 = tm.get("clip_start", 0.0)
    rel = lambda k: (round(tm[k] - t0, 1) if isinstance(tm.get(k), (int, float)) else None)
    events: list[dict] = []

    def add(street, actor, action, amount=None, t=None):
        events.append({"t": t, "street": street, "actor": actor, "action": action,
                       "amount": amount, "source": "human" if t is not None else "doubao",
                       "human_verified": t is not None})

    street_deal_t = {"preflop": rel("hand_start"), "flop": rel("flop_dealt"),
                     "turn": rel("turn_dealt"), "river": rel("river_dealt")}
    allin_street = hand.get("street_at_allin")
    for line in hand.get("betting_line", []):
        street = line.get("street")
        add(street, "dealer", "deal", None, street_deal_t.get(street))
        for seg in str(line.get("actions", "")).split(";"):
            ev = parse_segment(seg, street)
            if ev is None:
                continue
            t = None
            if ev["action"] == "allin" and street == allin_street:
                t = rel("villain_allin")
            elif street == "river" and ev["actor"] == "hero" and ev["action"] == "check":
                t = rel("hero_check_river")
            events.append({**ev, "t": t, "source": "human" if t is not None else "doubao",
                           "human_verified": t is not None})
    actual = hand.get("actual", {})
    final = actual.get("hero_action")
    if final in ("call", "fold"):
        amt = hand.get("hero_to_call") if final == "call" else None
        add(allin_street or "river", "hero", final, amt, rel("hero_announce"))
    if actual.get("villain_showed"):
        add(allin_street or "river", "villain", "showdown", None, rel("showdown"))
    add(allin_street or "river", "dealer", "pot_awarded", None, rel("pot_awarded"))
    return events


# ---------------- 入口 ----------------

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--hand", required=True)
    ap.add_argument("--fps", type=float, default=2.0)
    ap.add_argument("--mode", choices=("full", "skeleton"), default="full",
                    help="full=豆包看全程视频提取完整动作序列（默认）；skeleton=旧版 L0 骨架（不调豆包）")
    ap.add_argument("--variant", choices=("masked", "hided"), default="hided")
    a = ap.parse_args(argv)
    hd = hand_dir(a.hand)
    hand = load_json(hd / "hand.json")
    stem = "clip_hided" if a.variant == "hided" else "clip_masked"
    dur = video_duration(hd / f"{stem}.mp4")

    if a.mode == "skeleton":
        events = build_skeleton(hand)
        fixes = []
    else:
        events, fixes, usage = extract_full(hd, hand, a.fps, dur, stem)
        print(f"[action_timeline] usage={usage}", file=sys.stderr)

    rep = check_report(events)
    print(f"[action_timeline] {a.hand} {rep}", file=sys.stderr)
    for f in fixes:
        print(f"[action_timeline] fix: {f}", file=sys.stderr)

    out = hd / "action_timeline.jsonl"
    bak = hd / "action_timeline.jsonl.bak"
    if out.exists() and not bak.exists():
        bak.write_bytes(out.read_bytes())
        print(f"[action_timeline] old backed up → {bak.name}", file=sys.stderr)
    out.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in events) + "\n", encoding="utf-8")

    if a.mode == "full":
        ble = betting_line_extracted(events, hand)
        (hd / "betting_line_extracted.json").write_text(
            json.dumps(ble, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[action_timeline] betting_line_extracted: streets={[l['street'] for l in ble['betting_line']]} "
              f"new_vs_l0={ble['streets_new_vs_l0']}", file=sys.stderr)
    print(f"[action_timeline] {len(events)} events → {out}")


if __name__ == "__main__":
    main()
