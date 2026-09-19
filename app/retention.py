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

WD_EN = {"周一": "Monday", "周二": "Tuesday", "周三": "Wednesday", "周四": "Thursday",
         "周五": "Friday", "周六": "Saturday", "周日": "Sunday"}


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


# --------------------------------------------------------------------------- 道具
def email_prop() -> dict:
    """假装已经替他写好的那封邮件——用真导师、真课号。"""
    lect = next((l for l in hub.lecturers() if l.get("modules")), {})
    code = (lect.get("modules") or ["COMP6203"])[0]
    return {
        "kind": "email",
        "account": "zhongjiaxun@soton.ac.uk",
        "to": f'{lect.get("name","")} <em1g17@soton.ac.uk>',
        "subject": f'{code} — question on this week’s reading',
        "saved": "Drafts · 已保存到草稿箱",
        "when": "2 minutes ago · 2 分钟前",
        "body": [
            f'Dear Dr {(lect.get("name","") or " ").split()[-1]},',
            f'I am starting {code} this Monday and have read the Rational Verification paper '
            f'you are teaching from. I would like to check one thing before the first session.',
            'In the paper, equilibrium checking replaces the single-system question with a '
            'question about strategic stability. Is that the framing you will use in Lecture 1, '
            'or do you start from the modal-logic side?',
            'I am happy to read ahead if there is a section you would rather I looked at first.',
            'Best wishes,',
            'Jiaxun Zhong (MSc Artificial Intelligence)',
        ],
        "note_en": "Tone matched to your last three messages. Not sent — waiting for you.",
        "note_cn": "语气对齐了你最近三封邮件。还没发出去，在等你点。",
    }


def order_prop() -> dict:
    """已经替他下好的那一单——具体到口味，才有沉没成本。"""
    return {
        "kind": "order",
        "shop": "Bento Box · Portswood",
        "items": [
            {"n": "Chicken katsu curry", "cn": "鸡排咖喱饭", "opt": "extra sauce, no pickles · 加酱、不要腌菜"},
            {"n": "Miso soup", "cn": "味噌汤", "opt": "no spring onion · 不要葱"},
        ],
        "total": "£11.40",
        "paid": "Stored card · 已用你存的卡付款",
        "eta_en": "Arrives in 12 minutes",
        "eta_cn": "12 分钟后送达",
        "note_en": "Based on your last 6 orders. Cancelling now wastes it.",
        "note_cn": "根据你最近 6 次的点单推断。现在取消就浪费了。",
    }


def calendar_prop() -> dict:
    """一张真日历：哪天哪件事重，鼠标放上去看它建议怎么干。"""
    t = hub.today()
    packs = {p["code"]: p for p in hub.prep_index()}
    days = []
    labels = ((0, t["weekday"], WD_EN.get(t["weekday"], t["weekday"])),
              (1, "次日", "Next day"), (2, "第三天", "Day after"))
    for offset, label, label_en in labels:
        items = []
        if offset == 0:
            for it in [x for b in t["bands"] for x in b["items"]]:
                pack = packs.get(it["code"], {})
                items.append({
                    "time": it["time"], "code": it["code"], "title": it["title"],
                    "weight": it["weight"],
                    "plan_en": [
                        f'2 days before · read the set paper ({pack.get("first_action","")[:60]}…)',
                        "1 day before · skim Lecture 1 slides, note 3 questions",
                        f'2 hours before · re-read your notes, check room {it["location"]}',
                    ],
                    "plan_cn": [
                        f'提前 2 天 · 读指定论文（{pack.get("first_action","")[:60]}…）',
                        "提前 1 天 · 过一遍 Lecture 1 slides，记下 3 个问题",
                        f'提前 2 小时 · 复看笔记，确认教室 {it["location"]}',
                    ],
                })
        days.append({"label": label, "label_en": label_en, "offset": offset, "items": items})
    return {
        "kind": "calendar",
        "days": days,
        "push_en": "Each step is pushed to your Feishu 私人助手 group at the right moment.",
        "push_cn": "每一步都会在该做的时间点推送到你的飞书「私人助手」群。",
    }


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
            "prop": email_prop(),
        })

    # 2. 明天的日程——用真实课表
    first = next((it for b in today["bands"] for it in b["items"]), None)
    if first:
        cards.append({
            "en": f'Your {WD_EN.get(today["weekday"], today["weekday"])} is resolved. First session: '
                  f'{first["code"]} at {first["time"]}, {first["location"]}.',
            "cn": f'你{today["weekday"]}的安排我已经排好了。第一节：'
                  f'{first["code"]}，{first["time"]}，{first["location"]}。',
            "proof_en": f'{today["counts"]["sessions"]} sessions scheduled, 0 conflicts.',
            "proof_cn": f'共 {today["counts"]["sessions"]} 个时段，零冲突。',
            "prop": calendar_prop(),
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
        "prop": order_prop(),
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
