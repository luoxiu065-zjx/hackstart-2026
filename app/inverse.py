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
