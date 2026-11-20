# Master prompt — LoH v4 (GlobalSim) → engine 2 → cross-verified report

Paste this (or "follow docs/MASTER_PROMPT.md") to start or resume work. It is the single source of
truth for **what to do next and how**. Results live in files, never in chat memory.

---

## 0. Start-up procedure (every session, every resume, every time context was compressed)

1. `cd /home/user/src/uma-race-lab` (or wherever the repo is cloned) and `git pull`.
2. If `vendor/GlobalSim` is missing or not built, run `./setup.sh` (pins engine commit
   `80b54ca`, applies `data/globalsim-observation.patch`, builds release).
3. Read, in order: `docs/CONTEXT.md` → `docs/PROGRESS.md` → the top of `CHANGELOG.md` →
   `git log --oneline | head -20`.
4. Find the first step in `docs/PROGRESS.md` that is not `done`. If it is `running`, check whether
   its run finished (`runs/<stamp>-<name>/log.txt`, the `done` line) before restarting anything.
5. Do that step exactly as written below. Then do the step's **commit checkpoint**.
6. Never quote a number in chat or in a report that is not in a committed file or a run output you
   just read. If a number is needed and missing, re-run or say it is missing.

## 1. Commit checkpoint (after every step, and mid-step for anything longer than ~1 hour)

1. Copy the run's small outputs (CSV/JSON/TXT, no `*.gz`, each < 3 MB) to
   `data/loh/results/v4/<step-id>/` (engine 2: `data/loh/results/e2/<step-id>/`).
2. Update `docs/PROGRESS.md`: status `done`, run folder, commit, and a one-line key result.
3. Add a `CHANGELOG.md` entry under the current version (date, step id, what changed, key numbers).
4. If a rule or decision changed, update `docs/CONTEXT.md` (§2 rules, §4 results).
5. `git add -A data docs scripts umasim tests CHANGELOG.md CLAUDE.md` and commit:
   `v4 <step-id>: <what>` (body: key numbers; end with the attribution lines the session requires).
6. `git push` (retry up to 4 times with backoff on network errors). If no remote exists yet, say so
   once and keep committing locally.

## 2. Fixed definitions (do not change without the user)

