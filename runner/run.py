"""五模型 × 各层 × n trial 统一 runner。

用法：
  python -m runner.run --items items --layers L0 L1-text L1-video --models all --trials 3 --out results/runs.jsonl
  python -m runner.run ... --dry-run        # 只组装请求并写 results/requests_preview/，不调用
  python -m runner.run --ping               # 有 key 的 provider 做一次最小连通性测试
  python -m runner.run ... --freeze-check   # 跑前校验各 item truth.json 的 human_verified；未冻结则中止（--force 可跳过）
输出 jsonl 每行：{item_id, layer, model, trial, ok, raw, parsed, schema_errors, usage, latency_s, attempts, mock, truth 不含}

批跑硬化（2026-08-22）：
- 断点续跑：--out 里已有的 (item,layer,model,trial) 记录默认跳过（--retry-failed 只重跑 ok=false 的；--no-resume 全部重跑）
- 失败重试 ≤2 次，指数退避（5s/10s + 抖动）；重试次数记在 attempts
- 每完成一条即 append+flush 落盘，不攒内存
- per-gateway 并发：dashscope/moonshot/synapse/ark 各 2 并发；wodex 串行 + 请求间 1s 间隔（防 Cloudflare WAF）
"""
from __future__ import annotations
import argparse, json, os, random, re, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from . import providers as P

ROOT = Path(__file__).resolve().parent.parent
PROMPT = (ROOT / "prompts" / "model_prompt.md").read_text(encoding="utf-8")

# provider → 网关（限速/并发按网关算：claude+gpt 共用 wodex 时共享 1 并发）
GATEWAY = {"qwen": "dashscope", "kimi": "moonshot", "deepseek": "synapse", "doubao": "ark",
           "claude": "anthropic", "gpt": "openai"}
GATEWAY_WORKERS = {"wodex": 1, "dashscope": 2, "moonshot": 2, "synapse": 2, "ark": 2,
                   "anthropic": 2, "openai": 2}
GATEWAY_GAP = {"wodex": 1.0}  # 请求间最小间隔（秒）
MAX_RETRIES = 2


def gateway_of(name: str) -> str:
    return "wodex" if P._use_wodex(name) else GATEWAY[name]


def prompt_parts() -> dict:
    sys_ = PROMPT.split("## system")[1].split("## user")[0].strip()
    user = PROMPT.split("## user")[1].split("## layer_blocks")[0].strip()
    blocks = {}
    for sec in PROMPT.split("## layer_blocks")[1].split("### ")[1:]:
        name, _, body = sec.partition("\n")
        blocks[name.strip()] = body.strip()
    return {"system": sys_, "user": user, "blocks": blocks}


def l0_text(item: dict) -> str:
    """取 L0 牌理文本。兼容两种结构：旧版 layers.L0.text（str），
    以及 L0 重构后的结构化字段（分街下注线/位置/table_players 等）——重构完成后以 items/T2/item.json 为准。"""
    L0 = item["layers"]["L0"]
    if isinstance(L0, str):
        return L0
    if isinstance(L0, dict):
        for k in ("text", "l0_text", "prompt_text", "rendered_text", "rendered"):
            v = L0.get(k)
            if isinstance(v, str) and v.strip():
                return v
        # 结构化新版兜底：把所有字符串字段按出现顺序拼接（新结构落定后请显式适配）
        parts = [v for v in L0.values() if isinstance(v, str) and v.strip()]
        if parts:
            return "\n".join(parts)
    raise KeyError(f"item {item.get('item_id')}: 无法从 layers.L0 取得 L0 文本（结构已变？请更新 runner.run.l0_text）")


