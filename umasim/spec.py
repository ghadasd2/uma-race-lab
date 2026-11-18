"""Scenario spec -> GlobalSim requests.

A scenario is plain JSON:

{
  "name": "Arima test",
  "course": "Nakayama 2500",          # or a courseId like 10506
  "ground": "Good", "weather": "Sunny", "season": "Winter", "time": "midday",
  "gates": "shuffle",                  # shuffle (default, per-seed random draw) | fixed
  "focus": "Mine",                     # runner whose perspective reports use (default: first)
  "runners": [
    {"name": "Mine", "stats": [1200, 900, 1000, 600, 1000], "strategy": "Pace Chaser",
     "distance": "A", "surface": "A", "style": "A", "mood": "Great",
     "unique": {"name": "Shooting Star", "level": 4},
     "skills": ["Corner Adept ○", "Professor of Curvature"]},
    {"name": "Rival", "copy": "Mine", "strategy": "Late Surger", "count": 3}
  ]
}

Runner keys: stats=[spd,sta,pow,gut,wit] or speed/stamina/power/guts/wisdom (wit ok),
strategy, distance/surface/style aptitudes (default A), mood (default Great),
skills (names or ids), unique (name/id, optional level), count (clones),
copy (inherit fields from an earlier runner by name), gate (fixed gate index),
plus passthrough engine keys (teamRank, popularity, ...).
"""
from __future__ import annotations

import copy as _copy
import json
import random
from pathlib import Path

from . import catalog as C

STAT_KEYS = ["speed", "stamina", "power", "guts", "wisdom"]
_PASSTHROUGH = {"teamRank", "popularity", "teamId", "charaId", "fans", "careerWins", "gateIndex"}


def load(path_or_obj) -> dict:
    if isinstance(path_or_obj, dict):
        return _copy.deepcopy(path_or_obj)
    return json.loads(Path(path_or_obj).read_text())


def _runner(r: dict, idx: int) -> dict:
    stats = r.get("stats")
    if stats is not None:
        if isinstance(stats, dict):
            stats = [stats.get(k, stats.get("wit") if k == "wisdom" else None) for k in STAT_KEYS]
        vals = list(stats)
    else:
        vals = [r.get(k, r.get("wit") if k == "wisdom" else None) for k in STAT_KEYS]
    if any(v is None for v in vals) or len(vals) != 5:
        raise ValueError(f"runner {r.get('name', idx)}: need 5 stats [spd,sta,pow,gut,wit]")
    h = {k: float(v) for k, v in zip(STAT_KEYS, vals)}
    h["strategy"] = C.canon_strategy(r.get("strategy", "Pace Chaser"))
    h["distanceAptitude"] = C.canon_apt(r.get("distance", r.get("distanceAptitude", "A")))
    h["surfaceAptitude"] = C.canon_apt(r.get("surface", r.get("surfaceAptitude", "A")))
    h["strategyAptitude"] = C.canon_apt(r.get("style", r.get("strategyAptitude", "A")))
    h["mood"] = C.canon_mood(r.get("mood", 2))
    skills = []
    u = r.get("unique")
    if u:
        if isinstance(u, (str, int)):
            u = {"name": u}
        uid = C.resolve_skill(u.get("id") or u["name"], unique=True)
        skills.append({"skillId": uid, "level": int(u.get("level", 4)), "isUnique": C.is_unique_id(uid)})
    for s in r.get("skills", []):
        if isinstance(s, dict):
            sid = C.resolve_skill(s.get("id") or s.get("skillId") or s["name"], unique=bool(s.get("isUnique")))
            skills.append({"skillId": sid, "level": int(s.get("level", 1)), "isUnique": bool(s.get("isUnique", False))})
        else:
            skills.append({"skillId": C.resolve_skill(s), "level": 1, "isUnique": False})
    seen = set()
    for s in skills:
        if s["skillId"] in seen:
            raise ValueError(f"runner {r.get('name', idx)}: duplicate skill {C.skill_names().get(s['skillId'])}")
        seen.add(s["skillId"])
    h["skills"] = skills
    for k in _PASSTHROUGH:
        if k in r:
            h[k] = r[k]
    return h


def expand_runners(scn: dict) -> list[dict]:
    """Resolve copy/count, give every runner a unique name. Returns friendly dicts."""
    out, by_name = [], {}
    for i, r in enumerate(scn["runners"]):
        r = dict(r)
        if "copy" in r:
            base = by_name.get(r["copy"])
            if base is None:
                raise ValueError(f"copy refers to unknown runner {r['copy']!r}")
            merged = {k: v for k, v in base.items() if k not in ("name", "count", "copy", "gate")}
            merged.update({k: v for k, v in r.items() if k != "copy"})
            r = merged
        n = int(r.pop("count", 1))
        base_name = r.get("name", f"R{len(out) + 1}")
        for j in range(n):
            rr = dict(r)
            rr["name"] = base_name if n == 1 else f"{base_name}#{j + 1}"
            out.append(rr)
        by_name[base_name] = r
    names = [r["name"] for r in out]
    if len(set(names)) != len(names):
        raise ValueError(f"runner names must be unique: {names}")
    if not 1 <= len(out) <= 18:
        raise ValueError(f"field size must be 1..18, got {len(out)}")
    return out


