# Nukage Lockdown (`nukage_lockdown`)

## Concept

**You start locked out of the exit, looking at its switch and EXIT sign through a window; the only way to it is a loop all the way round the plant's nukage spill and back through the spill itself, to come at the exit from its far side.**

- **Shape:** one loop that leaves the start and comes back to it from the other side of the glass. The lobby is on the hot side of the plant's decontamination line; the exit vault, 16 units away through bars, is on the clean side. The loop runs west, north, east and south round an open-air spill basin, never through a hub, and closes by wading back across the basin, through the culvert the nukage drains by, into the clean side.
- **Theme:** lockdown after a spill. The plant's primary storage tank has burst, and its nukage pours out of the rupture in green falls and down a channel into the basin in the middle of the plant. The plant has sealed itself: every lockdown shutter (SPCDOOR3, one material for all of them) opens only from its far side. Red lamps blink in the lobby. Nukage is everywhere you go: the basin you see from almost every room, the flooded pump pit, the tank and its falls, the filter tubs, the basin wade, the culvert, and the decon pool on the clean side.
- **The reveal:** from the start you see the exit switch and its EXIT sign through a window into the vault, and from the lobby's north window the whole basin: the culvert mouth under a radiation sign, the megasphere on its island, and the falls at the far side. Every wing has windows back onto the basin, so the lobby's lit window and the culvert are in view all the way round.
- **Gating:** the lockdown shutters (opened from the far side: they are the map's shortcuts), one key (blue, on the burst tank's rim), and the basin itself, which can be entered only from the east bank's shore steps. Every other edge of the basin is a wall, a window with a sill too high to climb, or a grate.
- **Difficulty:** hard, a step up from MAP07 by toughness, not head count. The per-space counts below sum to 34/55/78 monsters on easy/HMP/UV, about 12,000 monster HP on UV before resurrections. The heavy share is about 18% (an arch-vile, 5 revenants, 2 mancubi, 2 arachnotrons, 3 hell knights, a baron), plus 4 cacodemons over the basin. **Debut: the arch-vile**, in the decon hall at the end of the loop, raising the fodder you kill around it.
- **Slot:** MAP08 of `NUKAGE.WAD`. UMAPINFO: `levelname "Nukage Lockdown"`, `music "D_DDTBLU"` (the slot's own track). MAP08 has no boss rule in DOOM II, so the mancubi and arachnotrons are free to stand anywhere.

How it differs from the set:

| Map | Shape in a phrase |
|---|---|
| MAP01 Nukage Junction | the template: courtyard hub, one wing per key |
| MAP02 Nukage Crossing | two banks of a canal, joined by a sluice gate that sinks into a bridge |
| MAP03 Nukage Core | a spiral climb around a reactor to the crown |
| MAP04 Nukage Divided | a fork into two wings that never meet, keys crossed |
| MAP05 Nukage Drain | a ring of walkways raised one by one out of a flooded reservoir |
| MAP06 Nukage Undercurrent | one hall crossed twice: over it, then under it |
| MAP07 Nukage Storage | one hall in two states: a maze on the way in, an arena once you sink it |
| **MAP08 Nukage Lockdown** | **a loop away from the exit you can see, closed by wading back through the spill** |

The nearest relative is MAP05, which also has nukage in the middle. There, you walk on the pool, along walkways you raise out of it, to a vault in its centre. Here, the basin is never walked round: the loop runs through buildings on its banks, sees it only through windows, and crosses it once, at the end. The goal isn't in the middle; it's next to the start.

## Route

Heights are floor/ceiling. Monster counts are UV (HMP, easy), and "deaf" means the ambush flag. Coordinates are in the rectangle table under the sketch.

1. **Lobby (LB)**, the start. 384×368, 0/160. Red lamps (TLITE6_5) in the ceiling; the room blinks. The player starts at (1120,544) facing east.
   - **Visible:** through the bars in the east wall (sill 32, MIDGRATE, impassable), the exit vault and its switch, lit; beside the bars, the lobby's lockdown shutter (BL), shut. Through the north window (sill 48), the basin: the culvert mouth to the right under a GRAYPOIS sign, the island and its megasphere in the middle, the tank's falls far off to the north.
   - **Gate:** the west door to the ready room is the only way out.
   - **Encounter:** none. Nothing in the basin can see the window at the start (see Build risks).
   - **Pickups:** shotgun (about 100 from the start), 4 shells, stimpack. Secret 1 in the south wall.
2. **Ready room (RR)**, 640×576, 0/128, staff lockers. **Encounter:** 4 zombiemen (3, 2), 2 imps (2, 1), 2 shotgun guys (1, 1), at close range among the locker bays. **Pickups:** green armor, box of shells, stimpack.
3. **Gallery, south half (PS, PGS).** Three 24 steps up from the ready room's north side to the gallery, 256 wide, 72/192, running north along the basin's west bank.
   - **Visible (the basin reveal):** five windows (sill 112, 40 above the floor, so they can't be climbed) look east over the whole basin: the lobby's lit window from outside, the culvert, the island, and the falls at the far end.
   - **Gate:** at its north end the gallery is cut by a lockdown shutter (BD1), shut, with its red lamp. A lift (L1) in the west wall goes down.
   - **Encounter:** 3 imps (2, 1) and 2 zombiemen (1, 1) along the gallery; a chaingunner (1, 0) at the shutter; 2 cacodemons (1, 1), deaf, in the basin's north-west, which see you through the windows and come across the basin at them. The windows' openings are 64 tall, so the cacodemons can come in.
   - **Pickups:** chaingun, box of bullets.
4. **Pump pit (L1, PP)**, through the lift. 384×672 plus the stair, -72/176, dark and flickering. Three pump plinths (PIPES, 96 high) stand in rows, and two nukage channels (-88, 64 wide, `DAMAGE_5`) cross the pit between them. The pit floor is dry grating; the channels are the obstacle.
   - **Encounter:** 2 demons (2, 1) and 2 spectres (1, 1) in the dark between the pumps; a hell knight (1, 0; easy: an imp) at the stair foot; 2 imps (2, 1) on the stair.
   - **Pickups:** **super shotgun** on a lit plinth at the pit's north end. Taking it opens a closet in the west wall behind you: 2 imps (1, 1). Medikit, box of shells.
   - **Secret 2** is a ledge in the pit's north-west corner.
5. **Pit stair and gallery, north half (ST2, LN2, PGN).** Six 24 steps rise north out of the pit to a landing at 72 and the gallery's north half, behind the shutter. **The switch beside the shutter's north face opens it**: the first lockdown shutter opened from its far side, and the loop's first shortcut back to the gallery's south half. **Encounter:** 2 shotgun guys (1, 1). **Pickups:** medikit, bullets.
6. **Tank hall (TV, BT)**, down three steps from the gallery's north end. 1536×560, 0/384, the hall the burst tank stands in.
   - **Visible:** the tank, an octagon 448 across with SLADWALL sides and SLADPOIS warnings at the foot of its stair, under a sky opening. Its south face is ruptured, and green falls (SFALL) pour out of the gap into a channel that runs south under the hall's wall, through a grate, into the basin. The blue key glows on the rim beside the rupture. The blue door is at the hall's east end.
   - **Encounter:** a mancubus (1, 1) at the hall's east end, by the blue door (spatial pressure; the meat shield between you and the door); 6 imps (4, 2) round the hall; **a revenant** (1, 0; easy: an imp) on the tank rim (the turret, priority threat).
   - **Pickups:** **rocket launcher** on a pedestal in the north-west corner, 2 rockets, medikit.
   - **Optional:** the north annex (NA), off the hall's north wall.
7. **The tank rim, the first set piece (TS, RW, KP).** Eight 24 steps climb the tank's west side to the rim at 192, a walkway 64 wide round the top of the tank. Inside, the tank's nukage is at 176, 16 below the rim, and you can step out of it. You walk the rim round to the rupture, with the hall 192 below and the falls under your feet. **Taking the blue key opens two closets in the hall's north-west wall** behind you: an arachnotron (1, 0) and 3 imps (2, 1). From the rim the arachnotron's plasma comes up at you across open air, and the way down is the stair at its end of the hall. **Visible from the rim:** the whole basin to the south over the hall's south wall top, with the lobby window across it; and a lit alcove high in the hall's north wall (secret 3).
8. **Blue door and connector (BD, FC)**, at the hall's east end. 304×128, 0/128, ending in a 16 step up to the filter house's 32 floor. The south door FD has the same 16 step on its east-bank side, so the bank can be climbed back into.
9. **Filter house (FH)**, 576×1088, 32/256. Three steel filter tubs (SILVER1, rims at 96) stand in a row down the middle, each full of nukage at 80, between 128-wide aisles. An optional loft (128) runs along the east wall, up four steps.
   - **Encounter:** a baron (1, 1; easy: a hell knight) at the far (south) end of the west aisle; a hell knight (1, 0) in the east aisle; 2 chaingunners (1, 1) behind the tubs, short sightlines only; 4 imps (3, 1); a revenant (1, 0) on the loft.
   - **Pickups:** medikit, box of shells. Loft: 2 boxes of rockets, berserk pack.
   - **Gate:** the south door (FD) onto the east bank.
10. **East bank (EB)**, 640×704, 0/sky. The basin's only shore: a step at -8 along its west edge leads down into the nukage. The airlock's lockdown shutter (AD) is in the south wall, shut, with its red lamp; it opens from inside.
    - **Visible:** the whole basin from water level, with the culvert mouth 400 to the south-west under its radiation sign, and the lobby window beyond it.
    - **Encounter:** an arachnotron (1, 0) and a mancubus (1, 0) on the bank's east side (easy: 2 imps); 3 imps (2, 1); 2 cacodemons (1, 1), deaf, over the basin's middle.
    - **Pickups:** **radiation suit** on a lit pedestal at the shore step; box of rockets, medikit.
    - **Optional:** the sampling shed (SS), and secret 4 behind it.
11. **The wade (WS), the second set piece.** Down the shore step into the basin (-32, NUKAGE1, `DAMAGE_10`, the hottest nukage in the set) and west along the basin's south wall for about 400, under the cacodemons, to the culvert mouth. The island (IS, 0, with a -8 step ring) stands 450 further into the basin, with the megasphere you've seen since the start; the suit makes the detour affordable.
12. **Culvert (CU)**, 128×192, -32/96, dark, NUKEDGE1 walls, nukage floor. **Encounter:** 2 spectres (1, 1) in the dark, deaf. **Pickups:** none. A -8 step at its south end climbs out into the decon hall.
13. **Decon hall (DH), the arch-vile.** 608×640, 0/256, bright and strobing, the clean side's white-grey panels. A decon pool (-16, nukage, `DAMAGE_5`) fills the middle, with four SUPPORT2 pillars round it; a dais (32) at the south end.
    - **Encounter** (all deaf):
      - **The arch-vile** (1, 1; easy: a hell knight) on the dais, facing north: the priority threat, debuting. It raises every corpse it can reach.
      - Fodder for it to raise: 4 imps (3, 2), 3 zombiemen (2, 1), 2 shotgun guys (1, 1), spread round the pool.
      - A hell knight (1, 1) and a revenant (1, 0) between the pool and the dais: the meat shield between you and the vile.
      - You come out of the culvert at the hall's north-west corner. The pillars are the only cover from the vile's sight, and the pool is between you and it.
    - **Pickups:** box of rockets and a box of shells in the culvert mouth corner (so you have ammo before the fight starts), medikit by each of two pillars, a cell pack.
14. **Exit vault (VD, EV)**, through the door in the decon hall's west wall. 320×368, 0/160, SHAWN2. **Crossing into the vault opens the lobby's closets** (a W1 line across VD): **you look back through the bars at the lobby you started in**, and 2 revenants (1, 0) and 2 imps (1, 1) come out of its south wall and shoot at you through them. The exit switch is on the vault's north wall. The lockdown switch on the west wall, beside the bars, raises the lobby shutter (BL) and closes the loop through the start, if you want to finish them.

Optional spaces:

15. **North annex (NA)**, 448×192, 0/128, off the tank hall's north wall: the tank's monitoring room. **Encounter:** 2 shotgun guys (1, 0), a chaingunner (1, 0). **Pickups:** stimpack, box of bullets. Secret 3 is behind a panel.
16. **Airlock (CA)**, 304×384, 0/128, east of the decon hall. Its switch opens AD, the lockdown shutter onto the east bank: a shortcut back to the shed and the island. **Encounter:** 2 imps (1, 1). **Pickups:** medikit.
17. **Sampling shed (SS)**, 192×256, 0/128, on the east bank. **Pickups:** stimpack, 4 shells. Secret 4 is behind it.
18. **The basin's body and the island (SB, IR, IS)**, everything off the wade strip. **Pickups:** the **megasphere** on the island; armor bonuses along the island's step ring.

## Sketch

64 units per character, each row label is that row's top edge (y). x ticks every 512 from 0.

```
 2880                           NNNNNNN
 2816                           NNNNNNN
 2752           aaaa            NNNNNNN
 2688           aaaa              DD
 2624          hhhhhhhhhhhhhhhhhh33hhhh
 2560          hRhhhhh//TTTTTTThhhhhhhh     FFFFFFFFF
 2496          hhhhhhh//%%%%%%Thhhhhhhh     FFFFFFFFF
 2432          hhhhhhh//%%%%%%Thhhhhhhh     FFuuuFFFF
 2368          hhhhhhh//%%%%%%Thhhhhhhh     FFuuuFFqq
 2304          hhhhhhh//%%%%%%ThhhhhhhhBkkkkFFuuuFFqq
 2240          hhhhhhh//KKff%%ThhhhhhhhBkkkkFFFFFFFqq
 2176          hhhhhhh//KK%%TTThhhhhhhh     FFFFFFFqq
 2112          hhhwwwhhhhh%%hhhhwwwhhhh     FFuuuFFqq
 2048          ^^ www     ##    www         FFuuuFFqq
 1984          ^^         %%                FFuuuFFqq
 1920     nnnngggg ~~~~~~~~~~~~~~~~~~~~~~~~ FFFFFFFqq
 1856  22p^^^ gggg ~~~~~~~~~~~~~~~~~~~~~~~~ FFFFFFFqq
 1792  22p^^^ gggg ~~~~~~~~~~~~~~~~~~~~~~~~ FFuuuFFqq
 1728  22p^^^ ggggw~~~~~~~~~~~~~~~~~~~~~~~~ FFuuuFFqq
 1664  ppp^^^ gggg ~~~~~~~~~~~~~~~~~~~~~~~~ FFuuuFF^^
 1600  ppp^^^ gggg ~~~~~~~~~~~~~~~~~~~~~~~~ FFFFFFF^^
 1536  ppoopp ggggw~~~~~~~~~~~~~~~~~~~~~~~~ FFFFFFF^^
 1472  ppoopp ggg! ~~~~~~~~~~iiiii~~~~~~~~~    DD
 1408  %%%%%% ==== ~~~~~~~~~~iIIIi~~~~~~~~~eeeeeeeeee
 1344  ppoopp gggg ~~~~~~~~~~iIIIi~~~~~~~~~:eeeeeeeee
 1280  ppoopplggggw~~~~~~~~~~iIIIi~~~~~~~~~:eeeeeeeee
 1216  pppppplgggg ~~~~~~~~~~iiiii~~~~~~~~~:eeeeeeHHH
 1152  %%%%%% ggggw~~~~~~~~~~~~~~~~~~~~~~~~:eeeeeeHHH44
 1088  ppoopp gggg ~~~~~~~~~~~~~~~~~~~~~~~~:eeeeeeHHH44
 1024  ppoopp gggg ~~~~~~~~~~~~~~~~~~~~~~~~:eeeeeeHHH
  960  pppppp ggggw~~~~~~~~~~~~~~~~~~~~~~~~:eeeeeeeee
  896         gggg ~~~~~~~~~~~~~~~~~~~~~~~~:eeeeeeeee
  832         gggg ~~~~~~~~~~~~~~~~~~~~~~~~:Seeeeeeee
  768         ssss ~~~~~~~~~~~~~~~~~~~~~~~~eeeeeeeeee
  704         ssss     LwwwwLVVXXVVCC         DD
  640       rrrrrrrrrr LLLLLL|VVVVVCC       AAAA!
  576       rrrrrrrrrrDL@LLLL|VVVVVCC       AAAAA
  512       rrrrrrrrrrDLLLLLL=VVVVD::dddddddAAAAA
  448       rrrrrrrrrr LLLLLL=VVVVDdPddddPddDAAAA
  384       rrrrrrrrrr LLLLLL=VVVVDdddddddddDAAAA
  320       rrrrrrrrrr 11 ccc     ddd%%%%dddAAAAA
  256       rrrrrrrrrr 11 ccc     ddd%%%%ddd
  192       rrrrrrrrrr            ddd%%%%ddd
  128       rrrrrrrrrr            dddddddddd
   64                             ddPddddPdd
    0                             dddddddddd
  -64                             dddZZZZddd
       |       |       |       |       |       |       
       0       512     1024    1536    2048    2560    
```

**Legend.**

| Symbol | Meaning |
|---|---|
| `@` | start (1120,544), facing east |
| `L` | lobby, 0 |
| `c` | lobby closets, 0 (open when you enter the vault) |
| `=` | lockdown shutters: BL (lobby–vault, x 1408) and BD1 (gallery, y 1344) |
| `\|` | bars between lobby and vault, sill 32 |
| `w` | windows onto the basin: lobby (sill 48), gallery (sill 112, floor 72), tank hall (sill 48) |
| `r` | ready room, 0 |
| `s` | stair, 24/48, up to the gallery |
| `g` | gallery, 72 |
| `!` | switches: BD1's on its north face; the airlock switch |
| `l` | lift L1, 72 → -72 |
| `p` | pump pit, -72 |
| `o` | pump plinths, 24 |
| `%` | nukage: pit channels (-88), tank (176), falls channel (-32), filter tubs (80), decon pool (-16) |
| `^` | stairs: pit stair (-48→48), the hall's entry steps (48→0), the loft stair (56→128) |
| `n` | pit landing, 72 |
| `h` | tank hall, 0 |
| `T` | tank wall and rim, 192 |
| `/` | tank stair, 24→168 |
| `f` | the rupture: falls (SFALL) from the tank down to the channel |
| `K` | blue key on the rim |
| `#` | grate (MIDGRATE, impassable) where the channel leaves the hall |
| `R` | rocket launcher pedestal |
| `a` | arachnotron and imp closets (blue-key trap) |
| `N` | north annex, 0 |
| `B` | blue door |
| `k` | connector, 0 |
| `F` | filter house, 32 |
| `u` | filter tubs, rim 96 |
| `q` | loft, 128 |
| `e` | east bank, 0, sky |
| `:` | shore step, -8 (east bank); culvert's exit step, -8 (decon hall) |
| `S` | radiation suit pedestal |
| `H` | sampling shed, 0 |
| `~` | spill basin, -32, sky, `DAMAGE_10` |
| `i` / `I` | island step ring -8 / island 0, megasphere |
| `C` | culvert, -32 |
| `d` | decon hall, 0 |
| `P` | pillars |
| `Z` | arch-vile dais, 32 |
| `A` | airlock, 0 |
| `V` | exit vault, 0 |
| `X` | exit switch |
| `D` | doors |
| `1`–`4` | secrets |

Rectangles (map units). They don't overlap, except where one is cut out of another (pillars, tubs, the island, the tank's interior).

| Id | x0..x1 | y0..y1 | Floor / ceiling | Notes |
|---|---|---|---|---|
| LB | 1024..1408 | 320..688 | 0 / 160 | start (1120,544) facing east; north window x 1088..1344, y 688..704, sill 48, lintel 128; bars x 1408..1424, y 512..640, sill 32; shutter BL x 1408..1424, y 352..480 |
| LC | 1216..1408 | 192..320 | 0 / 128 | two closets 96 wide, doors in LB's south wall, disguised as STARG3 |
| S1 | 1024..1152 | 192..320 | 0 / 128 | secret door in LB's south wall at x 1056..1120 |
| LD | 960..1024 | 448..576 | door | DOORTRAK jambs |
| RR | 320..960 | 64..640 | 0 / 128 | locker bays along the south wall |
| PS | 448..704 | 640..784 | 24, 48 | three steps, 48 deep, rising north |
| PGS / PGN | 448..704 | 784..1344 / 1360..1920 | 72 / 192 | windows x 704..768 at y 896..960, 1088..1152, 1216..1280 (south), 1472..1536, 1664..1728 (north); sill 112, lintel 176 |
| BD1 | 448..704 | 1344..1360 | shutter | floor = ceiling = 72; S1 switch on its north side at (672,1360); no use action from the south |
| L1 | 384..448 | 1152..1280 | 72 → -72 | lift; PP ceiling 176 over it |
| PP | 0..384 | 896..1568; 0..192 × 1568..1856 | -72 / 176 | channels -88 at y 1088..1152 and 1344..1408; plinths 128..256 × 960..1056, 1216..1312, 1440..1536 at 24; SSG on the north plinth; trap closet in the west wall at y 1440..1536 |
| S2 | 0..128 | 1664..1856 | 24 / 176 | lit ledge; a SILVER3-faced pump plinth beside it is a hidden lift |
| ST2 / LN2 | 192..384 × 1568..1856 / 192..448 × 1856..1920 | | -48..48 / 72 | six steps, 48 deep, rising north; LN2 opens into PGN at x 448 |
| TV | 512..640 | 1920..2064 | 48, 24 | steps down north into BT |
| BT | 512..2048 | 2064..2624 | 0 / 384 | sky over the tank; south windows x 704..896 and 1600..1792, sill 48 |
| TK | octagon in 1056..1504 × 2160..2560 | | rim 192; interior 176 | interior nukage 1120..1440 × 2224..2496 (`DAMAGE_5`, glows); rupture x 1216..1344 on the south face |
| TS | 960..1056 | 2160..2544 | 24..168 | eight steps, 48 deep, rising north to the rim's west side |
| KP | (1152,2192) | | 192 | blue key on the rim's south segment, W1 ring round it |
| CH | 1216..1344 | 1920..2160 | -32 | falls channel; -8 step strip along its west side inside the hall; grate (MIDGRATE, impassable) at y 1984..2000 |
| RL | 576..640 | 2496..2560 | 16 | rocket launcher pedestal |
| AC | 576..832 | 2624..2752 | 0 / 128 | two trap closets (arachnotron; imps) in BT's north wall |
| NA | 1600..2048 | 2688..2880 | 0 / 128 | door at x 1728..1856, y 2624..2688 |
| S3 / AL | 1664..1792 | 2560..2624 | 192 / 288 | lit alcove in BT's north wall, reached from NA by a secret door and a stair behind the wall |
| BD / FC | 2048..2064 / 2064..2368 | 2176..2304 | door / 0 | blue door, DOORBLU2 jambs |
| FH | 2368..2944 | 1472..2560 | 32 / 256 | tubs 2496..2688 × 1600..1792, 1920..2112, 2240..2432 (rim 96, nukage 80) |
| LF | 2816..2944 | 1472..1664 / 1664..2368 | 56..128 / 128 | four steps rising north, then the loft; parapet on its west edge |
| FD | 2560..2688 | 1408..1472 | door | |
| EB | 2304..2944 | 704..1408 | 0 / sky | shore step 2304..2368 × 768..1344 at -8; radsuit (2400,800) on a lit pedestal |
| SS / S4 | 2752..2944 / 2944..3072 | 960..1216 / 1024..1152 | 0 / 128 | secret door in SS's east wall |
| AD | 2496..2624 | 640..704 | shutter | floor = ceiling = 0; opened only by the CA switch |
| SB | 768..2304 | 704..1920 | -32 / sky | `DAMAGE_10`; split into the wade strip WS (1792..2304 × 704..896) and the rest |
| IR / IS | 1408..1728 × 1152..1472 / 1472..1664 × 1216..1408 | | -8 / 0 | megasphere on IS |
| CU | 1792..1920 | 512..704 | -32 / 96 | culvert; step 1792..1920 × 448..512 at -8 inside DH |
| DH | 1760..2368 | -128..512 | 0 / 256 | pool 1920..2176 × 128..320 at -16; pillars 64² at (1856,0), (2176,0), (1856,384), (2176,384); dais 1952..2176 × -128..-64 at 32 |
| CAD / CA | 2368..2384 / 2384..2688 | 320..448 / 256..640 | door / 0, 128 | airlock switch at (2656,608) |
| VD / EV | 1744..1760 / 1424..1744 | 352..480 / 320..688 | door / 0, 160 | W1 across VD opens LC; exit switch on EV's north wall at x 1552..1616; shutter switch on EV's west wall beside BL |

Triggers:

| Trigger | Where | Effect |
|---|---|---|
| BD1 switch (S1 door open, SW1PIPE) | PGN side of BD1 | opens BD1 (stays open) |
| L1 lift | gallery and pit | SR lift; use action from the top, so monsters can't ride it |
| SSG pickup (W1 ring) | PP north plinth | opens the pit closet |
| Blue key pickup (W1 ring) | KP | opens both AC closets |
| Blue door | BD | DR, blue key |
| Airlock switch (S1 door open) | CA | opens AD onto the east bank |
| Vault entry (W1) | across VD | opens both LC closets |
| Lobby shutter switch (S1 door open) | EV west wall | opens BL |
| Exit switch | EV north wall | exit |
| Secret doors | LB south wall, S2 hidden lift, NA wall, SS east wall | open (DR, ML_SECRET), S2 is a lift |

## Materials

The base family is **STARG** (green-streaked grey panels): **STARG3** on every wall of the hot side's connective tissue and on every facade round the basin. The plant's lockdown shutters are all **SPCDOOR3** with a blinking lamp sector in front: one look for "opens from the far side". **SUPPORT3** (brown-green rivets) is the trim on the hot side, **SUPPORT2** (silver) on the clean side; **DOORTRAK** jambs every ordinary door; **NUKEDGE1** is the riser wherever a floor drops to nukage; **LITE5** marks every secret.

| Area (spaces) | Walls | Trim | Floor / ceiling flats | Reason |
|---|---|---|---|---|
| Lobby (LB, LC, S1) | STARG3; closet faces STARG3 | SUPPORT2 frames the bars and BL (the clean side's trim, where the clean side meets this wall); DOORTRAK at LD; LITE5 beside the S1 panel | FLOOR0_3 / CEIL5_1 with TLITE6_5 red lamp panels | the hot side's front door: base family, red lockdown lamps |
| Ready room (RR) | METAL2, METAL5 locker bays in the south wall | SUPPORT3 at its corners and both doors | FLOOR4_8 / CEIL5_2 | staff room: the only plain steel room |
| Gallery (PS, PGS, PGN, LN2, TV) | STARG3 | SUPPORT3 between window bays; SPCDOOR3 face on BD1 with SUPPORT3 jambs | SLIME14 (riveted plates) / CEIL3_5; steps STEP1 risers | connective tissue along the basin |
| Pump pit (L1, PP, ST2, S2) | PIPE2 (256-wide pipework); plinths PIPES; S2's hidden lift SILVER3 | SUPPORT3 at the lift and the stair top; NUKEDGE1 channel risers; LITE5 by S2 | MFLR8_1 (dark grating) / CEIL5_2; channels NUKAGE3; lift PLAT1 sides, STEP2 top | the pumps: pipes everywhere |
| Tank hall (BT, AC, RL, CH) | BROWN144 (grimy, streaked brown) | SUPPORT3 framing the windows and the blue door; DOORBLU2 at BD; AC faces BROWN144 | FLOOR0_3 at 0 / CEIL5_1, F_SKY1 over the tank; channel NUKAGE1 with NUKEDGE1 risers, its -8 strip SLIME01 | the oldest building, stained by the leak |
| Tank (TK, TS, RW, KP) | SLADWALL; SLADPOIS at the stair foot; the rupture's face SFALL1 (animated falls) | none: a free-standing object | rim and steps SLIME15 / F_SKY1; interior NUKAGE1 | the burst tank, the map's landmark: slime-green, poisoned |
| North annex and alcove (NA, S3/AL) | COMPSTA2 screens | COMPSPAN between screen bays; DOORTRAK at its door; LITE5 by the secret panel | FLAT14 / TLITE6_1; alcove TLITE6_1 floor (lit) | the tank's monitoring room |
| Connector and filter house (FC, FH, LF, FD) | SPACEW4 (riveted tan-green plate); tubs SILVER1 | DOORBLU2 at BD (FC's end); SUPPORT3 at the 32 step, FD and the loft stair; NUKEDGE1 inside tub rims | SLIME16 at 32 / CEIL3_5; tubs NUKAGE1 at 80, rims FLAT23 | filtration: a newer annex, steel tubs |
| East bank and shed exterior (EB, SS outside) | STARG3, the same facades as the basin | SUPPORT3 framing AD (SPCDOOR3) and FD; DOORTRAK at SS | RROCK18 (gravel) / F_SKY1; shore step SLIME01 at -8 | the basin's shore: one open space, one material |
| Sampling shed (SS, S4) | SILVER3 instrument panels | LITE5 beside the shifted panel | FLAT23 / CEIL5_1 | sampling instruments |
| Basin and island (SB, WS, IR, IS) | STARG3 facades all round | NUKEDGE1 at every wall foot | NUKAGE1 (`DAMAGE_10`) / F_SKY1; IR SLIME01, IS SLIME15 | the spill in the middle of the plant; told apart by landmarks (falls N, lobby window S, culvert sign SE, bank E) |
| Culvert (CU) | NUKEDGE1 | GRAYPOIS sign on its DH face; SUPPORT2 where it enters DH | NUKAGE1 / CEIL5_2 | the drain the nukage leaves by |
| Decon hall (DH) | GRAY1 (clean grey panels), GRAYPOIS signs | SUPPORT2 pillars and corners; NUKEDGE1 pool risers; DOORTRAK at VD and CAD | FLAT5_4 / CEIL3_5 with TLITE6_1; pool NUKAGE1; dais FLAT1 with SUPPORT2 riser | the clean side: grey and lit, the first clean room you reach |
| Airlock (CA, AD inside) | GRAY1 | SUPPORT2 round the switch and AD | FLAT5_4 / CEIL3_5 | clean side |
| Exit vault (EV, VD) | SHAWN2, LITE5 strips | SUPPORT2 at the bars, BL and VD; SW1EXIT in a SHAWN2 frame | FLOOR1_7 (glowing) / TLITE6_5 | the exit, as in MAP07: the brightest room |

Notes for the build:

- Every switch sits in a trim frame: BD1's SW1PIPE in SUPPORT3, the airlock's and the lobby shutter's SW1COMM in SUPPORT2, SW1EXIT in SHAWN2/LITE5.
- The red lamp in front of each shutter is a 16-deep sector at the door's foot with a blink effect and TLITE6_5 overhead: the only lights that blink red-panel, so the cue reads.
- Don't change STARG variants within a wall; give a wall relief with a SUPPORT3 pilaster.

## Secrets

| # | Where | Hint | Reward |
|---|---|---|---|
| 1 | A maintenance closet behind the lobby's south wall (S1) | A STARG3 panel shifted out of line, LITE5 strip beside it, in the room you start in | backpack, green armor |
| 2 | A lit ledge in the pump pit's north-west corner (S2), at 24 | The ledge and its blue armor are lit, in view from the lift; the pump beside it is the only one faced in SILVER3, and using it lowers it | megaarmor, box of shells |
| 3 | The alcove high in the tank hall's north wall (AL), at 192 | Visible from the tank rim, lit; reached from the north annex through a COMPSTA2 screen shifted out of line, with LITE5 beside it | plasma rifle, cell pack |
| 4 | Behind the sampling shed (S4) | A SILVER3 panel shifted out of line in the shed's east wall, LITE5 beside it | soulsphere (just before the wade and the arch-vile) |

## Targets

| Target (DOOM II median) | Plan | Where it comes from |
|---|---|---|
| Optional share of area ≥ 0.3 [0.5] | ≈ 0.4 | The basin is about 1.9M of a reachable 5.5M; only the wade strip (0.1M) is critical, so the basin must be split into the strip and the rest. Plus NA, AL, the loft, SS and S4, CA, the island, S1, S2 and the hall's east half beyond the route line. |
| Distinct floor heights ≥ 15 [23] | about 30 | -88 pit channels; -72 pit; -48, -24, 0, 24, 48 pit stair; -32 basin, culvert, channel; -16 decon pool; -8 shore, island ring, culvert step, channel strip; 0; 16 RL pedestal; 24 plinths, S2; 24/48 PS; 32 FH, dais; 56, 80, 104 loft steps; 128 loft; 72 gallery; 80 tub nukage; 96 tub rims; 24–168 tank stair; 176 tank nukage; 192 rim and alcove |
| Secrets ≥ 2 [4] | 4 | S1–S4 |
| Light-effect sectors ≥ 3 [9] | about 11 | lobby blink, three shutter lamps (BL, BD1, AD), pit flicker (2), tank nukage glow, radsuit pedestal glow, culvert flicker, DH strobe, vault glow |
| Deaf share (UV) ≥ 0.2 [0.42] | ≈ 0.7 | every monster except the ready room's and the tank hall's imps (as built: all of them, see the playtest notes) |
| Most-used wall texture 0.2–0.45 [0.3] | ≈ 0.35 STARG3 | the basin facades (about 5,500 long × 224–288 high), the gallery, the lobby, the bank. If it reads above 0.45, lower the basin's sky ceiling so the facades are shorter. |
| Rule-2 seams with a border ≥ 0.5 [0.31] | ≥ 0.7 | SUPPORT3/SUPPORT2 at every area boundary and window bay; DOORTRAK, DOORBLU2 or shutter jambs at every door; NUKEDGE1 at every nukage riser; every switch framed |

Balance targets:

- **Ammo:** UV pistol-start ratio 2.0–2.4. MAP07's human playtest ran dry at 1.9 and asked for more.
- **Health:** 35–45 per 1,000 monster HP, not counting the megasphere (optional, in nukage) or the soulsphere (secret).
- **Skill ratios:** easy/UV ≈ 0.44, HMP/UV ≈ 0.71 as planned. The arch-vile is on HMP and UV; easy gets a hell knight on its dais.
- **Weapons:** shotgun (lobby), chaingun (gallery), super shotgun (pump pit), rocket launcher (tank hall), plasma rifle (secret 3).
- **The arch-vile:** the static balance doesn't count resurrections. Budget ammo for the decon hall's fodder twice over (about 500 HP more).

### As built

Measured by the build (`levels/nukage_lockdown.py`, 123 sectors, monsters 34/55/78): every target above is met. Playtested with `levels/playtests/nukage_lockdown.playtest` (below).

| Target | Built |
|---|---|
| Optional share | 0.43 |
| Distinct floor heights | 25 (the plan estimated about 30; still above id's median of 23) |
| Secrets | 4 |
| Light-effect sectors | 15 |
| Deaf share (UV) | 1.0: every monster is deaf, the ready room's too (see the playtest notes) |
| Most-used wall texture | 0.27 |
| Rule-2 seams with a border | 0.99; the one unbordered seam is the east bank's NUKEDGE1 riser meeting the basin's STARG3 wall at (2304,1408), left as it is |
| Ammo ratio (UV, pistol start) | 2.30; lowest detour ratio along the route 1.70, the lowest thorough ammo left / HP 0.88 |
| Health per 1,000 monster HP | 44.7 |
| Easy/UV, HMP/UV | 0.44, 0.70 |
| Nearest monster to the start | 304 |
| Whole-map symmetry | 0.70, above id's IQR (0.43–0.64): the loop round a square basin is close to square. The doc set no target; the wings differ in material, height and light |

Changes from the plan above, and why:

- **Lobby and vault are 0/128**, not 0/160, so the SPCDOOR3 shutter and the BIGDOOR2 doors fill their walls with no recesses. The lobby window's lintel is 112.
- **Shutters are single 128-wide door sectors** (BD1, BL, AD) with each face split in the middle, because SPCDOOR3 is a 64-wide picture (see the playtest notes for why not two doors). BD1 is 128 wide in the middle of the gallery, with a 16-deep SUPPORT3 strip on each side; the gallery's ceiling is 200 so the face fills it. Each shutter's lamp is a 16-deep blinking strip on its locked side (the whole east wall of the lobby, for BL).
- **BD1's switch** is SW1PIPE, 128 wide, at y 1376..1504 on the gallery's east wall; the north gallery windows moved to y 1536 and 1728 to make room.
- **The tank is a rectangle** (1056..1504 × 2160..2560), not an octagon: the eight-step stair needs a straight 384-long west face. Its stair has eight 24 steps from 24 to 192, the top one level with the rim.
- **The tank's nukage doesn't hurt**: the style check wants a damaging floor below every dry neighbour, and the tank (176) drops through the rupture onto the dry strip beside the channel. It glows instead.
- **The tank hall is 736 deep** (y 2016..2752), so a 192-wide aisle runs north of the tank: the falls channel cuts the hall's south side in two. The closets, the north annex and secret 3 moved north with the wall.
- **Secret 3** is reached by a shifted COMPSTA2 panel in the annex's west wall, a small room and a lift (s3l, 192 → 0) up to the alcove (AL, 1344..1472 × 2752..2848), which is the secret sector.
- **The pump pit's channels** run 0..288 and the pit stays dry along its east side, so the route through the pit doesn't have to wade. Secret 2's lift is a 128×64 lift faced in SILVER3 in front of the ledge.
- **The dais is 24**, so the player can climb it to the arch-vile; a pillar stands south of the culvert's exit step, so the dais isn't in view as you climb out.
- **The shed's door is 128 wide** (BIGDOOR2 is a 128-wide picture).
- **Ammo**: a second shell box in the pit, a box of bullets instead of a clip on the north gallery, a rocket box and a shell box in the tank hall, which brought the UV ratio from 1.94 to 2.25 and the blue-key leg's detour ratio from 0.93 to 1.37.
- **The ready room's monsters** face away from the lobby door, so none starts facing the player.
- **Stair risers** in the gallery family are METAL (STEP1 is 16 tall and warns on a 24 riser).
- **The exit reads from the start** (after a human playtest: "I see a room in front of me, but I can't tell it's the exit"). The plan put SW1EXIT on the vault's north wall, side-on to the start, behind a MIDGRATE whose bands hid most of the room. As built, the opening is a plain window (sill 32, which neither the player nor a monster can climb, so the reach check still needs the blue key to reach the vault), and the exit switch is on the west face of a lit console (`ev_console`, 1504..1520 × 560..592, 72 high) straight ahead of the start, 384 away, under a hanging EXITSIGN (`ev_sign`, 1472..1488 × 544..608, 16 below the ceiling). The console's face is 112 east of the window, beyond use range from the lobby. The walk-over line that opens the lobby closets now runs only south of the console (y 320..512), so it never sits between a player and the switch.

### Playtest

The wiring run (`uv run -q --with vizdoom scripts/tools/playtest.py wads/NUKAGE.WAD MAP08 levels/playtests/nukage_lockdown.playtest`) passes all 31 checks: every shutter, both lifts and the secret lift, all three traps, the four secrets, the suit, the megasphere and the exit. The static balance prints no warnings. Changes the playtest led to:

- **Shutters are one door sector each.** Two 64-wide door halves side by side each opened only to the other's closed ceiling, 4 below their own floor. Each shutter is now one 128-wide sector whose faces are split at the middle, so SPCDOOR3 fits each half.
- **Window sills.** The lobby window's sill is 32 (it was 48, above eye height, so the basin didn't show from the start) and the gallery windows' sills are 104 (32 above the gallery). Both are still too high to climb.
- **The lobby window is barred** (MIDGRATE), and it and the gallery windows carry sound-blocking lines on both faces. In the first fight runs the first shots in the lobby woke all four basin cacodemons, which have a line of sight to it through the window, and they flew in and killed the bot at the start (seed 1: 11 starved deaths in the lobby). The cacodemons now face west (the gallery pair) and east (the bank pair).
- **The ready room's monsters are deaf.** Awake, they came through the lobby door at the first shot; now you meet them in their room.
- **The lobby holds a box of shells** instead of 4 shells, for the ready-room fight.
- **A box of shells and a box of bullets by the blue door.** Taking the key opens the arachnotron closet while the hall's mancubus is still near the door, and every seed ran dry in the hall after the key (seed 2: 18 starved deaths); the curve hid it, because the ammo for that fight was further along the leg. To stay inside the ammo target, the loft lost one box of rockets and the decon hall's cell pack is a cell.
- **The suit is the last thing taken on the bank.** The route script took it first, and the bot's suit ran out during the bank fight; a player chooses when to take it.

Fight runs on UV, seeds 1–3, after those changes:

| Seed | Kills | Deaths (labels) | Skipped steps | Ammo left |
|---|---|---|---|---|
| 1 | 73 | 8 (5 combat, 3 stuck) | 0 | 12 bullets, 34 shells, 10 rockets, 25 cells |
| 2 | 74 | 12 (11 combat, 1 stuck) | 2 | 24 shells, 4 rockets |
| 3 | 78 | 17 (5 combat, 5 stuck, 4 hazard, 3 unseen) | 6 | 46 bullets, 12 shells, 3 rockets |

No death is `starved`. Clusters and calls:

- **Filter house** (every seed, 2–6 deaths in the aisles beside the tubs): the bot stands in a 128-wide aisle punching the baron and the hell knight with the berserk, 145 cells unused. Bot. It's the map's hardest fight, by design; a human should judge whether the aisles are too tight.
- **Pump pit** (seeds 2, 3: stuck at the S2 lift and the pit stair's foot): the bot loses the lift's timing and gets caught on the stair while imps hold it. Bot; the wiring run walks both.
- **The tank hall after the key** (seed 2: 5 combat deaths in 6 s walking back from the stair): the arachnotron's closet and the mancubus together, with no rockets left. One seed of three; the other two lost at most one life there. Left as it is: it's the trap.
- **The culvert and the decon hall** (seed 3: 3 hazard deaths, health 1): the bot backed into the culvert's nukage, suit spent, fighting the arch-vile's group. Bot.
- **Unseen** (seed 3, once each): spectres in the dark pit (the doc's intent), the north annex's chaingunner when its door opens, an airlock imp behind the switch.

## Build risks

- **The safe start through two openings.** The lobby has bars to the vault (empty until you enter it) and a window over the basin. No monster in the basin may see the window at the start: put the four cacodemons deaf, outside the window's view (north-west, behind the gallery's line, and in the basin's middle-east, facing away), and check with the build's line-of-sight test. Deaf monsters still wake on sight.
- **Sealing the basin.** The basin must be enterable only from the east bank's shore step, or the culvert and the decon hall are reachable without the blue key. Every window sill must be more than 24 above the floor it's in (the gallery's is 40); the channel's exit is an impassable grate; the shore step is the only place where floors within 24 meet the nukage. The reach check's running-jump model will flag a window that can be jumped through: check that no basin sector is reached before the blue door.
- **Pits without an exit.** Every nukage floor needs a way out within 24: the pit channels (16 deep), the tank interior (16 below the rim), the falls channel (its -8 strip inside the hall, and the grate stops you leaving), the basin (the shore step, the island ring, the culvert step), the decon pool (16). A player who drops off the rim into the channel walks out by the strip.
- **Shutters with no use action from the near side.** Build BD1, AD and BL as tagged doors opened only by their switches (S1 door open); no DR on their faces. The reach check should show each switch reached before its door is passed.
- **The lift L1 travels 144.** The space it lowers into needs a ceiling at least 56 above the lift top (the pit is 176). Give it a use action from the top in `SPECIAL_BETWEEN`, not the default walk-over, so the pit's demons don't ride it up.
- **The tank.** An octagon of 8 wall sectors, a ring of rim sectors and an interior; the rupture is a gap in the south wall where the interior (176) meets the channel (-32) with SFALL1 as the lower texture, 208 tall. SFALL1 is 128 tall, so it tiles; peg it so its seam isn't at eye height. The sky ceiling over the tank sits under the hall's 384 ceiling: cut it as the tank's own ceiling, so the hall's walls don't show sky.
- **Long sightlines over the basin.** The basin is 1536×1216 and open. No hitscanner anywhere with a line across it: the gallery's chaingunner stands at the shutter, out of the windows' view of the east bank, and the bank's monsters are projectile users.
- **The arch-vile's attack ignores range.** It needs only a line of sight, so the decon hall's four pillars are the cover, and nothing in the vault or the lobby may see into the hall through VD (the vault door is shut until used). The vile can't be in sight of the culvert mouth, or you'd take its flame climbing the step.
- **Lobby closets shooting through bars.** Bars (impassable) stop the closet monsters but not their shots, which is the point. The two revenants' missiles home: the vault is 320 deep, so the exit switch is reachable, but test it.
- **Set bookkeeping.** Add MAP08 to README "Included WAD" and SPOILERS, and write the preview `wads/NUKAGE-MAP08.svg`.

## Concepts considered

1. **Locked Out (chosen; nukage added after the user asked "where's the NUUUUUUUKAGE???").** A loop that comes back to the start from the far side of the glass, gated by doors opened from their far side. The spill basin, the burst tank and the wade back through the nukage were added to make the loop circle the spill and close through it.
2. **Cascade.** A terraced hillside of settling ponds, descended one one-way drop at a time, with the exit pumphouse visible from the top terrace.
3. **The Bowl.** You drop into a vast cooling tower's basin and escape through the intake tunnels and up the outside to its base.
4. **The Pipeline.** One straight 4,000-unit trunk main, crossed section by section through airlock bulkheads that shut behind you.
5. **Crater.** The plant has collapsed into a sinkhole; you cross it on rubble and a fallen cooling stack.

Locked Out wins because:

- **Its goal is behind you.** The exit is in view from the first frame, and every window round the basin shows the lobby again, so the player always knows where they're going without a central room to return to.
- **Far-side shutters are legible and make the loops.** One material (SPCDOOR3 with a red lamp) means "opened from the other side"; each one you open is a shortcut back.
- **The nukage carries the route.** You see the spill from the start, watch its source on the tank, and close the loop by wading it.
- **Its mechanisms are cheap:** doors, one lift, W1 closets. No rising floors.

The others lose:

- **Cascade** is a descent, and SPEEDY already has three; its open terraces invite long-range hitscan.
- **The Bowl** repeats MAP06's one-way sink into a pit.
- **The Pipeline** is one trick at every bulkhead, with long sightlines and one material.
- **Crater** needs irregular geometry, which is slow and fragile in this builder.
