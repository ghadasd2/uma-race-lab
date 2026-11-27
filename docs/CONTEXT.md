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
- A4 stamina requirement study (2,500 races per point, seeds 102M, cost-neutral via speed; files
  `data/loh/results/v4/A4/`). Lowest stamina meeting the HP-out floor (point estimate):

  | Uma | none | RS:Stamina | Mad Dash / Full Throttle / Keep Going! | RS + MD / FT / KG |
  | --- | --- | --- | --- | --- |
  | Kitasan | 1200 (1.32 %) | > 1350 (1.72 % at 1350) | MD > 1350 (2.64 % at 1350) | > 1350 (9.5 % at 1350) |
  | Ines | 1100 (1.16 %) | 1150 (1.32 %) | MD 1200 (1.60 %) | > 1350 (2.04 % at 1350) |
  | Neo | 1000 (0.92 %) | 1100 (0.96 %) | FT 1100 (0.96 %), KG 1100 (0.76 %) | RS+FT 1200 (0.48 %), RS+KG 1200 (0.64 %) |

  Value at that stamina vs the best feasible no-drain build (team top-3 pp, no CI — skill adds carry
  ~±0.5–0.8 pp RNG noise): Ines RS +0.01, MD +0.13; Neo RS +0.08, FT +0.53, KG +0.69, RS+FT +0.69,
  RS+KG +0.99. Kitasan has no feasible drain set ≤ 1350. Above the requirement every set loses value
  as stamina rises (speed paid). Duels (none set): rate 30–36 % Kitasan, 35 % Ines, 16–22 % Neo;
  top-3 when dueling 97–99 %; length +~0.3 s per 50 stamina; entry 1927 m fronts, ~2080 m Neo. Guts
  1000–1250 (cost-neutral): team top-3 within ±0.3 pp, duel rate/length unchanged; Spot Struggle
  9.5 → 10.3 s. Late start: Kitasan 20.8 %, Neo 20.4 %, Ines 1.3 %.
- A5 stat exchange rates at the v4 base (4,000 races per variant, seeds 103M; `data/loh/results/v4/A5/`).
  Base on these seeds: team 95.97 %, HP-out 1.20 / **1.95** / 1.25 % — Ines at 1150 stamina sits on the
  floor (1.32–1.95 % across seed blocks); Ines +50 stamina → 1.52 % and +0.08 pp [0.03, 0.12].
  In the weak field every rate is smaller (team near 96 %). pp per 100 cost (cut −50/−100 → add +50/+100):
  speed 0.15–0.22; stamina ≤ 0.15; guts ≈ 0 (all CIs span 0); power below 1200 0.2–0.5, above 1200
  +0.16–0.49 (Kitasan +50 pow 0.49 [0.18, 0.81]; Neo +50 pow 0.31); wit cut 0.17–0.57, wit above 1200
  +0.16–0.37 (Kitasan +50 0.30, Ines +50 0.37). Unlike v3, power and wit above 1200 are worth as much as
  or more than speed per cost point in this field.
- A6 skill values at the v4 base (4,000 races per variant, seeds 104M; accel test 6,000 races, seeds 104.5M;
  `data/loh/results/v4/A6/`, per-skill table `skill_table.csv` with SP, m/s per 100 SP, pp per 100 SP, own HP-out).
  Base on these seeds: 95.88 %, HP-out 1.23 / 1.52 / 1.52 %. Effects are smaller than v3 (ceiling near 96 %);
  most single-skill CIs are ±0.45 pp.
  - Front accel test (legal sets): Kitasan Groundwork instead of SP −0.43 [−0.75, −0.11]; Ines GW + TtL −0.56
    [−0.91, −0.21], SP only −0.92 [−1.30, −0.53] → keep SP (Kitasan) and SP + TtL (Ines). Holding SP is worth
    1.65 pp on Ines and 1.12 pp on Kitasan; TtL 0.70 pp on Ines.
  - New skills: Ines Racing Spirit: Speed +0.68 [0.25, 1.12], Downhill Speedster +0.54 [0.09, 0.99], RS: Wit
    +0.22 (ns); Kitasan RS: Speed +0.32, Downhill +0.12, RS: Wit +0.12 (all ns); Neo Keep Going! +1.09 [0.66,
    1.53] and Full Throttle +0.84 [0.40, 1.28] but at stamina 1000 Neo then runs out of HP in ~10 % (A4: they
    need 1100).
  - Other adds with CI > 0: Ines In Body and Mind +0.83, Prudent Positioning +0.67, Superb Gait +0.64, Wisdom of
    the Sun +0.63, Operation Cacao +0.61, Straightaway Adept +0.48; Kitasan Hesitant FR +0.63, Tail Held High
    +0.48, Professor +0.46; Neo Medium Straightaways ◎ +0.88, straightaway whites +0.73, Professor +0.65, LS
    Corners ◎ +0.61, In Body and Mind +0.61, Groundwork +0.47, Prudent Positioning +0.47.
  - Optional: Killer Tunes on Ines +0.62 [0.19, 1.06].
  - Holding values with CI > 0: Neo 1,500,000 CC 0.93, Superb Gait 0.65, Uma Stan 0.60, Divine Speed 0.53,
    ◎ greens 0.43, Restraint 0.36; Ines Taking the Lead 0.70, Red Shift 0.68, ◎ greens 0.32; Kitasan ◎ Left-Handed
    0.30, Red Shift 0.46 (borderline).
