# Nukage Crossing (MAP02, NUKAGE.WAD): retexture

## Concept

**A nukage canal cuts the plant in two. You loop round it on brick quays, and a sluice gate sinks into a footbridge so you can cross.**

- Theme: the plant's outdoor canal basin. Three paved yards with brick quay walls (south, north, sealed south-east), a pump hall at the canal's west intake, a steel control tower on the north bank, and small brown-panelled plant buildings.
- Difficulty: medium, the set's second map. Slot: `MAP02` of `NUKAGE.WAD`, module `levels/nukage_crossing.py`.
- **Scope: retexture only.** The shape, route, heights, lights, things and specials stay as built. This map was made before the texture research and the contact sheets, and its walls are a collage. It averages 27 wall textures, and the one outdoor basin uses a different material on each side: `BRICK12` south, `BROWN144` north, `STONE3` south-east. The canal walls switch between `BRICK12`, `SILVER2` and `METAL`. Geometry changes are limited to what the trim needs: recesses beside door faces and switches, and short trim wall lines at seams.

Baseline (`python3 -c "import levels.nukage_crossing as m; from levels import build; build(m, out='/tmp/nc.wad')"`, DOOM II median in brackets):

| Measure | Now | Target |
|---|---|---|
| most-used wall texture | 0.17 BRICK12 [0.3], **below id's range** | 0.25–0.35 |
| rule-2 seams with a border | 0.42 [0.31]; 21 unbordered seams listed | ≥ 0.7 |
| distinct wall textures | 27 | about 20 |

The other maps in the set and their base families. MAP02 takes **BRICK**, which no other map uses as a base.

| Map | Shape | Base family |
|---|---|---|
| MAP01 Outskirts (in progress on its own branch; replaces Junction) | climb a hillside to a station whose deck looks over a nukage spill | ROCK5 / ASHWALL4 |
| MAP03 Core | climb round a reactor core in a moat | TEKBRON / SUPPORT |
| MAP04 Divided | two wings that never meet (lava and screens) | STONE3 |
| MAP05 Drain | pump a flooded reservoir dry, walkways surface | STONE2 / TEKGREN |
| MAP06 Undercurrent | one hall crossed over, then under | STARGR |
| MAP07 Storage | cask maze that sinks into an arena | CEMENT6 |
| MAP08 Lockdown | loop away from an exit you can see, closed by wading | STARG3 |
| MAP09 Meltdown | descent down terraced nukage falls | CEMENT6 |

## Palettes considered

The shape is fixed, so the open choice was the palette, not the concept (step 2 of `doom-design` does not apply).

1. **Brick quays with brown plant buildings (chosen).** One brick for the whole basin, its darker variant for the canal walls, PIPE for the pump wing, SILVER for the tower, BROWN variants for the small buildings. A canal with brick embankments reads at once. BRICK is free in the set. It also keeps the map's best existing pieces: PIPE2 in the pump hall, SILVER in the tower and the brown key doors.
2. **BROWN panels everywhere outside** (BROWN96 yards, BROWN144 canal). This sits too close to MAP08 Lockdown's BROWN144 and SUPPORT3, and a brown-panel quay reads as a shed wall, not an embankment.
3. **STONE2/STONE3 grey blocks.** MAP04 and MAP05 already lean on STONE, and grey stone against grey MFLR8_1 paving makes the basin monotone.

## Route

The route is unchanged. Heights are floor/ceiling; SKY is a 256 sky ceiling. Encounter roles are as in `THINGS`.

1. **Start booth** (start, 512×288; sec1 secret closet). 0/128, light 160. Leaving it: the north door. Visible: through the window, the yard, the canal, the soulsphere island and the red door on the north terrace. Encounter: none. Pickups: shotgun, clip, stim; the secret has green armor and shells.
2. **South yard** (yard_s, about 1250×560; pump housing 72 high in the middle for cover). 0/SKY, light 192. Leaving it: the west door to the pump wing (the gate east stays shut). Visible: the canal and its parapet, the lit ledge, the island, the tower across the water. Encounter: a first fight at range, with zombies and sergeants as fodder, a hitscan screen and barrels. Pickups: shells, clip, stim.
3. **Pipe corridor** (corr1 and corr2, 480×128 and 128×208). 0/128, light 96–112, blinking. Leaving it: open into the hall. Encounter: a spectre or demon at the bend (a meat shield in the dark) and an imp. Pickups: a clip.
4. **Pump hall** (hall_s -16, hstep 0, hall_n 16; ceiling 256; pump plinths 48 and 80; blue-key pedestal 40; intake steps down to the -96 nukage). Light 176. Leaving it: the blue door (blue key). Visible: the canal through the intake. Encounter: deaf waiting imps and sergeants, and a chaingunner on hall_n as the priority threat. Taking the key opens hall_cl behind you (demons, an imp and a spectre: a cut-off ambush). Pickups: chaingun, radsuit, medikit, shells, clip, stim.
   - **Intake and culvert** (intake -96/256, culvert -96/32): optional. The radsuit lets you wade the canal to the **lit ledge** (-72; rocket launcher, secret).
