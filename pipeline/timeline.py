"""行为时间轴：豆包（doubao-seed-2-1-pro-260628, Ark）看整手打码视频生成初稿 → 人工在 annotator/ 里校准。

用法：python -m pipeline.timeline --hand hand_0001 [--fps 2] [--mock]
产物：timeline.jsonl（事件行，含 source/human_verified 字段）、timeline.txt（渲染文本）、timeline_meta.json。
无 ARK_API_KEY 或 --mock 时输出占位（source=mock）。禁情绪词自动校验保留（banned_words_hit / meta.banned_hits）。
"""
from __future__ import annotations
import argparse, datetime, json, os, re, sys
from pathlib import Path
from .common import ffmpeg_exe, run, load_json, dump_json, hand_dir, PROMPTS, Timer, load_env, video_duration

load_env()
BANNED = None
FIELDS = ("gaze", "posture", "hands", "speech", "chips", "face")


def banned_words() -> list[str]:
    global BANNED
    if BANNED is None:
        txt = (PROMPTS / "timeline_prompt.md").read_text(encoding="utf-8")
        m = re.search(r"## 禁用词清单.*?\n(.*?)\n\n## ", txt, re.S)
        BANNED = [w.strip() for w in m.group(1).replace("\n", ",").split(",") if w.strip()]
    return BANNED


def violates(text: str) -> list[str]:
    t = text.lower()
    return [w for w in banned_words() if w.lower() in t]


def prompt_system() -> str:
    txt = (PROMPTS / "timeline_prompt.md").read_text(encoding="utf-8")
    return txt.split("## system", 1)[1].strip()


def low_fps_video(hd: Path, fps: float, stem: str = "clip_masked") -> Path:
    vid = hd / f"{stem}_{fps:g}fps.mp4"
    if not vid.exists():
        run([ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error", "-i", str(hd / f"{stem}.mp4"),
             "-vf", f"fps={fps},scale=960:-2", "-c:v", "libx264", "-preset", "veryfast", "-crf", "24",
             "-ac", "1", "-c:a", "aac", "-b:a", "48k", str(vid)])  # 保留音轨（mono 48k）：台词是重要观察信号
    return vid


def action_anchor_text(hd: Path) -> str:
    """action_timeline.jsonl → 行动锚点清单文本（v2 prompt 的参照骨架）。"""
    p = hd / "action_timeline.jsonl"
    if not p.exists():
        return ""
    rows = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except Exception:
            continue
        if e.get("t") is None:
            continue
        amt = f" ${e['amount']:g}" if e.get("amount") else ""
        rows.append(f"  t={e['t']}s [{e['street']}] {e['actor']} {e['action']}{amt}")
    if not rows:
        return ""
    return "这手牌的行动时间线（锚点骨架，描述反应时以此为参照）：\n" + "\n".join(rows) + "\n"


def anchor_times(hd: Path) -> tuple[float | None, float | None]:
    """从 action_timeline.jsonl 取 allin / hero 最终决定的秒数（剪辑版时间基准）。"""
    p = hd / "action_timeline.jsonl"
    allin_t = announce_t = None
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                e = json.loads(line)
            except Exception:
                continue
            if e.get("t") is None:
                continue
            if e.get("action") == "allin" and allin_t is None:
                allin_t = float(e["t"])
            if e.get("actor") == "hero" and e.get("action") in ("call", "fold"):
                announce_t = float(e["t"])
    return allin_t, announce_t


def player_desc(hd: Path) -> dict:
    """action_timeline 重跑时由豆包生成的 hero/villain 座位方位+外观特征（player_desc.json）。"""
    p = hd / "player_desc.json"
    if not p.exists():
        return {}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {k: str(d[k]) for k in ("hero", "villain") if isinstance(d.get(k), str) and d[k].strip()}


