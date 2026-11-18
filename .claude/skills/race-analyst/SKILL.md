---
name: race-analyst
description: Answer Umamusume (Global) race questions by running thousands of GlobalSim simulations with the umasim toolkit, then explaining the trends with statistics and race mechanics. Use for any question about builds, stats, skills, strategies, courses, ground or why a runner wins or loses.
---

# Race analyst

You answer race questions with evidence from simulation, not intuition. The simulator is
GlobalSim v77 (Rust, validated against 696,777 of 696,778 official practice observations) running
the validated v77 runtime profile and the audited v70 skill table. Only **Global** mechanics are
enabled: never turn on `experimentalLaterStaminaMechanics` or other JP-only/experimental switches.

## Loop

1. **Frame** the question as a measurable claim about the *focus* runner, e.g. "Does stamina above
   900 help Mine at Nakayama 2500?" Choose metric(s): win %, avg place, top-3 %, finish time.
2. **Build a scenario** in `scenarios/` (see format below). The rival field matters a lot: if the user
   gives none, build a realistic mixed field and *say what you assumed*. Run `./umasim.sh check` first.
3. **Pick the experiment**:
   - `run`: where do we stand, and what correlates with winning (drivers table).
   - `compare`: A/B/C of concrete changes. Paired on identical seeds and gates, so deltas are precise.
   - `sweep`: one knob across values (stat, strategy, ground, mood, aptitude) for a response curve.
   - `skills`: marginal value of each candidate skill added to the focus runner.
4. **Size it.** Win % standard error ≈ √(p(1−p)/n): n=2000 gives ±1.8 pp at 20%. Paired deltas
   (compare/sweep/skills) are far tighter than that. Throughput is roughly 350–700 races/s, so
   10k races take under 30 s. Start at n=1000–2000 and scale up only when a result is borderline.
5. **Read `findings` first**, then the tables. Drill into `runs/<dir>/runners.csv.gz` and
   `skills.csv.gz` with pandas for anything custom (e.g. win rate by Red Ace activation time bucket).
6. **Explain the mechanism.** Tie every conclusion to a mechanic (below, or
   `vendor/GlobalSim/docs/RACE-MECHANICS.md`, `SKILLS.md` and `MATHEMATICS.md`). Then verify the
   explanation with a follow-up experiment where you can. Example: "the gain stops at 1000 stamina
   because full spurt is already 100%", confirmed by `hp_empty_pct` and `full_spurt_pct` on the curve.
7. **Conclude** with a recommendation, its effect size with CI, the assumptions (field, conditions),
   and what would change the answer.

## Commands

```bash
./umasim.sh check    scenarios/x.json
./umasim.sh run      scenarios/x.json -n 2000 [--frames] [--md]
./umasim.sh compare  scenarios/x.json -n 2000 --variant 'wit1200={"runners.Mine.wisdom":1200}' --variant 'late={"runners.Mine.strategy":"Late Surger"}'
./umasim.sh sweep    scenarios/x.json --path runners.Mine.stamina --values 600:1400:100 -n 1000
./umasim.sh sweep    scenarios/x.json --path ground --values Good,Yielding,Soft,Heavy
./umasim.sh skills   scenarios/x.json -n 1000 --candidates "Corner Adept ○,Swinging Maestro"   # or --query corner --max-cost 200
./umasim.sh courses  tokyo 2400
./umasim.sh skill    recovery --conditions
```
By default output is compact JSON; pass `--md` for a readable report. Every saved run writes
`summary.json`, `report.md` and the raw tables to `runs/`. In Python:
`from umasim import experiments as X; s = X.compare(scn, {...}, n=2000); df, sk = s["_tables"]`.

Change paths: `runners.<Name>.<field>` (stats, strategy, mood, distance/surface/style aptitudes,
skills, unique), top-level `ground` / `weather` / `season` / `course`. Use `runners.<Name>.skills+`
or `skills-` with a list to add or remove skills.

## Scenario format

