"""How map norms move across flavors: a markdown report of key metrics per
(game, flavor), counted both per map and per release.

A megawad contributes 32 correlated maps, so each metric is also reduced to
one value per release (the median of its maps) before flavors are compared;
the `releases` columns use those. Combat metrics leave out maps whose release
changes monsters (DEHACKED lump or .deh file: doomwad applies the vanilla
tables), progression and route metrics maps with progression_valid=false.
`rho(year)` is Spearman's rho between release year and release median over
the community releases of one game; `agree` is yes when DOOM and DOOM II have
the same sign (|rho| < 0.1 counts as no trend).

Run from the repo root after the metrics scripts and flavor_summary.py:
    python3 scripts/metrics/era_report.py > /tmp/era.md
"""
import csv
import glob
import os
import statistics
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from doomwad import METRICS  # noqa: E402

KEY = [
    ("space", "n_lines", "linedefs"), ("space", "walkable_area", "walkable area (mu²)"),
    ("space", "width_median", "median space width"), ("space", "frac_width_le128", "share ≤128 wide"),
    ("space", "distinct_floor_heights", "distinct floor heights"), ("space", "floor_height_sd", "floor height SD"),
    ("space", "light_sd", "light SD"), ("space", "sky_area_frac", "sky share"),
    ("space", "distinct_wall_textures", "distinct wall textures"),
    ("combat", "monsters_hard", "UV monsters"), ("combat", "monster_hp_hard", "UV monster HP"),
    ("combat", "hp_density_hard", "UV HP density"), ("combat", "mean_monster_hp_hard", "mean monster HP"),
    ("combat", "share_heavy_hard", "heavy share"), ("combat", "share_hitscan_hard", "hitscan share"),
    ("combat", "ammo_ratio_ps_hard", "ammo ratio (pistol start)"),
    ("combat", "health_per_khp_hard", "health per 1000 HP"), ("combat", "armor_per_khp_hard", "armor per 1000 HP"),
    ("progression", "n_keys", "keys"), ("progression", "key_chain_depth", "key-chain depth"),
    ("progression", "crit_path_len", "critical path length"),
    ("progression", "optional_area_share", "optional area share"),
    ("progression", "cyclomatic_room", "room loops"), ("progression", "n_secrets", "secrets"),
    ("route", "route_min_health", "route min health"),
]
REACH = {"progression", "route"}


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def spearman(a, b):
    def rank(xs):
        order = sorted(range(len(xs)), key=xs.__getitem__)
        r = [0.0] * len(xs)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2
            i = j + 1
        return r
    if len(a) < 5:
        return None
    ra, rb = rank(a), rank(b)
    ma, mb = statistics.fmean(ra), statistics.fmean(rb)
    num_ = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return num_ / den if den else None


def fmt(v):
    if v is None:
        return "–"
    return f"{v:.3g}" if abs(v) < 1000 else f"{v:,.0f}"


def main():
    with open(os.path.join(METRICS, "flavors.csv"), newline="") as f:
        flavor_of = {r["set"]: r["flavor"] for r in csv.DictReader(f)}
    rows = defaultdict(dict)   # table -> {(set, wad, slot): row}
    for table in {t for t, _, _ in KEY}:
        for path in [os.path.join(METRICS, f"metrics_{table}.csv")] + \
                sorted(glob.glob(os.path.join(METRICS, "sets", "*", f"metrics_{table}.csv"))):
            with open(path, newline="") as f:
                for r in csv.DictReader(f):
                    rows[table][r["set"], r["wad"], r["slot"]] = r
    every = [r for t in rows.values() for r in t.values()]
    year_of = {r["set"]: int(r["year"]) for r in every}
    community = {r["set"] for r in every if r["official"] == "false"}
    groups = sorted({(r["game"], flavor_of.get(r["set"], "unassigned")) for r in every},
                    key=lambda g: (g[0], g[1] not in ("doom", "doom2"), g[1]))
    print("| metric | " + " | ".join(f"{g} {fl}" for g, fl in groups) + " | rho(year) DOOM | rho(year) DOOM II | agree |")
    print("|---|" + "---|" * len(groups) + "---|---|---|")
    for table, col, label in KEY:
        per_release = defaultdict(list)   # (game, flavor, set) -> [value]
        for r in rows[table].values():
            if table in REACH and r["progression_valid"] != "true":
                continue
            if table == "combat" and ("DEHACKED" in r["format_evidence"] or "deh_file" in r["format_evidence"]):
                continue
            if (x := num(r.get(col))) is not None:
                per_release[r["game"], flavor_of.get(r["set"], "unassigned"), r["set"]].append(x)
        cells = []
        for g in groups:
            meds = [statistics.median(v) for (gg, fl, _), v in per_release.items() if (gg, fl) == g]
            cells.append(f"{fmt(statistics.median(meds))} ({len(meds)})" if meds else "–")
        rhos = []
        for game in ("doom", "doom2"):
            pts = [(year_of[s], statistics.median(v)) for (gg, _, s), v in per_release.items()
                   if gg == game and s in community]
            rhos.append(spearman([p[0] for p in pts], [p[1] for p in pts]) if pts else None)
        signs = [0 if r is None or abs(r) < 0.1 else (1 if r > 0 else -1) for r in rhos]
        agree = "yes" if signs[0] == signs[1] and signs[0] != 0 else "flat" if signs == [0, 0] else "no"
        print(f"| {label} | " + " | ".join(cells) + f" | {fmt(rhos[0])} | {fmt(rhos[1])} | {agree} |")
    print("\nCells: median of release medians (releases); each official set counts as one release. "
          "rho(year): community releases only.")


if __name__ == "__main__":
    main()
