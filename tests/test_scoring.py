import sys, pathlib, random
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from scoring.metrics import brier, ece, score_ev_bb, oracle_ev_bb, hard_ev_bb, aggregate, reading_gain, bootstrap_ci


def test_ev_score():
    # 主指标：score = p × EV(call) + (1−p) × 0
    assert score_ev_bb(1.0, {"ev_call_bb": 10, "ev_fold_bb": 0}) == 10
    assert score_ev_bb(0.0, {"ev_call_bb": 10, "ev_fold_bb": 0}) == 0
    assert score_ev_bb(0.5, {"ev_call_bb": 10, "ev_fold_bb": 0}) == 5
    assert score_ev_bb(1.0, {"ev_call_bb": -4, "ev_fold_bb": 0}) == -4   # 错误跟注被扣分
    assert oracle_ev_bb({"ev_call_bb": -4, "ev_fold_bb": 0}) == 0        # 该 fold 的题上界=0
    assert oracle_ev_bb({"ev_call_bb": 211.5, "ev_fold_bb": 0}) == 211.5
    assert hard_ev_bb(0.49, {"ev_call_bb": 10, "ev_fold_bb": 0}) == 0
    assert hard_ev_bb(0.51, {"ev_call_bb": 10, "ev_fold_bb": 0}) == 10
    # 附录指标
    assert abs(brier([0.5, 0.5], [1, 0]) - 0.25) < 1e-9
    assert brier([1.0, 0.0], [1, 0]) == 0.0
    assert abs(ece([0.9, 0.9, 0.1, 0.1], [1, 1, 0, 0])[0] - 0.1) < 1e-9


def test_aggregate_synthetic():
    rng = random.Random(0); truths = {}; recs = []
    for i in range(12):
        y = i % 2 == 0
        truths[f"h{i}"] = {"correct_call": y, "ev_call_bb": 20 if y else -20, "ev_fold_bb": 0}
        for layer, skill in (("L0", 0.0), ("L1-video", 0.3)):
            for t in range(3):
                p = min(1, max(0, (0.5 + (skill if y else -skill)) + rng.gauss(0, 0.1)))
                recs.append({"item_id": f"h{i}", "layer": layer, "model": "m", "ok": True, "parsed": {"p_call": p, "recognized": False}})
    recs.append({"item_id": "h0", "layer": "L0", "model": "m", "ok": True, "parsed": {"p_call": 0.9, "recognized": True}})
    agg = aggregate(recs, truths)
    assert agg[("m", "L0")]["n_recognized_excluded"] == 1 and agg[("m", "L0")]["n_items"] == 11
    # 会读人的层 EV 更高（读人增益为正，单位 bb）
    g = reading_gain(agg)[("m", "L1-video")]
    assert g > 1.0, g
    # 无知模型（p≈0.5）的 EV ≈ 0（对半题 ±20bb 抵消附近）
    assert abs(agg[("m", "L0")]["ev_bb"]) < 3.0
    lo, hi = agg[("m", "L1-video")]["ev_bb_ci95"]
    assert lo <= agg[("m", "L1-video")]["ev_bb"] <= hi
    assert 0 < agg[("m", "L1-video")]["ev_capture"] <= 1


def test_hand_0001_numbers():
    # 样例题：ev_call=211.5bb、correct_call=True → p=1 拿满 211.5，p=0 拿 0
    t = {"ev_call_bb": 211.5, "ev_fold_bb": 0.0, "correct_call": True}
    assert abs(score_ev_bb(0.35, t) - 74.025) < 1e-9


if __name__ == "__main__":
    for k, f in list(globals().items()):
        if k.startswith("test_"):
            f(); print("ok", k)