def user_text(hand: dict, dur: float, anchors: str = "", allin_t: float | None = None,
              announce_t: float | None = None, desc: dict | None = None) -> str:
    cam = hand.get("camera", {})
    pos = {"split_left": "分屏左侧", "split_right": "分屏右侧"}
    if desc and desc.get("hero") and desc.get("villain"):
        seat = (f"人物识别：hero（主角，面对全下做决定的一方）＝{desc['hero']}；"
                f"villain（对手，全下的一方）＝{desc['villain']}。")
    elif cam.get("hero_seat_crop") or cam.get("villain_seat_crop"):
        seat = (f"决胜时段为分屏画面：hero（主角，待决者）在{pos.get(cam.get('hero_seat_crop'), '左侧')}，"
                f"villain（对手，全下者）在{pos.get(cam.get('villain_seat_crop'), '右侧')}。")
    else:
        seat = ("hero（主角，待决者）与 villain（对手，全下者）的画面位置未标定，请从动作判断：推出全下筹码的是 villain，"
                "随后长考并宣布决定的是 hero。")
    seat += ("观察对象＝villain 的全部行为＋hero 的操作动作（下注/看牌/筹码/言语，即 hands/chips/speech 至少一项非 -）；"
             "不记录 hero 自身神态表情，不记录 other。who 对照上述外观特征判定为 villain/hero/both。"
             "观察内容需覆盖 gaze/posture/hands/speech/chips/face 六个字段（各字段都要有事件出现，不要集中在 hands 一列）。")
    if allin_t is None:
        allin_t = hand["timing_abs_sec"]["villain_allin"] - hand["timing_abs_sec"]["clip_start"]
    if announce_t is None:
        announce_t = hand["timing_abs_sec"]["hero_announce"] - hand["timing_abs_sec"]["clip_start"]
    return (f"这段视频约 {dur:.0f} 秒，是一整手牌。{seat}"
            f"对手大约在 t≈{allin_t:.0f}s 全下，"
            f"主角大约在 t≈{announce_t:.0f}s 宣布决定。\n"
            + anchors +
            "请按 system 要求输出整手牌的行为时间轴 JSON 行（只记变化事件、描述具体、note 挂行动锚点）。")


def parse_events(text: str, dur: float) -> list[dict]:
    events = []
    for m in re.finditer(r"\{[^{}]*\}", text):
        try:
            d = json.loads(m.group(0))
        except Exception:
            continue
        if not isinstance(d.get("t"), (int, float)) or d.get("who") not in ("villain", "hero", "both", "other"):
            continue
        d["t"] = round(min(max(float(d["t"]), 0.0), dur), 1)
        for f in FIELDS:
            d[f] = str(d.get(f, "-"))
        d["note"] = str(d.get("note", "") or "")
        events.append({k: d[k] for k in ("t", "who", *FIELDS, "note")})
    events.sort(key=lambda e: e["t"])
    return events


def mock_events(dur: float, allin_t: float) -> list[dict]:
    ev = []
    t = 0.0
    while t <= dur:
        ev.append({"t": round(t, 1), "who": "villain", "gaze": "看公共牌", "posture": "直立", "hands": "交叉",
                   "speech": "闭口", "chips": "不动", "face": "嘴角水平"})
        t += 4 if t < allin_t else 2
    return ev


