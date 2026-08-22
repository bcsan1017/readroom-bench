"""抽帧：事件锚点 + 心跳（2s；对手 all-in 10s 后降为 4s），每帧输出全景 + 对手脸部 crop，并写 frames_manifest.json。

用法：python -m pipeline.frames --hand hand_0001 [--video clip_masked.mp4] [--heartbeat 2 --slow 4 --slow-after 10]
时间轴：帧时间 t 以切片起点为 0（切片起点 = all-in 前 5s）。
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
from PIL import Image
from .common import ffmpeg_exe, run, load_json, dump_json, hand_dir, CONFIGS, Timer


def anchor_times(hand: dict) -> dict[str, float]:
    tm = hand["timing_abs_sec"]; c0 = tm["clip_start"]
    allin = tm["villain_allin"] - c0
    ann = tm["hero_announce"] - c0
    a = {"allin": allin, "allin_plus1": allin + 1.0, "decision_minus1": ann - 1.0, "announce": ann}
    if "hero_first_look" in tm:
        a["hero_first_look"] = tm["hero_first_look"] - c0
    return a


def schedule(hand: dict, hb: float, slow: float, slow_after: float, dedupe: float = 0.4) -> list[dict]:
    tm = hand["timing_abs_sec"]; dur = tm["clip_end"] - tm["clip_start"]
    allin = tm["villain_allin"] - tm["clip_start"]
    pts = [{"t": round(v, 2), "kind": "anchor", "label": k} for k, v in anchor_times(hand).items()]
    t = 0.0
    while t <= dur + 1e-6:
        pts.append({"t": round(t, 2), "kind": "heartbeat", "label": f"hb_{t:.0f}"})
        t += hb if t < allin + slow_after else slow
    pts.sort(key=lambda p: (p["t"], 0 if p["kind"] == "anchor" else 1))
    out = []
    for p in pts:
        if out and abs(p["t"] - out[-1]["t"]) < dedupe:
            if p["kind"] == "anchor" and out[-1]["kind"] != "anchor":
                out[-1] = p  # 锚点优先
            continue
        out.append(p)
    return out


def grab(video: Path, t: float, out: Path) -> None:
    run([ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1", str(out)])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--hand", required=True)
    ap.add_argument("--video", default="clip_masked.mp4")
    ap.add_argument("--heartbeat", type=float, default=2.0)
    ap.add_argument("--slow", type=float, default=4.0)
    ap.add_argument("--slow-after", type=float, default=10.0)
    ap.add_argument("--seats", default=str(CONFIGS / "seats.json"))
    a = ap.parse_args(argv)
    hd = hand_dir(a.hand); hand = load_json(hd / "hand.json"); seats = load_json(a.seats)
    video = hd / a.video
    fdir = hd / "frames"; fdir.mkdir(exist_ok=True)
    vcrop = seats["crops"][hand["camera"]["villain_seat_crop"]]["box"]
    hcrop = seats["crops"][hand["camera"]["hero_seat_crop"]]["box"]
    face_size = tuple(seats.get("face_out_size", [320, 400]))
    sched = schedule(hand, a.heartbeat, a.slow, a.slow_after)
    frames = []
    with Timer("frames.extract"):
        for i, p in enumerate(sched):
            full = fdir / f"f{i:03d}_t{p['t']:05.1f}_full.png"
            grab(video, p["t"], full)
            im = Image.open(full)
            face = fdir / f"f{i:03d}_t{p['t']:05.1f}_villain.png"
            im.crop(vcrop).resize(face_size).save(face)
            frames.append({"idx": i, "t": p["t"], "t_abs": round(p["t"] + hand["timing_abs_sec"]["clip_start"], 2),
                           "kind": p["kind"], "label": p["label"],
                           "full": str(full.relative_to(hd)), "villain_face": str(face.relative_to(hd)),
                           "villain_crop_box": vcrop, "hero_crop_box": hcrop})
    manifest = {"hand_id": a.hand, "video": a.video, "clip_t0_abs": hand["timing_abs_sec"]["clip_start"],
                "allin_t": anchor_times(hand)["allin"], "announce_t": anchor_times(hand)["announce"],
                "params": {"heartbeat": a.heartbeat, "slow": a.slow, "slow_after": a.slow_after},
                "n_frames": len(frames), "n_images": len(frames) * 2, "frames": frames}
    dump_json(manifest, hd / "frames_manifest.json")
    print(f"[frames] {len(frames)} timestamps × 2 images → {fdir}; anchors={[f['label'] for f in frames if f['kind']=='anchor']}")


if __name__ == "__main__":
    main()
