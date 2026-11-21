# Changelog

All notable changes to the project: code, rules, data and results. Newest first.
Each entry names the step from `docs/MASTER_PROMPT.md` it belongs to (v4 onward).

## v4 — new rules, weaker mocks, full re-run (track A done; engine 2 pending)

### 2026-11-21 — X2 Ignited Spirit WIT side effects (pace down, blocking, hurt rate)
- Engine observation patch: `posKeepLog` (position-keep mode changes with gap to pacemaker), in both the retail
  and legacy solvers; observation only, results byte-identical (checked on 500 races); applies to the pinned commit.
- `scripts/loh_v4_x2_ignited_wit_effects.py 17500 5000`, `loh_v4_x2_analyze.py` → `data/loh/results/v4/X2/`.
- Pace down: tiny increase (+0.012 s per race; extra entry in 0.73 %). Blocking: more early front blocks (window
  27.7 % vs 21.2 % of races), none extra after 400 m. Hurt: Neo lower in 9.2 % of races vs higher in 14.6 %; top 3
  lost 1.5 % vs gained 2.4 %.
- X1 notes corrected: the lane-move speed bonus that runs is in `retail_physics.rs` (retail runtime), same formula.

### 2026-11-21 — X1 Ignited Spirit WIT on Neo (extra analysis)
- `scripts/loh_v4_x1_ignited_wit.py 17500 2500`, `loh_v4_x1_analyze.py`, `loh_v4_x1_example.py` →
  `data/loh/results/v4/X1/`. Counterfactual skill clones (same lottery, changed effects) isolate the mechanism.
- Neo top-3 +0.86 [0.57, 1.15], team +0.27 [0.14, 0.40]. All of it comes from the lane-move effect's target-speed
  bonus (+√(0.0002·P) ≈ 0.49 m/s while changing lanes); the +5 m vision is inert in this engine.

### 2026-11-21 — A9 v4 results summary (track A done)
- `scripts/loh_v4_a9_tables.py` → `docs/reports/v4_results.md`: every A2–A8 table (numbers only, run folders,
  seeds), the stamina requirements in words, and the two readings of the HP floor. Regenerate it rather than
  editing it by hand; it is the input for the engine-2 cross-check.

### 2026-11-21 — A8 validation
- `scripts/loh_v4_a8_validate.py 17500` (seeds 190M) → `data/loh/results/v4/A8/` (summary, batch
  distribution, per-batch files, races, log, telemetry).
- Champion 96.31 % and the only team meeting the HP floor (1.38 / 1.17 / 1.15 %); base 96.17 % fails on Ines
  (1.76 %); v3 champion 96.22 % fails (3.23 / 4.58 %); CN 96.05 %. Champion − base +0.14 [−0.07, 0.36].
- HP-outs per 175-race batch follow the binomial model; the per-batch reading of the floor would need ≤ 0.78 %.

### 2026-11-21 — A7 constrained build search
- `scripts/loh_v4_a7_search.py 8 30 1500` (8 generations, ~123k races each). Outputs `data/loh/results/v4/A7/`.
- Accepted only Kitasan + Hesitant Front Runners (+0.43 [0.13, 0.74], 9,000 races). Champion saved as
  `data/loh/my_team_v4_champion.json`. No other candidate cleared lo > 0 in gens 1–7.
- Drain skills tested under the real skill cap and ESP (with stamina from A4) gave ≈ 0: Neo RS + Keep Going!
  @ 1200 −0.01 [−0.32, 0.30].

### 2026-11-21 — A6 skill values and front accel test
- `scripts/loh_v4_a6_skill_values.py` (129 variants × 4,000 races + accel test 3 × 6,000; 544k races).
  `scripts/loh_v4_skill_table.py` → `data/loh/results/v4/A6/skill_table.csv`.
- Accel: Solid Preparation (Kitasan) and Solid Preparation + Taking the Lead (Ines) beat every other legal set
  by 0.43–0.92 pp. New skills: Ines Racing Spirit: Speed +0.68, Downhill Speedster +0.54; Neo Keep Going! +1.09,
  Full Throttle +0.84 (both need stamina 1100 for the HP floor). Killer Tunes on Ines (optional) +0.62.
