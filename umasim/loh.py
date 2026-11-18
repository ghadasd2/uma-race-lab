"""League of Heroes (LoH) race model: 3 (mine) v 3 (opponent team) v 6 NPCs, Tokyo 2400m (Tokyo Yushun) Spring.

Per seed everything except my team is drawn deterministically from the seed: NPC strategies/stats/
kits, every runner's mood, the 12-gate draw, ground, weather and time. So different builds for my team
face *identical* races (common random numbers), which makes build comparisons paired.

Runner order in every request: [mine x3, opponent x3, npc x6]; teamId 1 = mine, 2 = opponent, 0 = NPC
(team ids matter: team-stat skills like Racing Spirit / Ignited Spirit sum their team's stats).
"""
from __future__ import annotations

import copy
import json
import random
from pathlib import Path

import numpy as np
import pandas as pd

from . import catalog as C
from . import engine, spec

DATA = C.ROOT / "data" / "loh"
COURSE = "Tokyo 2400"
POINTS = {1: 100, 2: 60, 3: 40, 4: 30, 5: 20}  # 6th-12th: 10
GROUNDS = ["Good", "Yielding", "Soft", "Heavy"]
WEATHERS = ["Sunny", "Cloudy", "Rainy"]          # Spring: no snow
TIMES = ["morning", "midday", "evening"]
STRATS = ["Front Runner", "Pace Chaser", "Late Surger", "End Closer"]
APT_KEY = {"Front Runner": "front", "Pace Chaser": "pace", "Late Surger": "late", "End Closer": "end"}
CHARA = {"Kitasan Black": 1068, "Ines Fujin": 1031, "Neo Universe": 1105, "Mihono Bourbon": 1026}

# evolved skill -> the skill it replaces (from in-game data supplied by the user)
EVOLVES_FROM = {
    "Introducing the Victor!": "Taking the Lead", "Leap Ahead to the Future": "Escape Artist",
    "Perfect ♪ Order Up!": "Concentration", "Slick Serving": "Crescent Gale",
    "Beyond the Stars with You": "Come What May", "Cross the Sea of Stars": "Luminescence",
    "Perfect Boost": "Concentration", "Malfunction Mitigation": "Escape Artist",
}

PACE_NPC_KIT = ["Firm Conditions ○", "Outer Post Proficiency ○", "Straightaway Adept", "Soft Step", "Center Stage",
                "Prepared to Pass", "Pace Chaser Straightaways ○", "Pace Chaser Corners ○", "Pace Chaser Savvy ○",
                "Prudent Positioning", "Up-Tempo"]


def course_distance() -> int:
    return C.course_info(C.resolve_course(COURSE))["distance"]


def points(place: int) -> int:
    return POINTS.get(place, 10)


# ----------------------------------------------------------------------------- data

def _load(name):
    return json.loads((DATA / name).read_text())


def _from_record(u: dict, *, level=None, distance=None, style=None, strategy=None) -> dict:
    """Team-file record -> build dict."""
    strat = strategy or u["strategy"]
    name = u.get("name") or u.get("en", "").replace(" (alt)", "")
    return {
        "name": name, "chara": name, "strategy": strat, "stats": list(u["stats"]),
        "surface": u["turf"], "distance": distance or u["medium"], "style": style or u[APT_KEY[strat]],
        "unique": {"name": u["unique"]["name"], "level": level or u["unique"]["level"]},
        "skills": list(u["skills"]),
    }


def opponent_team(world: str) -> list[dict]:
    cn = _load("cn_team.json")
    neo = next(u for u in cn["team"] if u["name"] == "Neo Universe")
    if world == "cn":
        return [_from_record(u) for u in cn["team"]]
    if world == "jp":
        jp = _load("jp_team.json")
        recs = [dict(u, name=u["en"].replace(" (alt)", "")) for u in jp["team"]] + [neo]
        return [_from_record(u) for u in recs]
    raise ValueError(world)


