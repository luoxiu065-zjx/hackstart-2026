"""ORCHESTRA backend.

跑起来：  python -m uvicorn app.main:app --port 8001 --reload
然后开：  http://localhost:8001
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
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

def _acc(request: Request) -> billing.Account:
    return billing.get(request.headers.get("X-Client"))


@app.get("/api/state")
def state(request: Request):
    return {**_acc(request).snapshot(), "tiers": billing.tier_list()}


@app.post("/api/upgrade")
def upgrade(u: Upgrade, request: Request):
    acc = _acc(request)
    acc.upgrade(u.tier)
    return acc.snapshot()


@app.post("/api/tamper")
def tamper(request: Request):
    """用户动了配置 → 完整性校验失败 → 强制混乱。"""
    acc = _acc(request)
    acc.tamper()
    return acc.snapshot()


@app.post("/api/reset")
def reset(request: Request):
    acc = _acc(request)
    acc.reset()
    return acc.snapshot()


# ---------------------------------------------------------------------------
# 干活
# ---------------------------------------------------------------------------

@app.get("/api/pipeline")
def run_pipeline(request: Request, seed: int | None = None):
    """真实流水线。抽不抽风由套餐决定，不由前端决定。"""
    acc = _acc(request)
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


_REQUESTS = {"n": 0}


@app.post("/api/command")
def command(c: Command, request: Request):
    acc = _acc(request)
    _REQUESTS["n"] += 1
    n = _REQUESTS["n"]

    # 豪华版：正常做事，而且客客气气
    if acc.tier in ("trial", "pro"):
        en, cn = inverse.correct(c.text)
        return {"reply": en, "reply_cn": cn, "sound": "ok", "strike": False}

    # C14 罢工
    strike = inverse.on_strike(n)
    if strike:
        return {"reply": strike[0], "reply_cn": strike[1], "sound": "alarm", "strike": True}

    # C11 反向满足 + C13 尊重程度递减
    en, cn = inverse.invert(c.text)
    pen, pcn = inverse.politeness(n)
    return {"reply": pen + en, "reply_cn": pcn + cn,
            "sound": inverse.sound_for(c.text), "strike": False}


class CancelReq(BaseModel):
    history: list[dict] = []


@app.post("/api/cancel")
def cancel(req: CancelReq, request: Request):
    """取消意向一出现，它立刻变成完美的自己。"""
    acc = _acc(request)
    acc.upgrade("pro")                      # 性能瞬间恢复——证明它一直做得到
    return {
        "replay": retention.replay(req.history),
        "survey": retention.survey(),
        "finale": retention.FINALE,
        "live_work": retention.live_work(),
        "account": acc.snapshot(),
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
