# George 留下的代码（2026-09-19 12:36 离场前）

他因家人临时来访提前离开，走之前把这两个文件发在 Discord 私信里。

- `cancel_subscription.py` —— pygame 窗口 + `Question` / `Q_TextInput` 抽象，
  注释写明了他的三步设想：`complete true actions` → `cancellation survey` → `shrinking exit`
- `moduley.py` —— 一个可用的 pygame 文本输入控件（退格、删除、回车提交、随文字变宽）

**为什么没有直接合进主程序**：我们的作品是 FastAPI + 网页，他的是 pygame 桌面窗口，
两套渲染栈不通。离截止只剩两小时，改栈会把美观分和进度一起赔进去。

**保留的是他的设计意图**：问卷用「一个问题 = 一个对象」的方式组织、
每题一个输入、退出口越点越小——这三点原样落进了网页版的 retention 流程。