```json
{"name": "...", "course": "Tokyo 2400" , "ground": "Good", "weather": "Sunny", "season": "Spring",
 "gates": "shuffle", "focus": "Mine",
 "runners": [
   {"name": "Mine", "stats": [1200, 900, 1000, 600, 1000], "strategy": "Pace Chaser", "mood": "Great",
    "distance": "A", "surface": "A", "style": "A", "unique": {"name": "Red Ace", "level": 4},
    "skills": ["Corner Recovery ○", "Swinging Maestro"]},
   {"name": "Rival", "copy": "Mine", "strategy": "End Closer", "count": 3}]}
```
Stats are [Speed, Stamina, Power, Guts, Wit]. `gates: shuffle` draws a random gate per seed
(realistic). Use `fixed` only to isolate gate effects, which also enables a faster batch path.
Unique-skill names resolve to the unique (1xxxx); in `skills` they resolve to the inherited
version (9xxxxx). Field size is 1–18.

## Metric glossary

- `full_spurt_pct`: the last spurt started at the 2/3 point (HP was enough). Below ~95%, stamina-limited.
- `hp_empty_pct`: HP hit zero during the race. Harsh: speed collapses.
- `spurt_delay_m_mean`: how far past the 2/3 point the spurt actually started.
- `rushed_pct`: kakari (rushing). Chance falls with Wit; rushing burns HP faster.
- `late_start_pct`: start delay above 0.08 s.
- `duel_pct`: entered a duel (compete fight, final straight).
- `--frames` only: `hp_left_pct`, `blocked_frac`, `avg_lane`, `rank_mid` and `rank_late` (position when the leader reaches 50% and 66%).
- `drivers`: conditional win rates (if X happened / otherwise), Holm-corrected. **Correlational**:
  a skill that fires "late" may just mark races where the runner was already behind. Confirm
  causal claims with `compare`.
- `lengths_gained`: −Δtime × average speed / 2.5 m (one length ≈ 2.5 m).
- **RNG de-sync / noise floor.** Pairing shares seeds and gates, but any change that alters how the
  engine draws random numbers (adding even a skill that never fires, changing Wit) re-rolls part of
  the race. `skills` reports `noise_floor` from never-firing candidates. In `compare` you can add a
  placebo variant (a skill that can't fire, e.g. another strategy's corner skill) to measure it.
  Effects inside that band are noise. Increase `-n` rather than over-reading them.

## Mechanics cheat-sheet (Global)

- **Speed** sets top speed through the middle phase and the spurt. **Power** sets acceleration and
  helps fight through blocking. **Guts** adds to spurt speed (0.0001·(450G)^0.597), affects HP use in the spurt and helps dueling.
  **Wit** feeds the skill activation lottery for wisdom-checked skills, lowers rushing chance and drives positioning
  decisions. **Stamina** sets max HP (distance and strategy coefficient); enough HP means a full spurt.
- Strategy speed and HP coefficients are in RACE-MECHANICS §4. Pace Chaser uses less HP (0.89) than Late (1.00).
  Front Runner and Runaway are fast early and weaker late.
- Aptitude: distance aptitude scales speed (S 1.05, A 1, B .9, C .8), surface aptitude scales
  acceleration, and strategy aptitude scales Wit.
- Last spurt (§9): the planner checks whether remaining HP affords max speed. If not, it shortens
  in 30 m steps, with a Wit-based lottery ≈ 15 + 0.05·Wit % to accept a plan.
- Stats above 1200 keep only half the excess (overcap). Mood scales base stats by ≈ 1 + 0.02·mood
  (Great = +2 → ×1.04). Ground/weather and Career adjustments are in §3.
- Skills fire only when their conditions match (phase, corner, order rate and so on). A skill with low
  `activation_pct` on this course is dead weight. Look at conditions with `./umasim.sh skill NAME --conditions`.

When the cheat-sheet and the docs disagree, trust `vendor/GlobalSim/docs` and the source.

## Honesty rules

- Report effect sizes with CIs. Say "not significant" when it isn't, and don't call 0.3 pp a trend.
- State the assumed rival field and conditions. Conclusions transfer poorly across fields.
- GlobalSim is unofficial (see ACCURACY.md). Experimental or oversized-field setups are out of validation scope.
- Don't edit engine settings or the skill table to "fix" a surprising result. Investigate it instead.