- A7 start team `data/loh/my_team_v4_a7_start.json` (used by scripts/loh_v4_a7_search.py) = v4 base with Ines stamina 1200 / speed 1355 (so the
  search starts from a team that meets the floor).
- A7 constrained build search (run runs/20261121-002043-loh-v4-a7-search; `data/loh/results/v4/A7/`): 8
  generations × 30 candidates + base, successive halving 1,500 → 4,500 → 9,000 races (seeds 110M + g·1M),
  HP floor enforced in the final round, accept only if lo > 0. Only gen 0 accepted: **Kitasan + Hesitant Front
  Runners +0.43 [+0.13, +0.74]** (9,000 races). Gens 1–7 kept the champion (best: Neo Straightaway Adept for
  Slick Surge +0.29 [−0.01, +0.58]; Ines Operation Cacao for All I've Got +0.19; Neo LS Straightaways ○ for
  Slick Surge +0.17; Kitasan 25 sta → guts +0.15; Kitasan Playtime's Over! for Ramp Up +0.11).
  Champion = `data/loh/my_team_v4_champion.json`: Kitasan 1380/1200/1230/1175/1200 (A3 base + HFR, ESP 4560),
  Ines 1355/1200/1245/1200/1200 (ESP 4550), Neo 1450/1000/1250/1200/1200 (ESP 4600), base kits otherwise.
  Drain skills under the real skill cap / ESP (they must replace a skill, stamina paid from speed):
  Neo RS + Keep Going! @ 1200 −0.01 [−0.32, +0.30] (9,000 races), Neo FT @ 1100 +0.36, KG @ 1100 +0.22,
  RS + FT @ 1200 −0.07 (1,500 races, eliminated); FT / KG at Neo's 1000 stamina +0.3–0.7 but 8–15 % HP-out
  (fail). The A4/A6 values (+0.5 to +1.1) were measured adding on top of a full kit, so they overstate what
  the skills are worth once something has to be dropped. Ines RS: Speed −0.04 / −0.24 / −0.31 when it
  replaces a skill (A6 +0.68 on top); Downhill Speedster on Kitasan −0.05 for Slipstream (9,000 races).
  Halving caveat: round 0 (1,500 races) CIs are ±0.7 pp, so true effects ≤ 0.3 pp can be dropped early;
  e.g. Kitasan Tail Held High +0.89 in round 0 → −0.26 in round 1 (regression to the mean).
- A8 validation (runs/20261121-014012-loh-v4-a8-validate; `data/loh/results/v4/A8/`): 17,500 unseen races
  (seeds 190M, 100 batches). Team top-3 / HP-out % (Kitasan, Ines, Neo) / status:
  champion 96.31 % / 1.38, 1.17, 1.15 / **ok**; v4 base 96.17 % / 1.38, **1.76**, 1.29 / fail (Ines at 1150);
  v3 champion 96.22 % / **3.23, 4.58**, 1.31 / fail; CN team 96.05 % / 4.33, 2.13, 6.00 (target 95–97 % ✓).
  Champion − base +0.14 [−0.07, +0.36] (the A7 +0.43 shrank on fresh seeds: selection effect). P(batch ≥ 95 %)
  97 % for champion and base, P(≥ 97.1 %) 19 % vs 15 %. Points 198.09 per race (34,665 per batch).
  Champion per uma: top-3 Ines 97.0, Kitasan 96.7, Neo 95.2; late start Kitasan 20.0 %, Neo 20.0 %, Ines 1.6 %
  (top-3 after a late start −2 to −4 pp); duel rate 38 / 33 / 18 % (top-3 when dueling 98.6 / 97.8 / 96.1);
  Neo worse from inner gates (2–3: 93.6 %, 10–12: 96.0 %); mood −2 → +2 spans ~4.5–7 pp; ground and weather ≤ 1 pp.
  HP floor readings: batches with > 3 HP-outs match the binomial prediction (e.g. champion Kitasan 21 % observed
  vs 22.5 % predicted), so HP-outs are independent across races. The rate reading (≤ 3/175 on average) is
  what every step used; a per-batch reading ("never more than 3 in a given 175") would need a rate ≤ 0.78 %
  for 95 % of batches (≤ 1.00 % for 90 %), i.e. more stamina than any v4 build carries — not studied yet.

- X1 (extra) why Ignited Spirit WIT helps Neo (runs/20261121-035126-loh-v4-x1-ignited-wit; `data/loh/results/v4/X1/`;
  scripts `loh_v4_x1_ignited_wit.py`, `loh_v4_x1_analyze.py`, `loh_v4_x1_example.py`). Skill 210052 (white, 200 SP,
  wit-checked, random point in phase 0 = 0–400 m, 9.6 s): lane move speed +0.015 and vision +5 m. Method: clones of the
  skill with the same lottery/condition but changed effects, so races are identical until it fires (clone = full in
  100 % of 17,500 races; no-fire races identical to 0 s). Outcomes vs the no-effect clone (17,500 races, seeds 195M):
  team top-3 +0.27 [0.14, 0.40], Neo top-3 +0.86 [0.57, 1.15], points +0.15/race. Vision only +0.01 (inert: overtake
  targets must be 1–20 m ahead, so 20 → 25 m vision adds none). Lane effect only = the whole value. Mechanism (engine
  retail_physics.rs — the v77 profile runs the retail runtime; same rule in race_solver.rs; mechanics doc v77): while a type-28 skill is active, each tick after lane movement gets target speed
  + √(0.0002·P) ≈ +0.49 m/s for Neo. Frames (2,500 races, seeds 195.5M): fired 91.7 % (wit check 1 − 90/W ≈ 92.5 %),
  at 2–392 m (median 184); Neo moves lanes 3.2 s of the 9.6 s window (4.2 s without: faster lateral speed ends the
  move sooner), mean speed +0.10 m/s, +0.96 m by window end, +1.04 m 10 s later, rank −0.25 at 1600 m, finish −0.044 s.
  Gain ∝ time spent moving (corr 0.75, 0.33 m per moving second); early fire (0–200 m) +1.3 m vs 300–400 m +0.5 m;
  Neo top-3 gain by gate 2–3 +0.59, 4–6 +0.30, 7–9 +0.97, 10–12 +1.47 (outer gates move inward more). A bonus-only
  clone (lane +0.0001) is worth more (+0.43 team, +1.42 Neo) because slower lateral movement means more bonus ticks.
  Example seed 195501125 (gate 11): fires at 69 m, Neo reaches the rail ~4 s sooner at +0.49 m/s, +3.25 m by 350 m,
  finishes 2nd vs 4th. Removing the skill (A6-style drop) is noisier because the RNG stream changes: −0.32 [−0.53, −0.10].

- X2 (extra) side effects of Ignited Spirit WIT on Neo (runs/20261121-075514-loh-v4-x2-ignited-wit-effects;
  `data/loh/results/v4/X2/`; scripts `loh_v4_x2_ignited_wit_effects.py`, `loh_v4_x2_analyze.py`). Engine observation
  patch now also logs position-keep mode changes (`posKeepLog`, indexed by gate like duelLog; retail runtime in
  race_solver_retail.rs); verified byte-identical results. Paired full vs no-effect clone, 17,500 races (seeds 195M)
  + 5,000 dense-frame races (seeds 195.5M). Placebo (HP +0.01 %) leaves Neo's place unchanged in 99.99 %.
  Position keep (0–1000 m): Neo starts every race in pace down (field bunched at the gate, gap ~0.26 m), 3.4 s on
  average, and never enters it after the skill window. The skill lengthens pace down by +0.012 s per race (+0.038 s
  when it fires while the opening pace down is still running, 18.5 % of races) and adds a second entry in 0.73 % of
  races (−1 in 0.10 %); pace-up time −0.044 s (she is closer to the pacemaker). Rough give-back ≈ 0.05 m of the
  ~1 m gained. Engine rules: the lane-move bonus is added after the pace coefficient and does not count as a speed
  skill for the pace-down check; pace down needs no wit roll, pace up does.
  Blocking: during the window blocked +0.093 s and 27.7 % vs 21.2 % of races see a front block (she runs up behind
  runners sooner); opening 0–400 m +0.11 s, 37.7 % vs 33.0 %; middle, late and final phases unchanged (−0.04, −0.01,
  0.00 s, all CIs span 0); whole race +0.065 s.
  Hurt cases: Neo finishes lower in 9.22 % of races, higher in 14.61 %, same 76.17 %; loses top 3 in 1.51 %, gains in
  2.37 %; team top-3 count down 2.83 % / up 3.62 %; points down 3.40 % / up 4.23 %. In hurt races the skill still
  gained 1.24 m by the window end; causes (5,000-race frames, first match): 52 % ahead at 1600 m but lost later,
  27 % blocked ≥ 0.5 s more after 400 m, 12 % worse at 1600 m, 6.6 % behind at window end, 2.4 % more pace down.
  Only 2.4 % of fired races end the window behind. Outer gates reshuffle more both ways (10–12: lower 11.4 %,
  higher 20.7 %); top-3 lost is flat at 1.4–1.6 % across gates.

- X3 (extra) niche skill tests on Neo (runs/20261126-191610-loh-v4-x3-neo-skills; `data/loh/results/v4/X3/`;
  scripts `loh_v4_x3_neo_skills.py`, `loh_v4_x3_analyze.py`). v4 champion, only Neo's kit changes; 17,500 paired races
  per variant (seeds 197M). Break the Mold condition fixed from the in-game page (order_rate>=40, legacy had >=50) via
  new `data/loh/skill_overrides.json` (applied in catalog.skill_table(); no runner held it before, so earlier results are
  unchanged); Beautiful Form (gold) still has the legacy >=50, unverified. Team top-3 vs base (Neo top-3):
  add on top — Condor's Fury (inh.) +0.47 [0.27, 0.68] (+1.15), Latch On +0.47 [0.26, 0.67] (+1.07), RS: Power +0.34
  [0.14, 0.55] (+0.86), Break the Mold +0.33 [0.12, 0.54] (+0.98), Pedal to the Metal +0.14 [−0.07, 0.35] (+0.22).
  Swap for Slick Surge — Condor's +0.28 [0.07, 0.49] (+0.77; +20 SP → ESP 4620), Latch On +0.16 [−0.05, 0.37],
  Break the Mold +0.14 [−0.08, 0.35], RS: Power −0.01, Pedal −0.18 [−0.40, 0.04] (Neo −0.61). Slick Surge itself
  worth +0.26 [0.05, 0.48] on these seeds (A6 had −0.27 ns). Slot value (swap − drop Slick Surge): Condor's +0.55,
  Latch On +0.43, Break the Mold +0.40, RS: Power +0.25, Pedal +0.09 (ns). Firing (Neo): Latch On 93 % at ~1214 m,
  Break the Mold 91 % at 1376–1588 m (3rd corner), Condor's 91 % at ~1626 m (final-corner entry), Pedal 66 % at
  1876–2291 m (needs ≤ 10 m from the leader), RS: Power 70 % at ~2002 m. HP-out: base 1.22 %; adding a late
  skill on top raises it to 1.55–1.61 % (marginal), swaps stay ok (≤ 1.48 %).

- X4 (extra) more Neo skills, same script/seeds as X3 (`--skills/--drop` options; run
  runs/20261126-200217-loh-v4-x4-neo-skills; `data/loh/results/v4/X4/`). Base and drop-Slick-Surge identical to X3
  (96.26 / 96.00 %), so X3 and X4 are directly comparable. Holding Into High Gear! (inh., already in Neo's kit) is worth
  team +0.73 [0.52, 0.95], Neo +2.26, points +0.43 (fires 85 % at ~1500 m). Add on top / swap for Slick Surge (team):
  Triumphant Pulse (inh.) +0.44 [0.23, 0.64] / +0.09, Barcarole of Blessings (inh.) +0.39 [0.18, 0.59] / +0.03,
  Straightaway Acceleration +0.17 [−0.04, 0.38] / −0.10 (Neo −0.49). Slot values (swap − drop Slick Surge) across
  X3+X4: Condor's Fury +0.55, Latch On +0.43, Break the Mold +0.40, Triumphant Pulse +0.36, Barcarole +0.30,
  Slick Surge +0.26, RS: Power +0.25, Straightaway Acceleration +0.16, Pedal to the Metal +0.09 (each ±0.21).
  Firing: Triumphant Pulse 79 % at 2200 m (needs 2nd–5th), Barcarole 90 % at 2000 m (needs top 4), Straightaway
  Acceleration 93 % anywhere 100–2240 m (median 1115 m). Adding a late speed skill on top: Neo HP-out 1.66–1.67 %
  (marginal); swaps ok.

- X5 (extra) best Neo kit and stats WITHOUT Ignited Spirit WIT (user rule: no skills that risk losing position;
  run runs/20261126-210313-loh-v4-x5-neo-kit; `data/loh/results/v4/X5/`; script `loh_v4_x5_neo_kit.py`). Also excluded:
  Prudent Positioning (same opening lane-move mechanism), drains, Pedal to the Metal; Nimble Navigator (lane +0.005)
  optional. Pool = Neo's pool + X3/X4 skills. 1,955 legal kits (best removal per add set, diversity-capped) → 56 →
  14 → 8 by halving (2,000 / 6,000 / 17,500 races, seeds 198.0/198.1/198.2M); stats 9 variants x 9,000 (198.4M);
  validation 17,500 unseen races (199M), vs current champion (with IS WIT):
    final kit `data/loh/my_team_v4_neo_no_isw.json` (stats unchanged 1450/1000/1250/1200/1200, ESP 4540, 23 skills,
    inherited Moving Past / Into High Gear! / Condor's Fury): −IS WIT −Red Shift −Position Pilfer −Slipstream
    +Condor's Fury +Groundwork +Medium Straightaways ◎ +Straightaway Adept → team 96.80 %, +0.41 [0.21, 0.61],
    Neo top-3 +1.53, points +0.17; Neo HP-out 1.45 % (ub 1.64, ok); P(batch ≥ 95) 100 %, ≥ 97.1 43 % (base 98 / 15).
    without Nimble Navigator `my_team_v4_neo_no_isw_no_nn.json` (ESP 4510): −IS WIT −Red Shift −Nimble Navigator
    −Slipstream +Corner Adept ○ +Groundwork +Late Surger Straightaways ○ +Medium Straightaways ◎ → +0.33 [0.13, 0.54],
    HP-out 1.14 %.  Dropping IS WIT and adding nothing: −0.50 [−0.72, −0.29].
  Search-round gain +0.71 shrank to +0.41 on fresh seeds (selection effect). For Neo on this course Medium
  Straightaways ○ (100 SP), Late Surger Straightaways ○ (130) and Straightaway Adept (170) are the same effect
  (+0.15 m/s, 7.2 s, random straight; identical results in round 2), so the cheapest legal one should fill that role.
  Stats: no cost-neutral move beat 1450/1000/1250/1200/1200; guts −50 → stamina +50 costs −0.05 [−0.20, 0.09] and cuts
  Neo HP-out 1.43 → 0.41 % (free safety margin).

- X6 (extra) theory test: Angling and Scheming (inh. 900201, +0.2 m/s² for 5.76 s when 1st on a corner in the final
  leg; fires at ~1603 m for whichever front leads) on the fronts reduces dueling (run
  runs/20261127-012527-loh-v4-x6-angling; `data/loh/results/v4/X6/`; scripts `loh_v4_x6_angling.py`,
  `loh_v4_x6_analyze.py`). Team = v4 champion fronts + Neo X5 build; added on top (Ines 24 skills, over the cap);
  17,500 races per variant (seeds 200M), downsampled frames; duel partner = runner with the same duel start time.
  Clean causal comparison vs a no-effect clone (identical race until it fires; no-fire races identical to 0 s),
  both fronts holding it: either front duels −10.6 pp [−11.2, −10.1] (base 44 %), Kitasan and Ines duel each other
  −10.4 pp (base 26 %), duel time −1.7 / −1.8 s per race, gap at 1875 m +1.87 m, within 3 m at 1875 m −8.6 pp; a front
  wins +6.7 pp, fronts finish 1-2 −2.3 pp; team top-3 +0.03 [−0.00, +0.07] (no change), points +0.08 [0.05, 0.11].
  Kitasan only: duels −3.2 pp, wins +4.3, team +0.01. Ines only: duels −7.6 pp, wins +2.7, team +0.03. When it fires the
  holder's win rate rises +10–14 pp, own top-3 +0.15–0.34, the other front's top-3 −0.08 to −0.20. Verdict: the theory's
  mechanism is right (less dueling, fronts separate) but it does not cost team top-3 — the leader's acceleration
  replaces the duel. The plain add-vs-base comparison showed −0.18/−0.19 team, but the no-effect clone shows the same
  (−0.20/−0.23): that is the engine's RNG reshuffle when any skill is added, not the skill.

- X7 (extra) Angling and Scheming on the MOCKS instead (run in `data/loh/results/v4/X7/run.txt`; scripts
  `loh_v4_x7_angling_mocks.py`, `loh_v4_x7_analyze.py`; same team/seeds as X6, base identical to X6 base). Skill
  appended to every mock (and in "all" also to my two fronts); real vs no-effect twin, 17,500 races each.
  Mocks hold it: team top-3 −0.54 [−0.60, −0.47], points −0.38/race, Ines −0.83, Kitasan −0.47, Neo −0.31, mock top-3
  +0.54. It fires only when a mock front leads at 1600 m (9.1 % of races; mock leads at 1600 m 8.5 % in base); in those
  races team top-3 −5.9 pp (Ines −9.1, Kitasan −5.2), the mock's lead at 1875 m +1.0 m, my fronts duel more (+5.5 pp,
  with a mock +10.9 pp) but still lose the podium spot. Taking it back on my fronts too ("all"): vs mocks-only
  +0.15 [−0.06, +0.35] team (ns), +0.16 points — little counter, because mine fires only when my front leads, i.e. in
  the races where the mock's does not. Asymmetry vs X6: when my leader accelerates, the runner left behind is usually
  my other front (top-3 count unchanged); when a mock leader does, it keeps a podium spot from my team.

## 5. Open questions / leads
- Kitasan RS + Mad Dash at 1200 stamina vs the final team (dropped early in v3 search). v4 A4: Kitasan has
  no drain set that meets the floor up to 1350 stamina.
- Per-batch reading of the HP floor (rate ≤ 0.78–1.00 %): stamina needed per uma not yet measured.
- Killer Tunes on Ines (never tested).
- Second engine: not yet provided by the user.

## 6. Where things are
| What | Where |
| --- | --- |
| Rules (machine-readable) | `data/loh/rules.json` (`v3`, `v4` blocks) |
| Skill pool | `data/loh/skill_pool.json/.csv` ← `scripts/loh_skill_pool.py` |
| Skill fixes (in-game verified) | `data/loh/skill_overrides.json` (applied by `catalog.skill_table()`), specs in `data/loh/skill_specs.json` |
| Teams | `data/loh/my_team_v3_base.json`, `my_team_v3_champion.json`, `my_team_v4_base.json`, `my_team_v4_champion.json`, `my_team_v4_neo_no_isw*.json`, `cn_team.json`, `jp_team.json` |
| Mock builds | `data/loh/mocks.json` |
| Archived small run outputs | `data/loh/archive/<run>/` (runs/ itself is git-ignored) |
| Curated results | `data/loh/results/` |
| Reports | `docs/reports/` (`v3_research_report.md`; `v4_results.md` ← `scripts/loh_v4_a9_tables.py`) |
| Plan and progress | `docs/MASTER_PROMPT.md`, `docs/PROGRESS.md`, `CHANGELOG.md` |
