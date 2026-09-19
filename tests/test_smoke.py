"""赛前冒烟测试：证明「写代码 → 跑测试 → 提交」这条链是通的。"""
import sys
from datetime import datetime
from zoneinfo import ZoneInfo


def test_python_version():
    assert sys.version_info >= (3, 12)


def test_uk_timezone_available():
    now = datetime.now(ZoneInfo("Europe/London"))
    assert now.year == 2026


def test_math_still_works():
    assert sum(range(1, 11)) == 55
