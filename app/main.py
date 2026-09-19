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

from app import inverse, pipeline

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"

app = FastAPI(title="ORCHESTRA")


class Command(BaseModel):
    text: str


@app.post("/api/command")
def command(c: Command):
    """反向满足：把用户的请求翻过来执行。"""
    return {
        "reply": inverse.invert(c.text),
        "sound": inverse.sound_for(c.text),
        "mode": "chaos",
    }


@app.get("/api/pipeline")
def run_pipeline(mode: str = "nominal", seed: int | None = None):
    """真实流水线：读真课表、真课程、真预习包。"""
    return {"mode": mode, "stages": pipeline.run(mode, seed)}


# ---------------------------------------------------------------------------
# TODO(George): 取消订阅 / 挽留流程
#   POST /api/cancel  {}  ->  {"replay":[...], "survey":[...]}
#   前端在 window 上监听 "orchestra:cancel"，把结果渲染进 #billing-slot
# ---------------------------------------------------------------------------
@app.post("/api/cancel")
def cancel():
    return {"replay": [], "survey": [], "todo": "George"}


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/", StaticFiles(directory=STATIC), name="static")
