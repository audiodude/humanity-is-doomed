# Nukage Core (MAP03, NUKAGE.WAD): retexture

## Concept

**A reactor core stands in a nukage moat in an open-air atrium. You see its crown from the start window, then climb three galleries round it to reach the exit on top.**

- Theme: the plant's reactor atrium. Galleries at three heights line the atrium's west, north and east walls, the core stands in the moat in the middle, and a wing opens off each gallery: the pump room and tank room (west), the storage room and turbine hall (north), the control room (east). The start booth and a filter house open off the terrace on the south side.
- Difficulty: medium, the set's third map, the first mancubus. Slot: `MAP03` of `NUKAGE.WAD`, module `levels/nukage_core.py`.
- **Scope: retexture only.** The shape, route, heights, lights, things and specials stay as built. Like MAP02 before its retexture, this map came before the texture research and its walls are a collage: 31 wall textures, and the one open atrium takes a different material on each side (`TEKWALL4` south, `BROWNGRN` west, `BRONZE2` north, `SILVER3` east), so the gallery you're on changes material at each corner. The two stair towers are `STONE2` and `STONE3`, the base families of MAP04 and MAP05. Geometry changes are limited to what the trim needs.

Baseline (`python3 -c "import levels.nukage_core_original as m; from levels import build; build(m, out='/tmp/ncore_original.wad')"`, DOOM II median in brackets):

| Measure | Now | Target |
|---|---|---|
| most-used wall texture | 0.13 TEKBRON1 [0.3], **below id's range** | 0.25–0.40 |
| rule-2 seams with a border | 0.80 [0.31]; 9 unbordered seams listed | ≥ 0.7, none listed |
| distinct wall textures | 31 | about 25 |

The other maps in the set and their base families. MAP03 takes **BRONZE**, which no other map uses.

| Map | Shape | Base family |
|---|---|---|
| MAP01 Outskirts | climb a hillside to a station whose deck looks over a nukage spill | ROCK5 / ASHWALL4 |
| MAP02 Crossing | loop round a canal and sink a sluice gate to cross it | BRICK6 |
| MAP04 Divided | two wings that never meet (lava and screens) | STONE3 |
| MAP05 Drain | pump a flooded reservoir dry, walkways surface | STONE2 / TEKGREN |
| MAP06 Undercurrent | one hall crossed over, then under | STARGR |
| MAP07 Storage | cask maze that sinks into an arena | CEMENT6 |
| MAP08 Lockdown | loop away from an exit you can see, closed by wading | STARG3 |
| MAP09 Meltdown | descent down terraced nukage falls | CEMENT6 |

## Palettes considered

The shape is fixed, so the open choice is the palette, not the concept (step 2 of `doom-design` does not apply).

1. **Bronze cladding with a green reactor (chosen).** BRONZE2 on every atrium wall and through both stair towers, so the climb round the core is one place at every height. The core keeps its green TEKGREN panels and stands out against the bronze as the landmark it is. The turbine hall's TEKBRON1 is bronze machinery, so the biggest wing belongs to the same plant. SUPPORT3, the bronze girder, is the natural trim. BRONZE is free in the set, and BIGDOOR4 is a bronze door.
2. **SILVER/grey steel throughout** (SILVER1 atrium, SUPPORT2 trim). A clean reactor hall, but grey walls round a grey-green core flatten the landmark, and it would sit next to MAP02's silver tower.
3. **METAL2–7 dark riveted plate.** Industrial and free in the set, but very dark at the atrium's 176–216 light, and METAL is the border texture the trim relies on elsewhere.

## Route

The route is unchanged. Heights are floor/ceiling; SKY is a 448 sky ceiling.

1. **Start booth** (start, 512×288). 0/128, light 160. Leaving it: the door north-east. Visible through the window: the terrace, the moat, the core with its crown, and the secret ledge on the core's south face. Pickups as built.
2. **Terrace** (terrace, 1152×192, parapets 32, steps down into the moat). 0/SKY, light 192. Leaving it: the pump-room door west (the lift east stays shut). Visible: the whole atrium, the galleries rising round it, the core.
   - **Filter house** (filt, 672×480, sludge beds -16, crates 64; secret closet sec5): optional, off the terrace. Light 144, flickering.
   - **Moat and ledge** (moat -48, lift_core to the ledge at 96): secret. The ledge and its lift are faced in the core's TEKGREN2, so from the moat they're part of the core.
