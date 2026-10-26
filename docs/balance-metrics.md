# Balance metrics without the bot

Status: built (`levels/balance.py`, `scripts/metrics/route_metrics.py`, `scripts/tools/playtest.py --fight`). The design below is as first written; "As built" at the end records where the build departs from it and why. Covers a static resource curve and static exposure checks, both run at build time, and a `--fight` bot that fails fast and labels its own deaths.

## Why

`--fight` costs builders hours, and most of that time measures the bot, not the map. Building MAP06 (Nukage Turbine), the fight phase went like this:

- Runs that didn't finish: the bot walked behind a desk (seed 2), lost a door that shut mid-fight (seeds 1 and 3), and strafed off a lift in the middle of a fight (seeds 1 and 2). Each one meant an edit to the playtest script and another run.
- One run went into a loop of 503 deaths at one spot and took 9 minutes to fail (`walk_to` re-plans up to 40 times per leg, and buddha mode keeps healing).
- One real signal, "no shells or bullets at the return fight", couldn't be told apart from the bot's waste: it had fired 130–148 bullets at range on gantry B. A map change was made on that evidence and pushed the UV ammo ratio from 1.95 to 2.26, past the doc's 1.6–2.2 target.
- Deciding map or bot meant rendering video, pulling frames and reading them. That's the most expensive step in `doom-test`, and it needs judgement every time.

The problems the skill asks about ("out of ammo before a fight ends", "a start under fire", "sniping across a gap") are mostly questions about resource order and geometry. They can be answered from the map, deterministically, in seconds.

## Scope

| Part | Where | Needs ViZDoom |
|---|---|---|
| A. Resource curve | `levels/balance.py`, printed by `build()` | no |
| B. Exposure checks | `levels/balance.py`, printed by `build()` | no |
| C. Fail-fast, self-labelling bot | `scripts/tools/playtest.py --fight` | yes |

Not in scope: changing the `doom-test` skill's contract (beyond documenting the new output), modelling player skill, and judging fun or vanilla rendering. Those still need dsda-doom.

## What the reach model gives us

`reach.solve(m, textures)` returns `(model, res)`. Facts the design relies on, from `levels/reach.py`:

- `Model.run()` is a fixpoint over **waves**. Each wave computes `R`, the regions reachable from the start, and then fires *every* key, trigger, exit and boss action whose site is in `R`. Snapshots `(base, man, keys, R)` are kept per wave.
- Sites are regions: `res["key_site"]`, `res["trig_site"]`, `res["exit_site"]`, along with the wave each one fired in.
- `R` is recomputed from the start each wave, so it never shrinks. A one-way drop doesn't remove the regions above it.
- There's no player position and no walk order. Wave order is dependency depth: a closet trap and the key that springs it can fire in the same wave.
- `run(off_groups=..., off_keys=...)` re-runs with triggers or keys disabled. That's how we tell required objectives from optional ones.
- `closure(...)` with `can_pass` respects heights, so a path over the region graph is physically one-way where the map is.
- `monster_closure(res, start, actor)` gives the regions a monster can get to.
- `shoot_site(target, tsec, R, base, man)` is a height-aware straight-line hit test, up to `MISSILE_RANGE`.
- `self.monsters[type]` holds `(region, point)` for each monster. Pickups aren't located yet: `region_of_point` does it.

## A. Resource curve

### Route: waves split by path order

1. **Required objectives.** For each key and trigger group the run fired, re-run with it disabled (`off_keys`/`off_groups`). If the normal exit becomes unreachable, it's required. These are the route's waypoints. On MAP06 they should come out as the blue key, the yellow key (its ring sinks the cradle), EL's passage line, the floodgate switch and the exit. That's from the design doc; it hasn't been computed yet.
2. **Order within a wave.** Objectives that fired in the same wave are visited nearest-next, by path distance from the current position. The next wave's objectives only become available once the current wave's are done.
3. **Legs.** One leg per objective. Its path is the shortest path over the region graph, under that wave's snapshot state, from the previous objective's site (the start, for the first) to this one. Distances run between region centroids, plus the extra distance `moves_nonwalk` already reports for gaps, jumps and teleports. The path respects one-way drops because `can_pass` does.
4. **Phases** are legs, labelled by the objective and its site's sector name (e.g. `blue key @ ped_b`, `W1 lower tag 2 @ cd`, `exit @ exit_niche`). Modules know their sector names; IWAD and decompiled maps fall back to sector numbers.
5. **Triggers along the way.** An optional trigger fires on the first leg whose path passes through its site region (closets, lights, AR1/AR2 on MAP06). That's where its monsters get released.

