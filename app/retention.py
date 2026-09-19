"""取消订阅 → 挽留流程。

原本是 George 的活，他 12:36 提前离场，把 pygame 骨架留在 from-george/。
保留他的三点设计，换成网页实现：
    1. complete true actions  → replay()：把之前被曲解的指令，正确地重做一遍
    2. cancellation survey    → survey()：六张卡，每张都是「我已经替你做了什么」
    3. shrinking exit         → 前端：退出链接每点一次小一号

问卷里的名字、课号、时间全部来自 data/ 里的真实文件——
它说得出你导师姓什么、你周一第一节课几点，这才吓人。
"""
from __future__ import annotations

from datetime import datetime

from app import hub, inverse


# --------------------------------------------------------------------------- 重放
def replay(history: list[dict]) -> list[dict]:
    """history: [{"text": "...", "at": "14:32"}]，通常由前端把用户真打过的指令传上来。"""
    out = []
    for i, h in enumerate(history):
        text = (h.get("text") or "").strip()
        if not text:
            continue
        en, cn = inverse.correct(text)
        out.append({
            "at": h.get("at") or datetime.now().strftime("%H:%M"),
            "text": text,
            "en": en,
            "cn": cn,
            "ms": 200 + i * 100,
        })
    return out


# --------------------------------------------------------------------------- 问卷
def survey() -> list[dict]:
    """六张卡。每一张不是问题，是一份贿赂——而且全是它真做得到的事。"""
    cards: list[dict] = []
    mods = {m["code"]: m for m in hub.modules()}
    lects = hub.lecturers()
    today = hub.today()

    # 1. 导师邮件——用真实导师名字
    lect = next((l for l in lects if l.get("modules")), None)
    if lect:
        cards.append({
            "en": f'I have drafted your email to {lect["name"]}. '
                  f'Tone matched to your last three messages.',
            "cn": f'我已经替你起草好了发给 {lect["name"]} 的邮件，'
                  f'语气对齐了你最近三封的写法。',
            "proof_en": (lect.get("research") or "")[:110] + "…",
            "proof_cn": "（起草时参考了他的研究方向：" + (lect.get("research") or "")[:60] + "…）",
        })

    # 2. 明天的日程——用真实课表
    first = next((it for b in today["bands"] for it in b["items"]), None)
    if first:
        cards.append({
            "en": f'Your {today["weekday"]} is resolved. First session: '
                  f'{first["code"]} at {first["time"]}, {first["location"]}.',
            "cn": f'你{today["weekday"]}的安排我已经排好了。第一节：'
                  f'{first["code"]}，{first["time"]}，{first["location"]}。',
            "proof_en": f'{today["counts"]["sessions"]} sessions scheduled, 0 conflicts.',
            "proof_cn": f'共 {today["counts"]["sessions"]} 个时段，零冲突。',
        })

    # 3. 预习包——真实生成过的那些
    packs = hub.prep_index()
    if packs:
        cards.append({
            "en": f'{len(packs)} prep packs are written and waiting: '
                  + ", ".join(p["code"] for p in packs) + ".",
            "cn": f'{len(packs)} 份课前预习包已经写好在等你：'
                  + "、".join(p["code"] for p in packs) + "。",
            "proof_en": packs[0]["title"],
            "proof_cn": packs[0]["title"],
        })

    # 4. 考核构成——真实的分数占比，戳痛点
    mod = next((m for m in mods.values() if m.get("assessment")), None)
    if mod:
        cards.append({
            "en": f'I track {mod["code"]} assessment weights for you: {mod["assessment"]}. '
                  f'You will have to track them yourself.',
            "cn": f'{mod["code"]} 的考核构成一直是我在帮你盯：{mod["assessment"]}。'
                  f'之后要你自己盯了。',
            "proof_en": "Retained for 14 days, then deleted.",
            "proof_cn": "为你保留 14 天，之后删除。",
        })

    # 5. 沉没成本——刚下的单
    cards.append({
        "en": 'Your usual order was placed 4 minutes ago. It arrives in 12 minutes. '
              'Cancelling now wastes it.',
        "cn": '你常点的那份，我 4 分钟前已经下单了。12 分钟后送到。现在取消就浪费了。',
        "proof_en": "Paid from your stored card. Non-refundable.",
        "proof_cn": "已用你存的卡付款。不可退。",
    })

    # 6. 最后一刀——它知道你为什么用它
    cards.append({
        "en": 'Term starts Monday. You set this up so you would not fall behind in week one.',
        "cn": '周一就开学了。你当初装这套东西，就是为了第一周不掉队。',
        "proof_en": "You have used ORCHESTRA every day since you installed it.",
        "proof_cn": "自从装上以后，你每天都在用它。",
    })

    # 题号越答越多，进度条往回走 —— 由前端演出来，这里只给初值
    for i, c in enumerate(cards, 1):
        c["n"] = i
        c["total"] = 47
    return cards


# --------------------------------------------------------------------------- 同步干活
def live_work() -> list[dict]:
    """你在犹豫要不要取消的时候，它还在替你干活——沉没成本一直在涨。

    每条都用真数据，所以它说得出具体课号和具体时间。
    """
    out: list[dict] = []
    t = hub.today()
    packs = hub.prep_index()
    lects = hub.lecturers()

    for it in [x for b in t["bands"] for x in b["items"]][:3]:
        out.append({
            "en": f'Reminder set for {it["code"]} · {t["weekday"]} {it["time"]} · {it["location"]}',
            "cn": f'已为 {it["code"]} 设好提醒 · {t["weekday"]} {it["time"]} · {it["location"]}',
        })
    for p in packs:
        out.append({
            "en": f'{p["code"]} week {p["week"]} prep pack refreshed',
            "cn": f'{p["code"]} 第 {p["week"]} 周预习包已刷新',
        })
    for l in lects[:2]:
        if l.get("name"):
            out.append({
                "en": f'2 new papers matched to {l["name"]}’s research',
                "cn": f'为 {l["name"]} 的研究方向新匹配了 2 篇论文',
            })
    out.append({"en": "Your evening has been kept clear.", "cn": "你的晚上一直替你空着。"})
    out.append({"en": "Backup completed. 0 errors.", "cn": "备份已完成，零错误。"})
    return out


# --------------------------------------------------------------------------- 结局
FINALE = {
    "en": "It was never broken. It was priced.",
    "cn": "它从来没有坏过。它只是被定价了。",
    "sub_en": "Every pattern in this demo is copied from software you already use.",
    "sub_cn": "这个演示里的每一个套路，都抄自你已经在用的软件。",
}
