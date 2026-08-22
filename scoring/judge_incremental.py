"""增量幻觉 judge：按 item 分组、状态化去重，可多轮补增量。
每轮：从 runs 文件集合收 cues（按 (item,layer,model,trial) 取最新记录）→ 与 results/judge/<item>.jsonl
已判集合对比 → 新增 cues 每 item 一次豆包视频调用批判 → append 到该 item 文件。
用法：python -m scoring.judge_incremental --runs results/final_runs.jsonl results/shards/*.jsonl --models claude gpt deepseek
最终合并：python -m scoring.judge_incremental --export results/hallucination.jsonl
"""
import argparse, json, sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from pipeline.common import load_env, ROOT
from .hallucination import judge_item

load_env()
JUDGE_DIR = ROOT / "results" / "judge"


def latest_records(files):
    best = {}
    for f in files:
        p = Path(f)
        if not p.exists():
            continue
        for ln in p.read_text(encoding="utf-8").splitlines():
            if not ln.strip():
                continue
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get("mock") or not r.get("parsed"):
                continue
            k = (r["item_id"], r["layer"], r["model"], r["trial"])
            cur = best.get(k)
            if cur is None or (r.get("ok") and not cur.get("ok")) or bool(r.get("ok")) == bool(cur.get("ok")):
                if cur is not None and cur.get("ok") and not r.get("ok"):
                    continue
                best[k] = r
    return best


def load_state(item_id):
    p = JUDGE_DIR / f"{item_id}.jsonl"
    rows = []
    if p.exists():
        for ln in p.read_text(encoding="utf-8").splitlines():
            if ln.strip():
                rows.append(json.loads(ln))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="*", default=["results/final_runs.jsonl"])
    ap.add_argument("--items", default="items")
    ap.add_argument("--models", nargs="*", help="只判这些模型（默认全部）")
    ap.add_argument("--only", nargs="*", help="只判这些 item")
    ap.add_argument("--export", help="把 results/judge/*.jsonl 合并导出为单一 hallucination jsonl 后退出")
    a = ap.parse_args()
    if a.export:
        rows = []
        for p in sorted(JUDGE_DIR.glob("*.jsonl")):
            rows += [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
        out = ROOT / a.export
        out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
        print(f"[judge-inc] export {len(rows)} rows → {out}")
        return
    JUDGE_DIR.mkdir(parents=True, exist_ok=True)
    best = latest_records([ROOT / f if not str(f).startswith("/") else f for f in a.runs])
    by_item = defaultdict(list)
    for (item_id, layer, model, trial), r in sorted(best.items()):
        if a.models and model not in a.models:
            continue
        if a.only and item_id not in a.only:
            continue
        for i, c in enumerate(r["parsed"].get("cues") or []):
            if isinstance(c, dict) and isinstance(c.get("t"), (int, float)):
                by_item[item_id].append((r, i, c))
    def run_item(item_id):
        done = {(r["model"], r["layer"], r["trial"], r["cue_index"]) for r in load_state(item_id)}
        new = [(r, i, c) for (r, i, c) in by_item[item_id] if (r["model"], r["layer"], r["trial"], i) not in done]
        if not new:
            return f"{item_id}: no new cues ({len(done)} already judged)"
        rows = None
        for attempt in range(3):  # 429/空判定重试（判定数组解析失败时不落占位行，否则会挡住重判）
            try:
                cand = judge_item(item_id, new, ROOT / a.items)
            except Exception as e:
                err = f"{type(e).__name__}: {e}"
                import time as _t; _t.sleep(45 * (attempt + 1))
                continue
            n_ret = sum(1 for r in cand if r["judge"].get("evidence") != "judge 未返回该条判定")
            if n_ret == 0:
                err = f"judge returned no parseable verdicts ({len(cand)} cues)"
                import time as _t; _t.sleep(20)
                continue
            rows = cand
            break
        if rows is None:
            return f"{item_id}: JUDGE CALL FAILED after retries: {err}"
        with (JUDGE_DIR / f"{item_id}.jsonl").open("a", encoding="utf-8") as fo:
            for row in rows:
                fo.write(json.dumps(row, ensure_ascii=False) + "\n")
        n_unc = sum(1 for r in rows if r["judge"].get("exists") == "uncertain")
        return f"{item_id}: +{len(rows)} rows judged (uncertain {n_unc})"

    with ThreadPoolExecutor(max_workers=3) as ex:  # ark 并发（总控 2026-08-23 指令：2-3 并发）
        futs = {ex.submit(run_item, i): i for i in sorted(by_item)}
        for fut in as_completed(futs):
            print(f"[judge-inc] {fut.result()}", flush=True)

if __name__ == "__main__":
    main()