### Monsters: engaged, or in a side room

A monster on the current skill is **engaged** on the first leg where any of these is true, given that leg's state:

- its region is on the leg's path;
- `monster_closure` from its region reaches a region on the path (it can come to you);
- it has a shot at a region on the path (`shoot_site` from its point, within `MISSILE_RANGE`). Deaf monsters still wake on sight, so the ambush flag doesn't exempt them.

Monsters that are never engaged are optional. Their connected optional regions, each with its monsters and items, form a **side room**. Each side room is reported as one line: monster HP, ammo damage, health, net. A side room with negative net ammo makes the thorough curve optimistic, and gets flagged.

### Supply: two curves

Both curves count ammo as damage, like `checks.balance_report`: `DAMAGE_PER_AMMO`, pistol start, monster drops (credited on the leg the monster is engaged). Ammo for a weapon the player doesn't have yet is held back until they do.

- **Thorough (upper bound).** An item counts on the first leg whose snapshot `R` contains its region. That's everything reachable so far, secrets included, side rooms included. It's set against **engaged HP only**: the most generous player, picking up everything and fighting only what they must. **If this curve runs out, the map starves.**
- **Detour-budgeted.** An item counts on a leg if a round trip off that leg's path gets it within budget `D`: path distance from the nearest path region to the item's region and back, with `can_pass` both ways. So items behind a one-way drop off the path don't count. Items in secret areas (sector special 9, or behind `ML_SECRET` doors) don't count. `D` defaults to 1024 (512 each way), pending calibration. This is the normal player.

### Carrying, not just totals

Each curve is simulated leg by leg, not summed:

```
carried = min(cap, carried + pickups on this leg)   # per ammo type; a backpack doubles caps
carried -= damage needed for this leg's engaged monsters  # from a single damage pool, best weapon first
```

Health uses the same walk: pickups (capped at 100, 200 for soulspheres), set against a nominal cost per engaged HP. That cost is calibrated from the IWAD, so the column means "health left at the IWAD's typical attrition", not a prediction.

### Output

Printed after the measurement table, at UV by default (`--skill` for others):

```
resource curve (UV, pistol start)       thorough      detour D=1024
 #  phase                      path  eng.HP  ammo left  ratio  ammo left  ratio  health
 1  blue key @ ped_b            1410    1210       2380   2.9       1630   2.3      82
 2  W1 lower tag 2 @ cd         1980    3420       2910   1.8       1150   1.3      61
 3  W1 open tag 4 @ bp3         1120    2350       1840   1.6        420   1.1      48
 4  S1 lower tag 6 @ fg_niche   1460    2100       2600   1.6        310   1.0      55   !! detour < 1.1
 ...
side rooms: sv  -210 ammo  (HP 640, ammo 430)  ...
```

The numbers above are illustrative, not measured. `ratio` is cumulative supply over cumulative engaged HP.

- **Error** when thorough `ammo left` < 0 on any leg.
- **Warning** when detour `ratio` falls below the threshold on any leg, or a side room's net ammo is negative.

Two summary numbers go into `measure.py` with IWAD ranges, like the other targets: **minimum detour ratio over legs** and **minimum thorough ammo left as a share of engaged HP so far**.

### Calibration

Thresholds come from the DOOM II IWAD, like the repo's other targets. `scripts/metrics/route_metrics.py` (stdlib, like its siblings) writes `research/data/metrics_route.csv`: for MAP01–MAP32 at each skill, the per-leg curves and the two summaries. The thresholds are the IWAD's low quantiles (say the 10th percentile of minimum detour ratio). `D` is chosen so that id's maps sit comfortably inside it.

## B. Exposure checks

All of these reuse the route and engagement data from A.

