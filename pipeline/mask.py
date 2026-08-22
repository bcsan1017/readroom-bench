"""打码：按 configs/mask_1280x720.json 用 ffmpeg drawbox/boxblur 遮住底牌 UI、胜率条、姓名条、logo。

用法：
  python -m pipeline.mask --hand hand_0001 [--config configs/mask_1280x720.json] [--check 3]
输出 items/<hand>/clip_masked.mp4；--check N 额外抽 N 帧到 items/<hand>/mask_check/ 供人工核验。
"""
from __future__ import annotations
import argparse
from pathlib import Path
from .common import ffmpeg_exe, run, load_json, hand_dir, CONFIGS, Timer


def build_filter(cfg: dict, windows: dict | None = None) -> str:
    """windows: region_name -> [[t0,t1],...]（相对切片秒）。enabled=false 但在 windows 里的区域按时间段打码。"""
    parts = []
    color = cfg.get("box_color", "0x000000")
    blur = int(cfg.get("blur_strength", 20))
    windows = windows or {}
    for r in cfg["regions"]:
        wins = windows.get(r["name"])
        if not r.get("enabled", True) and not wins:
            continue
        x0, y0, x1, y1 = r["box"]
        w, h = x1 - x0, y1 - y0
        mode = r.get("mode", cfg.get("default_mode", "box"))
        enable = ""
        if wins:
            expr = "+".join(f"between(t,{a:g},{b:g})" for a, b in wins)
            enable = f":enable='{expr}'"
        if mode == "blur":
            # crop→blur→overlay 组合；为简洁用 boxblur 的 enable 无法限定区域，这里用 split/overlay
            ov_en = f":enable='{'+'.join(f'between(t,{a:g},{b:g})' for a, b in wins)}'" if wins else ""
            parts.append(f"split[a][b];[b]crop={w}:{h}:{x0}:{y0},boxblur=lr={blur}:lp=2:cr={max(1,blur//2)}:cp=2[bl];[a][bl]overlay={x0}:{y0}{ov_en}")
        else:
            parts.append(f"drawbox=x={x0}:y={y0}:w={w}:h={h}:color={color}:t=fill{enable}")
    return ",".join(parts) if parts else "null"


def apply_mask(src: Path, dst: Path, cfg: dict, fps: float | None = None, windows: dict | None = None) -> None:
    vf = build_filter(cfg, windows)
    if fps:
        vf += f",fps={fps}"
    run([ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error", "-i", str(src), "-vf", vf,
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "copy", str(dst)])


def sample_frames(video: Path, out_dir: Path, n: int) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    # 取均匀 n 帧
    p = run([ffmpeg_exe(), "-i", str(video), "-hide_banner"], quiet=True) if False else None
    import subprocess, re
    pr = subprocess.run([ffmpeg_exe(), "-i", str(video)], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", pr.stderr)
    dur = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
    outs = []
    for i in range(n):
        t = dur * (i + 0.5) / n
        o = out_dir / f"check_{i:02d}_t{t:05.1f}.png"
        run([ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", str(o)])
        outs.append(o)
    return outs


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--hand", required=True)
    ap.add_argument("--config", default=str(CONFIGS / "mask_1280x720.json"))
    ap.add_argument("--check", type=int, default=0)
    a = ap.parse_args(argv)
    hd = hand_dir(a.hand); cfg = load_json(a.config)
    hand = load_json(hd / "hand.json")
    windows = {k: v for k, v in (hand.get("mask_windows") or {}).items() if not k.startswith("_")}
    with Timer("mask.apply"):
        apply_mask(hd / "clip_raw.mp4", hd / "clip_masked.mp4", cfg, windows=windows)
    print(f"[mask] wrote {hd/'clip_masked.mp4'} windows={windows} filter={build_filter(cfg, windows)[:120]}...")
    if a.check:
        outs = sample_frames(hd / "clip_masked.mp4", hd / "mask_check", a.check)
        print("[mask] check frames:", *map(str, outs), sep="\n  ")


if __name__ == "__main__":
    main()
