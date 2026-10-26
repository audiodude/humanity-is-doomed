# Nukage Undercurrent (`nukage_undercurrent`)

## Concept

**Cross the turbine hall west to east on the gantry, sink to its floor, and fight your way back underneath the gantry to the exit you saw from the start.**

- **Shape:** one long hall crossed twice, at two heights and in opposite directions: a horizontal hairpin folded vertically. On the first crossing you look down at everything you'll walk through on the second. On the second, the gantry you walked along is the arachnotrons' firing line.
- **Theme:** the turbine hall of the nukage plant. Four turbine housings stand in a grey hall 2048 long and 384 high. A railed gantry runs the length of its north wall, and a control annex, a bronze generator house and a flooded sump open off it.
- **Difficulty:** medium-hard. About 24/46/63 monsters on easy/HMP/UV. **Debut: the arachnotron.**
- **Slot:** MAP06 of `NUKAGE.WAD`. No other module changes: UMAPINFO entries without `next` follow slot order, so MAP05 leads to MAP06.

How it differs from the set:

| Map | Shape in a phrase |
|---|---|
| MAP01 Nukage Junction | the template: courtyard hub, one wing per key |
| MAP02 Nukage Crossing | two banks of a canal, joined by a sluice gate that sinks into a bridge |
| MAP03 Nukage Core | a spiral climb around a reactor to the crown |
| MAP04 Nukage Divided | a fork into two wings that never meet, keys crossed |
| MAP05 Nukage Drain | a ring of walkways raised one by one out of a flooded reservoir |
| **MAP06 Nukage Undercurrent** | **one hall crossed twice: over it, then under it** |

None of these crosses the same space twice at two heights. The SPEEDY maps don't either: they're hubs, spiral shafts, descents and canyon crossings.

## Route

Heights are floor/ceiling. Coordinates are in the sketch's rectangle table.

