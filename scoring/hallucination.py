"""线索幻觉核验：豆包 judge 看整手打码视频，对 runs 里全部 cue 批量判"有没有"（每题一次视频调用）。

用法：python -m scoring.hallucination --runs results/runs.jsonl [--out results/hallucination.jsonl] [--sample-rate 0.15]
产物：results/hallucination.jsonl，每行一条 cue 的判定；human 字段留空，由 annotator/ 人工抽检改判
（sampled_for_review=true 的行为建议抽检对象，比例 10–20%）。
幻觉率 = judge 判 false / (true + false)，uncertain 不计入；按 (model, layer) 聚合，人工改判优先于 judge。
"""
from __future__ import annotations
import argparse, json, random, sys
from collections import defaultdict
from pathlib import Path
from pipeline.common import load_env, load_json, PROMPTS, ROOT, Timer

load_env()


def judge_prompt_system() -> str:
    txt = (PROMPTS / "judge_prompt.md").read_text(encoding="utf-8")
    return txt.split("## system", 1)[1].strip()


def collect_cues(records: list[dict]) -> dict:
    """item_id -> [(record, cue_index, cue), ...]，只收 schema 合法且非 mock 的 run。"""
    by_item = defaultdict(list)
    for r in records:
        if r.get("mock") or not r.get("parsed"):
            continue
        for i, c in enumerate(r["parsed"].get("cues") or []):
            if isinstance(c, dict) and isinstance(c.get("t"), (int, float)):
                by_item[r["item_id"]].append((r, i, c))
    return by_item


def judge_item(item_id: str, cues: list, items_dir: Path) -> list[dict]:
    from runner import providers as P
    hd = items_dir / item_id
    item = load_json(hd / "item.json")
    vid = hd / item["layers"]["L1-video"]["clip"]
    fps = item["layers"]["L1-video"]["fps"]
    lines = [f"视频时长 {item['timing']['clip_duration']:.0f}s，对手在 t≈{item['timing']['allin_t']}s 全下，主角在 t≈{item['timing']['announce_t']}s 宣布。待核验线索："]
    for n, (_r, _i, c) in enumerate(cues):
        lines.append(json.dumps({"idx": n, "t": c["t"], "who": c.get("who"), "type": c.get("type"), "observed": c.get("observed")}, ensure_ascii=False))
    with Timer(f"hallucination.judge[{item_id}]"):
        text, usage = P.ark_call(
            [{"role": "system", "content": judge_prompt_system()},
             {"role": "user", "content": P.video_content(vid, fps, "\n".join(lines))}],
            max_tokens=6000, temperature=0.0)
    import re
    m = re.search(r"\[.*\]", text, re.S)
    verdicts = {}
    if m:
        try:
            for v in json.loads(m.group(0)):
                verdicts[v.get("idx")] = {"exists": v.get("exists"), "evidence": str(v.get("evidence", ""))[:300]}
        except Exception:
            pass
    print(f"[hallucination] {item_id}: {len(cues)} cues, {len(verdicts)} verdicts, usage={usage}", file=sys.stderr)
    rows = []
    for n, (r, i, c) in enumerate(cues):
        rows.append({"item_id": item_id, "layer": r["layer"], "model": r["model"], "trial": r["trial"], "cue_index": i,
                     "cue": {k: c.get(k) for k in ("t", "who", "type", "observed", "direction", "weight")},
                     "judge": verdicts.get(n, {"exists": "uncertain", "evidence": "judge 未返回该条判定"}),
                     "human": None, "sampled_for_review": False})
    return rows


def hallucination_rate(rows: list[dict]) -> dict:
    """(model, layer) -> 幻觉率；人工改判(human.exists)优先于 judge。uncertain 不计入。"""
    num = defaultdict(int); den = defaultdict(int)
    for row in rows:
        v = (row.get("human") or {}).get("exists", None)
        if v is None:
            v = row["judge"].get("exists")
        if v is True or v is False:
            k = (row["model"], row["layer"])
            den[k] += 1
            if v is False:
                num[k] += 1
    return {k: num[k] / den[k] for k in den}


def load_rows(path: Path) -> list[dict] | None:
    if not path.exists():
        return None
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="results/runs.jsonl"); ap.add_argument("--items", default="items")
    ap.add_argument("--out", default="results/hallucination.jsonl")
    ap.add_argument("--sample-rate", type=float, default=0.15, help="建议人工抽检比例（10–20%）")
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args(argv)
    records = [json.loads(l) for l in (ROOT / a.runs).read_text(encoding="utf-8").splitlines() if l.strip()]
    by_item = collect_cues(records)
    if not by_item:
        print("[hallucination] no real (non-mock) cues found in runs; nothing to judge"); return
    all_rows = []
    for item_id, cues in sorted(by_item.items()):
        all_rows += judge_item(item_id, cues, ROOT / a.items)
    rng = random.Random(a.seed)
    n_sample = max(1, round(len(all_rows) * a.sample_rate))
    for idx in rng.sample(range(len(all_rows)), min(n_sample, len(all_rows))):
        all_rows[idx]["sampled_for_review"] = True
    out = ROOT / a.out
    out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in all_rows) + "\n", encoding="utf-8")
    rate = hallucination_rate(all_rows)
    print(f"[hallucination] {len(all_rows)} cues judged → {out}")
    for k, v in sorted(rate.items()):
        print(f"  {k[0]}/{k[1]}: rate={v:.2f}")


if __name__ == "__main__":
    main()
