"""Lookup tables: courses, skills, strategies, aptitudes.

Engine data (course geometry, skill effect tables) comes from GlobalSim.
English names come from data/names/ (from alpha123/uma-tools, GPL-3.0).
"""
from __future__ import annotations

import difflib
import json
import os
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENGINE_DIR = Path(os.environ.get("UMASIM_ENGINE_DIR", ROOT / "vendor" / "GlobalSim"))
ENGINE_BIN = Path(os.environ.get("UMASIM_ENGINE_BIN", ENGINE_DIR / "target" / "release" / "race_engine_rs_v2"))
NAMES_DIR = ROOT / "data" / "names"

# --- enums -----------------------------------------------------------------

STRATEGIES = {  # canonical engine name -> English names / aliases
    "Nige": ["front runner", "front", "runner", "nige", "escape", "lead"],
    "Senkou": ["pace chaser", "pace", "chaser", "senkou", "leader"],
    "Sasi": ["late surger", "late", "surger", "sasi", "sashi", "betweener"],
    "Oikomi": ["end closer", "end", "closer", "oikomi", "chaser-end"],
    "Oonige": ["runaway", "great escape", "oonige", "big escape"],
}
STRATEGY_EN = {"Nige": "Front Runner", "Senkou": "Pace Chaser", "Sasi": "Late Surger",
               "Oikomi": "End Closer", "Oonige": "Runaway"}
RUNNING_STYLE_CODE = {1: "Nige", 2: "Senkou", 3: "Sasi", 4: "Oikomi", 5: "Oonige"}

MOODS = {"awful": -2, "bad": -1, "normal": 0, "good": 1, "great": 2}
APTITUDES = ["S", "A", "B", "C", "D", "E", "F", "G"]
GROUNDS = ["Good", "Yielding", "Soft", "Heavy"]
GROUND_ALIASES = {"firm": "Good", "good": "Good", "yielding": "Yielding", "slightly heavy": "Yielding",
                  "soft": "Soft", "heavy": "Heavy", "bad": "Heavy"}
WEATHERS = ["Sunny", "Cloudy", "Rainy", "Snowy"]
SEASONS = ["Spring", "Summer", "Autumn", "Winter", "Sakura"]
SURFACE = {1: "Turf", 2: "Dirt"}
DIST_TYPE = {1: "Sprint", 2: "Mile", 3: "Medium", 4: "Long"}
TURN = {1: "Right", 2: "Left", 3: "Straight", 4: "Straight"}
COURSE_VARIANT = {1: "", 2: "Inner", 3: "Outer", 4: "Outer→Inner"}
SKILL_RARITY = {1: "white", 2: "gold", 3: "unique", 4: "unique", 5: "evolved/unique+"}


def canon_strategy(s: str) -> str:
    if s in STRATEGIES:
        return s
    k = s.strip().lower().replace("_", " ")
    for canon, aliases in STRATEGIES.items():
        if k == canon.lower() or k in aliases:
            return canon
    raise ValueError(f"unknown strategy {s!r}; use one of {list(STRATEGY_EN.values())}")


def canon_mood(m) -> int:
    if isinstance(m, (int, float)):
        return int(m)
    k = str(m).strip().lower()
    if k in MOODS:
        return MOODS[k]
    return int(k)


def canon_apt(a) -> str:
    a = str(a).strip().upper()
    if a not in APTITUDES:
        raise ValueError(f"aptitude must be one of {APTITUDES}, got {a!r}")
    return a


def canon_choice(v: str, choices: list[str], aliases: dict | None = None) -> str:
    k = str(v).strip().lower()
    if aliases and k in aliases:
        return aliases[k]
    for c in choices:
        if c.lower() == k:
            return c
    raise ValueError(f"{v!r} not in {choices}")


# --- data loading ------------------------------------------------------------

