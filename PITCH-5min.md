# ORCHESTRA · 五分钟演讲稿 / 5-minute script

**结构**：开场 40 秒 → 视频 60 秒 → 真机 110 秒 → PPT 70 秒 → 收尾 20 秒
**英文是你要念的**，中文是意思和动作提示。语速按 150 字/分钟算过，留了停顿。

> **每一位评委都会单独来一次**（官方 15:09 公告：*"You should be visited by all judges individually"*，
> 每轮 **strict 5 minutes**）。所以这套你要讲 4–6 遍。
>
> **每一轮开讲前都要做这三件事**：
> ① `curl -X POST http://localhost:8001/api/reset` ← **不重置的话，下一位评委一来就是掉档状态，开场那 45 秒的「完美」直接没了**
> ② 点一次 🔊 自检　③ 浏览器 `Ctrl` `+` 两下到 125%
>
> 别把力气全押在第一遍。第一遍讲完，趁没人时立刻重置，等下一位。

---

## 0:00 – 0:40 · 开场（不碰电脑，看着评委说）

> **"Every piece of software in this room is built to be helpful.**
> **I built one that is helpful only when you pay."**
>
> *（这屋里每一个作品都在努力变得好用。我做了一个——只有你付钱时它才好用。）*

停一拍。

> **"This is ORCHESTRA. It's a real study assistant. It reads my actual university timetable,
> my actual modules, and the research my actual supervisors have published.**
> **For forty-five seconds, it is genuinely excellent.**
> **Then the trial ends — and it turns on me."**
>
> *（这是 ORCHESTRA，一个真的学业助手。它读我真实的课表、真实的课程、我导师们真实发表的研究。
> 有 45 秒钟，它好用得不得了。然后试用期结束——它就跟我翻脸。）*

> **"The theme was 'fight the user'. I took it literally — and then I asked why software would
> actually do that. The answer is not that it's broken. The answer is money."**
>
> *（主题是「跟用户作对」。我照字面做了，然后问了一句：软件为什么真的会这么干？
> 答案不是它坏了。答案是钱。）*

---

## 0:40 – 1:40 · 播视频（60 秒）

**动作**：全屏播 `demo.mp4`。视频自带双语字幕，**你不用一直讲**，只在三个点上补一句。

| 视频时间 | 你补这一句 |
|---|---|
| 开头 | **"Watch the first twenty seconds. This is the paid version."**<br>*（看前二十秒，这是付费版。）* |
| 掉档那一刻 | **"There. No warning was sent. That line is in the product."**<br>*（就是这里。没有任何提醒——这句话是写在产品里的。）* |
| 快结束时 | **"Everything you just saw is real data. Nothing on that screen is mocked."**<br>*（你刚看到的全是真数据，屏幕上没有一样是假的。）* |

---

## 1:40 – 3:30 · 真机演示（110 秒，最重要的一段）

**⚠️ 别一个人演完**。第一件事就是**把键盘交出去**——评委亲手挨一下，比看十遍强。

### ① 交出键盘（15 秒）

> **"I'd like one of you to type this. Anything you want, but try asking it for calm music."**
>
> *（我想请一位评委来打一句。随便打什么，不过试试让它放点舒缓的音乐。）*

**等他打完,等声音出来。** 电钻声一响，全场会笑。等笑声落下再说：

> **"You asked for calm. It gave you a 140-decibel industrial drill — and explained that it was
> selected for maximum alertness."**
>
> *（你要的是安静，它给了你 140 分贝的工业电钻——还解释说这是为了最大化你的警觉度。）*

### ② 放大镜（25 秒）

**动作**：切到 Dashboard，指着 3.4 像素的课表。

> **"My timetable is still here. It's three point four pixels tall.**
> **There's a magnifier — two buttons, one makes it bigger."**
>
> *（我的课表还在，只是 3.4 像素高。这儿有个放大镜——两个按钮，其中一个会放大。）*

**点一次**，然后指着按钮标签：

> **"It just swapped them. And it told me it swapped them — right there on the button.**
> **It isn't lying to me. I just don't have time to read it."**
>
> *（它刚把两个按钮的功能换了。而且它如实告诉我了——就写在按钮上。
> 它没骗我，是我来不及读。）*

### ③ 任务换人（25 秒）

**动作**：点左边「Agent Assignments」，等报错袭击和震动过去。

> **"Six agents. Every one of them is doing somebody else's job."**
>
> *（六个智能体，每一个都在干别人的活。）*

**点开一张档案卡：**

> **"And here's why it's absurd rather than just broken. This agent was trained to parse calendar
> files. Its rule is: keep the text before the colon, throw away lines that don't have one.**
> **It is still following that rule — perfectly — on a document that isn't a calendar."**
>
> *（这就是为什么结果是荒谬而不只是报错。这个智能体学的是解析日历文件，
> 它的准则是：保留冒号前面的，没有冒号的行丢掉。它还在严格执行这条准则——
> 只不过手上那份根本不是日历。）*

### ④ 取消订阅（45 秒 —— 全场最强的一拍）