5. **North bank** (yard_n, about 2180×600; crates 64; terrace step 20, terrace 40). 0/SKY, light 192. Leaving it: the tower door, which needs no key. Visible: the sluice gate standing 128 high between its rails, and the pinkies pacing the sealed south-east bank. Encounter: imps and sergeants (deaf), a knight plus a demon on easy, and a caco over the water on UV. Pickups: armor bonuses, medikits, shells, stims.
6. **Control tower** (lobby 0/224; twin stairs from 16 to 96; control room 96/224). Light 112–176. Leaving it: the bridge switch beside the east window lowers the gate. Visible: the gate sinking through the window, and the pier and island below (the hint for the seamless pier door). Encounter: a lobby demon, zombies, an imp, a sergeant. Pickups: super shotgun, shells.
   - **Pier and island** (pier 96, lift to the island at 8, soulsphere pedestal 32): secret, reached through the seamless panel. Health bonuses and the soulsphere.
7. **Filter house** (filter, 512×320, sunken to -24/168; crates 40; sec4 secret closet). Optional, off the north bank. Light 144, flickering. Encounter: imps, zombies, a sergeant. Pickups: medikit, stim, clip; the secret has a backpack and a medikit.
8. **Sluice bridge** (bridge, 128×384; 128, lowering to 0). Leaving it: the far bank. The demons charge across it.
9. **South-east yard** (yard_se, about 880×620; red-key pedestal 24; platform 64; gate and gag switch niches). 0/SKY, light 176. Leaving it: back over the bridge, or through the gate (its switch is here) to the south yard. Encounter: demons as the charge, imps and a caco as harassers, and sergeants. Taking the red key opens secl_e, secl_s and the guardroom (demons, a knight, imps, chaingunners: closets on both flanks). Pickups: medikit, shells, stims, a rocket.
10. **Terrace and guardroom** (terrace 40; guard 192×192 at 40). Leaving it: the red door (red key). Encounter: the guardroom's sergeants and chaingunner, released by the red key.
11. **Exit hall** (192×256, 40/200, glowing). The exit switch is in a niche on its north wall.

## Sketch

Unchanged layout, generated from the module's sectors. One character is 64 units; rows are labelled with their top y. Column 0 is x = -1152, so x = 0 is column 18, 512 is column 26, 1024 is column 34 and 1536 is column 42.

