"""LoH v3 environment: my team vs a *random mock player team* + 6 NPCs, per race.

Per seed (deterministic, so every candidate build faces identical races = paired comparisons):
  * 6 NPCs, moods, ground, weather, time exactly as loh.draw
  * gates: 12 random, but my 3 umas are never in gate 1 (LoH inner-gate opt-out)
  * enemy team: 3 distinct umas from {Kitasan, Ines, Neo, Bourbon}; each takes a random mock build
    (data/loh/mocks.json, the 40-60th percentile builds), then
      - stats re-rolled per stat in MOCK_STATS: with prob P_HEAVY uniform in the 'heavy' sub-range,
        else uniform in the rest of the range
      - 2-3 random non-gold skills dropped, plus one gold with prob P_DROP_GOLD (evolved skills kept)
      - Nimble Navigator never on fronts
My team's stats: game-cost budget, every point above 1200 costs 2 (stat_cost).
"""
from __future__ import annotations

import copy
import json
import random

import numpy as np
import pandas as pd

from . import buildgen as G
from . import catalog as C
from . import engine, esp, loh

UMAS = ["Kitasan Black", "Ines Fujin", "Neo Universe", "Mihono Bourbon"]
# stat: (lo, hi, heavy_lo, heavy_hi)
MOCK_STATS = [(1370, 1520, 1370, 1450),   # speed
              (950, 1170, 1100, 1170),    # stamina
              (1130, 1250, 1220, 1250),   # power
              (850, 1230, 1100, 1230),    # guts
              (1150, 1230, 1200, 1230)]   # wit
P_HEAVY = 0.7
DROP_N = (2, 3)
P_DROP_GOLD = 0.4
FRONT_BANNED = {"Nimble Navigator"}
NO_GATE1 = True
COST_BUDGET = 6700


def stat_cost(stats) -> int:
    """In-game cost: points above 1200 count double."""
    return int(sum(s + max(0, s - 1200) for s in stats))


_MOCKS = None


def mocks() -> dict:
    global _MOCKS
    if _MOCKS is None:
        _MOCKS = {k: [m["build"] for m in v] for k, v in json.loads((loh.DATA / "mocks.json").read_text()).items()}
    return _MOCKS


def roll_stat(rng: random.Random, lo, hi, hlo, hhi) -> int:
    if rng.random() < P_HEAVY:
        return rng.randint(hlo, hhi)
    rest = [(lo, hlo - 1)] if hlo > lo else []
    if hhi < hi:
        rest.append((hhi + 1, hi))
    if not rest:
        return rng.randint(lo, hi)
    a, b = rng.choices(rest, weights=[r[1] - r[0] + 1 for r in rest])[0]
    return rng.randint(a, b)


def mock_runner(rng: random.Random, uma: str) -> dict:
    b = copy.deepcopy(rng.choice(mocks()[uma]))
    b["stats"] = [roll_stat(rng, *r) for r in MOCK_STATS]
    fixed = set(G.EVOLVED.get(uma, []))
    sk = [s for s in b["skills"] if not (b["strategy"] == "Front Runner" and s in FRONT_BANNED)]
    kinds = {s: esp.kind(C.resolve_skill(s)) for s in sk}
    golds = [s for s in sk if kinds[s] == "gold" and s not in fixed]
    others = [s for s in sk if kinds[s] != "gold" and s not in fixed]
    drop = set(rng.sample(others, min(len(others), rng.randint(*DROP_N))))
    if golds and rng.random() < P_DROP_GOLD:
        drop.add(rng.choice(golds))
    b["skills"] = [s for s in sk if s not in drop]
    b["mock_dropped"] = sorted(drop)
    return b


def draw(seed: int) -> dict:
    d = loh.draw(seed)
    rng = random.Random(seed * 7_919 + 13)
    if NO_GATE1:
        g = d["gates"]
        for i in range(3):
            if g[i] == 0:                       # swap gate 1 to a random non-mine runner
                j = rng.randrange(3, 12)
                g[i], g[j] = g[j], g[i]
    d["opp"] = [mock_runner(rng, u) for u in rng.sample(UMAS, 3)]
    return d


