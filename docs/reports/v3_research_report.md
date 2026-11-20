# League of Heroes Tokyo 2400m: Team-Building Research Report

Nov 19, 2026

## Summary

The best team found places a team average of **81.6% top-3** against random mock LoH teams. That is +3.6pp over the starting builds (78.0%) and +1.75pp over the CN winning team (79.9%), checked on 17,500 races it had never seen.

| Uma | Spd / Sta / Pow / Guts / Wit | Stat cost | Skills | Top-3 | Points per race |
| --- | --- | --- | --- | --- | --- |
| New Year Kitasan Black (Front) | 1430 / 1100 / 1230 / 1175 / 1200 | 6395 | 21 | 84.0% | 62.9 |
| Valentine Ines Fujin (Front) | 1430 / 1050 / 1245 / 1200 / 1200 | 6400 | 23 | 84.0% | 62.1 |
| Neo Universe (Late Surger) | 1450 / 1000 / 1250 / 1200 / 1200 | 6400 | 23 | 77.0% | 58.9 |

In 175-race batches this team averages 32,182 points and clears 80% team top-3 in 90 of 100 batches. The CN team clears it in 49.

The five things that matter most, in order:

1. **Power, wit and guts up to 1200 come first.** Each 100 points below 1200 costs 1–2.2pp of team top-3. Points above 1200 cost double and return little, except power on Neo.
2. **Speed is the steady sink for spare points.** It returns about 0.45pp per 100 cost points, in a straight line, at every level tested.
3. **Taking the Lead and Solid Preparation are core on fronts.** Removing both from Ines costs 12.4pp of team top-3.
4. **Stamina past about 1000–1100 is wasted** unless the uma carries stamina-draining skills. Even then, only Kitasan needs about 1200.
5. **Mood is the biggest thing you don't control.** Each mood step moves top-3 by about 5pp. Ground, weather and gate (except Neo in gates 2–3) barely matter.

## Method

Every number here comes from the GlobalSim race engine, the backend of the umaeclipse race sim, using Global mechanics. In total, about 2.5 million races were simulated.

**The race:** Tokyo 2400m (Tokyo Yushun), spring, left-handed, 12 runners. Each race has your 3 umas, a random enemy team of 3 and 6 random NPCs. Every race re-rolls gates, mood, ground, weather and time of day. Your umas never draw gate 1.

**Scoring:** 1st 100, 2nd 60, 3rd 40, 4th 30, 5th 20, 6th–12th 10. The goal metric is **team top-3%**, the average of your three umas' top-3 rates. Points are tracked next to it. A 175-race batch matches one LoH run.

**Your stat budget:** 6400 cost points per uma. Each point above 1200 costs 2, as in game. So 1430 speed costs 1660, and 1430 / 1100 / 1200 / 1200 / 1200 costs 6360. Builds stay inside Spd 1350–1500, Sta 950–1250, Pow 1100–1250, Guts 1000–1250, Wit 1100–1250.

**Skill rules:** skills come from the realistic pool only. Each build spends 4500–4600 skill points, carries at most 23 skills including the unique and at most 3 inherited skills. The unique is level 6, distance S, style A. Concentration and Killer Tunes are not used on Kitasan, and Nimble Navigator is not used on fronts.

**Paired testing:** each seed fixes one race: gates, mood, conditions, NPCs and the enemy team. Every build variant runs the same list of seeds, so differences come from the build, not from luck. Final checks always use seeds the search never saw.

**Reading the numbers:**

- **pp** = percentage points of team top-3, so 81.6% minus 78.0% is +3.6pp.
- **\[lo, hi\]** = the 95% confidence interval of a paired difference. When lo is above 0, the gain is real.
- **Noise floor:** adding a skill that never fires still shifts results by up to about ±0.8pp, because the race's random numbers fall differently. Treat any effect under about 0.5pp as "no clear effect" unless its interval says otherwise.

## Mock opponents

The enemy team in each race is 3 different umas drawn from Kitasan, Ines, Neo and Bourbon. Each is built from one of 139 mock builds: 43 Kitasan, 40 Ines, 42 Neo and 14 Bourbon. Simming against the real CN and JP teams gave no usable answers: those teams carry 24–26 skills and up to 4990 skill points, past the LoH rules. So the mock field is a realistic, beatable field instead.

**How each mock is rolled:**

| Stat | Range | Weighted range (70% of rolls) |
| --- | --- | --- |
| Speed | 1370–1520 | 1370–1450 |
| Stamina | 950–1170 | 1100–1170 |
| Power | 1130–1250 | 1220–1250 |
| Guts | 850–1230 | 1100–1230 |
| Wit | 1150–1230 | 1200–1230 |

- **Skills:** each mock drops 2–3 random non-gold skills from its kit, and one gold skill with a 40% chance. Evolved skills stay.
- **Distance aptitude:** S with a 70% chance, otherwise A.
- **Nimble Navigator** is removed from mock fronts.

**Calibration:** against this field the CN team places 79.8–79.9% team top-3, and your starting builds 77.1–78.0%. One 175-race batch swings about ±2.5pp around a team's true rate from luck alone. So one LoH run can't tell two builds within about 2pp apart.

**What makes a mock dangerous** (tests on an earlier, stronger version of the field):

- Distance A instead of S: the field gets 7.7pp easier.
- 8 more skills dropped: your team climbs to about 95.8%.
- −200 on every stat: your team climbs to about 95.9%.
- Unique skill level barely matters.

The CN team's 97.1% in real LoH means the real field was far weaker than this mock spec. Trust the gaps between builds here more than the absolute percentages.

## Stats

The last points you put into power, wit and guts on the way to 1200 are the most valuable points in the build. Past 1200 they cost double and return little, so speed takes everything left over.

&#91;embedded content: Stats study, 6,000 paired races per variant vs random mock teams; average of the ±50 and ±100 steps\]

**How to read it:** a blue bar is what you lose per 100 cost points by cutting that stat; a grey bar is what you gain by adding to it. Anything right of the dashed line beats spending the same points on speed.

- **Speed is linear.** About 0.4–0.55pp per 100 cost, both directions and on all three umas. 100 speed above 1200 costs 200 points and returns about 0.7–1.0pp.
- **Power, wit and guts below 1200** are worth 0.7–2.1pp per 100 cost. Cutting 100 wit on Kitasan costs 1.7pp, as much as removing her best gold skill.
- **Above 1200 the same stats** return −0.3 to +0.3pp per 100 cost, which is noise. The one exception is **Neo's power** at about 0.75: Late Surgers use power to push through the pack late, so Neo takes power to 1250 before speed.
- **Stamina** is the cheapest stat to cut on fronts (about 0.25pp per 100) and almost free to cut on Neo (0.05). It only pays when skills drain it (next section).

