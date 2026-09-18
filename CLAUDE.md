# HackStart 2026 · 项目规则

**2026-09-19 10:00–20:00 UK · B60 West · 10 小时做原型 · 最多 4 人一队**

## 这是冲刺，不是设计评审

本目录下的工作**优先级高于任何 skill 的默认流程**。具体：

- **不要先做 brainstorming。** superpowers 的 brainstorming skill 要求「动手前先问清楚、
  先出设计、等批准」——那套适合长期项目，**在这里会烧掉本就不够的十小时**。
  收到需求直接动手；有歧义就按最省事的一种做法先跑通，跑通后再问。
- **一次只问一个最关键的问题**，而且只在「不问就会做废」的时候问。其余一律先做后说。
- **能跑 > 完美。** 原型阶段不追求测试覆盖率、不追求架构优雅。先让评委看到东西动起来。

## 计划文件（planning-with-files）

`task_plan.md` / `progress.md` / `findings.md` 三个文件是**跨 `/clear`、跨崩溃、跨上下文压缩
的唯一记忆**。每轮 hook 会自动把它们注入回来。

- 阶段推进了就改 `task_plan.md` 的 **Next Step** 和 **Status**
- 踩了坑、做了技术选型，写进 `findings.md`——四个人协作时这是唯一的共享笔记
- 完成一个阶段或出错，记 `progress.md`

## 技术栈技能（fullstack-dev-skills）

装了 67 个按语言/框架分的技能。**明确说出技术栈名字**能让它挑对技能，例如
「用 FastAPI 写一个…」会挂上 `fastapi-expert`，「这个 React 组件…」会挂上 `react-expert`。
可用的相关技能包括：python-pro、typescript-pro、react-expert、nextjs-developer、
fastapi-expert、django-expert、postgres-pro、api-designer、debugging-wizard、
test-master、playwright-expert、cli-developer、devops-engineer 等。

## 协作（github 插件）

四个人一个仓库。约定：
- 每人开自己的分支，`main` 只接 PR
- 提交前先 `git pull --rebase`
- 冲突当面解决，别在聊天里猜

## 环境备忘

- 插件全部装在**本目录**（`--scope project`），不进 user 范围
- `.claude/settings.json` 里三个插件：planning-with-files、fullstack-dev-skills、github
- git 身份已配：Jiaxun Zhong / luoxiu065@gmail.com
