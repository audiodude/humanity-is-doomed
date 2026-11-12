# Research metrics: the dataset

One pipeline (`scripts/metrics/`) measures every map it can read and writes one dataset to `data/metrics/`. Rows from every era and set have the same columns; maps are split into flavors only when they're read, through `data/metrics/flavors.csv`. Later code (per-set flavors in `levels/sets`, `levels/measure.py` against flavor medians) will read these files, so the column names below are stable.

`data/metrics/` is tracked: it holds only measurements, facts (authors, years, formats) and statistics. The local, untracked `research/` tree keeps what quotes or redraws other people's work: `research/data/reception.csv` and `designers.csv` (paraphrased reviews and interviews), the facet write-ups, and the SVGs in `research/maps/` (id's geometry). The metrics scripts read `designers.csv`, `reception.csv` and `episode_maps.csv` from there for the `authors` and `rating` columns, when they exist.

## Regenerating

```sh
scripts/metrics/run_all.sh                  # everything, in this order (hours: the community maps dominate)
scripts/metrics/run_all.sh --no-community   # id maps and official sets only (about 20 minutes)
```

1. `python3 scripts/metrics/map_svgs.py [SET ...] [--timeout CPU_SECONDS]`: decompiles every map, keeps each module in `levels/imported/<set>__<wad>_<slot>.py` (gitignored; build one with `python3 -m levels imported.<name>`), draws `research/maps/<set>/<map>.svg` (community: `research/maps/community/<release>/<WAD>_<slot>.svg`) and writes `data/metrics/decompile_status.csv` (`set, wad, slot, svg, module, decompile, detail, cpu_seconds`; every map marker, UDMF and Hexen ones too). The time limit (default 300) counts each worker's CPU time, so load can't cause timeouts, but run it alone anyway: beside the metrics scripts both slow down and memory runs short. The metrics read their `decompile` column from it, and it rewrites that column in every existing metrics CSV when it finishes, so it can run before or after them. `map_svgs.py tnt master` redoes some sets, `map_svgs.py community` the community releases; `--index` only rewrites `research/maps/INDEX.md`.
2. For the id maps (no flag), then each official set (`--set tnt`, `--set plutonia`, `--set master`; the list is `doomwad.SETS`) and the community releases (`--set community`):
   `space_metrics.py`, `combat_metrics.py`, `progression_metrics.py`, `route_metrics.py`. The id maps go to `data/metrics/metrics_<table>.csv`, a set to `data/metrics/sets/<set>/metrics_<table>.csv`. Each runs on every core with a 15-minute limit per map; a map that raises or runs out of time gets no row and is listed in `errors_metrics_<table>.csv` beside it.
3. `python3 scripts/metrics/flavor_summary.py [METRIC ...]`: gives new community releases a `flavors.csv` row, then writes the per-(game, flavor) summary, below.
   `python3 scripts/metrics/era_report.py`: a markdown table of key norms per (game, flavor), each release reduced to its median first so a megawad counts once, with Spearman ρ of release year against each metric for DOOM and DOOM II community releases and whether their signs agree. Combat columns leave out releases that change monsters with DEHACKED.
4. `python3 research/correlate.py`: metrics against per-map reception, written to `data/metrics/correlations.csv` (needs the local `research/` tree).

Paths come from `.env`: `DOOM_WAD`, `DOOM2_WAD` (v1.9 IWADs) and `DOOM_STEAM_BASE` (the Steam "Ultimate Doom" `base/` directory, with `tnt/`, `plutonia/` and `master/wads/`). The community releases are the local `research/sources/idgames/` download of `research/fetch_idgames.py` (rating ≥ 4.0, ≥ 10 votes; `manifest.csv`).

### Community releases

Each downloaded idgames zip is a set named after it (`btsx_e1`; a name in both `levels/doom/` and `levels/doom2/` gets `@doom` on the DOOM one). Every WAD in the extracted zip is read, and every Doom-format map in them is measured over the IWAD its slot needs (ExMy: `DOOM_WAD`, MAPxx: `DOOM2_WAD`), with all the release's WADs loaded after it for textures. A map repeated byte for byte inside a release is measured once; variant WADs of the same map (fixes, easier patches) are kept, with `wad` telling them apart. DEHACKED monster changes are not applied: monster HP and ammo use the vanilla tables, and `format_evidence` lists `DEHACKED` (a lump in the map's WAD) or `deh_file` (a `.deh` in the release) so such maps can be left out.

## Metadata columns

Every row of every metrics CSV ends with these columns (`doomwad.META_COLS`), after the metric columns. `combat` and `progression` already had `game`; it keeps its place.