**The 1200 rule in plain terms:** going from 1400 to 1500 speed costs 200 points and returns about 0.8pp. Going from 1100 to 1200 guts costs 100 points and returns 0.7–1.1pp. Fill power, wit and guts to 1200 first; then speed.

**Your planned −50 speed / +100 stamina trade** costs about 0.3pp on stats alone. It only pays off when the extra stamina lets you carry draining skills; see Dueling, stamina and guts.

## Dueling, stamina and guts

Stamina is only worth buying to carry Racing Spirit: Stamina and Mad Dash, and only on fronts. Guts changes nothing measurable in duels, so treat it as a stat to fill to 1200 and stop.

### Stamina and the draining skills

Every stamina change here is paid for with speed, so each point on a line costs the same in game.

&#91;embedded content: Stamina × draining-skill study, 2,500 paired races per point vs random mock teams\]

- **Kitasan** wants both skills at **1200 stamina** (speed 1380): +1.05pp team over no draining skills, and her own top-3 goes 80.4% → 84.1%. Mad Dash alone needs 1150. Racing Spirit alone is fine from 1000.
- **Ines** wants both skills at **1100–1150**: +1.9pp team, and her own top-3 goes 81.4% → 86.7%.
- **Neo** wants the lowest stamina in every case. Racing Spirit adds about 1pp; Mad Dash adds nothing on top.
- **Without draining skills, stamina above about 1000–1100 is wasted.** The lines slope down to the right: the speed you gave up costs more.

### Running out of HP is a price, not a failure

HP-out rate = share of races where the uma's HP hit zero before the finish.

| Uma | Skills | Stamina 950 | 1100 | 1200 |
| --- | --- | --- | --- | --- |
| Kitasan | none | 30% | 3% | 1% |
| Kitasan | Racing Spirit + Mad Dash | 94% | 63% | 29% |
| Ines | none | 7% | 1% | 1% |
| Ines | Racing Spirit + Mad Dash | 83% | 29% | 6% |
| Neo | Racing Spirit + Mad Dash | 12% | 0% | 0% |

Neo almost never runs out of HP from 1000 stamina up, even with both skills. Ines' best setup runs out of HP in 29% of races and still places best. A late, small HP-out is the cost of a faster middle section. Judge stamina by placements, never by HP-out rate alone. The floor is real, though: Kitasan with Mad Dash at 950 stamina runs out in 83% of races and her top-3 falls from 80% to 58%.

### Duels

A duel (the final-straight compete) is good for you: when your uma duels she places top-3 88–92% of the time, against 72–81% when she doesn't.

| Uma, no draining skills | Duel rate | Duel length | Starts at | Top-3 when dueling |
| --- | --- | --- | --- | --- |
| Kitasan, stamina 950 → 1250 | 38% → 42% | 14.0 s → 15.4 s | 1927 m | 86–88% |
| Ines, stamina 950 → 1250 | 49% → 52% | 13.9 s → 15.7 s | 1927 m | 89–91% |
| Neo, stamina 950 → 1250 | 30% → 34% | 10.1 s → 11.2 s | 2075 m | 83–88% |

- **Stamina makes duels longer**, by about 0.3 s per 50 stamina, and slightly more frequent. Duel length is set by HP left, so draining skills shorten duels by 1–2 s.
- **Longer duels don't pay for themselves.** Without draining skills, the speed traded away costs more than the extra duel time gains.
- **Duels start at a fixed point:** about 1927 m for fronts and 2075 m for Neo, whatever the stats.

### Guts

Guts traded for speed between 1000 and 1250 changed team top-3 by under 0.4pp (within noise), and did not move duel rate, length or start.

- Guts lengthens the **opening Spot Struggle** for fronts (the early fight for the lead): about 9.6 s at 1000 guts versus 10.5 s at 1250. Kitasan is in one 75% of races and Ines 85%. It didn't change placements.
- In the stats study, cutting guts below 1200 cost 0.7–1.1pp per 100. So: fill guts to 1200 if you can; never pay double for guts above it.

## Skills

Acceleration skills are the most valuable skills in this race, point for point. Speed skills return about the same per SP whether white or gold, so cheap ones that fire reliably come first.

**Taking the Lead and Solid Preparation are worth it on fronts, by a wide margin.**

| Ines test (4,000 paired races) | Team pp | Ines' own top-3 |
| --- | --- | --- |
| Remove both Taking the Lead and Solid Preparation | −12.4 | −50 pp |
| Remove Solid Preparation only | −4.8 | −15.6 pp |
| Remove Taking the Lead only | −2.8 | −8.5 pp |
| Solid Preparation → Groundwork | −0.97 | −2.4 pp |

Together they are worth far more than apart, because each covers the other's start. On Kitasan, upgrading Groundwork to Solid Preparation is +1.63pp for 180 SP, and the build search kept it.

**What the columns mean:**

- **Test:** *held* = the skill was removed from the build, so the value is what holding it is worth. *add* = added on top. *swap for X* = it replaced X, and SP is the difference.
- **SP** = full skill-point cost with no hint discounts, including the white skill under a gold. Hints make every skill cheaper, so pp per SP improves with hints.
- **m/s per 100 SP** = the skill's speed bonus divided by its cost, for speed skills.
- **Speed × time** = bonus m/s × duration at 2400 m: roughly the metres a full activation is worth. Gold speed skills sit at 2.0–2.5; whites at 0.65–1.8.
- **Team pp \[95% CI\]** = change in team top-3. Single skills carry about ±0.8pp of noise, so only intervals that clear 0 are firm.
- **Own pp** = that uma's own top-3 change.

**Patterns across all three umas:**

