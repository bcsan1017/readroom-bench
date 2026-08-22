"""下载片段：按 hand.json 的 youtube_id + download_window 下载原始窗口（不分发），再按 clip_start/clip_end 切出 clip_raw.mp4。

用法：
  python -m pipeline.fetch --hand hand_0001            # yt-dlp 下载窗口 + 切片
  python -m pipeline.fetch --hand hand_0001 --local /path/raw.mp4 --local-offset 450  # 已有本地窗口文件时复用
说明：yt-dlp 需 >= 2026.08 版本，否则 googlevideo 对 ffmpeg 分段下载返回 403。
"""
from __future__ import annotations
import argparse, shutil, sys
from pathlib import Path
from .common import ffmpeg_exe, run, load_json, hand_dir, hms_to_sec, Timer, ROOT


def ytdlp_download(video_id: str, start: str, end: str, out: Path) -> Path:
    ffdir = ROOT / ".venv" / "ffbin"
    ffdir.mkdir(parents=True, exist_ok=True)
    link = ffdir / "ffmpeg"
    if not link.exists():
        link.symlink_to(ffmpeg_exe())
    ytdlp = ROOT / ".venv" / "bin" / "yt-dlp"
    cmd = [str(ytdlp) if ytdlp.exists() else "yt-dlp", "--ffmpeg-location", str(ffdir),
           "-f", "bv*[height<=720][ext=mp4]+ba[ext=m4a]/b[height<=720]/b",
           "--download-sections", f"*{start}-{end}", "--force-keyframes-at-cuts",
           "-o", str(out.with_suffix("")) + ".%(ext)s", f"https://www.youtube.com/watch?v={video_id}"]
    print("[fetch]", " ".join(cmd), file=sys.stderr)
    run(cmd, quiet=False)
    return out


def cut(src: Path, start: float, end: float, out: Path) -> Path:
    """精确重编码切片（保证帧时间轴从 0 开始、便于抽帧）。"""
    out.parent.mkdir(parents=True, exist_ok=True)
    run([ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{start:.3f}", "-to", f"{end:.3f}",
         "-i", str(src), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-movflags", "+faststart", str(out)])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--hand", required=True)
    ap.add_argument("--local", help="已下载的窗口文件（跳过 yt-dlp）")
    ap.add_argument("--local-offset", type=float, help="本地文件 0s 对应的原视频秒数（默认=download_window 起点）")
    a = ap.parse_args(argv)
    hd = hand_dir(a.hand)
    hand = load_json(hd / "hand.json")
    src = hand["source"]; tm = hand["timing_abs_sec"]
    win_start = hms_to_sec(src["download_window"][0])
    raw = hd / "raw_window.mp4"
    with Timer("fetch.download"):
        if a.local:
            if Path(a.local).resolve() != raw.resolve():
                shutil.copy(a.local, raw)
            offset = a.local_offset if a.local_offset is not None else win_start
        else:
            ytdlp_download(src["youtube_id"], src["download_window"][0], src["download_window"][1], raw)
            offset = win_start
    with Timer("fetch.cut"):
        cut(raw, tm["clip_start"] - offset, tm["clip_end"] - offset, hd / "clip_raw.mp4")
    print(f"[fetch] wrote {hd/'clip_raw.mp4'} (clip t=0 ↔ abs {tm['clip_start']}s, offset {offset})")


if __name__ == "__main__":
    main()
