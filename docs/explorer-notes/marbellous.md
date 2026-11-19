# Marbel MAP25 (marbellous): why the seeds never left courtyard 62

## 1. What the person did to get past
- Courtyard sector 62 (floor 16, sky) has six 64x64 pedestals, sectors 112-117 (floor 144, 128 above the courtyard, tag 2, GSTGARG/GSTSATYR/GSTLION faces). Two of them are teleport pads: 112 (GATE2, WR teleport lines 560-563, tag 3 -> walkway 63 at -640,1088) and 115 (GATE1, lines 572-575, tag 10 -> sector 125 at -1408,544).
- The only line that moves tag 2 is line 576: SR lift (special 62), SW1GSTON on the north face of pedestal 116 (front sector 62, back 116), at (-1024,1152). It lowers all six pedestals to 16 for about 3 s (4 units/tic down, 105-tic wait).
- The person pressed it before 0:57 (inferred: no other line moves tag 2) and took pad 112 at 0:57 and pad 115 at 1:11, then went back and forth many times. At 2:24 pad 115 -> sector 125; at 2:29 they pressed line 675 (SR door, tag 9, SW1GSTON, sector 123 at -1582,624), which opened door 336 (milestone "switch tag 9", -1561,606). L press at 2:19 at (-1034,584) in 62, just before.
- Sector 125/123 can't be reached on foot from 62 or 63 (rough static BFS, inferred), so pad 115 is the way on.

## 2. What each seed did instead
- All three seeds: doors 48 and 240, then the SR lift 307 by sector 63 at 0:40 (last progress). Up on walkway 63 (z 144) to about 1:03, where they saw the pads, then down into 62 for the rest of the run.
- Traced seed 2 (worktree at cfa4b69, debug prints): from 1:07 to at least 5:48 (where I stopped it) every pick is a `teleport` target on lines 560-563/572-575. Each one aborts after about 5 s with "walk stuck ... heading for" a point inside the pad (e.g. at (-927,720) heading for (-928,664), the pad 115 edge). That's 3 tries per line, 8 lines, given up and retried 1, 2, 4 minutes later. At 5:48 it also had pedestals 114/117 in static/dead (it tried to ride them as lifts, and they didn't come). Line 576 was never picked (0 occurrences).
- Seed 1 frames: 1:15, 3:00, 10:40 and 11:40 all show the bot facing a green pedestal side at close range.
- Wall search began at 8:55/8:56/8:35. It found line 576 at 10:28/14:11/10:12 ("found ... moved sector 112/113/114"). Seed 1 frames from 10:27 to 10:31: the bot shoots a wall, faces the skull-plate SW1GSTON switch, uses it, the pedestals sink flush, it crosses a pad and teleports. In each seed that teleport, 2 s after the find, used pad 112 (tag 3 -> 63, ground it already knew). It never reached pad 115.
- Afterwards seed 1 was back at the pedestals by 10:40 (frame), searched again from 13:22 and ran to 15:00. No seed pressed 576 a second time.

## 3. Cause
Two explorer faults together. Fairly sure about both: the trace and code are verified, the person's switch press is inferred.
1. **Raised teleport pads are targets.** In `options()` (explore.py ~648) a teleport line only needs `h[bs]` headroom >= 56. The pad's floor height against the floor it is approached from is never checked: the spot is 40 units out, on the 62 side at floor 16, and the pad is at 144. `through()` drives into a 128-unit wall. That cost about 8 minutes of the 14 (verified by trace).
2. **A lift switch on its own lift's edge is never a switch target.** In `options()` ~635 an S1/SR lift line whose back sector is a tagged lift with floor < ceiling is skipped, on the reasoning that `ride()` presses it when a route crosses that lift. Pedestal 116 is on no route, so 576, an obvious SW1 switch, waited for a wall search (verified in code, and the trace never picked it). After a search "found", nothing marks 576 as reusable: `door_lines` is only for D doors, `again` only for lines in `done`, and each wall is searched once. Search also doesn't call `catch_lift`. So the bot got one 3-second window, used it on the nearer pad 112, and could never press the switch again to try pad 115.

## 4. Classification
**B-weak** (target logic and navigation: a lift switch it won't press, and pads it walks into). Not a known blind spot. It isn't "timed lifts it's too slow for": in the one window it got, it caught a pad within 2 s. All three seeds were stuck from 0:40/0:41, before the person's first L at 2:19, but because the cause isn't a known blind spot the Bot-limited rule does **not** apply. The verdict stands.

## 5. Fix sketch
- Teleport option: skip a pad whose floor is more than 24 above the approach floor (`lv` at the spot). If the pad is a lift, it can be lowered: tie it to a switch that lowers its tag (`lift_switch`, or an unpressed lift switch it has seen with the same tag).
- Make an unpressed S1/SR lift switch a normal switch target when no planned route rides that lift (or always once; ride() can still use it). After pressing it, `catch_lift` should run for a lowered **teleport pad it hasn't been through** before a plain pedestal, and `lift_switch` should record the line, so it can press it again and run for the next pad (115) on a later go. A "found" that moved lifts should register the same way (`lift_switch`), not be a one-shot.
- Design rule: fine. The switch texture is plain to see from the courtyard, the pad tops (GATE1/GATE2) are visible from walkway 63, and pressing the switch visibly sinks all six pedestals.
- Likely to recur: teleport pads on raised pedestals lowered by a switch are a common Doom idiom, and fault 1 hits any teleporter on a ledge more than 24 high. Fault 2 hits any lift switch mounted on a lift that isn't on the way somewhere: pillars, lowering platforms, pads.
