# Community norms: first pass (2026-11-11)

What the rated idgames corpus says about how DOOM maps are built, by era. Data and method: [metrics-data.md](metrics-data.md); regenerate the table with `python3 scripts/metrics/era_report.py`.

## The corpus

539 idgames releases rated ≥ 4.0 with ≥ 10 votes (`research/fetch_idgames.py`): 3,250 map markers, 2,818 of them Doom-format and measured; 417 Hexen-format and 14 UDMF maps can't be parsed yet. Releases are filed into flavors by release year (txt file 290, idgames upload date 223, Cacowards year 26).

| game | flavor | releases | maps | measured | not Doom-format | progression-invalid | exit unreachable |
|---|---|---|---|---|---|---|---|
| doom | 1993–2003 | 40 | 259 | 241 | 18 | 30 | 24 |
| doom | 2004–2014 | 47 | 363 | 359 | 4 | 24 | 27 |
| doom | 2015–present | 9 | 119 | 119 | 0 | 0 | 19 |
| doom2 | 1993–2003 | 129 (incl. TNT, Plutonia, Master) | 679 | 610 | 69 | 48 | 116 |
| doom2 | 2004–2014 | 264 | 1,514 | 1,208 | 306 | 503 | 446 |
| doom2 | 2015–present | 21 | 399 | 365 | 33 | 217 | 152 |

Biases to keep in mind:

- **Only well-rated WADs.** These are norms of releases players liked, not of the archive.
- **Modern maps are under-measured.** 2004–2014 DOOM II loses 306 maps to Hexen/UDMF and 503 more to Boom actions the reach model doesn't know (progression and route metrics skip those). 2015–present has 21 releases and 365 maps, most of them Boom.
- **Combat leaves out DEHACKED releases** (monster stats would be wrong): DOOM II 2015–present has only 5 releases left for combat metrics. Treat that column as provisional.
- **Space metrics time out on the biggest maps** (101 of 2,818 over 15 minutes), so the size medians are a little low.
- The reach model finds no exit on about 15 % of progression-valid community maps; their critical-path and route numbers are blank.

## Findings [Q]

Values are medians of release medians (a megawad counts once); "id" is the median of id's maps. ρ is Spearman's ρ of release year against the release median, community releases only.

1. **Community maps are far bigger than id's, and DOOM II maps keep growing.** Linedefs: id DOOM II 774; community 2,070 (1993–2003), 4,253 (2004–2014), 4,839 (2015–). ρ(year) +0.31 for DOOM II and +0.18 for DOOM: the one size trend both games agree on.
2. **They carry about twice id's monster HP with half the healing.** DOOM II UV monster HP: id 16,560; community 32,700 and 35,030. Health per 1000 monster HP: id 39.8; community 19.4, 16.7. Armor per 1000 HP: 21.2 → 15.1, 11.6.
3. **Resources tighten over time in both games.** Pistol-start ammo ratio ρ −0.17 (DOOM) and −0.14 (DOOM II); armor per 1000 HP ρ −0.14 and −0.21. Signs agree in both games, which makes this the strongest trend in the set. The route model's lowest health along the critical path (`route_min_health`, negative means the pickups on the route don't cover the damage) falls from id's −0.5 (DOOM II) to −59 and −80 (2004–2014).
4. **More verticality and more choice.** DOOM II distinct floor heights: id 23; community 43, 52, 61. Optional area share: id 0.50; community 0.70–0.72. Room loops: id 8.5; community 13–18.
5. **The key structure is a constant.** 2–3 keys, key-chain depth 1–2, 3–4 secrets in every era and both games, the same as id's. Critical path length doesn't trend (ρ ≈ −0.05).
6. **id's DOOM II is the wide outlier.** Median space width: id DOOM II 324; community DOOM II 260–272, close to id's DOOM (239).
7. **DOOM-format and DOOM II community maps drift apart.** Walkable area, floor-height variety and room loops rise with year in DOOM II but fall in DOOM-format releases (signs disagree); sky share rises in DOOM II and is flat in DOOM. [INFERENCE] Modern DOOM-format releases lean on the "as id did it" style (compact, E1-like), while DOOM II releases scale up. This is why norms have to be per (game, flavor).

## What it means for NUKAGE

NUKAGE (DOOM II) averaged 516 linedefs and 63 UV monsters per map in facet 24's nine-map measurement. That is below id's DOOM II (774, 112) and a fraction of any community era. That's a choice, not an error, but next to the norms players rated well NUKAGE's maps are small. [INFERENCE] The levers the data points to are verticality, optional area and loops more than raw size or monster count; these are norms, not quality signals.

## Next

- Use these medians in `levels/measure.py` per set flavor (the planned change).
- Parse Hexen-format and UDMF maps, and teach the reach model Boom actions: today they take most of the modern data out of the progression metrics.
- Apply DEHACKED monster changes, so combat covers modern releases.
