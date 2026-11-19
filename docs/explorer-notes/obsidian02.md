# obsidian02 (OBSIDIAN02.WAD MAP01): why the seeds ran out of things to try

## 1. What the person did to get past
- 0:19 stepped from the ledge (sector 82/83, floor -56) onto lift **sector 81** (LIFTFLAT, floor -64, tag 34) at (-2395,-2188). Its edges L246/L247/L5724 are walk-over lifts (special 13369 = Boom *generalized* lift WR, turbo, 1 s wait, to lowest neighbour floor), so it sank to -120 into the yellow-key pit (sectors 80/700/486/67, all floor -120).
- 0:21 pressed the switch L1703 (SW1COMP, tag 30, S1 floor_lower) by sector 485; 0:23 took the yellow key at (-2174,-2790).
- Then got back out the only way there is: at ~0:27 used the lift's face **L245** (special 13371 = generalized lift **SR**, turbo, 1 s wait; front sector 80, lower texture SUPPORT2 (dark hex), no switch texture), stepped on as it dropped and rode it up to -64, walking off north to sector 82/83 by ~0:28. Not a milestone (sector 81 had already moved), so not in report.txt. Seen in the person's replay: frames 0:27-0:27.5 face the dark hex SUPPORT2 face from the pit, 0:28 the view is at the upper level over the hex-floor room, 0:29 the stairs north.
- The pit has no other way up: sector 59 (floor -56) drops 64 into 486 (L5727/L5762), 82/83 are 64 above 700/80, all other neighbours are 32-unit-high trim (-88).

## 2. What each seed did instead
- All three went into the pit the same way the person did, by walking onto lift 81 from above (compare "switch, tag 34": seed 1 1:56, seed 2 2:13, seed 3 0:20), then pressed L1703 and took the yellow key (2:07 / 2:24 / 0:30). That was each seed's last progress.
- From then on they never left sectors 67 (~59%), 486 (~33%), 700, 80 (seed reports): 3:35 / 3:33 / 3:36 stretches. They ran "nothing left it knows to try" wall searches; each seed's search used L245 once ("found: using a wall by sector 80 moved sector 81", 2:26 / 2:43 / 1:49) - the lift went down - and then it stood and looked round (search(): press, 20 tics, look_round) and never stepped on. The lift came back up a second later. L245 is now in found_secs, not in `done`, so neither the "again" pass nor a ride ever uses it again.
- Stopped 5:42 / 5:57 / 4:06: "nothing left it knows to try (searched 65 walls, crossed 1-2 edges)".

## 3. Cause
**Sector 81 is not a lift to the explorer, because Boom generalized lift specials (0x3400-0x37FF) are missing from playtest.LIFTS.**
- `playtest.Geometry.lifts` comes from `LIFTS = {10, 21, 62, 88, 120, 121, 122, 123}` (playtest.py:149-252). Tag 34's lines are 13369/13371, so sector 81 isn't in `geo.lifts`; the Planner sees a plain floor at -64, 56 above the pit floor: no route up, so ride() (which calls a lift from beside it with use) never runs.
- At the same time `levels/doom2.BOOM_SPECIALS` *does* decode 13371 as `SR lift`, so explore.options() (explore.py:635) drops L245 as a switch target: "a switch on the lift's own side calls it, which ride() does". Two halves of the code disagree; the lift switch falls between them.
- Only the wall search touches L245, and it treats the result as a find to note, not a lift to ride (and the lift waits just 1 s).
- Same gap covers tags 39-42 (sectors 335/337/339/340, floor 188; 32 more generalized lift lines) elsewhere on the map; whether the person needed them is unverified.
- Verified: line/sector data from the WAD (heights, textures, specials decoded: trigger, turbo, 1 s delay, target LnF); LIFTS contents; options()/ride()/search() code paths; seed reports; person's replay frames (0:27 L245 used, up by 0:28); seed 1 replay frame at 2:26 shows it at the same hex face (its "found" press), then it turns away.
- **Patched run** (worktree at cfa4b69, only change: `sp in LIFTS or 0x3400 <= sp < 0x3800` in Geometry's lift_tags; WAD copied to /tmp so compare's recordings were untouched), seed 3 --max-time 4: same start (yellow key 0:30), then **left the pit by 0:45**, blue key 1:45, red key 2:09, and the person's tag-2 switch (sector 349/352, "switch S1 door by sector 492") at 3:37; was still progressing at the 4-min cap. Unpatched seed 3 stopped in the pit at 4:06. Confidence: very high.

## 4. Classification
- **B-blind**, known blind spot **"unread line types"** (generalized lift types read by SPECIALS but not by the lift model). Arguably a plain bug rather than a missing mechanic: the riding mechanic exists.
- All three seeds were in the pit for good by 2:13 (seed 3 from 0:20, seed 1 from 1:56, seed 2 from 2:13); the person's first L was at 2:17. So all seeds failed on a known blind spot before the first L press: **the Bot-limited rule applies** (narrowly, by 4 s for seed 2).

## 5. Fix sketch
- In playtest.py, make lifts include Boom generalized lifts: `0x3400 <= sp < 0x3800` (and, for consistency, generalized doors 0x3C00-0x3FFF / locked 0x3800-0x3BFF in USE_DOORS when their trigger is D). Better: derive LIFTS from `BOOM_SPECIALS[sp].kind == "lift"` so the two tables can't drift again.
- ride() seems to cope with the 1 s turbo wait as is: the patched run got out of the pit, and the lift is the only way out (the ride itself wasn't watched).
- Design rule: fine. A player sees a LIFTFLAT platform 56 above the pit floor and presses its face, the stock Doom lift idiom (the person did, 4 s after the key); the explorer already takes "this is a lift" from line specials.
- Likely to recur: any Boom-format map with generalized lifts gets the same trap whenever a walk-over or one-way drop puts the bot below one (this map alone has 24 such lines on 5 lifts). Worth checking playtest's other vanilla-only sets the same way (USE_DOORS lacks generalized doors, e.g. this map's 15342 = 0x3BEE locked D door; [INFERENCE] not shown to matter here).
