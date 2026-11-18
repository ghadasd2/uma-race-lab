"""Run: python3 -m pytest -q tests  (needs the engine built)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from umasim import catalog as C
from umasim import engine, experiments as X, spec

SCN = {"course": "Tokyo 2400", "runners": [
    {"name": "Mine", "stats": [1100, 900, 1000, 500, 1000], "strategy": "Pace Chaser", "skills": ["Corner Recovery ○"]},
    {"name": "Rival", "copy": "Mine", "strategy": "Late Surger", "count": 5}]}


def test_course_resolution():
    assert C.course_info(C.resolve_course("Nakayama 2500"))["surface"] == "Turf"
    assert C.course_info(C.resolve_course("Chukyo 1200 dirt"))["surface"] == "Dirt"
    assert C.resolve_course(10606) == 10606


def test_skill_resolution():
    assert C.resolve_skill("Corner Recovery ○") == "200352"
    assert C.resolve_skill("corner recovery") in ("200352", "200353")
    with pytest.raises(ValueError):
        C.resolve_skill("Definitely Not A Skill")
    # unique vs inherited
    assert C.resolve_skill("Red Ace", unique=True).startswith("1")
    assert C.resolve_skill("Resplendent Red Ace").startswith("9")
    with pytest.raises(ValueError):
        C.resolve_skill("Red Ace")  # no inherited version in table


def test_expand_and_gates():
    c = spec.Compiled(SCN)
    assert c.names == ["Mine", "Rival#1", "Rival#2", "Rival#3", "Rival#4", "Rival#5"]
    g = c.gate_order(5)
    assert sorted(g) == list(range(6)) and g == c.gate_order(5)
    assert set(c.template["skillData"]) == {"200352"}


def test_determinism_and_null_variant():
    a = X.run(SCN, n=60, save=False)["focus"]
    b = X.run(SCN, n=60, save=False)["focus"]
    assert a == b
    s = X.compare(SCN, {"same": {"runners.Mine.mood": 2}}, n=60, save=False)
    assert s["results"][1]["d_win_pp"]["diff"] == 0 and s["results"][1]["d_time_s"]["diff"] == 0


def test_stamina_monotone_hp():
    s = X.sweep(SCN, "runners.Mine.stamina", [500, 1100], n=150, save=False)
    lo, hi = s["curve"]
    assert lo["hp_empty_pct"] >= hi["hp_empty_pct"]
    assert lo["full_spurt_pct"] <= hi["full_spurt_pct"]
