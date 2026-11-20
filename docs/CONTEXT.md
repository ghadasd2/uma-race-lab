# Project context — League of Heroes (LoH) team building on GlobalSim

This file is the durable memory of the project. It records the user's goals and rules, every
decision, and every result so far, so that work can resume after a context reset without guessing.
**If something is not written here, in `CHANGELOG.md`, in `docs/PROGRESS.md` or in a committed data
file, treat it as unknown — re-derive it from data or ask; never fill the gap from memory.**

Last updated: 2026-11-20 (start of v4).

---

## 1. Goals

### Original goal
An agent wired to the GlobalSim race simulator (the backend of umaeclipse's race sim) that runs
thousands of sims, compiles and explains the data, finds trends and draws conclusions.
**Global mechanics only** (no JP-only/experimental engine switches).

### Real goal: League of Heroes
- **Race:** Tokyo 2400 m (Tokyo Yushun), Spring, left-handed, standard, 12 runners.
- **Field:** my 3 umas + an enemy team of 3 + 6 NPCs.
- **Random per race:** gates, mood, ground, weather, time of day.
- **Scoring:** 1st 100, 2nd 60, 3rd 40, 4th 30, 5th 20, 6th–12th 10.
- **Goal metric:** team-average top-3 % (mean of the 3 umas' top-3 rates), reported in **175-race
  batches** (one LoH run). Also track LoH points. The CN winning team averaged **97.1 %** team
  top-3 across their 175 real LoH races.
- **Deliverables so far:** research report v3 (`docs/reports/v3_research_report.md`, also a Claude
  Docs artifact https://claude.ai/artifact/Xftfw2TfzecGim9ygrGxdX).

### My team (the user's umas)
| Slot | Uma | Style | Notes |
| --- | --- | --- | --- |
| 0 | New Year Kitasan Black [真打・慶鶴之志] | Front Runner | evolved: Introducing the Victor! (start accel, +0.5 m/s² 12000 base dur, `always==1`), Leap Ahead to the Future |
| 1 | Valentine Ines Fujin [MELTY GIFT] | Front Runner | evolved: Perfect ♪ Order Up! (start delay ×0.4 + all stats), Slick Serving (corners speed+accel) |
| 2 | Neo Universe [Universe-Naut] | Late Surger | evolved: Beyond the Stars with You, Cross the Sea of Stars |

- Unique level 6, distance S, style A.
- 22–23 skills including the unique (MAX_SKILLS = 23), at most 3 inherited.
- Skill points (ESP) 4500–4600, **full basis** (a gold includes its white; ◎ includes ○; evolved =
  base gold + white; own unique 0).
- Realistic skill pool only: `data/loh/skill_pool.json` (built by `scripts/loh_skill_pool.py`).

---

## 2. User rules (cumulative — all still in force unless marked superseded)

### Skills
- Killer Tunes: disabled in generation; allowed only for Ines in a dedicated test (never Kitasan).
- Concentration: never on Kitasan.
- Nimble Navigator: never on any front (Neo only).
- Solid Preparation allowed for both fronts. All I've Got and With All My Soul added to the pool.
- **v4 additions (2026-11-20):**
  - Front pool: Downhill Speedster (the user wrote "downhill speed star"; `Speed Star` is a
    Pace-Chaser-only gold and cannot fire for fronts), Racing Spirit: Wit, Racing Spirit: Speed.
  - Late pool (Neo): Full Throttle (white, 202152) and its gold Keep Going! (202151). These replace
    Mad Dash in Neo's stamina-drain tests (Mad Dash is Front-Runner-only).
  - **Front start-accel rule:** every front must carry Groundwork (white) **and** at least one gold
    or evolved starting-acceleration skill. Solid Preparation is Groundwork's gold (it includes
    Groundwork), Taking the Lead is a separate gold (its white is Early Lead), Kitasan's evolved
    Introducing the Victor! is a start accel. So legal sets are:
    - Ines: {Groundwork + Taking the Lead}, {Solid Preparation}, {Solid Preparation + Taking the Lead}.
    - Kitasan: {Groundwork}, {Solid Preparation}. Introducing the Victor! (her evolved skill) already
      supplies the gold/evo start accel, and it evolved from Taking the Lead, so she cannot buy TtL.
    - Never Taking the Lead without the Groundwork family.

### Stats
- Stat cost budget **6400**; every point above 1200 costs 2 (`stat_cost = Σ s + max(0, s−1200)`).
  (The user first said 6700, then corrected to 6400.)
- User's realistic target was ~1430 / 1100 / 1200 / 1200 / 1200.
- Stat box used (never confirmed by the user, proposed by me):
  Spd 1350–1500, Sta 950–1250, Pow 1100–1250, Guts 1000–1250, Wit 1100–1250.
  v4 widens stamina to 950–1350 for the stamina study only.
- **v4 stamina floor (2026-11-20):** my umas must NOT run out of HP (stam out) in more than
  **3 of 175 races (≤ 1.71 %) each**. This applies to every stamina-related test and to all data
  collection: a build that violates it is infeasible. Stamina-drain conclusions must be stated as
  "you need X stamina to get value out of skill(s) Y".

### Race environment
- My umas never draw gate 1 (only my umas are excluded from gate 1).
- Mock enemy team: 3 distinct umas from {Kitasan, Ines, Neo, Bourbon}, each from a random mock build
  in `data/loh/mocks.json` (43 Kitasan, 40 Ines, 42 Neo, 14 Bourbon builds).
- Mock stats rolled per stat with p=0.7 in the "heavy" sub-range:

  | Stat | Range | Heavy (70 %) |
  | --- | --- | --- |
  | Speed | 1370–1520 | 1370–1450 |
  | Stamina | 950–1170 | 1100–1170 |
  | Power | 1130–1250 | 1220–1250 |
  | Guts | 850–1230 | 1100–1230 |
  | Wit | 1150–1230 | 1200–1230 |
- Mock skills: drop 2–3 random non-gold skills + one gold with p=0.4; evolved skills kept.
- Mock distance aptitude: S with 70 %, else A. Nimble Navigator stripped from mock fronts.
- **v4 (2026-11-20):** keep the same mock logic but weaken mocks (stats, maybe 1–2 more skill
  drops) until the **CN team scores 95–97 % team top-3** against them.

### Process rules (v4)
- Push everything to git; keep a changelog; follow `docs/MASTER_PROMPT.md` step by step with a
  commit after every step.
- After v4 on GlobalSim, the user will supply a **second engine**. Re-run the same tests on it with
  the same inputs, then write a cross-verification report (correlations, differences, theory using
  both engines and the game-mechanics doc).
- No generated character art (charts/diagrams only; user screenshots may be used if uploaded).
- Privacy: never put the user's email or personal details in commits, URLs or external requests.
- umaeclipse.com, gametora.com and docs.google.com are blocked by the network here.

---

## 3. Method (how every number is produced)

- Engine: GlobalSim Rust JSON-lines worker `race_engine_rs_v2`, v77 settings, v70 skill table plus
  legacy skills converted to the same shape (`approximated` flag). Pinned engine commit
  `80b54cacf174b54ff6f7ca27ee7f88b5856c0bd1` of https://github.com/daftuyda/GlobalSim, plus the
  observation-only patch `data/globalsim-observation.patch` (adds `duelLog`, `spotLog`,
  `skillPosLog`, indexed by gate rank; map with `g2i = {sorted(gates).index(gates[i]): i}`).
- **Paired common random numbers:** a seed fixes the whole race (gates, mood, conditions, NPCs,
  enemy team), so every variant faces identical races. Fresh seed blocks per study/round; final
  checks on unseen seeds. Successive halving for searches; paired-difference 95 % CIs.
- Seed blocks used so far: 50M (v3 calib), 51M (exchange), 52M (skill values), 53M (stamina/duel),
  60M+g·1M (search gen g), 90M (v3 validation). **v4 uses 100M+ (see MASTER_PROMPT).**
- Noise: adding a never-firing skill still moves results by up to ±0.8 pp (RNG desync). Speed and
  stamina deltas have tight CIs (~±0.12 pp at 6000 races); wit/guts/power ~±0.5 pp.
- Wit skill-activation lottery: max(0.2, 1 − 90/Wit) → 92.5 % at 1200, 91.8 % at 1100; uniques skip it.
- Engine mechanics confirmed in source (`vendor/GlobalSim/src/race_solver_builder.rs`):
  - Raw stats above 1200 count at half in the race: `1200 + (raw − 1200)/2`. Green skill stat
    bonuses are applied on top (full value).
  - Power > 1200 enables conserve-power (asitame) late release; coefficient at medium distance:
    Front 0.75, Pace 0.7, Late 0.875, End 1.0.
  - Stamina > 1200 "stamina syoubu" exists only as an experimental switch (disabled — Global).
- Key code: `umasim/mock.py` (environment, `evaluate`, `summarize`, `batches`, `stat_cost`),
  `umasim/loh.py` (race model, telemetry), `umasim/buildgen.py` (legal builds, `valid`, `mutate`),
  `umasim/esp.py` (skill costs), `umasim/catalog.py` (skill lookup, cached `resolve_skill`).

---

## 4. Results history

### v1 (vs real CN and JP teams; stages 1–3)
Optimized skills then stats against the actual CN/JP builds. Superseded: those opponents carry
24–26 skills and ESP up to 4990 (beyond LoH rules), so the field was unwinnable to a degree that
hid differences.

### v2 (realistic pool vs CN/JP)
- Skill search gave +1.8 pp (Ines only changed). Stats validated on fresh seeds: Kitasan
  [1500, 1000, 1250, 1150, 1200], Ines [1500, 1000, 1225, 1175, 1200] → +1.86 pp (CI 1.42–2.30).
  Team 44.4 % → 48.0 %.
- Late starts ~20 % for Kitasan and Neo; Kitasan loses 12 pp top-3 when it happens.
- User then pivoted to mock opponents.

### v3 (vs random mock teams; 6400 budget; ~2.5 M races)
**Calibration:** CN team 79.8–79.9 %, my base 77.1–78.0 %. 175-race batch p10–p90 ≈ ±2.5 pp; points
per batch ≈ 31,200–31,700. Weakness probes (pre-70 %-S spec): distance A +7.7 pp to the field;
unique level barely matters; 8 more skills dropped → my team ≈ 95.8 %; stats −200 → ≈ 95.9 %.

**Stat exchange rates** (pp team top-3 per 100 cost points, around 1430/1100/1200/1200/1200;
cut / add):

| Stat | Kitasan | Ines | Neo |
| --- | --- | --- | --- |
| Speed | 0.45 / 0.39 | 0.47 / 0.38 | 0.55 / 0.50 |
| Stamina | 0.27 / 0.10 | 0.23 / 0.13 | 0.05 / 0.01 |
| Power | 1.38 / 0.34 | 1.40 / 0.19 | 2.11 / 0.75 |
| Guts | 1.07 / −0.04 | 0.73 / −0.26 | 0.77 / 0.07 |
| Wit | 1.46 / −0.10 | 1.16 / −0.24 | 1.71 / 0.20 |

**Skill values** (4,000 paired races; full table `data/loh/results/v3_skill_table.csv`):
- Ines without TtL+SP −12.4 pp team (−50 own); SP only −4.8; TtL only −2.8; SP→Groundwork −0.97.
- Kitasan Groundwork→SP +1.63 (0.90–2.36); Kitasan dropping Groundwork −2.81.
- Top adds: Kitasan Hesitant FR +1.2, Professor +1.07, Restraint +0.93; Ines Superb Gait +1.45,
  Hesitant FR +1.12, Restraint +0.78; Neo Professor +1.62, LS Corners ◎ +1.34, Groundwork +1.24,
  Medium Straightaways ◎ +1.09.
- Dead weight: Ines Playtime's Over!, Tail Held High, Uma Stan; Neo Be Still; Kitasan Front Runner
  Savvy ○, Standard Distance ○. Late inherited skills (Moving Past, Into High Gear, Bring on the
  Banquet) never fire for fronts.
- ◎ greens (+60 stat) are worth 1.4–1.9 pp — more than 100 raw speed above 1200.

**Stamina × drain skills** (2,500 races per point, cost-neutral via speed; **no HP-out floor then**):
- Kitasan: RS:Stamina + Mad Dash peaks at stamina 1200 (79.08 vs none 78.03, own 84.1 vs 80.4);
  Mad Dash alone needs ≥ 1150; RS alone fine from 1000. MD at 950 → 83 % HP-out.
- Ines: RS + MD peaks at 1100–1150 (+1.9 pp; own 86.7 vs 81.4) despite 29 % HP-out at 1100.
- Neo: lowest stamina always best; RS ≈ +1 pp; MD adds ~nothing.
- HP-out % (none / RS+MD) at 950, 1100, 1200: Kitasan 30/94, 3/63, 1/29; Ines 7/83, 1/29, 1/6.
- Duels: length +~0.3 s per 50 stamina (Kitasan 14.0 → 15.4 s, 950 → 1250); draining skills
  shorten duels 1–2 s; entry ≈ 1927 m fronts, 2075 m Neo, independent of stats. Top-3 when dueling
  85–92 %.
- Guts 1000–1250 traded for speed: no measurable change in placements, duel rate/length/entry.
  Spot Struggle 9.6 s → 10.5 s from guts 1000 → 1250 (Kitasan in one 75 %, Ines 85 %).

**Build search** (8 generations, `scripts/loh_v3_search.py`): accepted gen 0 (Neo sta 1000, pow
1250, +RS +1.25), gen 1 (Neo Ignited Spirit WIT for RS; Kitasan SP for Groundwork + FR Savvy ○,
+0.93), gen 2 (Ines Hesitant FR for Playtime's Over!; Kitasan 25 guts→power, +1.35), gen 6 (Ines 50
stamina→power, +0.40). Kitasan RS+MD @1200 dropped in the first cut and was never retested.

**v3 champion** (`data/loh/my_team_v3_champion.json`):
- Kitasan 1430/1100/1230/1175/1200, 21 skills; Ines 1430/1050/1245/1200/1200, 23 skills;
  Neo 1450/1000/1250/1200/1200, 23 skills.

**Validation** (17,500 unseen races, seeds 90M): champion 81.64 % (+3.63 [3.25, 4.01] vs start),
CN team 79.89 %, start 78.02 %. Points/batch 32,182 vs 31,720 vs 31,497. Batches ≥ 80 %: 90 / 49 / 9
of 100. Per uma (champion): top-3 Kitasan 84.0, Ines 84.0, Neo 77.0; **HP-out Kitasan 3.1 %, Ines
4.9 %, Neo 1.7 %** (Kitasan and Ines would violate the v4 floor); late start 19.4 / 1.7 / 19.9 %;
mood −2 → +2 ≈ 65–74 → 86–93 %; ground/weather < 1.5 pp; Neo −5 pp in gates 2–3.

---

### v4 (in progress — see docs/PROGRESS.md for each step)
- A2 mock recalibration (grid 39 settings × 1,750 races; confirm 8,750 races, seeds 100.5M):
  chosen setting → CN 96.00 % (batches ≥ 95 %: 94 %, ≥ 97.1 %: 8 %; 34,620 pts/batch); my v3 champion
  96.29 %, v3 base 94.86 %. HP-out under the new field: v3 champion Kitasan 3.15 %, Ines 4.41 %,
  Neo 1.49 % (fails the floor); CN team 4.31 / 1.79 / 6.15 %.
- A3 v4 base (`data/loh/my_team_v4_base.json`, 3,500 races, seeds 101M): v3 champion skills; stamina
  raised cost-neutrally until the floor held: Kitasan 1380/1200/1230/1175/1200, Ines
  1380/1150/1245/1200/1200, Neo unchanged 1450/1000/1250/1200/1200. HP-out 1.17 / 1.60 / 1.63 %
  (status marginal: point estimates pass, upper bounds don't at 3,500 races). Team top-3 96.25 → 96.17 %.

## 5. Open questions / leads
- Kitasan RS + Mad Dash at 1200 stamina vs the final team (dropped early in v3 search).
- Killer Tunes on Ines (never tested).
- Second engine: not yet provided by the user.

## 6. Where things are
| What | Where |
| --- | --- |
| Rules (machine-readable) | `data/loh/rules.json` (`v3`, `v4` blocks) |
| Skill pool | `data/loh/skill_pool.json/.csv` ← `scripts/loh_skill_pool.py` |
| Teams | `data/loh/my_team_v3_base.json`, `my_team_v3_champion.json`, `cn_team.json`, `jp_team.json` |
| Mock builds | `data/loh/mocks.json` |
| Archived small run outputs | `data/loh/archive/<run>/` (runs/ itself is git-ignored) |
| Curated results | `data/loh/results/` |
| Reports | `docs/reports/` |
| Plan and progress | `docs/MASTER_PROMPT.md`, `docs/PROGRESS.md`, `CHANGELOG.md` |
