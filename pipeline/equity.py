"""纯 Python 胜率枚举：主角底牌 vs 对手真实底牌，在当前公共牌下的胜率（翻牌/转牌精确枚举，河牌直接比牌，翻前蒙特卡洛）。

用法：python -m pipeline.equity --hero AhKd --villain Ts9s --board 8dAd2c7cQd --pot 5125 --call 5450
返回 hero_equity（win + tie/2）、required_equity、correct_call。
"""
from __future__ import annotations
import argparse, itertools, random
from collections import Counter

RANKS = "23456789TJQKA"
SUITS = "cdhs"
RV = {r: i + 2 for i, r in enumerate(RANKS)}


def parse_cards(s: str) -> list[tuple[int, str]]:
    s = s.replace(" ", "").replace(",", "")
    assert len(s) % 2 == 0, f"bad cards {s}"
    out = []
    for i in range(0, len(s), 2):
        r, su = s[i].upper(), s[i + 1].lower()
        assert r in RV and su in SUITS, f"bad card {s[i:i+2]}"
        out.append((RV[r], su))
    return out


def eval5(cards) -> tuple:
    """5 张牌牌力元组，越大越强。类别：8 同花顺 7 四条 6 葫芦 5 同花 4 顺子 3 三条 2 两对 1 一对 0 高牌。"""
    ranks = sorted((c[0] for c in cards), reverse=True)
    flush = len({c[1] for c in cards}) == 1
    cnt = Counter(ranks)
    groups = sorted(cnt.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    uniq = sorted(set(ranks), reverse=True)
    straight_high = 0
    if len(uniq) == 5:
        if uniq[0] - uniq[4] == 4:
            straight_high = uniq[0]
        elif uniq == [14, 5, 4, 3, 2]:
            straight_high = 5
    if straight_high and flush:
        return (8, straight_high)
    if groups[0][1] == 4:
        return (7, groups[0][0], groups[1][0])
    if groups[0][1] == 3 and groups[1][1] == 2:
        return (6, groups[0][0], groups[1][0])
    if flush:
        return (5, *ranks)
    if straight_high:
        return (4, straight_high)
    if groups[0][1] == 3:
        return (3, groups[0][0], *[g[0] for g in groups[1:]])
    if groups[0][1] == 2 and groups[1][1] == 2:
        return (2, groups[0][0], groups[1][0], groups[2][0])
    if groups[0][1] == 2:
        return (1, groups[0][0], *[g[0] for g in groups[1:]])
    return (0, *ranks)


def best7(cards) -> tuple:
    return max(eval5(c) for c in itertools.combinations(cards, 5))


def showdown(hero, villain, board) -> float:
    """返回主角得分：1 赢 0.5 平 0 输"""
    h, v = best7(hero + board), best7(villain + board)
    return 1.0 if h > v else 0.5 if h == v else 0.0


def hero_equity(hero: str, villain: str, board: str, mc_samples: int = 20000, seed: int = 0) -> dict:
    H, V, B = parse_cards(hero), parse_cards(villain), parse_cards(board)
    assert len(H) == 2 and len(V) == 2 and len(B) in (0, 3, 4, 5)
    used = set(H + V + B)
    assert len(used) == 4 + len(B), "duplicate cards"
    deck = [(RV[r], s) for r in RANKS for s in SUITS if (RV[r], s) not in used]
    need = 5 - len(B)
    if need == 0:
        sc = showdown(H, V, B)
        return {"hero_equity": sc, "win": float(sc == 1), "tie": float(sc == 0.5), "lose": float(sc == 0),
                "method": "showdown", "n": 1, "street": "river"}
    if need <= 2:
        combos = list(itertools.combinations(deck, need)); method = "enumerate"
    else:
        rng = random.Random(seed)
        combos = [tuple(rng.sample(deck, need)) for _ in range(mc_samples)]; method = "monte_carlo"
    w = t = 0.0
    for extra in combos:
        sc = showdown(H, V, B + list(extra))
        if sc == 1: w += 1
        elif sc == 0.5: t += 1
    n = len(combos)
    return {"hero_equity": (w + t / 2) / n, "win": w / n, "tie": t / n, "lose": (n - w - t) / n,
            "method": method, "n": n, "street": {0: "preflop", 3: "flop", 4: "turn"}[len(B)]}


def truth(hero: str, villain: str, board: str, pot_before: float, to_call: float, bb: float = 1.0) -> dict:
    """框架 §5：required_equity = 跟注额/(底池+跟注额)，其中底池含对手已推入的 all-in 额。"""
    eq = hero_equity(hero, villain, board)
    pot_total = pot_before + to_call  # 对手推入后的底池
    req = to_call / (pot_total + to_call)
    ev_call_bb = (eq["hero_equity"] * pot_total - (1 - eq["hero_equity"]) * to_call) / bb
    return {**eq, "pot_before_allin": pot_before, "pot_after_allin": pot_total, "to_call": to_call,
            "required_equity": req, "correct_call": eq["hero_equity"] >= req,
            "ev_call_bb": ev_call_bb, "ev_fold_bb": 0.0}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--hero", required=True); ap.add_argument("--villain", required=True)
    ap.add_argument("--board", default=""); ap.add_argument("--pot", type=float, required=True)
    ap.add_argument("--call", type=float, required=True); ap.add_argument("--bb", type=float, default=1.0)
    a = ap.parse_args(argv)
    import json; print(json.dumps(truth(a.hero, a.villain, a.board, a.pot, a.call, a.bb), indent=2))


if __name__ == "__main__":
    main()
