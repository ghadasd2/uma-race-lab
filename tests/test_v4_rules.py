"""v4 rule helpers: front start-accel rule, stat cost, HP-out floor."""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from umasim import buildgen as G, mock  # noqa: E402

TEAM = json.loads((Path(__file__).resolve().parent.parent / "data/loh/my_team_v3_champion.json").read_text())
KITA, INES, NEO = TEAM


def test_front_accel_rule():
    base = [s for s in INES["skills"] if s not in G.GROUNDWORK_FAMILY + ("Taking the Lead",)]
    assert G.front_accel_ok(INES, base + ["Solid Preparation"])
    assert G.front_accel_ok(INES, base + ["Groundwork", "Taking the Lead"])
    assert not G.front_accel_ok(INES, base + ["Taking the Lead"])          # TtL without Groundwork
    assert not G.front_accel_ok(INES, base + ["Groundwork"])               # no gold/evo start accel
    kb = [s for s in KITA["skills"] if s not in G.GROUNDWORK_FAMILY + ("Taking the Lead",)]
    assert G.front_accel_ok(KITA, kb + ["Groundwork"])                     # Introducing the Victor! counts
    assert not G.front_accel_ok(KITA, kb + ["Taking the Lead"])
    assert G.front_accel_ok(NEO, [])                                       # rule is fronts-only


def test_legal_accel_sets():
    assert sorted(map(tuple, G.legal_accel_sets(INES))) == sorted(
        [("Groundwork", "Taking the Lead"), ("Solid Preparation",), ("Solid Preparation", "Taking the Lead")])
    # Kitasan: Taking the Lead is the base of her evolved Introducing the Victor!, so it is not separately available
    assert sorted(map(tuple, G.legal_accel_sets(KITA))) == [("Groundwork",), ("Solid Preparation",)]


def test_v3_champion_still_legal():
    for b in TEAM:
        assert G.valid(b, b["skills"])[0], b["name"]


def test_stat_cost():
    assert mock.stat_cost([1430, 1100, 1200, 1200, 1200]) == 6360
    assert mock.stat_cost([1450, 1000, 1250, 1200, 1200]) == 6400


def test_hp_floor():
    ok = pd.DataFrame({"hp0": [True] * 3 + [False] * 172, "hp1": [False] * 175, "hp2": [False] * 175})
    bad = ok.assign(hp1=[True] * 4 + [False] * 171)
    assert mock.hp_ok(ok) and not mock.hp_ok(bad)
    assert mock.hp_status(bad) == "fail"
    assert mock.hp_status(ok) == "marginal"                                # 3/175 passes, its upper bound doesn't
    assert mock.wilson_ub(0, 1000) < 0.004