3. **Pump room** (wcorr, pumps, 576×448 with two pillars; secret closet sec1; stairs pst 16→48; landing pland 48). 0/112, light 104 flickering. Leaving it: the stairs up onto the west gallery.
4. **West gallery** (gal_w 48, pier 40). Light 176. Leaving it: the tank-room door, then the blue door. Visible: the core across the moat, the terrace below.
5. **Tank room** (tank, 592×448, four nukage pools, blue key on a pedestal). 48/256, light 208. Taking the key blacks the room out and opens two closets (tcl_w, tcl_s).
6. **North-west stair tower** (nw_low 48, nwst 72–144, nw_top 144). Light 112–144, blinking at the bottom. Leaving it: open onto the north gallery.
   - **Storage** (store 144/320, crate stack to 216): optional, off the tower.
7. **North gallery** (gal_n 144). Light 200. Leaving it: the turbine-hall door, then the yellow door.
8. **Turbine hall** (turb 144/400, two METAL turbine housings, dais 168, yellow key 184; pens behind pwall_w and pwall_e; secret closet sec3). Light 160. Taking the key drops the pen walls.
9. **North-east stair tower** (ne_low 144, nest 168–240, ne_top 240; secret closet sec4). Light 128–160. Leaving it: open onto the east gallery.
10. **East gallery** (gal_e 240). Light 216. Leaving it: the control-room door.
11. **Control room** (ctrl 240/368). Light 224. The switch beside the window raises the causeway shutter and the shutter at the lift down to the terrace.
12. **Causeway and core** (causeway 256, core 272). Stepping onto the core opens the crown's hatch.
13. **Crown** (crown 280/400, glowing). The exit switch is in a niche on its west wall.

## Sketch

Unchanged layout except the control-room door (below), generated from the module's sectors. One character is 64 units; rows are labelled with their top y. Column 0 is x = -1584, so x = 0 is column 25.

