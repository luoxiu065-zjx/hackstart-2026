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

from app import billing, inverse, pipeline

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"

app = FastAPI(title="ORCHESTRA")


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


# ---------------------------------------------------------------------------
# TODO(George): 取消订阅 / 挽留流程
#   POST /api/cancel  ->  {"replay":[...], "survey":[...]}
#   前端监听 window 的 "orchestra:cancel" 事件，渲染进 #billing-slot
# ---------------------------------------------------------------------------
@app.post("/api/cancel")
def cancel():
    return {"replay": [], "survey": [], "todo": "George"}


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/", StaticFiles(directory=STATIC), name="static")
