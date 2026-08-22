#!/usr/bin/env python3
"""readroom-bench 本地可视化标注/校准工具（纯标准库）。

启动：python3 annotator/server.py --port 8765
浏览器打开 http://localhost:8765/

数据根默认为仓库根（本文件上一级目录），可用 --root 覆盖。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parent
STATIC_DIR = HERE / "static"

FIELDS6 = ["gaze", "posture", "hands", "speech", "chips", "face"]
ACT_STREETS = ("preflop", "flop", "turn", "river")
ACT_ACTORS = ("hero", "villain", "dealer", "other")
ACT_ACTIONS = ("deal", "check", "bet", "raise", "call", "fold", "allin", "showdown", "pot_awarded")
ID_RE = re.compile(r"^[A-Za-z0-9_\-]+$")

MIME = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
}

ROOT = DEFAULT_ROOT  # main() 里覆盖


# ---------------- 工具函数 ----------------

def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.unlink(tmp)
            except OSError:
                pass


def atomic_write_json(path: Path, obj) -> None:
    atomic_write_text(path, json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def load_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def load_jsonl(path: Path) -> list:
    """宽容读取 jsonl：坏行跳过。"""
    out = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    except FileNotFoundError:
        pass
    return out


def dump_jsonl(rows: list) -> str:
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)


def fmt_t(t: float) -> str:
    s = f"{float(t):.1f}"
    if abs(float(s) - float(t)) > 1e-9:
        s = f"{float(t):g}"
    return s


def normalize_event(e: dict) -> dict:
    """旧格式行缺字段按默认补；新格式原样保留。"""
    out = {}
    try:
        out["t"] = float(e.get("t", 0.0))
    except (TypeError, ValueError):
        out["t"] = 0.0
    who = e.get("who", "villain")
    out["who"] = who if who in ("villain", "hero", "both", "other") else "other"
    for k in FIELDS6:
        v = e.get(k, "-")
        out[k] = v if isinstance(v, str) and v != "" else "-"
    out["note"] = e.get("note", "") if isinstance(e.get("note", ""), str) else ""
    src = e.get("source", "doubao")
    out["source"] = src if src in ("doubao", "human") else "doubao"
    out["human_verified"] = bool(e.get("human_verified", False))
    return out


BLOCK_KEYS = ("t_start", "t_end", "anchor", "who_focus", "summary", "key_speech", "source", "human_verified")


def is_block(e: dict) -> bool:
    return isinstance(e, dict) and ("t_start" in e or "anchor" in e or "summary" in e)


def normalize_block(e: dict) -> dict:
    """聚类块行：{t_start,t_end,anchor,who_focus,summary,key_speech,source,human_verified}"""
    out = {}
    for k, d in (("t_start", 0.0), ("t_end", 0.0)):
        try:
            out[k] = float(e.get(k, d))
        except (TypeError, ValueError):
            out[k] = d
    if out["t_end"] < out["t_start"]:
        out["t_end"] = out["t_start"]
    out["anchor"] = str(e.get("anchor", "") or "")
    wf = e.get("who_focus", "villain")
    out["who_focus"] = wf if wf in ("villain", "hero", "both") else "villain"
    out["summary"] = str(e.get("summary", "") or "")
    ks = e.get("key_speech")
    out["key_speech"] = [str(x) for x in ks if str(x).strip()] if isinstance(ks, list) else []
    src = e.get("source", "doubao")
    out["source"] = src if src in ("doubao", "human") else "doubao"
    out["human_verified"] = bool(e.get("human_verified", False))
    if e.get("banned_words_hit"):
        out["banned_words_hit"] = e["banned_words_hit"]
    return out


def blocks_txt(blocks: list) -> str:
    lines = []
    for b in blocks:
        # 台词已融合进 summary；key_speech 仅作数据索引，不再单独渲染
        lines.append(f"[{b['t_start']:.1f}–{b['t_end']:.1f}s] {b['anchor']}（关注:{b['who_focus']}）：{b['summary']}")
    return "\n".join(lines) + "\n"


def normalize_action(e: dict) -> dict:
    """行动时间线行校验/补默认。"""
    out = {}
    try:
        out["t"] = None if e.get("t") is None else round(float(e["t"]), 1)
    except (TypeError, ValueError):
        out["t"] = None
    out["street"] = e.get("street") if e.get("street") in ACT_STREETS else "preflop"
    out["actor"] = e.get("actor") if e.get("actor") in ACT_ACTORS else "other"
    out["action"] = e.get("action") if e.get("action") in ACT_ACTIONS else "check"
    amt = e.get("amount")
    try:
        out["amount"] = None if amt in (None, "") else float(amt)
    except (TypeError, ValueError):
        out["amount"] = None
    src = e.get("source", "doubao")
    out["source"] = src if src in ("doubao", "human") else "doubao"
    out["human_verified"] = bool(e.get("human_verified", False))
    return out


def timeline_txt(events: list) -> str:
    lines = []
    for e in events:
        parts = [f"{k}={e[k]}" for k in FIELDS6 if e.get(k) and e[k] != "-"]
        lines.append(f"t={fmt_t(e['t'])}s [{e['who']}] " + "; ".join(parts))
    return "\n".join(lines) + "\n"


def parse_banned() -> list:
    p = ROOT / "prompts" / "timeline_prompt.md"
    if not p.exists():
        return []
    out, active = [], False
    for ln in p.read_text(encoding="utf-8").splitlines():
        if ln.startswith("##"):
            active = ln.lstrip("#").strip().startswith("禁用词清单")
            continue
        if active:
            for w in re.split(r"[,，\n]", ln):
                w = w.strip()
                if w:
                    out.append(w)
    return out


BET_ACTS = ("check", "bet", "raise", "call", "fold", "allin")


def regen_action_timeline(d: Path, bl: dict) -> int:
    """核对页保存 betting_line 时同步落盘 action_timeline.jsonl（runner/时间轴锚点消费方兼容）。

    下注类动作全部来自 betting_line（唯一编辑入口）；原文件里的非下注行
    （deal/showdown/pot_awarded）保留不动，按 t 重新排序合并。source 继承。
    """
    p = d / "action_timeline.jsonl"
    keep = [e for e in load_jsonl(p) if isinstance(e, dict) and e.get("action") not in BET_ACTS]
    rows = []
    for st in ACT_STREETS:
        blk = bl.get(st)
        if not isinstance(blk, dict):
            continue
        for a in blk.get("actions") or []:
            if not isinstance(a, dict):
                continue
            try:
                t = None if a.get("t") in (None, "") else round(float(a["t"]), 1)
            except (TypeError, ValueError):
                t = None
            amt = a.get("amount")
            rows.append({"t": t, "street": st,
                         "actor": a.get("actor") if a.get("actor") in ACT_ACTORS else "other",
                         "action": a.get("action") if a.get("action") in BET_ACTS else "check",
                         "amount": float(amt) if isinstance(amt, (int, float)) else None,
                         "source": a.get("source") if a.get("source") in ("doubao", "human") else "human",
                         "human_verified": True})
    merged = keep + rows
    srank = {s: i for i, s in enumerate(ACT_STREETS)}
    merged.sort(key=lambda e: (e.get("t") is None, e.get("t") if e.get("t") is not None else 0.0,
                               srank.get(e.get("street"), 0)))
    atomic_write_text(p, dump_jsonl(merged))
    return len(merged)


def merge_truth_defaults(obj: dict, d: Path) -> None:
    """truth.json 缺的展示字段用 hand.json / item.json / betting_line_extracted.json 合成默认值。

    - hero/villain 位置与开局筹码：hand.json table.*（若 truth 未填）
    - 玩家-筹码表：item.json table_players + internal_names（前端以 _ 前缀字段带出，保存时写回 item.json）
    - 桌上人数：table_players 长度
    - 按街下注线：betting_line_extracted.json（视频提取）+ hand.json betting_line（L0 已知信息）
    """
    hand = load_json(d / "hand.json", {}) or {}
    table = hand.get("table") or {}
    for k in ("hero_position", "villain_position", "hero_stack_start", "villain_stack_start"):
        if obj.get(k) in (None, ""):
            obj[k] = table.get(k)
    item_obj = load_json(d / "item.json", {}) or {}
    obj["_table_players"] = item_obj.get("table_players") or []
    obj["_internal_names"] = item_obj.get("internal_names") or {}
    # 原片跳转链接：youtube_id + 该手起始秒（hand.json，缺则查 clips_manifest_merged.json）
    yid = ((hand.get("source") or {}).get("youtube_id"))
    t0 = (hand.get("timing_abs_sec") or {}).get("clip_start")
    if not (yid and isinstance(t0, (int, float))):
        for row in load_json(ROOT / "data" / "clips_manifest_merged.json", []) or []:
            if isinstance(row, dict) and row.get("id") == d.name:
                yid = yid or row.get("youtube_id")
                t0 = t0 if isinstance(t0, (int, float)) else row.get("start_sec")
                break
    obj["_source_url"] = f"https://youtu.be/{yid}?t={int(t0)}" if yid and isinstance(t0, (int, float)) else None
    if not isinstance(obj.get("betting_line"), dict):
        obj["betting_line"] = build_betting_line_blocks(hand, load_json(d / "betting_line_extracted.json", {}) or {})


def suit_std(s: str) -> str:
    """♠♥♦♣ 花色符号 → 标准两字符记法（K♦ → Kd）。"""
    return re.sub(r"([2-9TJQKA])\s*([♠♥♦♣])",
                  lambda m: m.group(1) + {"♠": "s", "♥": "h", "♦": "d", "♣": "c"}[m.group(2)],
                  str(s or ""))


def board_by_street(board: str) -> dict:
    cards = re.findall(r"[2-9TJQKA][shdc]", suit_std(board))
    out = {}
    if len(cards) >= 3:
        out["flop"] = " ".join(cards[:3])
    if len(cards) >= 4:
        out["turn"] = cards[3]
    if len(cards) >= 5:
        out["river"] = cards[4]
    return out


def build_betting_line_blocks(hand: dict, extracted: dict) -> dict:
    """{street: {board, actions:[{t,actor,action,amount,source}], l0_text, source}}"""
    bs = board_by_street(hand.get("board", ""))
    l0_by_street = {l.get("street"): suit_std(str(l.get("actions", "")))
                    for l in hand.get("betting_line", []) if isinstance(l, dict)}
    out = {}
    ex_by_street = {l.get("street"): l for l in (extracted.get("betting_line") or []) if isinstance(l, dict)}
    for st in ACT_STREETS:
        ex = ex_by_street.get(st) or {}
        actions = []
        for e in ex.get("events", []) or []:
            if not isinstance(e, dict):
                continue
            actions.append({"t": e.get("t"), "actor": e.get("actor", "other"),
                            "action": e.get("action", "check"), "amount": e.get("amount"),
                            "source": "doubao"})
        out[st] = {"board": suit_std(ex.get("board") or bs.get(st, "")),
                   "actions": actions,
                   "l0_text": l0_by_street.get(st),
                   "source": "video_extracted" if actions else None}
    return out


def item_dir(item_id: str) -> Path | None:
    if not ID_RE.match(item_id):
        return None
    d = ROOT / "items" / item_id
    return d if d.is_dir() else None


# ---------------- HTTP handler ----------------

class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):  # 安静一点
        pass

    # ---- 应答 ----
    def send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def read_body_json(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(n) if n else b""
            return json.loads(raw.decode("utf-8")) if raw else None
        except Exception:
            return None

    # ---- 路由 ----
    def do_GET(self):
        self.route("GET")

    def do_POST(self):
        self.route("POST")

    def do_HEAD(self):
        self.route("HEAD")

    def route(self, method):
        try:
            path = unquote(urlparse(self.path).path)
            m = re.match(r"^/api/item/([^/]+)/(truth|timeline|action_timeline|l0|mask_review|recompute)$", path)
            if m:
                item_id, kind = m.group(1), m.group(2)
                d = item_dir(item_id)
                if d is None:
                    return self.send_json({"error": f"item 不存在: {item_id}"}, 404)
                fn = getattr(self, f"api_{kind}")
                return fn(method, item_id, d)
            if path == "/api/items" and method == "GET":
                return self.api_items()
            if path == "/api/hallucination":
                return self.api_hallucination(method)
            if path == "/api/banned" and method == "GET":
                return self.send_json(parse_banned())
            m = re.match(r"^/video/([^/]+)\.mp4$", path)
            if m and method in ("GET", "HEAD"):
                return self.serve_video(m.group(1), head=(method == "HEAD"))
            if method in ("GET", "HEAD"):
                return self.serve_static(path, head=(method == "HEAD"))
            return self.send_json({"error": "not found"}, 404)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            try:
                self.send_json({"error": f"server error: {e!r}"}, 500)
            except Exception:
                pass

    # ---- APIs ----
    def api_items(self):
        items_root = ROOT / "items"
        out = []
        if items_root.is_dir():
            for d in sorted(items_root.iterdir()):
                if not d.is_dir():
                    continue
                meta = load_json(d / "timeline_meta.json", {}) or {}
                truth = load_json(d / "truth.json", {}) or {}
                mask = load_json(d / "mask_review.json", {}) or {}
                out.append({
                    "id": d.name,
                    "has_timeline": (d / "timeline.jsonl").exists(),
                    "has_action_timeline": (d / "action_timeline.jsonl").exists(),
                    "has_truth": (d / "truth.json").exists(),
                    "has_video": any((d / n).exists() for n in ("clip_hided.mp4", "clip_automask.mp4", "clip_masked.mp4")),
                    "has_item_json": (d / "item.json").exists(),
                    "timeline_human_verified": bool(meta.get("human_verified", False)),
                    "truth_human_verified": bool(truth.get("human_verified_truth", False)),
                    "mask_checked": bool(mask.get("checked", False)),
                })
        return self.send_json(out)

    def api_truth(self, method, item_id, d):
        p = d / "truth.json"
        if method == "GET":
            obj = load_json(p)
            if obj is None:
                return self.send_json({"error": "truth.json 不存在或不可解析"}, 404)
            merge_truth_defaults(obj, d)
            return self.send_json(obj)
        body = self.read_body_json()
        if not isinstance(body, dict):
            return self.send_json({"error": "body 必须是 JSON 对象"}, 400)
        # _ 前缀键是服务端合成的展示字段，不落 truth.json；
        # 其中 _table_players / _internal_names 写进 item.json（存储只有角色+筹码；姓名独立、不进模型输入层）
        tp = body.pop("_table_players", None)
        names = body.pop("_internal_names", None)
        for k in [k for k in body if k.startswith("_")]:
            body.pop(k)
        if tp is not None or names is not None:
            item_p = d / "item.json"
            item_obj = load_json(item_p, None)
            if isinstance(item_obj, dict):
                ibak = d / "item.json.bak"
                if item_p.exists() and not ibak.exists():
                    shutil.copy2(item_p, ibak)
                if isinstance(tp, list):
                    item_obj["table_players"] = [
                        {"role": str(x.get("role", "other_1")),
                         "stack": x.get("stack") if isinstance(x.get("stack"), (int, float)) else None}
                        for x in tp if isinstance(x, dict)]
                if isinstance(names, dict):
                    item_obj["internal_names"] = {str(k): str(v) for k, v in names.items() if str(v).strip()}
                atomic_write_json(item_p, item_obj)
        bak = d / "truth.json.bak"
        if p.exists() and not bak.exists():
            shutil.copy2(p, bak)
        atomic_write_json(p, body)
        n_at = None
        if isinstance(body.get("betting_line"), dict):
            n_at = regen_action_timeline(d, body["betting_line"])
        return self.send_json({"ok": True, "n_action_timeline": n_at})

    def api_recompute(self, method, item_id, d):
        if method != "POST":
            return self.send_json({"error": "POST only"}, 405)
        body = self.read_body_json() or {}
        try:
            hero = str(body["hero"]).replace(" ", "")
            villain = str(body["villain"]).replace(" ", "")
            board = str(body.get("board", "")).replace(" ", "")
            pot = float(body["pot"])
            call = float(body["call"])
            bb = float(body.get("bb", 1.0))
        except (KeyError, TypeError, ValueError) as e:
            return self.send_json({"error": f"参数不合法: {e!r}"})
        py = ROOT / ".venv" / "bin" / "python"
        cmd = [str(py) if py.exists() else "python3", "-m", "pipeline.equity",
               "--hero", hero, "--villain", villain, "--board", board,
               "--pot", str(pot), "--call", str(call), "--bb", str(bb)]
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=180)
        except Exception as e:
            return self.send_json({"error": f"子进程启动失败: {e!r}"})
        if proc.returncode != 0:
            return self.send_json({"error": (proc.stderr or proc.stdout or "unknown error").strip()[-2000:]})
        try:
            return self.send_json(json.loads(proc.stdout))
        except Exception:
            return self.send_json({"error": f"stdout 解析失败: {proc.stdout[:2000]}"})

    def api_timeline(self, method, item_id, d):
        jsonl_p = d / "timeline.jsonl"
        meta_p = d / "timeline_meta.json"
        if method == "GET":
            raw = [e for e in load_jsonl(jsonl_p) if isinstance(e, dict)]
            fmt = "blocks" if any(is_block(e) for e in raw) else "rows"
            events = [normalize_block(e) if fmt == "blocks" else normalize_event(e) for e in raw]
            meta = load_json(meta_p, None)
            return self.send_json({"events": events, "meta": meta, "format": fmt})
        body = self.read_body_json()
        if not isinstance(body, dict) or not isinstance(body.get("events"), list):
            return self.send_json({"error": "body 需为 {events: [...]}"}, 400)
        raw = [e for e in body["events"] if isinstance(e, dict)]
        if any(is_block(e) for e in raw):
            events = [normalize_block(e) for e in raw]
            events.sort(key=lambda e: e["t_start"])
            for e in events:
                e["human_verified"] = True
            atomic_write_text(jsonl_p, dump_jsonl(events))
            txt = blocks_txt(events)
            atomic_write_text(d / "timeline.txt", txt)
        else:
            events = [normalize_event(e) for e in raw]
            events.sort(key=lambda e: e["t"])
            for e in events:
                e["human_verified"] = True
            atomic_write_text(jsonl_p, dump_jsonl(events))
            txt = timeline_txt(events)
            atomic_write_text(d / "timeline.txt", txt)
        meta = load_json(meta_p, None)
        if not isinstance(meta, dict):
            meta = {"model": None, "generated_at": None, "banned_hits": []}
        meta["human_verified"] = True
        meta["n_events"] = len(events)
        meta.setdefault("banned_hits", [])
        atomic_write_json(meta_p, meta)
        # 同步 item.json 的 L1-text
        item_p = d / "item.json"
        item_obj = load_json(item_p, None)
        synced = False
        if isinstance(item_obj, dict):
            l1 = (item_obj.get("layers") or {}).get("L1-text")
            if isinstance(l1, dict):
                l1["timeline_text"] = txt.rstrip("\n")
                l1["is_mock"] = False
                atomic_write_json(item_p, item_obj)
                synced = True
        return self.send_json({"ok": True, "n_events": len(events), "item_json_synced": synced})

    def api_action_timeline(self, method, item_id, d):
        p = d / "action_timeline.jsonl"
        if method == "GET":
            events = [normalize_action(e) for e in load_jsonl(p) if isinstance(e, dict)]
            return self.send_json({"events": events})
        body = self.read_body_json()
        if not isinstance(body, dict) or not isinstance(body.get("events"), list):
            return self.send_json({"error": "body 需为 {events: [...]}"}, 400)
        events = [normalize_action(e) for e in body["events"] if isinstance(e, dict)]
        events.sort(key=lambda e: e["t"] if e["t"] is not None else 1e9)
        for e in events:
            e["human_verified"] = True
        atomic_write_text(p, dump_jsonl(events))
        return self.send_json({"ok": True, "n_events": len(events)})

    def api_l0(self, method, item_id, d):
        p = d / "item.json"
        obj = load_json(p, None)
        if not isinstance(obj, dict):
            return self.send_json({"error": "item.json 不存在或不可解析"}, 404)
        layers = obj.setdefault("layers", {})
        l0 = layers.setdefault("L0", {})
        if method == "GET":
            return self.send_json({"text": l0.get("text", ""),
                                   "human_verified": bool(l0.get("human_verified", False))})
        body = self.read_body_json()
        if not isinstance(body, dict) or not isinstance(body.get("text"), str):
            return self.send_json({"error": "body 需为 {text: str}"}, 400)
        bak = d / "item.json.bak"
        if p.exists() and not bak.exists():
            shutil.copy2(p, bak)
        l0["text"] = body["text"]
        l0["human_verified"] = True
        atomic_write_json(p, obj)
        return self.send_json({"ok": True})

    def api_mask_review(self, method, item_id, d):
        p = d / "mask_review.json"
        if method == "GET":
            obj = load_json(p, None)
            if not isinstance(obj, dict):
                obj = {"item_id": item_id, "checked": False, "leaks": [], "updated_at": None}
            return self.send_json(obj)
        body = self.read_body_json()
        if not isinstance(body, dict):
            return self.send_json({"error": "body 必须是 JSON 对象"}, 400)
        leaks = []
        for lk in body.get("leaks", []) or []:
            if isinstance(lk, dict):
                try:
                    leaks.append({"t": float(lk.get("t", 0.0)), "note": str(lk.get("note", ""))})
                except (TypeError, ValueError):
                    continue
        obj = {"item_id": item_id, "checked": bool(body.get("checked", False)),
               "leaks": leaks, "updated_at": now_iso()}
        atomic_write_json(p, obj)
        return self.send_json({"ok": True, **obj})

    def api_hallucination(self, method):
        p = ROOT / "results" / "hallucination.jsonl"
        if method == "GET":
            return self.send_json(load_jsonl(p))
        body = self.read_body_json()
        if not isinstance(body, list):
            return self.send_json({"error": "body 必须是 JSON 数组"}, 400)
        atomic_write_text(p, dump_jsonl(body))
        return self.send_json({"ok": True, "n": len(body)})

    # ---- 视频（支持 Range/206）----
    def serve_video(self, item_id, head=False):
        d = item_dir(item_id)
        p = None
        if d:  # 优先同事精遮罩剪辑版（与重跑后的时间轴同一时间基准）
            for name in ("clip_hided.mp4", "clip_automask.mp4", "clip_masked.mp4"):
                if (d / name).exists():
                    p = d / name
                    break
        if p is None or not p.exists():
            return self.send_json({"error": "视频不存在"}, 404)
        size = p.stat().st_size
        rng = self.headers.get("Range")
        start, end = 0, size - 1
        status = 200
        if rng:
            m = re.match(r"^bytes=(\d*)-(\d*)$", rng.strip())
            if m and (m.group(1) or m.group(2)):
                if m.group(1):
                    start = int(m.group(1))
                    end = int(m.group(2)) if m.group(2) else size - 1
                else:  # 后缀范围 bytes=-N
                    n = int(m.group(2))
                    start = max(0, size - n)
                    end = size - 1
                if start >= size or start > end:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                end = min(end, size - 1)
                status = 206
        length = end - start + 1
        self.send_response(status)
        self.send_header("Content-Type", "video/mp4")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(length))
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        if head:
            return
        try:
            with open(p, "rb") as f:
                f.seek(start)
                remain = length
                while remain > 0:
                    chunk = f.read(min(65536, remain))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remain -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass

    # ---- 静态页 ----
    def serve_static(self, path, head=False):
        if path in ("/", ""):
            path = "/index.html"
        target = (STATIC_DIR / path.lstrip("/")).resolve()
        if not str(target).startswith(str(STATIC_DIR.resolve())) or not target.is_file():
            return self.send_json({"error": "not found"}, 404)
        data = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", MIME.get(target.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        # 防浏览器缓存旧 JS/CSS（Byron 遇到过疑似缓存问题）
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        if not head:
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError):
                pass


def main():
    global ROOT
    ap = argparse.ArgumentParser(description="readroom-bench 标注工具")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--root", default=str(DEFAULT_ROOT), help="数据根目录（默认仓库根）")
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    ROOT = Path(args.root).resolve()
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"[annotator] root={ROOT}")
    print(f"[annotator] http://localhost:{args.port}/")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()


if __name__ == "__main__":
    main()