```
     y |0         1         2         3         4    (column)
  2864 |             $$$UUUUUUUUyUUUUUUUU           <- yellow key 184 on the dais (y)
  2800 |             $$$UUUUUUUUUUUUUUUUU           <- sec3 closet ($)
  2736 |                UUUUUUUUUUUUUUUUU
  2672 |             UUUUUUUUUUUUUUUUUUUU           <- pens behind dropping walls (x -768 and 768)
  2608 |   KKKKKKKKK UUUUUUUUUUUUUUUUUUUU
  2544 |   KKKKKKKKK UUUUUUUUUUUUUUUUUUUUUUUU       <- turbine hall 144/400 (U)
  2480 |   KKKKKKKKK UUUUUUUUUUUUUUUUUUUUUUUU
  2416 |   KKKKKKKKK UUUUUUUUUUUUUUUUUUUUUUUU       <- storage 144, crate stack to 216 (K)
  2352 |   KKKKKKKKK UUUUUUUUUUUUUUUUUUUUUUUU
  2288 |   KKKKKKKKK    UUUUUUUUUUUUUUUUU
  2224 |   KKKKKKKKK    UUUUUUUUUUUUUUUUU
  2160 |   KKKKKKKKK    UUUUUUUUUUUUUUUUU      $$    <- sec4 closet
  2096 |        ++              ++             $$    <- store and turbine doors
  2032 |      NNNNNNNnnnnnnnnnnnnnnnnnnnnnnnnEEEEEE  <- north gallery 144 (n); NE tower (E)
  1968 |      NNNNNNNnnnnnnnnnnnnnnnnnnnnnnnnYEEEEE  <- yellow door (768,1952)
  1904 |      NN     nnnnnnnnnnnnnnnnnnnnnnnnEEEEEE
  1840 |      NN     www~~~~~~~~~~~~~~~~~-eee    EE  <- NW tower stairs 72-144 (N), NE stairs 168-240
  1776 |      NNNNNNBwww~~~~~~~~~~~~~~~~~-eee    EE  <- blue door (-768,1696)
  1712 |      NNNNNNBwww~~~~~~~~~~~~~~~~~-eeeEEEEEE  <- ne_top 240 opens onto the east gallery
  1648 |      NNNNNN www~~~~~~~~~~~~~~~~~-eeeEEEEEE
  1584 |             www~~~~~CCCCCCC~~~~~-eee
  1520 |   TTTTTTTTT wwwww~~CCCCCCCCC~~~~-eee        <- pier 40 off the west gallery
  1456 |   TTTTTTTTT wwwww~~CCCCCCCCC~~~~-eeeRRRRR   <- control window (768-800, 1248-1376)
  1392 |TTTTTTTTTTTT+www~~~~CCCXXX CC====+eeeRRRRR   <- crown 280 (X), hatch (+) at x 112-128
  1328 |TTTTTTTbTTTT+www~~~~CCCXXX+CC====+eeeRRRRR   <- tank door (-768,1312); causeway 256 (=), shutter (+)
  1264 |TT TTTTTTTTT www~~~~CCCXXX+CC====+eeeRRRRR   <- exit niche on the crown's west wall; switch (800,1184-1248)
  1200 |   TTTTTTTTT www~~~~CCCXXX CC~~~~-eeeRRRRR   <- control door (768,1120)
  1136 |   TTTTTTTTT www~~~~CCCCCCCCC~~~~-eeeRRRRR
  1072 |    TT   PPPPwww~~~~~CCCCCCC~~~~~-eeeRRRRR   <- core 272 (C) in the moat -48 (~)
  1008 |    TT   PPPPwww~~~~~~~$$$~~~~~~~-eee        <- secret ledge 96 ($)
   944 |    TT   PP  www~~~~~~~~L~~~~~~~~-eee        <- ledge lift (L)
   880 |         PP  www~~~~~~~~~~~~~~~~~-eee        <- west gallery 48 (w), east gallery 240 (e)
   816 |    PPPPPPPPPwww~~~~~~~~~~~~~~~~~-eee
   752 |    PPPPPPPPPwww~~~~~~~~~~~~~~~~~-eee
   688 | $$ PPPPPPPPPPP+ttttttttttttttttttLL         <- terrace 0 (t); lift 240->0 behind a shutter (LL)
   624 | $$+P  P PPPPPP+ttttttttttttttttttLL         <- pump-room door (-576,608); sec1 closet
   560 |    PPPPPPPPP   tttttttttttttttttt
   496 |    PPPPPPPPP          SSS ++  ++            <- start window, start door (192,448), filter door (448,512)
   432 |    PPPPPPPPP        SSSSSSSSFFFFFFFFFFF
   368 |                     SSS@SSSSFFFFFFFFFFF$$   <- start (@), filter house 0 with sludge beds (F), sec5
   304 |                     SSSSSSSSFFFFFFFFFFF$$
   240 |                     SSSSSSSSFFFFFFFFFFF
   176 |                             FFFFFFFFFFF
   112 |                             FFFFFFFFFFF
    48 |                             FFFFFFFFFFF
```

Legend: `S` start booth; `t` terrace; `~` moat (-48) with parapets (`-`); `C` core; `X` crown; `=` causeway; `w`/`n`/`e` west, north and east galleries; `P` pump room and its stairs; `T` tank room and closets (`b` blue key); `N` north-west stair tower; `K` storage; `U` turbine hall, dais and pens (`y` yellow key); `E` north-east stair tower; `R` control room; `F` filter house; `L` lifts; `B`/`Y` blue and yellow doors, `+` other doors and the shutters; `$` secrets; `@` start.

## Materials

**Base family: BRONZE.** The atrium is one continuous open space, so every one of its walls is **BRONZE2**: the terrace, the three galleries, the parapets' kerbs and moat faces, the lift shaft. Its sides are told apart by height (0, 48, 144, 240), light (176 west to 216 east) and what's beside them (the start booth and filter house, the pier, the turbine-hall door, the control window), not by material. The two stair towers are connective tissue and open straight onto the galleries, so they're BRONZE2 too, risers included. Projected from the current wall areas: **0.36**.

**Trim set: SUPPORT3**, the bronze girder, for every door recess, the causeway's sides, the causeway and lift shutters, and the pier. **SUPPORT2**, the grey girder, in the steel rooms only: the control room's door recess and window frame either side of its switch, and the crown's exit niche.