| column | values |
|---|---|
| `set` | `doom`, `doom2`, `tnt`, `plutonia`, `master`, or a community release (its zip name); later `sigil`, `nerve`. The key into `flavors.csv`. |
| `game` | `doom` or `doom2` (the map format's game: SIGIL is `doom`). Never pooled across. |
| `slot` | `E1M1`, `MAP01` (same as `map`) |
| `wad` | stem of the WAD the map lumps come from: `DOOM`, `DOOM2`, `TNT`, `ATTACK` |
| `year` | release year of the set or WAD (E4: 1995) |
| `year_source` | `official release`; community: `txt file` (a release/date line in the release's txt, if not after the upload), else `cacowards` (the award year, if it isn't more than a year after upload), else `idgames date` (upload date, can be years after release) |
| `authors` | per map where known (id: `designers.csv`; other official sets: `episode_maps.csv`, matched on geometry; community: the map's UMAPINFO `author`), else the WAD's author (idgames), else blank |
| `official` | `true` / `false`. A tag, not a flavor. |
| `format` | `vanilla`, `limit-removing`, `boom`, `mbf21`, `hexen`, `udmf` (see below) |
| `format_evidence` | `;`-separated: `generalized=N`, `specials>141=N`, `mbf21_specials=N`, `special_65535=N`, `thing_flags=N`, `line_flags=N`, `index>32767`, the WAD lumps `COMPLVL`, `UMAPINFO`, `DEHACKED`, and `deh_file` (a community release ships a `.deh`) |
| `nonvanilla_specials` | lines with Boom extended, generalized or MBF21 actions |
| `decompile` | `ok`, `repaired` (unclosed sectors repaired), `refused` (the decompiler refused it; UDMF and Hexen maps always), `lines-only` (decompiled, but the module doesn't build), `timeout` (over the CPU-time limit) or `error` (the decompiler crashed); blank if `map_svgs.py` hasn't run on its set |
| `progression_valid` | `false` when the map has a line action the reach model doesn't know (not in `levels/doom2.LINE_SPECIALS`), so its progression and route metrics can't be trusted |
| `rating` | per-map: `reception.csv` score (−2..+2); per-WAD: the idgames rating (1–5) |
| `votes` | sources (per-map) or idgames votes (per-WAD) |
| `rating_scope` | `per-map` (id maps), `per-WAD` (idgames: every map of a WAD shares one score), `none` |

`format` comes from the map, in this order: a `TEXTMAP` lump is `udmf`, `BEHAVIOR` is `hexen`; a `COMPLVL` lump names it outright (`mbf` counts as `boom`); MBF21 offset scrollers (1024–1026) make `mbf21`; Boom actions (above 141, or generalized from 0x2F80) or Boom/MBF thing flags (32, 64, 128) make `boom`; sidedef or vertex indexes over 32767 make `limit-removing`; otherwise `vanilla`. Line flags, `UMAPINFO` and `DEHACKED` are evidence only: vanilla ignores high line flags, and E2M7 carries DoomEd junk (flags 0xFE00 on 249 lines and one action 65535). Limit-removing maps that only overflow visplanes or drawsegs look `vanilla`: those limits can't be checked statically. UDMF and Hexen maps don't parse yet, so they have no rows.

## Flavors

`data/metrics/flavors.csv` has `set, flavor, reason`, one row per set. Flavors: `doom` (id's E1–E4), `doom2` (id's DOOM II), `1993-2003`, `2004-2014`, `2015-present`. A flavor groups maps within one game: the summary keys on `(game, flavor)`, so a DOOM-format community map is never compared with DOOM II maps. Official sets are filed by the era they play like (TNT, Plutonia, Master Levels: `1993-2003`; NRFTL: `2004-2014`; SIGIL, SIGIL II, Legacy of Rust: `2015-present`, reasons in the file). Community releases get a row by release year (`year` above) the first time `flavor_summary.py` sees them; it never changes an existing row, so a release can be refiled by hand. Moving a set is a one-line edit, then `flavor_summary.py`; no metric is recomputed.

## Per-flavor summary

`flavor_summary.py` reads every metrics CSV and writes:

- `data/metrics/flavor_summary.csv`: `game, flavor, metric, n, median, q1, q3, provisional`. `metric` is `<table>.<column>` (`space.width_median`), as in `correlations.csv`. Quartiles use `statistics.quantiles(n=4, method="exclusive")`, like `levels/measure.py`. Progression and route metrics leave out `progression_valid=false` maps. A group with fewer than 10 values is kept and marked `provisional=true`.
- `data/metrics/flavor_coverage.csv`: per `(game, flavor)`: `n_sets`, `sets`, `maps` (every map marker in `decompile_status.csv`, plus any measured map), `measured` (maps with metric rows), `not_doom_format` (UDMF, Hexen-format or broken maps: never measured), decompile outcomes (`ok`, `repaired`, `refused`, `lines_only`, `timeout`, `error`, `unknown`), `progression_invalid` and `exit_unreachable` (maps whose exit the reach model can't reach, so their critical-path and route metrics are blank), so the bias of what got measured shows. `provisional` is `true` under 10 measured maps.

Sets missing from `flavors.csv` are grouped as `unassigned` with a warning, not dropped.

## How the data is meant to be used

- Norms (size, detail, monster HP, ammo ratios): per-(game, flavor) medians from `flavor_summary.csv`.
- Quality signals: correlations stay pooled, with ranks taken within each group (`rho_within`), and count only if the per-group signs agree (`sign_disagrees` in `correlations.csv` is 1 when `rho_doom` and `rho_doom2` have opposite signs). Per-WAD community ratings are evidence for norms, not for map-level quality.
- Mechanics checks don't use flavors.
