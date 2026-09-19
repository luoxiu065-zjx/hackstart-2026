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
