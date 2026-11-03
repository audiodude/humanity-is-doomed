# Nukage Drain (MAP06, NUKAGE.WAD): retexture

## Concept

**A flooded open-air reservoir with the exit vault standing in the middle. You pump it dry one pump house at a time, and each pump raises the next walkway out of the nukage.**

- Theme: the plant's nukage reservoir. Its retaining walls enclose a square pool; walkways run round it under the sludge, and a causeway leads to the pillar in the middle that holds the vault. A pump house opens off the west, north and east sides, and each one looks back over the reservoir through an opening beside its pump switch.
- Difficulty: medium, the set's sixth map, the first lost souls. Slot: `MAP06` of `NUKAGE.WAD`, module `levels/nukage_drain.py`.
- **Scope: retexture, and remove floor height changes that do nothing.** The shape, route, lights, things and specials stay as built; geometry moves only where a texture needs it (a door recess, a room raised to a texture's height) or where a step had no job (`doom-build`, Gotchas: Floor heights).

Baseline (the module before this change; DOOM II median in brackets):

| Measure | Before | Target |
|---|---|---|
| most-used wall texture | 0.29 NUKEPOIS [0.3] | 0.25–0.40 |
| rule-2 seams with a border | 0.61 [0.31]; 7 unbordered seams listed | ≥ 0.7, none listed |
| distinct floor heights | 13 [23] | no padding; record the miss |

What the walls were: the reservoir in NUKEPOIS, its poison sign repeated every 128 units round the whole pool; each pump house split between two families (west BROWNPIP corridor and PIPE2 hall, east STONE2 boiler hall and METAL1 pump room); the three switch booths, the door recesses and the ledges in SUPPORT2 grey girders inside brown and green rooms; the start booth the map's only STARG3; the exit niche EXITSTON in a SILVER3 vault; the yellow door a wooden skull door (BIGDOOR7) in a steel plant.

Other maps in the set and their base families, so Drain's differs:

| Map | Shape | Base family |
|---|---|---|
| MAP01 Outskirts | climb a hillside to a station over a nukage spill | ROCK5 / ASHWALL4 |
| MAP02 Crossing | loop round a canal and sink a sluice gate to cross it | BRICK6 |
| MAP03 Divided | two wings that never meet (lava and screens) | STONE3 |
| MAP04 Tower | climb three galleries round a reactor core | BRONZE2 |
| MAP05 Undercurrent | one hall crossed over, then under | STARGR |
| MAP06 Drain | pump a flooded reservoir dry, walkways surface | **NUKEDGE1** |
| MAP07 Storage | cask maze that sinks into an arena | CEMENT6 |
| MAP08 Lockdown | loop away from an exit you can see, closed by wading | STARG3 |
| MAP09 Meltdown | descent down terraced nukage falls | CEMENT6 |

## Palettes considered

The shape is fixed, so the open choice is the palette, not the concept (step 2 of `doom-design` does not apply).

1. **Stained retaining walls, steel pillar, one family per pump house (chosen).** NUKEDGE1 is NUKEPOIS without the sign: the same nukage-stained concrete, with the green slime line along its foot, so the reservoir keeps its look without a poison sign every 128 units. The pillar keeps its SILVER3 instrument panels and stands out against the brown as the landmark. Each pump house gets one family through all its rooms. SUPPORT3, the dark girder, is the trim and the structure: walkway sides, booths, ledges, recesses.
2. **Keep NUKEPOIS on the reservoir, fix only the seams.** Least change, but the repeated sign is the loudest thing in the map and says nothing about any one place.
3. **Grey concrete basin (GRAY/CEMENT) with silver pillar.** Clean, but the pillar's grey panels disappear against grey walls, and CEMENT6 is MAP07's and MAP09's base.

## Height changes

Every floor change that's left has a job:

| Change | Kept or removed | Why |
|---|---|---|
| catwalk 32 → steps 8 → nukage -16 | kept | the steps into the flood and back out |
| walkways -16 → 32 | kept | the pumps' set piece |
| secret ledge 8 | kept | a ledge you wade round to find |
| door sills at 32 → building floors at 40 (start booth, pump houses, vault) | kept | the step into each building is where the floor flat changes (rule 1); doors are level with the walkway outside |
| switch booths 48 | kept | the booth's FLAT23 floor is what each pump copies onto its walkway (`S1_RAISE_CHANGE`), so the booth floor has to differ from the room's, and rule 1 puts a step there |
| pedestals 56, gallery stairs to 104, revenant ledge 136, balcony stairs to 120 | kept | pedestals, a gallery to fight from, the revenant's ledge, the balcony |
| north lobby 16 between a 32 door and a 24 sill up to the hall at 40 | **removed**: lobby, its secret and the hall door all at 40 | a dip and climb between two rooms of one house |
| east pump-room door sill 48 between two rooms at 40 | **removed**: sill at 40 | a bump between two rooms of one house |
| vault 48, a step above its own entrance hall at 40 | **removed**: one floor at 40 | the hall and vault are one room |
| east walkway 32 → causeway 40 → vault door 40 | **removed**: the vault door sill is at 32, so the causeway rises level with the walkways; the step is inside the vault door, like every other building | a step onto one walkway from another |

## Route

Unchanged. Heights are floor/ceiling; SKY is a 384 sky ceiling.

1. **Start booth** (start, 384×256). 40/168, light 160. Open onto the catwalk, one step down. Visible: the reservoir, the pillar, the walkways' girder sides under the sludge, the pump-house doors. Shotgun, clip.
2. **South catwalk** (cw_s, 1600×160; steps ex_w, ex_e down into the nukage). 32/SKY, light 192. Leaving it: the west pump-house door (the walkways are under the sludge). Off it: the suit locker (d_suit, suit 128×96, radiation suit).
   - **Wading** (res, -16): optional with the suit: chaingun, berserk, rockets, soulsphere, armor bonuses round the pillar, and the secret ledge on the pillar's north face.
3. **West pump house**: corridor (w_corr 384×160, 40/168, light 96 blinking; secret w_sec), arch, pump hall (w_pump 576×672 with two pillars, 40/232; super shotgun on a pedestal; gallery w_gal 104 up three steps; closets wcl1, wcl2). Taking the super shotgun opens the closets. Stepping into the booth (niche_w) opens the pillar's west closet; the switch raises the west walkway (ww). Visible through the window: the walkway rising, the pillar's closet letting out cacodemons.
4. **West walkway** (ww 32 once raised) north to the north pump-house door.
5. **North pump house**: lobby (n_lobby 352×240, 40/168, light 128 flickering; secret n_sec), hall door, hall (n_hall 960×576, 40/296, two pillars; revenant on n_ledge 136; yellow key on ped_y 56; closets ncl1, ncl2). The key opens the closets; the booth (niche_n) opens the pillar's north closet; the switch raises the north walkway (wn).
6. **North walkway** (wn 32) east to the yellow door.
7. **East pump house**: boiler hall (e_hall, 40/256, two pillars; stairs to balcony e_balc 120; secret e_sec; rocket launcher), pump room door, pump room (e_pump 512×320, 40/208). The booth (niche_e) opens the pillar's east closet; the switch raises the east walkway (we) and the causeway (wc).
8. **East walkway** (we 32) back south to the catwalk, closing the loop. Stepping onto the causeway (we → wc) opens two closets (amb1, amb2) in the walkway's outer wall behind you.
9. **Causeway and vault** (wc 32; d_vault sill 32; v_hall and vault 40/160 and 40/208, glowing). The exit switch is in a niche in the vault's west wall (64).

## Sketch

Generated from the module's sectors. One character is 64 units; rows are labelled with the y of their bottom edge. Column 0 is x = -1600, so x = 0 is column 25.

```
     y |0         1         2         3         4    (column)
  2240 |                  TTTTTTTTTTTTTTT                <- revenant ledge 136 along the north wall
  2176 |                  TTTTTTTTTTTTTTTkkk             <- ncl2
  2112 |                  TTTTTTTTTTTTTTTkkk
  2048 |                  TTTTTTTTTTTTTTTkkk      $$     <- e_sec
  1984 |                  TT TTTTTTTT  TT         $$     <- yellow key 56 between the pillars
  1920 |           TTTTTT TT TTTTTTTT  TTkkk       +     <- ncl1
  1856 |         $$TTTTTT+TTTTTTTTTTTTTTTkkk  MMMMMMMMM  <- n_sec, lobby 40, hall door, hall 40; balcony 120
  1792 |         $$TTTTTT+TTTTTTTTTTb TTT     MMMMMMMMM  <- north booth (b)
  1728 |           TTTTTT TTTTTTTTTTb TTT     MMM  MMMM  <- e_st stairs 56-104
  1664 |             ++          PPP          MMM  M  M  <- north door (-720,1696); north window (0-192)
  1600 |            WWWNNNNNNNNNNNNNNNNNNNNNN+MMMMMMMMM  <- yellow door (800,1616); boiler hall 40
  1536 |            WWWNNNNNNNNNNNNNNNNNNNNNN+MMMMMMMMM  <- north walkway (N)
  1472 |            WWW~~~~~~~~~~~~~~~~~~~~EE    ++      <- pump-room door (1120,1520)
  1408 |            WWW~~~~~~~~~~~~~~~~~~~~EE bbMMMMMM   <- east booth; pump room 40
  1344 |            WWW~~~~~~~~~~~~~~~~~~~~EEP  MMMMMM   <- east window (800-864)
  1280 |            WWW~~~~~~~~~~~~~~~~~~~~EEPMMM MM M
  1216 |            WWW~~~~~~~$$~~~~~~~~~~~EE MMM MM M   <- secret ledge 8 on the pillar's north face
  1152 |   PPPPPPPPPWWW~~~~~     xxxx~~~~~~EE MMMMMMMM   <- pillar closets (x): north, east
  1088 |   PPPPPPPPPWWW~~~~~xx VVVV x~~~~~~EE            <- gallery 104 (west), west window (-832..-800)
  1024 |kkkPPPPPPPPPWWW~~~~~xx VVVVVV======EE+kk         <- vault 40, exit niche 64; causeway (=) 32
   960 |kkkPP PPPPbbWWW~~~~~   VVVVVV======EE+kk         <- west booth (b); amb2
   896 |   PPPPPPP  WWW~~~~~   VVVV  ~~~~~~EE            <- super shotgun 56
   832 |   PPPPPPPPPWWW~~~~~         ~~~~~~EE
   768 |kkkPPPPPPPPPWWW~~~~~~~~~~~~~~~~~~~~EE            <- wcl1, wcl2 (k)
   704 |kkkPP PPPPPPWWW~~~~~~~~~~~~~~~~~~~~EE+kk         <- amb1
   640 |   PPPPPPPPPWWW~~~~~~~~~~~~~~~~~~~~EE+kk
   576 |   PPPPPPPPPWWW~~~~~~~~~~~~~~~~~~~~EE            <- west pump hall 40 (P); reservoir -16 (~)
   512 |   PPPPPPPPPWWW~~~~~~~~~~~~~~~~~~~~EE            <- west walkway (W), east walkway (E)
   448 |      PPPPPPccccccccccccccccccccccccc            <- west door (-800,432); corridor 40
   384 |      PPPPPPccccccccccccccccccccccccc            <- south catwalk 32 (c)
   320 |      PPPPPPccccccccccccccccccccccccc            <- suit door (-560,352)
   256 |        $$     rr     SSSSSS                     <- w_sec, suit locker (r), start booth 40 (S)
   192 |        $$     rr     SSSSSS
```

Legend: `S` start booth (start at (0,256), facing north); `c` south catwalk and its steps; `r` suit locker; `~` reservoir; `W`/`N`/`E` the west, north and east walkways, `=` the causeway (all -16, raised to 32 by the pumps); `V` vault, its hall and exit niche; `x` pillar closets; `P` west pump house; `T` north pump house; `M` east pump house; `b` pump booths; `k` monster closets; `+` doors; `$` secrets.

## Materials

**Base family: NUKEDGE.** Every retaining wall of the reservoir is **NUKEDGE1**: the catwalk, all three walkways, their outer walls round the corner, the sills below the pump-house windows, the step and lintel of the start booth's opening, and the walls of the causeway closets in the east walkway, whose doors are the same wall. It's one continuous space, so one material; its sides are told apart by what's on them (the start booth, the three doors, the windows, the pillar), and its light (176-192). Measured: **0.30** of wall area.

**Trim set: SUPPORT3**, the dark girder: the sides of every walkway, the catwalk and its steps (the structure the pumps raise), every door recess, the window jambs, the three switch booths, the west gallery and its stair risers, the revenant's ledge, the balcony and its stair risers. **SUPPORT2**, the grey girder, belongs to the pillar: the vault door's recess and the exit niche.

**Signature families**, one per area:
- **SILVER** for the pillar and the operations rooms: SILVER3 instrument panels on the pillar, inside the vault and its hall, on the pillar closets (hidden in the panelling), and in the start booth, which looks out at the pillar it belongs with. SILVER1 plain steel for the suit locker.
- **PIPE2** for the west pump house: corridor, arch, hall, secret, closets; the pedestal stands in it.
- **TEKGREN** for the north pump house: TEKGREN5 in the lobby and its secret (the lobby is 128 tall, so the lamp strip runs under its ceiling), TEKGREN2 in the hall, on the ledge wall and in the closets.
- **METAL2** for the east pump house: riveted plate in the boiler hall, its secret and the pump room.

**Doors**: every door is BIGDOOR2 on DOORTRAK, recessed in SUPPORT3. The yellow door is BIGDOOR2 too, with DOORYEL tracks and DOORYEL2 skull columns lining both its recesses. Switches match the house: SW1BRNGN (green-stained brown) west, SW1TEK north, SW1MET2 east.

| Area (route spaces) | Walls | Trim | Flats (floor / ceiling) | Reason |
|---|---|---|---|---|
| Reservoir (cw_s, ex_w, ex_e, ww, wn, we, res) | NUKEDGE1 | SUPPORT3 walkway and catwalk sides; SUPPORT3 door recesses; window sills NUKEDGE1 | FLAT23 / SKY; NUKAGE1 | base family; one space, one material |
| Causeway (wc) | its ends on the pillar SILVER3 | SUPPORT3 sides | FLAT23 (once raised) / SKY | it meets the pillar, not the retaining wall |
| Causeway closets (d_amb1, amb1, d_amb2, amb2) | NUKEDGE1, doors NUKEDGE1 | none: hidden in the wall | FLAT23 / CEIL5_1 | closets in the retaining wall, disguised as it |
| Start booth (start) | SILVER3; step and lintel over the opening NUKEDGE1 | none | FLOOR0_6 / CEIL3_5 | signature: operations, facing the pillar |
| Suit locker (d_suit, suit) | SILVER1 | SUPPORT3 recess | FLAT23 / CEIL5_1 | operations family, plain steel locker |
| Pillar and vault (d_vault, v_hall, vault, exit_niche, v_ledge, v_ledge_back, c_dw, cl_w, c_dn, cl_n, c_de, cl_e) | SILVER3, closet doors SILVER3, ledge face SILVER3 | SUPPORT2 vault recess and exit niche | vault and hall FLOOR0_1 / CEIL5_1, TLITE6_4; closets FLAT23; ledge FLAT5_4 | signature: the landmark; the closets and the ledge hide in it, the ledge's light is its clue |
| West pump house (d_west, w_corr, d_ws, w_sec, w_arch, w_pump, ped_ssg, wgst1-3, w_gal, w_wwin, niche_w, d_wcl1, wcl1, d_wcl2, wcl2) | PIPE2; booth SUPPORT3 with SW1BRNGN | SUPPORT3 recess, jambs, booth, gallery and risers; pedestal METAL | FLOOR3_3 / CEIL5_2; booth FLAT23 | signature: pumps are pipes |
| North pump house (d_north, n_lobby, d_ns, n_sec, d_nhall, n_hall, n_ledge, ped_y, w_nwin, niche_n, d_ncl1, ncl1, d_ncl2, ncl2) | lobby and secret TEKGREN5; hall, ledge and closets TEKGREN2; booth SUPPORT3 with SW1TEK | SUPPORT3 recesses, jambs, booth, ledge face; pedestal METAL | FLOOR0_3 / CEIL5_1; booth FLAT23 | signature: the pump controls |
| East pump house (d_east, e_hall, e_st1-4, e_balc, d_es, e_sec, d_epump, e_pump, w_ewin, niche_e) | METAL2; booth SUPPORT3 with SW1MET2 | DOORYEL2 yellow-door recesses; SUPPORT3 pump-room recesses, jambs, booth, balcony and risers | FLOOR4_8 / CEIL5_1; booth FLAT23 | signature: riveted boiler iron; the yellow door in its key colour |

### Change list

| Sector(s) | Before | After |
|---|---|---|
| `OUT` constant (reservoir walls, causeway closets) | NUKEPOIS | `BASE = "NUKEDGE1"` |
| wc walls | NUKEPOIS | SILVER3 (its walls are the pillar's) |
| start | 48 floor, STARG3, FLOOR4_8 | 40, SILVER3, FLOOR0_6; riser and lintel on the catwalk side NUKEDGE1 |
| suit | SUPPORT3 | SILVER1 |
| all door recesses | NUKEPOIS, SILVER3, SUPPORT2 | SUPPORT3 (SUPPORT2 at the vault, DOORYEL2 at the yellow door) |
| d_west | 16 recess outside, door flush in the corridor's wall | 8 recess, 8-thick door, 16 recess inside (same 32-unit wall) |
| d_east | BIGDOOR7 | BIGDOOR2, DOORYEL tracks, DOORYEL2 recesses |
| switch booths | SUPPORT2; SW1BRN2, SW1TEK, SW1METAL | SUPPORT3; SW1BRNGN, SW1TEK, SW1MET2 |
| exit niche | EXITSTON, floor 72 | SUPPORT2, floor 64 (24 above the vault, as before) |
| vault, v_hall | vault 48, hall FLAT23 | both 40, FLOOR0_1; hall ceiling 160 |
| d_vault | sill 40, recess SILVER3 | sill 32, recess SUPPORT2 |
| v_ledge | METAL face | SILVER3 face |
| w_corr, w_arch, w_sec, closets | BROWNPIP, corridor 112 tall | PIPE2, corridor and arch 128 tall |
| windows | house wall, sill in the house wall | SUPPORT3 jambs, NUKEDGE1 sill |
| n_lobby, n_sec, d_ns, d_nhall | floors 16 / 16 / 16 / 24, TEKGREN1, FLOOR5_2, lobby 112 tall | all 40, TEKGREN5, FLOOR0_3, lobby 128 tall |
| ncl1, ncl2 | TEKGREN1 inside | TEKGREN2 |
| e_hall, e_st, e_balc, e_sec | STONE2, FLOOR5_1 | METAL2, FLOOR4_8; risers and balcony face SUPPORT3 |
| e_pump, d_epump | METAL1, FLOOR0_2, CEIL5_2; sill 48 | METAL2, FLOOR4_8, CEIL5_1; sill 40 |
| w_gal, wgst, n_ledge | SUPPORT2 faces | SUPPORT3 |

Each of the seven seams the build listed goes away: the causeway and reservoir seams at the pillar because the causeway's walls are now the pillar's; the start booth's because its riser is the catwalk's wall; the north and east windows' because their sills are; the vault's because the exit niche is framed in SUPPORT2; the west door's because it's recessed into the corridor in SUPPORT3.

## Secrets

Unchanged in place and reward. Each panel is in its room's own material, with the default `SECRET_HINT` offset.

| # | Where | Hint | Reward |
|---|---|---|---|
| 1 | w_sec, south wall of the west corridor | the PIPE2 panel is offset | green armor, stimpack |
| 2 | v_ledge, the pillar's north face, reached by wading | a brightly lit ledge in the pillar's panelling, out of sight until you wade round it | blue armor, rockets |
| 3 | n_sec, west wall of the north lobby | the TEKGREN5 panel is offset | shells, medikit |
| 4 | e_sec, north wall of the boiler hall | the METAL2 panel is offset | backpack, shells |

## Targets

| Target (DOOM II median) | Measured | Where it comes from |
|---|---|---|
| most-used wall texture 0.2–0.45 [0.3] | **0.30 NUKEDGE1** | every retaining wall of the reservoir |
| rule-2 seams with a border ≥ 0.5 [0.31] | **1.0, none listed** | SUPPORT3 recesses and jambs, the pillar's own walls on the causeway, NUKEDGE1 sills and risers, SUPPORT2 round the exit switch |
| rule-1 slips | 0 | building floors change flat at their step; booths at theirs |
| optional share ≥ 0.3 [0.5] | 0.36, unchanged | wading round the reservoir, the suit locker, the west gallery, the balcony, the secrets |
| distinct floor heights ≥ 15 [23] | **12, missed** (was 13) | nukage -16, steps 8, walkways 32, buildings 40, booths 48, pedestals and stairs 56-104, the exit niche 64, balcony 120, ledge 136. The reservoir is one flat pool and the pump houses are single-floor buildings; the two heights removed (the north lobby's dip) were pointless steps, so the miss stays rather than be padded |
| secrets ≥ 2 [4] | 4, unchanged | w_sec, v_ledge, n_sec, e_sec |
| light-effect sectors ≥ 3 [9] | 9, unchanged | blinking west corridor and north closets, flickering north lobby and west closets, glowing vault and pedestals |
| deaf share (UV) ≥ 0.2 [0.42] | 0.41, unchanged | waiting monsters in the pump houses and out on the walkways |

## Build risks

- **Raised walkways.** `S1_RAISE_CHANGE` stops at the next higher neighbouring floor. The causeway's highest neighbour was the vault door sill at 40; it's now 32, so the causeway comes up level with the walkways. The pump-house windows are at 40, so no walkway rises past 32. The playtest checks both.
- **The booth flat.** The pumps copy the booth's floor flat onto the walkways, so the booths stay FLAT23 and a step up.
- **The west door moves.** Its recesses and an 8-thick door fit the same 32-unit wall, so the corridor and catwalk don't move.
- **Texture fit.** PIPE2 and TEKGREN5 are 128 tall: the west corridor and the north lobby are raised to 128 so neither is cut off. The 64-wide booths need 64-wide switches (SW1PIPE is 128 and is refused by the build).
- **Don't regress the untouched measures.** Lights, things and specials don't change; compare the measurement table and the resource curve with the baseline.

## As built

- **Measured** (build table, DOOM II median in brackets): most-used wall texture 0.30 NUKEDGE1 [0.3], rule-2 seams with a border 1.0 [0.31] with none listed, rule-1 slips 0, 12 floor heights [23]. Lights, secrets, deaf share, optional share, symmetry and the resource curve are identical to the baseline.
- **The resource curve's one warning is the baseline's**: the first leg (start to the west pump) is 450 short even taking everything, with a detour ratio of 0.87; this change moves no item or monster.
- **Playtest** (`levels/playtests/nukage_drain.playtest`): material shots added (`west-corridor`, `west-pump`, `north-lobby`, `north-hall`, `yellow-door`, `east-hall`, `east-pump`, `causeway`), joining `start`, `pump1`, `pump3` and `vault`; the causeway now rises to 32. Wiring passes, 30 checks, 0 fails.
- **Look**: the shots up to `pump1` are tinted green by the radiation suit, so the materials were also checked untinted with a throwaway route that skips the suit. Each pump house reads as one place; the trim shows at every door, window and booth.
- **Fight runs** (UV, seeds 1-3), against the baseline map on the same seeds:

  | Seed | Retextured: deaths (labels), kills, skipped | Baseline: deaths (labels), kills, skipped |
  |---|---|---|
  | 1 | 53 (33 hazard, 15 starved, 4 combat, 1 stuck), 56, 10 | 44 (29 hazard, 12 starved, 2 combat, 1 stuck), 55, 6 |
  | 2 | 48 (30 hazard, 14 starved, 4 combat), 53, 5 | 26 (10 hazard, 14 starved, 1 combat, 1 unseen), 57, 7 |
  | 3 | 54 (49 hazard, 2 starved, 3 combat), 48, 2; hit the 15-minute cap | 23 (5 hazard, 6 starved, 10 combat, 1 unseen, 1 stuck), 53, 3 |

  - `hazard`: the bot knocked off a walkway into the nukage while fighting, then standing in it. Seed 3 fell off the north walkway at the yellow door and spent the rest of the run in the nukage 40 units west of the catwalk's steps, dying every 18 s, too slowly for the loop check to warp it on. No walkway, edge or step in the reservoir changed, so these are the bot's known weak spot; seeds 1 and 2 cover the whole route.
  - `starved`: on the first leg and on the way to the yellow door. The curve's lowest detour ratio is 0.87 on the first leg, unchanged from the baseline, whose runs starve about as often (12, 14 and 6 deaths).
  - The `expect has YellowCard` fail (seeds 1 and 2, and baseline seed 3) follows a loop skip on the walk to the key; the yellow-door fail (seed 3, and a loop at the same door on baseline seed 3) came mid-fight. The wiring run takes the key and opens the door every time.
