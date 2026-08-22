#!/usr/bin/env bash
# 一键跑通样例手牌。用法：bash run_all.sh [hand_id] [--local /path/raw_window.mp4]
# 无 ARK/SYNAPSE key 时时间轴与模型自动 mock；有 key 时 timeline/deepseek/doubao 走真实 API。
set -euo pipefail
cd "$(dirname "$0")"
HAND=${1:-hand_0001}; shift || true
PY=.venv/bin/python
[ -x "$PY" ] || { ~/.local/bin/uv venv -q .venv --python 3.11 && ~/.local/bin/uv pip install -q --python .venv/bin/python imageio-ffmpeg "yt-dlp>=2026.8" pillow numpy; }
t0=$(date +%s)
$PY -m pipeline.fetch --hand "$HAND" "$@"              # 下载窗口（或 --local 复用）+ 整手切片 clip_raw.mp4
$PY -m pipeline.mask  --hand "$HAND" --check 6         # 打码（含 hand.json mask_windows 分段区域）→ clip_masked.mp4 + mask_check/
$PY -m pipeline.timeline --hand "$HAND"                # 豆包整手视频时间轴初稿（无 key → mock）；人工校准用 annotator/
$PY -m pipeline.build_item --hand "$HAND"              # item.json + truth.json + 2fps 视频
$PY tests/test_equity.py && $PY tests/test_scoring.py
$PY -m runner.run --dry-run --only "$HAND"             # 请求预览 results/requests_preview/
$PY -m runner.run --mock --trials 3 --only "$HAND" --out results/runs_mock.jsonl   # mock 链路验证
$PY -m scoring.report --runs results/runs_mock.jsonl --out results/report_mock.md
echo "[run_all] done in $(( $(date +%s) - t0 ))s"
echo "真跑（花钱，注意视频调用次数）："
echo "  $PY -m runner.run --models deepseek --layers L0 L1-text --trials 3 --only $HAND --out results/runs.jsonl"
echo "  $PY -m runner.run --models doubao --layers L0 L1-video --trials 3 --only $HAND --out results/runs.jsonl"
echo "  $PY -m scoring.hallucination --runs results/runs.jsonl && $PY -m scoring.report"
echo "标注工具：python3 annotator/server.py --port 8765  →  http://localhost:8765/"