| Check | Rule | Level |
|---|---|---|
| **Start under fire** | A monster on the skill, ambush or not, with a shot at the start region and the start inside its 180° facing cone, or within 64 units of the start. | error |
| **Long-range hitscan** | Per path region: the summed expected hitscan damage per second (per-type constants for zombieman, shotgun guy, chaingunner, SS, spider mastermind) from engaged hitscanners with a shot at it from beyond 768 units. Report each leg's maximum. | warning above the IWAD's 90th percentile |
| **Trap pressure** | For each trigger fired on the path: the HP of monsters engaged because of it, against ammo carried at that moment on the detour curve; the nearest such monster's distance from the trigger site; and whether the way back from the site is still open in the next state (no retreat: the cradle, for example). | warning when carried ammo damage < released HP; info otherwise |

A separate "can't answer" check was considered and dropped. Sight is symmetric, and the pistol reaches anything within `MISSILE_RANGE`, so the player can always shoot back at anything that can hit them. What "sniping across a gap" actually costs is long-range attrition, which the long-range hitscan check measures.

## C. Fail-fast, self-labelling bot

The changes are to `--fight` only. Wiring runs keep failing hard on a stuck step.

- **Stuck doesn't end the run.** On `Abort` in a step (stuck, no way, interrupted by fighting too often), record `STUCK` with its step line, position and clock, `warp` to the step's target, and carry on. The report counts these as bot problems.
- **Death loops.** Three deaths within 128 units and 30 s of each other count as a loop. Record `LOOP`, `warp` to the next step's target, and carry on.
- **Time cap.** `--max-time` in game minutes (default 15). When the clock passes it, the run ends with a partial report.
- **Death labels**, decided at the moment of death from state the runner already reads:

  | Label | Rule | Usually |
  |---|---|---|
  | `starved` | no ammo for any weapon but the pistol and fist | map, if A agrees; bot otherwise |
  | `stuck` | no progress in the 2 s before death | bot |
  | `hazard` | standing on a damaging floor | bot |
  | `unseen` | damage taken in the last 1 s with no monster in the labels buffer | map (an ambush) |
  | `combat` | anything else | read the numbers |

  The report shows labels per section and in the death list. `starved` deaths are checked against A's detour curve for that phase: "starved, curve says 1.3 → bot waste" or "starved, curve says 0.8 → map".
- **Range discipline.** No pistol or chaingun past 768 units. Stop shooting at a monster it hasn't damaged in 3 s (extend the existing `self.ignore`). On MAP06, gantry B cost 130–148 bullets this way.

## Validation

- **A on known cases.** NUKAGE MAP01–MAP06 and the DOOM II IWAD. Each map's curve takes under 5 s. The test case is `nukage_turbine` without the two shell boxes added during its playtest (UV ammo ratio 1.95). The curve has to say whether the return fight was short on ammo for a normal player. That's the question the bot couldn't answer.
- **A against `balance_report`.** Thorough ammo at the last leg, without caps, equals `balance_report`'s total. That pins the accounting.
- **B.** Plant a hitscanner facing a test map's start and watch it error, then turn it round and give it a wall: no error.
- **C.** Re-run MAP06's three seeds with the original script, without the waypoint workarounds. Every seed should finish, each in under 2 minutes of wall time, with its stuck spots and loops labelled.

## Open questions

- `D`, the health cost per HP, and the thresholds wait for the IWAD calibration.
- The spend model uses one damage pool. Per-type spending (shells before bullets, say) would be more accurate, at the cost of a weapon-choice model. Start with the pool.
- Nearest-next order within a wave is a heuristic. A map whose intended order differs could set it explicitly with an optional `ROUTE = ["blue key", ...]` in its module. Add that only if a map needs it.
- Multiplayer-only and skill-flagged things follow `balance_report`'s rules.

## As built

Calibrating on the id maps (`route_metrics.py`, 68 maps, about 40 s) overturned several of the design's absolute rules. The id maps are the reference for what a playable map looks like, so the rules follow them.

**Route.** The legs come from `progression_metrics.analyse`, which already computed this critical path: required keys and triggers by disabling each one, then the best order within a wave (all permutations up to 6), not nearest-next. It now also returns the legs.

**Engagement** needed three changes to stop it from engaging nearly the whole map on the first leg:

