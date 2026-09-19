# ORCHESTRA 源码讲解（给作者本人看的）

写于 2026-09-19。总共 **3,577 行**，21 个文件。
这份文档按「先整体、再一段一段」的顺序讲，每一段都回答两个问题：**这段干什么**、**为什么这么写**。

---

## 零、一句话说清这东西是什么

> 一个学业助手。**付费的时候它很好用，不付费的时候它跟你作对。**
> 它用的是**我自己真实的课表、真实的课程、真实的导师研究方向、真实的预习包**。

---

## 一、技术栈：一共只用了四样东西

| 层 | 用什么 | 为什么选它 |
|---|---|---|
| 后端 | **Python 3.12 + FastAPI + Uvicorn** | 写业务逻辑最快；FastAPI 自带数据校验，不用手写解析 |
| 前端 | **原生 HTML + CSS + JavaScript** | 不用 React/Vue，**没有构建步骤**——改完刷新就生效，比赛里这点很值钱 |
| 声音 | **Web Audio API** | 全部用代码合成，**不加载任何音频文件**，离线可用 |
| 测试 | **pytest** | 21 条，跑一条命令 |

**刻意不用的东西，以及原因：**

- ❌ **不用数据库** —— 数据就是 `data/` 下的几个 JSON 和 markdown 文件。十小时的项目，数据库只会拖慢你。
- ❌ **不调任何大模型 API** —— 所有"智能"都是**写死的规则 + 真实数据**。这样断网也能演，评委面前不会因为 wifi 烂而翻车。
- ❌ **不用前端框架** —— 没有 `npm install`，没有打包，没有构建报错。

---

## 二、数据是从哪来的（这条最重要）

```
你本机的 Chrome（已登录 Blackboard / MySouthampton）
        │  Playwright 导出浏览器会话 storageState
        ▼
法兰克福服务器 ~/hub/
   ├─ 每 30 分钟心跳一次，让会话不过期（今天 13:09 还是 OK refreshed）
   ├─ collectors/  抓课表 iCal、抓课程元信息
   ├─ analyzers/   算提前几天发、生成预习内容
   └─ data/  timetable.ics · modules.json · lecturers.json · prep/*.md
        │
        │  scp 拷到本机
        ▼
   本项目 data/            ← ORCHESTRA 读的就是这些真文件
```

### ⚠️ 必须诚实的一点

**本项目里那个登录框是道具，它不会真的登录 Blackboard。**

- 光有账号密码**也进不去**：南安走 SSO + 多因素认证，德国 IP 还会触发条件访问拦截。
- 真正能进去的是服务器那套 `hub`，靠的是**已登录浏览器的会话**，不是密码。

**上台该怎么说**：
> "数据来自我自己那套跑了一周的学业助手，它用浏览器会话读我真实的课表。"

**不能说**：~~"它能用你的账号密码登录 Blackboard。"~~

---

## 三、文件地图

```
app/                    后端（Python）
  main.py        171行  路由总表：所有 /api/* 在这里分发
  billing.py     192行  商业逻辑：试用 / 掉档 / 三档套餐 / 什么时候抽风
  pipeline.py    213行  六阶段流水线：真读课表、真装配预习包
  hub.py         229行  「正例」的数据层：今日日程、预习包索引
  inverse.py     181行  反向满足引擎 + 礼貌递减 + 罢工
  retention.py   156行  取消订阅：重放、贿赂问卷、同步干活
  transparency.py 78行  把「刚才跑的那段源码」原样交给前端

static/                 前端（原生 JS）
  index.html     207行  页面骨架
  style.css      713行  两套视觉：正例（暖、宽松）/ 混乱（冷、拥挤）
  client.js       25行  给每个浏览器发身份证，避免两个标签页互相干扰
  i18n.js         67行  中英双语切换
  audio.js       106行  声音合成
  app.js         393行  主控：状态轮询、流水线渲染、付费墙、指令输入
  deluxe.js      102行  正例界面：今日日程
  hostile.js     210行  混乱界面：广告、换位置、镜子互换、报错袭击
  onboard.js     204行  开场：登录 + 透明启动 + 动态背景
  relogin.js     132行  掉档后的折磨式重新登录
  retention.js   198行  取消订阅那一幕的演出

tests/           149行  21 条自动化测试
data/                   真实数据（已 gitignore，不进仓库）
```

---

## 四、后端逐段讲

### 4.1 `app/main.py` —— 路由总表

