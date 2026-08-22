"""已知结果单测（数值来自常见赔率表/手算）。运行：.venv/bin/python -m pytest -q  或  .venv/bin/python tests/test_equity.py"""
import math, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from pipeline.equity import eval5, parse_cards, hero_equity, truth, best7


def approx(a, b, tol=0.005):
    assert abs(a - b) <= tol, (a, b)


def test_eval5_categories():
    assert eval5(parse_cards("AsKsQsJsTs"))[0] == 8
    assert eval5(parse_cards("5d4c3h2sAd"))[0] == 4 and eval5(parse_cards("5d4c3h2sAd"))[1] == 5  # 轮子顺
    assert eval5(parse_cards("9c9d9h9sKd"))[0] == 7
    assert eval5(parse_cards("9c9d9hKsKd"))[0] == 6
    assert eval5(parse_cards("2h7h9hJhKh"))[0] == 5
    assert eval5(parse_cards("AcAdKhKsQd")) > eval5(parse_cards("AcAdQhQsKd"))
    assert best7(parse_cards("AhKd8dAd2c7cQd")) > best7(parse_cards("Ts9s8dAd2c7cQd"))


def test_river_showdown_sample_hand():
    t = truth("AhKd", "Ts9s", "8dAd2c7cQd", 5125, 5450)
    assert t["hero_equity"] == 1.0 and t["correct_call"] is True
    approx(t["required_equity"], 5450 / (5125 + 5450 + 5450), 1e-9)


def test_turn_enumeration():
    # 主角 AhKd 顶对 vs 对手 Ts9s 开口顺听（8d Ad 2c 7c，J 或 6 各 4 张 = 8 outs/44）
    r = hero_equity("AhKd", "Ts9s", "8dAd2c7c")
    assert r["method"] == "enumerate" and r["n"] == 44
    approx(r["hero_equity"], 36 / 44, 1e-9)


def test_flop_enumeration_known():
    # 翻牌 AhKd vs Ts9s on 8d Ad 2c：对手仅后门顺/后门两对，主角约 94%（手算：runner 顺 48/990 + 跑出 TT/99 等 ≈ 6%）
    r = hero_equity("AhKd", "Ts9s", "8dAd2c")
    assert r["method"] == "enumerate" and r["n"] == 990
    assert 0.93 < r["hero_equity"] < 0.95, r


def test_flop_set_vs_flushdraw():
    # 经典：翻牌 set vs 同花听牌 ≈ 73-75% vs 25-27%（取决于具体牌）
    r = hero_equity("8c8h", "AsJs", "8s5s2d")
    assert 0.70 < r["hero_equity"] < 0.78, r


def test_preflop_mc_aa_vs_kk():
    r = hero_equity("AsAd", "KhKc", "", mc_samples=20000, seed=1)
    assert r["method"] == "monte_carlo"
    approx(r["hero_equity"], 0.82, 0.02)


def test_correct_call_threshold():
    # 主角 25% 胜率、赔率要求 30% → 不该跟
    t = truth("2c3d", "AsAd", "", 100, 60)  # preflop MC；23o vs AA ≈ 12-13%
    assert t["correct_call"] is False


if __name__ == "__main__":
    g = dict(globals())
    for k, f in g.items():
        if k.startswith("test_"):
            f(); print("ok", k)