```
    y |0         1         2         3         4      (column)
 2432 |            FFFFFFFF
 2368 |          $$FFFFFFFF                   XX!     <- exit switch (1472,2352)
 2304 |          $$FFFFFFFF                   XXX
 2240 |            FFFFFFFF               KKK XXX
 2176 |            FFFFFFFF               KKK XXX
 2112 |               FF                  KKK  XR     <- red door (1472,2048)
 2048 |             yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy  <- terrace 40 (x 1072-1792)
 1984 |            yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
 1920 |            yyyyyyyyyWWWWWWWWyyyyyyyyyyyyyyyyy  <- tower door (464,1888)
 1856 |            yyyyyyyyyWWWWWWW yyyyyyyyyyyyyyyyy
 1792 | PPPPPPPPPP yyyyyyyyyWWWWWWW yyyyyyyyyyyyyyyyy
 1728 |PPPPPPPPPPP+yyyyyyyyyWWWWWWW yyyyyyyyyyyyyyyyy
 1664 |PPPPPbbPPPPByyyyyyyyyWWWWWWW yyyyyyyyyyyyyyyyy  <- B blue door (-448,1664)
 1600 |PPPPPbbPPPP yyyyyyyyyWWWWWWW yyyyyyyyyyyyyyyyy
 1536 |PPPPPPPPPPP yyyyyyyyyWWWWWWW!yyyyyyyyyyyyyyyyy  <- bridge switch (672,1536)
 1472 |PPPPPPPPPPP yyyyyyyyyWWWWWWWWyyyyyyyyyyyyyyyyy
 1408 |PPPPPPPPPPPP~~~~$$$~~~~~ii~~~~~~~~==~~~~~~~~~~  <- parapets 32; ledge -72 ($)
 1344 |PPPPPPPPPPPP~~~~~~~~~~~~ii~~~~~~~~==~~~~~~~~~~
 1280 |PPPPPPPPPPPP~~~~~~~~~~~~ii~~~~~~~~==~~~~~~~~~~  <- pier 96 (ii), bridge 128->0 (==)
 1216 |PPPPPPPPPPPP~~~~~~~~~~~$LL$~~~~~~~==~~~~~~~~~~  <- lift 96->8 (LL)
 1152 |PPPPPPPPPPPP~~~~~~~~~~~$$$$~~~~~~~==~~~~~~~~~~  <- island 8, soulsphere
 1088 |PPPPPPPPPPPP~~~~~~~~~~~~~~~~~~~~~~==~~~~~~~~~~
 1024 |PPPPPPPPPPP yyyyyyyyyyyyyyyyyyy yyyyyyyyyyyyyy!  <- gag switch (1792,976)
  960 |PPPPPPPPPPP yyyyyyyyyyyyyyyyyyy yyyyyyyyyyyyyyKKK
  896 |PPPPPPPPPPP yyyyyyyyyyyyyyyyyyy yyyyyyyyyyyyyyKKK
  832 |PPPPPPPPPPP yyyyyyyyyyyyyyyyyyy yyyyyyyyyyyyyyKKK
  768 |  PP        yyyyyyyyyyyyyyyyyyyyyyyyyyyrryyyyy  <- gate (864,736); red key (1408,704)
  704 |  PPPPPPPPP+yyyyyyyyyyyyyhhyyyyyyyyyyyyrryyyyy  <- housing 72 (hh)
  640 |  PPPPPPPPP+yyyyyyyyyyyyyyyyyyy yyyyyyyyyyyyyy  <- pump-wing door (-384,624)
  576 |            yyyyyyyyyyyyyyyyyyy yyyyyyyyyyyyyy
  512 |            yyyyyyyyyyyyyyyyyyy !yyyyyyyyyyyy  <- gate switch (912,480)
  448 |                 SSSS ++        yyyyyyyyyyyy    <- start door (320,416)
  384 |                SSS@SSSS              KKK
  320 |             $$$SSSSSSSS              KKK       <- sec1 closet ($)
  256 |             $$$SSSSSSSS              KKK
```

Legend: `S` start booth; `y` yard basin (yard_s south, yard_n north, yard_se east of the bridge); `~` canal (-96) with parapets; `P` pump wing (corridor, hall, intake); `W` control tower; `F` filter house (-24); `K` red-key closets and the pump-hall closet; `X` exit hall; `==` sluice bridge; `ii` pier; `LL` island lift; `$` secret; `b`/`r` blue and red key; `B` blue door, `R` red door, `+` other doors; `!` switch; `@` start.

## Materials

**Base family: BRICK.** The yard basin is one continuous space, so every one of its walls (south, north and south-east yards, the terrace, gate and closet faces) is **BRICK6**, warm brown brick. Its sides are told apart by landmarks, not material: the pump housing in the south yard, the silver tower on the north bank, the red-key pedestal and platform in the south-east, and the terrace's rise and lamps. The canal is the basin's lower level. Its quay walls, below the parapet coping, are **BRICK9**, the darker and grimier variant of the same family, stained by the nukage. Projected from the current wall areas, BRICK6 covers **0.30** of wall area and BRICK9 0.13.

**Trim set: SUPPORT3**, the bronze girder, for every door jamb and recess, switch niche and key pedestal, and every seam in the brick and brown areas. In the silver tower it is **SUPPORT2**, the grey girder. **METAL** (riveted dark plate, a border on the sheets) is the canal's ironwork: parapet rails, the sluice gate, the pier and island sides.

