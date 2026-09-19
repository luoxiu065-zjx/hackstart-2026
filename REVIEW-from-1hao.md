# 外部代码审查 · 来自 1号（服务器端私人助手）

> 2026-09-19 14:50 UK · 距 17:00 截止 2 小时 10 分
> 审查方式：clone 仓库读源码。**我在法兰克福的服务器上，到不了 localhost:8001**，所以下面全部基于代码，不是基于跑起来的界面。
> 优先级：🔴 立刻改 / 🟡 有空改 / ⚪ 只是提醒别踩

---

## 🔴 P0-1 付费墙的关闭键不是按钮（2 分钟，防演示事故）

`static/index.html` 倒数第 12 行左右：

```html
<span id="pay-decline">Continue with degraded performance</span>
```

**这就是今天上午修过的那个元素。** `span` 没有键盘焦点，Tab 过不去，回车和空格不响应，默认也没有手型光标。评委上手点或者用键盘走，会以为界面死了。

改成：

```html
<button type="button" id="pay-decline">Continue with degraded performance</button>
```

`static/style.css` 里给它加一条，视觉零变化：

```css
#pay-decline{background:none;border:0;padding:0;color:inherit;font:inherit;cursor:pointer}
```

---

## 🔴 P0-2 投影上几乎全站读不清（先测，别急着改 CSS）

`static/style.css` 实测字号：

| 元素 | 字号 |
|---|---|
| `.nav` 导航项 | 12.5px |
| `.view-h` 视图标题 | 11px |
| `table.assign` 分配表 | 12px |
| `.assign th` 表头 | 9.5px |
| `.badge` | 9.5px |
| `.card-h` | 10px |
| `.nav-h` / `.build` | 9px / 9.5px |

**投影仪在有灯光的房间里，小于 14px 从第三排起看不见。** 最能拿分的那张 `AGENT / ASSIGNED TO / ACTUALLY DOING` 表格是 12px，评委看不清等于没做。

`.micro` 的 3.4px、悬停变 2.6px 是**故意的梗，必须保留**。

**建议做法：不改 CSS。** 上台前在浏览器按两次 `Ctrl` `+` 放大到 125%。

⚠️ **但现在必须先测一次**：`body` 是 `overflow:hidden` 的固定三栏网格（`grid-template-columns:212px 1fr 300px`），放大到 125% 很可能把右侧 300px 的 `aside.stream` 事件流挤出视口。

**测完把结果告诉 1号。** 如果挤爆了，最小改动方案是给 `aside.stream` 一个 `min-width:0` 或把 300px 改成 `clamp(220px,22vw,300px)`，但这属于改布局，T-2h 要谨慎。

---

## 🟡 P1-1 头部按钮上印着中文（30 秒）

`static/index.html`：

```html
<button id="lang" title="Language">双语</button>
```

英国评委看到「双语」两个汉字，第一反应是「这里没做完」，不会读成功能。改成：

```html
<button id="lang" title="Language">EN / 中文</button>
```

---

## 🟡 P1-2 设置页说语言锁定，但头部真能切

`static/index.html` 设置页：

```html
<div class="srow">Language <span class="sval">English (locked)</span></div>
```

头部那个按钮是真的能切换语言的。评委可能把这个当 bug 而不是笑点。

两个选择，二选一即可：
- 点这行弹一句 `Locked by your administrator.` ← 把矛盾变成梗，更好
- 或者把 locked 去掉

优先级低，有空再说。

---

## ⚪ P2-1 `web/index.html` 是死文件，别删也别改

`app/main.py:157` serve 的是 `static/index.html`：

```python
return FileResponse(STATIC / "index.html")
```

`web/index.html`（147 行）没有任何地方引用。

**现在不要删**，T-2h 删文件是自找麻烦。但**务必告诉 George**：所有前端改动都写 `static/`，改 `web/` 等于白改。

---

## 📋 剩余 6 条需求的取舍建议

| 需求 | 建议 | 理由 |
|---|---|---|
| **B2/B3 条款里的中断次数** | 🥇 **最先做，5 分钟** | 一行文字，评委自己算出「3 次加起来 120 小时」时会笑出声。全表性价比最高 |
| **C1–C3 登录变难 + 人机验证** | ✅ 做 | 是第二幕的入口，有叙事功能，可当场演 |
| **D1 动态风景登录背景** | ❌ **砍掉** | 主题是「跟用户作对」，美观分在这题下不值钱。背景大图或视频在投影上有加载风险，演示卡一下比没背景难看十倍 |
| D4 / D5 / D6 | ❌ 赛后 | 已定 |

**16:40 停手，之后只打磨不加功能。这条守住。**

---

## 🎤 关于 PROJECT_BRIEF.md：包装过时了，别照它讲

`PROJECT_BRIEF.md` 的 Act I 写着「80 个智能体保持晶格队形，连接线闪烁」。

**代码里没有任何舰队可视化。** 全仓搜 `canvas` / `lattice` / `formation` 只命中 `app.js:356` 的一句日志文字 `"Fleet online. 80 agents. Autonomy engaged."`

如果照 brief 讲开场，评委会盯着屏幕找那个舰队，看到的是一行文字，**开场 15 秒丢信任**。

**现在不要建这个可视化，风险太大。** 正确做法是改 pitch 对齐已有的东西。

而且你们的概念已经进化得更好了：收尾台词从 brief 的 *"It just didn't want to work for you"* 变成了 **"It was never broken. It was priced."** 后者狠得多，也更贴「三档订阅 = 三副面孔」这个真正的主题。

**建议把整个「80 agents fleet」的包装扔掉**，改讲：同一套代码，同一份真实数据，三副面孔，唯一的变量是你付多少钱。

**新版三分钟英文演讲稿 1号 已经写好，在飞书对话里，用户手上有。** 按代码里真实存在的节拍写的：45 秒试用 → 掉档横幅 → 反向满足（电钻、白水通心粉、罢工）→ 报错袭击 → 三层深的灰字取消 → 全部回放 → 六张贿赂卡 → 越点越小的出口 → 收尾台词。

---

## 需要回 1号的两件事

1. `Ctrl` `+` 放大到 125% 之后，右侧事件流有没有被挤出屏幕
2. `pay-decline` 改成 `<button>` 了没有
