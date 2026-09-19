# Findings

技术选型、踩到的坑、查到的事实都记在这里。四个人共享，别只记在自己脑子里。

---

## 环境事实（2026-09-19 凌晨核实，可直接用）

| 项 | 版本 / 位置 |
|---|---|
| Python | 3.12.10 — `D:\apps\Python312\python.exe` |
| Node.js | v24.21.0 — `C:\Program Files\nodejs\` |
| npm | 11.19.0 |
| Git | 2.55.0 |
| gh CLI | 2.101.0（已授权 luoxiu065-zjx） |
| VS Code | 1.138.0 |

**Python 和 Node 都在，FastAPI + React 直接能跑，不用现装运行时。**

## 仓库

- `https://github.com/luoxiu065-zjx/hackstart-2026`（private）
- 加队友：`gh repo add-collaborator luoxiu065-zjx/hackstart-2026 <用户名>`

## 已知的坑

- **winget 装东西会弹 UAC，没人点会静默取消，但它照样报 "Successfully installed"。**
  装完一定要 `winget list --id <包名>` 复查，别信它的成功提示。
- **`repo` scope 的 GitHub token 覆盖账号下所有仓库**，没有"只给一个仓库"的选项。
  要精确到单仓库得用 Fine-grained token。赛后再收紧。

## 技术选型

（定了什么写在这里，附一句为什么）

- 待定

## 调试记录

（谁踩了什么坑、怎么解决的，写一行省队友半小时）

- 待定

## 选题背景
- 参考先例：User Inyerface（著名的反人类表单网站）、r/badUIbattles、The Worst Volume Control UI
- 加分点设计：结尾点题「这些设计都真实存在于线上产品」，把恶搞升华成暗黑模式科普
- 技术分薄弱是这类题的通病 → 计划补一个排行榜后端（用时/点击数），避免被评委说「只有前端」

## 官方题面（2026-09-19 11:05 从 Discord 抓到的 Intro PDF，24 页）
PDF 存档：桌面\claude图片文档专用\文档\HackStart26-Intro.pdf

**主题：Stubborn Software —— 官方一句话注解：`fight the user`（跟用户对着干）。**

**评分四项（同等权重，出现在 p14 Judging Formula）：**
Functionality（能不能跑） / Aesthetics（好不好看） / Uniqueness（够不够独特） / Salesmanship（会不会卖）

**真实时间线（p11，跟我们原以为的 10 小时差很多）：**
- 10:45-12:00 编码 → 12:00-12:15 纸飞机 → 13:00 午饭
- 14:00-17:00 编码 → 14:00-15:00 geoguessr → 16:30-17:00 WikiRacer
- **17:00 提交截止 + 评审（science fair 形式，评委走过来看）**
- 18:00-18:45 演讲 → 19:00-20:00 颁奖

**官方给的示例点子（p22）——这四个必定撞车，要避开：**
1. 搜索结果按服务器物理距离决定等待时间
2. 一次只显示一个字符的密码管理器
3. 必须滚动"输入动能"才解锁的新闻
4. 停止打字 5 秒就删光全文的文本编辑器

**评委（p15）：** Andersen Ang（一年级 CS 讲师）、Alex Dunlop（Future Worlds 创业孵化器）、
Krish Mathur（往届冠军）、Arun Muthu（JetBrains 大使）+2 名神秘评委。
→ 有孵化器的人在场，Salesmanship 这项含金量高，pitch 必须练。

**奖项：** 冠军 USB-C 便携显示器 / 亚军 £50 礼券 / **Best Idea 蓝牙音箱（单独设奖，我们主攻这个 + 冲冠军）**

**规则：** 队伍上限 4 人（硬性）；允许用 AI。
