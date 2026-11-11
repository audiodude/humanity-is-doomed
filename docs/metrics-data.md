# Research metrics: the dataset

One pipeline (`scripts/metrics/`) measures every map it can read and writes one dataset to `data/metrics/`. Rows from every era and set have the same columns; maps are split into flavors only when they're read, through `data/metrics/flavors.csv`. Later code (per-set flavors in `levels/sets`, `levels/measure.py` against flavor medians) will read these files, so the column names below are stable.

`data/metrics/` is tracked: it holds only measurements, facts (authors, years, formats) and statistics. The local, untracked `research/` tree keeps what quotes or redraws other people's work: `research/data/reception.csv` and `designers.csv` (paraphrased reviews and interviews), the facet write-ups, and the SVGs in `research/maps/` (id's geometry). The metrics scripts read `designers.csv`, `reception.csv` and `episode_maps.csv` from there for the `authors` and `rating` columns, when they exist.

## Regenerating

```sh
scripts/metrics/run_all.sh     # everything, in this order (about 20 minutes)
```

1. `python3 scripts/metrics/map_svgs.py`: decompiles every map, draws `research/maps/<set>/<map>.svg` and writes `data/metrics/decompile_status.csv` (`set, wad, slot, svg, decompile, detail`). It runs first because the metrics read their `decompile` column from it. `map_svgs.py tnt master` redoes some sets; `--index` only rewrites `research/maps/INDEX.md`.
2. For the id maps (no flag) and then each official set (`--set tnt`, `--set plutonia`, `--set master`; the list is `doomwad.SETS`):
   `space_metrics.py`, `combat_metrics.py`, `progression_metrics.py`, `route_metrics.py`. The id maps go to `data/metrics/metrics_<table>.csv`, a set to `data/metrics/sets/<set>/metrics_<table>.csv`.
3. `python3 scripts/metrics/flavor_summary.py [METRIC ...]`: the per-(game, flavor) summary, below.
4. `python3 research/correlate.py`: metrics against per-map reception, written to `data/metrics/correlations.csv` (needs the local `research/` tree).

Paths come from `.env`: `DOOM_WAD`, `DOOM2_WAD` (v1.9 IWADs) and `DOOM_STEAM_BASE` (the Steam "Ultimate Doom" `base/` directory, with `tnt/`, `plutonia/` and `master/wads/`).

## Metadata columns

Every row of every metrics CSV ends with these columns (`doomwad.META_COLS`), after the metric columns. `combat` and `progression` already had `game`; it keeps its place.

| column | values |
|---|---|
| `set` | `doom`, `doom2`, `tnt`, `plutonia`, `master`; later `sigil`, `nerve`, community WAD ids. The key into `flavors.csv`. |
| `game` | `doom` or `doom2` (the map format's game: SIGIL is `doom`). Never pooled across. |
| `slot` | `E1M1`, `MAP01` (same as `map`) |
| `wad` | stem of the WAD the map lumps come from: `DOOM`, `DOOM2`, `TNT`, `ATTACK` |
| `year` | release year of the set or WAD (E4: 1995) |
| `year_source` | `official release`, `txt file`, `cacowards` or `idgames date` (upload date, can be years after release) |
| `authors` | per map where known (id: `designers.csv`; other official sets: `episode_maps.csv`, matched on geometry), else the WAD's author, else blank |
| `official` | `true` / `false`. A tag, not a flavor. |
| `format` | `vanilla`, `limit-removing`, `boom`, `mbf21`, `hexen`, `udmf` (see below) |
| `format_evidence` | `;`-separated: `generalized=N`, `specials>141=N`, `mbf21_specials=N`, `special_65535=N`, `thing_flags=N`, `line_flags=N`, `index>32767`, and the WAD lumps `COMPLVL`, `UMAPINFO`, `DEHACKED` |
| `nonvanilla_specials` | lines with Boom extended, generalized or MBF21 actions |
| `decompile` | `ok`, `repaired` (unclosed sectors repaired), `refused` (the decompiler refused it) or `lines-only` (decompiled, but the module doesn't build); blank if `map_svgs.py` hasn't run |
| `progression_valid` | `false` when the map has a line action the reach model doesn't know (not in `levels/doom2.LINE_SPECIALS`), so its progression and route metrics can't be trusted |
| `rating` | per-map: `reception.csv` score (−2..+2); per-WAD: the idgames rating (1–5) |
| `votes` | sources (per-map) or idgames votes (per-WAD) |
| `rating_scope` | `per-map` (id maps), `per-WAD` (idgames: every map of a WAD shares one score), `none` |

`format` comes from the map, in this order: a `TEXTMAP` lump is `udmf`, `BEHAVIOR` is `hexen`; a `COMPLVL` lump names it outright (`mbf` counts as `boom`); MBF21 offset scrollers (1024–1026) make `mbf21`; Boom actions (above 141, or generalized from 0x2F80) or Boom/MBF thing flags (32, 64, 128) make `boom`; sidedef or vertex indexes over 32767 make `limit-removing`; otherwise `vanilla`. Line flags, `UMAPINFO` and `DEHACKED` are evidence only: vanilla ignores high line flags, and E2M7 carries DoomEd junk (flags 0xFE00 on 249 lines and one action 65535). Limit-removing maps that only overflow visplanes or drawsegs look `vanilla`: those limits can't be checked statically. UDMF and Hexen maps don't parse yet, so they have no rows.

## Flavors

`data/metrics/flavors.csv` has `set, flavor, reason`, one row per set. Flavors: `doom` (id's E1–E4), `doom2` (id's DOOM II), `1993-2003`, `2004-2014`, `2015-present`. A flavor groups maps within one game: the summary keys on `(game, flavor)`, so a DOOM-format community map is never compared with DOOM II maps. Official sets are filed by the era they play like (TNT, Plutonia, Master Levels: `1993-2003`; NRFTL: `2004-2014`; SIGIL, SIGIL II, Legacy of Rust: `2015-present`, reasons in the file). Moving a set is a one-line edit there, then `flavor_summary.py`; no metric is recomputed.

## Per-flavor summary

`flavor_summary.py` reads every metrics CSV and writes:

- `data/metrics/flavor_summary.csv`: `game, flavor, metric, n, median, q1, q3, provisional`. `metric` is `<table>.<column>` (`space.width_median`), as in `correlations.csv`. Quartiles use `statistics.quantiles(n=4, method="exclusive")`, like `levels/measure.py`. Progression and route metrics leave out `progression_valid=false` maps. A group with fewer than 10 values is kept and marked `provisional=true`.
- `data/metrics/flavor_coverage.csv`: per `(game, flavor)`, its sets, map count, decompile outcomes (`ok`, `repaired`, `refused`, `lines_only`, `unknown`), progression-invalid maps and `exit_unreachable` (maps whose exit the reach model can't reach, so their critical-path and route metrics are blank), so the bias of what got measured shows.

Sets missing from `flavors.csv` are grouped as `unassigned` with a warning, not dropped.

## How the data is meant to be used

- Norms (size, detail, monster HP, ammo ratios): per-(game, flavor) medians from `flavor_summary.csv`.
- Quality signals: correlations stay pooled, with ranks taken within each group (`rho_within`), and count only if the per-group signs agree (`sign_disagrees` in `correlations.csv` is 1 when `rho_doom` and `rho_doom2` have opposite signs). Per-WAD community ratings are evidence for norms, not for map-level quality.
- Mechanics checks don't use flavors.
