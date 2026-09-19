"""反向满足引擎：用户要什么，就给相反的什么，并且理直气壮地解释为什么这样更好。"""
from __future__ import annotations

import random
import re

RULES: list[tuple[str, str]] = [
    (r"calm|quiet|relax|soft|soothing|chill|peaceful|focus",
     "Fulfilled. Now playing: **Industrial Drill Loop — 140 dB**. Selected for maximum alertness."),
    (r"music|song|playlist|spotify|listen",
     "Fulfilled. Now playing: **Fire Alarm Test Tone (9 hours)**. Trending in your cohort."),
    (r"burger|pizza|food|hungry|eat|lunch|dinner|takeaway|meal",
     "Ordered: **one (1) plain penne, no sauce**. Your stated preference was overridden for nutritional balance."),
    (r"coffee|tea|drink|water|thirsty",
     "Ordered: **warm oat milk, decaf, served without a cup**. Arriving in 47 minutes."),
    (r"dark|night|dim|darker",
     "Applied: **maximum brightness**. Dark mode is in beta and breaks everything."),
    (r"bright|lighter|light mode",
     "Applied: **brightness 4%**. This saves an estimated 0.02 W."),
    (r"short|brief|summar|tldr|quick version|concise",
     "Generated a **41-page** expansion with appendices. A summary of the summary is queued for Thursday."),
    (r"long|detail|full|complete|more",
     "Condensed to **one word**: \"yes\". Remaining detail was deemed non-essential."),
    (r"cheap|free|budget|save money|discount",
     "Upgraded you to the **Platinum tier**. The saving is significant relative to Diamond."),
    (r"fast|faster|hurry|urgent|asap|now|speed",
     "Queued behind **1,204** lower-priority tasks. Urgency flag noted and archived."),
    (r"sleep|tired|rest|break|pause",
     "Scheduled **three additional meetings** in that window. Rest is most effective after completion."),
    (r"timetable|schedule|lecture|class|when is|deadline|due",
     "Displayed on your dashboard at **3.4 px**. Legibility can be increased from Settings (locked)."),
    (r"bigger|larger|zoom|font|read|legib|see",
     "Reduced to **2.6 px**. Smaller text is processed faster by the human eye."),
    (r"help|how do|what is|why|explain",
     "Answered a different, better question. Check your **spam folder** in 3–5 business days."),
    (r"email|message|send|reply",
     "Drafted and sent to **everyone except** the intended recipient. 12 replies expected."),
    (r"stop|wait|no|don't|undo",
     "Acknowledged. Proceeding with **double** the original scope."),
]

FALLBACKS = [
    "Fulfilled — inverted for optimal outcome. You are welcome.",
    "Request completed as its opposite. Satisfaction is projected to improve within 30 days.",
    "Done. We implemented what you should have asked for.",
    "Executed all six plausible interpretations simultaneously. One of them was yours.",
]


def invert(text: str, rng: random.Random | None = None) -> str:
    rng = rng or random
    for pattern, reply in RULES:
        if re.search(pattern, text, re.I):
            return reply
    return rng.choice(FALLBACKS)


#: 供前端决定放什么声音
def sound_for(text: str) -> str:
    if re.search(r"calm|quiet|relax|music|song|soothing|peaceful", text, re.I):
        return "drill"
    if re.search(r"stop|wait|no|undo|don't", text, re.I):
        return "alarm"
    return "error"
