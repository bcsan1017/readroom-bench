"""L1-video 抽帧近似（claude/gpt via wodex）：不吃视频的模型用帧序列参赛。

抽帧规则（定稿 2026-08-22）：
- 决策窗口（对手 all-in 前 5s → 主角宣布行动）每 2s 一帧；窗口外每 6s 一帧；
- 全景单视角（不做脸部 crop）；源用 items/<id>/clip_hided.mp4（全帧率打码片）；
- 压缩为 360 宽 jpg（q=4，实测 ~15KB/张）——wodex WAF 实测（2026-08-22）claude-opus-5 与
  gpt-5.6-sol 单请求 80 张（payload 1.38MB）均通过，上限 ≥80；
- 自动适配：若帧数超 --max-frames（默认 60，留安全余量），等比拉大两档间隔直至不超。

输出：items/<id>/vframes/f###_t<秒>.jpg + items/<id>/vframes/manifest.json

用法：python -m pipeline.frames_for_video_layer --items T1 T2 ...   # 或 --all
"""
from __future__ import annotations
import argparse
from pathlib import Path
from .common import ROOT, ffmpeg_exe, run, load_json, dump_json, now_iso

WINDOW_STEP = 2.0   # 决策窗口内间隔
OUTSIDE_STEP = 6.0  # 窗口外间隔
WINDOW_PRE = 5.0    # 窗口起点 = all-in 前 5s
MAX_FRAMES = 60     # wodex 实测 ≥80 张可过，60 留余量
DEDUPE = 0.8        # 两帧过近去重


def schedule(allin_t: float, announce_t: float, dur: float,
             win_step: float = WINDOW_STEP, out_step: float = OUTSIDE_STEP) -> list[dict]:
    """窗口 [allin-5, announce] 内 win_step 取帧，窗口外 out_step 取帧；含 announce 时刻帧。"""
    w0, w1 = max(0.0, allin_t - WINDOW_PRE), min(announce_t, dur)
    pts = []
    t = 0.0
    while t < w0 - 1e-6:
        pts.append({"t": round(t, 2), "kind": "outside"})
        t += out_step
    t = w0
    while t <= w1 + 1e-6:
        pts.append({"t": round(min(t, dur), 2), "kind": "window"})
        t += win_step
    if pts[-1]["t"] < round(w1, 2) - 1e-6:
        pts.append({"t": round(w1, 2), "kind": "window"})  # 宣布瞬间帧必含
    t = pts[-1]["t"] + out_step
    while t <= dur + 1e-6:
        pts.append({"t": round(min(t, dur), 2), "kind": "outside"})
        t += out_step
    out = []
    for p in pts:
        if out and p["t"] - out[-1]["t"] < DEDUPE:
            if p["kind"] == "window" and out[-1]["kind"] == "outside":
                out[-1] = p
            continue
        out.append(p)
    return out


def adaptive_schedule(allin_t: float, announce_t: float, dur: float,
                      max_frames: int = MAX_FRAMES) -> tuple[list[dict], float, float]:
    """帧数超上限时等比拉大两档间隔（×1.25 递进）直至 ≤max_frames。"""
    scale = 1.0
    while True:
        ws, os_ = WINDOW_STEP * scale, OUTSIDE_STEP * scale
        sched = schedule(allin_t, announce_t, dur, ws, os_)
        if len(sched) <= max_frames:
            return sched, ws, os_
        scale *= 1.25


def build_vframes(item_dir: Path, max_frames: int = MAX_FRAMES, width: int = 360, q: int = 4) -> dict:
    item = load_json(item_dir / "item.json")
    tm = item["timing"]
    video = item_dir / item["layers"]["L1-video"].get("clip_full_fps", "clip_hided.mp4")
    if not video.exists():
        raise FileNotFoundError(f"{item['item_id']}: {video} 不存在")
    sched, ws, os_ = adaptive_schedule(tm["allin_t"], tm["announce_t"], tm["clip_duration"], max_frames)
    vdir = item_dir / "vframes"
    vdir.mkdir(exist_ok=True)
    for old in vdir.glob("f*.jpg"):
        old.unlink()
    frames = []
    for i, p in enumerate(sched):
        f = vdir / f"f{i:03d}_t{p['t']:06.1f}.jpg"
        run([ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{p['t']:.3f}",
             "-i", str(video), "-frames:v", "1", "-vf", f"scale={width}:-2", "-q:v", str(q), str(f)])
        frames.append({"idx": i, "t": p["t"], "kind": p["kind"], "file": str(f.relative_to(item_dir))})
    total_kb = sum((item_dir / f["file"]).stat().st_size for f in frames) // 1024
    manifest = {"item_id": item["item_id"], "source_video": video.name, "generated_at": now_iso(),
                "rule": {"window_pre_sec": WINDOW_PRE, "window_step": ws, "outside_step": os_,
                         "max_frames": max_frames, "width": width, "jpg_q": q,
                         "adapted": ws != WINDOW_STEP},
                "allin_t": tm["allin_t"], "announce_t": tm["announce_t"], "duration": tm["clip_duration"],
                "n_frames": len(frames), "n_window": sum(1 for f in frames if f["kind"] == "window"),
                "total_jpg_kb": total_kb, "frames": frames}
    dump_json(manifest, vdir / "manifest.json")
    print(f"[vframes] {item['item_id']}: {len(frames)} 帧（窗口 {manifest['n_window']}）"
          f" step={ws:g}/{os_:g}s {total_kb}KB → {vdir}")
    return manifest


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", nargs="*", help="item id 列表（如 T1 T2）")
    ap.add_argument("--all", action="store_true", help="所有含 clip_hided.mp4 的 item")
    ap.add_argument("--max-frames", type=int, default=MAX_FRAMES)
    a = ap.parse_args(argv)
    items_dir = ROOT / "items"
    if a.all:
        dirs = sorted(d for d in items_dir.iterdir()
                      if (d / "item.json").exists() and (d / "clip_hided.mp4").exists())
    else:
        dirs = [items_dir / i for i in (a.items or [])]
    for d in dirs:
        build_vframes(d, a.max_frames)


if __name__ == "__main__":
    main()
