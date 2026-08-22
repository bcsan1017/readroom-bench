"""终版报表：双轨口径（全量为主、剔除对照）+ 认出优势检验 + 读人增益榜 + 附录诊断。
用法：python -m scoring.final_report --runs results/final_runs_merged.jsonl --out results/final_report.md
"""
import argparse, json
from collections import defaultdict
from pathlib import Path
from .metrics import aggregate, reading_gain, score_ev_bb
from .hallucination import hallucination_rate, load_rows

ROOT = Path(__file__).resolve().parent.parent
MODELS = ["claude", "gpt", "qwen", "kimi", "deepseek"]
LAYERS = ["L0", "L1-text", "L1-video"]

def fmt(x, nd=2):
    if x is None: return "—"
    if isinstance(x, (tuple, list)): return "[" + ", ".join(fmt(v, nd) for v in x) + "]"
    if isinstance(x, float): return f"{x:.{nd}f}"
    return str(x)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="results/final_runs_merged.jsonl")
    ap.add_argument("--items", default="items")
    ap.add_argument("--hallucination", default="results/hallucination.jsonl")
    ap.add_argument("--out", default="results/final_report.md")
    ap.add_argument("--banner", default=None, help="报表顶部加注（如 draft 声明）")
    a = ap.parse_args()
    recs = [json.loads(l) for l in (ROOT / a.runs).read_text(encoding="utf-8").splitlines() if l.strip()]
    recs = [r for r in recs if not r.get("mock")]
    truths = {d.name: json.loads((d / "truth.json").read_text(encoding="utf-8"))
              for d in sorted((ROOT / a.items).iterdir()) if (d / "truth.json").exists()}
    aggF = aggregate(recs, truths, exclude_recognized=False)   # 全量口径（主）
    aggX = aggregate(recs, truths, exclude_recognized=True)    # 剔除口径（对照）
    gainsF = reading_gain(aggF); gainsX = reading_gain(aggX)
    hrows = load_rows(ROOT / a.hallucination) or []
    hall = hallucination_rate(hrows) if hrows else {}

    # per-record 中间量：pro 一致率（全量口径）+ 认出优势检验样本
    by_rec = defaultdict(list)   # (model,layer) -> [(item, p, recognized)]
    for r in recs:
        if not r.get("ok") or not r.get("parsed"): continue
        p = r["parsed"].get("p_call")
        if not isinstance(p, (int, float)): continue
        by_rec[(r["model"], r["layer"])].append((r["item_id"], float(p), bool(r["parsed"].get("recognized"))))
    pro_agree = {}
    for k, rows in by_rec.items():
        by_item = defaultdict(list)
        for it, p, _ in rows:
            by_item[it].append(p)
        vals = []
        for it, ps in by_item.items():
            act = truths.get(it, {}).get("actual", {}).get("hero_action")
            if act not in ("call", "fold"): continue
            vals.append(("call" if sum(ps)/len(ps) >= 0.5 else "fold") == act)
        pro_agree[k] = sum(vals)/len(vals) if vals else None

    # 认出优势检验：recognized true/false 两组的方向正确率与 per-record EV
    adv = {}
    for k, rows in by_rec.items():
        g = {True: [], False: []}
        for it, p, rec_flag in rows:
            if it not in truths: continue
            t = truths[it]
            g[rec_flag].append(((p >= 0.5) == bool(t["correct_call"]), score_ev_bb(p, t)))
        if g[True] and g[False]:
            adv[k] = {side: (len(v), sum(x[0] for x in v)/len(v), sum(x[1] for x in v)/len(v))
                      for side, v in g.items()}

    ids = [i for i in ["T1","T2","T3","T4","T5","F1","F2","F3","F4","F5"] if i in truths]
    oracle = sum(max(truths[i]["ev_call_bb"], truths[i].get("ev_fold_bb", 0)) for i in ids) / len(ids)
    n_lat = sum(r.get("latency_s", 0) for r in recs)
    tok_in = sum((r.get("usage") or {}).get("prompt_tokens", 0) for r in recs)
    tok_out = sum((r.get("usage") or {}).get("completion_tokens", 0) for r in recs)

    banner = [f"> **{a.banner}**", ""] if a.banner else []
    L = banner + ["# 读人 Bench 终版报表（freeze-v1 + e3fd320/f89f05b 数据勘误，10 手 × 3 trial）", "",
         "主指标 soft EV：score = p_call × EV(call)（bb/题）；p_call 取 3-trial 均值。",
         "**口径双轨**：主数字为全量口径（含 recognized）；括号内为剔除口径（recognized 题剔除）对照。",
         "recognized 语义 = 模型自报认出节目/选手/手牌任一；L0 近零 vs L1 层高比例的分布说明触发源是画面/引语而非题面；\"认出优势检验\"见 §4。",
         f"全知上界 oracle EV = {oracle:.1f} bb/题；恒 fold 基线 = 0 bb。L1-video：qwen/kimi 原生视频，claude/gpt 抽帧近似（input_mode=sampled_frames）；deepseek 不参加 L1-video。",
         f"总记录 {len(recs)} 条；累计模型时延 {n_lat/3600:.1f}h（各网关并行）；tokens in/out ≈ {tok_in/1e6:.2f}M / {tok_out/1e6:.2f}M。", "",
         "## 1. 模型 × 层 EV 矩阵（soft EV，bb/题；全量口径（剔除口径））", "",
         "| model | L0 | L1-text | L1-video | 备注 |", "|---|---|---|---|---|"]
    def cell(m, l):
        f_ = aggF.get((m, l), {}).get("ev_bb"); x_ = aggX.get((m, l), {}).get("ev_bb")
        if f_ is None: return "—"
        s = f"**{f_:.1f}**"
        if x_ is not None and aggF[(m,l)].get("n_recognized_excluded"):
            s += f" ({x_:.1f})"
        return s
    for m in MODELS:
        note = "抽帧近似" if m in ("claude", "gpt") else ("不参加视频层" if m == "deepseek" else "原生视频")
        L.append(f"| {m} | {cell(m,'L0')} | {cell(m,'L1-text')} | {cell(m,'L1-video')} | {note} |")
    L += ["", "## 2. 读人增益榜（EV(L1-x) − EV(L0)，bb/题；全量口径（剔除口径））", "",
          "| model | L1-text 增益 | L1-video 增益 |", "|---|---|---|"]
    def gcell(m, l):
        f_ = gainsF.get((m, l)); x_ = gainsX.get((m, l))
        if f_ is None: return "—"
        return f"{f_:.1f}" + (f" ({x_:.1f})" if x_ is not None else "")
    for m in sorted(MODELS, key=lambda m: -(gainsF.get((m, "L1-text")) or -1e9)):
        L.append(f"| {m} | {gcell(m,'L1-text')} | {gcell(m,'L1-video')} |")
    L += ["", "## 3. 主表明细（全量口径；幻觉率来自豆包 judge）", "",
          "| model | layer | n_items | trials | failed | EV(bb) | 95%CI | 捕获率 | action acc | pro 一致率 | recognized 题数 | 幻觉率 |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in MODELS:
        for l in LAYERS:
            v = aggF.get((m, l))
            if not v or not v.get("n_items"): continue
            L.append(f"| {m} | {l} | {v['n_items']} | {v['n_trials']} | {v['n_failed']} | **{fmt(v['ev_bb'],1)}** | {fmt(v['ev_bb_ci95'],1)} | "
                     f"{fmt(v['ev_capture'])} | {fmt(v['action_accuracy'])} | {fmt(pro_agree.get((m,l)))} | {v['n_recognized_excluded']} | {fmt(hall.get((m,l)))} |")
    L += ["", "## 4. 认出优势检验（recognized=true vs false 两组，按 trial 记录）", "",
          "若两组方向正确率/EV 无系统性差异 ⇒ \"认出节目\"未转化为答案优势，全量口径可信。", "",
          "| model | layer | n(rec/unrec) | 方向正确率 rec | 方向正确率 unrec | EV rec | EV unrec | Δ EV |",
          "|---|---|---|---|---|---|---|---|"]
    for m in MODELS:
        for l in LAYERS:
            v = adv.get((m, l))
            if not v: continue
            (nt, dt, et), (nf, df, ef) = v[True], v[False]
            L.append(f"| {m} | {l} | {nt}/{nf} | {dt:.2f} | {df:.2f} | {et:.1f} | {ef:.1f} | {et-ef:+.1f} |")
    if len(L) and L[-1].startswith("|---"):
        L.append("| （无同时含两组样本的格子） | | | | | | | |")
    if hrows:
        n_j = len(hrows); n_f = sum(1 for r in hrows if r['judge'].get('exists') is False)
        n_u = sum(1 for r in hrows if r['judge'].get('exists') == 'uncertain')
        L += ["", f"幻觉核验：共 {n_j} 条 cue，judge 判不存在 {n_f}、uncertain {n_u}（不进分母）；人工抽检清单 results/cue_audit_sample.md。"]
    L += ["", "## 5. 披露", "",
          "1. **cue 真实性判定口径（Byron 拍板）**：cue 真实性判定由豆包 judge 自动完成（true/false/uncertain 三档口径）；标注人在时间轴人工校准过程中已核阅全部视频素材，未设置独立的 cue 抽检环节。抽检清单 results/cue_audit_sample.md 保留生成，供事后复核参考。",
          "2. **数据勘误**：正式跑前发现 e3fd320 重生成的 L0 曾把 hero 对 all-in 的实际响应写进下注线（真值泄露），已修复并全量重生成后重跑（README 决策 26）；F5/T3 两处经 Byron 裁定修正（f89f05b）。本报表全部记录基于勘误后数据。",
          "3. **思考档位**：五家按赛规开最高档；gpt-5.6-sol 经 wodex 网关传 reasoning_effort=high（usage 有 reasoning_tokens 细分，透传较可信但网关侧无法完全证实，README 决策 22/25）。",
          "4. **L1-video 输入模态不对等**：claude/gpt 不吃视频，以预抽帧序列近似参赛（15–51 帧/手，input_mode=sampled_frames）；qwen/kimi 原生视频。跨模态横比需注意此差异。",
          "5. **recognized 双轨**：全量口径为主、剔除口径对照（§1/§2 括号）；认出是否构成答案优势见 §4 检验。",
          "6. **rationale 超长处置**：超 200 字符截断保存并标 rationale_truncated，不判失败（rationale 不进指标，246e21a）。",
          "7. **幻觉率列可靠性警示（批跑总控实测，待 Byron 复核）**：豆包 judge 对 hero/villain 的身份归属存在系统性倒置——T2 人工校准时间轴明确 92–94s 推筹码全下者为 villain，judge 两版 prompt（含身份锚定强化版 A/B 复测）均坚持该动作属 hero，因而把大批与人工时间轴一致的 villain cues 判 false。本表幻觉率（0.53–1.00）应视为**严重高估的上界**，仅 judge 判 true 的比例可作下界参考；结论性引用前必须完成人工抽检（results/cue_audit_sample.md，judge=false 优先已排样）。",
          "", "## 附录 A：hard 决策口径（action = p≥0.5；全量口径）", "",
          "| model | layer | hard EV(bb) | soft EV(bb) |", "|---|---|---|---|"]
    for m in MODELS:
        for l in LAYERS:
            v = aggF.get((m, l))
            if v and v.get("n_items"):
                L.append(f"| {m} | {l} | {fmt(v['ev_bb_hard'],1)} | {fmt(v['ev_bb'],1)} |")
    L += ["", "## 附录 B：校准 / 稳定性（全量口径）", "",
          "| model | layer | Brier | ECE | 3-trial p_call std |", "|---|---|---|---|---|"]
    for m in MODELS:
        for l in LAYERS:
            v = aggF.get((m, l))
            if v and v.get("n_items"):
                L.append(f"| {m} | {l} | {fmt(v['brier'],3)} | {fmt(v['ece'],3)} | {fmt(v['consistency_std_mean'],3)} |")
    fails = [r for r in recs if not r.get("ok")]
    L += ["", f"## 附录 C：失败/跳过（{len(fails)} 条 ok=false 记录，均已含重试）", "",
          "| item | layer | model | trial | attempts | error |", "|---|---|---|---|---|---|"]
    for r in fails:
        L.append(f"| {r['item_id']} | {r['layer']} | {r['model']} | {r['trial']} | {r.get('attempts')} | {str(r.get('schema_errors'))[:80]} |")
    L += ["", "## 附录 D：真值结果口径（不进主分）", "",
          "| item | hero 实际 | 胜率口径 correct_call | EV(call) bb |", "|---|---|---|---|"]
    for i in ids:
        t = truths[i]
        L.append(f"| {i} | {t.get('actual',{}).get('hero_action','?')} | {t['correct_call']} | {t['ev_call_bb']:.1f} |")
    (ROOT / a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[final_report] → {ROOT / a.out}")

if __name__ == "__main__":
    main()