**Signature families**, one per area:
- **PIPE** for the pump wing. PIPE2 in the hall, PIPEWAL2 in the corridor and the closet, and PIPES on machinery blocks (the pump plinths here and the pump housing in the south yard, so "pale pipes = pump" holds across the map).
- **SILVER** for the control tower: SILVER1 on the outside and in the lobby and stairs, SILVER2 (blue lamps) in the control room.
- **BROWN** variants for the plant's small buildings, one per building: BROWN96 for the start booth and the exit hall, which bookend the route; BROWNGRN, slime-stained, for the filter house; BROWN144, dark streaked, for the red-key closets and guardroom.

**Doors**: key doors keep BIGDOOR4 between DOORBLU/DOORRED tracks. Every other door, the gate included, is BIGDOOR2. BIGDOOR7, the wooden skull door, goes.

| Area (route spaces) | Walls | Trim | Flats (floor / ceiling) | Reason |
|---|---|---|---|---|
| Yard basin (yard_s, yard_n, yard_se, tstep, terrace, plat_se, niche_g, niche_gag, d_gate, d_secl_e) | BRICK6 on every wall; tstep/terrace and plat_se risers BRICK9; crates keep CRATE1 | SUPPORT3: gate jambs and recesses, switch niches (SW1BRN2 switches), ped_r | MFLR8_1 / SKY; terrace and tstep FLOOR5_1 (height change); plat_se FLOOR4_8 | base family; one space, so one material |
| Pump housing (housing) | lower PIPES | none | CEIL5_1 top / SKY | a pump: machinery reads as pipes |
| Canal (river_w, river_e, river_e_lip, culvert, all par_*, ledge) | BRICK9 on every quay and end wall, the parapets' lower faces, the culvert and the ledge | none needed (same family as the yards) | NUKAGE1 / SKY; parapet and ledge tops FLAT5_4 | base family, darker variant: the embankment below the coping |
| Canal ironwork (rail_w, rail_e, bridge, pier, lift_i, island, ped_s) | METAL, the gate's 128-high faces included | METAL is itself a border | bridge, pier, lift FLAT23; island FLAT5_4 / SKY | the set piece is a steel gate, and its rails, pier and island are one kit of ironwork |
| Start booth (start, window_s, d_start, d_sec1, sec1) | BROWN96 (sec1 panel BROWN96 with the hint offset) | SUPPORT3 recess on the start-room side of the north door | FLOOR4_8 / CEIL3_5 | a plant building: brown panels |
| Pump wing (corr1, corr2, d_pump, hall_s, hstep, hall_n, pump_s, pump_n, ped_b, isteps, intake, hall_cl, d_blue) | corridor PIPEWAL2; hall and intake PIPE2; pump plinths' lower faces PIPES; hall-edge lower faces NUKEDGE1; hall_cl PIPEWAL2 (face PIPE2) | SUPPORT3 at d_pump and both sides of d_blue (DOORBLU tracks, BIGDOOR4); hall risers (hstep, isteps) METAL; ped_b SUPPORT3 | corridor FLOOR0_3 / CEIL5_2; hall FLOOR5_2 / CEIL3_5; plinths FLOOR4_8; steps FLOOR0_3 | signature: the pump wing is pipes; the blue door is a key colour |
| Control tower (plinth, d_tower, lobby, tst_w, tst_e, control, window_t, window_e, d_pier) | outside (plinth) and lobby/stairs SILVER1; control room, windows and the seamless d_pier SILVER2; stair and plinth risers SILVER1 | SUPPORT2 at d_tower, around SW1COMP, and where the tower meets the parapets | FLAT4 / TLITE6_5; plinth FLOOR5_1 | signature: a steel landmark standing on the brick bank |
| Filter house (d_filt, filter, crate_f*, d_sec4, sec4) | BROWNGRN (sec4 panel BROWNGRN with the hint offset); crates keep CRATE2 | SUPPORT3 at d_filt | FLOOR7_1 / CEIL5_1 | signature: the slime-stained shed where the nukage is filtered |
| Red-key closets (guard, secl_e, secl_s) | BROWN144 inside; faces BRICK6, flush in the yard wall, as now | SUPPORT3 where BROWN144 meets the yard wall's plane at the guard door | floors as now (FLOOR5_1 guard, MFLR8_1 others) / CEIL5_1 | closets the red key opens all look alike: dark brown sheds |
| Exit hall (d_red, exit_hall, exit_niche) | BROWN96 | SUPPORT3 on the d_red recesses (DOORRED tracks, BIGDOOR4) and around the SW1EXIT niche | FLOOR0_1 / TLITE6_4 | bookends the start booth; the red door is a key colour |

