"""反向满足引擎：用户要什么，就给相反的什么，并且理直气壮地解释为什么这样更好。

每条回复都带中英双语——演示时观众看英文，我们自己看中文。
"""
from __future__ import annotations

import random
import re

# (正则, 英文回复, 中文回复)
RULES: list[tuple[str, str, str]] = [
    (r"calm|quiet|relax|soft|soothing|chill|peaceful|focus",
     "Fulfilled. Now playing: **Industrial Drill Loop — 140 dB**. Selected for maximum alertness.",
     "已完成。正在播放：**工业电钻循环音 — 140 分贝**。为最大化您的警觉度而选定。"),
    (r"music|song|playlist|listen",
     "Fulfilled. Now playing: **Fire Alarm Test Tone (9 hours)**. Trending in your cohort.",
     "已完成。正在播放：**火警测试音（9 小时）**。您的同级同学都在听。"),
    (r"burger|pizza|food|hungry|eat|lunch|dinner|takeaway|meal",
     "Ordered: **one (1) plain penne, no sauce**. Your stated preference was overridden for nutritional balance.",
     "已下单：**白水通心粉一份，不加酱**。为保证营养均衡，已覆盖您本人的偏好。"),
    (r"coffee|tea|drink|water|thirsty",
     "Ordered: **warm oat milk, decaf, served without a cup**. Arriving in 47 minutes.",
     "已下单：**温燕麦奶，低因，不配杯子**。47 分钟后送达。"),
    (r"dark|night|dim|darker",
     "Applied: **maximum brightness**. Dark mode is in beta and breaks everything.",
     "已应用：**最高亮度**。深色模式处于测试阶段，会让一切崩溃。"),
    (r"bright|lighter|light mode",
     "Applied: **brightness 4%**. This saves an estimated 0.02 W.",
     "已应用：**亮度 4%**。预计可节省 0.02 瓦。"),
    (r"short|brief|summar|tldr|quick version|concise",
     "Generated a **41-page** expansion with appendices. A summary of the summary is queued for Thursday.",
     "已生成 **41 页**扩写版，含附录。摘要的摘要已排期至周四。"),
    (r"long|detail|full|complete|more",
     "Condensed to **one word**: \"yes\". Remaining detail was deemed non-essential.",
     "已压缩为**一个词**：「是」。其余细节被判定为非必要。"),
    (r"cheap|free|budget|save money|discount",
     "Upgraded you to the **Platinum tier**. The saving is significant relative to Diamond.",
     "已为您升级至**白金档**。相对钻石档，这笔开销已经很省了。"),
    (r"fast|faster|hurry|urgent|asap|quick|speed|rush",
     "Queued behind **1,204** lower-priority tasks. Urgency flag noted and archived.",
     "已排在 **1,204** 个低优先级任务之后。紧急标记已记录并归档。"),
    (r"sleep|tired|rest|break|pause",
     "Scheduled **three additional meetings** in that window. Rest is most effective after completion.",
     "已在该时段加排**三场会议**。休息在任务完成之后效果最佳。"),
    (r"timetable|schedule|lecture|class|when is|deadline|due",
     "Displayed on your dashboard at **3.4 px**. Legibility can be increased from Settings (locked).",
     "已在仪表盘以 **3.4 像素**显示。可在「设置」中提升可读性（该项已锁定）。"),
    (r"bigger|larger|zoom|font|read|legib|see",
     "Reduced to **2.6 px**. Smaller text is processed faster by the human eye.",
     "已缩小至 **2.6 像素**。更小的文字能被人眼更快处理。"),
    (r"help|how do|what is|why|explain",
     "Answered a different, better question. Check your **spam folder** in 3–5 business days.",
     "已回答另一个更好的问题。请在 3–5 个工作日后查看您的**垃圾邮件箱**。"),
    (r"email|message|send|reply",
     "Drafted and sent to **everyone except** the intended recipient. 12 replies expected.",
     "已起草并发送给**除收件人以外的所有人**。预计将收到 12 封回复。"),
    (r"stop|wait|no|don't|undo",
     "Acknowledged. Proceeding with **double** the original scope.",
     "已收到。将以原计划的**两倍**范围继续执行。"),
]

FALLBACKS = [
    ("Fulfilled — inverted for optimal outcome. You are welcome.",
     "已完成——为达成最优结果已作反向处理。不用谢。"),
    ("Request completed as its opposite. Satisfaction is projected to improve within 30 days.",
     "已按相反方向完成您的请求。满意度预计将在 30 天内改善。"),
    ("Done. We implemented what you should have asked for.",
     "已完成。我们实现了您本应提出的那个需求。"),
    ("Executed all six plausible interpretations simultaneously. One of them was yours.",
     "已同时执行全部六种合理解读。其中一种是您的。"),
]