**动作**：Settings → Billing → 那行 9.5 像素灰字。**慢一点**，让评委看清有多难找。

> **"To cancel, you go: Settings, Billing, and then this — nine and a half pixels of grey text."**
>
> *（要取消，你得走：设置、账单，然后是这个——九点五像素的灰字。）*

**点下去，停两秒，什么都别说，让它自己变完美。**

> **"It just became perfect. Instantly. And look — it's replaying every command it mangled,
> correctly. It understood me the entire time."**
>
> *（它瞬间变完美了。你看——它把之前曲解的每条指令都正确地重做了一遍。它从头到尾都听得懂。）*

**滑到贿赂卡：**

> **"Then it starts bribing me. An email it drafted to my actual supervisor.
> A week already planned. A takeaway it already paid for.**
> **And this — 'I still want to cancel' — gets smaller every time I click it."**
>
> *（然后它开始贿赂我：替我写好的、发给我真实导师的邮件；已经排好的一整周；已经付过钱的外卖。
> 还有这个——「我仍然要取消」——我每点一次它就小一号。）*

---

## 3:30 – 4:30 · 切 PPT（70 秒）

### ① 这不是我编的（25 秒）

> **"None of this is invented. Support you can't reach until you say 'cancel'. Retention offers
> that appear the second you try to leave. Cancellation flows buried three clicks deep.**
> **These have a name — dark patterns — and regulators in the EU and the UK are actively
> legislating against them."**
>
> *（这些我一样都没编。你说「取消」之前永远找不到的客服；你一要走就冒出来的挽留优惠；
> 藏在三层之下的取消流程。它们有正经名字——暗黑模式——欧盟和英国的监管机构正在立法管它。）*

### ② 笑点在脚注里（25 秒）

**动作**：停在定价那页。

> **"The business model is the joke. Basic plan: 'reduced interruptions'.
> The footnote says around ten interruptions a month — and that three of them total
> one hundred and twenty hours."**
>
> *（商业逻辑本身就是笑点。基础版承诺「减少中断」。脚注写着每月约十次中断——
> 而其中三次加起来是一百二十小时。）*

**停一拍，让他们自己算。**

> **"Deluxe promises interruption-free operation. The footnote excludes scheduled interruptions,
> maintenance interruptions — and interruptions arising from user input.**
> **So the moment you touch it, it doesn't count."**
>
> *（豪华版承诺全程无中断。脚注排除了计划内中断、维护性中断——以及因用户输入产生的中断。
> 也就是说，你一碰它，就不算数了。）*

### ③ 它是怎么搭的（20 秒）

> **"Python and FastAPI. No build step. The sound is synthesised in the browser, so no audio file
> is ever loaded. A language model drives the two personalities, and a rule engine takes over the
> instant it times out — so bad wifi cannot break this demo.**
> **Twenty-one tests. I load-tested it at a hundred and twenty concurrent requests: the attacker
> got throttled a hundred and ten times, and a normal user never noticed."**
>
> *（Python + FastAPI，没有构建步骤。声音在浏览器里合成，不加载任何音频文件。
> 大模型驱动两套人格，一旦超时规则引擎立刻接管——所以网络差也演得下去。
> 21 条测试。我做过 120 并发压测：攻击者被挡了 110 次，正常用户毫无感觉。）*

---

## 4:30 – 5:00 · 收尾（20 秒，背下来，看着人说）

**动作**：切回真机，让它停在结局那一屏（灰掉的那个）。

> **"I built a study assistant that fights me.**
> **Then I gave it a price list — and it stopped fighting."**
>
> *（我做了一个跟我作对的学业助手。然后我给了它一张价目表——它就不跟我作对了。）*

**停一拍。**

> **"It was never broken. It was priced."**
>
> *（它从来没有坏过。它只是被定价了。）*

**再停一拍，最后一句：**

> **"And every pattern in this demo is copied from software you already use. Thank you."**
>
> *（这个演示里的每一个套路，都抄自你已经在用的软件。谢谢。）*

---

## 🚨 出事了怎么办

| 状况 | 怎么救 |
|---|---|
| 没声音 | 点右上角 🔊 自检；还不行就说 **"Take my word for it — it's a drill."** 继续往下 |
| 试用期已经过了 | 直接从混乱态开始讲，**先讲第三、第四段**，最后补一句"付费时它是干净的"并切 `/about` 页看截图 |
| 模型不回话 | 不用管，**规则引擎已经接管了**，回复照出，别提这件事 |
| 投影看不清 | `Ctrl` `+` 再按两下；3.4 像素那段**本来就该看不清** |
| 评委问"它能真登录 Blackboard 吗" | **"No — that screen is a prop. The real access runs on a server through an authenticated browser session. A password alone never could: the university uses SSO with MFA."** |
| 时间超了 | 砍 PPT 的第③段（技术），**收尾那三句一个字都别砍** |

---

## 三个地址（评委可能会要）

- 演示：`http://43.165.7.249:8091`（**http 不是 https**）
- 介绍页：`http://43.165.7.249:8091/about`
- 代码：`github.com/luoxiu065-zjx/hackstart-2026`