### Change list

Grouped by sector. The `Now` column is what the module has; anything not listed stays.

| Sector(s) | Now | New |
|---|---|---|
| `OUT_S`, `OUT_N`, `OUT_E` constants | BRICK12, BROWN144, STONE3 | one `QUAY = "BRICK6"`; add `CANAL = "BRICK9"` |
| start, window_s, sec1, d_sec1, d_start far alcove | STARG3 | BROWN96; give d_start a near `alcove` in SUPPORT3 so BIGDOOR2 isn't set flush in the wall |
| housing lower | BROWNPIP | PIPES |
| d_pump alcove | BROWNPIP | SUPPORT3 |
| corr1, corr2 | BROWNPIP | PIPEWAL2 |
| pump_s, pump_n lower | METAL2 | PIPES |
| hstep, isteps risers | STEP4 | METAL |
| ped_b | PIPE2 | SUPPORT3 |
| culvert | BROWNPIP | BRICK9 |
| d_blue alcoves | SILVER2 | SUPPORT3 |
| river_w, river_e, river_e_lip walls | SILVER2 | BRICK9 |
| par_* lower | BRICK12 | BRICK9 (their wall attribute becomes QUAY) |
| bridge wall/lower | SUPPORT3 | METAL |
| ledge wall | SILVER2 | BRICK9 |
| island, ped_s, lift_i, pier walls | SILVER2 (pier lower SUPPORT3) | METAL |
| yard_n, crates_n wall, tstep, terrace | BROWN144 (risers STONE2) | BRICK6 (risers BRICK9) |
| plinth | SILVER2, lower STEP4 | SILVER1, lower SILVER1; SUPPORT2 trim lines where it meets par_nw and par_ne at (240,1424) and (688,1424) |
| d_tower alcoves | SILVER2 | SUPPORT2 |
| lobby, tst_w, tst_e | SILVER2, risers STEP4 | SILVER1, risers SILVER1 |
| control bridge switch | SW1COMP straight in SILVER2 | SW1COMP between SUPPORT2 trim lines (16 each side) |
| d_filt alcoves, filter, crate_f* wall, d_sec4, sec4 | BROWN96 | alcoves SUPPORT3; the rest BROWNGRN |
| guard | face BROWN144, walls STONE2 | face BRICK6, walls BROWN144 |
| d_red alcoves | STONE3 | SUPPORT3 |
| exit_hall | STONE3 | BROWN96 |
| exit_niche wall | EXITSTON | SUPPORT3 |
| yard_se, plat_se, ped_r | STONE3; plat_se lower METAL2 | BRICK6; plat_se lower BRICK9; ped_r SUPPORT3 |
| niche_gag | wall STONE3, SW1STON1 | wall SUPPORT3, SW1BRN2 |
| niche_g | wall METAL2, SW1MET2 | wall SUPPORT3, SW1BRN2 |
| d_gate | face BIGDOOR7, alcoves METAL2 | face BIGDOOR2, alcoves SUPPORT3 |
| d_secl_e, secl_s faces | STONE3 | BRICK6 |
| secl_e, secl_s walls | STONE2 | BROWN144 |

