"""模型统一调用层（stdlib urllib，无 SDK 依赖）。

被评五家：claude / gpt / qwen / kimi（暂 mock，等黑客松现场额度）+ deepseek（真实，经 Synapse 网关）。
工具模型 doubao（火山方舟 Ark）：时间轴初稿 + 幻觉 judge；另临时充当 L1-video 被评模型（provisional，正式名单等现场）。

每个 provider 实现 build_request(spec) → (url, headers, body) 与 call() → text。
spec = {"system": str, "user_text": str, "images": [(label, png_path)], "video": path|None, "video_fps": float}
环境变量（.env 自动加载）：SYNAPSE_API_KEY + SYNAPSE_BASE（OpenAI 兼容）、ARK_API_KEY；其余四家现场再配。
"""
from __future__ import annotations
import base64, json, os, urllib.request
from pathlib import Path
from pipeline.common import load_env

load_env()

ARK_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
# wodex 网关（黑客松额度）：OpenAI 兼容；两个硬约束——必须带浏览器 UA（默认 UA 被 Cloudflare 403 code 1010）、
# 大 payload 被 WAF 拦（实测 1MB base64 PNG 403、27KB jpg 通过），故发 wodex 的图片一律压成 ≤480 宽 jpg。
WODEX_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

def _wodex_url() -> str:
    base = os.environ.get("WODEX_BASE", "https://api.wodex.ai/v1").rstrip("/")
    return base + "/chat/completions"

def _use_wodex(name: str) -> bool:
    return name in ("claude", "gpt") and bool(os.environ.get("WODEX_API_KEY"))

# 模型名以框架 §0 为准；真实 model id 可用环境变量覆盖（例如 RRB_MODEL_claude=claude-opus-4-1）
DEFAULTS = {
    "claude":   {"model": "claude-opus-5", "env": "ANTHROPIC_API_KEY", "alt_env": "WODEX_API_KEY", "video": False},
    "gpt":      {"model": "gpt-5.6-sol", "env": "OPENAI_API_KEY", "alt_env": "WODEX_API_KEY", "video": False},
    "qwen":     {"model": "qwen3.8-max", "env": "DASHSCOPE_API_KEY", "video": True},
    "kimi":     {"model": "kimi-k3", "env": "MOONSHOT_API_KEY", "video": True},
    "deepseek": {"model": "deepseek-v4-pro", "env": "SYNAPSE_API_KEY", "video": False},
    "doubao":   {"model": "doubao-seed-2-1-pro-260628", "env": "ARK_API_KEY", "video": True, "provisional": True},
}
# v0.2：删除 L1-vision（抽帧层）；doubao 在 L1-video 为 provisional 被评模型
LAYER_MODELS = {"L0": ["claude", "gpt", "qwen", "kimi", "deepseek", "doubao"],
                "L1-text": ["claude", "gpt", "qwen", "kimi", "deepseek"],
                "L1-video": ["qwen", "kimi", "doubao"]}
# doubao 出现在 L0 仅为给其 provisional L1-video 提供同模型盲答基线（读人增益要同模型对比）


def model_id(name: str) -> str:
    return os.environ.get(f"RRB_MODEL_{name}", DEFAULTS[name]["model"])


def has_key(name: str) -> bool:
    d = DEFAULTS[name]
    return bool(os.environ.get(d["env"]) or (d.get("alt_env") and os.environ.get(d["alt_env"])))


def _b64(p: Path) -> str:
    return base64.b64encode(Path(p).read_bytes()).decode()


def _small_jpg(p: Path) -> Path:
    """wodex WAF 限制：把图压成 ≤480 宽 jpg（结果缓存在源文件旁 .wodex.jpg）。"""
    p = Path(p)
    out = p.with_suffix(".wodex.jpg")
    if not out.exists() or out.stat().st_mtime < p.stat().st_mtime:
        import imageio_ffmpeg, subprocess
        ff = imageio_ffmpeg.get_ffmpeg_exe()
        subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(p),
                        "-vf", "scale='min(480,iw)':-1", str(out)], check=True)
    return out


def _synapse_url() -> str:
    base = os.environ.get("SYNAPSE_BASE", "").rstrip("/")
    if base.endswith("/v1"):
        return base + "/chat/completions"
    return base + "/v1/chat/completions"


def _openai_compat_content(spec: dict) -> list:
    content = [{"type": "text", "text": spec["user_text"]}]
    for label, p in spec.get("images", []):
        content.append({"type": "text", "text": label})
        content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{_b64(p)}"}})
    if spec.get("video"):
        vu = {"url": f"data:video/mp4;base64,{_b64(spec['video'])}"}
        if spec.get("video_fps"):
            vu["fps"] = spec["video_fps"]
        content.append({"type": "video_url", "video_url": vu})
    return content


