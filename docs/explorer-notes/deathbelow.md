# deathbelow (db.wad MAP01): why the seeds never reached switch tag 15 / the blue key

## 1. What the person did to get past
- 3:29: stepped on the teleporter pad in sector 178 (lines 1134-1137, WR teleport tag 14; sector 178 was lowered by
  the tag 13 switch at 0:55) and landed on crate top sector 177 (floor 80, x 3456-3584, y -1024..-960), at the
  teleport destination thing (3484,-992), facing east.
- 3:31 (two seconds later): pressed line 1167 (S1 door blaze open, tag 15, SW1COMM upper texture, x=3800,
  y -960..-1024, facing west into the 8-unit recess sector 170, floor 80). Door sector 187 (80/80) opened.
- To get there they ran east off crate 177 across an 80-unit gap (sector 151's floor, 16) onto crate 169
  (floor 80, x 3664-3792), then 128 units to the switch, over a trail of three health bonuses on 169 (things
  at 3680/3728/3776,-992; health 100% -> 103%). Frames (person.mp4, 210.5 s / 211.0 s): on 177's edge looking
  straight at the SW1COMM switch past the gap, then already on 169 at the switch. 3:32: BlueSkull at
  (4032,-992) in sector 183 behind the door. Everything after (blue door 74, yellow, red, exit 7:00) follows.

## 2. What each seed did instead
All three seeds: tag 1 at 0:02, door 137 at 0:40-0:50, tag 13 at 1:04-1:08, then the same pad within 10 s
(teleport 1:17 / 1:17 / 1:14), landing on crate 177 like the person. None ever pressed line 1167.
- seed 1: teleported again 2:16 and 8:05; "nothing left it knows to try" at 2:26 (wall search at 2984,-1400);
  13:56 with no progress, 77% of it in sector 151 (the big room the crates stand in).
- seed 2: search from 2:03 (3008,-1879) and again 5:09; went back west to door 13 at 2:28; 13:51 with no
  progress, sector 151 54% + sector 212 20%.
- seed 3: teleported again 2:19, 6:15, 12:42; search from 2:28; 13:53 with no progress, sector 151 80%.
All three stopped at --max-time 15:00, having seen 48-49% of the map. Seed 1 frames (seed1.mp4, compare.py's
recording): lands 78.4 s, turns round looking, has the switch face (and a health bonus below it) at the right of
the screen at 79.0 s, and by 79.5-80 s is down on sector 151's floor among the crates. Each repeat teleport
put it back on 177, from which it only ever dropped into sector 151.

## 3. Cause
Crate 169 (and the switch recess 170 / door 187 beyond it) is reachable only by running across the 80-unit
gap from crate 177. Verified from the WAD:
- 169 borders only 151 (floor 16; lines 1094 CRATE3, 1095 CRATWIDE: 64-unit faces), the void (1096) and 170.
  151 -> 169 is a 64 step. The nearby crate 188 (floor 48, x 3752-3784, y -1064..-1032) is a 32 step from 151
  and from 169 and doesn't touch 169: no stair. 170 and 187 have only one-sided walls to the south/north.
- The gap: 177's east edge x=3584, 169's west edge x=3664, same height 80, floor 16 between. The player's box
  (radius 16) stays held up until its centre has moved 48 units past the gap's start, and Doom lets it step
  up 24 on landing; at run speed (~16.7 u/tic, no air friction) it drops ~6 units over those 48: an easy straight
  run, the way the teleport destination already faces (angle 0, east).
- The switch can't be used from below: from sector 151 the player's centre gets no closer than ~61 units to
  line 1167's end (3800,-1024) (crate 169 to the north, crate 188 and wall 1097 at x=3792 to the east), and
  explore.near() only allows use-from-below cells within USE_RANGE-8 = 56. So the switch was a seen line with
  no reachable cell, and never an option.
- The planner has no gap-crossing move: a drop off 177 is a one-way edge to 16, and 169 at 80 is cut off.
  playtest.py/explore.py have no jump/run-across logic (grep: none).
Sure: high. Verified: geometry, specials, heights, textures, things from the WAD; the person's crossing and
seed 1 seeing the switch then dropping, from frames; near()'s 56-unit rule from the code. Inferred (no debug
prints): that seeds 2 and 3 did the same as seed 1 (same landing, same reports), and that line 1167 sat in
seen_lines with no reachable cell rather than being dropped some other way.

## 4. Classification
B-blind: running jumps (the known blind spot "running jumps"; here a straight run across a gap between two
equal-height crates, no actual jump). All three seeds were on crate 177 with the way on in front of them at
1:14-1:17 (seed 1 dropped off within ~2 s); first wall searches 2:03-2:28. The person's first L press is 2:28
(report.txt; in sector 151 at 3014,-1522 - the person's trouble was finding/using the pad: 2:35 between tag 13
and the teleport, which the bot found in 10 s; once on 177 they crossed the gap at once). The seeds failed on
the known blind spot by 1:17, before the first L press: the Bot-limited rule applies. (The brief says first L
5:08; report.txt has L at 2:28 and 5:08. Either way the seeds were stuck first.)

## 5. Fix sketch
Add a "run across" edge to the planner: from a cell on a ledge, straight across a gap to a seen floor no higher
than the take-off floor (plus STEP) whose near edge is within reach of a run (here 80 units; vanilla carries a
running player ~100+ units with a 24-unit drop allowance, more if the landing is lower). Execute it as a
full-speed straight line along the edge normal, starting from a run-up of a few cells on the take-off ledge,
and check the landing like a lift ride (failed: fall back to the drop). Players know this: the far crate and
its switch are in plain sight from where they land, at the same height, and running across gaps is basic Doom.
Recurs: crate rooms, broken bridges and "ledge across a pit" layouts are common in community maps, and a
teleport or lift that drops you on a high crate facing the next one is a common way to make them; here the gap
also hides a whole half of the map (48% seen).
