# uma-race-lab

Turns [GlobalSim](https://github.com/daftuyda/GlobalSim) (the engine behind umaeclipse.com's race
simulation) into a numbers-only Monte Carlo lab that an AI agent (Claude Code) can drive at scale:
thousands of seeded races per question, paired A/B comparisons, parameter sweeps, skill rankings,
and auto-generated statistical findings.

```
question ─▶ scenario.json ─▶ umasim (parallel GlobalSim workers) ─▶ per-race tables ─▶ stats + findings ─▶ agent explains
```

## Setup

```bash
./setup.sh          # clones + builds GlobalSim (needs Rust), installs pandas/numpy
python3 -m pytest -q tests
```

## Use it as an agent

Open this folder in Claude Code and just ask, e.g.:

> "My Pace Chaser in `scenarios/example-arima.json`: is 1000 stamina enough, and which corner skill should I buy with 180 SP?"

The `race-analyst` skill (`.claude/skills/race-analyst/SKILL.md`) tells Claude how to design
experiments, size them, read the stats, tie results to mechanics and report honestly.

## Use it directly

```bash
./umasim.sh run      scenarios/example-arima.json -n 2000 --md
./umasim.sh compare  scenarios/example-arima.json --variant 'late={"runners.Mine.strategy":"Late Surger"}' --md
./umasim.sh sweep    scenarios/example-arima.json --path runners.Mine.stamina --values 700:1300:100 --md
./umasim.sh skills   scenarios/example-arima.json --query corner --max-cost 200 --md
./umasim.sh courses  tokyo
./umasim.sh skill    "swinging" --conditions
```

| experiment | what it answers |
|---|---|
| `run` | Win/top-3/place distribution for every runner, stamina and spurt health, rushing, skill activation rates and timing, gate effects, and **drivers**: what correlates with the focus runner winning |
| `compare` | Named variants on identical seeds and gates. Paired deltas with 95% CI and Holm-corrected p |
| `sweep` | One knob over many values. Response curve, plateau and threshold detection |
| `skills` | Marginal win%, lengths and per-SP value of each candidate skill, with an RNG noise floor |

Accuracy: GlobalSim v77 reports 696,777 of 696,778 official practice observations matched in its
validated profile, which is what umasim uses (see `vendor/GlobalSim/docs/ACCURACY.md`). It is
unofficial, and results depend on the rival field you assume.

## Credits and licenses

- Engine: GlobalSim, © Void (daftuyda) and contributors, AGPL-3.0-only. Used unmodified via its JSON-lines worker.
- English skill and track names (`data/names/`): from [alpha123/uma-tools](https://github.com/alpha123/uma-tools), GPL-3.0.