- `scripts/loh_v4_a7_search.py`: robust skill repair (`force_set`) and hypotheses from A4/A6.

### 2026-11-20 — A5 stat exchange rates
- `scripts/loh_v4_a5_exchange.py` (61 variants × 4,000 races, seeds 103M) → `data/loh/results/v4/A5/`.
- Speed 0.15–0.22 pp per 100 cost; power and wit above 1200 0.16–0.49 (as good as or better than speed in
  the weak field); guts ≈ 0; stamina ≤ 0.15.
- Ines at 1150 stamina measured 1.95 % HP-out here (floor 1.71 %): added
  `data/loh/my_team_v4_a7_start.json` (Ines 1355/1200/1245/1200/1200) as the search start.

### 2026-11-20 — A4 stamina requirement study
- `scripts/loh_v4_a4_stamina.py` (138 variants × 2,500 races, seeds 102M, resumable). Results:
  `data/loh/results/v4/A4/stamina.csv`, `requirements.csv`.
- Lowest floor-meeting stamina: Kitasan 1200 with no drain skills, no drain set feasible up to 1350;
  Ines none 1100, RS 1150, MD 1200, RS+MD > 1350; Neo none 1000, RS / Full Throttle / Keep Going! 1100,
  RS+FT / RS+KG 1200. Best value: Neo RS + Keep Going! at 1200 (+0.99 pp vs no drain at 1000).
- Guts 1000–1250: no measurable effect on placements or duels.

### 2026-11-20 — remote
- Pushed the full history to https://github.com/ghadasd2/uma-race-lab (private), branch `master`.

### 2026-11-20 — A3 v4 base team
- `scripts/loh_v4_a3_base.py` → `data/loh/my_team_v4_base.json`: the v3 champion with stamina raised
  (paid by speed) until each uma meets the HP-out floor on 3,500 races: Kitasan 1380/1200/1230/1175/1200,
  Ines 1380/1150/1245/1200/1200, Neo 1450/1000/1250/1200/1200. HP-out 1.17 / 1.60 / 1.63 %; team
  top-3 96.17 % (96.25 % before the fix).

### 2026-11-20 — A2 mock recalibration
- `scripts/loh_v4_a2_calibrate.py`: 39-setting grid (stat shift 0–300 × stamina shifted/kept × extra
  drops 0–2, 1,750 races each, seeds 100M) and a confirm of the 3 closest settings on 8,750 races
  (seeds 100.5M). Results: `data/loh/results/v4/A2/`.
- Chosen: `MOCK_STAT_SHIFT=150`, `SHIFT_STAMINA=True`, `EXTRA_DROP=2` → CN team 96.00 % team top-3.
  Under it: v3 champion 96.29 %, v3 base 94.86 %; v3 champion breaks the HP-out floor (Kitasan
  3.15 %, Ines 4.41 %).

### 2026-11-20 — A1 rules and pool
- Skill pool 56 → 61: Downhill Speedster, Racing Spirit: Wit, Racing Spirit: Speed (fronts only);
  Full Throttle and Keep Going! (Neo only). `Speed Star` not added: Pace-Chaser-only.
- `umasim/buildgen.py`: front start-accel rule (`front_accel_ok`, `legal_accel_sets`) enforced in
  `valid` and in random build generation. Kitasan's legal sets are {Groundwork} and {Solid
  Preparation}: Taking the Lead is the base of her evolved Introducing the Victor!.
- `umasim/mock.py`: per-uma HP-out columns (`hp0`–`hp2`) in `evaluate`; `summarize` reports per-uma
  HP-out %, its 95 % Wilson upper bound and `hp_ok`; helpers `hp_ok`, `hp_status`, `wilson_ub`;
  recalibration knobs `MOCK_STAT_SHIFT`, `SHIFT_STAMINA`, `EXTRA_DROP` (defaults = v3 field).
- `data/loh/rules.json`: `v4` block. `tests/test_v4_rules.py` (5 tests).

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