class MockMatchup(loh.Matchup):
    """loh.Matchup whose opponent team comes from the per-seed draw."""

    def __init__(self, mine):
        super().__init__(mine, mocks_placeholder(), "mock")

    def request(self, seed, d=None):
        d = d or draw(seed)
        self.opp = d["opp"]
        self.names = [f"me:{b['name']}" for b in self.mine] + [f"opp:{b['name']}" for b in self.opp] + [f"NPC{j}" for j in range(1, 7)]
        return super().request(seed, d)

    def simulate(self, seeds, workers=None, label="", chunk=3000):
        rows, skill_rows = [], []
        for k in range(0, len(seeds), chunk):
            part = seeds[k:k + chunk]
            draws = {s: draw(s) for s in part}
            reqs, names = [], []
            for s in part:
                reqs.append(self.request(s, draws[s])); names.append(list(self.names))
            replies = engine.run_requests(reqs, workers)
            for s, req, rep, nm in zip(part, reqs, replies, names):
                if "error" in rep:
                    raise engine.EngineError(rep["error"])
                self.opp = draws[s]["opp"]; self.names = nm
                r1, r2 = loh.telemetry(rep, req, draws[s], self, label, s)
                rows += r1; skill_rows += r2
        return pd.DataFrame(rows), pd.DataFrame(skill_rows, columns=loh.SKILL_COLS)


def mocks_placeholder():
    return [mocks()[u][0] for u in UMAS[:3]]


# ----------------------------------------------------------------------------- evaluation

_DRAWS: dict = {}


def _draw(s):
    if s not in _DRAWS:
        if len(_DRAWS) > 100_000:
            _DRAWS.clear()
        _DRAWS[s] = draw(s)
    return _DRAWS[s]


def evaluate(teams: dict[str, list[dict]], seeds: list[int], workers=None, chunk: int = 3000) -> pd.DataFrame:
    """Every variant on the same seeds. Rows: variant, seed, p0-p2, top3 (team avg), points, hp_empty, opp_top3."""
    rows, batch = [], []

    def flush():
        replies = engine.run_requests([r for _, r in batch], workers)
        for (key, _), rep in zip(batch, replies):
            if "error" in rep:
                raise engine.EngineError(f"{key}: {rep['error']}")
            res = rep["results"]
            pl = [r["finishOrder"] + 1 for r in res[:3]]
            op = [r["finishOrder"] + 1 for r in res[3:6]]
            rows.append({"variant": key[0], "seed": key[1], "p0": pl[0], "p1": pl[1], "p2": pl[2],
                         "top3": sum(p <= 3 for p in pl) / 3, "points": sum(loh.points(p) for p in pl),
                         "opp_top3": sum(p <= 3 for p in op) / 3,
                         "hp_empty": sum(bool(r.get("hpEmptyOnRace")) for r in res[:3])})
        batch.clear()

    ms = {name: MockMatchup(team) for name, team in teams.items()}
    for s in seeds:
        d = _draw(s)
        for name, m in ms.items():
            batch.append(((name, s), m.request(s, d)))
            if len(batch) >= chunk:
                flush()
    if batch:
        flush()
    return pd.DataFrame(rows)


def batches(x: pd.DataFrame, size: int = 175) -> pd.DataFrame:
    """Split one variant's races (seed order) into consecutive LoH-sized batches."""
    x = x.sort_values("seed").reset_index(drop=True)
    x["batch"] = x.index // size
    g = x.groupby("batch")
    out = pd.DataFrame({"n": g.size(), "team_top3": 100 * g.top3.mean(), "points": g.points.sum(),
                        "pts_per_race": g.points.mean()})
    return out[out.n == size]


def summarize(df: pd.DataFrame, base: str = "base", batch: int = 175) -> pd.DataFrame:
    from . import stats as S
    piv = df.pivot_table(index="seed", columns="variant", values=["top3", "points"])
    out = []
    for v in df.variant.unique():
        x = df[df.variant == v]
        bt = batches(x, batch)
        row = {"variant": v, "top3": 100 * x.top3.mean(), "points": x.points.mean(), "n": len(x),
               "ind0": 100 * (x.p0 <= 3).mean(), "ind1": 100 * (x.p1 <= 3).mean(), "ind2": 100 * (x.p2 <= 3).mean(),
               "hp_empty_per_race": x.hp_empty.mean(),
               "batch_top3_p10": bt.team_top3.quantile(.1) if len(bt) else np.nan,
               "batch_top3_p90": bt.team_top3.quantile(.9) if len(bt) else np.nan}
        if v != base and base in df.variant.values:
            d = S.paired_diff(piv["top3"][base], piv["top3"][v])
            row.update({"d_top3": 100 * d["diff"], "d_top3_lo": 100 * d["lo"], "d_top3_hi": 100 * d["hi"], "p": d["p"]})
            row["d_points"] = S.paired_diff(piv["points"][base], piv["points"][v])["diff"]
        out.append(row)
    return pd.DataFrame(out).sort_values("top3", ascending=False).reset_index(drop=True)
