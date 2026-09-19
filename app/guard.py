"""站点守卫：限时开放 + 抗压。

这是给「把网址发出去」准备的。一旦公网可达，就会遇到三件事：
  1. 有人一直刷（压力测试 / 好奇 / 脚本）
  2. 模型调用被刷爆，额度烧光
  3. 演示结束后链接还活着，不受控

所以：
  · **限时**：站点只在 OPEN_MINUTES 分钟内可访问，到点整站返回 410，链接自然作废。
  · **限速**：每个 IP 每分钟最多 RATE_PER_MIN 次；超了返回 429，但**不影响已在场的人**。
  · **限模型**：全站模型调用总数封顶 LLM_BUDGET，超了自动退回规则引擎——
    页面照常能玩，只是不再花钱。
"""
from __future__ import annotations

import os
import time
from collections import defaultdict, deque
from threading import Lock

# 站点存活时间。默认一小时；比赛当天用环境变量开到覆盖整场的时长。
#   ORCHESTRA_OPEN_MINUTES=480  ./run
OPEN_MINUTES = float(os.environ.get("ORCHESTRA_OPEN_MINUTES", "60"))

# 限速分两档。压测时发现两个真问题，这里都改掉了：
#   ① 原来按 IP 限速——评委在同一个会场 wifi 下共用出口 IP，会被一起锁死。
#      改成优先按浏览器身份（X-Client）算，同一个 wifi 下互不影响。
#   ② 前端 /api/state 每秒一次心跳，60 次/分钟，原来的 40 上限会把正常用户误伤。
#      所以便宜的读接口单独给高配额，只对花钱的写接口收紧。
CHEAP_PER_MIN = 240        # /api/state 这类只读心跳
COSTLY_PER_MIN = 30        # /api/command、/api/pipeline 这类
BURST = 10                 # 10 秒内的突发上限（只管 costly）
LLM_BUDGET = 400           # 全站模型调用总预算

COSTLY = ("/api/command", "/api/pipeline", "/api/cancel")

_started = time.monotonic()
_hits: dict[str, deque] = defaultdict(deque)
_lock = Lock()
_llm_used = 0

STATS = {"requests": 0, "throttled": 0, "expired": 0}


def seconds_left() -> float:
    return max(0.0, OPEN_MINUTES * 60 - (time.monotonic() - _started))


def expired() -> bool:
    return seconds_left() <= 0


def allow(who: str, path: str) -> tuple[bool, str]:
    """who = 浏览器身份（拿不到就退回 IP）。返回 (是否放行, 原因)。"""
    costly = any(path.startswith(c) for c in COSTLY)
    cap = COSTLY_PER_MIN if costly else CHEAP_PER_MIN
    now = time.time()
    with _lock:
        STATS["requests"] += 1
        q = _hits[who + ("!c" if costly else "!r")]
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= cap:
            STATS["throttled"] += 1
            return False, "rate"
        if costly and sum(1 for t in q if now - t <= 10) >= BURST:
            STATS["throttled"] += 1
            return False, "burst"
        q.append(now)
        if len(_hits) > 2000:                       # 防止 IP 表无限膨胀
            for k in [k for k, v in _hits.items() if not v][:500]:
                _hits.pop(k, None)
    return True, ""


def llm_allowed() -> bool:
    """模型预算还有没有。用完不报错，只是退回规则引擎。"""
    global _llm_used
    with _lock:
        if _llm_used >= LLM_BUDGET:
            return False
        _llm_used += 1
        return True


def snapshot() -> dict:
    return {
        "seconds_left": round(seconds_left()),
        "open_minutes": OPEN_MINUTES,
        "expired": expired(),
        "llm_used": _llm_used,
        "llm_budget": LLM_BUDGET,
        "unique_ips": len(_hits),
        **STATS,
    }
