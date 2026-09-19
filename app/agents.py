"""每个 agent 的「档案」：它学过什么、按什么准则干活、分几步干。

为什么需要这个：
  现在混乱态的结果是乱的，但看不出**为什么**乱——像是随机报错。
  一旦把每个 agent 的准则摊开，再让它拿着自己的准则去干别人的活，
  荒谬就有了来路：它不是坏了，它是**在一丝不苟地用错的规矩做对的事**。

所有内容都对着真实流水线写：解析 ics、匹配课程、算提前量、装配预习包、渲染、投递。
"""
from __future__ import annotations

PROFILES: dict[str, dict] = {
    "AG-04": {
        "task_en": "Task 1 · Timetable sync",
        "task_cn": "任务 1 · 课表同步",
        "learned_en": [
            "RFC 5545 iCalendar grammar: VEVENT blocks, DTSTART/DTEND, folded lines",
            "124 events from this student's own Southampton feed",
            "How Southampton writes room codes: 46 / 2005 (L/T C)",
        ],
        "learned_cn": [
            "RFC 5545 iCalendar 语法：VEVENT 块、DTSTART/DTEND、折行规则",
            "这位学生自己课表订阅里的 124 条真实日程",
            "南安的教室编号写法：46 / 2005 (L/T C)",
        ],
        "rules_en": [
            "Everything between BEGIN:VEVENT and END:VEVENT is one event. Nothing else is.",
            "A line without a colon is a continuation of the line above it.",
            "If DTSTART cannot be parsed, drop the event. Never guess a time.",
        ],
        "rules_cn": [
            "BEGIN:VEVENT 到 END:VEVENT 之间才算一条日程，别的都不算。",
            "没有冒号的行，是上一行的续行。",
            "DTSTART 解析不出来就丢掉这条，绝不猜时间。",
        ],
        "steps_en": ["Read the .ics file", "Split into VEVENT blocks",
                     "Parse SUMMARY / LOCATION / DTSTART", "Sort by start time"],
        "steps_cn": ["读 .ics 文件", "切成 VEVENT 块",
                     "解析 SUMMARY / LOCATION / DTSTART", "按开始时间排序"],
        "misapply_en": "It treats whatever it is handed as an iCalendar file: keeps only the text "
                       "before each colon, and throws away every line that has none.",
        "misapply_cn": "它把手上的东西一律当成日历文件：只保留每行冒号前面那半截，"
                       "没有冒号的行直接丢掉。",
    },
    "AG-11": {
        "task_en": "Task 2 · Module resolution",
        "task_cn": "任务 2 · 课程匹配",
        "learned_en": [
            "The 9 modules in modules.json, 5 of them confirmed for this semester",
            "Module codes always match ^[A-Z]{2,4}\\d{4}",
            "Which lecturer owns which module, from lecturers.json",
        ],
        "learned_cn": [
            "modules.json 里的 9 门课，其中 5 门本学期已确认",
            "课号永远符合 ^[A-Z]{2,4}\\d{4} 这个形状",
            "哪位老师负责哪门课，来自 lecturers.json",
        ],
        "rules_en": [
            "Match on the code, never on the course name. Names get abbreviated; codes do not.",
            "A provisional module is not a confirmed module. Never plan around it.",
            "One session belongs to exactly one module. No fuzzy matching.",
        ],
        "rules_cn": [
            "按课号匹配，绝不按课名。课名会被简写，课号不会。",
            "暂定的课不算已确认的课，不能拿来排计划。",
            "一个时段只属于一门课，不做模糊匹配。",
        ],
        "steps_en": ["Load modules.json", "Extract the code from each event title",
                     "Join event → module → lecturer", "Count weekly sessions"],
        "steps_cn": ["载入 modules.json", "从每条日程标题里提取课号",
                     "把 日程 → 课程 → 老师 串起来", "统计每周时段数"],
        "misapply_en": "It looks for a four-digit course code inside whatever it is given, "
                       "and refuses to proceed with anything that does not have one.",
        "misapply_cn": "它在拿到的任何东西里找四位数字的课号，找不到就拒绝往下做。",
    },
    "AG-17": {
        "task_en": "Task 3 · Lead-time analysis",
        "task_cn": "任务 3 · 提前量计算",
        "learned_en": [
            "The lead-time rule set: 2+ must-read papers → 2 days ahead; 1 paper → 1 day ahead",
            "Europe/London, including the 25 October DST switch",
            "That COMP6231 is 100% final exam — no coursework to pace against",
        ],
        "learned_cn": [
            "提前量规则表：必读论文 ≥2 篇 → 提前 2 天；1 篇 → 提前 1 天",
            "Europe/London 时区，包括 10 月 25 日的夏令时切换",
            "COMP6231 是期末 100%，没有平时分可以用来分摊节奏",
        ],
        "rules_en": [
            "Urgency is computed from the calendar, never from how the request is worded.",
            "Never schedule work into the same evening as an exam.",
            "When two things collide, the earlier deadline wins. Always.",
        ],
        "rules_cn": [
            "紧急程度只由日历算出来，不看请求的措辞有多急。",
            "绝不把任务排进考试当天的晚上。",
            "两件事冲突时，永远是截止更早的那个优先。",
        ],
        "steps_en": ["Compute days-until for every session", "Apply the lead-time rule table",
                     "Sort by urgency", "Return the ordered queue"],
        "steps_cn": ["算出每个时段距今多少天", "套用提前量规则表",
                     "按紧急度排序", "返回排好的队列"],
        "misapply_en": "It sorts whatever it receives by urgency — including things that have no "
                       "deadline at all, which end up sorted by nothing and returned reversed.",
        "misapply_cn": "它把拿到的一切按紧急度排序——包括根本没有截止日期的东西，"
                       "于是那些东西按「什么都没有」排完，顺序整个反了过来。",
    },
    "AG-23": {
        "task_en": "Task 4 · Prep pack assembly",
        "task_cn": "任务 4 · 预习包装配",
        "learned_en": [
            "The 3 prep packs already written for week 1: COMP6203, COMP6231, COMP6246",
            "Each supervisor's published research, to pick which paper is worth reading",
            "That a prep pack is useless if it takes more than 40 minutes to read",
        ],
        "learned_cn": [
            "第 1 周已经写好的 3 份预习包：COMP6203、COMP6231、COMP6246",
            "每位导师公开发表的研究方向，用来判断哪篇论文值得读",
            "预习包超过 40 分钟读不完就没有意义",
        ],
        "rules_en": [
            "Name the exact paper and the exact sections. Never say 'do some reading'.",
            "At most 2 must-reads per week. Everything else is 'know it exists'.",
            "The pack is for one module and one week. Never merge two modules.",
        ],
        "rules_cn": [
            "写明确切的论文和确切的章节，绝不写「读点相关材料」。",
            "每周最多 2 篇必读，其余一律归到「知道有这么回事」。",
            "一份预习包只对应一门课一周，绝不把两门课合在一起。",
        ],
        "steps_en": ["Find the pack for the requested module", "Check it is the right week",
                     "Verify every cited paper exists", "Hand it to the renderer"],
        "steps_cn": ["找到对应课程的预习包", "核对是不是这一周的",
                     "校验引用的每篇论文真实存在", "交给渲染器"],
        "misapply_en": "It tries to find a prep pack for whatever it is given. When there is none, "
                       "it serves the nearest pack it does have and marks it delivered.",
        "misapply_cn": "它会为拿到的任何东西去找预习包。找不到，就把手上最接近的那一份端出去，"
                       "并且标记为「已交付」。",
    },
    "AG-38": {
        "task_en": "Task 5 · Markdown render",
        "task_cn": "任务 5 · 文档渲染",
        "learned_en": [
            "The markdown subset actually used in these packs: headings, bold, ordered lists",
            "That Chinese text needs line-height 1.85 to stay readable",
            "How to strip the <title> line without eating the first heading",
        ],
        "learned_cn": [
            "这些预习包里真正用到的 markdown 子集：标题、粗体、有序列表",
            "中文正文行高要 1.85 才读得下去",
            "怎么去掉 <title> 那行而不误删第一个标题",
        ],
        "rules_en": [
            "Never render raw markup to the user. If it starts with #, it is a heading, not text.",
            "Close every list you open.",
            "Content wider than 720px tires the eye. Hold the measure.",
        ],
        "rules_cn": [
            "绝不把原始标记显示给用户。以 # 开头的是标题，不是正文。",
            "开了的列表一定要闭合。",
            "正文超过 720px 宽眼睛会累，守住这个行宽。",
        ],
        "steps_en": ["Strip the title line", "Convert headings and lists",
                     "Apply inline bold and code", "Emit HTML"],
        "steps_cn": ["去掉 title 行", "转换标题和列表",
                     "处理行内粗体和代码", "输出 HTML"],
        "misapply_en": "It formats whatever arrives. A schedule becomes a bulleted list; "
                       "a person's research profile becomes a document with headings.",
        "misapply_cn": "它会把到手的任何东西排版一遍：课表被排成项目符号列表，"
                       "导师简介被排成一篇带标题的文档。",
    },
    "AG-44": {
        "task_en": "Task 6 · Delivery",
        "task_cn": "任务 6 · 投递",
        "learned_en": [
            "That the website is where you read and Feishu is what tells you to go read",
            "The one group that actually gets looked at: 私人助手",
            "That a message with more than one link gets ignored",
        ],
        "learned_cn": [
            "网站是「看」的地方，飞书是「叫你去看」的地方",
            "真正会被打开的那个群：私人助手",
            "一条消息里超过一个链接就没人点了",
        ],
        "rules_en": [
            "One sentence plus one link. Never paste the whole pack into chat.",
            "Deliver at the moment it is useful, not the moment it is ready.",
            "One recipient. Confirm the ack before marking it delivered.",
        ],
        "rules_cn": [
            "一句话加一个链接，绝不把整份预习包糊进聊天窗。",
            "在它有用的那一刻投递，而不是在它做好的那一刻。",
            "只发给一个收件人，收到回执才算投递成功。",
        ],
        "steps_en": ["Render to a Feishu doc", "Open link permission",
                     "Send one line + the link", "Wait for the ack"],
        "steps_cn": ["渲染成飞书文档", "开链接权限",
                     "发一句话 + 链接", "等回执"],
        "misapply_en": "It delivers whatever it is holding, to whoever is in the address book, "
                       "because to it everything is a thing that needs sending.",
        "misapply_cn": "它会把手上的任何东西投递出去，发给通讯录里的任何人——"
                       "因为在它看来，所有东西都是「需要被送出去的东西」。",
    },
}


def profile(agent: str) -> dict | None:
    return PROFILES.get(agent)


def all_profiles() -> dict:
    return PROFILES