- **Acceleration wins.** Groundwork, Solid Preparation, Taking the Lead and Red Shift return 1–2.8pp per 100 SP on fronts. A front that gets out first is hard to pass, and the early lead decides who gets the inside line.
- **Positioning tools punch above their cost:** Dodging Danger (110 SP, +1.6pp on both fronts) and Hesitant Front Runners (130 SP, +0.9–1.2pp on all three) are top picks per SP.
- **Big gold speed skills are steady but expensive:** Superb Gait, Top Runner and Divine Speed return 0.25–0.6pp per 100 SP.
- **Cheap whites that fit the course** (Medium Corners ○, 1,500,000 CC, Uma Stan on Neo) can be worth as much as a gold.
- **Green ◎ over ○** is always worth its 110 SP: +0.4–0.5pp.
- **Inherited skills that don't fit the running style never fire.** Moving Past, Into High Gear and Bring on the Banquet sit at noise on fronts but are worth about 1.5pp on Neo.
- **Some skills help their uma but not the team:** Ines' Tail Held High and Playtime's Over! raise her own top-3 by 1.5–1.8pp but cost the team. Two fronts crowd each other, so a skill that helps Ines pass Kitasan is no team gain.

### New Year Kitasan Black

| Skill | Test | SP | Effect at 2400 m | m/s per 100 SP | Speed × time | Team pp \[95% CI\] | Own pp | Team pp per 100 SP |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Groundwork | held | 100 | +0.2 m/s² accel, 7.2 s |  |  | +2.81 \[+2.02, +3.60\] | +9.8 | +2.81 |
| Red Shift/LP1211-M | held | 200 | +0.2 m/s² accel, 5.8 s |  |  | +2.02 \[+1.23, +2.81\] | +8.0 | +1.01 |
| Superb Gait | held | 360 | +0.35 m/s target speed, 5.8 s | 0.097 | 2.02 | +1.73 \[+0.92, +2.55\] | +6.0 | +0.48 |
| Top Runner | held | 360 | +0.35 m/s target speed, 7.2 s | 0.097 | 2.52 | +1.69 \[+0.91, +2.47\] | +6.8 | +0.47 |
| Dodging Danger | held | 110 | +0.025 lane speed, lane change, 7.2 s |  |  | +1.63 \[+0.86, +2.41\] | +5.3 | +1.48 |
| Solid Preparation | swap for Groundwork | +180 | +0.4 m/s² accel, 7.2 s |  |  | +1.63 \[+0.90, +2.36\] | +4.0 | +0.91 |
| Divine Speed | held | 400 | +0.35 m/s current speed, +1.5% HP, 7.2 s | 0.087 | 2.52 | +1.53 \[+0.71, +2.34\] | +6.0 | +0.38 |
| Front Runner Straightaways ◎ | held | 270 | +0.25 m/s target speed, 7.2 s | 0.093 | 1.80 | +1.48 \[+0.67, +2.30\] | +4.8 | +0.55 |
| Medium Straightaways ◎ | held | 210 | +0.25 m/s target speed, 7.2 s | 0.119 | 1.80 | +1.48 \[+0.67, +2.30\] | +4.8 | +0.71 |
| Left-Handed ◎ | held | 200 | +60 Speed |  |  | +1.38 \[+1.14, +1.61\] | +5.4 | +0.69 |
| Ignited Spirit WIT | held | 200 | +0.015 lane speed, wider vision, 9.6 s |  |  | +1.30 \[+0.49, +2.11\] | +5.0 | +0.65 |
| Hesitant Front Runners | add | 130 | −0.15 m/s to other fronts, 7.2 s |  |  | +1.20 \[+0.39, +2.01\] | +1.2 | +0.92 |
| Professor of Curvature | add | 360 | +0.35 m/s target speed, 5.8 s | 0.097 | 2.02 | +1.07 \[+0.26, +1.89\] | +6.0 | +0.30 |
| Straightaway Adept | held | 170 | +0.15 m/s target speed, 7.2 s | 0.088 | 1.08 | +1.00 \[+0.18, +1.82\] | +2.5 | +0.59 |
| Restraint | add | 160 | +60 Wit, lower rushing chance |  |  | +0.93 \[+0.34, +1.52\] | +1.6 | +0.58 |
| Spring Runner ○ | held | 90 | +40 Speed |  |  | +0.92 \[+0.71, +1.12\] | +3.5 | +1.02 |
| Wisdom of the Sun | held | 400 | +0.42 m/s target speed, 4.3 s | 0.105 | 1.81 | +0.87 \[+0.08, +1.66\] | +4.5 | +0.22 |
| In Body and Mind | add | 340 | +0.35 m/s target speed, 5.8 s | 0.103 | 2.02 | +0.57 \[−0.25, +1.38\] | +3.4 | +0.17 |
| With All My Soul | add | 160 | +0.15 m/s target speed, −0.035 m/s to others, 4.3 s | 0.094 | 0.65 | +0.57 \[−0.24, +1.37\] | +1.0 | +0.35 |
| Medium Corners ○ | add | 100 | +0.15 m/s target speed, 7.2 s | 0.150 | 1.08 | +0.57 \[−0.26, +1.39\] | +3.7 | +0.57 |
| Front Runner Corners ○ | held | 130 | +0.15 m/s target speed, 7.2 s | 0.115 | 1.08 | +0.55 \[−0.26, +1.36\] | +1.8 | +0.42 |
| Playtime's Over! | add | 160 | +0.15 m/s target speed, 7.2 s | 0.094 | 1.08 | +0.51 \[−0.27, +1.29\] | +2.1 | +0.32 |
| Uma Stan | add | 160 | +0.15 m/s target speed, 7.2 s | 0.094 | 1.08 | +0.51 \[−0.26, +1.28\] | +2.3 | +0.32 |
| Prudent Positioning | add | 120 | +0.035 lane speed, 7.2 s |  |  | +0.51 \[−0.30, +1.32\] | +1.3 | +0.42 |
| Slipstream | held | 160 | +0.15 m/s target speed, 7.2 s | 0.094 | 1.08 | +0.49 \[−0.29, +1.27\] | +2.4 | +0.31 |
| Operation Cacao | held | 200 | +0.15 m/s target speed, +0.4% HP, 7.2 s | 0.075 | 1.08 | +0.40 \[−0.38, +1.18\] | +2.8 | +0.20 |
| All I've Got | add | 160 | +0.15 m/s target speed, 7.2 s | 0.094 | 1.08 | +0.40 \[−0.38, +1.18\] | +2.5 | +0.25 |
| Corner Adept ○ | add | 180 | +0.15 m/s target speed, 5.8 s | 0.083 | 0.86 | +0.38 \[−0.44, +1.21\] | +3.4 | +0.21 |
| Tail Held High | add | 100 | +0.15 m/s target speed, 7.2 s | 0.150 | 1.08 | +0.33 \[−0.45, +1.10\] | +1.7 | +0.33 |
| Ramp Up | held | 170 | +0.15 m/s target speed, 4.3 s | 0.088 | 0.65 | +0.25 \[−0.53, +1.03\] | +1.6 | +0.15 |
| Racing Spirit: Stamina | add | 150 | +0.25 m/s target speed, −2.0% HP, 7.2 s | 0.167 | 1.80 | +0.23 \[−0.58, +1.03\] | +1.9 | +0.15 |
| Spring Runner ◎ | swap for Spring Runner ○ | +110 | +60 Speed |  |  | +0.23 \[+0.09, +0.38\] | +1.4 | +0.21 |
| Standard Distance ○ | held | 90 | +40 Stamina |  |  | +0.12 \[+0.06, +0.19\] | +0.4 | +0.14 |
| Firm Resolve | add | 180 | +0.25 m/s target speed, 5.8 s | 0.139 | 1.44 | +0.12 \[−0.65, +0.90\] | +1.3 | +0.07 |
| Front Runner Savvy ○ | held | 110 | +40 Wit, wider vision |  |  | +0.08 \[−0.46, +0.63\] | +1.7 | +0.08 |
| Mad Dash | add | 180 | +0.25 m/s target speed, −4.0% HP, 6.5 s | 0.139 | 1.62 | −0.12 \[−0.92, +0.69\] | +0.0 | −0.06 |
| Moving Past, and Beyond | add | 200 | +0.2 m/s² accel, 5.8 s |  |  | −0.17 \[−0.94, +0.61\] | +0.4 | −0.08 |
| Into High Gear! | add | 200 | +0.15 m/s target speed, +0.05 m/s² accel, 7.2 s | 0.075 | 1.08 | −0.17 \[−0.94, +0.61\] | +0.3 | −0.08 |
| Left-Handed ○ | swap for Left-Handed ◎ | −110 | +40 Speed |  |  | −0.46 \[−0.60, −0.31\] | −1.7 | +0.42 |
| Medium Straightaways ○ | swap for Medium Straightaways ◎ | −110 | +0.15 m/s target speed, 7.2 s | 0.150 | 1.08 | −0.56 \[−1.27, +0.16\] | −1.6 | +0.51 |