def npc_pool() -> dict:
    """strategy -> {'kits': [...], 'stat_ranges': [(lo,hi)]*5}."""
    d = _load("npcs.json")["npcs"]
    stats = np.array([n["stats"] for n in d])
    ranges = [(int(stats[:, i].min()), int(stats[:, i].max())) for i in range(5)]
    kits = {s: [] for s in STRATS}
    for n in d:
        kits[n["strategy"]].append(n["skills"])
    kits["Pace Chaser"].append(PACE_NPC_KIT)
    return {"kits": kits, "stat_ranges": ranges}


def my_baseline() -> list[dict]:
    """CN builds of Kitasan / Ines / Neo with the user's rules: unique Lv6, distance S, style A,
    stats projected into the allowed box with total 6100."""
    r = _load("rules.json")["my_team"]
    cn = _load("cn_team.json")["team"]
    out = []
    for u in cn:
        b = _from_record(u, level=6, distance="S", style="A")
        b["stats"] = project_stats(b["stats"], r["stat_ranges"], r["stat_total_max"] if isinstance(r["stat_total_max"], int) else 6100)
        out.append(b)
    return out


STAT_ORDER = ["speed", "stamina", "power", "guts", "wisdom"]


def stat_box():
    r = _load("rules.json")["my_team"]
    return [tuple(r["stat_ranges"][k]) for k in STAT_ORDER], int(r["stat_total_max"]) if isinstance(r["stat_total_max"], int) else 6100


def project_stats(stats, ranges, total) -> list[int]:
    if isinstance(ranges, dict):
        ranges = [tuple(ranges[k]) for k in STAT_ORDER]
    s = [min(max(v, lo), hi) for v, (lo, hi) in zip(stats, ranges)]
    for _ in range(100):
        diff = total - sum(s)
        if diff == 0:
            break
        room = [i for i, (lo, hi) in enumerate(ranges) if (s[i] < hi if diff > 0 else s[i] > lo)]
        if not room:
            break
        step = diff / len(room)
        for i in room:
            lo, hi = ranges[i]
            s[i] = min(max(s[i] + step, lo), hi)
        s = [round(v) for v in s]
    # fix rounding residue on the first stat with room
    diff = total - sum(s)
    for i, (lo, hi) in enumerate(ranges):
        if diff and lo <= s[i] + diff <= hi:
            s[i] += diff
            diff = 0
    return [int(v) for v in s]


# ----------------------------------------------------------------------------- race draw

def draw(seed: int) -> dict:
    """Everything random in a LoH race except my team's build."""
    rng = random.Random(seed * 1_000_003 + 7)
    pool = npc_pool()
    npcs = []
    for j in range(6):
        strat = rng.choice(STRATS)
        kit = rng.choice(pool["kits"][strat])
        stats = [rng.randint(lo, hi) for lo, hi in pool["stat_ranges"]]
        npcs.append({"name": f"NPC{j + 1}", "chara": None, "strategy": strat, "stats": stats, "surface": "A",
                     "distance": rng.choice(["A", "B"]), "style": "A", "unique": None, "skills": list(kit)})
    gates = list(range(12))
    rng.shuffle(gates)
    return {"npcs": npcs, "moods": [rng.randint(-2, 2) for _ in range(12)], "gates": gates,
            "ground": rng.choice(GROUNDS), "weather": rng.choice(WEATHERS), "time": rng.choice(TIMES)}


# ----------------------------------------------------------------------------- request building

_SKILL_CACHE: dict = {}


def _skill_ids(b: dict) -> list[dict]:
    key = (json.dumps(b.get("unique"), sort_keys=True), tuple(b["skills"]))
    if key not in _SKILL_CACHE:
        out = []
        if b.get("unique"):
            uid = C.resolve_skill(b["unique"]["name"], unique=True)
            out.append({"skillId": uid, "level": int(b["unique"]["level"]), "isUnique": True})
        seen = {o["skillId"] for o in out}
        for s in b["skills"]:
            sid = C.resolve_skill(s)
            if sid not in seen:
                out.append({"skillId": sid, "level": 1, "isUnique": False})
                seen.add(sid)
        _SKILL_CACHE[key] = out
    return _SKILL_CACHE[key]