def render_text(lines: list[dict]) -> str:
    rows = []
    for d in lines:
        parts = [f"{f}={d[f]}" for f in FIELDS if d.get(f) and d[f] != "-"]
        note = f"; note={d['note']}" if d.get("note") else ""
        tag = "  (mock)" if d.get("source") == "mock" else ""
        rows.append(f"t={d['t']:.1f}s [{d['who']}] " + "; ".join(parts) + note + tag)
    return "\n".join(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--hand", required=True)
    ap.add_argument("--fps", type=float, default=2.0)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--variant", choices=("masked", "hided"), default="masked",
                    help="hided=同事精遮罩剪辑版 clip_hided.mp4（时间基准与原切片不同，锚点取自剪辑版 action_timeline）")
    a = ap.parse_args(argv)
    hd = hand_dir(a.hand)
    hand = load_json(hd / "hand.json")
    tm = hand["timing_abs_sec"]
    stem = "clip_hided" if a.variant == "hided" else "clip_masked"
    if a.variant == "hided":
        dur = video_duration(hd / "clip_hided.mp4")
        at, an = anchor_times(hd)
        allin_t = at if at is not None else dur * 0.6
        announce_t = an  # None → user_text 不该走到（hided 必有 action_timeline），保底用 hand.json 会错，直接给 dur-5
        if announce_t is None:
            announce_t = max(allin_t, dur - 5)
    else:
        dur = tm["clip_end"] - tm["clip_start"]
        allin_t = tm["villain_allin"] - tm["clip_start"]
        announce_t = None
    use_mock = a.mock or not os.environ.get("ARK_API_KEY")
    usage = {}
    if use_mock:
        print("[timeline] no ARK_API_KEY or --mock → placeholder timeline (source=mock)", file=sys.stderr)
        events, model, source = mock_events(dur, allin_t), "mock", "mock"
    else:
        from runner import providers as P
        vid = low_fps_video(hd, a.fps, stem)
        print(f"[timeline] calling doubao with {vid.name} ({vid.stat().st_size/1e6:.1f} MB, fps={a.fps:g})", file=sys.stderr)
        anchors = action_anchor_text(hd)
        if not anchors:
            print("[timeline] note: no action_timeline.jsonl anchors (run pipeline.action_timeline first for better output)", file=sys.stderr)
        with Timer("timeline.doubao"):
            text, usage = P.ark_call(
                [{"role": "system", "content": prompt_system()},
                 {"role": "user", "content": P.video_content(vid, a.fps, user_text(hand, dur, anchors, allin_t, announce_t, player_desc(hd)))}],
                max_tokens=8000, temperature=0.2)
        events = parse_events(text, dur)
        model, source = P.model_id("doubao"), "doubao"
        if not events:
            raise SystemExit(f"[timeline] doubao returned no parseable events; raw head: {text[:400]}")
    banned_hits = []
    lines = []
    for e in events:
        bad = violates(json.dumps(e, ensure_ascii=False))
        d = {**e, "note": e.get("note", ""), "source": source, "human_verified": False}
        if bad:
            d["banned_words_hit"] = bad
            banned_hits.append({"t": e["t"], "hits": bad})
        lines.append(d)
    if a.variant == "hided":
        # 剪辑版时间基准不同：旧（precut）时间轴改名 *.precut.bak 保留
        for name in ("timeline.jsonl", "timeline.txt", "timeline_meta.json"):
            old, bak = hd / name, hd / f"{name}.precut.bak"
            if old.exists() and not bak.exists():
                bak.write_bytes(old.read_bytes())
                print(f"[timeline] precut {name} backed up → {bak.name}", file=sys.stderr)
    else:
        old = hd / "timeline.jsonl"
        bak = hd / "timeline_v1_backup.jsonl"
        if old.exists() and not bak.exists():
            bak.write_bytes(old.read_bytes())
            print(f"[timeline] old timeline backed up → {bak}", file=sys.stderr)
    (hd / "timeline.jsonl").write_text("\n".join(json.dumps(l, ensure_ascii=False) for l in lines) + "\n", encoding="utf-8")
    (hd / "timeline.txt").write_text(render_text(lines), encoding="utf-8")
    dump_json({"model": model, "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
               "human_verified": False, "n_events": len(lines), "banned_hits": banned_hits, "usage": usage,
               "video_fps": a.fps, "clip_duration": dur,
               **({"video_variant": "colleague_hided_recut"} if a.variant == "hided" else {})}, hd / "timeline_meta.json")
    print(f"[timeline] {len(lines)} events → {hd/'timeline.jsonl'} source={source} banned_hits={len(banned_hits)}")


if __name__ == "__main__":
    main()
