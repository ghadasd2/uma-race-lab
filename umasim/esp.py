"""Skill point accounting (ESP = sum of base costs, no hint discounts).

full ESP (what was actually spent):  a top-tier skill (◎ or gold, id suffix 1) also pays for its
  lower tier in the same group (○ or white, suffix 2); an evolved skill costs its base skill chain
  (gold + white); character uniques cost 0; inherited uniques cost their listed base cost.
listed ESP: own base cost only, except ◎ adds its ○ and evolved counts its base gold only.
"""
from __future__ import annotations

import json
from functools import lru_cache

from . import catalog as C


@lru_cache(None)
def meta() -> dict:
    m = json.loads((C.NAMES_DIR / "skill_meta_jp.json").read_text())
    m.update({k: v for k, v in C.skill_meta().items() if v.get("baseCost")})  # Global costs take precedence
    return m


def cost(sid: str) -> int:
    return int(meta().get(sid, {}).get("baseCost") or 0)


def group(sid: str) -> str:
    return str(meta().get(sid, {}).get("groupId") or sid)


def _rarity(sid: str) -> int:
    return int(C.skill_table().get(sid, {}).get("rarity") or 0)


def siblings(sid: str) -> list[str]:
    g = group(sid)
    return [k for k, v in meta().items() if str(v.get("groupId")) == g and k != sid and len(k) == 6 and k[0] == "2"
            and not C.skill_names().get(k, "").endswith("×")]


def gold_of(sid: str) -> str | None:
    return next((k for k in siblings(sid) + [sid] if _rarity(k) == 2), None)


def white_below(sid: str) -> str | None:
    """The white you must own before this gold, or the ○ under a ◎."""
    name = C.skill_names().get(sid, "")
    for k in siblings(sid):
        n = C.skill_names().get(k, "")
        if _rarity(sid) == 2 and _rarity(k) == 1:
            return k
        if "◎" in name and n.endswith("○"):
            return k
    return None


def kind(sid: str) -> str:
    if C.is_evolved_id(sid):
        return "evolved"
    if C.is_unique_id(sid):
        return "unique"
    if sid[0] == "9":
        return "inherited"
    name = C.skill_names().get(sid, "")
    t = C.skill_table().get(sid, {})
    if any(e["type"] in (1, 2, 3, 4, 5) for a in t.get("alternatives", []) for e in a["effects"]) and \
            all(a.get("baseDuration") == -1 for a in t.get("alternatives", [])):
        return "green"
    return {1: "white", 2: "gold"}.get(t.get("rarity"), "other")


def esp(sid: str, full: bool = True) -> int:
    k = kind(sid)
    if k == "unique":
        return 0
    if k == "evolved":
        top = gold_of(sid)
        if top is None:
            return 0
        low = white_below(top)
        return cost(top) + (cost(low) if (full and low) else 0)
    c = cost(sid)
    low = white_below(sid)
    if low and (full or "◎" in C.skill_names().get(sid, "")):
        c += cost(low)
    return c


def build_esp(skill_names: list[str], full: bool = True) -> int:
    return sum(esp(C.resolve_skill(n), full) for n in skill_names)