**Signature families**, one per area:
- **TEKGREN** for the reactor: TEKGREN2 on the core's sides, TEKGREN5 (with its yellow lamp strip) inside the crown, TEKGREN1 (hazard stripes) for the crown's hatch. One family, so the hatch and crown need no trim against the core.
- **SILVER** for the operations rooms: SILVER3 (instrument panels) in the start booth and the control room, SILVER1 plain for the start window's jambs and sill.
- **PIPE4** for the pump room, as built.
- **TEKWALL1** for the tank room and its closets, as built.
- **BROWN1** for storage, as built.
- **TEKBRON** for the turbine hall: TEKBRON1 on its walls and closet, TEKBRON2 inside the pens, METAL on the turbine housings and the dais step.
- **BROWNGRN** for the filter house: the slime-stained shed, the same choice as MAP02's filter house, so the set's filter houses look alike.

**Doors**: every door is BIGDOOR4, the bronze door, on DOORTRAK tracks; the key doors keep DOORBLU/DOORYEL tracks. BIGDOOR2 and BIGDOOR7 go.

| Area (route spaces) | Walls | Trim | Flats (floor / ceiling) | Reason |
|---|---|---|---|---|
| Atrium (terrace, par_sw, par_se, moat_gap, mstep, moat, gal_w, par_w_s, par_w_n, gal_n, par_n, gal_e, par_e_s, par_e_n, lift_se) | BRONZE2 everywhere, kerbs and risers included; mstep's nukage edge NUKEDGE1 | SUPPORT3 door recesses; lift sides PLAT1 | walkways FLOOR5_2 / SKY; parapet tops FLAT5_4; moat NUKAGE1 | base family; one space, so one material |
| Causeway, shutters, pier (causeway, d_gate, d_shut, pier) | SUPPORT3 | SUPPORT3 is itself a border | FLAT23 / SKY | girder bridgework across the moat |
| Reactor (core_e, core_w, ledge, lift_core, d_crown, crown, niche) | core, secret ledge face and its lift's sides TEKGREN2; crown TEKGREN5; hatch TEKGREN1 | SUPPORT2 exit niche | core FLOOR4_8, crown FLOOR0_1 / TLITE6_4 | signature: the landmark, green against the bronze; the secret hides in it |
| Start booth (start, window_s, d_start) | SILVER3; window jambs and sill SILVER1, the sill's terrace face BRONZE2 | SUPPORT3 recesses, risers in each side's wall | FLOOR0_6 / CEIL3_5 | signature: an observation booth |
| Filter house (d_filt, filt, bed*, crate_f*, d_sec5, sec5) | BROWNGRN; crates CRATE1 | SUPPORT3 recesses | FLOOR1_7 / CEIL5_2 | signature: the slime shed |
| Pump room (d_west, wcorr, pumps, d_sec1, sec1, pst*, pland) | PIPE4; stair risers STEP4 | SUPPORT3 terrace-side recess | FLOOR3_3, stairs and landing FLOOR5_2 / CEIL5_2 | signature: pumps are pipes |
| Tank room (d_tank, tank, ring_b, ped_b, pool*, tcl_w, tcl_s) | TEKWALL1; pool edges NUKEDGE1; pedestal METAL | SUPPORT3 recesses | FLAT9 / CEIL4_1 | signature: the blackout set piece's machinery |
| NW stair tower (d_blue, nw_low, nwst*, nw_top) | BRONZE2, risers BRONZE2 | SUPPORT3 recesses, DOORBLU tracks | FLOOR5_2 / CEIL5_1 | base family: opens straight onto the north gallery |
| Storage (d_store, store, crate_a, crate_s*) | BROWN1; crates CRATWIDE, CRATE2 | SUPPORT3 recesses | FLOOR0_5 / CEIL5_1 | signature: a warehouse |
| Turbine hall (d_turb, turb, turbine_*, dais, ped_y, pwall_*, pen_*, d_sec3, sec3) | TEKBRON1; pens TEKBRON2; turbines and dais step METAL | SUPPORT3 recesses | FLOOR0_2, dais FLOOR4_8 / CEIL5_1 | signature: bronze machinery, of a piece with the base |
| NE stair tower (d_yel, ne_low, nest*, ne_top, d_sec4, sec4) | BRONZE2, risers BRONZE2 | SUPPORT3 recesses, DOORYEL tracks | FLOOR5_2 / CEIL3_5 | base family: opens straight onto the east gallery |
| Control room (d_ctrl, ctrl, window_c) | SILVER3; window sill's gallery face BRONZE2 | SUPPORT2 recess and window frame either side of the SW1COMP switch | FLAT14 / TLITE6_5 | signature: operations, like the start booth |