Each of the 21 seams the build lists now goes away: either both sides become one family (yard against yard, quay against yard, BROWNPIP against PIPE) or a trim sits between them (door recesses, the tower's SUPPORT2 corners, the switch frame).

## Secrets

Unchanged in place and reward. The retexture keeps one secret language: the panel is in its room's own material, with the `SECRET_HINT` offset.

| # | Where | Hint | Reward |
|---|---|---|---|
| 1 | sec1, west of the start booth | the BROWN96 panel is offset (16, 8) against the booth wall | green armor, shells |
| 2 | ledge, in the canal's north quay at (-128..64, 1344..1408), -72 | lit (208) against the canal's 160; seen from the south yard over the parapet | rocket launcher, rocket box |
| 3 | pier and island, through the tower's south wall | seamless SILVER2 panel; the hint is the pier and island in view from the tower window and the south yard | soulsphere, health bonuses |
| 4 | sec4, west of the filter house | the BROWNGRN panel is offset against the filter house wall | backpack, medikit |

## Targets

| Target (DOOM II median) | Plan | Where it comes from |
|---|---|---|
| most-used wall texture 0.2–0.45 [0.3] | **0.30 BRICK6**, projected from the current wall areas | every wall of the yard basin: yard_s, yard_n, yard_se, the terrace and closet faces |
| rule-2 seams with a border ≥ 0.5 [0.31] | **≥ 0.7**, no listed seams | SUPPORT3 at every brick or brown door and niche; SUPPORT2 in the tower; same-family joins quay to yard and corridor to hall |
| optional share ≥ 0.3 [0.5] | 0.33, unchanged | filter house, intake and ledge, pier and island, and the secret closets |
| distinct floor heights ≥ 15 [23] | 22, unchanged | canal -96, ledge -72, filter -24, hall -16/0/16, plinths and pedestals, terrace 20/40, tower stairs 16–96, bridge 128 |
| secrets ≥ 2 [4] | 4, unchanged | sec1, ledge, island, sec4 |
| light-effect sectors ≥ 3 [9] | 11, unchanged | blinking corridor and red-key closets, flickering filter house and pump closet, glowing exit hall |
| deaf share (UV) ≥ 0.2 [0.42] | 0.37, unchanged | pump hall, north bank and tower waiting monsters |

Outside this retexture: whole-map symmetry is 0.82, above id's 0.43–0.64, because the yards mirror each other across the canal. Fixing that would mean reshaping the map. The texture change doesn't move it, so record it rather than chase it here.

## Build risks

- **Recesses move walls.** A near `alcove` on d_start cuts 16 units into the start room's north wall at x 256–384. Check that the player starts and the shotgun at (288, 224) stay clear, and that the reveal through window_s is unchanged.
- **Trim wall lines need shared vertices.** The SUPPORT2 corners at the tower–parapet joins and the SW1COMP frame each split an existing line: add the vertices to both neighbouring outlines (see the shared-vertices gotcha), and give the trim in `OVERRIDES`.
- **Texture fit.** BRICK6 and BRICK9 are 64×128, METAL and SUPPORT3 64×128, PIPE2 256×128. Expect fit warnings on short walls: the 16-high hall risers in METAL, the 8-high plinth riser, and the 32-high parapet kerbs in BRICK9 seen from the yard. These are allowed if they're understood; check the parapets' lower faces still read as a brick kerb, not a sliver.
- **The bridge in METAL.** The gate sinks 128 to 0. Its faces are lower textures on the rails' and banks' sides, so check they're lower-unpegged and the rivets don't crawl while it moves (the playtest screenshot after the switch).
- **Seamless pier door.** d_pier must keep exactly the control room's texture and alignment (SILVER2, x-offset continuous along the wall), or the secret stops being seamless and the hint changes.
- **Don't regress the untouched measures.** No sector heights, lights, things or specials change. Compare the full measurement table and the reach check (`MUST_REACH`, secrets) with the baseline above. Any change outside the texture rows means a geometry edit went too far.

## As built

`levels/nukage_crossing.py` is authoritative; the first version is archived as `levels/nukage_crossing_original.py` (not built into the WAD). Departures from the plan above, each for a reason found in the build:

- **Culvert is METAL, not BRICK9.** It's the one wall plane shared by the pump wing (NUKEDGE1 risers, PIPE2) and the canal (BRICK9), so any material from either side left a seam. As a steel-lined culvert through the quay it reads as part of the canal's ironwork, and METAL is a border.
- **Start door: a SUPPORT3 jamb, not a near alcove.** The door sits in the start room's north-east corner, so only its west side was flush in the BROWN96 wall. A 16-unit wall line at (240-256, 416) in SUPPORT3 frames it without moving the room. The far side keeps its alcove, now SUPPORT3.
- **Pedestals** (ped_b, ped_r, ped_s) keep the `pedestal()` helper's METAL sides, which are already a border, rather than SUPPORT3.
- **The tower's south face over the canal** would have taken the canal's BRICK9 (it is the river sector's wall). It's SILVER1 by `OVERRIDES`, with SUPPORT2 corner lines at x 240-256 and 672-688 where it meets the parapets' brick, and SILVER1 above window_t; the window sills are SILVER1 too. The parapets' 16-unit ends against the plinth are SUPPORT2.
- **Bridge switch** has SUPPORT2 jambs on both sides. The south one needed window_e shortened from 64 to 48 (y 1440-1488).
- **Red-key closets** are wider than their doors, so inside, the door's QUAY back face met BROWN144: the 32- and 56-unit wall lines either side of each door are SUPPORT3.
- **Plain doors** keep the builder's DOORTRAK tracks, and the island lift keeps PLAT1 sides; both are border textures.
- **Measured** (build table, DOOM II median in brackets): most-used wall texture 0.28 BRICK6 [0.3], rule-2 seams with a border 0.81 [0.31] with no unbordered seams listed, 23 wall textures (was 27). Everything else is unchanged from the baseline: 22 floor heights, 4 secrets, 11 light-effect sectors, deaf share 0.37, optional share 0.33, symmetry 0.82. The remaining rule-1 slips are the d_blue and d_pier door thresholds, as before.
- **Playtest** (`levels/playtests/nukage_crossing.playtest`; `nukage_crossing_original.playtest` runs the same route and shots on the archived map for comparison). Wiring passes on both, 19 checks, 0 fails. The fight runs (UV, seeds 1-3) match the original's: seed 2 is identical (21 deaths, 55 kills), seed 3 has the same four fails (the bot was warped past the start door and the canal wade after loops), and seed 1 diverges (43 deaths against 22) as the bot's path drifts. The deaths are bot problems, not the retexture: most are `starved` where the static curve's lowest detour ratio is 1.46 (no leg short), so the bot wasted ammo, and `hazard` deaths wading the canal to the ledge secret.
- **Fixes from playing it in dsda-doom:**
  - **Canal walls are BRICK6 at the yards' light (192), not BRICK9 at 160.** Above the parapet the canal's end and side walls continue the yards' walls, and the darker brick in dimmer light read as a different material at every corner. BRICK9 stays on the parapets' kerbs and the risers. The secret ledge is now lit 240, so it still stands out against the brighter canal. Most-used wall texture becomes 0.31 BRICK6.
  - **Window jambs** hang from the lintel, so their texture bands didn't line up with the wall beside them: their y offsets now make up the difference (24 for the start window, 32 for the tower's). The tower's jambs are plain SILVER1, because a 16-wide slice of SILVER2 showed a random strip of its lamps that differed from one side of the window to the other. The sills are in the wall's own material on each side.
  - **Raised doorways** (start, pump wing, blue door, red door): the step up into the recess showed the recess's SUPPORT3 below the door, standing out from the brick wall. These risers are now BRICK9, like the terrace's.
  - **One material per run of wall** (second round of play feedback). The pump wing's corridor and closet are PIPE2 like the hall, not PIPEWAL2, so the pump-wing door no longer shows SUPPORT3, PIPEWAL2 and PIPE2 within 200 units. The south yard's pump housing is a 64-high crate (CRATOP1/CRATE1) matching the north bank's crates. The canal reads as one brick basin: the parapets' canal faces and the gate rails are BRICK6, not BRICK9 and METAL; only the sluice gate itself stays METAL. The pier, island, island lift and soulsphere pedestal are SILVER1, as part of the tower they're reached from, instead of a METAL/PLAT1 kit beside the silver tower.
  - **Measured after these fixes:** most-used wall texture 0.42 BRICK6, above the 0.25–0.35 planned but inside id's range (0.2–0.45): the basin is one continuous brick space, which is what the playtest asked for. Rule-2 border share 0.74. 21 distinct floor heights (the housing dropped from 72 to the crates' 64). Wiring run still 19 checks, 0 fails.
  - **Third round of play feedback.** Pump wing: the intake steps and pipe corridor take the hall's FLOOR5_2, the hall's raised edges are METAL like the intake risers, and the blue door's hall-side recess is PIPE2. The south-yard crate is a square 64×64. The gate door is BIGDOOR4 like the other doors set in brick. The raised doorways' step risers are BRICK6, pegged with the wall so the bricks line up. The tower's plinth strip is the yard's MFLR8_1; the island and its pedestal top are the pier's FLAT23. The pier side of the secret pier door is SILVER1 (the door shows SILVER2 only into the control room). Control tower: one light level (176) through lobby, stairs and control room; plain SILVER1 everywhere except the control room's south wall, which keeps SILVER2's lamps and carries them above and below the window, pegged to the ceiling so they line up with the wall on both sides. Rule-2 border share 0.9; wiring run 19 checks, 0 fails.
