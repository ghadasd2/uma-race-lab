"""Screenshot-verified corrections to converted legacy skills are applied by catalog.skill_table()."""
import json
from pathlib import Path

from umasim import catalog as C


def test_break_the_mold_condition_matches_in_game_page():
    cond = C.skill_table()["202522"]["alternatives"][0]["condition"]
    assert "order_rate>=40" in cond and "order_rate>=50" not in cond
    assert C.skill_table()["202522"]["alternatives"][0]["baseDuration"] == 30000


def test_every_override_targets_a_known_skill():
    ov = json.loads(Path(C.SKILL_OVERRIDES).read_text())
    for sid, o in ov.items():
        if sid.startswith("_"):
            continue
        assert sid in C.skill_table(), sid
        for idx, fields in o["alternatives"].items():
            for k, v in fields.items():
                assert C.skill_table()[sid]["alternatives"][int(idx)][k] == v
