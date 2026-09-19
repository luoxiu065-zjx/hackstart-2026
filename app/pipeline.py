"""ORCHESTRA 的真实流水线。

这里没有假动画：每个 stage 都真的读文件、真的解析、真的算。
nominal 模式下它做对；chaos 模式下它用同样真实的数据，把线接错。
错得越真，越好笑。
"""
from __future__ import annotations

import json
import random
import re
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
WEEKDAY = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


@dataclass
class StageResult:
    id: str
    name: str
    agent: str
    assigned_to: str          # 本来该它干的活
    actually_did: str         # 实际干的活
    ms: int
    ok: bool
    detail: str
    artifact: dict | None = field(default=None)


# --------------------------------------------------------------------------
# 真实的读取与解析
# --------------------------------------------------------------------------

def _ics_events() -> list[dict]:
    """解析真实的 timetable.ics，不依赖任何第三方库。"""
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


def _prep_packs() -> dict[str, str]:
    out = {}
    for p in sorted((DATA / "prep").glob("*.md")):
        out[p.stem.split("-")[0]] = p.read_text(encoding="utf-8")
    return out


# --------------------------------------------------------------------------
# 六个 stage
# --------------------------------------------------------------------------

STAGES = [
    ("fetch_timetable", "Task 1 · Timetable sync",      "AG-04"),
    ("resolve_modules", "Task 2 · Module resolution",   "AG-11"),
    ("lead_time",       "Task 3 · Lead-time analysis",  "AG-17"),
    ("build_prep",      "Task 4 · Prep pack assembly",  "AG-23"),
    ("render",          "Task 5 · Markdown render",     "AG-38"),
    ("deliver",         "Task 6 · Delivery",            "AG-44"),
]


def run(mode: str = "nominal", seed: int | None = None) -> list[dict]:
    """跑一遍真实流水线。mode='chaos' 时把接线打乱，但数据依然是真的。"""
    rng = random.Random(seed)
    chaos = mode == "chaos"
    results: list[StageResult] = []

    events = _ics_events()
    modules = _modules()
    lecturers = _lecturers()
    packs = _prep_packs()

    # chaos：把「谁干哪个活」整个洗牌
    names = [s[1] for s in STAGES]
    doing = names[:]
    if chaos:
        while doing == names:
            rng.shuffle(doing)

    def emit(i, ms, ok, detail, artifact=None):
        sid, name, agent = STAGES[i]
        results.append(StageResult(
            id=sid, name=name, agent=agent,
            assigned_to=name, actually_did=doing[i],
            ms=ms, ok=ok, detail=detail, artifact=artifact,
        ))

    # ---- Stage 1：真解析 ics ----
    t0 = time.perf_counter()
    now = datetime.now()
    upcoming = sorted([e for e in events if e["start"] > now], key=lambda e: e["start"])
    ms = int((time.perf_counter() - t0) * 1000)
    if upcoming:
        nxt = upcoming[0]
        detail = (f'{len(events)} events parsed · next: {nxt["summary"][:38]} '
                  f'{WEEKDAY[nxt["start"].weekday()]} {nxt["start"]:%H:%M}')
    else:
        detail = f"{len(events)} events parsed · none upcoming"
    emit(0, ms, True, detail)

    # ---- Stage 2：真匹配课程 ----
    t0 = time.perf_counter()
    confirmed = [m for m in modules if m.get("status") == "confirmed"]
    ms = int((time.perf_counter() - t0) * 1000)
    emit(1, ms, True,
         f'{len(modules)} modules loaded · {len(confirmed)} confirmed · '
         f'{sum(len(m.get("schedule", [])) for m in modules)} weekly sessions')

    # ---- Stage 3：真算提前量 ----
    t0 = time.perf_counter()
    due = []
    for m in confirmed:
        for s in m.get("schedule", []):
            delta = (s["weekday"] - now.weekday()) % 7
            when = now + timedelta(days=delta)
            due.append((m["code"], (when - now).days, s["start_uk"], s.get("location", "")))
    due.sort(key=lambda x: x[1])
    ms = int((time.perf_counter() - t0) * 1000)
    if chaos:
        rng.shuffle(due)
        detail = (f'{len(due)} sessions scored · earliest: {due[0][0]} in {due[0][1]} days '
                  f'· priority order re-derived')
    else:
        detail = f'{len(due)} sessions scored · earliest: {due[0][0]} in {due[0][1]} days'
    emit(2, ms, True, detail)

    # ---- Stage 4：真取预习包（chaos 时取错那一份）----
    t0 = time.perf_counter()
    target = due[0][0] if due else "COMP6203"
    codes = sorted(packs)
    if chaos and len(codes) > 1:
        wrong = [c for c in codes if c != target] or codes
        served = rng.choice(wrong)
    else:
        served = target if target in packs else codes[0]
    body = packs[served]
    ms = int((time.perf_counter() - t0) * 1000)
    title = re.search(r"^# (.+)$", body, re.M)
    emit(3, ms, not chaos,
         (f'requested {target} · served {served}' if chaos
          else f'{served} pack assembled · {len(body)} chars'),
         artifact={"title": title.group(1) if title else served,
                   "code": served, "requested": target,
                   "body": body[:1400]})

    # ---- Stage 5：真渲染 ----
    t0 = time.perf_counter()
    plain = re.sub(r"[#*`]", "", body)
    lines = [l for l in plain.splitlines() if l.strip()]
    ms = int((time.perf_counter() - t0) * 1000)
    if chaos:
        lec = rng.choice(lecturers)
        emit(4, ms, False,
             f'render target lost · substituted supervisor profile: {lec["name"]}',
             artifact={"title": f'{lec["name"]} — research profile',
                       "code": "LECTURER", "requested": served,
                       "body": lec["research"][:900]})
    else:
        emit(4, ms, True, f'{len(lines)} lines · {len(plain)} chars rendered')

    # ---- Stage 6：真投递（只模拟发送目标，不真发）----
    t0 = time.perf_counter()
    ms = int((time.perf_counter() - t0) * 1000) + (rng.randint(2100, 7400) if chaos else 180)
    if chaos:
        emit(5, ms, False,
             f'delivered to 12 unrelated recipients · original recipient not included')
    else:
        emit(5, ms, True, 'delivered to 私人助手群 · 1 recipient · ack received')

    return [asdict(r) for r in results]


if __name__ == "__main__":
    for r in run("nominal"):
        print(f'{r["ms"]:>5}ms  {r["name"]:<30} {r["detail"]}')
    print("\n--- CHAOS ---")
    for r in run("chaos", seed=7):
        print(f'{r["ms"]:>5}ms  {r["name"]:<30} -> {r["actually_did"]:<30} {r["detail"]}')
