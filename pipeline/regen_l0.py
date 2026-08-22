"""从 truth.json（人工校准的唯一事实源）重新生成 L0 文本，覆盖 item.json layers.L0.text。
标准化保证：L0 = truth 的纯函数投影，无自由发挥。"""
import json, sys
from pathlib import Path

CN_ACT = {"check":"check","bet":"bet","raise":"raise","call":"call","fold":"fold","allin":"allin","deal":"deal"}

def spaced(cards):
    c=str(cards).replace(" ","")
    return " ".join(c[i:i+2] for i in range(0,len(c),2))

def money(x):
    if x is None: return "$?"
    return f"${x:,.0f}" if isinstance(x,(int,float)) else f"${x}"

def trim_decision_street(acts):
    """决策街裁剪：villain 最后一次 allin/raise 之后的 hero 行动是待预测标签（call/fold），
    绝不能进 L0 输入——从该 hero 行动起全部裁掉；all-in 后、hero 决策前的 other 行动（如 other fold）保留。"""
    last_v=max((i for i,a in enumerate(acts) if a.get("actor")=="villain" and a.get("action") in ("allin","raise","bet")), default=-1)
    out=[]
    for i,a in enumerate(acts):
        if i>last_v and a.get("actor")=="hero":
            break
        out.append(a)
    return out

def render_actions(acts):
    parts=[]
    for a in acts:
        if a.get("action") in ("deal","showdown","pot_awarded"): continue
        s=f"{a.get('actor')} {CN_ACT.get(a.get('action'),a.get('action'))}"
        if a.get("amount") is not None: s+=f" ${a['amount']:,.0f}" if isinstance(a['amount'],(int,float)) else f" ${a['amount']}"
        parts.append(s)
    return "; ".join(parts) if parts else "（无行动记录）"

def regen(hid):
    d=Path("items")/hid
    t=json.load(open(d/"truth.json")); h=json.load(open(d/"hand.json")); it=json.load(open(d/"item.json"))
    tb=h.get("table",{})
    ts=t.get("table_size") or tb.get("players")
    bb=t.get("bb") or tb.get("bb") or 50
    hero_pos=t.get("hero_position") or tb.get("hero_position") or "未知"
    vill_pos=t.get("villain_position") or tb.get("villain_position") or "未知"
    hs=t.get("hero_stack_start") or tb.get("hero_stack_start")
    vs=t.get("villain_stack_start") or tb.get("villain_stack_start")
    lines=[
      f"牌局：NLHE cash，{ts} 人桌，盲注 {tb.get('blinds','$25/$50 with big-blind ante')}（1 bb = ${bb}）。",
      f"你（Hero）位置：{hero_pos}，本手开始筹码 {money(hs)}。对手（Villain）位置：{vill_pos}，本手开始筹码 {money(vs)}。",
      f"你的底牌：{spaced(t['hero_cards'])}。",
      "下注线（人工核对分街；加注金额=加注到的总额）：",
    ]
    bl=t.get("betting_line",{})
    street=t.get("street","")
    for st in ["preflop","flop","turn","river"]:
        blk=bl.get(st)
        if not blk or not blk.get("actions"): continue
        acts=blk["actions"]
        if st==street:
            acts=trim_decision_street(acts)  # 防真值泄露：hero 对 all-in 的实际响应不进输入
        board=f"（{blk['board']}）" if blk.get("board") else ""
        lines.append(f"  - {st}{board}：{render_actions(acts)}")
    lines.append(f"当前公共牌：{spaced(t['board'])}（{street}）。" if t.get("board") else "当前无公共牌（preflop 全下）。")
    pot_before=t.get("pot_before_allin"); to_call=t.get("to_call")
    lines.append(f"对手全下前底池：{money(pot_before)}；对手全下额：{money(t.get('allin_amount') or to_call)}；你需跟注：{money(to_call)}。")
    total=t.get("pot_after_allin"); req=t.get("required_equity")
    if total is not None and to_call is not None:
        lines.append(f"跟注后总底池：{money(total + to_call)}；所需胜率（跟注额 ÷ (底池+跟注额)）= {req:.1%}。")
    txt="\n".join(lines)
    old=it["layers"]["L0"]["text"]
    it["layers"]["L0"]["text"]=txt
    it["layers"]["L0"]["source"]="regen_from_truth_v1"
    json.dump(it,open(d/"item.json","w"),ensure_ascii=False,indent=1)
    return old!=txt

if __name__=="__main__":
    changed=[]
    for hid in ["T1","T2","T3","T4","T5","F1","F2","F3","F4","F5"]:
        if regen(hid): changed.append(hid)
    print("changed:",changed)
