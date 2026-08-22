"""共用工具：路径、ffmpeg、配置加载、计时。"""
from __future__ import annotations
import json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / "items"
CONFIGS = ROOT / "configs"
PROMPTS = ROOT / "prompts"


def ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return os.environ.get("FFMPEG", "ffmpeg")


def run(cmd: list[str], quiet: bool = True) -> subprocess.CompletedProcess:
    kw = dict(stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) if quiet else {}
    p = subprocess.run(cmd, **kw)
    if p.returncode != 0:
        sys.stderr.write((p.stderr or "")[-2000:])
        raise SystemExit(f"command failed ({p.returncode}): {' '.join(cmd[:6])}...")
    return p


def load_json(p) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8"))


def dump_json(obj, p) -> None:
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def hand_dir(hand_id: str) -> Path:
    return ITEMS / hand_id


def hms_to_sec(s) -> float:
    if isinstance(s, (int, float)):
        return float(s)
    parts = [float(x) for x in str(s).split(":")]
    sec = 0.0
    for p in parts:
        sec = sec * 60 + p
    return sec


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


class Timer:
    """with Timer('step') as t: ...; t.elapsed"""
    def __init__(self, name: str):
        self.name = name
    def __enter__(self):
        self.t0 = time.time(); return self
    def __exit__(self, *a):
        self.elapsed = time.time() - self.t0
        print(f"[timer] {self.name}: {self.elapsed:.1f}s", file=sys.stderr)


def load_env(path=None) -> None:
    """轻量 .env 加载（不覆盖已存在的环境变量；key 不打印）。"""
    p = Path(path) if path else ROOT / ".env"
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def video_duration(p) -> float:
    """ffmpeg -i 解析视频时长（秒）。"""
    import re as _re, subprocess as _sp
    pr = _sp.run([ffmpeg_exe(), "-i", str(p)], capture_output=True, text=True)
    m = _re.search(r"Duration: (\d+):(\d+):([\d.]+)", pr.stderr)
    if not m:
        raise SystemExit(f"cannot probe duration of {p}")
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
