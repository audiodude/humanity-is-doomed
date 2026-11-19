# selfish5 MAP25: why the seeds never got to switch tag 9 or the red key

## 1. What the person did to get past
- 4:40: blue door (sector 350). At 5:03 they walked into the lift booth: sectors 251 (outer ring) and 254 (inner), both tag 8, floor 144, reached from 249 (floor 128). They faced south and used **L2019** (SR 123 lift, tag 8; front side is sector 251, upper texture SW1GARG, a gargoyle switch on the booth's back wall). The booth dropped 144 -> 0 (z 144 at 5:03.0, 0 at 5:04.0). They walked south through the 352 ring (floor 8) into courtyard **351** (floor 0, sky).
- From 351: 353 -> 354 -> 355 (nukage) -> 386 ... a cave that slopes down 384 -> 377 (floor -120) -> 396/398 -> lift 376 (tag 10) up to 128 -> 373 -> 366 -> 368. They pressed **switch tag 9** (L2876, SW1GARG) at 5:47 (1862,-688), took the red key at 5:50 and opened the red door at 6:12. On the first try at 5:13 they fell into the nukage pit 387 and pad 391 sent them back to 351. That cost time but isn't the way on.
- The only way into 351 is this lift. The other neighbours of 351 are closed or are decoration (365 is shut at 128/128). The ring 352 has a 128 ceiling under the booth's 144 floor, so nobody can drop off the raised booth.

## 2. What each seed did instead
- Blue door at 3:54 / 3:22 / 3:14 (seeds 1/2/3). Then each went through 348/349 -> 228 -> 249 and first stood on the booth at 4:16 / 3:42 / 3:33.
- Traces of the compare recordings: the seeds were on 251/254 on 12 / 13 / 12 separate visits, and **z was 144 every time**. None of them ever went down, so none reached 351, the cave, tag 9 or the red key.
- "SR lift by sector 351 -> 251/254" (seed 1 at 4:52) is **L2821**, the call switch on 351's side (lower SW1GSTON). The bot used it from on top of the booth at (-160,-2537). The lift didn't move (z stayed 144), but the switch went into `done`.
- The rest of the time (to 15:00) was a loop: the booth, then lift 431 (tag 42, shut at 256/256 between 256 and secret sector 425). It pressed L2057, L3397, L3419 and L3420, ran for 431 and rode it up to nowhere, then went back to the booth. Each fresh 431 switch counts as progress, which clears `static`, so the booth ride was retried again and again. It stopped at --max-time with 74-76% of the map seen.

## 3. Cause (confident: checked with debug prints in a worktree at 26675f0, seed 3)
The explorer can't ride a lift down by its in-booth switch when it walks onto the lift from beside it.
- Debug line from the debug run: `ride s=251 cells=[249,251,251,254,251,352] aftersec=351 want=0 z=128 lift=144 pos=(-136,-2470) possec=249 on=(-152,-2536) seenliftsw=[2019]` -> 7.6 s later `ride abort didn't take z=144`. This repeated at 254.6, 269.7, 293.5, 317.2 and 347.5 s.
- `_ride` going down (explore.py ~899-929) looks for a switch with front sector == s (L2019, found) but uses it only `if sector_at(pos) == s`. The bot is still on 249 beside the booth, so it takes the "from beside it" branch: it faces the lift, uses its plain edge L2014 (no special, nothing happens), walks onto the middle (-152,-2536, which is sector 254, not 251) and waits 245 tics for z to reach 0. That is the 7 s it stands still each visit. Even standing on the inner part (254), it would find no switch, because L2019's front sector is 251.
- `options()` (line 635) never offers L2019 as a switch target: it's a lift switch with an open back sector (352: 8/128) on a tagged sector, so it's left to `ride()`.
- Second bug: L2821 was "pressed" because the check is only `seg_dist <= USE_RANGE` (about 40 units). In game, the line used from (-152,-2542) towards L2821 crosses L2022 (251/352: opening 128-144 = -16), which blocks it, so the use does nothing.
- Frame evidence: person.mp4 at 5:03 (/tmp/selfish5/person-lift-booth-5m03.png). A lit metal booth with the gargoyle switch on its back wall, in plain view from 249.
- Checked: map data, person and seed traces (positions every 7 tics, replayed from the compare recordings), and the debug run. Inferred, not traced: that seeds 1 and 2 hit the same `_ride` branch. Their recordings show the same 7 s stands at the booth, z always 144.

## 4. Classification
**B-weak** (lift navigation), not a known blind spot. The lift is neither timed nor perpetual; the explorer just never uses the switch it has seen inside the booth. All three seeds were stuck from their first booth visit (3:33-4:16). The person's first L press was at 1:58, before that, and the cause isn't a known blind spot, so **the Bot-limited rule doesn't apply**. The person's L stretches (1:29-3:10, 6:12-7:00) are elsewhere; the seeds did fine through the first one.

## 5. Fix sketch
- In `_ride`, going down: treat the lift as all its tagged sectors (251 and 254 here). Look for a seen S1/SR lift switch on any of them whose switch texture faces into the lift. If the bot isn't on the lift yet, walk on first, go within reach of that switch, use it and ride down. Don't use the lift's plain edge from beside it.
- Make the use-reach check do what Doom does: no non-special line with openrange <= 0 between the player and the switch, so that a switch below a ledge (L2821 from the booth) isn't marked done after a use that hit a wall.
- Smaller: a switch that only moves a lift it then rides to nowhere (431) shouldn't count as progress that clears `static`, or the loop goes on for 10 minutes.
- Design rule: fine. The switch is a plainly visible SW1GARG on the booth's back wall, and the courtyard below can be seen.
- Likely to recur: "elevator booth with a switch inside" is a common classic layout. Lifts built from two sectors with one tag (an inner panel and an outer ring for lighting or texture) are common too. Any lift reached from a floor level with it whose down switch is on its own wall will fail this way.