### Change list

Grouped by sector. The `Now` column is what the original module has; anything not listed stays.

| Sector(s) | Now | New |
|---|---|---|
| `OUT_S`, `OUT_W`, `OUT_N`, `OUT_E` constants | TEKWALL4, BROWNGRN, BRONZE2, SILVER3 | one `BASE = "BRONZE2"` |
| `F_TER`, `F_GW`, `F_GN`, `F_GE` | FLOOR4_6, FLOOR7_1, FLOOR5_2, FLAT5_5 | one `F_WALK = "FLOOR5_2"` for terrace, galleries, towers, thresholds and pump stairs |
| par_sw, par_se lower | SUPPORT3 | BRONZE2 |
| start | COMPSPAN | SILVER3 |
| window_s | COMPSPAN, lower METAL | SILVER1, lower SILVER1; terrace-side sill BRONZE2 (OVERRIDES) |
| all door recesses | COMPSPAN, BRICK7, SUPPORT2 | SUPPORT3 (SUPPORT2 inside the control room); recess step risers in the facing room's wall |
| door faces | BIGDOOR2, BIGDOOR7 | BIGDOOR4 |
| filt, bed*, crate_f*, sec5 | BRICK7 | BROWNGRN |
| d_crown | face and track METAL2 | face TEKGREN1, track DOORTRAK |
| crown | EXITSTON | TEKGREN5 |
| niche | EXITSTON | SUPPORT2 |
| nw_low, nwst*, nw_top | STONE2, risers SUPPORT2 | BRONZE2, risers BRONZE2 |
| ne_low, nest*, ne_top, sec4 | STONE3 (ne_low and sec4 floor FLOOR1_1), risers SUPPORT2 | BRONZE2, risers BRONZE2, floors FLOOR5_2 |
| dais lower | SUPPORT2 | METAL |
| pen_w, pen_e | METAL1 | TEKBRON2 |
| ctrl | COMPBLUE | SILVER3 |
| d_ctrl | 16-deep recess on the gallery side; door flush in the control room's wall | 8 recess, 8-thick door, 16 recess into the control room (same 32-unit wall) |
| window_c | COMPBLUE | SUPPORT2 jambs, sill and lintel on the control-room side; gallery-side sill BRONZE2 (OVERRIDES) |
| lift_se | SILVER3 | BRONZE2 |

Each of the 9 seams the build lists goes away: the atrium's corner seams (gal_w, gal_n, nw_top) because both sides are now BRONZE2; terrace BRICK7|TEKWALL4 because the filter door's recess is trim; the crown and hatch seams because the hatch is the core's own family; the control room's three because its door is recessed and its window framed in SUPPORT2 either side of the switch.

## Secrets

Unchanged in place and reward. Each panel is in its room's own material, with the default `SECRET_HINT` offset.

| # | Where | Hint | Reward |
|---|---|---|---|
| 1 | sec1, west wall of the pump room | the PIPE4 panel is offset against the wall | green armor |
| 2 | ledge on the core's south face, up a lift from the moat | the ledge and its items are in view from the start window; in the moat the lift is plain core panelling (TEKGREN2), so the clue is knowing the ledge is above you | blue armor, rockets |
| 3 | sec3, west wall of the turbine hall | the TEKBRON1 panel is offset | backpack |
| 4 | sec4, north wall of the north-east stair tower | the BRONZE2 panel is offset | soulsphere |
| 5 | sec5, east wall of the filter house | the BROWNGRN panel is offset | plasma rifle |

## Targets

| Target (DOOM II median) | Plan | Where it comes from |
|---|---|---|
| most-used wall texture 0.2–0.45 [0.3] | **0.36 BRONZE2** | every atrium wall and both stair towers |
| rule-2 seams with a border ≥ 0.5 [0.31] | **≥ 0.7, none listed** | SUPPORT3 recesses at every door; SUPPORT2 round the control-room switch; same-family joins at the atrium's corners and the crown |
| optional share ≥ 0.3 [0.5] | 0.40, unchanged | filter house, storage, pier, ledge, the secret closets |
| distinct floor heights ≥ 15 [23] | 29, unchanged | moat -48 to crown 280: terrace 0, galleries 48/144/240, tower stairs, causeway 256, core 272 |
| secrets ≥ 2 [4] | 5, unchanged | sec1, ledge, sec3, sec4, sec5 |
| light-effect sectors ≥ 3 [9] | 10, unchanged | flickering pump room, filter house and tank closets; blinking NW tower and pens; glowing crown and pedestals |
| deaf share (UV) ≥ 0.2 [0.42] | 0.48, unchanged | waiting monsters on the core's rim and in the wings |