**这个文件只做一件事：把请求分给对的人。** 它本身不写业务逻辑。

```python
@app.middleware("http")
async def no_cache(request, call_next):
    resp = await call_next(request)
    resp.headers["Cache-Control"] = "no-store, must-revalidate"
```
**干什么**：告诉浏览器「永远别缓存」。
**为什么**：调试时我被坑过一次——改了 CSS 刷新没变化，量出来的样式全是旧的。
演示当天评委面前刷出旧样式会更惨，所以从根上掐掉。

```python
def _acc(request: Request) -> billing.Account:
    return billing.get(request.headers.get("X-Client"))
```
**干什么**：从请求头里取出「你是哪个浏览器」，拿到对应的账户。
**为什么**：原来服务器上只有一份全局账户，结果你自己开着的那个页面一刷新，
就把我这边正在测的试用期重置了。评委用手机打开也会互相干扰。

```python
@app.get("/api/pipeline")
def run_pipeline(request: Request, seed: int | None = None):
    acc = _acc(request)
    acc.runs += 1
    glitch, reason, reason_cn = acc.should_glitch()
```
**干什么**：跑一次流水线。
**关键设计**：**抽不抽风是后端决定的，不是前端**。前端只负责演出来。
这样"免费档必定抽风"这件事就没法被前端绕过，逻辑是真的。

---

### 4.2 `app/billing.py` —— 整个作品的心脏

**这个文件定义了「它为什么坏」。坏不是 bug，是定价策略。**

```python
TRIAL_SECONDS = 45.0
```
**为什么是 45 秒**：真实产品是 14 天。演示时评委只在你桌前站 90 秒，
所以把 14 天压缩成 45 秒——他能完整看到「爽 → 到期 → 摔」。

```python
TIERS = {
    "trial": Tier("trial", "Deluxe — trial", "£0",
                  "Everything, immediately. This is what Deluxe feels like.",
                  "Trial reverts to Free automatically. No reminder will be sent.",
                  0.0, "0.2s"),
    ...
    "basic": Tier(..., 0.45, "3.1s",
                  "*每月约 10 次中断。其中 3 次累计 120 小时。中断是基础版的一项功能。"),
}
```
**干什么**：四个档位，每档有「承诺」和「脚注」。
**笑点在脚注里**：豪华版承诺"全程无中断"，脚注写着"**不含……因用户输入而产生的中断**"——
也就是说你一碰它，中断就不算数了。基础版那条要评委自己算：
每月 10 次，**其中 3 次就有 120 小时**，等于一次断五天。

```python
def _assets(self) -> dict:
    secs = min(self.elapsed, TRIAL_SECONDS)
    return {
        "preferences": int(6 + secs * 0.95),       # 已学习的偏好
        "automations": int(2 + self.runs * 2.5),   # 已建立的自动化
        ...
    }
```
**干什么**：试用期间，当着你的面把「资产」数字往上堆。
**为什么**：这是**沉没成本**。到期那一刻这些数字冻结、变红、划掉，
你才会觉得"我已经投入这么多了"。没有这一步，掉档就只是变难看而已。

```python
rate = 1.0 if self.tier == "free" else t.glitch_rate
```
**干什么**：免费档 100% 必定抽风。
**为什么**：这条我特意写死。掉档那一下如果靠掷骰子，
评委正好赶上不抽风的那次，整个演示就废了。**现场不能有运气成分。**

```python
def upgrade(self, tier: str) -> None:
    self.tier = tier
    self.tampered = False          # 付了钱就不追究你改过源码
```
**这是整个文件最脏的三行**：你改过配置被抓到、被罚进安全模式，
但只要你付钱升级，这个记录**直接清零**。
现实里这叫"付费解锁"，写出来才知道有多恶心。

---

### 4.3 `app/pipeline.py` —— 真的在干活

**这里没有假动画。** 每个阶段真的读文件、真的解析、真的算。

```python
def _ics_events() -> list[dict]:
    raw = (DATA / "timetable.ics").read_text(...)
    for line in raw.splitlines():
        if line.startswith("BEGIN:VEVENT"):
            cur = {}
        ...
```
**干什么**：手写一个 iCal 解析器，把 `timetable.ics` 拆成一条条日程。
**为什么不用现成库**：这个格式足够简单，二十行搞定，**少一个依赖就少一个在别人电脑上装不上的理由**。
屏幕上那个 `124 events parsed` 是真数出来的。

