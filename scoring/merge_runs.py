"""合并主 runs 文件与分片：按 (item_id, layer, model, trial) 去重。
优先级：ok=true 优先；同 ok 状态取后出现者（分片视为更新）。拒绝 mock 记录。
用法：python -m scoring.merge_runs --main results/final_runs.jsonl --shards results/shards --out results/final_runs_merged.jsonl
"""
import argparse, json, sys
from pathlib import Path

def load(path):
    rows = []
    for ln in Path(path).read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        try:
            rows.append(json.loads(ln))
        except Exception:
            print(f"[merge] WARN bad json line in {path}", file=sys.stderr)
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--main", default="results/final_runs.jsonl")
    ap.add_argument("--shards", default="results/shards")
    ap.add_argument("--out", default="results/final_runs_merged.jsonl")
    a = ap.parse_args()
    files = [Path(a.main)] + sorted(Path(a.shards).glob("*.jsonl"))
    best = {}
    n_in, n_mock = 0, 0
    for f in files:
        if not f.exists():
            continue
        rows = load(f)
        print(f"[merge] {f}: {len(rows)} rows")
        for r in rows:
            n_in += 1
            if r.get("mock"):
                n_mock += 1
                continue
            k = (r["item_id"], r["layer"], r["model"], r["trial"])
            cur = best.get(k)
            if cur is None or (r.get("ok") and not cur.get("ok")) or (bool(r.get("ok")) == bool(cur.get("ok"))):
                if cur is not None and cur.get("ok") and not r.get("ok"):
                    continue
                best[k] = r
    out = Path(a.out)
    with out.open("w", encoding="utf-8") as fo:
        for k in sorted(best):
            fo.write(json.dumps(best[k], ensure_ascii=False) + "\n")
    n_ok = sum(1 for r in best.values() if r.get("ok"))
    print(f"[merge] in={n_in} mock_dropped={n_mock} unique={len(best)} ok={n_ok} → {out}")
    # 完备性检查：期望矩阵
    ITEMS = ["T1","T2","T3","T4","T5","F1","F2","F3","F4","F5"]
    expect = []
    for it in ITEMS:
        for m in ["claude","gpt","qwen","kimi","deepseek"]:
            for layer in ["L0","L1-text"]:
                expect.append((it, layer, m))
        for m in ["claude","gpt","qwen","kimi"]:
            expect.append((it, "L1-video", m))
    missing = []
    for it, layer, m in expect:
        have = [t for t in range(3) if (it, layer, m, t) in best]
        n_ok3 = sum(1 for t in have if best[(it, layer, m, t)].get("ok"))
        if len(have) < 3 or n_ok3 < 3:
            missing.append(f"{it}/{layer}/{m}: trials_present={len(have)} ok={n_ok3}")
    if missing:
        print(f"[merge] 不完整 cell {len(missing)} 个：")
        for s in missing:
            print("  ", s)
    else:
        print("[merge] 完备性检查通过：420 cell-trial 全 ok。")

if __name__ == "__main__":
    main()
