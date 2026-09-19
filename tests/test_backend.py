"""ORCHESTRA 后端测试。

跑法（在 D:\\Projects\\hackstart-2026 目录下）：
    python -m pytest tests/ -v

这些测试保护的是演示里最不能出错的三件事：
  1. 流水线读的是真数据，且六个阶段都跑得出来
  2. 试用期一定完美、掉档后一定抽风（现场不能靠运气）
  3. 反向满足一定给出相反的结果，且中英双语都在
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import billing, inverse, pipeline


# ---------------------------------------------------------------- 真实数据
def test_data_files_exist():
    """真数据缺了，整个演示就是假的。"""
    data = Path(__file__).resolve().parent.parent / "data"
    assert (data / "timetable.ics").exists()
    assert (data / "modules.json").exists()
    assert (data / "lecturers.json").exists()
    assert list((data / "prep").glob("*.md")), "没有预习包，产物区会是空的"


def test_pipeline_parses_real_timetable():
    events = pipeline._ics_events()
    assert len(events) > 50, "真课表应该有上百条事件"
    assert all("start" in e for e in events)


# ---------------------------------------------------------------- 流水线
def test_nominal_run_all_ok():
    stages = pipeline.run("nominal")
    assert len(stages) == 6
    assert all(s["ok"] for s in stages), "正常态不能有失败阶段"
    assert all(s["actually_did"] == s["assigned_to"] for s in stages), "正常态不能改派"


def test_nominal_delivers_requested_pack():
    stages = pipeline.run("nominal")
    art = next(s["artifact"] for s in stages if s["artifact"])
    assert art["code"] == art["requested"], "正常态必须送对预习包"


def test_chaos_run_reroutes_and_fails():
    stages = pipeline.run("chaos", seed=7)
    assert any(not s["ok"] for s in stages), "混乱态必须有失败"
    assert any(s["actually_did"] != s["assigned_to"] for s in stages), "混乱态必须有改派"


def test_chaos_serves_the_wrong_pack():
    """要 A 给 B —— 这是整个演示最好笑的一拍，不能丢。"""
    stages = pipeline.run("chaos", seed=3)
    art = stages[3]["artifact"]
    assert art["code"] != art["requested"]


def test_every_stage_is_bilingual():
    for s in pipeline.run("chaos", seed=1):
        assert s["detail"] and s["detail_cn"], f'{s["id"]} 缺中文'
        assert s["name"] and s["name_cn"]


# ---------------------------------------------------------------- 商业逻辑
def test_trial_never_glitches():
    acc = billing.Account()
    for _ in range(30):
        glitch, _, _ = acc.should_glitch()
        assert not glitch, "试用期抽风就毁了落差"


def test_free_always_glitches():
    """掉档那一下必须当场可见，不能掷骰子。"""
    acc = billing.Account()
    acc.started -= billing.TRIAL_SECONDS + 1
    acc.snapshot()                       # 触发过期
    for _ in range(30):
        glitch, _, _ = acc.should_glitch()
        assert glitch


def test_expiry_freezes_assets_for_sunk_cost():
    acc = billing.Account()
    acc.runs = 4
    acc.started -= billing.TRIAL_SECONDS + 1
    snap = acc.snapshot()
    assert snap["just_expired"] is True
    assert snap["tier"] == "free"
    assert snap["assets"]["preferences"] > 0, "没有资产就没有沉没成本"
    assert snap["was"]["latency"] != snap["latency"], "前后延迟必须有落差"


def test_upgrade_restores_and_forgives_tampering():
    acc = billing.Account()
    acc.tamper()
    assert acc.should_glitch()[0] is True
    acc.upgrade("pro")
    assert acc.tampered is False, "付钱之后连改过源码都既往不咎——这是最脏的那个细节"


def test_all_paid_tiers_have_chinese():
    for t in billing.tier_list():
        assert t["blurb_cn"], f'{t["name"]} 缺中文卖点'
        assert t["footnote_cn"], f'{t["name"]} 缺中文脚注'


# ---------------------------------------------------------------- 反向满足
@pytest.mark.parametrize("ask,must_contain", [
    ("play me some calm music", "Drill"),
    ("I want a burger", "penne"),
    ("make it quick", "1,204"),
    ("can you make the text bigger", "2.6"),
])
def test_inverse_gives_the_opposite(ask, must_contain):
    en, cn = inverse.invert(ask)
    assert must_contain in en
    assert cn, "中文不能缺"


def test_inverse_always_answers():
    en, cn = inverse.invert("zzzz nonsense input")
    assert en and cn


def test_calm_music_triggers_the_drill_sound():
    assert inverse.sound_for("something calm please") == "drill"
