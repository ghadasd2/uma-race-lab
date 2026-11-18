"""LoH build optimizer: paired successive halving over team variants, scored against BOTH worlds.

A *variant* is a full my-team (3 builds). All variants in a round race the same seeds (same NPCs,
moods, gates, conditions) in both the JP world and the CN world, so differences are paired.
Score = my team's average top-3 rate (mean over my 3 umas), averaged over the two worlds;
expected points and the per-world numbers are reported alongside.
"""
from __future__ import annotations

import copy
import json
import math
import re
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from . import catalog as C
from . import engine, loh
from . import stats as S

STYLE_CODE = {"Front Runner": 1, "Pace Chaser": 2, "Late Surger": 3, "End Closer": 4}
# Tokyo 2300 turf, left-handed, medium, Spring
FIXED = {"distance_type": 3, "rotation": 2, "season": 1, "ground_type": 1, "track_id": 10006}
_TOK = re.compile(r"^([a-z_]+)(==|!=|>=|<=|>|<)(-?\d+)$")


def _ok(var, op, val, env):
    if var not in env:
        return True
    a = env[var]
    return {"==": a == val, "!=": a != val, ">=": a >= val, "<=": a <= val, ">": a > val, "<": a < val}[op]


def can_fire(sid: str, strategy: str) -> bool:
    """Static check: is any activation alternative satisfiable for this strategy on this course?"""
    env = dict(FIXED, running_style=STYLE_CODE[strategy], is_basis_distance=0)  # 2300 is not a multiple of 400
    for a in C.skill_table()[sid]["alternatives"]:
        for alt in (a["condition"] or "always==1").split("@"):
            toks = [t for t in alt.split("&") if t]
            good = True
            for t in toks:
                m = _TOK.match(t.strip())
                if m and not _ok(m.group(1), m.group(2), int(m.group(3)), env):
                    good = False
                    break
            if good:
                return True
    return False


def group_of(sid: str) -> str:
    return C.skill_meta().get(sid, {}).get("groupId") or sid


def candidate_pool(build: dict, extra_names: list[str], allowed_inherited: list[str]) -> list[str]:
    """Skill names that could be added to `build`: normal skills that can fire, the user's required extras,
    and inherited uniques seen on the top teams. Excludes × (negative) skills, base skills of the build's
    evolutions, other umas' evolved skills and uniques."""
    have = {C.resolve_skill(s) for s in build["skills"]}
    blocked = {C.resolve_skill(loh.EVOLVES_FROM[s]) for s in build["skills"] if s in loh.EVOLVES_FROM
               if _resolvable(loh.EVOLVES_FROM[s])}
    out = []
    for sid in C.skill_table():
        name = C.skill_names().get(sid)
        if not name or sid in have or sid in blocked:
            continue
        normal = sid[0] == "2" and len(sid) == 6
        inh = sid[0] == "9" and name in allowed_inherited
        if not (normal or inh or name in extra_names):
            continue
        if name.endswith("×"):
            continue
        if not can_fire(sid, build["strategy"]):
            continue
        out.append(name)
    for n in extra_names:
        if n not in out and C.resolve_skill(n) not in have:
            out.append(n)
    return sorted(set(out))


def _resolvable(n):
    try:
        C.resolve_skill(n)
        return True
    except ValueError:
        return False


def add_skill(build: dict, name: str) -> dict:
    """Add a skill; if it shares a skill group with one already held (gold <-> white), swap it in."""
    b = copy.deepcopy(build)
    g = group_of(C.resolve_skill(name))
    b["skills"] = [s for s in b["skills"] if group_of(C.resolve_skill(s)) != g] + [name]
    return b


def drop_skill(build: dict, name: str) -> dict:
    b = copy.deepcopy(build)
    b["skills"] = [s for s in b["skills"] if s != name]
    return b


# ----------------------------------------------------------------------------- evaluation

