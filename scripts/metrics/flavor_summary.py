"""Per-(game, flavor) norms of every research metric: median, IQR and n.

Reads every metrics CSV the metrics scripts write (data/metrics/metrics_*.csv
and data/metrics/sets/*/metrics_*.csv; every row carries doomwad.META_COLS)
and data/metrics/flavors.csv (set -> flavor), and writes:

    data/metrics/flavor_summary.csv   game, flavor, metric, n, median, q1, q3, provisional
    data/metrics/flavor_coverage.csv  per (game, flavor): sets, every map marker, measured maps,
                                       non-Doom-format maps, decompile outcomes,
                                       progression-invalid maps, maps whose exit the reach
                                       model can't reach (blank critical-path and route
                                       metrics), provisional (fewer than MIN_N measured)

Before that it gives every downloaded community release with no row in
flavors.csv one, by release year (assign_community_flavors).

A metric is `<table>.<column>` (space.width_median), as in correlations.csv.
Progression and route metrics skip maps with progression_valid=false. A group
with fewer than MIN_N values is kept and marked provisional, never dropped.
Quartiles: statistics.quantiles(n=4, method="exclusive"), as levels/measure.py.

Run from the repo root (after the metrics scripts; see docs/metrics-data.md):
    python3 scripts/metrics/flavor_summary.py              # write both CSVs, print coverage
    python3 scripts/metrics/flavor_summary.py space.width_median   # also print those metrics
"""
import csv
import glob
import os
import statistics
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from doomwad import DECOMPILE_STATUS, IDGAMES, META_COLS, METRICS as DATA, _csv, releases  # noqa: E402

MIN_N = 10
NOT_METRICS = set(META_COLS) | {"map", "episode"}
REACH_TABLES = {"progression", "route"}   # built on the reach model
OUT = os.path.join(DATA, "flavor_summary.csv")
OUT_COVERAGE = os.path.join(DATA, "flavor_coverage.csv")


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def tables():
    """[(table name, path)] for every metrics CSV."""
    paths = sorted(glob.glob(os.path.join(DATA, "metrics_*.csv"))) + \
        sorted(glob.glob(os.path.join(DATA, "sets", "*", "metrics_*.csv")))
    return [(os.path.basename(p)[len("metrics_"):-len(".csv")], p) for p in paths]


def assign_community_flavors():
    """Append a flavors.csv row for every downloaded community release that
    has none, by its release year (doomwad.releases). Existing rows, hand
    edits included, are never changed. Needs the local idgames download."""
    path = os.path.join(DATA, "flavors.csv")
    with open(path, newline="") as f:
        known = {r["set"] for r in csv.DictReader(f)}
    new = [{"set": r["set"], "flavor": era(r["year"]),
            "reason": f"community release, {r['year']} ({r['year_source']})"}
           for r in releases() if r["set"] not in known]
    if new:
        with open(path, "a", newline="") as f:
            csv.DictWriter(f, fieldnames=["set", "flavor", "reason"], lineterminator="\n").writerows(new)
        print(f"flavors.csv: {len(new)} community releases added")


def era(year):
    return "1993-2003" if year <= 2003 else "2004-2014" if year <= 2014 else "2015-present"