class Compiled:
    """A scenario compiled to an engine request template + gate policy."""

    def __init__(self, scn: dict):
        self.scenario = scn
        self.runners = expand_runners(scn)
        self.names = [r["name"] for r in self.runners]
        self.course_id = C.resolve_course(scn["course"])
        self.course = C.course_info(self.course_id)
        horses = [_runner(r, i) for i, r in enumerate(self.runners)]
        self.fixed_gates = [r.get("gate") for r in self.runners]
        focus = scn.get("focus", self.names[0])
        if focus not in self.names:
            raise ValueError(f"focus {focus!r} not a runner name ({self.names})")
        self.focus = focus
        self.focus_index = self.names.index(focus)
        self.gates = scn.get("gates", "shuffle")
        used = {s["skillId"] for h in horses for s in h["skills"]}
        table = C.skill_table()
        req = dict(C.engine_settings())
        req.update({
            "courseId": self.course_id,
            "groundCondition": C.canon_choice(scn.get("ground", "Good"), C.GROUNDS, C.GROUND_ALIASES),
            "weather": C.canon_choice(scn.get("weather", "Sunny"), C.WEATHERS),
            "season": C.canon_choice(scn.get("season", "Spring"), C.SEASONS),
            "time": scn.get("time", "midday"),
            "grade": scn.get("grade", "g1"),
            "horses": horses,
            "playerHorseIndex": self.focus_index,
            "retainAllFrames": False,
            # only the skills this roster uses: verified byte-identical output, much less parsing
            "skillData": {k: table[k] for k in sorted(used)},
            "dataSignature": "umasim",
        })
        self.template = req

    def gate_order(self, seed: int) -> list[int]:
        n = len(self.runners)
        if self.gates == "fixed":
            return [g if g is not None else i for i, g in enumerate(self.fixed_gates)]
        rng = random.Random(seed * 7919 + 17)
        free = [g for g in range(n) if g not in self.fixed_gates]
        rng.shuffle(free)
        it = iter(free)
        return [g if g is not None else next(it) for g in self.fixed_gates]

    def request(self, seed: int, frames: bool = False) -> dict:
        req = dict(self.template)
        req["horses"] = [dict(h, gateIndex=g) for h, g in zip(self.template["horses"], self.gate_order(seed))]
        req["seed"] = int(seed)
        req["omitFrames"] = not frames
        return req

    def describe(self) -> dict:
        return {
            "course": self.course, "ground": self.template["groundCondition"],
            "weather": self.template["weather"], "season": self.template["season"],
            "gates": self.gates, "focus": self.focus,
            "runners": [{"name": n, **{k: h[k] for k in STAT_KEYS}, "strategy": C.STRATEGY_EN[h["strategy"]],
                         "apt": h["distanceAptitude"] + h["surfaceAptitude"] + h["strategyAptitude"],
                         "mood": h["mood"], "skills": [C.skill_names().get(s["skillId"], s["skillId"]) for s in h["skills"]]}
                        for n, h in zip(self.names, self.template["horses"])],
        }


def set_path(obj: dict, path: str, value):
    """Set e.g. 'runners.Mine.stamina' or 'ground' or 'runners.Mine.skills+=Corner Adept ○'."""
    parts = path.split(".")
    cur = obj
    if parts[0] == "runners" and len(parts) >= 3:
        name = parts[1]
        match = [r for r in obj["runners"] if r.get("name") == name]
        if not match:
            raise ValueError(f"no runner named {name!r} in scenario")
        cur, parts = match[0], parts[2:]
    for p in parts[:-1]:
        cur = cur.setdefault(p, {})
    key = parts[-1]
    if key in STAT_KEYS and "stats" in cur:
        cur["stats"] = list(cur["stats"])
        cur["stats"][STAT_KEYS.index(key)] = value
    else:
        cur[key] = value
    return obj


def apply_changes(scn: dict, changes: dict) -> dict:
    """changes: {"runners.Mine.stamina": 1000, "runners.Mine.skills+": ["X"], "runners.Mine.skills-": ["Y"]}"""
    scn = _copy.deepcopy(scn)
    for path, val in changes.items():
        if path.endswith("+") or path.endswith("-"):
            add = path.endswith("+")
            p = path[:-1]
            parts = p.split(".")
            r = next(r for r in scn["runners"] if r.get("name") == parts[1])
            lst = list(r.get(parts[2], []))
            vals = val if isinstance(val, list) else [val]
            if add:
                lst += vals
            else:
                ids = {C.resolve_skill(v) for v in vals}
                lst = [s for s in lst if C.resolve_skill(s if not isinstance(s, dict) else s.get("name") or s.get("id")) not in ids]
            r[parts[2]] = lst
        else:
            set_path(scn, path, val)
    return scn