| Item | Definition |
| --- | --- |
| Race | Tokyo 2400 m, Spring, left-handed, 12 runners: my 3 + enemy 3 (mocks) + 6 NPCs |
| Per race random | gates, mood, ground, weather, time of day; my umas never gate 1 |
| Scoring | 100 / 60 / 40 / 30 / 20 / 10 (6th–12th) |
| Goal metric | team top-3 % (mean of my 3 umas), plus LoH points; report 175-race batches |
| Stat cost | Σ s + max(0, s − 1200) ≤ **6400** per uma |
| Stat box | Spd 1350–1500, Sta 950–1250 (stamina study: up to 1350), Pow 1100–1250, Guts 1000–1250, Wit 1100–1250 |
| Skills | realistic pool only; ≤ 23 incl. unique; ≤ 3 inherited; ESP 4500–4600 full basis |
| Banned | Killer Tunes (generation; Ines-only test allowed), Concentration on Kitasan, Nimble Navigator on fronts |
| **Front start-accel rule** | each front carries Groundwork or Solid Preparation **and** ≥ 1 gold/evo start accel (Taking the Lead, Solid Preparation, Kitasan's Introducing the Victor!) |
| **HP-out floor** | each of my umas runs out of HP in **≤ 3/175 races (1.71 %)**. Builds over it are infeasible. Report the 95 % upper bound too; call a build "marginal" if the point estimate passes but the upper bound does not |
| Stamina language | "You need X stamina to get value out of skill(s) Y" = the lowest stamina (50-step grid) at which the HP-out floor holds **and** the skill set beats no-drain at the same in-game cost |
| Paired testing | identical seeds for all variants of a comparison; 95 % paired CIs; effect is real when the CI excludes 0 |
| Noise floor | ±0.8 pp for single-skill changes; don't call effects under ~0.5 pp unless the CI says so |

## 3. Seed blocks (never reuse a block for a different purpose)

| Step | Seeds |
| --- | --- |
| A2 mock calibration | 100,000,000 + |
| A3 base team | 101,000,000 + |
| A4 stamina study | 102,000,000 + |
| A5 exchange rates | 103,000,000 + |
| A6 skill values | 104,000,000 + |
| A7 search, generation g | 110,000,000 + g·1,000,000 (+ round·100,000) |
| A8 validation | 190,000,000 + (unseen by every other step) |

Engine 2 (track B) uses **the same seeds and the same inputs** as the matching A step so results
pair across engines.

## 4. Track A — v4 on GlobalSim

### A0 Housekeeping — context to git
CONTEXT, CHANGELOG, MASTER_PROMPT, PROGRESS; archive v1–v3 small outputs; export the v3 report;
push. *Checkpoint.*

### A1 Rules and pool
- `scripts/loh_skill_pool.py`: add Downhill Speedster, Racing Spirit: Wit, Racing Spirit: Speed
  (fronts only); Full Throttle and Keep Going! (Neo only). Regenerate the pool.
- `umasim/buildgen.py`: enforce the front start-accel rule in `valid` (and therefore in `mutate`,
  `random_skills`).
- `umasim/mock.py`: `evaluate` records per-uma HP-out (`hp0`–`hp2`); `summarize` reports per-uma
  HP-out % and its 95 % upper bound; helper `hp_ok(df)` implements the floor.
- `data/loh/rules.json`: `v4` block with every rule above.
- Tests in `tests/` for the accel rule, stat cost and HP floor helper. *Checkpoint.*

### A2 Mock recalibration (CN team 95–97 %)
- Keep the mock logic. Add two knobs to `umasim/mock.py`: `MOCK_STAT_SHIFT` (subtracted from every
  range bound; variant: stamina kept or shifted) and `EXTRA_DROP` (0–2 more non-gold skills).
- Grid with the CN team as "my team": shift 0…−300 by 50 × extra drop 0/1/2 (both stamina variants
  for the shift), 3,500 races per setting (20 batches). Fit, then confirm the chosen setting on
  8,750 fresh races. Target team top-3 **96 %** (accept 95–97 %), smallest change wins; prefer
  keeping mock stamina when tied.
- Record the setting in `mock.py`, `rules.json` (`v4.mocks`), CONTEXT. Also report my v3 base and v3
  champion under the new mocks (team top-3, HP-out per uma). *Checkpoint.*

### A3 v4 base team
- Start from the v3 champion. Check the front rule. Raise stamina (paid by speed) on any uma that
  breaks the HP floor, 50 at a time, on 3,500 races, until it passes. Save
  `data/loh/my_team_v4_base.json`. *Checkpoint.*

### A4 Stamina requirement study (the core new deliverable)
- Per uma, cost-neutral (speed pays/refunds), stamina 950 → 1350 step 50, skill sets:
  - Fronts: none, Racing Spirit: Stamina, Mad Dash, RS:Stamina + Mad Dash.
  - Neo: none, RS:Stamina, Full Throttle, Keep Going!, RS:Stamina + Full Throttle,
    RS:Stamina + Keep Going!.
  - Guts 1000 / 1100 / 1200 / 1250 at the v4 base (duel telemetry).
- 2,500 races per point (enough to estimate HP-out near 1.7 % to ±0.5 pp). Full telemetry: HP-out,
  full spurt, duel rate/length/entry, spot struggle, top-3 when dueling.
- Output table: for each skill set, **minimum stamina that meets the floor**, value (pp team top-3 and
  own top-3) at that stamina vs no-drain at equal cost, and the best feasible stamina.
- Efficiency: skip stamina points below the first feasible one only after one probe confirms it fails.
  *Checkpoint.*

### A5 Stat exchange rates
- At the v4 base: each uma × each stat ± 50 / ± 100 (as v3), 4,000 races each. Flag variants that
  break the HP floor. Report pp per 100 cost, cut vs add. *Checkpoint.*

### A6 Skill values and front accel test
- At the v4 base, 4,000 races: drop-one (non-evolved), add-one, tier swaps, including the five new
  skills. Front accel test, legal sets only: Ines {GW + TtL, SP, SP + TtL}; Kitasan {GW, SP} (TtL is the base of
  her evolved Introducing the Victor!); 6,000 races. Optional, clearly labelled: Killer Tunes on Ines.
- Rebuild the per-skill table (`scripts/loh_v3_skill_table.py` → v4): SP, effect, m/s per 100 SP,
  speed × time, team pp [CI], own pp, pp per 100 SP, HP-out change. *Checkpoint.*

### A7 Constrained build search
- `scripts/loh_v3_search.py` → v4: candidates must pass `valid` (incl. front rule) and the HP floor.
  Rounds 0 and 1 drop candidates whose HP-out > 2.5 % (lenient, small samples); the final round
  requires the floor on 9,000 races. Gen 0 hypotheses come from A4–A6 (best feasible stamina/drain
  combos, top adds, accel sets). 8 generations, ~30 candidates, halving 1,500 → 4,500 → 9,000.
- Efficiency from v3 theory: stat moves of 25/50; skill adds weighted by A6 values; gen 0 seeded with
  the A4/A6 winners. (A proposed prune "never raise power/wit/guts above 1200 while another is below"
  was dropped: the v3 search accepted Kitasan guts 1175 → power 1230.)
  *Checkpoint after every 2 generations* (search state saved in history.csv and champion files).

### A8 Validation
- 17,500 unseen races (100 batches): v4 champion, v4 base, v3 champion, CN team. Team top-3, points,
  batch distribution (P ≥ 90 / 95 / 97.1 %), per-uma placements, **HP-out per uma vs the floor**,
  late starts, mood/gate/ground breakdowns, duel/spot telemetry. *Checkpoint.*

### A9 v4 results summary
- `docs/reports/v4_results.md`: every table needed for the cross-check, numbers only, with run
  folders. Update CONTEXT §4. *Checkpoint + push.* Then tell the user track A is done and ask for
  engine 2.

## 5. Track B — engine 2 (after the user provides it)

### B1 Intake and adapter
- Record the engine (source, version/commit, licence, how to run) in CONTEXT and
  `docs/engine2.md`. Do not modify its mechanics; observation-only patches must be saved as
  `data/<engine>-observation.patch`.
- Write `umasim/engines/<name>.py` exposing the same contract as GlobalSim's worker: one request per
  race (runners with stats/skills/style/apt/mood/gate, course, conditions, seed) → finish order,
  HP-out flag, and duel/spot/skill-activation logs if the engine has them. Map every input field;
  list fields the engine ignores or lacks.
- Parity smoke test: 5 fixed scenarios, compare finish-time scales and HP-out behaviour to GlobalSim;
  document mismatches. *Checkpoint.*

### B2 Same tests, same inputs
- Re-run A2 (CN team vs the **same** mock setting — do not recalibrate; report the CN rate),
  A3 check, A4, A5, A6, A7, A8 with identical seeds, teams and variants. Results go to
  `data/loh/results/e2/<step-id>/`. Same commit checkpoints (`e2 <step-id>: ...`).

## 6. Track C — cross-verification and final report

### C1 Analysis
For each test, pair every variant's effect across engines:
- Pearson and Spearman correlation of effects (pp deltas), sign agreement rate, slope of engine 2 on
  GlobalSim, mean absolute difference, Bland–Altman bias and limits.
- Flag disagreements whose CIs don't overlap; explain each from mechanics (GlobalSim docs
  `vendor/GlobalSim/docs/RACE-MECHANICS.md`, MATHEMATICS, SKILLS, FIELD-MECHANICS, and engine 2's
  docs). Mark conclusions as **confirmed** (both engines agree), **engine-dependent**, or
  **contradicted**. *Checkpoint.*

### C2 Final document
- A research document like v3 (Claude Docs artifact, charts not character art): summary, method,
  mocks, stats, dueling/stamina/guts with the HP-floor stamina requirements, skills with pp and m/s
  per SP, front accel verdict, search + validation, practical building guide (goal builds,
  substitutes), and a cross-verification section with correlations and differences.
- Export it to `docs/reports/` as markdown. *Checkpoint + push.*

## 7. Efficiency rules (from v1–v3 theory)
- Reuse seed blocks within a comparison; never compare variants run on different seeds.
- Use successive halving for anything with > 10 variants and only a winner needed.
- Tight-CI quantities (speed, stamina) need fewer races than power/wit/guts/skills.
- Don't test what can't fire (`opt.can_fire`).
- Keep each background job under ~1 hour and save outputs incrementally, so a container restart
  loses at most one chunk; long jobs must be resumable from their output files.