### Valentine Ines Fujin

| Skill | Test | SP | Effect at 2400 m | m/s per 100 SP | Speed × time | Team pp \[95% CI\] | Own pp | Team pp per 100 SP |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Solid Preparation | held | 280 | +0.4 m/s² accel, 7.2 s |  |  | +4.78 \[+3.99, +5.56\] | +15.6 | +1.71 |
| Taking the Lead | held | 240 | +0.4 m/s² accel, 2.9 s |  |  | +2.79 \[+2.00, +3.58\] | +8.5 | +1.16 |
| Red Shift/LP1211-M | held | 200 | +0.2 m/s² accel, 5.8 s |  |  | +2.29 \[+1.50, +3.08\] | +10.8 | +1.15 |
| Dodging Danger | held | 110 | +0.025 lane speed, lane change, 7.2 s |  |  | +1.69 \[+0.91, +2.48\] | +5.0 | +1.54 |
| Superb Gait | add | 360 | +0.35 m/s target speed, 5.8 s | 0.097 | 2.02 | +1.45 \[+0.64, +2.26\] | +4.2 | +0.40 |
| Left-Handed ◎ | held | 200 | +60 Speed |  |  | +1.42 \[+1.17, +1.67\] | +5.5 | +0.71 |
| Spring Runner ◎ | held | 200 | +60 Speed |  |  | +1.42 \[+1.17, +1.67\] | +5.5 | +0.71 |
| Top Runner | held | 360 | +0.35 m/s target speed, 7.2 s | 0.097 | 2.52 | +1.32 \[+0.53, +2.11\] | +6.3 | +0.37 |
| Ignited Spirit WIT | held | 200 | +0.015 lane speed, wider vision, 9.6 s |  |  | +1.25 \[+0.43, +2.07\] | +5.0 | +0.62 |
| Hesitant Front Runners | add | 130 | −0.15 m/s to other fronts, 7.2 s |  |  | +1.12 \[+0.33, +1.92\] | +1.5 | +0.87 |
| Divine Speed | held | 400 | +0.35 m/s current speed, +1.5% HP, 7.2 s | 0.087 | 2.52 | +0.96 \[+0.15, +1.77\] | +5.4 | +0.24 |
| Restraint | add | 160 | +60 Wit, lower rushing chance |  |  | +0.78 \[+0.21, +1.36\] | +1.5 | +0.49 |
| Medium Straightaways ◎ | held | 210 | +0.25 m/s target speed, 7.2 s | 0.119 | 1.80 | +0.68 \[−0.10, +1.47\] | +2.5 | +0.33 |
| Front Runner Straightaways ◎ | held | 270 | +0.25 m/s target speed, 7.2 s | 0.093 | 1.80 | +0.64 \[−0.16, +1.44\] | +3.2 | +0.24 |
| Straightaway Adept | add | 170 | +0.15 m/s target speed, 7.2 s | 0.088 | 1.08 | +0.60 \[−0.20, +1.40\] | +1.8 | +0.35 |
| Wisdom of the Sun | add | 400 | +0.42 m/s target speed, 4.3 s | 0.105 | 1.81 | +0.56 \[−0.23, +1.35\] | +3.1 | +0.14 |
| Bring on the Banquet! | add | 200 | +0.15 m/s current speed, +0.05 m/s² accel, 5.8 s | 0.075 | 0.86 | +0.51 \[−0.28, +1.30\] | +2.8 | +0.25 |
| In Body and Mind | add | 340 | +0.35 m/s target speed, 5.8 s | 0.103 | 2.02 | +0.48 \[−0.33, +1.28\] | +4.0 | +0.14 |
| With All My Soul | held | 160 | +0.15 m/s target speed, −0.035 m/s to others, 4.3 s | 0.094 | 0.65 | +0.43 \[−0.38, +1.25\] | +1.7 | +0.27 |
| Slipstream | held | 160 | +0.15 m/s target speed, 7.2 s | 0.094 | 1.08 | +0.34 \[−0.45, +1.13\] | +1.6 | +0.21 |
| Medium Corners ○ | add | 100 | +0.15 m/s target speed, 7.2 s | 0.150 | 1.08 | +0.32 \[−0.48, +1.13\] | +2.1 | +0.32 |
| Mad Dash | add | 180 | +0.25 m/s target speed, −4.0% HP, 6.5 s | 0.139 | 1.62 | +0.29 \[−0.51, +1.09\] | +1.8 | +0.16 |
| Racing Spirit: Stamina | held | 150 | +0.25 m/s target speed, −2.0% HP, 7.2 s | 0.167 | 1.80 | +0.29 \[−0.52, +1.10\] | +2.5 | +0.19 |
| All I've Got | held | 160 | +0.15 m/s target speed, 7.2 s | 0.094 | 1.08 | +0.19 \[−0.60, +0.98\] | +1.5 | +0.12 |
| Professor of Curvature | swap for Corner Adept ○ | +180 | +0.35 m/s target speed, 5.8 s | 0.097 | 2.02 | +0.16 \[−0.55, +0.86\] | +2.6 | +0.09 |
| Front Runner Savvy ○ | held | 110 | +40 Wit, wider vision |  |  | +0.15 \[−0.42, +0.72\] | +1.1 | +0.14 |
| Ramp Up | add | 170 | +0.15 m/s target speed, 4.3 s | 0.088 | 0.65 | +0.12 \[−0.68, +0.91\] | +1.0 | +0.07 |
| Corner Adept ○ | held | 180 | +0.15 m/s target speed, 5.8 s | 0.083 | 0.86 | +0.11 \[−0.70, +0.92\] | +1.8 | +0.06 |
| Standard Distance ○ | add | 90 | +40 Stamina |  |  | +0.07 \[+0.02, +0.13\] | +0.4 | +0.08 |
| Firm Resolve | add | 180 | +0.25 m/s target speed, 5.8 s | 0.139 | 1.44 | −0.06 \[−0.85, +0.73\] | +0.2 | −0.03 |
| Uma Stan | held | 160 | +0.15 m/s target speed, 7.2 s | 0.094 | 1.08 | −0.06 \[−0.83, +0.72\] | +0.7 | −0.04 |
| Operation Cacao | add | 200 | +0.15 m/s target speed, +0.4% HP, 7.2 s | 0.075 | 1.08 | −0.10 \[−0.89, +0.69\] | +1.6 | −0.05 |
| Moving Past, and Beyond | add | 200 | +0.2 m/s² accel, 5.8 s |  |  | −0.13 \[−0.92, +0.66\] | +0.0 | −0.07 |
| Into High Gear! | add | 200 | +0.15 m/s target speed, +0.05 m/s² accel, 7.2 s | 0.075 | 1.08 | −0.13 \[−0.92, +0.66\] | +0.0 | −0.07 |
| Tail Held High | held | 100 | +0.15 m/s target speed, 7.2 s | 0.150 | 1.08 | −0.14 \[−0.91, +0.63\] | +1.5 | −0.14 |
| Playtime's Over! | held | 160 | +0.15 m/s target speed, 7.2 s | 0.094 | 1.08 | −0.25 \[−1.03, +0.53\] | +1.8 | −0.16 |
| Prudent Positioning | add | 120 | +0.035 lane speed, 7.2 s |  |  | −0.36 \[−1.16, +0.45\] | +0.5 | −0.30 |
| Medium Straightaways ○ | swap for Medium Straightaways ◎ | −110 | +0.15 m/s target speed, 7.2 s | 0.150 | 1.08 | −0.44 \[−1.17, +0.28\] | −2.1 | +0.40 |
| Spring Runner ○ | swap for Spring Runner ◎ | −110 | +40 Speed |  |  | −0.49 \[−0.65, −0.34\] | −1.7 | +0.45 |
| Left-Handed ○ | swap for Left-Handed ◎ | −110 | +40 Speed |  |  | −0.49 \[−0.65, −0.34\] | −1.7 | +0.45 |
| Groundwork | swap for Solid Preparation | −180 | +0.2 m/s² accel, 7.2 s |  |  | −0.97 \[−1.71, −0.24\] | −2.4 | +0.54 |

