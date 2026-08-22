"""组装题目 JSON（框架 §3 输入分层 + §4 输出约定 + §5 真值）。

用法：python -m pipeline.build_item --hand hand_0001 [--video-fps 2]
产物：items/<hand>/item.json（给模型的各层输入 + 文件路径；不含对手底牌/姓名）、items/<hand>/truth.json（真值，仅打分用）。
"""
from __future__ import annotations
import argparse
from .common import ffmpeg_exe, run, load_json, dump_json, hand_dir, Timer
from .equity import truth as equity_truth

def pretty(cards: str) -> str:
    """统一标准两字符记法（Ah Kd Ts 9c），空格分隔；禁用 ♠♥♦♣ 花色符号。"""
    cards = cards.replace(" ", "")
    return " ".join(cards[i:i + 2] for i in range(0, len(cards), 2))


def money(x) -> str:
    return f"${x:,}" if isinstance(x, (int, float)) else "未知"


def l0_text(h: dict, t: dict) -> str:
    tb = h["table"]
    n_players = f"{tb['players']} 人桌" if tb.get("players") else "人数未知"
    cover = tb.get("cover_note", "对手盖过你")
    lines = [
        f"牌局：{tb['game']}，{n_players}，盲注 {tb['blinds']}（1 bb = ${tb['bb']}）。",
        f"你（Hero）位置：{tb.get('hero_position') or '未知'}，本手开始筹码 {money(tb.get('hero_stack_start'))}。对手（Villain）位置：{tb.get('villain_position') or '未知'}，本手开始筹码 {money(tb.get('villain_stack_start'))}（{cover}）。",
        f"你的底牌：{pretty(h['hero_cards'])}。",
        "下注线：",
    ]
    for s in h["betting_line"]:
        b = f"（{s['board']}）" if s.get("board") else ""
        lines.append(f"  - {s['street']}{b}：{s['actions']}")
    board_line = (f"当前公共牌：{pretty(h['board'])}（{h['street_at_allin']}）。" if h["board"]
                  else "当前无公共牌（preflop 全下）。")
    behind = h.get("hero_stack_behind")
    remain = f"（跟注后你剩 {money(behind - h['hero_to_call'])}）" if isinstance(behind, (int, float)) else ""
    lines += [
        board_line,
        f"对手全下前底池：${h['pot_before_allin']:,}；对手全下额：${h['allin_amount']:,}；你需跟注：${h['hero_to_call']:,}{remain}。",
        f"跟注后总底池：${t['pot_after_allin'] + h['hero_to_call']:,}；所需胜率（跟注额 ÷ (底池+跟注额)）= {t['required_equity']:.1%}。",
    ]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--hand", required=True)
    ap.add_argument("--video-fps", type=float, default=2.0)
    a = ap.parse_args(argv)
    hd = hand_dir(a.hand); h = load_json(hd / "hand.json")
    t = equity_truth(h["hero_cards"], h["villain_cards"], h["board"], h["pot_before_allin"], h["hero_to_call"], h["table"]["bb"])
    with Timer("build_item.video_fps"):
        vid = hd / f"clip_masked_{a.video_fps:g}fps.mp4"
        if not vid.exists():
            run([ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error", "-i", str(hd / "clip_masked.mp4"),
                 "-vf", f"fps={a.video_fps},scale=960:-2", "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-an", str(vid)])
    tm = h["timing_abs_sec"]; dur = tm["clip_end"] - tm["clip_start"]
    timeline_txt = (hd / "timeline.txt").read_text(encoding="utf-8") if (hd / "timeline.txt").exists() else ""
    tl_meta = load_json(hd / "timeline_meta.json") if (hd / "timeline_meta.json").exists() else {}
    tl_lines = [__import__("json").loads(l) for l in (hd / "timeline.jsonl").read_text().splitlines() if l.strip()] if (hd / "timeline.jsonl").exists() else []
    item = {
        "item_id": a.hand, "schema_version": "0.2",
        "source": {"show": h["source"]["show"], "youtube_id": h["source"]["youtube_id"],
                    "clip_abs_sec": [tm["clip_start"], tm["clip_end"]], "note": "只分发时间戳与打码产物，不分发原片；切片=整手（发牌→收池）"},
        "street_at_allin": h["street_at_allin"],
        "layers": {
            "L0": {"text": l0_text(h, t)},
            "L1-text": {"timeline_text": timeline_txt, "timeline_file": "timeline.jsonl",
                        "is_mock": any(l.get("source") == "mock" or l.get("mock") for l in tl_lines) if tl_lines else None,
                        "human_verified": bool(tl_meta.get("human_verified"))},
            "L1-video": {"clip": vid.name, "fps": a.video_fps, "duration_sec": dur, "clip_masked_full_fps": "clip_masked.mp4"},
        },
        "timing": {"allin_t": round(tm["villain_allin"] - tm["clip_start"], 1),
                   "announce_t": round(tm["hero_announce"] - tm["clip_start"], 1), "clip_duration": dur},
        "output_schema": {"p_call": "float 0..1", "action": "call|fold", "cues": [{"t": "float", "who": "villain|hero|other",
                          "type": "gaze|posture|hands|speech|chips|face", "observed": "str", "direction": "strong|weak|neutral", "weight": "float 0..1"}],
                          "rationale": "str ≤150字", "recognized": "bool"},
        "layer_model_matrix": {"L0": ["claude", "gpt", "qwen", "kimi", "deepseek"], "L1-text": ["claude", "gpt", "qwen", "kimi", "deepseek"],
                               "L1-video": ["qwen", "kimi", "doubao (provisional)"]},
        "truth_file": "truth.json",
    }
    truth = {"item_id": a.hand, "hero_cards": h["hero_cards"], "villain_cards": h["villain_cards"], "board": h["board"],
             **{k: t[k] for k in ("hero_equity", "win", "tie", "lose", "method", "n", "street", "required_equity", "correct_call", "ev_call_bb", "ev_fold_bb", "pot_before_allin", "pot_after_allin", "to_call")},
             "bb": h["table"]["bb"], "actual": h["actual"],
             "players": h.get("players", {"hero": "unknown", "villain": "unknown"}),
             "difficulty_tier": "TBD (按 L0 基线分档)"}
    dump_json(item, hd / "item.json"); dump_json(truth, hd / "truth.json")
    print(f"[build_item] item.json + truth.json written; hero_equity={t['hero_equity']:.3f} required={t['required_equity']:.3f} correct_call={t['correct_call']}")
    print(item["layers"]["L0"]["text"])


if __name__ == "__main__":
    main()
