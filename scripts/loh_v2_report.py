"""Full-telemetry validation + report. Usage: loh_v2_report.py N_PER_WORLD NAME=TEAM.json [NAME=TEAM.json ...]
Writes runs/<stamp>-loh-v2-report/: report.md, summary.json, per-runner and skill CSVs."""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import pandas as pd
from umasim import buildgen as G, loh, opt

n = int(sys.argv[1])
teams = {a.split("=", 1)[0]: json.loads(Path(a.split("=", 1)[1]).read_text()) for a in sys.argv[2:]}
out = opt.run_dir("v2-report")
seeds = list(range(20_000_000, 20_000_000 + n))
pct = lambda s: round(100 * float(s.mean()), 1) if len(s) else None
q = lambda s, p: round(float(np.nanpercentile(s, p)), 0) if s.notna().any() else None


def runner_block(x: pd.DataFrame) -> dict:
    d = x[x.dueled]; sp = x[x.spot]
    return {
        "n": len(x), "1st%": pct(x.p1), "2nd%": pct(x.p2), "3rd%": pct(x.p3), "top3%": pct(x.top3),
        "avg_place": round(x.place.mean(), 2), "points": round(x.points.mean(), 1),
        "spot_rate%": pct(x.spot), "spot_start_m": q(sp.spot_start_pos, 50), "spot_end_m_p10/50/90":
            [q(sp.spot_end_pos, 10), q(sp.spot_end_pos, 50), q(sp.spot_end_pos, 90)],
        "spot_len_s": round(sp.spot_time.mean(), 2) if len(sp) else None,
        "top3%_if_spot/else": [pct(sp.top3), pct(x[~x.spot].top3)],
        "duel_rate%": pct(x.dueled), "duels_per_dueling_race": round(d.duels.mean(), 2) if len(d) else None,
        "duel_enter_m_p10/50/90": [q(d.duel_start_pos, 10), q(d.duel_start_pos, 50), q(d.duel_start_pos, 90)],
        "duel_exit_m_p10/50/90": [q(d.duel_end_pos, 10), q(d.duel_end_pos, 50), q(d.duel_end_pos, 90)],
        "duel_len_s": round(d.duel_time.mean(), 2) if len(d) else None,
        "duel_to_finish%": pct(d.duel_to_finish) if len(d) else None,
        "top3%_if_duel/else": [pct(d.top3), pct(x[~x.dueled].top3)],
        "1st%_if_duel/else": [pct(d.p1), pct(x[~x.dueled].p1)],
        "late_start%": pct(x.late_start), "rushed%": pct(x.rushed), "full_spurt%": pct(x.full_spurt),
        "hp_empty%": pct(x.hp_empty), "top3%_by_mood": {int(k): pct(v) for k, v in x.groupby("mood").top3},
        "top3%_by_gate": {int(k): pct(v) for k, v in x.groupby("gate").top3},
    }


def skill_block(sk: pd.DataFrame, x: pd.DataFrame) -> list:
    rows = []
    races = x.seed.nunique()
    for name, g in sk.groupby("skill"):
        first = g.groupby("seed").pos.min()
        fired = x.seed.isin(first.index)
        early = x.seed.map(lambda s: first.get(s, np.inf) <= first.median())
        rows.append({"skill": name, "activation%": round(100 * len(first) / races, 1),
                     "pos_p10": q(first, 10), "pos_median": q(first, 50), "pos_p90": q(first, 90),
                     "spread_m(p10-p90)": (q(first, 90) - q(first, 10)) if len(first) else None,
                     "top3%_fired/not": [pct(x[fired.values].top3), pct(x[~fired.values].top3)],
                     "top3%_early/late_half": [pct(x[(fired & early).values].top3), pct(x[(fired & ~early).values].top3)]})
    return sorted(rows, key=lambda r: r["pos_median"] if r["pos_median"] is not None else 1e9)


summary, md = {}, ["# LoH v2 report (Tokyo 2400, 3v3+6 NPC)\n", f"{n} races per world per team.\n"]
for name, team in teams.items():
    opt.save_team(out / f"{name}.json", team)
    for w in ("jp", "cn"):
        t0 = time.time()
        df, sk = loh.Matchup(team, loh.opponent_team(w), w).simulate(seeds, label=name)
        df.to_csv(out / f"{name}-{w}-runners.csv.gz", index=False)
        sk.to_csv(out / f"{name}-{w}-skills.csv.gz", index=False)
        key = f"{name}/{w}"
        summary[key] = {"team": loh.team_score(df, "mine"), "opponent_team": loh.team_score(df, "opp"),
                        "esp": {b["name"]: G.build_esp(b["skills"]) for b in team},
                        "runners": {r: runner_block(g) for r, g in df[df.side != "npc"].groupby("runner")},
                        "skills": {r: skill_block(sk[sk.runner == r], df[df.runner == r]) for r in df[df.side == "mine"].runner.unique()},
                        "seconds": round(time.time() - t0)}
        tm = summary[key]["team"]
        md.append(f"\n## {key}: team top3 {100 * tm['top3_rate']:.1f}% · points/race {tm['points_per_race']:.1f} · "
                  f"podium sweep {100 * tm['all3_top3']:.1f}% · any win {100 * tm['team_win']:.1f}%\n")
        md.append("| runner | 1st | 2nd | 3rd | top3 | spot% | spot end m | duel% | duel in→out m | duel s | top3 if duel/else | late start | rushed | HP-out |\n|" + "---|" * 14)
        for r, b in summary[key]["runners"].items():
            md.append(f"| {r} | {b['1st%']} | {b['2nd%']} | {b['3rd%']} | {b['top3%']} | {b['spot_rate%']} | {b['spot_end_m_p10/50/90'][1]} | "
                      f"{b['duel_rate%']} | {b['duel_enter_m_p10/50/90'][1]}→{b['duel_exit_m_p10/50/90'][1]} | {b['duel_len_s']} | "
                      f"{b['top3%_if_duel/else'][0]}/{b['top3%_if_duel/else'][1]} | {b['late_start%']} | {b['rushed%']} | {b['hp_empty%']} |")
        print(key, json.dumps(tm), flush=True)
(out / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False, default=float))
(out / "report.md").write_text("\n".join(md))
print("done", out)
