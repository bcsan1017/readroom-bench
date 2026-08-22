"""读取 runner jsonl + items/*/truth.json（+ 可选 results/hallucination.jsonl），输出 markdown 报表（v0.2：EV 主指标）。
用法：python -m scoring.report --runs results/runs.jsonl --items items --out results/report.md
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from .metrics import aggregate, reading_gain
from .hallucination import hallucination_rate, load_rows

ROOT = Path(__file__).resolve().parent.parent
PROVISIONAL = {"doubao"}


def fmt(x, nd=2):
    if x is None:
        return "N/A"
    if isinstance(x, (tuple, list)):
        return "[" + ", ".join(fmt(v, nd) for v in x) + "]"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def mname(m):
    return f"{m}\\*" if m in PROVISIONAL else m


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="results/runs.jsonl"); ap.add_argument("--items", default="items")
    ap.add_argument("--hallucination", default="results/hallucination.jsonl")
    ap.add_argument("--out", default="results/report.md")
    a = ap.parse_args(argv)
    recs = [json.loads(l) for l in (ROOT / a.runs).read_text(encoding="utf-8").splitlines() if l.strip()]
    truths = {}
    for d in sorted((ROOT / a.items).iterdir()):
        if (d / "truth.json").exists():
            truths[d.name] = json.loads((d / "truth.json").read_text(encoding="utf-8"))
    agg = aggregate(recs, truths); gains = reading_gain(agg)
    hrows = load_rows(ROOT / a.hallucination)
    hall = hallucination_rate(hrows) if hrows else {}
    n_reviewed = sum(1 for r in (hrows or []) if r.get("human"))
    mock_models = sorted({r["model"] for r in recs if r.get("mock")})
    real_models = sorted({r["model"] for r in recs if not r.get("mock")})
    oracle = sum(max(t["ev_call_bb"], t.get("ev_fold_bb", 0)) for t in truths.values()) / max(1, len(truths))

    L = ["# 读人 Bench 报表", "",
         "一句话：给模型一手\"对手 all-in、主角待决\"的整手打码牌局，模型站主角视角报 p_call；",
         "真值由对手真实底牌算出的主角胜率决定；**主指标是期望收益 EV（bb）** —— 模型的判断值多少个大盲注。", "",
         f"- runs: `{a.runs}`（{len(recs)} 条记录，{len(truths)} 题）",
         f"- 真实 API 模型：{', '.join(real_models) or '无'}；mock 占位：{', '.join(mock_models) or '无'}（等现场额度）",
         f"- doubao\\* = provisional：临时充当 L1-video 被评模型，正式名单等黑客松现场定",
         f"- 全知上界（每题按最优行动）：oracle EV = {oracle:.1f} bb/题；恒 fold 基线 = 0 bb", ""]
    L += ["## 主表：EV（bb / 题，越高越好）",
          "",
          "score = p_call × EV(call) + (1−p_call) × 0；每题每层 n trial 的 p_call 取均值；recognized=true 的题剔除。",
          "",
          "| model | layer | n_items | trials | failed | **EV(bb)** | EV 95%CI | EV 捕获率 | hard EV(bb) | action acc | 幻觉率 |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for (m, layer), v in sorted(agg.items()):
        if v.get("n_items", 0) == 0:
            L.append(f"| {mname(m)} | {layer} | 0 | - | - | - | - | - | - | - | - |"); continue
        L.append(f"| {mname(m)} | {layer} | {v['n_items']} | {v['n_trials']} | {v['n_failed']} | **{fmt(v['ev_bb'],1)}** | {fmt(v['ev_bb_ci95'],1)} | "
                 f"{fmt(v['ev_capture'])} | {fmt(v['ev_bb_hard'],1)} | {fmt(v['action_accuracy'])} | {fmt(hall.get((m,layer)))} |")
    L += ["", "## 头条数字：读人增益（bb）＝ EV(L1-x) − EV(L0)，\"看了人之后每手多赚多少个大盲\"", "",
          "| model | L1-text | L1-video |", "|---|---|---|"]
    for m in sorted({m for m, _ in agg}):
        if any(gains.get((m, l)) is not None for l in ("L1-text", "L1-video")):
            L.append(f"| {mname(m)} | {fmt(gains.get((m,'L1-text')),1)} | {fmt(gains.get((m,'L1-video')),1)} |")
    if hrows:
        n_j = len(hrows); n_false = sum(1 for r in hrows if r['judge'].get('exists') is False)
        n_unc = sum(1 for r in hrows if r['judge'].get('exists') == 'uncertain')
        L += ["", "## 线索幻觉核验（豆包 judge 对照整手视频判\"有没有\"）", "",
              f"- 共核验 {n_j} 条 cue：judge 判不存在 {n_false} 条、uncertain {n_unc} 条（不计入分母）",
              f"- 人工复核 {n_reviewed}/{n_j} 条（目标抽检 10–20%，在 annotator/ cue 核验页操作；人工改判优先于 judge）"]
    L += ["", "## 附录", "",
          "### 校准与一致性（防极端自信；Brier 无知基线 0.25）", "",
          "| model | layer | Brier | ECE | 3-trial p_call std |", "|---|---|---|---|---|"]
    for (m, layer), v in sorted(agg.items()):
        if v.get("n_items", 0):
            L.append(f"| {mname(m)} | {layer} | {fmt(v['brier'],3)} | {fmt(v['ece'],3)} | {fmt(v['consistency_std_mean'],3)} |")
    L += ["", "### 结果口径（不进主指标）", "", "| item | 实际行动 | 实际盈亏($) | 胜率口径 correct_call |", "|---|---|---|---|"]
    for i, t in truths.items():
        ac = t.get("actual", {})
        L.append(f"| {i} | {ac.get('hero_action','?')} | {ac.get('hero_result_usd','?')} | {t['correct_call']} |")
    L += ["", "### 说明", "",
          "- EV 捕获率 = EV / oracle EV（该模型层拿到了全知上界的多少）。",
          "- hard EV：action=p≥0.5 的硬决策口径。",
          "- 题数 < 5 时 bootstrap CI 无统计意义，仅验证链路。",
          "- 全部 transcript 见 runs jsonl（raw 字段）；judge 明细见 hallucination.jsonl。"]
    (ROOT / a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[report] → {ROOT / a.out}")


if __name__ == "__main__":
    main()
