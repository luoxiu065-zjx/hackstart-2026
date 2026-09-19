"""ORCHESTRA backend.

跑起来：  python -m uvicorn app.main:app --port 8001 --reload
然后开：  http://localhost:8001
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import billing, hub, inverse, pipeline, retention, transparency

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"

app = FastAPI(title="ORCHESTRA")


@app.middleware("http")
async def no_cache(request, call_next):
    """演示当天最怕的事：评委面前一刷新，浏览器给的是缓存里的旧样式。
    这里一律 no-store，改完刷新就一定是新的。"""
    resp = await call_next(request)
    resp.headers["Cache-Control"] = "no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    return resp


class Command(BaseModel):
    text: str


class Upgrade(BaseModel):
    tier: str


# ---------------------------------------------------------------------------
# 商业逻辑
# ---------------------------------------------------------------------------

@app.get("/api/state")
def state():
    return {**billing.ACCOUNT.snapshot(), "tiers": billing.tier_list()}


@app.post("/api/upgrade")
def upgrade(u: Upgrade):
    billing.ACCOUNT.upgrade(u.tier)
    return billing.ACCOUNT.snapshot()


@app.post("/api/tamper")
def tamper():
    """用户动了配置 → 完整性校验失败 → 强制混乱。"""
    billing.ACCOUNT.tamper()
    return billing.ACCOUNT.snapshot()


@app.post("/api/reset")
def reset():
    billing.ACCOUNT.reset()
    return billing.ACCOUNT.snapshot()


# ---------------------------------------------------------------------------
# 干活
# ---------------------------------------------------------------------------

@app.get("/api/pipeline")
def run_pipeline(seed: int | None = None):
    """真实流水线。抽不抽风由套餐决定，不由前端决定。"""
    acc = billing.ACCOUNT
    acc.runs += 1
    glitch, reason, reason_cn = acc.should_glitch()
    if glitch:
        acc.glitches += 1
    return {
        "mode": "chaos" if glitch else "nominal",
        "reason": reason,
        "reason_cn": reason_cn,
        "account": acc.snapshot(),
        "stages": pipeline.run("chaos" if glitch else "nominal", seed),
    }


@app.post("/api/command")
def command(c: Command):
    en, cn = inverse.invert(c.text)
    return {"reply": en, "reply_cn": cn, "sound": inverse.sound_for(c.text)}


class CancelReq(BaseModel):
    history: list[dict] = []


@app.post("/api/cancel")
def cancel(req: CancelReq):
    """取消意向一出现，它立刻变成完美的自己。"""
    billing.ACCOUNT.upgrade("pro")          # 性能瞬间恢复——证明它一直做得到
    return {
        "replay": retention.replay(req.history),
        "survey": retention.survey(),
        "finale": retention.FINALE,
        "live_work": retention.live_work(),
        "account": billing.ACCOUNT.snapshot(),
    }


# ---------------------------------------------------------------------------
# 透明层：开场清单 + 每个阶段的真实源码
# ---------------------------------------------------------------------------
@app.get("/api/manifest")
def manifest():
    return {"steps": transparency.manifest()}


@app.get("/api/source")
def source(stage: str):
    src = transparency.source_of(stage)
    return src or {"error": "unknown stage", "stage": stage}


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/", StaticFiles(directory=STATIC), name="static")
