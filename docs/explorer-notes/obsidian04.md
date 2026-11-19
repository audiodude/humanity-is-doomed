# OBSIDIAN04 MAP01: why the seeds never pressed tags 20/22/21 or found the yellow key

## 1. What the person did to get past
- 2:28-2:29, in the big room sector 374 (floor 64), standing at 48,216, the person used the switch on line 2236.
  That switch is the SW1STARG lower texture on the 64-unit face of the step up to sector 664 (floor 128).
  Sector 664 is a Boom generalized lift, type 13363 = 0x3433 (SR lift, tag 20). It went down and the person rode it up.
  Frame person.mp4 @2:28: two switch plates are visible at the foot of a 64-high grey STARTAN wall. Frame @2:30: the person is on the grey FLOOR0_5 lift.
- From 664/967 (floor 128, reachable only by this lift) they went west to sector 701 (floor 128). There, at 2:40, they used line 5288.
  Line 5288 is the same arrangement: SW1STARG lower texture, front 701 (floor 128), back 1098 (floor 256), type 13363 SR lift, tag 22.
  It took them up to the 256 level (sectors 378, 382). At 2:46 they used line 1324 (type 166, S1 ceiling raise, tag 21, SW1BROWN).
  That raised the ceilings of crawlway sectors 386-393 (ceiling 264 over floor 256), and at 2:52 they picked up the YellowCard at 40,855.
- The only way into that region is up lift 664. A sector-graph check over the WAD's static heights (step <=24, headroom >=56) gives two sets: from 374, 123 sectors that don't include 664, 967 or 701; from 701, 143 sectors that include 374. So from 701 you can drop back into the 374 region, but you can't get back up without the lift.

## 2. What each seed did instead
- All three seeds pressed tag 7 (line 3907, a plain switch in the same room 374, at 64,544) at 2:33, 2:40 and 3:03. That was their last progress.
  After that they wandered for about 12 minutes (most time in sectors 374, 197, 422, 614 and 28) until --max-time 15:00.
- Seed 1, re-run with debug prints in a worktree (the events matched the compare run exactly):
  - It first saw lines 2234, 2236 and 2238 (the lift's edge facing 374) at 2:29, from 1069,217.
  - It never chose line 2236 as a target. From 2:29 to 15:00 that line was never marked done, never marked failed, and never searched.
  - Its target choices: frontier cells, and door line 1467 eight times (type 16271, DOOR3, from sector 430 to 429).
    Each time it got stuck at 1532,1043 (z 80, sector 433); this is the S7 bot trap near 1408,1152, a separate navigation weakness. It also got stuck at 128,-792.
  - The wall search started at 8:04, at -1828,1260, but it ran out of reachable cells (1-6 options, stuck on the corner of pillar sector 132). In 15 minutes it searched only 3 walls (433, 461, 916).
  - From 9:33 to 14:00 it went to the places it had only seen from far away (the "unvisited" pass, 2000-6000 cells). At 14:33 it found door 272, and it stopped at 15:00.
- Seeds 2 and 3 have the same event list and start searching at the same spot (-1828,1260). [INFERENCE] They fail the same way: the exclusion described in section 3 doesn't depend on the seed.

## 3. Cause
Two gaps together hide the lift switch:
1. **The explorer leaves out the switch on purpose.** `Explorer.options()` (explore.py about line 635) drops any S1/SR line whose kind is "lift" when its back sector is open and tagged by that line.
   The comment says ride() will use that switch. For line 2236: kind "lift", back sector bs=664 (ceiling 448 > floor 128), and 664 is tagged 20, so the line is never a switch target.
2. **ride() never runs, because the game doesn't know 664 is a lift.** `pt.LIFTS = {10, 21, 62, 88, 120, 121, 122, 123}` (playtest.py:149) only lists vanilla types.
   So `Geometry.lifts` holds just sectors 266 and 319: it leaves out generalized lift 664 and the tag 22 sectors 1098, 1099, 1110, 1139 and 1140.
   The Planner treats 664 as a plain ledge 64 units up and never plans a route over it, so `lift_of()` never returns it and ride() is never called. The same goes for line 5288 and lift 1098, one level further on.
The wall search would eventually have tried line 2236: it is a step face too high to climb, and its switch texture counts as a cue, a quarter of the cost. But the search barely ran (3 walls in 7 minutes), so it never got there. That is a secondary weakness, not the cause.
Confidence: high. The exclusion and the LIFTS set come straight from the code plus the WAD's line types, and the debug run confirmed the line was seen and never done, failed or searched.
Inferred, not run: that pressing line 2236 would let the explorer through. The person's run shows the map itself works.

## 4. Classification
- **B-blind**, under the known blind spot "unread line types": the bot doesn't treat Boom generalized lifts (0x3400-0x37FF) as lifts. It reads the line as a lift switch, then counts on lift handling it doesn't have for that type.
- The Bot-limited rule doesn't apply. The person's first L press was at 1:36, in sector 86, before their own stall at 0:17-2:20. The seeds got stuck only after tag 7, at 2:33-3:03 (seed 1 first saw the switch at 2:29). The play stays scored.

## 5. Fix sketch
- Fill the lift sets from the decoded specials, not a hard-coded vanilla list: `{sp for sp in SPECIALS-used-in-map if SPECIALS[sp].kind == "lift"}`. That covers generalized and Boom extended lifts. It needs the perpetual-lift caveat already found on CHORD_NG.
  Or, as a smaller change, make options() skip a lift-edge switch only when its sector is in `geo.lifts`, meaning ride() can actually handle it.
- Even with 664 counted as a lift, ride()'s "call it" branch just faces the middle of the lift and presses use. Here only 32 of the 352 units of edge (line 2236, y 208-240) do anything.
  A use aimed elsewhere along the edge hits 2234 or 2238, which have no special, so the lift "didn't come" and gets marked dead. ride() should walk to the seen S1/SR line on the lift's edge that carries the lift's tag and use that, as its "going down" branch already does.
- Design rule: this is fine. A player sees the SW1STARG switch plate at the foot of the step (frame @2:28), and the switch is in the room the bot spent the most time in.
- It will come up again: the obsidian generator uses generalized lifts in OBSIDIAN02 (24 lines), 03 (5), 04 (8), 07 (11) and 10 (4). These are types 13361/13363/13369/13371/13651, each switch next to a WR call line. All of them miss `pt.LIFTS`.
