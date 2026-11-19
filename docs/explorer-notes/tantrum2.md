# tantrum2 MAP01: stuck behind timed door 152

## 1. What the person did to get past
- 0:14: the person used switch L1335 (SR 63, door open-wait-close, tag 25, SW1GARG) in a 16-wide alcove, sector 331 (floor 32, ceiling 96), at (-528,184..232). That opened door sector 152 (32 wide, x -880..-848, y 0..128; floor 0, ceiling 0 up to 108).
- They ran west at once through 155 → 152 → 151 → 142. 7 s later (0:21) they used L160 at (-1080,-112): S1 special 20 (floor raise to next, change texture), tag 3, SW1GARG on a one-sided line. It sits at the back of an 8-deep niche, sector 144 (floor 20, ceiling 64). That raised nukage sector 141 (floor -128) into a bridge, and from there they reached tags 17/18 (0:51-0:55) and the blue key (1:21).
- Door 152 is the only way west:
  - Its east face L86 (BIGDOOR6) has **no special**.
  - Its west face L88 is DR (sp1, front = sector 151): it can only be used from the far side.
  - The other neighbours of sector 142 are nukage pits (137/141/143) and shut sector 150.

## 2. What each seed did instead
All three seeds behave the same way. Seed 1 debug trace (I reran it in a worktree with per-tic prints) and seed 2 report:
- 0:08: "doorway" try of L86 (the shut BIGDOOR6, no use action): nothing.
- 0:14: tag 15. 0:23/0:24: tag 25 switch L1335. It stayed at the switch until 0:26.
- 0:28: it opened DR door 159 (L78) on the east side instead of going west.
- 0:30-0:51: it kept making for frontier cells inside door 152 at (-856,56)/(-856,104). Each time: "walk stuck at -832,56" against L86.
- 0:35-0:40: it chose "door" L88 from its **back** side. It used it from (-832,64) and nothing happened, but the report still logs a false "door sector 152".
- 0:51-1:11: it walked "unvisited" cells to the east.
- 1:16 and 1:35: "again" presses of tags 15 and 25. After the 1:35 press it ran for 152 and reached L86 at 1:39.4, but the door had shut at 1:38.9.
- 1:43-1:58: two more aborts at L86. From 1:58 it searched walls (82 searched, 3 edges crossed) and gave up at 8:18 (seed 1) and 8:08 (seed 2). Seed 3 hit the 15:00 cap. Seeds 1/3 spent 44% and 72% of the time in sector 155 at the face of door 152.

## 3. Cause (high confidence; per-tic heights verified)
**The explorer's switch-use routine stands at the switch longer than the timed door stays open.**
- Door 152 (SR 63, normal speed) is passable (ceiling ≥ 56) for about 5.7 s. Per-tic trace: fully open (108) by 21.0 s, starts closing at 25.6 s, below 56 at about 26.2 s.
- The run itself is short: from the switch to L86 took 1.5 s (1:37.9 → 1:39.4 in the trace).
- How act() spends the window, all at (-496,208):
  1. **drive() to spot(L1335, 0, 24)** aims at (-504,208), which is on top of the 32-high alcove ledge (sector 331). It can't climb there, so it sits stuck. drive()'s stuck-press (every 23 tics, up to 3 times, then a 70-tic abort, caught by `except pt.Abort: pass`) is what actually used the switch, about 1.5 s before the logged "switch" event. Then it stays stuck for roughly another 3 s.
  2. quiet() waits until door 152 stops moving (it is within NEARBY=512).
  3. The real press does nothing, because the door is already open.
  4. The 70-tic post-press loop and look_round (24 tics) follow.
  5. It leaves at 26.2 s (and 1:37.9 the second time) with the door closing: ceiling 62 and 64.
- Frames (seed 2 video, 0:20 and 0:25): staring into the switch alcove the whole time. At 0:37.5: face-on to the shut BIGDOOR6 (L86).
- **Secondary bug, verified in the trace.** door_lines takes every D line as openable from either side. Once L88 has been seen, doors() contains 152 (from 0:30), so:
  - the planner routes through 152 from the east;
  - it gets stuck at L86 again and again;
  - it uses L88 from behind and logs a false "door" event.
  This wasted a 3-try budget per frontier cell but isn't what blocks it. Even without the bug, the east side has no way to open 152.
- Inferred, not tested: on the first press it also doesn't know what lies beyond 152 (it never saw L88 from the switch), so it chose door 159 by cost. On the 1:35 "again" press it did pick the 152 frontier, and would have got through if it had left about 2 s earlier.

## 4. Classification
- **B-blind: the known blind spot "timed doors it's too slow for".** It is made worse by the bot's own slowness at the switch (a ledge-blocked drive plus quiet() plus the post-press wait), which is really a B-weak flaw in the switch routine.
- All three seeds were stuck from 0:23-0:24. The person's first L press was at 3:59, so the seeds failed on a known blind spot well before it. **The Bot-limited rule applies.**

## 5. Fix sketch
- **Don't drive onto the switch's ledge.** If the switch is already within USE_RANGE (it is 32 units away here), press from where it stands rather than spending about 4 s on drive() stuck-presses. Any switch in a raised alcove pays this cost.
- **After a press that sets something moving, don't idle.** Skip quiet() when what's moving was started by its own press. Cut the 70-tic loop and look_round short when it has no lift to catch. Treat a far sector that opened (ceiling went up from shut) as a "just opened, go now" target: re-plan at once with live heights, so the frontier through the open door wins.
- **Player knowledge:** this fits the design rule. A player hears a door open, has already found the shut BIGDOOR6 at L86 that wouldn't open (the bot tried it at 0:08), and runs back to it. The bot may remember the "doorway" it tried and failed, and make it the target when a switch press sets a door-like sector moving within earshot. It must not use the tag link, which a player can't see.
- **Fix door_lines** to count a D line only from its front (side 0): Doom ignores use from the back for doors. Then L88 doesn't make 152 openable from the east and doesn't log a fake "door" event.
- **Recurs:** remote SR/S1 open-wait-close doors (63/29-style "timed" doors) and switches in raised or narrow alcoves are common in community maps. The few seconds lost at every switch will cut through any timed door or lift.
