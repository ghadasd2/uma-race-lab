"""Stage 3: large final validation. Usage: loh_stage3_validate.py N_PER_WORLD NAME=TEAM.json [NAME=TEAM.json ...]
Each team races the same N seeds in the JP world and the CN world. Writes full per-runner tables and a summary."""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pandas as pd
from umasim import loh, opt

n = int(sys.argv[1])
teams = {a.split("=", 1)[0]: json.loads(Path(a.split("=", 1)[1]).read_text()) for a in sys.argv[2:]}
out = opt.run_dir("stage3-validate")
summary = {}
seeds = list(range(7_000_000, 7_000_000 + n))
for name, team in teams.items():
    opt.save_team(out / f"{name}.json", team)
    for w in ("jp", "cn"):
        t0 = time.time()
        frames, skills = [], []
        for k in range(0, n, 10_000):  # chunk to bound memory
            df, sk = loh.Matchup(team, loh.opponent_team(w), w).simulate(seeds[k:k + 10_000], label=name)
            frames.append(df); skills.append(sk)
        df, sk = pd.concat(frames), pd.concat(skills)
        df.to_parquet(out / f"{name}-{w}-runners.parquet") if False else df.to_csv(out / f"{name}-{w}-runners.csv.gz", index=False)
        mine = df[df.side == "mine"]
        summary[f"{name}/{w}"] = {
            "team": loh.team_score(df, "mine"), "opponent_team": loh.team_score(df, "opp"),
            "runners": loh.per_runner(df).reset_index().to_dict("records"),
            "mine_top3_by_mood": (100 * mine.groupby(["runner", "mood"]).top3.mean()).round(1).unstack().to_dict("index"),
            "mine_top3_by_gate": (100 * mine.groupby(["runner", "gate"]).top3.mean()).round(1).unstack().to_dict("index"),
            "mine_top3_by_ground": (100 * mine.groupby(["runner", "ground"]).top3.mean()).round(1).unstack().to_dict("index"),
            "skill_activation_pct": (100 * sk[sk.runner.str.startswith("me:")].groupby(["runner", "skill"]).seed.nunique() / n)
                                    .round(1).unstack(0).fillna(0).to_dict(),
            "seconds": round(time.time() - t0)}
        print(name, w, json.dumps(summary[f"{name}/{w}"]["team"]), flush=True)
(out / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False, default=float))
print("done", out)