def _load(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def is_unique_id(sid: str) -> bool:
    """Character uniques are 5-6 digit ids starting with 1 (evolved skills are 9-digit 1xxxxxxxx)."""
    return sid[0] == "1" and len(sid) <= 6


def is_evolved_id(sid: str) -> bool:
    return len(sid) == 9 and sid[0] == "1"


@lru_cache(None)
def validated_table() -> dict:
    """The audited v70 skill table the v77 validated profile uses."""
    return _load(ENGINE_DIR / "data" / "v70-skill-data.json")


# Unique level scaling in the validated table depends only on effect type (checked over all uniques).
_UNIQUE_LEVEL_MODS = {
    27: [1.0, 1.01, 1.04, 1.07, 1.1, 1.13, 1.16, 1.19, 1.22, 1.25],    # target speed
    31: [1.0, 1.02, 1.04, 1.06, 1.08, 1.1, 1.125, 1.15, 1.175, 1.2],   # acceleration
    22: [1.0, 1.02, 1.04, 1.06, 1.08, 1.1, 1.12, 1.14, 1.16, 1.18],    # current speed
    9: [1.0, 1.02, 1.04, 1.06, 1.08, 1.1, 1.12, 1.14, 1.16, 1.18],     # recovery
}


def _convert_legacy(sid: str, e: dict) -> dict:
    """Legacy (sparse) entry -> validated-table shape. Conditions/values/durations are kept as-is;
    structural fields get the validated table's conventions (one-shot cooldown, permanent stat skills
    cooldown 0, unique level scaling by effect type)."""
    import copy
    e = copy.deepcopy(e)
    uniq = is_unique_id(sid)
    out = {"rarity": e["rarity"], "wisdomCheck": e.get("wisdomCheck", 0), "priority": 0, "tags": [],
           "alternatives": [], "isGeneralSkill": not uniq, "approximated": True}
    for a in e["alternatives"]:
        effs = []
        for ef in a["effects"]:
            f = {"type": ef["type"], "target": ef.get("target", 1), "targetValue": ef.get("targetValue", 0),
                 "additionalActivate": 0, "valueUsage": ef.get("valueUsage", 1), "modifier": ef["modifier"]}
            if uniq and ef["type"] in _UNIQUE_LEVEL_MODS:
                f["levelModifiers"] = _UNIQUE_LEVEL_MODS[ef["type"]]
            effs.append(f)
        out["alternatives"].append({"condition": a["condition"], "precondition": a.get("precondition", ""),
                                    "baseDuration": a["baseDuration"], "durationUsage": 1,
                                    "cooldown": 0 if a["baseDuration"] == -1 else 5000000, "effects": effs})
    return out


@lru_cache(None)
def skill_table() -> dict:
    """Validated v70 table, extended with legacy-only skills converted to the same shape
    (flagged `approximated`). Every LoH opponent skill among these was checked against in-game data."""
    t = dict(validated_table())
    for sid, e in _load(ENGINE_DIR / "data" / "skill_data.json").items():
        if sid not in t:
            try:
                t[sid] = _convert_legacy(sid, e)
            except (KeyError, TypeError):
                pass
    return t


def is_approximated(sid: str) -> bool:
    return bool(skill_table().get(str(sid), {}).get("approximated"))


@lru_cache(None)
def course_table() -> dict:
    return _load(ENGINE_DIR / "data" / "course_data.json")


@lru_cache(None)
def geometry_ids() -> frozenset:
    return frozenset(p.stem for p in (ENGINE_DIR / "data" / "course_geometry").glob("*.json"))


@lru_cache(None)
def skill_names() -> dict:
    return {k: v[0] for k, v in _load(NAMES_DIR / "skillnames.json").items()}


@lru_cache(None)
def skill_meta() -> dict:
    return _load(NAMES_DIR / "skill_meta.json")


@lru_cache(None)
def track_names() -> dict:
    return {int(k): v[1] for k, v in _load(NAMES_DIR / "tracknames.json").items()}


@lru_cache(None)
def engine_settings() -> dict:
    """Runtime switches from the validated v77 example (minus per-race fields)."""
    return _load(ENGINE_DIR / "examples" / "v77-settings.json")


# --- courses -----------------------------------------------------------------

def course_info(cid) -> dict:
    cid = str(cid)
    c = course_table()[cid]
    track = track_names().get(c["raceTrackId"], str(c["raceTrackId"]))
    variant = COURSE_VARIANT.get(c.get("course", 1), "")
    surface = SURFACE.get(c["surface"], "?")
    label = f"{track} {c['distance']}m {surface}" + (f" ({variant})" if variant else "")
    return {
        "courseId": int(cid), "label": label, "track": track, "distance": c["distance"],
        "surface": surface, "distanceType": DIST_TYPE.get(c["distanceType"], "?"),
        "turn": TURN.get(c.get("turn"), "?"), "variant": variant,
        "corners": len(c.get("corners", [])), "slopes": len(c.get("slopes", [])),
        "finalStraight": next((s["end"] - s["start"] for s in reversed(c.get("straights", []))), None),
        "hasGeometry": cid in geometry_ids(),
    }


def list_courses() -> list[dict]:
    return [course_info(k) for k in sorted(course_table(), key=int)]


def resolve_course(spec) -> int:
    """Accept an id (10504), or text like 'Nakayama 2000' / 'Tokyo 2400 turf' / 'Hanshin 1600 outer'."""
    if isinstance(spec, int) or (isinstance(spec, str) and spec.strip().isdigit()):
        cid = str(int(spec))
        if cid not in course_table():
            raise ValueError(f"unknown courseId {cid}")
        return int(cid)
    words = str(spec).lower().replace("m ", " ").split()
    nums = [int(re.sub(r"\D", "", w)) for w in words if re.sub(r"\D", "", w)]
    text = [w for w in words if not re.sub(r"\D", "", w)]
    hits = []
    for c in list_courses():
        if nums and c["distance"] not in nums:
            continue
        hay = f"{c['track']} {c['surface']} {c['variant']}".lower()
        if all(t in hay for t in text):
            hits.append(c)
    if not hits:
        raise ValueError(f"no course matches {spec!r} (try `umasim courses`)")
    if len(hits) > 1 and not any(t in ("turf", "dirt") for t in text):
        turf = [h for h in hits if h["surface"] == "Turf"]
        hits = turf or hits
    if len(hits) > 1:
        # prefer the plain (non inner/outer) layout when ambiguous
        plain = [h for h in hits if not h["variant"]]
        if len(plain) == 1 and not any(t in ("inner", "outer") for t in text):
            return plain[0]["courseId"]
        raise ValueError(f"{spec!r} is ambiguous: " + "; ".join(f"{h['courseId']}={h['label']}" for h in hits))
    return hits[0]["courseId"]


# --- skills ------------------------------------------------------------------

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def skill_info(sid: str) -> dict:
    sid = str(sid)
    t = skill_table().get(sid, {})
    m = skill_meta().get(sid, {})
    kind = ("evolved" if is_evolved_id(sid) else "unique" if is_unique_id(sid)
            else {"9": "inherited unique", "2": "normal", "3": "scenario"}.get(sid[0], "?"))
    conds = [a.get("condition", "") for a in t.get("alternatives", [])]
    return {"id": sid, "name": skill_names().get(sid, sid), "kind": kind,
            "rarity": SKILL_RARITY.get(t.get("rarity"), t.get("rarity")),
            "cost": m.get("baseCost"), "groupId": m.get("groupId"),
            "wisdomCheck": bool(t.get("wisdomCheck")), "conditions": conds,
            "effectTypes": sorted({e["type"] for a in t.get("alternatives", []) for e in a.get("effects", [])}),
            "inEngine": sid in skill_table(), "approximated": is_approximated(sid)}


def resolve_skill(spec, unique: bool = False) -> str:
    """Name or id -> engine skill id. For a name shared by a unique (1xxxxx) and its
    inherited version (9xxxxx), `unique=True` picks the unique, otherwise inherited."""
    s = str(spec).strip()
    if s.isdigit():
        if s not in skill_table():
            raise ValueError(f"skill id {s} is not in the engine skill table")
        return s
    want = _norm(s)
    table = skill_table()
    cands = [sid for sid, n in skill_names().items() if sid in table and _norm(n) == want]
    if not cands:
        # tolerate missing ○/◎ marks and punctuation
        strip = lambda x: re.sub(r"[^a-z0-9 ]", "", _norm(x)).strip()
        cands = [sid for sid, n in skill_names().items() if sid in table and strip(n) == strip(s)]
    if not cands:
        names = {skill_names()[k]: k for k in table if k in skill_names()}
        close = difflib.get_close_matches(s, list(names), n=5, cutoff=0.6)
        raise ValueError(f"unknown skill {s!r}" + (f"; did you mean {close}?" if close else ""))
    if len(cands) > 1:
        pref = [c for c in cands if (is_unique_id(c) if unique else c[0] == "9")]
        if pref:
            cands = pref
    if not unique and all(is_unique_id(c) for c in cands):
        raise ValueError(f"{s!r} is a unique skill and its inherited version is not in the engine skill table; "
                         f"put it in the runner's \"unique\" field instead")
    if len(cands) > 1:
        # e.g. ○ and ◎ variants that only differ by mark were already disambiguated by exact match
        cands.sort()
    return cands[0]


def search_skills(query: str = "", limit: int = 30, kind: str | None = None) -> list[dict]:
    q = _norm(query)
    out = []
    for sid in skill_table():
        info = skill_info(sid)
        if kind and not info["kind"].startswith(kind):
            continue
        hay = (info["name"] + " " + " ".join(info["conditions"])).lower()
        if not q or all(w in hay for w in q.split()):
            out.append(info)
    out.sort(key=lambda d: (d["kind"] != "normal", d["name"]))
    return out[:limit]
