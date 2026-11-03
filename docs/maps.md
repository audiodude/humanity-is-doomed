# The maps

The nine maps in `wads/NUKAGE.WAD`, each measured against the DOOM II maps with the research scripts (see the [builder docs](builder.md#what-every-build-checks)). Routes and secrets are in [SPOILERS.md](../SPOILERS.md).

## Nukage Outskirts (`nukage_outskirts`)
MAP01, the easiest map in the set: 104 sectors, 12/22/31 monsters on easy/medium/hard, four secrets, nothing heavier than a demon. Its design doc is `levels/designs/nukage_outskirts.md`, with the playtest results; the route script is `levels/playtests/nukage_outskirts.playtest`.

You start in a sunlit valley below a hillside cut into switchback shelves, with the plant's monitoring station on the crest. Its front shutter is jammed; you get in through the loading dock round the back, find the blue key in the instrument room, and the blue door at the top of the stairs opens onto the observation deck. The far side of the ridge drops into a valley filled wall to wall with nukage, and the jetty across it leads to the exit in the plant's wall.

| Measure | MAP01 | DOOM II median |
|---|---|---|
| Distinct floor heights | 32 | 23 |
| Light SD / light-effect sectors | 24 / 7 | 23 / 9 |
| Most-used wall texture | 33% | 30% |
| Wall material changes with a border texture | 99% | 31% |
| Optional share of the reachable area | 47% | 50% |
| UV ammo per monster HP (pistol start) | 2.66 | 1.81 |
| Health per 1000 monster HP | 83 | 40 |
| Easy/UV and HMP/UV monster ratios | 0.39 / 0.71 | 0.33 / 0.70 |
| Deaf monsters | 39% | 42% |
| Nearest monster to the start | 643 | 300 |

Ammo and health are generous on purpose for a first map; the secret soulsphere is 100 of the health.

The original MAP01, Nukage Junction (`levels/nukage_junction.py`, a courtyard hub with a wing per key), is kept in the repo but is no longer in the set: `python3 -m levels nukage_junction` builds it to `wads/scratch/nukage_junction.WAD`.

## Nukage Crossing (`nukage_crossing`)
MAP02, designed from the [research](../README.md#research-what-makes-doom-levels-fun) below: 99 sectors, 21/43/57 monsters on easy/medium/hard, four secrets. It was retextured after the texture research (design: `levels/designs/nukage_crossing.md`): one brick for the whole canal basin, a signature material per area, and trim where materials meet. The first version's textures are kept in `levels/nukage_crossing_original.py`, which isn't built into the WAD.

Measured with the research scripts against the DOOM II maps (median in brackets):

| Measure | MAP02 | DOOM II median |
|---|---|---|
| Rule-1 flat changes without a height change | 1% | 3% |
| Distinct floor heights | 22 | 23 |
| Light-effect sectors | 11 | 9 |
| UV ammo per monster HP (pistol start) | 2.1 | 1.8 |
| Health per 1000 monster HP | 58 | 40 |
| Easy/UV and HMP/UV monster ratios | 0.37 / 0.75 | 0.33 / 0.70 |
| Deaf monsters | 37% | 42% |
| Nearest monster to the start | 487 | 300 |
| Most-used wall texture (BRICK6) | 28% | 30% |
| Material joins with a border texture | 81% | 31% |

No monster can see the start window. Whole-map symmetry (0.82) is above the id range, because the two banks mirror each other across the canal; they are told apart by their landmarks: the pump housing, the silver tower, the red-key platform and the terrace.

## Nukage Divided (`nukage_divided`)
MAP03: 112 sectors, 23/43/56 monsters on easy/medium/hard, four secrets, and the first barons. Its first version, Nukage Divide, is kept as `levels/nukage_divide_original.py` and built on its own into `wads/DIVIDE.WAD` (set `levels/sets/divide.py`).

You leave the start room facing a wall that is half lava, half blue computer screens: a red furnace wing on one side, a blue cooling wing on the other. The wings never meet, and each ends at its own key beside a locked arena door of the other colour, with the other key in sight across a nukage pit.

| Measure | MAP03 | DOOM II median |
|---|---|---|
| Rule-1 flat changes without a height change | 2% | 3% |
| Distinct floor heights | 23 | 23 |
| Light SD / light-effect sectors | 39 / 11 | 23 / 9 |
| Most-used wall texture | 26% | 30% |
| UV ammo per monster HP (pistol start) | 1.8 | 1.8 |
| Health per 1000 monster HP | 36 | 40 |
| Easy/UV and HMP/UV monster ratios | 0.41 / 0.77 | 0.33 / 0.70 |
| Nearest monster to the start | 563 | 300 |
| Whole-map symmetry | 0.71 | 0.54 |

Symmetry is high because the two wings mirror each other's footprint around the fork and the pit; their materials, lighting and monsters are opposites.

## Nukage Tower (`nukage_tower`)
MAP04, also designed from the research (built as Nukage Core, and renamed): 112 sectors, 27/53/73 monsters on easy/medium/hard, five secrets. It introduces the mancubus. It was retextured after the texture research (design: `levels/designs/nukage_tower.md`): one bronze cladding for the whole atrium and its stair towers, the reactor core in green tech panels, a signature material per wing, and trim where materials meet. The first version's textures are kept in `levels/nukage_tower_original.py`, which isn't built into the WAD.

A reactor core stands in a nukage moat, with the exit in the crown on top; you see it from the start and climb around it to get there.

Measured with the research scripts against the DOOM II maps:

| Measure | MAP04 | DOOM II median |
|---|---|---|
| Rule-1 flat changes without a height change | 0% | 3% |
| Distinct floor heights | 29 | 23 |
| Light-effect sectors | 10 | 9 |
| Optional share of the reachable area | 40% | 50% |
| Heavy-monster share (UV) | 15% | 10% |
| UV ammo per monster HP (pistol start) | 2.7 | 1.8 |
| Health per 1000 monster HP | 38 | 40 |
| Easy/UV and HMP/UV monster ratios | 0.37 / 0.73 | 0.33 / 0.70 |
| Deaf monsters | 48% | 42% |
| Nearest monster to the start | 353 | 300 |
| Most-used wall texture (BRONZE2) | 36% | 30% |
| Material joins with a border texture | 77% | 31% |
| Whole-map symmetry | 0.62 | 0.54 |

## Nukage Undercurrent (`nukage_undercurrent`)
MAP05: 118 sectors, 26/46/64 monsters on easy/medium/hard, four secrets, and the first arachnotrons and revenants. Its design doc is `levels/designs/nukage_undercurrent.md`.

You cross the turbine hall on a railed gantry along its north wall, looking down at the exit door, the turbines and a floodgate across the floor. At the far end, taking the yellow key sinks the platform you're standing on into a pit of demons, and the only way back is along the hall floor, under the gantry, where arachnotrons now walk.

| Measure | MAP05 | DOOM II median |
|---|---|---|
| Distinct floor heights | 24 | 23 |
| Light SD / light-effect sectors | 35 / 12 | 23 / 9 |
| Most-used wall texture | 22% | 30% |
| Wall material changes with a border texture | 96% | 31% |
| Optional share of the reachable area | 42% | 50% |
| UV ammo per monster HP (pistol start) | 2.26 | 1.81 |
| Health per 1000 monster HP | 47 | 40 |
| Easy/UV and HMP/UV monster ratios | 0.41 / 0.72 | 0.33 / 0.70 |
| Deaf monsters | 42% | 42% |
| Nearest monster to the start | 511 | 300 |

## Nukage Drain (`nukage_drain`)
MAP06: 83 sectors, 24/43/59 monsters on easy/medium/hard, four secrets, and the first lost souls. Its design doc is `levels/designs/nukage_drain.md`.

You start on the only dry catwalk of a reservoir full of nukage, with the exit vault standing in the middle. Each of three pump houses has a switch beside an opening onto the reservoir: throw it and watch the next walkway rise out of the sludge to take you onward, while whatever was waiting inside the vault's pillar comes out at you.

| Measure | MAP06 | DOOM II median |
|---|---|---|
| Rule-1 flat changes without a height change | 0% | 3% |
| Distinct floor heights | 12 | 23 |
| Most-used wall texture | 30% | 30% |
| Wall material changes with a border texture | 100% | 31% |
| Light SD / light-effect sectors | 24 / 9 | 23 / 9 |
| Optional share of the reachable area | 36% | 50% |
| UV ammo per monster HP (pistol start) | 1.9 | 1.8 |
| Health per 1000 monster HP | 35 | 40 |
| Easy/UV and HMP/UV monster ratios | 0.41 / 0.73 | 0.33 / 0.70 |
| Nearest monster to the start | 697 | 300 |
| Whole-map symmetry | 0.64 | 0.54 |

It has fewer floor heights than most id maps because the reservoir is one flat pool and each pump house is one floor; symmetry is high because it's a square reservoir with a pump house off each side.

## Nukage Storage (`nukage_storage`)
MAP07: 187 sectors, 30/54/75 monsters on easy/medium/hard, four secrets, and the first pain elemental.

You look over a spent-fuel store from a gallery: a maze of steel casks under lit aisles, the yellow key on a blue-lit cask stack, the control tower's window high in the far wall, and blast shutters under an EXIT sign. You thread the maze at floor level to the tower, and the switch in its cab sinks every cask into the floor at once. The maze becomes an open hall, and the six mancubi sealed among the casks are standing in it, each in the nukage its cask leaked. DOOM II's own MAP07 rule opens the way out: the shutters drop when the last mancubus dies.

| Measure | MAP07 | DOOM II median |
|---|---|---|
| Rule-1 flat changes without a height change | 3% | 3% |
| Distinct floor heights | 33 | 23 |
| Light SD / light-effect sectors | 25 / 10 | 23 / 9 |
| Most-used wall texture | 30% | 30% |
| Optional share of the reachable area | 67% | 50% |
| Heavy-monster share (UV) | 20% | 10% |
| UV ammo per monster HP (pistol start) | 2.4 | 1.8 |
| Health per 1000 monster HP | 44 | 40 |
| Easy/UV and HMP/UV monster ratios | 0.40 / 0.72 | 0.33 / 0.70 |
| Nearest monster to the start | 488 | 300 |
| Whole-map symmetry | 0.59 | 0.54 |

## Nukage Lockdown (`nukage_lockdown`)
MAP08: 120 sectors, 33/53/72 monsters on easy/medium/hard, four secrets, and the first arch-vile. Its design doc is `levels/designs/nukage_lockdown.md`, with the playtest results; the route script is `levels/playtests/nukage_lockdown.playtest`.

You start in a locked-down lobby looking through a window at the exit switch under its EXIT sign, and the only way out leads away from it. The route circles the plant's nukage spill basin, through buildings on its banks, past the burst storage tank pouring nukage down a channel into it, and closes by wading the basin in a radiation suit, through the drainage culvert into the decontamination hall where the arch-vile waits. Every lockdown shutter opens only from its far side.

| Measure | MAP08 | DOOM II median |
|---|---|---|
| Distinct floor heights | 25 | 23 |
| Light SD / light-effect sectors | 25 / 15 | 23 / 9 |
| Most-used wall texture | 27% | 30% |
| Wall material changes with a border texture | 99% | 31% |
| Optional share of the reachable area | 43% | 50% |
| UV ammo per monster HP (pistol start) | 2.30 | 1.81 |
| Health per 1000 monster HP | 45 | 40 |
| Easy/UV and HMP/UV monster ratios | 0.44 / 0.70 | 0.33 / 0.70 |
| Deaf monsters | 100% | 42% |
| Nearest monster to the start | 304 | 300 |
| Whole-map symmetry | 0.70 | 0.54 |

Symmetry is high because the loop runs round a square basin; each bank is its own material, height and light.

## Nukage Meltdown (`nukage_meltdown`)
MAP09, the last map: 137 sectors, 40/63/84 monsters on easy/medium/hard, four secrets, and the Cyberdemon. Its design doc is `levels/designs/nukage_meltdown.md`, with the playtest results; the route script is `levels/playtests/nukage_meltdown.playtest`. Its exit opens only when the Cyberdemon dies, which needs a port that reads UMAPINFO (see [Compatibility](../README.md#compatibility)); those ports also show an end text after it and then the cast call. The end text is the `intertext` list in MAP09's `UMAPINFO` lines in the set file, `levels/sets/nukage.py`.

From the operations balcony at the start you see the whole map: the plant's outfall runs down a canyon in four terraced shelves, each pond pouring over a railed lip onto the next, down to the reactor's cooling lake and the cracked dome in it. Something huge is down there: you hear it more than see it. You go down shelf by shelf, through the buildings at each bank's end, drop through a breach in the third shelf, open the floodgate from the gatehouse and ride the dam's falls into the lake, where the Cyberdemon wades. As you land, the dome's hatch opens, and the arch-vile is waiting in the exit alcove at its back.

| Measure | MAP09 | DOOM II median |
|---|---|---|
| Distinct floor heights | 35 | 23 |
| Light SD / light-effect sectors | 40 / 10 | 23 / 9 |
| Wall material changes with a border texture | 92% | 31% |
| Optional share of the reachable area | 59% | 50% |
| UV ammo per monster HP (pistol start) | 2.23 | 1.81 |
| Health per 1000 monster HP | 47 | 40 |
| Easy/UV and HMP/UV monster ratios | 0.48 / 0.75 | 0.33 / 0.70 |
| Deaf monsters | 91% | 42% |
| Nearest monster to the start | 667 | 300 |
| Whole-map symmetry | 0.78 | 0.54 |

Symmetry is high because the shelves are full-width bands across one canyon; the buildings at their ends alternate sides, and the lake round the dome is open.