## Build risks

- **The control-room door moves 8 units.** Its recesses and an 8-thick door fit the same 32-unit wall, so the room and gallery don't move, but the playtest's `open` at the door and the reach check must still pass.
- **Texture fit.** BRONZE2 is 64×128 and tiles under the 448 sky; the atrium's 32-high kerbs and 8-high recess steps show a slice of it, pegged so the panels line up with the wall. TEKGREN5's lamp strip sits at the crown's ceiling only if the crown's walls stay top-pegged.
- **Window sills per side.** A window's sill shows the window sector's `lower` on both sides; the outside face is set in `OVERRIDES` and unpegged to line up with the bronze.
- **Don't regress the untouched measures.** No sector heights, lights, things or specials change. Compare the full measurement table, the resource curve and the reach check with the baseline.

## As built

`levels/nukage_core.py` is authoritative; the first version is archived as `levels/nukage_core_original.py` (not built into the WAD).

- **Measured** (build table, DOOM II median in brackets): most-used wall texture 0.36 BRONZE2 [0.3], rule-2 seams with a border 0.77 [0.31] with no unbordered seams listed, 25 wall textures (was 31), rule-1 slips 0. Everything else is identical to the baseline: 29 floor heights, 5 secrets, 10 light-effect sectors, deaf share 0.48, optional share 0.40, symmetry 0.62, and the same resource curve (lowest detour ratio 1.75, on the blue-key leg).
- **Door thresholds** keep the walkway flat (FLOOR5_2) through both recesses, so the flat changes at the step down into each room rather than at the door.
- **The crown's 8-unit step** at the hatch shows TEKGREN5's lamp strip as a lit sill, seen from the causeway. It's the crown's own material, so it stays.
- **Secret lift disguised** (play feedback): the original's ledge lift had the default PLAT1 sides and the ledge a METAL face, a grey hazard-striped block and a dark column against the green core that gave the secret away from anywhere in the moat. Both are now TEKGREN2.
- **Playtest** (`levels/playtests/nukage_core.playtest`; `nukage_core_original.playtest` runs the same route and shots on the archived map). Material shots added to both: `terrace`, `filter-house`, `pump-room`, `gallery-west`, `stair-tower-nw`, `storage`, `turbine-hall`, `gallery-north`, `gallery-east`, `control-room`, joining `start`, `blackout`, `pens`, `control-window`, `causeway` and `crown`. Wiring passes on both, 26 checks, 0 fails.
- **Fight runs** (UV, seeds 1–3, on both versions) play the same, and every death cluster is the bot's:

  | Seed | Retextured: deaths (labels), kills | Original: deaths (labels), kills |
  |---|---|---|
  | 1 | 52 (41 hazard, 9 starved, 2 combat), 24 | 57 (22 hazard, 23 starved, 10 combat, 1 unseen, 1 stuck), 70 |
  | 2 | 54 (40 hazard, 10 starved, 3 stuck, 1 combat), 24 | 55 (41 hazard, 10 starved, 2 stuck, 2 combat), 24 |
  | 3 | 39 (13 hazard, 22 starved, 4 combat), 70 | 43 (16 hazard, 19 starved, 8 combat), 61 |

  - `hazard`: the moat detour to the ledge secret. The bot misses the ledge lift's window at the bottom while fighting, stands beside it in the nukage, and dies about every 18 s, too slowly for the 30 s loop check to warp it on. Seeds 1 and 2 of the retextured map and seed 2 of the original stay there until the 15-minute cap (seed 2 almost identically on both); seed 1 of the original died faster there and was warped on. A lift in a damaging floor is one of the bot's known weak spots, so the map and script stay as they are; seed 3 covers the whole route on both.
  - `starved`: the static curve's lowest detour ratio is 1.75, with no leg short on either curve, so the bot wasted the ammo.
  - Seed 3's one fail is the blue door's `open` mid-fight ("door still only 0 high"), with the bot out of ammo; by the next step it was inside the stair tower, so the door did open. The wiring run opens it every time.