def build_request(name: str, spec: dict, temperature: float = 0.7, max_tokens: int = 1600) -> tuple[str, dict, dict]:
    mid = model_id(name)
    if _use_wodex(name):
        content = [{"type": "text", "text": spec["user_text"]}]
        for label, p in spec.get("images", []):
            content.append({"type": "text", "text": label})
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{_b64(_small_jpg(p))}"}})
        # wodex 不支持视频输入（claude/gpt 本就不吃视频）
        body = {"model": mid, "temperature": temperature, "max_tokens": max(max_tokens, 8192),
                "messages": [{"role": "system", "content": spec["system"]},
                             {"role": "user", "content": content}]}
        # 赛规最高档思考：wodex 实测（2026-08-22）走 OpenAI 风格 reasoning_effort——
        # claude-opus-5 带 reasoning_effort 后响应出现 message.reasoning_content（Anthropic 风格
        # {"thinking":{"type":"enabled","budget_tokens":N}} 被网关静默忽略，usage/输出与 baseline 完全一致）；
        # gpt-5.6-sol 对 high/xhigh 均不报错，但 usage 无 reasoning 细分且 completion tokens 几乎不变，
        # 档位是否真透传存疑（详见 README「wodex 思考档位」）。max_tokens 提到 ≥8192 给思维链留空间。
        body["reasoning_effort"] = "high"
        return (_wodex_url(), {"Authorization": f"Bearer {os.environ['WODEX_API_KEY']}",
                               "Content-Type": "application/json", "User-Agent": WODEX_UA}, body)
    if name == "claude":
        content = [{"type": "text", "text": spec["user_text"]}]
        for label, p in spec.get("images", []):
            content.append({"type": "text", "text": label})
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": _b64(p)}})
        body = {"model": mid, "max_tokens": max_tokens, "temperature": temperature, "system": spec["system"],
                "messages": [{"role": "user", "content": content}]}
        return ("https://api.anthropic.com/v1/messages",
                {"x-api-key": os.environ.get("ANTHROPIC_API_KEY", ""), "anthropic-version": "2023-06-01", "content-type": "application/json"}, body)
    urls = {"gpt": "https://api.openai.com/v1/chat/completions",
            "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            "kimi": "https://api.moonshot.cn/v1/chat/completions",
            "deepseek": _synapse_url(), "doubao": ARK_URL}
    body = {"model": mid, "temperature": temperature, "max_tokens": max_tokens,
            "messages": [{"role": "system", "content": spec["system"]},
                         {"role": "user", "content": _openai_compat_content(spec)}]}
    if name == "kimi":
        body["temperature"] = 1  # kimi-k3 reasoning 模型只允许 temperature=1
        body["max_tokens"] = max(body["max_tokens"], 16384)  # reasoning 吃 token，太小只吐 reasoning_content
        body["reasoning_effort"] = "max"  # 赛规最高档思考：k3 顶层 reasoning_effort ∈ low/high/max（默认即 max，显式固定）
        if spec.get("video"):
            # moonshot 视频输入实测（2026-08-22）：video_url 直发 data:video/mp4;base64 即可通过
            # （T2 2fps 96.5s mp4 ≈2.8MB，base64 后 body ≈3.8MB，prompt ≈34.7k tokens）；
            # 更大视频才需走 POST /v1/files purpose=video → ms://<file_id>。注意 moonshot 不认 fps 字段，需剥掉。
            for part in body["messages"][1]["content"]:
                if part.get("type") == "video_url":
                    part["video_url"].pop("fps", None)
    if name == "deepseek":
        # 赛事规则：被评模型开最高档思考。开思维链后需要大 max_tokens 才能推完（16k 不够）
        body["thinking"] = {"type": "enabled"}
        body["max_tokens"] = max(body["max_tokens"], 32768)
    if name == "doubao":
        body["thinking"] = {"type": "disabled"}  # doubao 是工具模型（timeline/judge），非被评，保持稳定 JSON
    return (urls[name], {"Authorization": f"Bearer {os.environ.get(DEFAULTS[name]['env'], '')}", "Content-Type": "application/json"}, body)


def call(name: str, spec: dict, timeout: int = 900, **kw) -> tuple[str, dict]:
    url, headers, body = build_request(name, spec, **kw)
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        resp = json.loads(r.read())
    if name == "claude" and not _use_wodex(name):
        text = "".join(b.get("text", "") for b in resp.get("content", []))
        usage = resp.get("usage", {})
    else:
        msg = resp["choices"][0]["message"]
        text = msg.get("content") or ""
        if not text and msg.get("reasoning_content"):
            text = msg["reasoning_content"]  # reasoning 模型 content 截断时的兜底（parse_json 会提取其中 JSON）
        usage = resp.get("usage", {})
    return text, usage


def ark_call(messages: list, max_tokens: int = 4000, temperature: float = 0.2, timeout: int = 900) -> tuple[str, dict]:
    """工具用途（时间轴/judge）直调豆包：messages 已按 OpenAI 兼容格式组好。"""
    body = {"model": model_id("doubao"), "messages": messages, "temperature": temperature,
            "max_tokens": max_tokens, "thinking": {"type": "disabled"}}
    req = urllib.request.Request(ARK_URL, data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {os.environ['ARK_API_KEY']}", "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        resp = json.loads(r.read())
    return resp["choices"][0]["message"]["content"], resp.get("usage", {})


def video_content(video: Path, fps: float, text: str) -> list:
    return [{"type": "video_url", "video_url": {"url": f"data:video/mp4;base64,{_b64(video)}", "fps": fps}},
            {"type": "text", "text": text}]


def ping(name: str) -> dict:
    """最小连通性测试（几十 token）。"""
    spec = {"system": "Reply with the single word: pong", "user_text": "ping", "images": [], "video": None}
    try:
        text, usage = call(name, spec, temperature=0, max_tokens=16, timeout=60)
        return {"ok": True, "text": text[:40], "usage": usage}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}