def main(argv):
    if os.path.exists(os.path.join(IDGAMES, "manifest.csv")):
        assign_community_flavors()
    with open(os.path.join(DATA, "flavors.csv"), newline="") as f:
        flavor_of = {r["set"]: r["flavor"] for r in csv.DictReader(f)}
    values = defaultdict(list)    # (game, flavor, metric) -> [value]
    maps = defaultdict(dict)      # (game, flavor) -> {(set, wad, slot): metadata row}
    unassigned = set()
    no_exit = defaultdict(set)    # (game, flavor) -> maps whose exit the reach model can't reach
    for table, path in tables():
        with open(path, newline="") as f:
            rows = list(csv.DictReader(f))
        if rows and "set" not in rows[0]:
            sys.exit(f"{os.path.relpath(path)} has no metadata columns: rerun its metrics script")
        for r in rows:
            flavor = flavor_of.get(r["set"])
            if flavor is None:
                unassigned.add(r["set"])
                flavor = "unassigned"
            group = (r["game"], flavor)
            maps[group][r["set"], r["wad"], r["slot"]] = r
            if table == "progression" and r["exit_reachable"] != "1":
                no_exit[group].add((r["set"], r["wad"], r["slot"]))
            if table in REACH_TABLES and r["progression_valid"] != "true":
                continue
            for k, v in r.items():
                if k not in NOT_METRICS and (x := num(v)) is not None:
                    values[(*group, f"{table}.{k}")].append(x)
    if unassigned:
        print(f"warning: sets with no row in flavors.csv (grouped as 'unassigned'): {', '.join(sorted(unassigned))}")

    out = []
    for (game, flavor, metric), xs in sorted(values.items()):
        q1, md, q3 = (statistics.quantiles(xs, n=4, method="exclusive") if len(xs) >= 2
                      else (None, xs[0], None))
        out.append({"game": game, "flavor": flavor, "metric": metric, "n": len(xs),
                    "median": f"{md:.4g}", "q1": "" if q1 is None else f"{q1:.4g}",
                    "q3": "" if q3 is None else f"{q3:.4g}", "provisional": str(len(xs) < MIN_N).lower()})
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)

    # Coverage: every map decompile_status.csv lists (every map marker, UDMF
    # and Hexen ones too) plus every measured map.
    status = {}
    for r in _csv(DECOMPILE_STATUS):
        game = "doom" if r["slot"][0] == "E" else "doom2"
        status[game, flavor_of.get(r["set"], "unassigned"), r["set"], r["wad"], r["slot"]] = r
    groups = defaultdict(set)
    for (game, flavor, *key) in status:
        groups[game, flavor].add(tuple(key))
    for group, ms in maps.items():
        groups[group] |= set(ms)
    cov = []
    for (game, flavor), keys in sorted(groups.items()):
        measured = maps.get((game, flavor), {})
        outcome = defaultdict(int)
        for key in keys:
            r = status.get((game, flavor, *key))
            outcome[r["decompile"] if r else "unknown"] += 1
        not_doom = sum(1 for key in keys if (r := status.get((game, flavor, *key)))
                       and r["detail"] in ("udmf map", "hexen map", "broken map"))
        sets = sorted({s for s, _, _ in keys})
        cov.append({"game": game, "flavor": flavor, "n_sets": len(sets), "sets": ";".join(sets),
                    "maps": len(keys), "measured": len(measured), "not_doom_format": not_doom,
                    "decompile_ok": outcome["ok"], "decompile_repaired": outcome["repaired"],
                    "decompile_refused": outcome["refused"] - not_doom,
                    "decompile_lines_only": outcome["lines-only"], "decompile_timeout": outcome["timeout"],
                    "decompile_error": outcome["error"], "decompile_unknown": outcome["unknown"],
                    "progression_invalid": sum(r["progression_valid"] != "true" for r in measured.values()),
                    "exit_unreachable": len(no_exit[game, flavor]),
                    "provisional": str(len(measured) < MIN_N).lower()})
    with open(OUT_COVERAGE, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(cov[0]))
        w.writeheader()
        w.writerows(cov)
    print(f"wrote {os.path.relpath(OUT)} ({len(out)} rows), {os.path.relpath(OUT_COVERAGE)}\n")
    cols = ("n_sets", "maps", "measured", "not_doom_format", "decompile_ok", "decompile_repaired",
            "decompile_refused", "decompile_lines_only", "decompile_timeout", "decompile_error",
            "decompile_unknown", "progression_invalid", "exit_unreachable")
    print("| game | flavor | " + " | ".join(c.removeprefix("decompile_").replace("_", " ") for c in cols) + " |")
    print("|---|---|" + "---|" * len(cols))
    for c in cov:
        mark = " (provisional)" if c["provisional"] == "true" else ""
        print(f"| {c['game']} | {c['flavor']}{mark} | " + " | ".join(str(c[k]) for k in cols) + " |")
    for metric in argv:
        print(f"\n{metric}: median [q1-q3] (n)")
        for r in (r for r in out if r["metric"] == metric):
            mark = " provisional" if r["provisional"] == "true" else ""
            print(f"  {r['game']:5} {r['flavor']:10} {r['median']} [{r['q1']}-{r['q3']}] (n={r['n']}){mark}")


if __name__ == "__main__":
    main(sys.argv[1:])