def evaluate(teams: dict[str, list[dict]], seeds: list[int], worlds=("jp", "cn"), workers=None) -> pd.DataFrame:
    """Race every variant on the same seeds in each world. Returns per-(variant, world, seed) team rows."""
    jobs, meta = [], []
    for w in worlds:
        opp = loh.opponent_team(w)
        for name, team in teams.items():
            m = loh.Matchup(team, opp, w)
            for s in seeds:
                jobs.append(m.request(s, _draw(s)))
                meta.append((name, w, s))
    replies = engine.run_requests(jobs, workers)
    rows = []
    for (name, w, s), rep in zip(meta, replies):
        if "error" in rep:
            raise engine.EngineError(f"{name}/{w}/{s}: {rep['error']}")
        res = rep["results"]
        places = [r["finishOrder"] + 1 for r in res[:3]]
        opp_places = [r["finishOrder"] + 1 for r in res[3:6]]
        rows.append({"variant": name, "world": w, "seed": s,
                     "p0": places[0], "p1": places[1], "p2": places[2],
                     "top3": sum(p <= 3 for p in places) / 3, "points": sum(loh.points(p) for p in places),
                     "opp_top3": sum(p <= 3 for p in opp_places) / 3,
                     "hp_empty": sum(bool(r.get("hpEmptyOnRace")) for r in res[:3])})
    return pd.DataFrame(rows)


_DRAWS: dict = {}


def _draw(s):
    if s not in _DRAWS:
        if len(_DRAWS) > 200_000:
            _DRAWS.clear()
        _DRAWS[s] = loh.draw(s)
    return _DRAWS[s]


def summarize(df: pd.DataFrame, base: str = "base") -> pd.DataFrame:
    """Per variant: overall/per-world top3 and points, paired delta vs base with 95% CI."""
    out = []
    piv = df.pivot_table(index=["world", "seed"], columns="variant", values=["top3", "points"])
    for v in df.variant.unique():
        x = df[df.variant == v]
        row = {"variant": v, "top3": 100 * x.top3.mean(), "points": x.points.mean(),
               "top3_jp": 100 * x[x.world == "jp"].top3.mean(), "top3_cn": 100 * x[x.world == "cn"].top3.mean(),
               "pts_jp": x[x.world == "jp"].points.mean(), "pts_cn": x[x.world == "cn"].points.mean(),
               "n": len(x)}
        if v != base and base in df.variant.values:
            d = S.paired_diff(piv["top3"][base], piv["top3"][v])
            row.update({"d_top3": 100 * d["diff"], "d_top3_lo": 100 * d["lo"], "d_top3_hi": 100 * d["hi"], "p": d["p"]})
            dp = S.paired_diff(piv["points"][base], piv["points"][v])
            row.update({"d_points": dp["diff"]})
            for w in ("jp", "cn"):
                if (w, ) and w in df.world.values:
                    dw = S.paired_diff(piv["top3"][base].loc[w], piv["top3"][v].loc[w])
                    row[f"d_top3_{w}"] = 100 * dw["diff"]
        out.append(row)
    return pd.DataFrame(out).sort_values("top3", ascending=False).reset_index(drop=True)


def halving(teams: dict[str, list[dict]], n0: int = 300, keep: float = 0.34, rounds: int = 3, grow: int = 3,
            seed_base: int = 10_000, log=print, out_dir: Path | None = None, min_keep: int = 3) -> pd.DataFrame:
    """Successive halving. 'base' is always kept as the paired reference. Seeds differ per round."""
    alive = dict(teams)
    n = n0
    hist = []
    for r in range(rounds):
        seeds = list(range(seed_base + r * 1_000_000, seed_base + r * 1_000_000 + n))
        t0 = time.time()
        df = evaluate(alive, seeds)
        summ = summarize(df)
        summ["round"] = r
        hist.append(summ)
        el = time.time() - t0
        log(f"round {r}: {len(alive)} variants x {n} seeds x 2 worlds = {len(df)} races in {el:.0f}s")
        if out_dir:
            summ.to_csv(out_dir / f"round{r}.csv", index=False)
        if r == rounds - 1:
            break
        others = summ[summ.variant != "base"]
        k = max(min_keep, math.ceil(len(others) * keep))
        survivors = list(others.head(k).variant)
        alive = {v: alive[v] for v in ["base"] + survivors}
        n *= grow
    return pd.concat(hist, ignore_index=True)


# ----------------------------------------------------------------------------- run folders

def run_dir(name: str) -> Path:
    d = C.ROOT / "runs" / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-loh-{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_team(path: Path, team: list[dict]):
    path.write_text(json.dumps(team, indent=1, ensure_ascii=False))
