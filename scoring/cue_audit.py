"""人工抽检清单：从 hallucination.jsonl 分层抽 15%——每 (model, layer) 至少 2 条，judge 判 false 的优先入样。
同时把入样行的 sampled_for_review 写回 hallucination.jsonl。
用法：python -m scoring.cue_audit --hallucination results/hallucination.jsonl --out results/cue_audit_sample.md
"""
import argparse, json, random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hallucination", default="results/hallucination.jsonl")
    ap.add_argument("--out", default="results/cue_audit_sample.md")
    ap.add_argument("--rate", type=float, default=0.15)
    ap.add_argument("--min-per-cell", type=int, default=2)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    hp = ROOT / a.hallucination
    rows = [json.loads(l) for l in hp.read_text(encoding="utf-8").splitlines() if l.strip()]
    rng = random.Random(a.seed)
    by_cell = defaultdict(list)
    for idx, r in enumerate(rows):
        by_cell[(r["model"], r["layer"])].append(idx)
    target = max(round(len(rows) * a.rate), a.min_per_cell * len(by_cell))
    chosen = set()
    def pick(pool, k):
        pool = [i for i in pool if i not in chosen]
        rng.shuffle(pool)
        chosen.update(pool[:k])
    # 1) 每 cell 至少 min_per_cell，false 优先
    for cell, idxs in sorted(by_cell.items()):
        falses = [i for i in idxs if rows[i]["judge"].get("exists") is False]
        pick(falses, a.min_per_cell)
        short = a.min_per_cell - len([i for i in idxs if i in chosen])
        if short > 0:
            pick(idxs, short)
    # 2) 全局补足到 target，false 优先
    all_false = [i for i in range(len(rows)) if rows[i]["judge"].get("exists") is False]
    if len(chosen) < target:
        pick(all_false, target - len(chosen))
    if len(chosen) < target:
        pick(list(range(len(rows))), target - len(chosen))
    for i, r in enumerate(rows):
        r["sampled_for_review"] = i in chosen
    hp.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    sel = sorted(chosen, key=lambda i: (rows[i]["item_id"], rows[i]["model"], rows[i]["layer"], rows[i]["trial"], rows[i]["cue_index"]))
    L = [f"# cue 人工抽检清单（{len(sel)}/{len(rows)} ≈ {len(sel)/max(1,len(rows)):.0%}；每模型×层 ≥{a.min_per_cell} 条，judge=false 优先）",
         "",
         "> 口径（Byron 拍板，2026-08-23）：cue 真实性判定由豆包 judge 自动完成（true/false/uncertain 三档）；",
         "> 标注人在时间轴人工校准过程中已核阅全部视频素材，未设置独立的 cue 抽检环节。本清单保留生成，供事后复核参考。",
         "", "如需复核：在 annotator/ 页签④逐条核对，人工改判写回 hallucination.jsonl 的 human.exists（人工优先于 judge）。", "",
         "| # | item | model | layer | trial | t | who/type | observed | judge | evidence |", "|---|---|---|---|---|---|---|---|---|---|"]
    for n, i in enumerate(sel, 1):
        r = rows[i]; c = r["cue"]; j = r["judge"]
        ob = str(c.get("observed", "")).replace("|", "/")[:60]
        ev = str(j.get("evidence", "")).replace("|", "/")[:60]
        L.append(f"| {n} | {r['item_id']} | {r['model']} | {r['layer']} | {r['trial']} | {c.get('t')} | {c.get('who')}/{c.get('type')} | {ob} | {j.get('exists')} | {ev} |")
    n_false = sum(1 for i in sel if rows[i]["judge"].get("exists") is False)
    L += ["", f"入样构成：judge=false {n_false} 条 / true {sum(1 for i in sel if rows[i]['judge'].get('exists') is True)} 条 / uncertain {sum(1 for i in sel if rows[i]['judge'].get('exists')=='uncertain')} 条。"]
    (ROOT / a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[cue_audit] {len(sel)} sampled → {ROOT / a.out}")

if __name__ == "__main__":
    main()
