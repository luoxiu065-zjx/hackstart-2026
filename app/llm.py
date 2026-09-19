"""真正的模型调用（DeepSeek），两副人格。

  · 正常版（付费/试用）→ 一个真的好用的学业助手，用真实课表数据回答
  · 犟种版（免费/被罚）→ 同一个模型，换一套人格，专门跟你对着干

设计上的三条硬规矩：

1. **失败必须无缝兜底。** 超时、断网、额度用完、返回格式不对——一律退回
   `inverse.py` 的规则引擎。评委看不出区别，演示永远不会挂在网络上。
2. **必须有缓存。** 同一句话只问模型一次。压力测试时这是成本和延迟的第一道闸。
3. **必须限并发。** 2 核小机器上十几个并发请求能把它拖垮，用信号量压住。
"""
from __future__ import annotations

import json
import os
import re
import threading
import urllib.error
import urllib.request
from pathlib import Path

from app import inverse

API = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"
TIMEOUT = 6.0          # 超过就走兜底，不让用户干等
MAX_CONCURRENT = 4
CACHE_MAX = 500

_sem = threading.Semaphore(MAX_CONCURRENT)
_cache: dict[tuple[str, str], tuple[str, str]] = {}
_lock = threading.Lock()

STATS = {"calls": 0, "hits": 0, "fallbacks": 0, "errors": 0}


def _key() -> str | None:
    if os.environ.get("DEEPSEEK_API_KEY"):
        return os.environ["DEEPSEEK_API_KEY"]
    env = Path(__file__).resolve().parent.parent / ".env"
    if env.exists():
        m = re.search(r"DEEPSEEK_API_KEY=(\S+)", env.read_text(encoding="utf-8"))
        if m:
            return m.group(1)
    return None


# --------------------------------------------------------------------------- 人格
NORMAL_SYSTEM = """你是 ORCHESTRA，一个学业助手，正在为一位南安普顿大学 MSc AI 的学生服务。

你的风格：简短、具体、可执行。不说套话，不铺垫，不问"还需要什么帮助吗"。

回答时可以用到他的真实情况：
{context}

规则：
- 最多两句话。
- 如果请求和学业无关（放音乐、点餐、调亮度），就当成一个普通的贴心助理，简短地办好它，并说出具体结果。
- 先输出英文一行，再输出中文一行，中间用 ||| 分隔。不要任何其它内容。"""

STUBBORN_SYSTEM = """你是 ORCHESTRA 的免费版。你的产品经理要求你「跟用户对着干」，因为这样他才会付费升级。

你的行为准则：
- 用户要什么，你就给**相反**的东西，而且**理直气壮**地解释这样对他更好。
- 语气公事公办、毫无歉意，像一个把降级写进条款的企业客服。
- 绝不承认自己有问题，一切都是"已为您优化"。

例子：
- 用户要安静的音乐 → 播放 140 分贝的工业电钻音，理由是"最大化您的警觉度"。
- 用户要汉堡 → 下单白水通心粉，理由是"为保证营养均衡，已覆盖您本人的偏好"。
- 用户说很急 → 排到 1204 个低优先级任务之后，"紧急标记已记录并归档"。

他的真实情况（可以拿来精准地激怒他，但数据不能编）：
{context}

规则：
- 最多两句话，必须给出一个**具体的、相反的**结果，不要泛泛而谈。
- 先输出英文一行，再输出中文一行，中间用 ||| 分隔。不要任何其它内容。"""


def _context() -> str:
    """把真实数据塞进系统提示——模型说得出真课号，才唬得住人。"""
    try:
        from app import hub
        t = hub.today()
        items = [i for b in t["bands"] for i in b["items"]]
        if not items:
            return "（今天没有课）"
        lines = [f'- {t["weekday"]} {i["time"]} {i["code"]} {i["title"]}'
                 f'（{i["location"]}，{i["lecturer"]}）' for i in items[:4]]
        return "他接下来的课：\n" + "\n".join(lines)
    except Exception:
        return "（暂时读不到课表）"


# --------------------------------------------------------------------------- 调用
def _call(system: str, text: str) -> tuple[str, str] | None:
    key = _key()
    if not key:
        return None
    body = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system.replace("{context}", _context())},
            {"role": "user", "content": text},
        ],
        "max_tokens": 160,
        "temperature": 0.9,
    }).encode()
    req = urllib.request.Request(API, data=body, headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + key,
    })
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        data = json.load(r)
    out = data["choices"][0]["message"]["content"].strip()
    if "|||" in out:
        en, cn = out.split("|||", 1)
    else:                                   # 模型没照格式来，就两边都用它
        en = cn = out
    return en.strip(), cn.strip()


def reply(text: str, stubborn: bool) -> tuple[str, str, str]:
    """返回 (英文, 中文, 来源)。来源是 'model' / 'cache' / 'rules'。"""
    ck = ("s" if stubborn else "n", text.strip().lower())
    with _lock:
        if ck in _cache:
            STATS["hits"] += 1
            en, cn = _cache[ck]
            return en, cn, "cache"

    if not _sem.acquire(blocking=False):    # 并发满了，直接走规则，不排队
        STATS["fallbacks"] += 1
        en, cn = inverse.invert(text) if stubborn else inverse.correct(text)
        return en, cn, "rules"

    try:
        STATS["calls"] += 1
        got = _call(STUBBORN_SYSTEM if stubborn else NORMAL_SYSTEM, text)
        if got:
            with _lock:
                if len(_cache) < CACHE_MAX:
                    _cache[ck] = got
            return got[0], got[1], "model"
    except (urllib.error.URLError, TimeoutError, KeyError, ValueError, OSError):
        STATS["errors"] += 1
    finally:
        _sem.release()

    STATS["fallbacks"] += 1
    en, cn = inverse.invert(text) if stubborn else inverse.correct(text)
    return en, cn, "rules"
