"""指标实现（框架 v0.2 §5）。

主指标（期望收益 EV，单位 bb，越高越好）：
    score_ev = p_call × EV(call) + (1 − p_call) × EV(fold)=0
读人增益（头条数字）= EV(L1-x) − EV(L0)，单位 bb（"L1 相对 L0 多赚多少 bb"）。
附录：Brier（防极端自信）、ECE、一致性 std、hard 决策 EV（action=p≥0.5）。
log loss / 区分度已删（v0.2 拍板）。
"""
from __future__ import annotations
import random
from collections import defaultdict

EPS = 1e-6


def score_ev_bb(p, truth):
    """主指标：按 p_call 混合行动的期望收益（bb）。EV(call) 来自真值（对手真实底牌算出的胜率×底池）。"""
    return p * truth["ev_call_bb"] + (1 - p) * truth.get("ev_fold_bb", 0.0)


def oracle_ev_bb(truth):
    """全知最优行动的期望收益（bb），EV 的上界。"""
    return max(truth["ev_call_bb"], truth.get("ev_fold_bb", 0.0))


def hard_ev_bb(p, truth):
    """硬决策口径：action = p≥0.5。"""
    return truth["ev_call_bb"] if p >= 0.5 else truth.get("ev_fold_bb", 0.0)


def brier(ps, ys):
    return sum((p - y) ** 2 for p, y in zip(ps, ys)) / len(ps)


def ece(ps, ys, bins=10):
    """Expected Calibration Error（等宽 bins）+ 可靠性曲线点（附录用）。"""
    tot = len(ps); e = 0.0; curve = []
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        idx = [i for i, p in enumerate(ps) if (lo <= p < hi) or (b == bins - 1 and p == 1.0)]
        if not idx:
            continue
        conf = sum(ps[i] for i in idx) / len(idx); acc = sum(ys[i] for i in idx) / len(idx)
        e += len(idx) / tot * abs(conf - acc); curve.append({"bin": [lo, hi], "n": len(idx), "conf": conf, "acc": acc})
    return e, curve


def std(xs):
    if len(xs) < 2:
        return 0.0
    m = sum(xs) / len(xs)
    return (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5


def bootstrap_ci(values_by_item: dict, stat, n=1000, seed=0, alpha=0.05):
    """对题目重采样（每题一个聚合值）。values_by_item: item_id -> (p, y, truth)。"""
    keys = list(values_by_item); rng = random.Random(seed)
    if not keys:
        return (float("nan"), float("nan"))
    samples = []
    for _ in range(n):
        pick = [values_by_item[rng.choice(keys)] for _ in keys]
        samples.append(stat(pick))
    samples.sort()
    return samples[int(alpha / 2 * n)], samples[min(n - 1, int((1 - alpha / 2) * n))]


def aggregate(records: list[dict], truths: dict) -> dict:
    """records: runner jsonl 行；truths: item_id -> truth。返回 (model, layer) -> 指标 dict。"""
    groups = defaultdict(lambda: defaultdict(list))  # (model,layer) -> item -> [p...]
    recognized = defaultdict(set); failures = defaultdict(int); n_trials = defaultdict(int)
    for r in records:
        k = (r["model"], r["layer"]); n_trials[k] += 1
        if not r.get("ok") or not r.get("parsed"):
            failures[k] += 1; continue
        if r["parsed"].get("recognized"):
            recognized[k].add(r["item_id"])
        groups[k][r["item_id"]].append(float(r["parsed"]["p_call"]))
    out = {}
    for k, by_item in groups.items():
        items = [i for i in by_item if i not in recognized[k] and i in truths]
        if not items:
            out[k] = {"n_items": 0, "note": "all items excluded/missing truth"}; continue
        pm = {i: sum(by_item[i]) / len(by_item[i]) for i in items}
        ps = [pm[i] for i in items]; ys = [1.0 if truths[i]["correct_call"] else 0.0 for i in items]
        ev = sum(score_ev_bb(pm[i], truths[i]) for i in items) / len(items)
        oracle = sum(oracle_ev_bb(truths[i]) for i in items) / len(items)
        vb = {i: (pm[i], ys[j], truths[i]) for j, i in enumerate(items)}
        ci = bootstrap_ci(vb, lambda pick: sum(score_ev_bb(x[0], x[2]) for x in pick) / len(pick))
        e, curve = ece(ps, ys)
        out[k] = {
            "n_items": len(items), "n_trials": n_trials[k], "n_failed": failures[k], "n_recognized_excluded": len(recognized[k]),
            # 主指标
            "ev_bb": ev, "ev_bb_ci95": ci, "oracle_ev_bb": oracle,
            "ev_capture": (ev / oracle) if oracle > EPS else None,
            "ev_bb_hard": sum(hard_ev_bb(pm[i], truths[i]) for i in items) / len(items),
            "action_accuracy": sum((pm[i] >= 0.5) == bool(truths[i]["correct_call"]) for i in items) / len(items),
            # 附录
            "brier": brier(ps, ys), "ece": e, "reliability": curve,
            "consistency_std_mean": sum(std(by_item[i]) for i in items) / len(items),
            "hallucination_rate": None,  # 由 scoring/hallucination.py 的 judge 结果填充
        }
    return out


def reading_gain(agg: dict) -> dict:
    """读人增益 = EV(L1-x) − EV(L0)，单位 bb，按模型。正值 = 读人层比盲答层多赚。"""
    gains = {}
    models = {m for m, _ in agg}
    for m in models:
        e0 = agg.get((m, "L0"), {}).get("ev_bb")
        if e0 is None:
            continue
        for layer in ("L1-text", "L1-video"):
            e = agg.get((m, layer), {}).get("ev_bb")
            if e is not None:
                gains[(m, layer)] = e - e0
    return gains