- Monsters move with manual doors shut: a monster that hasn't been woken doesn't open doors. Before this change, MAP06's sump spectres "reached" the hall floor through a DR door and engaged on the first leg.
- Demons and spectres engage only by walking to the path. Sight engagement is for monsters that shoot.
- Sight engagement counts from anywhere the monster can walk, but only within `ENGAGE_RANGE` (1024). A monster that can only hit the route from farther away is a nuisance, and the hitscan check covers it.

Also, the last leg of each wave is checked under the next wave's state too, because triggers fired in a wave (closets, a sinking floor) are sprung while walking it.

**Carry caps** are applied after each leg's fights rather than at each pickup. Pickups and fights interleave within a leg, and capping at pickup made long single-leg id maps starve.

**No errors.** A quarter of the DOOM II maps run short on the thorough curve too (median lowest thorough share 0.11, lower quartile −0.69), and 9 of 32 DOOM II maps (18 of 36 Ultimate Doom maps) have a monster that can shoot the start and faces it. Every finding is a warning, and the two curve summaries, the hitscan peak and the health rate go into the measurement table with id's quartiles:

| measure | DOOM II quartiles | Ultimate Doom quartiles |
|---|---|---|
| lowest ammo ratio near the route (detour) | 0.32 / 0.65 / 1.54 | 0.59 / 0.89 / 1.57 |
| lowest ammo left / HP, taking everything | −0.69 / 0.11 / 0.73 | −0.46 / 0.01 / 0.54 |
| long-range hitscan peak per second | 0 / 0 / 35.5 | 0 / 10 / 21.5 |
| health per 1000 HP the route affords | 9.9 / 17.3 / 30.7 | 16.7 / 22.0 / 45.4 |

Warnings fire on legs below the id maps' 10th percentile of the detour ratio (0.147 DOOM II, 0.402 Ultimate), above the 90th percentile of the hitscan peak (88.4 and 46), on any leg where the thorough curve runs short, on traps that release more HP than the ammo in hand, and on starts under fire.

**Health.** The cost per HP is the DOOM II median of the highest rate each map's detour route can afford (17.3 per 1000 HP). So the column reads "health left if the fights cost what the median id map's route can afford". That rate, per map, is the new "health per 1000 HP the route affords" measure.

**Side rooms** are listed but don't warn: the id maps routinely have closets that cost more ammo than they hold.

**Traps.** "Ammo in hand" is the pool after the trigger leg's pickups and before its fights, an optimistic figure, so a warning means the trap is short even then. Lifts aren't counted as traps. For "no way back", `reach.run` now also snapshots current heights (`snap_now`), because `base` keeps every height a sector has ever had, so a sunk floor would still look climbable.

**Not calibrated:** `DETOUR` stays 1024. `HITSCAN_DPS` is rough, but only its ratios matter, because the threshold is calibrated with it.

**Bot (part C).** Built as specified, with two exceptions:

- Not built: "stop shooting at a monster it hasn't damaged in 3 s". ViZDoom's state has no monster health, so the existing 5-second give-up stays. The no-bullets-beyond-768 rule is in.
- `starved` deaths aren't checked against the curve automatically, because script sections don't map onto curve legs. The report prints a reminder to check the build's curve instead.

### Validation

- **MAP06 without the two shell boxes added during its playtest.** The curve shows the shell boxes weren't needed. The detour curve reaches the boiler passage with 2,970 ammo damage in hand. It then has 3,890 left after the return fight (1,760 HP) and 2,740 at the exit, a lowest detour ratio of 1.17, above id's median. The bot's ammo trouble was its own waste. The build also flags a start under fire: the HMP/UV cacodemon over the gantry break (864,560) faces the start booth's window exactly side-on (90°, which vanilla counts as in view).
- **MAP06 fights, same WAD, the script without its bot workarounds.** All three seeds ran to the exit, in 72–83 s of wall time each, run in parallel.

  | Seed | Deaths | Labels | Steps skipped |
  |---|---|---|---|
  | 1 | 36 | 26 starved, 6 combat, 3 stuck, 1 unseen | 9 |
  | 2 | 10 | 7 combat, 3 starved | 2 |
  | 3 | 21 | 9 combat, 7 starved, 5 stuck | 3 |

  Before these changes the same map's runs failed outright or took 9 minutes to fail in a 503-death loop.
- **Tests.** `tests/test_balance.py` covers detour versus thorough pickup, start under fire by facing, and engaged HP paid from the pool.