### Neo Universe

| Skill | Test | SP | Effect at 2400 m | m/s per 100 SP | Speed × time | Team pp \[95% CI\] | Own pp | Team pp per 100 SP |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Superb Gait | held | 360 | +0.35 m/s target speed, 5.8 s | 0.097 | 2.02 | +2.22 \[+1.42, +3.01\] | +9.3 | +0.62 |
| 1,500,000 CC | held | 120 | +0.15 m/s target speed, 5.8 s | 0.125 | 0.86 | +2.11 \[+1.30, +2.92\] | +10.0 | +1.76 |
| Spring Runner ◎ | held | 200 | +60 Speed |  |  | +1.86 \[+1.55, +2.16\] | +7.1 | +0.93 |
| Left-Handed ◎ | held | 200 | +60 Speed |  |  | +1.86 \[+1.55, +2.16\] | +7.1 | +0.93 |
| Medium Corners ○ | held | 100 | +0.15 m/s target speed, 7.2 s | 0.150 | 1.08 | +1.82 \[+0.99, +2.64\] | +6.1 | +1.82 |
| Professor of Curvature | add | 360 | +0.35 m/s target speed, 5.8 s | 0.097 | 2.02 | +1.62 \[+0.80, +2.43\] | +6.2 | +0.45 |
| Moving Past, and Beyond | held | 200 | +0.2 m/s² accel, 5.8 s |  |  | +1.55 \[+0.75, +2.35\] | +8.9 | +0.78 |
| Divine Speed | held | 400 | +0.35 m/s current speed, +1.5% HP, 7.2 s | 0.087 | 2.52 | +1.46 \[+0.66, +2.26\] | +8.6 | +0.36 |
| Into High Gear! | held | 200 | +0.15 m/s target speed, +0.05 m/s² accel, 7.2 s | 0.075 | 1.08 | +1.45 \[+0.65, +2.25\] | +7.9 | +0.73 |
| Uma Stan | held | 160 | +0.15 m/s target speed, 7.2 s | 0.094 | 1.08 | +1.35 \[+0.57, +2.13\] | +7.0 | +0.84 |
| Late Surger Corners ◎ | add | 270 | +0.25 m/s target speed, 7.2 s | 0.093 | 1.80 | +1.34 \[+0.52, +2.16\] | +5.5 | +0.50 |
| Groundwork | add | 100 | +0.2 m/s² accel, 7.2 s |  |  | +1.24 \[+0.46, +2.02\] | +5.3 | +1.24 |
| Hesitant Front Runners | held | 130 | −0.15 m/s to other fronts, 7.2 s |  |  | +1.22 \[+0.41, +2.02\] | +3.2 | +0.94 |
| Medium Straightaways ◎ | add | 210 | +0.25 m/s target speed, 7.2 s | 0.119 | 1.80 | +1.09 \[+0.29, +1.89\] | +6.1 | +0.52 |
| Wisdom of the Sun | held | 400 | +0.42 m/s target speed, 4.3 s | 0.105 | 1.81 | +1.05 \[+0.26, +1.84\] | +6.7 | +0.26 |
| Corner Adept ○ | add | 180 | +0.15 m/s target speed, 5.8 s | 0.083 | 0.86 | +0.83 \[+0.01, +1.64\] | +3.4 | +0.46 |
| Restraint | held | 160 | +60 Wit, lower rushing chance |  |  | +0.78 \[+0.31, +1.24\] | +3.9 | +0.48 |
| Nimble Navigator | held | 150 | +0.2 m/s² accel, +0.005 lane speed, 7.2 s |  |  | +0.74 \[−0.05, +1.53\] | +5.0 | +0.49 |
| Straightaway Adept | add | 170 | +0.15 m/s target speed, 7.2 s | 0.088 | 1.08 | +0.73 \[−0.09, +1.54\] | +4.2 | +0.43 |
| Late Surger Straightaways ○ | add | 130 | +0.15 m/s target speed, 7.2 s | 0.115 | 1.08 | +0.73 \[−0.09, +1.54\] | +4.2 | +0.56 |
| Medium Straightaways ○ | add | 100 | +0.15 m/s target speed, 7.2 s | 0.150 | 1.08 | +0.73 \[−0.09, +1.54\] | +4.2 | +0.73 |
| Position Pilfer | held | 180 | +0.15 m/s target speed, 5.8 s | 0.083 | 0.86 | +0.71 \[−0.09, +1.51\] | +4.8 | +0.39 |
| Playtime's Over! | held | 160 | +0.15 m/s target speed, 7.2 s | 0.094 | 1.08 | +0.70 \[−0.09, +1.49\] | +4.7 | +0.44 |
| In Body and Mind | add | 340 | +0.35 m/s target speed, 5.8 s | 0.103 | 2.02 | +0.59 \[−0.21, +1.39\] | +3.7 | +0.17 |
| Ignited Spirit WIT | add | 200 | +0.015 lane speed, wider vision, 9.6 s |  |  | +0.59 \[−0.21, +1.39\] | +3.4 | +0.30 |
| Ramp Up | add | 170 | +0.15 m/s target speed, 4.3 s | 0.088 | 0.65 | +0.58 \[−0.20, +1.36\] | +3.2 | +0.34 |
| Tail Held High | held | 100 | +0.15 m/s target speed, 7.2 s | 0.150 | 1.08 | +0.54 \[−0.25, +1.34\] | +4.5 | +0.54 |
| Slipstream | held | 160 | +0.15 m/s target speed, 7.2 s | 0.094 | 1.08 | +0.46 \[−0.33, +1.25\] | +4.3 | +0.29 |
| Prudent Positioning | add | 120 | +0.035 lane speed, 7.2 s |  |  | +0.38 \[−0.43, +1.18\] | +2.4 | +0.31 |
| Racing Spirit: Stamina | add | 150 | +0.25 m/s target speed, −2.0% HP, 7.2 s | 0.167 | 1.80 | +0.33 \[−0.48, +1.13\] | +2.7 | +0.22 |
| Slick Surge | held | 180 | +0.2 m/s² accel, 4.3 s |  |  | +0.27 \[−0.54, +1.07\] | +3.7 | +0.15 |
| Red Shift/LP1211-M | held | 200 | +0.2 m/s² accel, 5.8 s |  |  | +0.24 \[−0.55, +1.03\] | +3.4 | +0.12 |
| Standard Distance ○ | add | 90 | +40 Stamina |  |  | +0.13 \[−0.14, +0.41\] | +1.0 | +0.15 |
| Be Still | held | 180 | +1.5% HP |  |  | −0.07 \[−0.87, +0.74\] | +1.6 | −0.04 |
| Operation Cacao | add | 200 | +0.15 m/s target speed, +0.4% HP, 7.2 s | 0.075 | 1.08 | −0.13 \[−0.91, +0.65\] | +0.3 | −0.07 |
| Bring on the Banquet! | add | 200 | +0.15 m/s current speed, +0.05 m/s² accel, 5.8 s | 0.075 | 0.86 | −0.13 \[−0.91, +0.65\] | +0.3 | −0.07 |
| With All My Soul | add | 160 | +0.15 m/s target speed, −0.035 m/s to others, 4.3 s | 0.094 | 0.65 | −0.37 \[−1.17, +0.44\] | −0.5 | −0.23 |
| Left-Handed ○ | swap for Left-Handed ◎ | −110 | +40 Speed |  |  | −0.42 \[−0.56, −0.27\] | −1.7 | +0.38 |
| Spring Runner ○ | swap for Spring Runner ◎ | −110 | +40 Speed |  |  | −0.42 \[−0.56, −0.27\] | −1.7 | +0.38 |