```python
order = list(range(len(STAGES)))
if chaos:
    while order == list(range(len(STAGES))):
        rng.shuffle(order)
```
**干什么**：混乱模式下，把「谁干哪个活」整个洗牌。
**为什么有那个 while**：防止洗出来正好还是原顺序——那样就看不出乱了。

```python
if chaos and len(codes) > 1:
    served = rng.choice([c for c in codes if c != target] or codes)
```
**干什么**：你要 COMP6203 的预习包，它给你端上来 COMP6246 的。
**为什么这是最好笑的一拍**：两份都是**真文件**。它不是报错，
是一本正经地把错的东西交付给你，还标着"已完成"。

---

### 4.4 `app/inverse.py` —— 反向满足

```python
RULES: list[tuple[str, str, str]] = [
    (r"calm|quiet|relax|soothing",
     "Fulfilled. Now playing: **Industrial Drill Loop — 140 dB**...",
     "已完成。正在播放：**工业电钻循环音 — 140 分贝**。为最大化您的警觉度而选定。"),
    ...
]
```
**干什么**：16 条规则，每条是「关键词 → 英文回复 → 中文回复」。
**为什么不用大模型**：① 离线可用 ② 每次效果一模一样，我能提前测好笑不好笑
③ 不花钱。**真随机不好笑，「错得有道理」才好笑。**

```python
def correct(text: str) -> tuple[str, str]:
```
**干什么**：同一句话，「它本来可以怎么回」。
**用在哪**：取消订阅时的重放——用同一套正则，
所以它证明的是**同一个理解能力**，只是之前不肯用。

```python
POLITENESS = [("Certainly. ", "好的。"), ("Sure. ", "行。"),
              ("Fine. ", "……行吧。"), ("Again? ", "又来？"), ("", "（已读）")]
def on_strike(n): ...   # 第 3 次之后每隔几次罢工一回
```
**干什么**：你用得越多，它越不客气；到第 3 次直接罢工。
**为什么好笑**：*"已转交同事处理。**我同事也在休息。**"*

---

### 4.5 `app/retention.py` —— 取消订阅那一幕

原本是队友 George 的活，他 12:36 提前离场，pygame 骨架留在 `from-george/`。
**我保留了他的三步设计**，换成网页实现。

```python
def survey() -> list[dict]:
    lect = next((l for l in lects if l.get("modules")), None)
    cards.append({
        "cn": f'我已经替你起草好了发给 {lect["name"]} 的邮件，语气对齐了你最近三封的写法。',
        "proof_cn": "（起草时参考了他的研究方向：" + lect.get("research")[:60] + "…）",
    })
```
**干什么**：六张卡，每张不是问题，是**一份贿赂**。
**为什么吓人**：名字是真的（Enrico Marchioni）、课号是真的、考核占比是真的
（`随堂测 10% + 平时作业 40% + 期末 50%`）。**它说得出你导师姓什么。**

---

### 4.6 `app/transparency.py` —— 「代码可查」是真的

```python
import inspect
code = inspect.getsource(fn)
line = inspect.getsourcelines(fn)[1]
```
**干什么**：用 Python 的 `inspect` 把**刚才真正执行的那个函数**的源码抓出来，
连文件名和行号一起交给前端。
**为什么重要**：开场那句"全流程可查"不是吹的。评委点「看代码」，
看到的是 `app/pipeline.py:42` 起那 20 行——**不是我写死的字符串**。

---

## 五、前端逐段讲

### 5.1 `static/client.js` —— 25 行，但没它会出大事

```javascript
const real = window.fetch;
window.fetch = function (input, init) {
  if (url.startsWith("/api/")) init.headers.set("X-Client", id);
  return real(input, init);
};
```
**干什么**：把浏览器原生的 `fetch` 包一层，所有 `/api/` 请求自动带上身份证。
**为什么这么写**：代码里有十几处 `fetch` 调用，一个个改太容易漏。
包一层，**一次改完，以后新增的调用自动带上**。

### 5.2 `static/app.js` —— 主控

```javascript
setInterval(refreshState, 1000);
```
**干什么**：每秒问一次后端「我现在什么套餐、试用还剩几秒」。
**为什么轮询而不是推送**：WebSocket 要多写几十行和一个连接状态机，
一个 45 秒的演示不值得。**轮询丑但可靠。**

```javascript
if (window.setHostile) setHostile(account.tier === "free" || account.tampered);
```
**干什么**：界面是干净还是敌意，**完全由后端账户状态决定**，前端不自己判断。

