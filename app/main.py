"""ORCHESTRA backend.

跑起来：  python -m uvicorn app.main:app --port 8001 --reload
然后开：  http://localhost:8001
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import agents, billing, guard, hub, inverse, llm, pipeline, retention, transparency

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"

app = FastAPI(title="ORCHESTRA")


@app.middleware("http")
async def gate(request: Request, call_next):
    """限时开放 + 每 IP 限速。静态资源不限速，否则一进页面就被自己打爆。"""
    path = request.url.path
    if guard.expired() and not path.startswith("/api/guard"):
        return PlainTextResponse(
            "This demo link has expired.\n此演示链接已过期。", status_code=410)
    if path.startswith("/api/") and not path.startswith("/api/guard"):
        # 优先用浏览器身份：同一个 wifi 下的多个评委不会互相拖累
        who = (request.headers.get("X-Client")
               or request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
               or (request.client.host if request.client else "?"))
        ok, why = guard.allow(who, path)
        if not ok:
            return JSONResponse(
                {"error": "too_many_requests", "why": why,
                 "reply": "Slow down. This is a free plan.",
                 "reply_cn": "慢点。这是免费套餐。"}, status_code=429)
    return await call_next(request)


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
def run_pipeline(request: Request, seed: int | None = None, lang: str = "cn"):
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
        "stages": pipeline.run("chaos" if glitch else "nominal", seed, lang),
    }


_REQUESTS = {"n": 0}


@app.post("/api/command")
def command(c: Command, request: Request):
    acc = _acc(request)
    _REQUESTS["n"] += 1
    n = _REQUESTS["n"]

    stubborn = acc.tier not in ("trial", "pro")

    # C14 罢工：罢工是产品行为，不花模型的钱
    if stubborn:
        strike = inverse.on_strike(n)
        if strike:
            return {"reply": strike[0], "reply_cn": strike[1],
                    "sound": "alarm", "strike": True, "src": "rules"}

    # 正常版 = 正常的我；犟种版 = 反向的我。同一个模型，两套人格。
    if guard.llm_allowed():
        en, cn, src = llm.reply(c.text, stubborn)
    else:                                   # 预算用完：页面照常玩，只是不再花钱
        en, cn = (inverse.invert(c.text) if stubborn else inverse.correct(c.text))
        src = "rules"

    if stubborn:                            # C13 越用越不客气
        pen, pcn = inverse.politeness(n)
        en, cn = pen + en, pcn + cn

    return {"reply": en, "reply_cn": cn, "src": src, "strike": False,
            "sound": inverse.sound_for(c.text) if stubborn else "ok"}


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
@app.get("/api/hub/today")
def hub_today():
    """正例：正常版学业助手的「今日」数据。时间段 + 重要度，不是 9 点做什么。"""
    return hub.today()


@app.get("/api/hub/prep")
def hub_prep():
    return {"packs": hub.prep_index()}


@app.get("/api/agents")
def agent_profiles():
    """每个 agent 学过什么、按什么准则干活——混乱之所以荒谬，是因为它在严格执行错的规矩。"""
    return {"profiles": agents.all_profiles()}


@app.get("/api/guard")
def guard_state():
    return {**guard.snapshot(), "llm": llm.STATS}


@app.get("/api/manifest")
def manifest():
    return {"steps": transparency.manifest()}


@app.get("/api/source")
def source(stage: str):
    src = transparency.source_of(stage)
    return src or {"error": "unknown stage", "stage": stage}


@app.get("/about")
def about():
    """对外介绍页。评委和同学打不开 claude.ai，所以挂在自己的服务器上。"""
    return FileResponse(STATIC / "about.html")


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/", StaticFiles(directory=STATIC), name="static")