1. **Start booth (SB)**, 256×192, 160/288. A quiet booth behind the hall's west wall, with an open 128-wide window onto the gantry. **Visible:** the whole hall down the gantry's length, the blue door at the far east end, the break in the gantry halfway along, the turbines below. **Gate:** none. **Encounter:** none; nothing can see the start. **Pickups:** shotgun, 2 clips, stimpack.
2. **Balcony (BA) and gantry segment A (GA)**, 768×192 plus a 256×160 balcony, 160/384. A railed gantry with a grate floor along the north wall. **Visible:** from the balcony, straight down onto the yellow exit door in the west wall with its EXIT sign (door before key). Also the hall floor and turbines T1 and T2, and the secret ledge (LS) lit on the south wall. **Gate:** the gantry is broken at x 768 (the gap, GB); the only way on is door N1 into the annex. **Encounter:** fodder at range below: 3 zombiemen and 2 shotgun guys among T1/T2 (deaf, facing south), 2 imps on the turbine tops at 128 throwing up at you, and a cacodemon (HMP+) over the gap. **Pickups:** super shotgun on the balcony, about 250 units from the start; shells.
3. **Annex corridor N1**, 128×576, 160/288, grey. **Gate:** door N1 from the gantry; door into the control room halfway up. **Encounter:** 2 imps. A shifted panel with a light line in the west wall leads to secret 2 (SR).
4. **Control room (CR)**, 320×320, 176/320. Banks of screens and raised console desks at 216. **Visible:** its south window looks down into the gap bay's nukage pool (PB) and out across the hall. **Gate:** the blue key sits on the centre console. Taking it opens two panels in the ring corridor (NC) behind the room. **Encounter:** 2 shotgun guys and a chaingunner behind the desks (turrets). On the key, 2 demons (easy: 1) come round the ring from either side, which is what the ring is for. **Pickups:** chaingun, bullets, medikit.
5. **Ring corridor NC and corridor N2**, 128 wide, 160. NC loops behind CR from N1 to N2, so the annex is a loop. N2 leads back down to the gantry. **Optional:** the switchgear vault (SV), off N2's east side.
6. **Switchgear vault (SV)**, optional, 256×256, 144/256, dark and blinking. **Encounter:** a cacodemon (HMP+) and 2 imps among cabinets. **Pickups:** green armor, a box of bullets.
7. **Gantry segment B (GBn)**, 1088×192, 160/384. **Visible:** below, the floodgate (FG) across the floor aisle at x 1024, a 128-high wall whose lowering you'll need later. Also turbines T3/T4 and the hell knight pacing the east floor. The gantry wall holds two closets you can't yet tell from the wall (AR1 here, AR2 back on segment A). **Gate:** the blue door at the east end. **Encounter:** 2 imps on T3/T4 tops, 2 cacodemons over the floor aisle (UV; HMP 1), and the hell knight below (deaf, unable to reach you; he's waiting for the return). **Pickups:** rockets are not yet useful; shells and a medikit by the blue door.
8. **Vestibule (V) and generator gallery (arms Wa, Na, Sa)**, 160/320, bronze. A 128-wide gallery running round three sides of the generator well and joined at its east end by the cradle, so the gallery is a loop. **Visible:** down into the well (WL), where the generator column glows and 3 demons and 2 spectres pace (deaf, unable to climb). That's the room you're about to sink into. **Gate:** railed inner edges, so the only way into the well is the cradle. **Encounter:** 3 imps on the arms, 2 shotgun guys at the far end of the north arm, with the generator column breaking line of sight across the well. **Optional:** stairs (ST) up from the north arm to the loft (LO).
9. **Loft (LO)**, optional, 384×128 plus stairs at 184/208/232, floor 256. **Encounter:** 2 imps. Secret 3 (the plasma rifle) is behind a shifted panel.
10. **The cradle (CD), the set piece.** A 256×384 platform at 160, flush with the gallery arms, at the well's east end. The yellow key stands on a spotlit pedestal in its middle. A 16-wide parapet (LIP, 200) separates it from the well. **Taking the key lowers the cradle and the parapet together** (same tag, floor lower to lowest neighbour, 0): you sink slowly, 160 units in about 5 s, the walls rising around you. The parapet sinks with you and opens onto the well's demons. A second line on the pedestal opens the door in the cradle's east wall (CDE) at floor level, showing the boiler room. The gallery arms are now 160 above you: **one way**. **Encounter:** the well's 3 demons and 2 spectres (meat shields, deaf) converge as the parapet drops. **Pickups:** none on the cradle; a medikit and shells in the well.
11. **Boiler room (BR)**, 288×960, 0/256, flickering. **Encounter:** a revenant (HMP+; easy: an imp) on a dais at 48 (priority threat, deaf) and 3 imps (fodder). **Pickups:** **rocket launcher**, rockets, a medikit.
12. **Pipe gallery (PG)**, 752×192, -32/128, dark, blinking. Pipe columns along it serve as cover. **Encounter:** 2 chaingunners at the far (west) end behind the pipes, close range in the dark, and 2 spectres (all deaf). **Pickups:** a box of rockets, a stimpack.
13. **Boiler passage (BP)**, 128×608, -16 rising to 0. It ends at door EL in the hall's east wall. The door opens only from this side (a W1 line in the passage), so the hall can't be entered early from the lower wing.
14. **Hall floor, east (FE)**, 0/384. **The return.** Crossing the hall threshold opens closet AR1 on the gantry above. **The arachnotron** walks out onto the gantry you crossed half an hour ago, with 2 imps, and fires down. T3/T4 are the cover. The hell knight from step 7 closes in on the floor. **Gate:** the floodgate across the aisle at x 1024. **Encounter:** arachnotron (all skills: it's the debut), the hell knight, 2 imps, and any turret imps still alive. **Pickups:** rockets, a stimpack behind T4, cells on HMP- (for anyone carrying the plasma rifle).
15. **Sump stairs (S2) and sump hall (SH)**, 576×384, -40/96, low, dark and blinking, with three glowing nukage pools at -56. Door S2 in the hall's south wall, east of the floodgate. **Encounter:** 4 spectres (HMP 3, easy 2) in the dark. **Optional:** the pump room (PR) to the west, the cooling yard (CY) to the south, and (secret 1) a shifted panel in the east wall.
16. **Switch booth (SWB)**, 160×176, -16. A brown booth with the floodgate switch. Its barred window (WIN, sill 48) looks onto the hall floor right beside the gate, so you watch the gate sink. **Gate:** the switch lowers FG to 0. Return to the hall the way you came (S2).
17. **Pump room (PR)**, optional, 384×256, -40. **Encounter:** 3 imps, 1 demon. **Pickups:** berserk.
18. **Cooling yard (YC, CY)**, optional, 704×448, open sky. Walkways at -64 across a nukage pond at -80; no suit needed. **Encounter:** 2 cacodemons (HMP+) in open air, 3 imps on the far bank. **Pickups:** megaarmor on the pond's island walkway, 2 rocket boxes.
19. **Hall floor, west (FW)**, 0/384. Crossing the lowered floodgate (W1) opens closet AR2: the second arachnotron (UV/HMP) walks out onto gantry segment A, above the exit. **Optional:** the gap bay (GB/PB) under the gantry's break holds secret 4 and items. Lift L1 (use from the floor only) rises to the balcony and the start, which closes the loop through the start.
20. **Exit approach.** A W1 line at x 384 opens closet MC in the south wall: a mancubus (HMP+; easy: 2 imps) and 2 imps. The yellow door (EX) is in the west wall under the balcony.
21. **Exit vault (EV)**, 288×320, floor 16, bright and pulsing, with an EXIT sign and an exit switch.

## Sketch

Plan at 64 units per character across and 64 per row; row labels give the top edge (y), and the x ticks are every 512 units starting at x = 0.

```
  1216                11nnnnn22vvvv
  1152                11nnnnn22vvvv
  1088             $$$11CCCCC22vvvv
  1024             $$$11CCCCC22vvvv               oooooo^^^
   960                11CCCCC22                   oooooo^^^
   896                11CCCCC22                         ^^^
   832           AAA  11CCCCC22      AAA                ^^^
   768           AAA  11 ~~~ 22      AAA        ggggggggggg
   704           AAA  11 ~~~ 22      AAA        ggggggggggg
   640   ssss============...=================   ggwwwww|KKK BBBB
   576   ssss============...=================VVVggwwwww|KKK BBBB
   512   ssss============...=================   ggwwwww|KKKDBBBB
   448       bbbbLL..........#...............   ggwwwww|KKKDBBBB
   384       bbbbLL..........#...............   ggwwwww|KKK BBBB
   320  EEEE ................#...............   ggwwwww|KKK BBBB
   256  EEEE ................#............... P ggggggggggg BBBB
   192  EEEEY................#...............DP ggggggggggg BBBB
   128  EEEE ................#............... P             BBBB
    64  EEEE ................#............... P             BBBB
     0         MMM ****      xx22             P             BBBB
   -64         MMM  ll       xx22             P             BBBB
  -128              cc       xx22             P ppppppppppp BBBB
  -192              cc    hhhhhhhhh           P ppppppppppp BBBB
  -256              cc    hhhhhhhhh           P ppppppppppp BBBB
  -320              rrrrrrhhhhhhhhh
  -384              rrrrrrhhhhhhhhh
  -448              rrrrrrhhhhhhhhh
  -512              rrrrrrhhhhhhhhh
  -576                        yy
  -640                    YYYYYYYYYYY
   ...                    YYYYYYYYYYY   (cooling yard to y -1088)
             |       |       |       |       |       |       |
             0       512     1024    1536    2048    2560    3072
```

Legend: `s` start booth (player start at (-128,544), facing east) · `=` gantry 160, railed · `b` balcony 160 · `L` lift L1 0↔160 · `.` hall floor 0 (turbines T1-T4 stand on it, not drawn) · `#` floodgate 128→0 · `~` gap-bay nukage pool -16 · `1 n 2` annex corridors 160 · `C` control room 176 · `$` secret server room · `v` switchgear vault 144 · `A` arachnotron closets 160 · `V` vestibule (blue door at x 2048) · `g` gallery arms 160 · `w` well 0 · `|` parapet 200→0 · `K` cradle 160→0 · `D` doors CDE/EL (one-way into the hall) · `B` boiler room 0 · `p` pipe gallery -32 · `P` boiler passage · `^` loft stairs · `o` loft 256 · `x` switch booth and window · `h` sump hall -40 · `r` pump room · `c l *` secret corridor, lift, ledge 96 · `M` mancubus closet · `E` exit vault 16, `Y` its yellow door (x 0) · `y Y` (south) yard corridor and cooling yard.

Section north–south through the east half of the hall, x ≈ 1600, looking west:

```
 y=0 (S wall)                                   448        640 (N wall)
 384 +-------------------------------------------------------+  ceiling 384, light strips over the lane
     |                                       rail :  AR1     |
 160 |                                     +------+----------+  gantry 160 (grate floor)  <- pass 1, W->E
 128 |  [plinth 16][ T4 128 ]              | METAL|
   0 +--south half (optional)---lane-------+ face |              hall floor 0              <- pass 2, E->W
```

Rectangles (map units). They don't overlap, apart from BA and L1, which are cut out of FW:

| Id | x0..x1 | y0..y1 | Floor | Notes |
|---|---|---|---|---|
| SB | -256..0 | 448..640 | 160 | start; window x 0, y 480..608 |
| GA | 0..768 | 448..640 | 160 | rail on the south edge and the east end; N1 door x 576..704 |
| BA | 0..256 | 288..448 | 160 | balcony; rail except where L1 meets it |
| L1 | 256..384 | 320..448 | 0↔160 | use from the floor faces only |
| GB / PB | 768..960 | 448..640 / 640..768 | 0 / -16 | gap under the gantry break / pool recess |
| GBn | 960..2048 | 448..640 | 160 | rail; N2 door x 1024..1152; AR1 x 1536..1728 |
| FW / FE | 0..1024 / 1088..2048 | 0..448 | 0 | split each into a north lane (y 320..448, under the gantry face) and a south half (the plinths' surroundings) |
| FG | 1024..1088 | 0..448 | 128→0 | flat = hall floor flat |
| T1-T4 | centres T1 (448,160), T2 (832,160), T3 (1440,160), T4 (1792,160) | r 96 | 128 | octagonal housings on 320² plinths at 16, y 0..320 (T1 x 288..608, T2 672..992, T3 1280..1600, T4 1632..1952); S2's door (x 1152..1280) and EL's approach stay clear of plinths |
| N1 | 576..704 | 640..1216 | 160 | CR door at x 704, y 896..1024; secret panel at x 576, y 992..1056 |
| CR | 704..1024 | 768..1088 | 176 | window onto PB at y 768, x 768..960; desks at 216 |
| NC | 704..1024 | 1088..1216 | 160 | NC closets in the north wall |
| N2 | 1024..1152 | 640..1216 | 160 | CR door at x 1024, y 768..896; SV door at x 1152, y 1024..1152 |
| SR | 384..576 | 960..1088 | 168 | secret 2 |
| SV | 1152..1408 | 960..1216 | 144 | optional |
| AR2 / AR1 | 256..448 / 1536..1728 | 640..832 | 160 | closets, faces textured as the hall wall |
| V | 2048..2240 | 480..608 | 160 | blue door at x 2048 |
| Wa / Na / Sa | 2240..2368 / 2368..2960 / 2368..2960 | 128..768 / 640..768 / 128..256 | 160 | rail on edges facing the well |
| WL | 2368..2688 | 256..640 | 0 | generator column x 2464..2592, y 384..512 (void) |
| LIP | 2688..2704 | 256..640 | 200→0 | same tag as CD |
| CD | 2704..2960 | 256..640 | 160→0 | yellow key at (2832,448) |
| CDE | 2960..2976 | 384..512 | door | floor 0 |
| ST / LO | 2752..2944 / 2368..2752 | 768..1024 / 896..1024 | 184-256 / 256 | 4 steps 64 deep |
| BR | 2976..3264 | -320..640 | 0 | dais 48 at x 3072..3200, y 384..576 |
| PG | 2208..2960 | -320..-128 | -32 | steps up to BR at its east end |
| BP / EL | 2080..2208 / 2048..2080 | -320..288 / 96..224 | -16..0 / door | 32-unit gap of void between BP and Wa |
| S2 | 1152..1280 | -192..0 | -16, -32 | door at y 0 |
| SWB / WIN | 992..1152 / 1088..1152 | -192..-16 / -16..0 | -16 / 48 | WIN: barred window onto FE beside FG |
| SH | 832..1408 | -576..-192 | -40 | pools at -56 |
| PR | 448..832 | -576..-320 | -40 | door at x 832, y -512..-384 |
| SC / LL / LS | 448..576 / 448..576 / 384..640 | -320..-128 / -128..-64 / -64..0 | -40 / -40↔96 / 96 | secret 1 |
| MC | 128..320 | -160..0 | 0 | closet |
| EX / EV | -32..0 / -320..-32 | 96..224 / 0..320 | door / 16 | yellow door / exit vault |
| YC / CY | 1088..1216 / 832..1536 | -640..-576 / -1088..-640 | -52 / -64, pond -80 | sky over CY |

Triggers:

| Trigger | Where | Effect |
|---|---|---|
| Blue-key pickup | line ring around the CR console | opens the NC closets (2 demons) |
| Yellow-key pickup, line 1 | ring around the cradle pedestal | lowers CD and LIP to 0 (W1) |
| Yellow-key pickup, line 2 | ring around the cradle pedestal | opens CDE (W1) |
| Passage line | BP, before EL | opens EL (W1) |
| Hall threshold | FE, just inside EL | opens AR1 (W1) |
| Switch | in SWB | lowers FG to 0 |
| Floodgate line | across FG | opens AR2 (W1) |
| Exit approach | FW, x 384 | opens MC (W1) |

## Materials

The base family is **STARGR**, the plain grey tech panels, in two variants. STARGR2 (detailed) is for hall walls, between **SUPPORT2** pilasters that jut 16 units every 256, so the hall has a rhythm without a second material. STARGR1 (plain) is for the connective rooms. Each other area has one signature family. Trim is SUPPORT2 in grey areas and SUPPORT3 in bronze and brown ones, with DOORTRAK on door jambs.

| Area (spaces) | Walls | Trim | Floor / ceiling flats | Reason |
|---|---|---|---|---|
| Turbine hall (FW, FE, GB, PB walls, LS opening) | STARGR2 between SUPPORT2 pilasters | SUPPORT2; DOORTRAK at every door; LITE5 jambs on the LS opening | FLOOR0_3 / CEIL5_1, TLITE6_5 strips over the lane; PB NUKAGE1 | base family; the one big space keeps one material, and its two halves read by the turbines, the floodgate and light |
| Gantry and balcony (GA, BA, GBn) | gantry face METAL (structure); rails MIDBARS3 | — | FLAT20 (grate) | structure, not wall: a different object, not a different side of the room |
| Turbines T1-T4, plinths | METAL2 housings | METAL around the lamp tops | tops FLAT23; plinths FLAT19 at 16 | landmarks you navigate by on both passes |
| Floodgate (FG) | METAL6 (warning light strip on top) | — | FLOOR0_3 (same as hall floor, so no seam when lowered) | the one obstacle on the return, flagged by its light |
| Start booth, corridors, closets, passage (SB, N1, NC, N2, AR1/2, MC, BP, EL) | STARGR1 | SUPPORT2 | FLOOR0_6 / CEIL3_5 | connective tissue, base family |
| Control annex (CR) | COMPTALL screens, COMPSTA1/COMPSTA2 under the window | COMPSPAN between screen bays, SUPPORT2 at corners | FLAT14 at 176 / TLITE6_1; desks CONS1_1 at 216 | the control room says "control"; the annex's signature |
| Annex back rooms (SR, SV) | COMPWERD racks | SUPPORT2 | FLAT14 / CEIL5_2 | same signature family as CR (server racks) |
| Generator house (V, Wa, Na, Sa, WL, CD, LIP, ST, LO) | BRONZE1 main, BRONZE2 on the well's 160 faces, BRONZE3 in the loft; generator column PIPEWAL1 | SUPPORT3; blue door: DOORBLU jambs | arms FLOOR5_2 / CEIL5_2; well FLOOR5_4; cradle FLOOR1_7 (red light plate); loft FLOOR5_3 | the bronze wing is warm and old against the grey hall; the cradle's plate marks the set piece |
| Lower generator house (BR, PG) | BRONZE1; PIPES columns in PG | SUPPORT3 | FLOOR5_4 (BR), FLOOR5_1 at -32 (PG) / CEIL5_2 | the same area one storey down; pipes as cover and landmark |
| Sump (S2, SH, SWB, WIN, PR, SC) | BROWN96 (stained), BROWN144 in SH | SUPPORT3; switch SW1BRN1 framed in SUPPORT3; WIN bars MIDGRATE | FLOOR6_2 / CEIL5_2; pools NUKAGE1 at -56 | wet, low, dark: the plant's underbelly |
| Secret lift and ledge (LL, LS) | lift face PLAT1; ledge recess STARGR1 with LITE5 | LITE5 | FLAT19 at 96 | PLAT1 is the secret cue; the LITE5-lit ledge is the tease from the gantry |
| Cooling yard (YC, CY) | ROCK3 retaining cliffs | DOORTRAK at the yard door | walkways FLOOR6_2 / F_SKY1; pond NUKAGE3 | outdoors, so natural rock and sky |
| Exit vault (EX, EV) | STARGR1 with LITE5 strips, EXITSIGN over the door | yellow door: DOORYEL jambs | FLOOR1_7 at 16 / TLITE6_5 | the exit marker: brightest room, glowing |

Every door from the hall into another area is framed in DOORTRAK or a key-colour jamb, so the material changes there, at a border. CR's screens are set in COMPSPAN/SUPPORT2 bays, never straight into STARGR. Switches always sit in a trim frame.

## Secrets

| # | Where | Hint | Reward |
|---|---|---|---|
| 1 | Ledge LS on the hall's south wall, 96 up, above T3/T4. Reached from the sump hall (SH) through a shifted BROWN144 panel in its east wall, the corridor SC, and the PLAT1-faced lift LL. | The ledge is lit (LITE5, light 240) and in plain view from the start and the gantry from the first minute. The panel is offset from its neighbours. | soulsphere, box of rockets |
| 2 | Server room SR, off corridor N1. | A shifted STARGR1 panel with a LITE5 light line beside it, a cue ordinary walls never use. | backpack, box of shells, green armor |
| 3 | Behind the loft's west wall. | A BRONZE3 panel offset and lit differently from the rest of the loft. | plasma rifle (a weapon leaked early) and 2 cell packs |
| 4 | Alcove at the back of the gap-bay pool (PB), under the control room's window. | Seen from the CR window: the pool is lit from inside and the alcove glows. Reachable only on the return, by wading in from the floor. | blue armor, box of rockets |

## Targets

| Target (DOOM II median) | Plan | Where it comes from |
|---|---|---|
| Optional share of area ≥ 0.3 [0.5] | ≈ 0.33-0.36 | Optional: cooling yard (~310k units²), pump room, secret corridor/lift/ledge, switchgear vault, server room, loft and stairs, gap bay, the four closets once open, ring corridor NC, and the hall floor's south half (keep it a separate sector from the north lane the route runs along). Total ≈ 1.2M of ≈ 3.6M reachable. If the build measures under 0.3, enlarge the yard first. |
| Distinct floor heights ≥ 15 [23] | 20 | -80 pond, -64 yard, -56 pools, -52 YC, -40 sump, -32 PG, -16 S2/BP/PB/SWB, 0 hall, 16 plinths/EV, 48 dais/WIN, 96 ledge, 128 turbines/FG, 144 SV, 160 gantry, 168 SR, 176 CR, 184/208/232 stairs, 200 lip, 216 desks, 256 loft |
| Secrets ≥ 2 [4] | 4 | above |
| Light-effect sectors ≥ 3 [9] | 11 | glowing PB pool, SH blink, 3 glowing sump pools, SV blink, flicker in the well, BR flicker, PG blink, glowing CY pond, glowing EV |
| Deaf share (UV) ≥ 0.2 [0.42] | ≈ 0.5 | all closet monsters (NC, AR1, AR2, MC), the well, the boiler room, the pipe gallery and the sump; the floor monsters below the gantry (they wake on sight anyway) |
| Most-used wall texture 0.2-0.45 [0.3] | ≈ 0.3, STARGR2 | the hall's walls are about 2M units² of roughly 5M total; pilasters take ~20% of that. If it reads above 0.45, narrow the pilaster spacing; below 0.2, use STARGR2 in SB and EV too. |
| Rule-2 seams with a border ≥ 0.5 [0.31] | ≥ 0.6 | DOORTRAK or key jambs at every area-boundary door (N1, N2, blue door, EL, S2, PR, YC, EX); COMPSPAN/SUPPORT2 bays in CR; trim frames on every switch; LITE5 jambs on the LS opening and the secret 2 panel |

Balance targets for the build: UV pistol-start ammo ratio 1.6-2.2, 35-45 health per 1,000 monster HP, easy/UV ≈ 0.38 and HMP/UV ≈ 0.73 of monsters with items kept. A weapon within 300 units of the start. Heavy share on UV ≈ 17%: 6 cacodemons, a hell knight, a revenant, 2 arachnotrons and a mancubus.

Static balance as built (resource curve, UV pistol start): the lowest detour ratio is 1.17, at the exit leg (id median 0.65); the thorough curve never runs short (lowest ammo left / HP 0.94); 42 health left at the exit on the detour curve; long-range hitscan peaks at 14/s on the first leg (id's 90th percentile is 88.4). One warning stays, listed in the module's `KNOWN_ISSUES`: **start under fire**, the HMP/UV cacodemon over the gantry break (864,560). It faces south, exactly side-on to the start window to its west (vanilla's 90° counts as in view), about 1000 units off, and it floats over the break you can't cross, so it's the gantry's first target, seen and answered from the window with the shotgun. Turning it would lose that.

## Build risks

- **The cradle and the parapet sinking (the set piece).** Both have the same tag and lower to their lowest neighbour (the well and the closed CDE door at 0). The parapet travels 200 and the cradle 160, at 1 unit per tic, so 5-6 s. The reach check must count the well, CDE and the boiler room as reachable only after the yellow key line. Gallery arms touch the cradle on two sides, so give the arm-to-cradle lines no specials and check that nothing on the arms reaches the lowest-neighbour search (the arms are at 160, so it shouldn't). Don't put a rail on the cradle–well edge: the parapet is the barrier, because an impassable rail would still block the way after the sink.
- **Railings.** Every gantry, balcony and gallery edge facing a drop needs impassable two-sided lines with MIDBARS3 (`dashed = bars/fence` in the preview). A missed rail lets the player drop to the floor early and break the order. Rails must leave a gap where L1 meets the balcony and the gantry.
- **Lift L1** must work only from the floor: override the default walk-over `WR_LIFT` from the top in `SPECIAL_BETWEEN` with a use action on its lower faces (doom-build gotcha). The reach check treats the lift at its top height, so the floor next to it needs ceiling clearance; the hall's 384 is fine.
- **One-way door EL.** It's opened by a W1 line in the passage, with no use action on the hall side. Otherwise a player on the floor could get in from the hall, but the floor is only reachable from BP in the first place, so this is only a guard.
- **Floodgate.** Floor lowers to its lowest neighbour (0). Its flat must be the hall floor flat, and the gantry's 160 face next to its north end must not catch it (it's lowering, not rising, so it won't).
- **Doors in a 384-high hall.** N1, N2, AR1/AR2, the blue door, EL, EX, S2 and MC all need `doorway(..., alcove=, far_alcove=)` recesses 128 high (doom-build gotcha). The gantry doors at 160 sit under a 384 ceiling, so their alcoves are cut into the north wall above the gantry.
- **Long sightlines.** The gantry sees 2048 units of floor. Keep hitscanners only near T1/T2, within about 500 of the balcony, ambush-flagged and facing away. Everything east of the floodgate is a projectile monster, and the cacodemons and the hell knight are deaf until seen.
- **Arachnotrons on a 192-wide gantry.** They have radius 64, so closets need to be at least 192 wide, as planned. Rails keep them from falling, and they must be able to step out (closet floor = gantry floor, 160).
- **Shared vertices.** The gantry break, the plinths in the split floor lanes, the parapet strip, WIN against FE beside FG, and the pilaster jogs along 2048-unit walls all have neighbours meeting mid-edge. Add the vertices.
- **Sector count.** About 130-160 with pilasters, plinths and stairs, which is within the IWAD band.
- **Set bookkeeping.** README "Included WAD" and SPOILERS sections for MAP06; preview `wads/NUKAGE-MAP06.svg`.

## As built

`levels/nukage_undercurrent.py` is authoritative for coordinates. Departures from the plan above, each for a reason found in the build (the map was built as Nukage Turbine, and renamed once the coolant went in):

- **Secret ledge moved east of the floodgate** (x 1616..1872, reached from the sump's east wall, not the pump room). Dropping off the ledge onto the west floor was a way round the floodgate.
- **Balcony lift (L1).** A lift resting at the top is a platform you can step off, so the balcony was a way down to the floor at the start. L1 is now railed off from the gantry, and a door between it and the balcony opens with the floodgate crossing (the same tag as AR2). Until then it's a lift from the floor to a shut door, and after it the loop through the start is closed.
- **Cradle.** The key ring is 96 across (W1 lower), inside a 160 one (W1 open the door at its foot), so the sink starts just before your hand reaches the key rather than after. The parapet stops 32 short of each end of the cradle, so the cradle touches the well (railed) and has a floor at 0 to sink to. The cradle is at 168, a step above the arms, so its red-light plate isn't a flat change on one level. Its door faces BRONZE3 and opens onto a recess 128 high on the boiler side, so it rises to 124: you can't fit through until the cradle is down, and can't drop into the boiler room without the key.
- **Turbines** are housings with no monsters on top: an imp on a 128-high turbine can't come down and the player can't go up, which fails the 100%-kills check. The turbine imps stand on the floor and plinths instead. Plinths are 16 high, so the south half is walkable all round the housings. Housings glow (LIGHT_GLOW).
- **Boiler dais** is 24, not 48, so the revenant can step down.
- **Doors** have 128-high recesses on any side taller than 128, walled in SUPPORT2/SUPPORT3 (or DOORBLU/DOORYEL/LITE5), which also frames each face for rule 2. The control room, server room, switchgear vault and pump room shrank by those recesses.
- **Hall floor halves.** Each turbine half wraps round the end of the floodgate, so the lit lanes don't meet it. With a lane boundary vertex on the gate's edge, the reach model's running-jump profile skipped the gate sector and let the player "jump" over 128 units.
- **Materials.** The start booth, exit vault and closets use STARGR2 (the hall's texture) rather than STARGR1. The pipe gallery's walls are PIPES. No pilasters: the hall needed none to hold the most-used texture in range.
- **Measured** (build table, DOOM II median in brackets): optional share 0.42 [0.5], 24 floor heights [23], 4 secrets [4], 12 light-effect sectors [9], deaf share 0.42 [0.42], most-used wall texture 0.22 STARGR2 [0.3], rule-2 seams with a border 0.96 [0.31], UV ammo ratio 2.26 [1.81], health 46.8 per 1000 HP [39.8], 26/46/64 monsters. The most-used texture is below the planned 0.3 but inside id's range. The remaining rule-1 slips are door thresholds. Two balance figures sit just above the plan, both inside id's interquartile range: the ammo ratio (2.26 against 1.6-2.2; the same items read 1.95 under the builder's earlier ammo measure) and health (46.8 against 35-45, after the playtest added the control room's medikit, which the route above always promised).
- **Playtest** (`levels/playtests/nukage_undercurrent.playtest`, UV): the wiring run passes with 39 checks and no fails. Two map fixes came out of the fight runs. **The control-room desk** had 16-unit gaps at both ends, which the bot squeezed through, then it died behind the desk with no way back up the 40-unit step (an earlier playtest hit the same thing). The desk now starts at the west wall, and there's a 64-wide walkway round its east end. **The control room's medikit**, which the route above promised, wasn't in the map; it's now on the floor by the west door. After both fixes the three seeds died 5, 31 and 9 times, and every cluster is the bot's: foraging off the route takes the yellow key early (the `expect` before the cradle then fails), it spends its bullets on cacodemons it can't reach and ends up starved with the detour curve still at 5,540 ammo damage at the exit, it loops under the secret-1 lift, and it gets pinned in the balcony's corner (16,304) by arachnotron 2 and the mancubus, both of which a player can fight back from that spot.
- **Switchgear vault door** is a fast door monsters can't open (action 117). The vault is a dead end lying between the annex and gantry B, so monsters woken in the annex, chasing a player on the gantry, walked into it and pressed against its south wall (found in play: a demon and a cacodemon stuck at its door; reproduced in ViZDoom, a demon stayed in the vault for 25 s). Now the ring corridor's demons come down N2 to the gantry, and the vault's own cacodemon waits in its room until you open the door.
- **Coolant nukage in the hall.** Each turbine housing stands in a nukage moat 8 deep (the plinths were dry steps at 16), and a 32-wide nukage channel runs along the south wall: west of the floodgate, and east of it in two lengths either side of the sump door, which bridges it. The channel stops 16 short of the floodgate, because a floor lowering to its lowest neighbour would otherwise sink the gate into the channel. Three things moved out of the new nukage: the zombieman and shotgun guy from the south wall (now just south of the lane) and the stimpack (now between T3 and T4). The switch booth's window bars cover the channel too.
- **Critical path** (reach model): start → gantry A → annex → control room (blue key) → gantry B → blue door → north arm → cradle → boiler room → pipe gallery → boiler passage → hall floor east → sump → switch booth → back → over the floodgate → exit. This matches the route.

## Concepts considered

1. **Over and Under (chosen).** Cross the turbine hall on the gantry, sink into the generator pit, come back across the floor underneath, with the exit seen from the start. Gated by a broken gantry, the blue key, a one-way sinking platform and a floodgate.
2. **The Breach.** Start sealed in the containment core at the centre and work outward through concentric rings. Each ring's door is half-way round, opened from the far side, and the exit is outside the outer wall. The reveal is the next ring through slots in each wall.
3. **The Long Line.** An open-air rail cutting runs straight through the map, with the exit gate in sight 3000 units away from the start. Blast doors across the cutting open from the far side, reached through stations alternating north and south.
4. **Flood Behind.** Descend a terraced plant whose terraces sink into the nukage behind you, then climb back up the opposite side of the valley, looking across at the flooded way down, to an exit beside the start.
5. **Inside the Walls.** Move through maintenance ducts inside the plant's hollow walls, looking through grates into the rooms below, dropping in to clear them and climbing back into the walls.

Over and Under wins for four reasons:

- It's one sentence, and its forced revisit changes the space: the gantry becomes the arachnotrons' firing line, and the floodgate and closets are new on the way back.
- It shows the exit at the start.
- It rests on three cheap mechanisms: one sinking platform, one lowering gate and one lift.
- Nothing in the repo shares its shape.

The others lose on these grounds:

- The Breach is MAP03 inside out, and ring after ring reads alike.
- The Long Line is a straight line with hitscan sightlines, which is on the anti-pattern list.
- Flood Behind repeats MAP05's nukage-level mechanic and the SPEEDY descents, and needs many fragile floor-change actions.
- Inside the Walls puts too much of the map in passages 128 wide or less, and is hard to read.