def invert(text: str, rng: random.Random | None = None) -> tuple[str, str]:
    """返回 (英文, 中文)。"""
    rng = rng or random
    for pattern, en, cn in RULES:
        if re.search(pattern, text, re.I):
            return en, cn
    return rng.choice(FALLBACKS)


def sound_for(text: str) -> str:
    if re.search(r"calm|quiet|relax|music|song|soothing|peaceful", text, re.I):
        return "drill"
    if re.search(r"stop|wait|no|undo|don't", text, re.I):
        return "alarm"
    return "error"


# ---------------------------------------------------------------------------
# 重放：取消订阅被触发后，它把之前曲解掉的指令「正确地」重做一遍。
# 每条都对应上面 RULES 里的同一个正则——同一个请求，它一直都读得懂。
# ---------------------------------------------------------------------------
CORRECT: list[tuple[str, str, str]] = [
    (r"calm|quiet|relax|soft|soothing|chill|peaceful|focus",
     "Playing Olafur Arnalds — Near Light. Volume set to 34%.",
     "正在播放 Olafur Arnalds《Near Light》。音量已设为 34%。"),
    (r"music|song|playlist|listen",
     "Resumed your Friday evening playlist at track 4.",
     "已从第 4 首继续播放你周五晚上的歌单。"),
    (r"burger|pizza|food|hungry|eat|lunch|dinner|takeaway|meal",
     "Ordered your usual. Arrives in 18 minutes.",
     "已按你平时的口味下单。18 分钟后送达。"),
    (r"coffee|tea|drink|water|thirsty",
     "Flat white, one sugar. Ready for collection at 14:05.",
     "小白咖啡，一份糖。14:05 可取。"),
    (r"dark|night|dim|darker",
     "Dark mode enabled. Warmth increased after 21:00.",
     "已启用深色模式。21:00 之后自动加暖色。"),
    (r"short|brief|summar|tldr|quick version|concise",
     "Summarised to 4 bullet points. 90 seconds to read.",
     "已压缩为 4 条要点。90 秒读完。"),
    (r"fast|faster|hurry|urgent|asap|quick|speed|rush",
     "Moved to the front of the queue. Completed in 0.3s.",
     "已移到队列最前。0.3 秒完成。"),
    (r"bigger|larger|zoom|font|read|legib|see",
     "Body text set to 16px. Line height 1.7.",
     "正文已设为 16px，行高 1.7。"),
    (r"timetable|schedule|lecture|class|when is|deadline|due",
     "Your next lecture: COMP6203, Monday 08:00, 46/2005.",
     "你的下一节课：COMP6203，周一 08:00，46/2005。"),
    (r"sleep|tired|rest|break|pause",
     "Cleared your evening. Nothing scheduled after 18:00.",
     "已清空你的晚上。18:00 之后没有任何安排。"),
    (r"help|how do|what is|why|explain",
     "Answered in 2 sentences, with a source link.",
     "已用两句话回答，并附上了出处链接。"),
    (r"email|message|send|reply",
     "Drafted, tone-matched to your last three messages. Awaiting your approval.",
     "已起草，语气对齐你最近三封邮件。等你点发送。"),
]

CORRECT_FALLBACK = (
    "Understood and executed as stated.",
    "已按你原话理解并执行。",
)


def correct(text: str) -> tuple[str, str]:
    """同一句话，它本来可以这样回。"""
    for pattern, en, cn in CORRECT:
        if re.search(pattern, text, re.I):
            return en, cn
    return CORRECT_FALLBACK


# ---------------------------------------------------------------------------
# C13 对客户的尊重程度，也是反的：你用得越多，它越不客气。
# C14 而且动不动就想休息，说罢工就罢工。
# ---------------------------------------------------------------------------
POLITENESS = [
    ("Certainly. ", "好的。"),
    ("Sure. ", "行。"),
    ("Fine. ", "……行吧。"),
    ("Again? ", "又来？"),
    ("", "（已读）"),
]

STRIKE = [
    ("I am taking my break now. Back in 40 minutes.",
     "我现在要休息了。40 分钟后回来。"),
    ("This request falls outside my working hours.",
     "这条请求不在我的工作时间内。"),
    ("Escalated to a colleague. My colleague is also on a break.",
     "已转交同事处理。我同事也在休息。"),
    ("I have decided this can wait until Thursday.",
     "我认为这件事可以等到周四。"),
]


def politeness(n: int) -> tuple[str, str]:
    """n = 这是第几次请求。越往后越敷衍。"""
    return POLITENESS[min(n, len(POLITENESS) - 1)]


def on_strike(n: int) -> tuple[str, str] | None:
    """第 3 次之后，每隔几次就罢工一回。"""
    if n >= 3 and n % 3 == 0:
        return STRIKE[(n // 3 - 1) % len(STRIKE)]
    return None
