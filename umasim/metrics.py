"""Turn engine replies into tidy tables (pandas).

runners table: one row per (seed, runner)
skills table:  one row per skill activation
"""
from __future__ import annotations

import pandas as pd

from . import catalog as C

LATE_START_S = 0.08      # start delay above this is shown in-game as a late start
FULL_SPURT_TOL_M = 5.0   # spurt start within this of the 2/3 point counts as a full spurt


def tables(compiled, seeds: list[int], replies: list[dict], variant: str = "base"):
    D = compiled.course["distance"]
    spurt_point = D * 2 / 3
    names = compiled.names
    rows, skill_rows = [], []
    for seed, rep in zip(seeds, replies):
        res = rep["results"]
        win_time = min(r["finishTimeRaw"] for r in res)
        duels = [0] * len(res)
        for e in rep.get("competitionEvents", []):
            if e["type"] == 5:
                duels[e["horseIndex"]] += 1
        fx = _frame_metrics(rep, D) if "frames" in rep else None
        gates = compiled.gate_order(seed)
        for i, r in enumerate(res):
            place = r["finishOrder"] + 1
            sp = r.get("lastSpurtStartDistance", -1)
            row = {
                "variant": variant, "seed": seed, "runner": names[i], "gate": gates[i] + 1,
                "strategy": C.STRATEGY_EN.get(C.RUNNING_STYLE_CODE.get(r.get("runningStyle")), "?"),
                "place": place, "win": place == 1, "top3": place <= 3,
                "time": r["finishTimeRaw"], "behind": r["finishTimeRaw"] - win_time,
                "start_delay": r.get("startDelayTime", 0.0),
                "late_start": r.get("startDelayTime", 0.0) > LATE_START_S,
                "spurt_start_m": sp, "spurt_delay_m": (sp - spurt_point) if sp >= 0 else None,
                "full_spurt": sp >= 0 and sp - spurt_point <= FULL_SPURT_TOL_M,
                "hp_empty": bool(r.get("hpEmptyOnRace")),
                "rushed": r.get("rushingStartCount", 0) > 0,
                "duels": duels[i],
            }
            if fx:
                row.update(fx[i])
            rows.append(row)
        for e in rep.get("skillEvents", []):
            sid = str(e["skillId"])
            if sid == "kakari":   # rushing is reported as a pseudo-skill; it's already in `rushed`
                continue
            skill_rows.append({"variant": variant, "seed": seed, "runner": names[e["horseIndex"]],
                               "skill_id": sid, "skill": C.skill_names().get(sid, sid),
                               "t": e["t"], "duration": e.get("duration")})
    runners = pd.DataFrame(rows)
    skills = pd.DataFrame(skill_rows, columns=["variant", "seed", "runner", "skill_id", "skill", "t", "duration"])
    return runners, skills


def _frame_metrics(rep: dict, D: float) -> list[dict]:
    frames = rep["frames"]
    n = len(rep["results"])
    out = []
    lead_pos = [max(h["pos"] for h in f["horses"]) for f in frames]

    def rank_when_leader_at(frac):
        k = next((j for j, p in enumerate(lead_pos) if p >= D * frac), len(frames) - 1)
        pos = [h["pos"] for h in frames[k]["horses"]]
        order = sorted(range(n), key=lambda i: -pos[i])
        return {i: order.index(i) + 1 for i in range(n)}

    r_mid, r_late = rank_when_leader_at(0.5), rank_when_leader_at(2 / 3)
    for i in range(n):
        running = [f["horses"][i] for f in frames if f["horses"][i]["pos"] < D]
        hp0 = frames[0]["horses"][i]["hp"] or 1.0
        hp_end = running[-1]["hp"] if running else 0.0
        out.append({
            "hp_left": hp_end, "hp_left_pct": 100 * hp_end / hp0,
            "blocked_frac": sum(h["blockFrontHorseIndex"] >= 0 for h in running) / max(1, len(running)),
            "avg_lane": sum(h["lane"] for h in running) / max(1, len(running)),
            "rank_mid": r_mid[i], "rank_late": r_late[i],
        })
    return out
