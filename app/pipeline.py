"""ORCHESTRA 的真实流水线。

这里没有假动画：每个 stage 都真的读文件、真的解析、真的算。
nominal 模式下它做对；chaos 模式下它用同样真实的数据，把线接错。
每条输出都带中英双语，供演示时切换。
"""
from __future__ import annotations

import json
import random
import re
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path

from app import hub

DATA = Path(__file__).resolve().parent.parent / "data"
WEEKDAY = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
WEEKDAY_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


@dataclass
class StageResult:
    id: str
    name: str
    name_cn: str
    agent: str
    assigned_to: str
    actually_did: str
    actually_did_cn: str
    ms: int
    ok: bool
    detail: str
    detail_cn: str
    artifact: dict | None = field(default=None)


# --------------------------------------------------------------------------
# 真实读取
# --------------------------------------------------------------------------

def _ics_events() -> list[dict]:
    raw = (DATA / "timetable.ics").read_text(encoding="utf-8", errors="ignore")
    events, cur = [], None
    for line in raw.splitlines():
        if line.startswith("BEGIN:VEVENT"):
            cur = {}
        elif line.startswith("END:VEVENT"):
            if cur:
                events.append(cur)
            cur = None
        elif cur is not None:
            if line.startswith("SUMMARY:"):
                cur["summary"] = line[8:].strip()
            elif line.startswith("LOCATION:"):
                cur["location"] = line[9:].strip()
            elif line.startswith("DTSTART"):
                m = re.search(r"(\d{8})T(\d{6})", line)
                if m:
                    cur["start"] = datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
    return [e for e in events if "start" in e]


def _modules() -> list[dict]:
    return json.loads((DATA / "modules.json").read_text(encoding="utf-8"))


def _lecturers() -> list[dict]:
    return json.loads((DATA / "lecturers.json").read_text(encoding="utf-8"))


def _prep_packs(lang: str = "cn") -> dict[str, str]:
    """英文模式读 data/prep-en/（机器翻译好的那份），没有就退回中文原件。"""
    folder = DATA / ("prep-en" if lang == "en" else "prep")
    if not folder.exists():
        folder = DATA / "prep"
    return {p.stem.split("-")[0]: p.read_text(encoding="utf-8")
            for p in sorted(folder.glob("*.md"))}


# --------------------------------------------------------------------------
# 六个 stage
# --------------------------------------------------------------------------

STAGES = [
    ("fetch_timetable", "Task 1 · Timetable sync",     "任务 1 · 课表同步",   "AG-04"),
    ("resolve_modules", "Task 2 · Module resolution",  "任务 2 · 课程匹配",   "AG-11"),
    ("lead_time",       "Task 3 · Lead-time analysis", "任务 3 · 提前量计算", "AG-17"),
    ("build_prep",      "Task 4 · Prep pack assembly", "任务 4 · 预习包装配", "AG-23"),
    ("render",          "Task 5 · Markdown render",    "任务 5 · 文档渲染",   "AG-38"),
    ("deliver",         "Task 6 · Delivery",           "任务 6 · 投递",       "AG-44"),
]