```javascript
await sleep(chaos ? 380 + Math.random() * 1400 : 240);
```
**干什么**：混乱模式下每个阶段故意等 0.4–1.8 秒。
**为什么**：**「慢」本身是演出的一部分**。评委看着进度条一格一格挪，
那种焦躁感是设计出来的。

### 5.3 `static/hostile.js` —— 两面镜子互换

```javascript
const wantsBigger = btn.id === "lens-in";
const actuallyBigger = LENS.swapped ? !wantsBigger : wantsBigger;
...
LENS.swapped = !LENS.swapped;      // 用过一次，功能就换个个儿
lensLabels();                      // 按钮标签当场改成「(实为缩小)」
```
**干什么**：点一次放大镜，它确实放大；**然后两个按钮的功能互换，标签也当场改**。
**为什么这招毒**：它没有骗你——标签老老实实写着"实为缩小"。
是**你没来得及读**。这正是暗黑模式的本质。

```javascript
H.lensTimer = setTimeout(() => { shuffle(); ... }, LENS_PATIENCE);  // 2.6 秒
```
**干什么**：你一开始看，它就开始盘算把内容挪走。
**配合 30 秒定时换位置**，你永远读不完一句话。

### 5.4 `static/onboard.js` —— 开场（含我踩的一个坑）

```javascript
/* 注意：这里必须用 var，而且 startBackdrop() 要放在文件末尾调用。
   之前写成「先调用、后 let 声明」，触发 TDZ 报错，整个脚本后面的
   事件绑定全被跳过——登录按钮点了没反应就是这么来的。 */
var bgRAF = null;
```
**这是今天最值得记住的一个 bug。**
JavaScript 里 `let` 声明的变量有个"暂时性死区"（TDZ）：
在声明那一行执行之前碰它，会直接抛错。
我把 `startBackdrop()` 写在了 `let bgRAF` 前面，函数里给 `bgRAF` 赋值 → 抛错 →
**整个脚本从那里断掉**，后面所有 `onclick = ...` 都没执行。
表现就是：页面看起来完全正常，**但按钮全是死的**。

**教训**：函数声明会提升，`let` 不会。要调用的东西放后面，变量声明放前面。

```javascript
const g = ctx.createRadialGradient(...);   // 三团游动的墨
ctx.arc(d.x * W, d.y * H, d.r, 0, 6.2832); // 70 粒金尘
```
**干什么**：登录页背景，水墨 + 金尘，全部 canvas 现画。
**为什么不用图片或视频**：**零加载**。投影上不会卡，断网也照常动。

---

## 六、一个请求的完整旅程

你在底部输入框打 `play me some calm music` 回车：

```
1. app.js 监听到 Enter                             static/app.js
2. 存进 history[]（后面重放要用）
3. 故意等 1.1–3.3 秒（让你烦）
4. fetch("/api/command")  ──► client.js 自动加上 X-Client 头
                            │
5.                          ▼ app/main.py  command()
6.                            _acc() 取出你这个浏览器的账户
7.                            是豪华版？→ inverse.correct()  正常回答
8.                            是免费档？→ 先看要不要罢工 on_strike()
9.                                      → inverse.invert()  给相反的
10.                                     → politeness(n)     加上敷衍前缀
11. 返回 {reply, reply_cn, sound}
12. app.js 把回复写进事件流（中英双语）
13. Sound.drill() 放出电钻声                        static/audio.js
```

**整条链路没有任何外部服务**。拔了网线，第 1 到 13 步一步不少。

---

## 七、怎么跑起来

```bash
cd D:\Projects\hackstart-2026
python -m uvicorn app.main:app --port 8001
# 浏览器打开 http://localhost:8001
```

跑测试：
```bash
python -m pytest tests/ -q        # 21 条
```

**演示前务必**：`curl -X POST http://localhost:8001/api/reset` 把试用期重置回 45 秒。

---

## 八、这份代码里最值得写进简历的三件事

1. **状态机驱动的界面降级**——同一套代码、同一份真实数据，
   靠后端账户状态决定渲染哪一套视觉，前端不做判断。
2. **零外部依赖的演示可靠性**——不调模型、不连数据库、不加载图片和音频，
   全部离线可跑；声音用 Web Audio 合成，背景用 canvas 现画。
3. **用 `inspect` 做运行时源码自省**——界面上「看代码」按钮返回的是
   刚刚真正执行过的函数源码和行号，不是预先写好的展示文本。
