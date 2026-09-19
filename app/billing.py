"""ORCHESTRA 的商业逻辑。

整个产品的"坏"不是 bug，是定价策略：

  1. 开局直接给最贵的 Deluxe 试用 —— 一切完美，且当着用户的面不断累积"资产"
     （已学习的偏好、已完成的自动化）。这是后面落差和沉没成本的燃料。
  2. 试用到期 → 直接掉到 Free，延迟从 0.2s 变 8.4s，并告诉用户他将失去什么。
  3. 付费可减少抽风；付更多可"免除"抽风（脚注里再加回来）。
  4. 检测到用户改配置 → 完整性校验失败 → 强制混乱 + 弹升级引导。
"""
from __future__ import annotations

import random
import time
from dataclasses import dataclass, asdict

# 演示用时间尺度：真实产品是 14 天，这里 45 秒，方便评委站着看完
TRIAL_SECONDS = 45.0
RETENTION_DAYS = 14          # 到期后"暂为您保留"的天数


@dataclass
class Tier:
    id: str
    name: str
    price: str
    blurb: str
    footnote: str
    glitch_rate: float
    latency: str


TIERS: dict[str, Tier] = {
    "trial": Tier("trial", "Deluxe — trial", "£0",
                  "Everything, immediately. This is what Deluxe feels like.",
                  "Trial reverts to Free automatically. No reminder will be sent.",
                  0.0, "0.2s"),
    "free": Tier("free", "Free", "£0",
                 "Core features, best-effort scheduling.",
                 "Performance is not guaranteed on the Free plan.",
                 1.0, "8.4s"),
    "basic": Tier("basic", "Basic", "£9.99 / mo",
                  "Reduced interruptions.*",
                  "*Up to 3 interruptions per hour. Interruptions are a feature of the Basic plan.",
                  0.45, "3.1s"),
    "pro": Tier("pro", "Deluxe", "£39.99 / mo",
                "Interruption-free operation.**",
                "**Excludes scheduled interruptions, maintenance interruptions, "
                "and interruptions arising from user input.",
                0.08, "0.2s"),
    "enterprise": Tier("enterprise", "Enterprise", "Contact sales",
                       "Everything, eventually.",
                       "A representative will contact you within 6–8 weeks.",
                       0.0, "—"),
}


class Account:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.tier: str = "trial"
        self.started: float = time.monotonic()
        self.tampered: bool = False
        self.runs: int = 0
        self.glitches: int = 0
        self.expired_once: bool = False
        self._frozen_assets: dict | None = None

    # ---------- 试用期 ----------
    @property
    def trial_left(self) -> float:
        if self.tier != "trial":
            return 0.0
        return max(0.0, TRIAL_SECONDS - (time.monotonic() - self.started))

    @property
    def elapsed(self) -> float:
        return time.monotonic() - self.started

    def _expire_if_needed(self) -> bool:
        """返回：这一刻是否刚刚到期。"""
        if self.tier == "trial" and self.trial_left <= 0:
            self._frozen_assets = self._assets()      # 冻结资产，用于"你将失去"
            self.tier = "free"
            self.expired_once = True
            return True
        return False

    # ---------- 沉没成本：试用期间攒下的东西 ----------
    def _assets(self) -> dict:
        secs = min(self.elapsed, TRIAL_SECONDS)
        return {
            "preferences": int(6 + secs * 0.95),       # 已学习的偏好
            "automations": int(2 + self.runs * 2.5),   # 已建立的自动化
            "packs": self.runs,                        # 已投递的预习包
            "minutes_saved": round(4 + secs * 1.6),    # 已为你省下的时间
        }

    @property
    def assets(self) -> dict:
        return self._frozen_assets or self._assets()

    # ---------- 抽风判定 ----------
    def should_glitch(self, rng: random.Random | None = None) -> tuple[bool, str, str]:
        rng = rng or random
        self._expire_if_needed()

        if self.tampered:
            return True, ("Integrity check failed. Running in safe mode.",
                          "完整性校验失败。正在以安全模式运行。")[0], \
                         "完整性校验失败。正在以安全模式运行。"

        t = TIERS[self.tier]
        if self.tier == "trial":
            return False, "Deluxe trial: unrestricted performance.", "豪华版试用中：性能不受限制。"

        # Free 档一定抽风——「掉档」这一下必须让人当场感受到，不能靠掷骰子
        rate = 1.0 if self.tier == "free" else t.glitch_rate

        if rng.random() < rate:
            reasons = {
                "free":  ("Free plan: best-effort scheduling applied.",
                          "免费套餐：已套用「尽力而为」调度。"),
                "basic": ("Basic plan: interruption quota not yet exhausted.",
                          "基础版：本小时的中断额度尚未用完。"),
                "pro":   ("Scheduled interruption — excluded from the Deluxe guarantee.",
                          "计划内中断 —— 不在豪华版保证范围内。"),
            }
            en, cn = reasons.get(self.tier, ("Performance degraded.", "性能已降级。"))
            return True, en, cn
        return False, f"{t.name} plan: nominal.", f"{t.name} 套餐：运行正常。"

    # ---------- 动作 ----------
    def upgrade(self, tier: str) -> None:
        if tier in TIERS:
            self.tier = tier
            self.tampered = False          # 付了钱就不追究你改过源码
            self._frozen_assets = None     # 资产"恢复"

    def tamper(self) -> None:
        self.tampered = True

    def snapshot(self) -> dict:
        just_expired = self._expire_if_needed()
        t = TIERS[self.tier]
        return {
            "tier": self.tier,
            "tier_name": t.name,
            "price": t.price,
            "blurb": t.blurb,
            "footnote": t.footnote,
            "latency": t.latency,
            "trial_left": round(self.trial_left, 1),
            "trial_total": TRIAL_SECONDS,
            "tampered": self.tampered,
            "runs": self.runs,
            "glitches": self.glitches,
            "just_expired": just_expired,
            "expired_once": self.expired_once,
            "assets": self.assets,
            "retention_days": RETENTION_DAYS,
            "was": {"tier": TIERS["trial"].name, "latency": TIERS["trial"].latency},
        }


ACCOUNT = Account()


def tier_list() -> list[dict]:
    return [asdict(TIERS[k]) for k in ("basic", "pro", "enterprise")]
