"""离线导出全部评测请求体（轨迹完整性：输入侧）。base64 媒体替换为文件引用+sha256。"""
import json, hashlib, sys, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from runner import run as R, providers as P

def strip_b64(obj):
    if isinstance(obj, dict):
        out={}
        for k,v in obj.items():
            if k=="url" and isinstance(v,str) and v.startswith("data:"):
                head=v.split(",",1)[0]
                out[k]=f"<{head};base64 omitted, {len(v)} chars>"
            elif k=="data" and isinstance(v,str) and len(v)>1000:
                out[k]=f"<base64 omitted, {len(v)} chars>"
            else: out[k]=strip_b64(v)
        return out
    if isinstance(obj, list): return [strip_b64(x) for x in obj]
    return obj

def media_refs(item_id, layer, model):
    d=Path("items")/item_id; refs=[]
    if layer=="L1-video":
        if model in ("qwen","kimi"):
            p=d/"clip_hided_2fps.mp4"
            if p.exists(): refs.append({"file":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
        else:
            vf=d/"vframes"
            if vf.exists():
                for f in sorted(vf.glob("*.jpg")): refs.append({"file":str(f),"sha256":hashlib.sha256(f.read_bytes()).hexdigest()})
    return refs

outdir=Path("results/requests"); outdir.mkdir(parents=True,exist_ok=True)
matrix={"L0":["claude","gpt","qwen","kimi","deepseek"],"L1-text":["claude","gpt","qwen","kimi","deepseek"],"L1-video":["claude","gpt","qwen","kimi"]}
n=0
for item_id in ["T1","T2","T3","T4","T5","F1","F2","F3","F4","F5"]:
    for layer,models in matrix.items():
        for model in models:
            try:
                d=Path("items")/item_id
                item=json.load(open(d/"item.json"))
                spec=R.build_spec(item, d, layer, model=model)
                url,headers,body=P.build_request(model, spec)
            except Exception as e:
                print(f"skip {item_id}/{layer}/{model}: {e}"); continue
            rec={"item_id":item_id,"layer":layer,"model":model,"url":url,
                 "headers":{k:("<redacted>" if k.lower() in ("authorization","x-api-key") else v) for k,v in headers.items()},
                 "body":strip_b64(body),"media_refs":media_refs(item_id,layer,model)}
            (outdir/f"{item_id}_{layer}_{model}.json").write_text(json.dumps(rec,ensure_ascii=False,indent=1))
            n+=1
print("dumped",n,"request bodies →",outdir)