Tested on the starting builds, 4,000 paired races each. Rows with identical numbers (for example Neo's straightaway whites) are skills with the same effect and trigger window in the engine, so they are interchangeable here. Speed-stat greens give their bonus all race: +60 Speed is worth about the same as 60 raw speed above 1200 (120 cost points).

## Build search and validation

An 8-round search improved the starting team by +3.6pp \[3.25, 4.01\] on races it never saw. It kept four changes; the last three rounds found nothing it could prove.

Each round tested about 30 whole-team variants on 1,500 races, kept the best 8 for 4,500 races, then the best 3 for 9,000. A change was accepted only if its 95% interval stayed above zero. Every round used new seeds. Round 0 tested the leads from the earlier studies; later rounds made random guided changes to the current best team (stat moves of 25–50, skill adds weighted by measured value, skill swaps).

| Round | Best change found | Team pp \[95% CI\] | Kept? |
| --- | --- | --- | --- |
| 0 | Neo: stamina 1000, power 1250, + Racing Spirit: Stamina | +1.25 \[+0.91, +1.59\] | yes |
| 1 | Neo: Ignited Spirit WIT replaces Racing Spirit; Kitasan: Solid Preparation replaces Groundwork and Front Runner Savvy ○ | +0.93 \[+0.45, +1.41\] | yes |
| 2 | Ines: Hesitant Front Runners replaces Playtime's Over!; Kitasan: 25 guts → power | +1.35 \[+0.83, +1.88\] | yes |
| 3 | Ines: 25 guts → speed | +0.29 \[−0.06, +0.64\] | no |
| 4 | Ines: small skill reshuffle | +0.10 \[−0.12, +0.32\] | no |
| 5 | Kitasan: 25 stamina → guts | +0.07 \[−0.26, +0.41\] | no |
| 6 | Ines: 50 stamina → power | +0.40 \[+0.04, +0.76\] | yes |
| 7 | Kitasan: 50 stamina → power; Ines: 25 guts → stamina | +0.31 \[−0.06, +0.69\] | no |

Kitasan with Racing Spirit + Mad Dash at 1200 stamina was tested in round 0 but fell out in the first cut, behind the Neo changes. It wasn't retested against the final team, so it remains an open lead.

### The final team

**New Year Kitasan Black** — 1430 / 1100 / 1230 / 1175 / 1200, 4600 SP, 21 skills (unique plus): Introducing the Victor!, Leap Ahead to the Future, Red Shift/LP1211-M, Operation Cacao, Left-Handed ◎, Standard Distance ○, Spring Runner ○, Straightaway Adept, Ramp Up, Medium Straightaways ◎, Front Runner Straightaways ◎, Front Runner Corners ○, Dodging Danger, Top Runner, Slipstream, Superb Gait, Divine Speed, Ignited Spirit WIT, Wisdom of the Sun, Solid Preparation.

**Valentine Ines Fujin** — 1430 / 1050 / 1245 / 1200 / 1200, 4550 SP, 23 skills (unique plus): Perfect ♪ Order Up!, Slick Serving, With All My Soul, Red Shift/LP1211-M, Left-Handed ◎, Ignited Spirit WIT, Dodging Danger, All I've Got, Medium Straightaways ◎, Corner Adept ○, Solid Preparation, Front Runner Straightaways ◎, Spring Runner ◎, Front Runner Savvy ○, Top Runner, Divine Speed, Slipstream, Taking the Lead, Tail Held High, Uma Stan, Racing Spirit: Stamina, Hesitant Front Runners.

**Neo Universe** — 1450 / 1000 / 1250 / 1200 / 1200, 4600 SP, 23 skills (unique plus): Beyond the Stars with You, Cross the Sea of Stars, Red Shift/LP1211-M, Moving Past, and Beyond, Into High Gear!, Left-Handed ◎, Spring Runner ◎, Nimble Navigator, Position Pilfer, Slick Surge, Hesitant Front Runners, Medium Corners ○, 1,500,000 CC, Uma Stan, Tail Held High, Slipstream, Playtime's Over!, Restraint, Superb Gait, Divine Speed, Wisdom of the Sun, Ignited Spirit WIT.

### Validation on unseen races

&#91;embedded content: Final validation, 17,500 unseen races (100 batches of 175) per team vs random mock teams\]

Points per 175-race batch: champion 32,182 (p10–p90 31,720–32,621), CN team 31,720, starting builds 31,497. No team reached 90% in any batch, so 97.1% is out of reach against this mock field; it reflects a weaker real field.

### What the champion's races look like

|  | Kitasan | Ines | Neo |
| --- | --- | --- | --- |
| Top-3 | 84.0% | 84.0% | 77.0% |
| 1st / 2nd / 3rd | 31.6 / 32.9 / 19.5% | 30.2 / 31.9 / 21.9% | 31.2 / 18.6 / 27.3% |
| Points per race | 62.9 | 62.1 | 58.9 |
| Late start | 19.4% | 1.7% | 19.9% |
| Top-3 after a late start | 79.1% | 69.9% | 72.6% |
| HP ran out | 3.1% | 4.9% | 1.7% |
| Dueled | 37.8% | 47.7% | 30.7% |
| Top-3 when dueling / not | 88.4 / 81.3% | 91.5 / 77.1% | 89.1 / 71.7% |
| Top-3 at mood −2 → +2 | 74.0 → 92.1% | 72.6 → 92.6% | 64.9 → 86.0% |
| Top-3 by gate 2–3 / 4–6 / 7–9 / 10–12 | 84.1 / 84.3 / 83.9 / 83.5% | 83.5 / 86.0 / 83.4 / 82.8% | 72.6 / 77.8 / 78.3 / 78.0% |

Ground (good to heavy) and weather moved top-3 by under 1.5pp for every uma.

## Building for LoH in practice

Build to a priority order, not to an exact stat line. Get power, wit and guts to 1200, set stamina to what your skills need, and pour the rest into speed; then buy acceleration and positioning skills before big speed golds.

### Why the numbers come out this way

- **Points above 1200 are worth a quarter as much.** They cost 2 to train, and the race engine counts raw stats above 1200 at half value (1300 raw races as 1250). That is why power, wit and guts fall off a cliff at 1200 in the stats chart.
- **Green skills dodge that cap.** Their +40/+60 is added after the halving, so Left-Handed ◎ and Spring Runner ◎ (+60 Speed each, 200 SP) are worth 1.4–1.9pp, more than 100 raw speed above 1200 (0.7–1.0pp, 200 cost points). Always take ◎ greens that match the race.
- **Speed is linear** across 1350–1500 because each point raises cruising and last-spurt target speed by a similar amount. That makes it the safe place for every spare point.
- **Power above 1200 unlocks a late burst for Late Surgers.** Power past 1200 stores a late-race boost, and the engine weights it 0.875 for Late Surgers at this distance against 0.75 for fronts. That is why Neo, and only Neo, keeps paying for power to 1250.
- **Wit below 1200** costs placements through more rushing (wasted HP early), worse positioning choices and a slightly lower skill activation rate (92.5% at 1200, 91.8% at 1100). Most of the loss is the first two.
- **Stamina only buys HP.** Fronts need enough HP to run a full last spurt; anything more is idle unless a skill drains it. This engine has no bonus for stamina above 1200 at this distance on Global settings.
- **Acceleration decides front races.** Tokyo 2400 starts with a long run to the first corner, and the front that gets out first takes the inside line and the lead. Every acceleration skill on a front is a top-5 skill by value.
- **Mood is about 5pp per step and you can't build for it,** so don't over-read one LoH run: a single 175-race batch swings ±2.5pp from luck.

### Priority order for stats

1. **Power, wit and guts to 1200.** These are the most valuable points in the build. Neo takes power to 1250.
2. **Stamina to the need:** fronts 1050–1100; Kitasan 1200 only if she carries Racing Spirit + Mad Dash; Neo 1000.
3. **Everything left into speed,** up to 1500.
4. **If you must come up short,** short guts first (0.7–1.1pp per 100), then wit or power (1.2–2.1pp per 100). Never buy guts or wit above 1200 while any of the three is under it.
5. **If you overshoot stamina** (common in training), each 100 extra on a front costs about 0.25pp; on Neo it costs almost nothing. It's the cheapest mistake to make.

### Goal builds

In-game cost in brackets (budget 6400; points above 1200 cost 2).

| Uma | Ideal (6400) | Good enough (about 6200) | Floor (about 6000) |
| --- | --- | --- | --- |
| Kitasan | 1430 / 1100 / 1230 / 1175 / 1200 | 1350 / 1100 / 1200 / 1200 / 1200 \[6200\] | 1350 / 1050 / 1200 / 1100 / 1150 \[6000\] |
| Kitasan with Racing Spirit + Mad Dash | 1380 / 1200 / 1200 / 1200 / 1200 \[6360\] | 1350 / 1200 / 1200 / 1150 / 1200 \[6250\] | Drop the two skills; use the floor above |
| Ines | 1430 / 1050 / 1245 / 1200 / 1200 | 1350 / 1100 / 1200 / 1200 / 1200 \[6200\] | 1350 / 1050 / 1200 / 1100 / 1150 \[6000\] |
| Neo | 1450 / 1000 / 1250 / 1200 / 1200 | 1375 / 1000 / 1250 / 1150 / 1200 \[6200\] | 1350 / 1000 / 1200 / 1150 / 1150 \[6000\] |

Expected cost of each step down: about −0.5 to −1pp team top-3 per uma from Ideal to Good enough, and −1.5 to −2pp per uma from Good enough to Floor (the floor cuts below 1200, where points are expensive).

Acceptable ranges when you can't hit a line exactly:

| Stat | Kitasan | Ines | Neo |
| --- | --- | --- | --- |
| Speed | 1350–1500, more is better | 1350–1500, more is better | 1350–1500, more is better |
| Stamina | 1050–1150 (1200 with RS + MD) | 1000–1150 | 950–1050 |
| Power | 1200–1250 | 1200–1250 | 1250 (1200 minimum) |
| Guts | 1150–1200 | 1150–1200 | 1150–1200 |
| Wit | 1200 | 1200 | 1200 |

### Priority order for skills

| Tier | Fronts (Kitasan, Ines) | Neo |
| --- | --- | --- |
| Must have | Distance S; Left-Handed ◎; Spring Runner ◎; Solid Preparation; Taking the Lead (Ines); Red Shift/LP1211-M | Distance S; Left-Handed ◎; Spring Runner ◎; Superb Gait; 1,500,000 CC; Medium Corners ○ |
| Strong | Dodging Danger; Hesitant Front Runners; Top Runner; Superb Gait; Divine Speed; Front Runner Straightaways ◎; Medium Straightaways ◎; Ignited Spirit WIT | Moving Past, and Beyond; Into High Gear!; Divine Speed; Uma Stan; Hesitant Front Runners; Professor of Curvature; Late Surger Corners ◎; Groundwork; Restraint |
| Good filler | Restraint; Professor of Curvature; Straightaway Adept; Wisdom of the Sun; Racing Spirit + Mad Dash (only with the stamina) | Wisdom of the Sun; Medium Straightaways ◎; Corner Adept ○; Nimble Navigator; Position Pilfer; Playtime's Over!; Racing Spirit: Stamina |
| Skip | Moving Past / Into High Gear / Bring on the Banquet (don't fire for fronts); Prudent Positioning; Firm Resolve; Standard Distance ○ | Be Still; With All My Soul; Operation Cacao; Bring on the Banquet |

### Substitutes when the ideal isn't available

| Missing | Use instead | Expected cost |
| --- | --- | --- |
| Solid Preparation | Groundwork | about −1pp (Ines); still keep Groundwork, worth 2.8pp on Kitasan |
| Taking the Lead | No real substitute; add Groundwork-group or Red Shift if missing | about −2.8pp; both front accel skills missing ≈ −12pp |
| A ◎ green (Left-Handed, Spring Runner) | The ○ version | −0.4 to −0.5pp each |
| Medium / Front Runner Straightaways ◎ | The ○ version | about −0.5pp |
| A gold speed skill | Two cheap whites that fit (Medium Corners ○, Straightaway Adept, Uma Stan on Neo) | often break-even; the gold is 2.0–2.5 speed × time vs 1.08 per white |
| Red Shift inherit | Any other early-accel inherit that fires for fronts | depends on trigger; Moving Past and Into High Gear don't fire for fronts |
| Distance S | Nothing replaces it | distance A on a mock was worth about 7.7pp to the field |
| 1200 wit or power | Fill it before adding speed | 1.2–2.1pp per 100 short |
| Enough stamina for Racing Spirit + Mad Dash | Drop the skills and move the stamina into speed | the skills are worth +1 to +1.9pp only at the right stamina |

### Team-level rules

- **Two fronts share one lead.** Skills that only help one front pass the other (Tail Held High, Playtime's Over! on Ines) don't help the team. Prefer skills that beat the enemy: Hesitant Front Runners slows enemy fronts.
- **Neo is the team's swing slot.** She has the lowest top-3 (77%) and loses the most from gates 2–3 and late starts, so her skill points go to late-race speed and acceleration, not stamina.
- **Judge builds over many batches.** Two builds within 2pp can't be told apart in one LoH run.

## Limits and caveats

- **Simulator, not the game.** GlobalSim reproduces Global race mechanics closely, but some skills are converted from an older table (marked approximated); their triggers can differ slightly from the game. Results for those skills are best read as direction, not exact size.
- **Mock field, not the real one.** All percentages are against the mock spec in this report. The real LoH field was weaker (the CN team scored 97.1% there vs 79.9% here), so expect higher absolute numbers in game; the ranking of builds should hold.
- **Single-skill noise.** Adding a skill that never fires still moves results by up to ±0.8pp. Skill values with intervals crossing zero are "no clear effect", not "zero".
- **Skill values were measured on the starting builds.** Values shift a little as builds change, especially for skills that overlap (two accel skills, two straightaway skills).
- **Search depth.** The search ran 8 rounds. Kitasan with Racing Spirit + Mad Dash at 1200 stamina dropped out early and was never retested against the final team; it is the strongest open lead. Killer Tunes on Ines was not tested.
- **Data on disk.** Every table in this report is in the project's data/loh/results folder (skill table, search history, validation summary), committed locally.
