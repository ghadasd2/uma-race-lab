# Changelog

All notable changes to the project: code, rules, data and results. Newest first.
Each entry names the step from `docs/MASTER_PROMPT.md` it belongs to (v4 onward).

## v4 — new rules, weaker mocks, full re-run (in progress)

### 2026-11-20 — A0 housekeeping
- Added `docs/CONTEXT.md` (full project memory), `docs/MASTER_PROMPT.md` (step-by-step protocol),
  `docs/PROGRESS.md` (step checklist), this changelog.
- Archived small outputs of every LoH run into `data/loh/archive/` (runs/ is git-ignored).
- Exported the v3 research report to `docs/reports/v3_research_report.md`.
- Recorded new user rules for v4 (see CONTEXT §2): pool additions (Downhill Speedster, Racing
  Spirit: Wit, Racing Spirit: Speed for fronts; Full Throttle / Keep Going! for Neo), HP-out floor
  ≤ 3/175 races per uma, front start-accel rule (Groundwork + one gold/evo start accel), mock
  recalibration to CN team 95–97 %, second engine and cross-verification to follow.

## v3 — random mock opponents, 6400 stat budget

### 2026-11-19
- `50e5594` Per-skill effect and value table (`data/loh/results/v3_skill_table.csv`,
  `scripts/loh_v3_skill_table.py`); v3 research report published.
- `06bfa22` Champion team (`data/loh/my_team_v3_champion.json`), search history and unseen-seed
  validation (`scripts/loh_v3_validate.py`): champion 81.64 % vs CN 79.89 % vs start 78.02 %.
- `7f8ea25` Iterative whole-team build search (`scripts/loh_v3_search.py`, 8 generations).
- `b91f124` Stamina × draining skills and guts telemetry study (`scripts/loh_v3_stamina_duel.py`).
- `0c59060` v3 base team (target stats 1430/1100/1200/1200/1200; Ines Nimble Navigator →
  Playtime's Over!), skill value study script.
- `5743d38` 6400 stat-cost budget (points > 1200 cost 2), mock distance S 70 % / A 30 %, stats study.
- `9c281b5` Mock-opponent environment (`umasim/mock.py`): gate-1 opt-out for my umas, skewed stat
  rolls, skill drops; stat cost model; pool rules (no Nimble Navigator on fronts, no Killer Tunes
  on Kitasan); calibration probes.

## v2 — realistic skill pool vs CN/JP teams

### 2026-11-18
- `08a656a` Stat check on fresh seeds; final v2 team with tuned stats (+1.86 pp).
- `a38ba98` Realistic-pool skill optimization results, mock builds, telemetry report script.
- `06e3bda` Realistic pool pipeline, engine observation patch (duels, spot struggle, skill
  positions), telemetry, anchors, mocks.
- `b2ab686` Solid Preparation added, Killer Tunes disabled, ESP range, realistic build generator.
- `fdf5d76` ESP accounting and realistic Front/Late skill pool.

## v1 — optimizer vs CN/JP teams

### 2026-11-18
- `d49f265` Final optimized team (stages 1–3).
- `c46a9d4` Global-only assembly mode. `e5718b8` Chunked evaluation, skill assembly script.
- `753890c` Course fixed to Tokyo 2400 (Tokyo Yushun). `8969709` LoH race model, team data,
  extended skill table, optimizer and stage scripts.

## v0 — lab

### 2026-11-17
- `4cab9cb` umasim: Monte Carlo race analysis lab on GlobalSim with analyst agent skill.