def _horse(b: dict, mood: int, gate: int, team: int) -> dict:
    h = {k: float(v) for k, v in zip(STAT_ORDER, b["stats"])}
    h.update({"strategy": C.canon_strategy(b["strategy"]), "distanceAptitude": b["distance"],
              "surfaceAptitude": b["surface"], "strategyAptitude": b["style"], "mood": mood,
              "gateIndex": gate, "teamId": team, "skills": _skill_ids(b)})
    if b.get("chara") in CHARA:
        h["charaId"] = CHARA[b["chara"]]
    return h


class Matchup:
    """My team vs one opponent team (+ NPCs) on the LoH course."""

    def __init__(self, mine: list[dict], opp: list[dict], world: str = ""):
        assert len(mine) == 3 and len(opp) == 3
        self.mine, self.opp, self.world = mine, opp, world
        self.names = [f"me:{b['name']}" for b in mine] + [f"opp:{b['name']}" for b in opp] + [f"NPC{j}" for j in range(1, 7)]
        self.course_id = C.resolve_course(COURSE)
        self.course = C.course_info(self.course_id)
        self.settings = dict(C.engine_settings())

    def request(self, seed: int, d: dict | None = None) -> dict:
        d = d or draw(seed)
        builds = self.mine + self.opp + d["npcs"]
        teams = [1, 1, 1, 2, 2, 2] + [0] * 6
        horses = [_horse(b, d["moods"][i], d["gates"][i], teams[i]) for i, b in enumerate(builds)]
        used = sorted({s["skillId"] for h in horses for s in h["skills"]})
        table = C.skill_table()
        sd = {}
        for k in used:
            e = table[k]
            sd[k] = {kk: vv for kk, vv in e.items() if kk != "approximated"}
        req = dict(self.settings)
        req.update({"seed": seed, "courseId": self.course_id, "groundCondition": d["ground"], "weather": d["weather"],
                    "season": "Spring", "time": d["time"], "grade": "g1", "horses": horses, "playerHorseIndex": 0,
                    "retainAllFrames": False, "omitFrames": True, "skillData": sd, "dataSignature": "umasim-loh"})
        return req

    def simulate(self, seeds: list[int], workers=None, label: str = "", chunk: int = 3000) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Full telemetry for every runner: placings, spot struggle, duels, skill activation positions."""
        rows, skill_rows = [], []
        for k in range(0, len(seeds), chunk):
            part = seeds[k:k + chunk]
            draws = {s: draw(s) for s in part}
            reqs = [self.request(s, draws[s]) for s in part]
            replies = engine.run_requests(reqs, workers)
            for s, req, rep in zip(part, reqs, replies):
                if "error" in rep:
                    raise engine.EngineError(rep["error"])
                r1, r2 = telemetry(rep, req, draws[s], self, label, s)
                rows += r1; skill_rows += r2
        return pd.DataFrame(rows), pd.DataFrame(skill_rows, columns=SKILL_COLS)


SKILL_COLS = ["label", "world", "seed", "runner", "side", "skill", "t", "pos"]


def telemetry(rep: dict, req: dict, d: dict, m: "Matchup", label: str, s: int):
    """One reply -> runner rows + skill rows. Engine observation logs (duelLog/spotLog/skillPosLog)
    are indexed by gate rank; competitionEvents/results/skillEvents by runner. Map gate -> runner."""
    D = m.course["distance"]
    gates = [h["gateIndex"] for h in req["horses"]]
    g2i = {sorted(gates).index(gates[i]): i for i in range(12)}   # gate rank -> runner
    builds = m.mine + m.opp + d["npcs"]
    duels = {i: [] for i in range(12)}
    for e in rep.get("duelLog", []):
        duels[g2i[e["horseIndex"]]].append(e)
    spots = {i: [] for i in range(12)}
    for e in rep.get("spotLog", []):
        spots[g2i[e["horseIndex"]]].append(e)
    win_t = min(r["finishTimeRaw"] for r in rep["results"])
    rows = []
    for i, r in enumerate(rep["results"]):
        place = r["finishOrder"] + 1
        sp = r.get("lastSpurtStartDistance", -1)
        dl, sl = duels[i], spots[i]
        row = {"label": label, "world": m.world, "seed": s, "idx": i, "runner": m.names[i],
               "side": "mine" if i < 3 else ("opp" if i < 6 else "npc"), "strategy": builds[i]["strategy"],
               "place": place, "points": points(place), "top3": place <= 3, "win": place == 1,
               "p1": place == 1, "p2": place == 2, "p3": place == 3,
               "time": r["finishTimeRaw"], "behind": r["finishTimeRaw"] - win_t,
               "gate": gates[i] + 1, "mood": d["moods"][i], "ground": d["ground"], "weather": d["weather"],
               "time_of_day": d["time"], "start_delay": r.get("startDelayTime", 0.0),
               "late_start": r.get("startDelayTime", 0) > 0.08, "rushed": r.get("rushingStartCount", 0) > 0,
               "spurt_start": sp, "full_spurt": sp >= 0 and sp - D * 2 / 3 <= 5.0, "hp_empty": bool(r.get("hpEmptyOnRace")),
               "duels": len(dl), "dueled": bool(dl),
               "duel_start_pos": dl[0]["pos0"] if dl else None,
               "duel_end_pos": (dl[-1]["pos1"] if dl[-1]["t1"] >= 0 else D) if dl else None,
               "duel_time": sum(((e["t1"] if e["t1"] >= 0 else r["finishTimeRaw"]) - e["t0"]) for e in dl) if dl else 0.0,
               "duel_to_finish": bool(dl) and dl[-1]["t1"] < 0,
               "spot": bool(sl), "spot_start_pos": sl[0]["pos0"] if sl else None,
               "spot_end_pos": sl[-1]["pos1"] if sl and sl[-1]["t1"] >= 0 else None,
               "spot_time": sum((e["t1"] - e["t0"]) for e in sl if e["t1"] >= 0) if sl else 0.0}
        rows.append(row)
    skill_rows = []
    for e in rep.get("skillPosLog", []):
        i = g2i[e["horseIndex"]]
        if i >= 6:
            continue
        skill_rows.append([label, m.world, s, m.names[i], "mine" if i < 3 else "opp",
                           C.skill_names().get(str(e["skillId"]), str(e["skillId"])), e["t"], e["pos"]])
    return rows, skill_rows


def team_score(df: pd.DataFrame, side: str = "mine") -> dict:
    """Team metrics per race averaged over races."""
    x = df[df.side == side]
    per_race = x.groupby("seed").agg(top3_count=("top3", "sum"), pts=("points", "sum"), wins=("win", "sum"))
    return {"races": int(per_race.shape[0]),
            "top3_rate": float(x.top3.mean()),                    # avg over my 3 umas
            "all3_top3": float((per_race.top3_count == 3).mean()),  # sweep of the podium
            "points_per_race": float(per_race.pts.mean()),
            "team_win": float((per_race.wins > 0).mean())}


def per_runner(df: pd.DataFrame, sides=("mine", "opp")) -> pd.DataFrame:
    x = df[df.side.isin(sides)]
    g = x.groupby("runner")
    return pd.DataFrame({"strategy": g.strategy.first(), "top3_pct": 100 * g.top3.mean(), "win_pct": 100 * g.win.mean(),
                         "avg_place": g.place.mean(), "points": g.points.mean(), "full_spurt_pct": 100 * g.full_spurt.mean(),
                         "hp_empty_pct": 100 * g.hp_empty.mean(), "rushed_pct": 100 * g.rushed.mean(),
                         "duel_pct": 100 * (g.duels.apply(lambda s: (s > 0).mean()))}).round(2)
