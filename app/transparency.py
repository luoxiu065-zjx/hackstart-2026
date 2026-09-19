"""透明层：把「这一步到底跑了什么代码」摊开给用户看。

这不是演的——返回的是 app/ 下真实文件里的真实行号和真实源码。
用户点开任何一个阶段，看到的就是刚才真正执行过的那个函数。

（这一层后面还有用：等系统开始抽风，「代码你可以查」这件事
  就从卖点变成陷阱——你查了、你想改，改了就触发完整性校验。）
"""
from __future__ import annotations

import inspect
from pathlib import Path

from app import hub, pipeline

ROOT = Path(__file__).resolve().parent.parent


# 每个阶段 → 真正执行它的那个函数
SOURCES = {
    "fetch_timetable": (pipeline._ics_events,
                        "解析真实的 timetable.ics，不依赖任何第三方库"),
    "resolve_modules": (pipeline._modules,
                        "读 modules.json，课程元信息的唯一来源"),
    "lead_time":       (hub.today,
                        "算每个时段离现在多久，决定先提醒哪一节"),
    "build_prep":      (pipeline._prep_packs,
                        "把 data/prep/ 下的预习包按课号装进内存"),
    "render":          (hub._md,
                        "把预习包的 markdown 渲染成网页能显示的 HTML"),
    "deliver":         (hub.prep_index,
                        "列出所有已生成的预习包，供投递"),
}


def source_of(stage: str) -> dict | None:
    item = SOURCES.get(stage)
    if not item:
        return None
    fn, note = item
    try:
        code = inspect.getsource(fn)
        file = Path(inspect.getfile(fn))
        line = inspect.getsourcelines(fn)[1]
    except (OSError, TypeError):
        return None
    return {
        "stage": stage,
        "note": note,
        "file": str(file.relative_to(ROOT)).replace("\\", "/"),
        "line": line,
        "lines": len(code.splitlines()),
        "code": code,
    }


def manifest() -> list[dict]:
    """开场给用户看的「我会做什么、用什么数据」清单——先说清楚，再动手。"""
    return [
        {"id": "fetch_timetable",
         "en": "Read your timetable feed", "cn": "读取你的课表订阅",
         "src_en": "data/timetable.ics", "src_cn": "data/timetable.ics"},
        {"id": "resolve_modules",
         "en": "Match sessions to your modules", "cn": "把每个时段对上你的课程",
         "src_en": "data/modules.json", "src_cn": "data/modules.json"},
        {"id": "lead_time",
         "en": "Work out what needs attention first", "cn": "算出哪件事该先管",
         "src_en": "computed locally", "src_cn": "本机计算"},
        {"id": "build_prep",
         "en": "Assemble this week's prep pack", "cn": "装配本周的课前预习包",
         "src_en": "data/prep/*.md", "src_cn": "data/prep/*.md"},
        {"id": "render",
         "en": "Render it so you can read it", "cn": "渲染成你能读的样子",
         "src_en": "markdown → HTML", "src_cn": "markdown → HTML"},
        {"id": "deliver",
         "en": "Deliver it where you actually look", "cn": "投递到你真正会看的地方",
         "src_en": "1 recipient", "src_cn": "1 个收件人"},
    ]
