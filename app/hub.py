"""HUB —— 正常版学业助手的数据层。

严格按 2026-09-18《学业助手系统·设计方案》做：
  · /today 写「时间段 + 该时段值得关注的事」，不写「9:00-10:00 做什么」
  · 颜色 = 重要度，不是紧急度：red 今天不做有后果 / amber 该推进但不致命 / plain 有空再说
  · 网站是「看」的地方，飞书是「叫你去看」的地方

这一层完全不知道 billing / 降级的存在——商业化那套是后面叠上去的，不往这里渗。
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

WEEKDAY_CN = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
BANDS = [("morning", "上午", 0, 12), ("afternoon", "下午", 12, 18), ("evening", "晚上", 18, 24)]


# --------------------------------------------------------------------------- 读取
def modules() -> list[dict]:
    return json.loads((DATA / "modules.json").read_text(encoding="utf-8"))


def lecturers() -> list[dict]:
    return json.loads((DATA / "lecturers.json").read_text(encoding="utf-8"))


def events() -> list[dict]:
    raw = (DATA / "timetable.ics").read_text(encoding="utf-8", errors="ignore")
    out, cur = [], None
    for line in raw.splitlines():
        if line.startswith("BEGIN:VEVENT"):
            cur = {}
        elif line.startswith("END:VEVENT"):
            if cur and "start" in cur:
                out.append(cur)
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
            elif line.startswith("DTEND"):
                m = re.search(r"(\d{8})T(\d{6})", line)
                if m:
                    cur["end"] = datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
    return sorted(out, key=lambda e: e["start"])


def prep_files() -> list[tuple[str, int, Path]]:
    out = []
    for p in sorted((DATA / "prep").glob("*.md")):
        m = re.match(r"([A-Z0-9]+)-w(\d+)", p.stem)
        if m:
            out.append((m.group(1), int(m.group(2)), p))
    return out


# --------------------------------------------------------------------------- 工具
def _code_of(summary: str) -> str | None:
    m = re.match(r"([A-Z]{2,4}\d{4})", summary or "")
    return m.group(1) if m else None


def _lecturer_for(code: str) -> dict | None:
    return next((l for l in lecturers() if code in l.get("modules", [])), None)


def _prep_for(code: str) -> Path | None:
    for c, _w, p in prep_files():
        if c == code:
            return p
    return None


# --------------------------------------------------------------------------- /today
def today(now: datetime | None = None) -> dict:
    """今天有课就看今天；今天没课，就看下一个有课的日子——周末不该是空白页。"""
    now = now or datetime.now()
    evs = events()

    day = now.date()
    todays = [e for e in evs if e["start"].date() == day]
    looking_ahead = False
    if not todays:
        future = [e for e in evs if e["start"].date() > day]
        if future:
            day = future[0]["start"].date()
            todays = [e for e in future if e["start"].date() == day]
            looking_ahead = True

    mods = {m["code"]: m for m in modules()}
    bands = []
    for bid, label, lo, hi in BANDS:
        items = []
        for e in todays:
            if not (lo <= e["start"].hour < hi):
                continue
            code = _code_of(e.get("summary", ""))
            mod = mods.get(code, {})
            lect = _lecturer_for(code) if code else None
            prep = _prep_for(code) if code else None
            items.append({
                "time": e["start"].strftime("%H:%M"),
                "end": e["end"].strftime("%H:%M") if e.get("end") else "",
                "title": (mod.get("name") or e.get("summary", "")).strip(),
                "code": code or "",
                "location": e.get("location", "") or mod.get("schedule", [{}])[0].get("location", ""),
                "lecturer": (lect or {}).get("name", ""),
                "assessment": mod.get("assessment", ""),
                "has_prep": prep is not None,
                # 重要度：有课 = 今天不做有后果
                "weight": "red" if code else "plain",
            })
        note = ""
        if bid == "evening" and not items:
            note = "没有硬性安排。把明天第一节课的预习包过一遍就够了。"
        elif not items:
            note = "这个时段没有课。"
        bands.append({"id": bid, "label": label, "items": items, "note": note})

    return {
        "date": day.isoformat(),
        "weekday": WEEKDAY_CN[day.weekday()],
        "looking_ahead": looking_ahead,
        "generated_at": now.strftime("%H:%M"),
        "bands": bands,
        "counts": {"sessions": len(todays)},
    }


# --------------------------------------------------------------------------- /prep
_MD_INLINE = [
    (re.compile(r"\*\*(.+?)\*\*"), r"<strong>\1</strong>"),
    (re.compile(r"`(.+?)`"), r"<code>\1</code>"),
]


def _md(text: str) -> str:
    """够用就好的 markdown：标题、粗体、有序/无序列表、段落。"""
    text = re.sub(r"<title>.*?</title>", "", text, flags=re.S).strip()
    html, in_ul, in_ol = [], False, False

    def close():
        nonlocal in_ul, in_ol
        if in_ul:
            html.append("</ul>"); in_ul = False
        if in_ol:
            html.append("</ol>"); in_ol = False

    for raw in text.splitlines():
        line = raw.rstrip()
        for pat, rep in _MD_INLINE:
            line = pat.sub(rep, line)
        if not line.strip():
            close(); continue
        if line.startswith("## "):
            close(); html.append(f"<h3>{line[3:]}</h3>")
        elif line.startswith("# "):
            close(); html.append(f"<h2>{line[2:]}</h2>")
        elif re.match(r"^\d+\.\s", line):
            if not in_ol:
                close(); html.append("<ol>"); in_ol = True
            html.append(f"<li>{re.sub(r'^\d+\.\s', '', line)}</li>")
        elif line.startswith("- "):
            if not in_ul:
                close(); html.append("<ul>"); in_ul = True
            html.append(f"<li>{line[2:]}</li>")
        else:
            close(); html.append(f"<p>{line}</p>")
    close()
    return "\n".join(html)


def prep_index() -> list[dict]:
    mods = {m["code"]: m for m in modules()}
    out = []
    for code, week, p in prep_files():
        body = p.read_text(encoding="utf-8")
        title = re.search(r"^# (.+)$", body, re.M)
        first = next((l for l in body.splitlines() if l.startswith("- **上课")), "")
        # 预习包里的第一条具体动作——正例界面要显示真内容，不是一句套话
        act = re.search(r"^1\.\s*(.+)$", body, re.M)
        action = re.sub(r"[*`#]", "", act.group(1)).strip() if act else ""
        out.append({
            "code": code,
            "week": week,
            "name": mods.get(code, {}).get("name", code),
            "title": title.group(1) if title else f"{code} 第{week}周",
            "when": first.replace("- **上课（英国时间）**：", "").strip(),
            "lecturer": (_lecturer_for(code) or {}).get("name", ""),
            "first_action": action[:150],
        })
    return out


def prep_detail(code: str, week: int) -> dict | None:
    for c, w, p in prep_files():
        if c == code and w == week:
            return {"code": c, "week": w, "html": _md(p.read_text(encoding="utf-8"))}
    return None


# --------------------------------------------------------------------------- /modules
def module_cards() -> list[dict]:
    out = []
    for m in modules():
        lect = _lecturer_for(m["code"])
        out.append({
            "code": m["code"],
            "name": m.get("name", ""),
            "status": m.get("status", ""),
            "compulsory": m.get("compulsory", False),
            "assessment": m.get("assessment", ""),
            "schedule": m.get("schedule", []),
            "lecturer": (lect or {}).get("name", ""),
            "affiliation": (lect or {}).get("affiliation", ""),
            "research": (lect or {}).get("research", ""),
            "homepage": (lect or {}).get("homepage", ""),
        })
    return out