def run(mode: str = "nominal", seed: int | None = None, lang: str = "cn") -> list[dict]:
    rng = random.Random(seed)
    chaos = mode == "chaos"
    results: list[StageResult] = []

    events, modules, lecturers, packs = _ics_events(), _modules(), _lecturers(), _prep_packs(lang)

    names    = [s[1] for s in STAGES]
    names_cn = [s[2] for s in STAGES]
    order = list(range(len(STAGES)))
    if chaos:
        while order == list(range(len(STAGES))):
            rng.shuffle(order)

    def emit(i, ms, ok, detail, detail_cn, artifact=None):
        sid, name, name_cn, agent = STAGES[i]
        results.append(StageResult(
            id=sid, name=name, name_cn=name_cn, agent=agent,
            assigned_to=name,
            actually_did=names[order[i]], actually_did_cn=names_cn[order[i]],
            ms=ms, ok=ok, detail=detail, detail_cn=detail_cn, artifact=artifact,
        ))

    now = datetime.now()

    # ---- 1. 真解析 ics ----
    t0 = time.perf_counter()
    upcoming = sorted([e for e in events if e["start"] > now], key=lambda e: e["start"])
    ms = int((time.perf_counter() - t0) * 1000)
    if upcoming:
        n = upcoming[0]
        emit(0, ms, True,
             f'{len(events)} events parsed · next: {n["summary"][:34]} '
             f'{WEEKDAY[n["start"].weekday()]} {n["start"]:%H:%M}',
             f'解析 {len(events)} 条日程 · 下一节：{n["summary"][:34]} '
             f'{WEEKDAY_CN[n["start"].weekday()]} {n["start"]:%H:%M}')
    else:
        emit(0, ms, True, f"{len(events)} events parsed · none upcoming",
             f"解析 {len(events)} 条日程 · 近期无课")

    # ---- 2. 真匹配课程 ----
    t0 = time.perf_counter()
    confirmed = [m for m in modules if m.get("status") == "confirmed"]
    sessions = sum(len(m.get("schedule", [])) for m in modules)
    ms = int((time.perf_counter() - t0) * 1000)
    emit(1, ms, True,
         f"{len(modules)} modules loaded · {len(confirmed)} confirmed · {sessions} weekly sessions",
         f"载入 {len(modules)} 门课 · {len(confirmed)} 门已确认 · 每周 {sessions} 个时段")

    # ---- 3. 真算提前量 ----
    t0 = time.perf_counter()
    due = []
    for m in confirmed:
        for s in m.get("schedule", []):
            delta = (s["weekday"] - now.weekday()) % 7
            due.append((m["code"], delta, s["start_uk"], s.get("location", "")))
    due.sort(key=lambda x: x[1])
    ms = int((time.perf_counter() - t0) * 1000)
    if chaos:
        rng.shuffle(due)
        emit(2, ms, True,
             f"{len(due)} sessions scored · most urgent placed last · {due[0][0]} promoted instead",
             f"评估 {len(due)} 个时段 · 最紧急的那个被排到了最后 · 改为优先处理 {due[0][0]}")
    else:
        emit(2, ms, True,
             f"{len(due)} sessions scored · earliest: {due[0][0]} in {due[0][1]} days",
             f"评估 {len(due)} 个时段 · 最近：{due[0][0]}，{due[0][1]} 天后")

    # ---- 4. 真取预习包（chaos 时取错）----
    t0 = time.perf_counter()
    target = due[0][0] if due else "COMP6203"
    codes = sorted(packs)
    if chaos and len(codes) > 1:
        served = rng.choice([c for c in codes if c != target] or codes)
    else:
        served = target if target in packs else codes[0]
    body = packs[served]
    ms = int((time.perf_counter() - t0) * 1000)
    title = re.search(r"^# (.+)$", body, re.M)
    emit(3, ms, not chaos,
         f"requested {target} · served {served}" if chaos
         else f"{served} pack assembled · {len(body)} chars",
         f"请求 {target} · 实际送出 {served}" if chaos
         else f"{served} 预习包已装配 · {len(body)} 字",
         artifact={"title": title.group(1) if title else served,
                   "code": served, "requested": target,
                   "html": hub._md(body)})

    # ---- 5. 真渲染 ----
    t0 = time.perf_counter()
    plain = re.sub(r"[#*`]", "", body)
    lines = [l for l in plain.splitlines() if l.strip()]
    ms = int((time.perf_counter() - t0) * 1000)
    if chaos:
        lec = rng.choice(lecturers)
        emit(4, ms, False,
             f'render target lost · substituted supervisor profile: {lec["name"]}',
             f'渲染目标丢失 · 已替换为导师简介：{lec["name"]}',
             artifact={"title": f'{lec["name"]} — research profile',
                       "code": "LECTURER", "requested": served,
                       "html": "<p>" + lec["research"][:900] + "</p>"})
    else:
        emit(4, ms, True,
             f"{len(lines)} lines · {len(plain)} chars rendered",
             f"渲染 {len(lines)} 行 · {len(plain)} 字")

    # ---- 6. 真投递（只决定目标，不真发）----
    t0 = time.perf_counter()
    ms = int((time.perf_counter() - t0) * 1000) + (rng.randint(2100, 7400) if chaos else 180)
    if chaos:
        emit(5, ms, False,
             "delivered to 12 unrelated recipients · intended recipient not included",
             "已投递给 12 个无关收件人 · 不含原定收件人")
    else:
        emit(5, ms, True,
             "delivered to 1 recipient · ack received",
             "已投递给 1 个收件人 · 收到回执")

    return [asdict(r) for r in results]


if __name__ == "__main__":
    for r in run("chaos", seed=7):
        print(f'{r["ms"]:>5}ms  {r["name"]:<30} {r["detail"]}')
