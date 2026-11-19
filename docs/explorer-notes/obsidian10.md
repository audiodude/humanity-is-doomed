# obsidian10 (20261118-084642-OBSIDIAN10-MAP01, compare-cfa4b69)

## 1. What the person did to get past
- Position trace of play.lmp (replayed in ViZDoom, sector + lift 546 floor per tic; /tmp/obs10/person_trace.txt):
  - 2:47.21 in 451 (floor 96) → 2:48.24 on lift 546 at (1047,-570), lift floor 72 and falling (crossed the WR generalized-lift lines L2108/L4628/L4629, special 13369, tag 21 = the "switch tag 21" milestone) → 2:48.28 in 459 at floor 32 with the lift at 32. Rode the lift down into the basin.
  - 2:59 walk 549/550 at (278,1448); 3:03 yellow key in sector 579 (-876,1330), inside the basin.
  - 3:07-3:11 back through 476/459 to the lift; 3:11.23 on 546 at (1039,-517) with it at 32 (used its face L4630 from 459), 3:12.30 in 451 at z 96 (rode it up). Then 933→826→444→422 (3:15-3:17), a loop west, back to 451 at 3:49, then 933→924→925→585→634→712.
- L press at 4:00 in sector 924 (1838,-394): already out of the basin, looking for the door. 4:06 yellow door sector 713 at (1979,1517): L2732/L2736 (special 34, yellow D door, SPCDOOR2) between 712 (floor 104, SLIME14) and 714. Exit 4:33.

## 2. What each seed did instead
All took the person's route to 451 (via 826→933→455→453→452) but walked off its 64-unit ledge (451 floor 96 → 459 floor 32, the y=-504 edge L4676 etc.) just east of the lift instead of crossing the lift's WR lines, so the lift never moved and they were in the basin with no way back. Position traces of compare's recordings (/tmp/obs10/seed{1,3}_trace.txt; seed 2 inferred from its events):
- Seed 1: 2:37 in 451, 2:39.21 off the ledge at (1144,-493), z 96→32 by 2:39.33, lift still at 88. Key 3:02, last progress 3:15 (tag 20, 522→520 at 480,2032, inside the basin). 3:29 wall search. 9:12 "found: using a wall by sector 459 moved sector 546" at (1062,-488) = L4630, the lift's own face; it walked off without stepping on. 11:44 stretch in 476 31% / 459 29% / 552 / 469 until 15:00.
- Seed 2: door 506 (basin side, 1057,395) 3:21, so in the basin by then [inferred]; key 3:34, last progress 3:51 (tag 20). 6:12 search; never tried L4630. 11:09 stretch, 459 68%.
- Seed 3: 4:03 in 451, 4:04.34 off the ledge at (1144,-494), z 32 by 4:05.23, lift at 88. Key 4:34, last progress 4:46 (tag 20). 5:00 search. 13:50.00 at (1061,-490), 22 units from L4630, lift down at 32 (its own use); by 13:50.31 it had turned away to 469 and the lift was back at 88. 10:13 stretch, 459 53% / 476 14%.
No seed ever had the lift as a target; all stopped at the 15:00 time limit.

## 3. Cause
The key basin (459, 476, key sector 579 and ~130 sectors around them) has exactly one way out: lift 546 (floor 88, ceiling 432, LIFTFLAT) between 459 (floor 32) and 451 (floor 96). Its face toward 459 is L4630 (special 13371 = Boom generalized SR lift, tag 21, lower texture SUPPORT2, no switch texture). A sector-graph flood from 579 with every other tagged floor lowered and 546 blocked never reaches 451, 924 or 712 (verified); with 546 ridden it does.
The explorer can't ride it because `playtest.LIFTS = {10,21,62,88,120,121,122,123}` (vanilla only) builds `Geometry.lifts`; generalized lifts (0x3400-0x37FF, here 13369/13371) aren't in it. On this map `geo.lifts` is empty (verified). So:
- the planner treats 546 as a plain floor at 88: a 56-unit wall from 459, so no route to 451 → no ride()/call;
- explore.py's target filter skips L4630 as a switch ("a switch on the lift's own side calls it, which ride() does": kind=='lift', 546 tagged, ceiling>floor) — the call is left to ride(), which never runs because 546 isn't a lift;
- so its only chance is the wall search, which seeds 1 and 3 reached late (9:12, 13:49; seed 2 never). search() presses, waits 20 tics, logs "found", and only remembers trigger-D lines as doors (`door_lines`); it doesn't step onto a lift it just lowered, so the lift (down at 32 at 13:50.00, back at 88 by 13:50.31 in seed 3) went up without it, and a searched wall is never searched again.
Sure: high. Verified: WAD data, `geo.lifts` empty, BOOM_SPECIALS kinds, the explore.py code paths above, the person's ride down/up and seeds 1/3's drop beside the lift and seed 3 leaving the lowered lift (traces). Inferred: seed 2's drop (events only); the exact reason seed 2's search never reached L4630 (search order/time).

## 4. Classification
B-blind: unread line type (Boom generalized lift specials 13369/13371 not in `playtest.LIFTS`), a known blind spot. (Dropping off the ledge is fine on its own; the person rode down and nothing a player knows forbids the drop — the trap is only that the way back up is a lift the bot can't read.) Each seed was sealed in when it dropped into 459: seed 1 at 2:39, seed 2 by 3:21, seed 3 at 4:05. Person's first L press: 4:00. Seeds 1 and 2 were stuck before it; seed 3 by 5 s after it (it was just slower on the same route; its outcome was the same). Strictly the rule wants all seeds before the L press; I'd still mark the play Bot-limited: the person's L (in 924, looking for the yellow door after the lift) is in a phase none of the seeds could ever reach, so the comparison past the key measures only this blind spot.

## 5. Fix sketch
Build `Geometry.lifts` from `BOOM_SPECIALS` (every line whose spec.kind == "lift", vanilla, Boom extended and generalized) instead of the hard-coded vanilla `LIFTS` set; check the other vanilla-only sets (`USE_DOORS`) the same way. Then the planner sees 546 as a lift, ride() calls it from 459 by using L4630, and the target filter's "ride() does it" assumption holds. A player knows this: LIFTFLAT floor, a ledge 56 up, using the face of a lift is standard Doom. Will recur on any Boom-format map (generalized lifts are common in Boom/MBF21 WADs); a one-way drop beside such a lift makes it a hard trap rather than a detour.
