"""Realistic random skill builds for my LoH umas, drawn only from data/loh/skill_pool.json.

Constraints per build:
  * the uma's evolved skills are always held (they cost their base gold+white in ESP)
  * only enabled pool skills usable by the uma's strategy (and allowed for that uma)
  * one skill per tier group (◎ vs ○, gold vs its white, e.g. Solid Preparation vs Groundwork)
  * no base skill of the uma's own evolutions, no inheriting her own unique
  * at most MAX_INHERITED inherited uniques, at most MAX_SKILLS skills incl. the unique
  * full ESP within ESP_RANGE
Skills are drawn in a weighted-random order (weight = 1 + number of top builds that carry the skill),
so common meta skills appear more often but every pool skill gets explored.
"""
from __future__ import annotations

import copy
import json
import random
from functools import lru_cache

from . import catalog as C
from . import esp

POOL_FILE = C.ROOT / "data" / "loh" / "skill_pool.json"
MAX_SKILLS = 23          # incl. unique
MAX_INHERITED = 3
EVOLVED = {"Kitasan Black": ["Introducing the Victor!", "Leap Ahead to the Future"],
           "Ines Fujin": ["Perfect ♪ Order Up!", "Slick Serving"],
           "Neo Universe": ["Beyond the Stars with You", "Cross the Sea of Stars"]}
EVOLVED_BASES = {"Introducing the Victor!": ["Taking the Lead"], "Leap Ahead to the Future": ["Escape Artist"],
                 "Perfect ♪ Order Up!": ["Concentration"], "Slick Serving": ["Crescent Gale"],
                 "Beyond the Stars with You": ["Come What May"], "Cross the Sea of Stars": ["Luminescence"]}


def esp_range():
    r = json.loads((C.ROOT / "data" / "loh" / "rules.json").read_text())["my_team"]
    return tuple(r.get("esp_range", [4500, 4600]))


@lru_cache(None)
def pool() -> list[dict]:
    return json.loads(POOL_FILE.read_text())


def candidates(uma: dict) -> list[dict]:
    key = "front" if uma["strategy"] == "Front Runner" else "late"
    blocked = {b for e in EVOLVED.get(uma["name"], []) for b in EVOLVED_BASES.get(e, [])}
    own_unique = uma["unique"]["name"]
    out = []
    for p in pool():
        if not p["enabled"] or not p[key] or p["type"] == "evolved":
            continue
        if p.get("allowed_umas") and uma["name"] not in p["allowed_umas"]:
            continue
        if p["skill"] in blocked or p["skill"] == own_unique:
            continue
        out.append(p)
    return out


def build_esp(skills: list[str]) -> int:
    return sum(esp.esp(C.resolve_skill(s), True) for s in skills)


def _group(name: str) -> str:
    return esp.group(C.resolve_skill(name))


def valid(uma: dict, skills: list[str], lo_hi=None) -> tuple[bool, str]:
    lo, hi = lo_hi or esp_range()
    if len(skills) + 1 > MAX_SKILLS:
        return False, f"{len(skills) + 1} skills > {MAX_SKILLS}"
    groups = [_group(s) for s in skills]
    if len(groups) != len(set(groups)):
        return False, "two tiers of one skill"
    inh = sum(1 for s in skills if esp.kind(C.resolve_skill(s)) == "inherited")
    if inh > MAX_INHERITED:
        return False, f"{inh} inherited > {MAX_INHERITED}"
    allowed = {p["skill"] for p in candidates(uma)} | set(EVOLVED.get(uma["name"], []))
    bad = [s for s in skills if s not in allowed]
    if bad:
        return False, f"not allowed: {bad}"
    e = build_esp(skills)
    if not lo <= e <= hi:
        return False, f"ESP {e} outside {lo}-{hi}"
    return True, "ok"


def random_skills(uma: dict, rng: random.Random, lo_hi=None, tries: int = 2000) -> list[str]:
    lo, hi = lo_hi or esp_range()
    fixed = list(EVOLVED.get(uma["name"], []))
    cands = candidates(uma)
    for _ in range(tries):
        order = sorted(cands, key=lambda p: rng.random() ** (1.0 / (1 + len(p["used_by"]))), reverse=True)
        skills, e = list(fixed), build_esp(fixed)
        groups = {_group(s) for s in skills}
        inh = 0
        for p in order:
            if len(skills) + 1 >= MAX_SKILLS:
                break
            g = _group(p["skill"])
            if g in groups or e + p["esp_full"] > hi:
                continue
            if p["type"] == "inherited" and inh >= MAX_INHERITED:
                continue
            skills.append(p["skill"]); groups.add(g); e += p["esp_full"]
            inh += p["type"] == "inherited"
        if lo <= e <= hi:
            return skills
    raise RuntimeError(f"could not draw a build for {uma['name']} in ESP {lo}-{hi}")


def random_build(uma: dict, rng: random.Random, lo_hi=None) -> dict:
    b = copy.deepcopy(uma)
    b["skills"] = random_skills(uma, rng, lo_hi)
    return b


def mutate(uma_build: dict, rng: random.Random, lo_hi=None, tries: int = 500) -> dict | None:
    """Swap 1-2 non-locked skills for others (local search step), keeping every constraint."""
    fixed = set(EVOLVED.get(uma_build["name"], []))
    cands = [p["skill"] for p in candidates(uma_build)]
    for _ in range(tries):
        s = list(uma_build["skills"])
        for _k in range(rng.choice([1, 1, 2])):
            removable = [x for x in s if x not in fixed]
            if removable and rng.random() < 0.85:
                s.remove(rng.choice(removable))
            add = [c for c in cands if c not in s]
            if add:
                s.append(rng.choice(add))
        if s != uma_build["skills"] and valid(uma_build, s, lo_hi)[0]:
            b = copy.deepcopy(uma_build); b["skills"] = s
            return b
    return None