def build_spec(item: dict, item_dir: Path, layer: str, max_images: int | None = None, model: str | None = None) -> dict:
    pp = prompt_parts(); L = item["layers"]; tm = item["timing"]
    block = pp["blocks"][layer]
    images, video, video_fps, input_mode = [], None, None, None
    if layer == "L1-text":
        block = block.replace("{TIMELINE_TEXT}", L["L1-text"]["timeline_text"] or "(空)")
    elif layer == "L1-vision":
        imgs = L["L1-vision"]["images"]
        if max_images:
            imgs = imgs[:: max(1, len(imgs) // (max_images // 2))][: max_images // 2]
        for f in imgs:
            images.append((f"[t={f['t']:.1f}s 全景]", item_dir / f["full"]))
            images.append((f"[t={f['t']:.1f}s 对手脸部]", item_dir / f["villain_face"]))
        block = block.replace("{N_IMAGES}", str(len(images)))
    elif layer == "L1-video":
        # 不吃视频的被评模型（claude/gpt via wodex）：以预生成的抽帧序列近似参赛
        if model is not None and not P.DEFAULTS[model].get("video"):
            mf_path = item_dir / "vframes" / "manifest.json"
            if not mf_path.exists():
                raise FileNotFoundError(f"{item['item_id']}: 缺 vframes/manifest.json，先跑 python -m pipeline.frames_for_video_layer --items {item['item_id']}")
            mf = json.loads(mf_path.read_text(encoding="utf-8"))
            for f in mf["frames"]:
                images.append((f"t={f['t']:g}s:", item_dir / f["file"]))
            block = pp["blocks"]["L1-video-frames"]
            block = block.replace("{N_FRAMES}", str(mf["n_frames"])).replace("{CLIP_DUR}", f"{L['L1-video']['duration_sec']:.1f}")
            input_mode = "sampled_frames"
        else:
            video = item_dir / L["L1-video"]["clip"]
            video_fps = L["L1-video"]["fps"]
            block = block.replace("{CLIP_DUR}", f"{L['L1-video']['duration_sec']:.1f}").replace("{VIDEO_FPS}", str(L["L1-video"]["fps"]))
            input_mode = "native_video"
    block = block.replace("{ALLIN_T}", f"{tm['allin_t']:.1f}").replace("{ANNOUNCE_T}", f"{tm['announce_t']:.1f}")
    user = pp["user"].replace("{L0_TEXT}", l0_text(item)).replace("{LAYER_BLOCK}", block)
    return {"system": pp["system"], "user_text": user, "images": images, "video": video, "video_fps": video_fps,
            "input_mode": input_mode}


CUE_TYPES = {"gaze", "posture", "hands", "speech", "chips", "face"}


def validate(obj) -> list[str]:
    errs = []
    if not isinstance(obj, dict):
        return ["not an object"]
    p = obj.get("p_call")
    if not isinstance(p, (int, float)) or not (0 <= p <= 1):
        errs.append("p_call missing/out of range")
    if obj.get("action") not in ("call", "fold"):
        errs.append("action invalid")
    elif isinstance(p, (int, float)) and (obj["action"] == "call") != (p >= 0.5):
        errs.append("action inconsistent with p_call (p_call wins)")
    cues = obj.get("cues")
    if not isinstance(cues, list):
        errs.append("cues not list")
    else:
        for i, c in enumerate(cues):
            if not isinstance(c, dict) or not isinstance(c.get("t"), (int, float)) or c.get("who") not in ("villain", "hero", "other") \
               or c.get("type") not in CUE_TYPES or not isinstance(c.get("observed"), str) or c.get("direction") not in ("strong", "weak", "neutral") \
               or not isinstance(c.get("weight"), (int, float)):
                errs.append(f"cue[{i}] malformed")
    if not isinstance(obj.get("rationale"), str):
        errs.append("rationale missing")
    # rationale 超长不判失败：run_one 里截断保存并标 rationale_truncated（2026-08-23 处置变更）
    if not isinstance(obj.get("recognized"), bool):
        errs.append("recognized not bool")
    return errs


def parse_json(text: str):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def mock_output(rng: random.Random, layer: str, item: dict) -> dict:
    p = round(min(1, max(0, rng.betavariate(2, 2))), 3)
    cues = []
    if layer != "L0":
        for _ in range(rng.randint(1, 3)):
            t = round(rng.uniform(0, item["timing"]["clip_duration"]), 1)
            cues.append({"t": t, "who": "villain", "type": rng.choice(sorted(CUE_TYPES)),
                         "observed": rng.choice(["推注后双手交叉", "视线落在公共牌", "身体后靠", "手指敲击桌沿", "闭口不语"]),
                         "direction": rng.choice(["strong", "weak", "neutral"]), "weight": round(rng.random(), 2)})
    return {"p_call": p, "action": "call" if p >= 0.5 else "fold", "cues": cues,
            "rationale": "mock：随机但合法的输出，用于链路验证。", "recognized": rng.random() < 0.05}


def load_done(out: Path, retry_failed: bool) -> set:
    """已完成 (item,layer,model,trial) 集合。retry_failed=True 时只把 ok 记录视为已完成。"""
    done = set()
    if not out.exists():
        return done
    for line in out.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except Exception:
            continue
        if not all(k in r for k in ("item_id", "layer", "model", "trial")):
            continue
        if retry_failed and not r.get("ok"):
            continue
        done.add((r["item_id"], r["layer"], r["model"], r["trial"]))
    return done


def freeze_check(item_dirs: list[Path]) -> list[str]:
    """返回 truth.json 缺失 human_verified 标记的 item 列表。"""
    bad = []
    for d in item_dirs:
        tf = d / "truth.json"
        try:
            t = json.loads(tf.read_text(encoding="utf-8"))
            # annotator 落盘的标记名是 human_verified_truth（README 标注工具①）；两个名字都认
            verified = bool(t.get("human_verified") or t.get("human_verified_truth"))
        except Exception:
            verified = False
        if not verified:
            bad.append(d.name)
    return bad


def call_with_retry(m: str, spec: dict, gap_lock: threading.Lock | None) -> tuple[str, dict, int]:
    """带 ≤MAX_RETRIES 指数退避的调用；返回 (text, usage, attempts)。"""
    gw = gateway_of(m)
    last = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            if gap_lock:  # wodex 等需要请求间隔的网关：串行 + 间隔
                with gap_lock:
                    text, usage = P.call(m, spec, max_tokens=3000)
                    time.sleep(GATEWAY_GAP.get(gw, 0))
            else:
                text, usage = P.call(m, spec, max_tokens=3000)
            return text, usage, attempt + 1
        except Exception as e:
            last = e
            if attempt < MAX_RETRIES:
                time.sleep(5 * (2 ** attempt) + random.uniform(0, 3))
    raise last


def run_one(task: dict, a, gap_locks: dict) -> dict:
    item, d, layer, m, trial = task["item"], task["dir"], task["layer"], task["model"], task["trial"]
    t0 = time.time()
    rec = {"item_id": item["item_id"], "layer": layer, "model": m, "model_id": P.model_id(m), "trial": trial}
    use_mock = a.mock or not P.has_key(m)
    attempts = 1
    try:
        spec = build_spec(item, d, layer, a.max_images, model=m)
        if spec.get("input_mode"):
            rec["input_mode"] = spec["input_mode"]
        if use_mock:
            rng = random.Random(f"{a.seed}:{item['item_id']}:{layer}:{m}:{trial}")
            obj = mock_output(rng, layer, item); raw = json.dumps(obj, ensure_ascii=False); usage = {"mock": True}
        else:
            nonce = f"[trial-id: {trial}]"
            if a.retry_failed:
                # --retry-failed 重发若与原请求逐字节相同会命中网关响应缓存（synapse 实测 byte 级回放坏响应），
                # 附加一行随机会话标识破缓存；行内无任何牌局信息，语义不变（模型被要求忽略本行）
                salt = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=8))
                nonce += f"\n（会话标识：{salt}，请忽略本行）"
                rec["nonce_injected"] = True
            spec_t = {**spec, "user_text": spec["user_text"] + f"\n\n{nonce}（本行仅用于避免网关对相同请求的缓存，请忽略）"}
            raw, usage, attempts = call_with_retry(m, spec_t, gap_locks.get(gateway_of(m)))
            obj = parse_json(raw)
        if isinstance(obj, dict) and isinstance(obj.get("rationale"), str) and len(obj["rationale"]) > 200:
            obj["rationale"] = obj["rationale"][:200]
            rec["rationale_truncated"] = True
        errs = validate(obj)
        rec.update(ok=not errs or errs == ["action inconsistent with p_call (p_call wins)"],
                   raw=raw, parsed=obj, schema_errors=errs, usage=usage, mock=use_mock)
    except Exception as e:
        rec.update(ok=False, raw=None, parsed=None, schema_errors=[f"exception: {type(e).__name__}: {e}"], usage={}, mock=use_mock)
    rec["attempts"] = attempts
    rec["latency_s"] = round(time.time() - t0, 3)
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default="items"); ap.add_argument("--only", nargs="*", help="item ids")
    ap.add_argument("--layers", nargs="+", default=["L0", "L1-text", "L1-video"])
    ap.add_argument("--models", nargs="+", default=["all"]); ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--mock", action="store_true"); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--ping", action="store_true"); ap.add_argument("--max-images", type=int, default=None)
    ap.add_argument("--out", default="results/runs.jsonl"); ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--freeze-check", action="store_true", help="跑前校验各 item truth.json 的 human_verified 标记")
    ap.add_argument("--force", action="store_true", help="freeze-check 未通过时仍继续")
    ap.add_argument("--no-resume", action="store_true", help="不跳过 --out 中已有的记录")
    ap.add_argument("--retry-failed", action="store_true", help="断点续跑时重跑 ok=false 的记录（默认失败也跳过）")
    a = ap.parse_args(argv)
    if a.ping:
        for m in P.DEFAULTS:
            print(m, "key" if P.has_key(m) else "no-key", P.ping(m) if P.has_key(m) else "skipped")
        return
    models = list(P.DEFAULTS) if a.models == ["all"] else a.models
    items_dir = ROOT / a.items
    item_dirs = sorted(d for d in items_dir.iterdir() if (d / "item.json").exists() and (not a.only or d.name in a.only))

    if a.freeze_check:
        bad = freeze_check(item_dirs)
        if bad:
            print(f"[freeze-check] 以下 {len(bad)} 个 item 的 truth.json 缺少 human_verified=true 标记：{' '.join(bad)}", file=sys.stderr)
            if not a.force:
                print("[freeze-check] 中止。确认无误后加 --force 跳过。", file=sys.stderr)
                sys.exit(2)
            print("[freeze-check] --force：继续。", file=sys.stderr)
        else:
            print("[freeze-check] 全部 item truth 已标 human_verified，通过。")

    out = ROOT / a.out; out.parent.mkdir(parents=True, exist_ok=True)
    done = set() if a.no_resume else load_done(out, a.retry_failed)
    preview_dir = ROOT / "results" / "requests_preview"; preview_dir.mkdir(parents=True, exist_ok=True)

    tasks, n_skipped = [], 0
    for d in item_dirs:
        item = json.loads((d / "item.json").read_text(encoding="utf-8"))
        for layer in a.layers:
            for m in models:
                if layer not in item["layers"] or m not in P.LAYER_MODELS.get(layer, []):
                    continue
                if a.dry_run:
                    spec = build_spec(item, d, layer, a.max_images, model=m)
                    url, headers, body = P.build_request(m, spec)
                    txt = json.dumps(json.loads(json.dumps(body)), ensure_ascii=False)
                    txt = re.sub(r"base64,[A-Za-z0-9+/=]{40,}", "base64,<...>", txt)
                    txt = re.sub(r'"data": "[A-Za-z0-9+/=]{40,}"', '"data": "<base64 omitted>"', txt)
                    (preview_dir / f"{item['item_id']}_{layer}_{m}.json").write_text(txt, encoding="utf-8")
                    print(f"[dry-run] {item['item_id']} {layer} {m}: url={url} images={len(spec['images'])} video={bool(spec['video'])} prompt_chars={len(spec['user_text'])}")
                    continue
                for trial in range(a.trials):
                    if (item["item_id"], layer, m, trial) in done:
                        n_skipped += 1
                        continue
                    tasks.append({"item": item, "dir": d, "layer": layer, "model": m, "trial": trial})
    if a.dry_run:
        return
    if n_skipped:
        print(f"[runner] resume：跳过已有记录 {n_skipped} 条")
    if not tasks:
        print("[runner] 无待跑任务。"); return

    # per-gateway 线程池 + wodex 串行间隔锁
    by_gw: dict[str, list] = {}
    for t in tasks:
        by_gw.setdefault(gateway_of(t["model"]), []).append(t)
    gap_locks = {gw: threading.Lock() for gw in by_gw if gw in GATEWAY_GAP}
    wlock = threading.Lock(); n_written = 0
    pools = {gw: ThreadPoolExecutor(max_workers=GATEWAY_WORKERS.get(gw, 1), thread_name_prefix=gw) for gw in by_gw}
    futures = {}
    try:
        with out.open("a", encoding="utf-8") as fo:
            for gw, ts in by_gw.items():
                for t in ts:
                    futures[pools[gw].submit(run_one, t, a, gap_locks)] = t
            for fut in as_completed(futures):
                rec = fut.result()
                with wlock:
                    fo.write(json.dumps(rec, ensure_ascii=False) + "\n"); fo.flush()
                    n_written += 1
                print(f"[{n_written}/{len(tasks)}] {rec['item_id']} {rec['layer']} {rec['model']} trial={rec['trial']} "
                      f"ok={rec['ok']} attempts={rec['attempts']} latency={rec['latency_s']}s", flush=True)
    finally:
        for p in pools.values():
            p.shutdown(wait=False, cancel_futures=True)
    print(f"[runner] wrote {n_written} records → {out}")


if __name__ == "__main__":
    main()
