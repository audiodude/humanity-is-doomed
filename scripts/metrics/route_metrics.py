"""Balance along the critical path (levels/balance.py) of the id maps, at UV:
the resource curves' low points, the long-range hitscan peak, the health
column's low point and the starts under fire. Writes
data/metrics/metrics_route.csv; the thresholds in levels/balance.py and the
quartiles in levels/measure.py come from it.

Run from the repo root:
    python3 scripts/metrics/route_metrics.py            # every map of both IWADs
    python3 scripts/metrics/route_metrics.py MAP06      # print one map's report
    python3 scripts/metrics/route_metrics.py --set tnt  # an official set (doomwad.SETS)
"""
import csv
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import doomwad as dw  # noqa: E402  (also puts the repo root on sys.path)
import progression_metrics as pm  # noqa: E402
from levels.balance import health_rate, report, route_balance  # noqa: E402
from levels.reach import solve  # noqa: E402
from levels.wad import iwad_textures  # noqa: E402

OUT = os.path.join(dw.METRICS, "metrics_route.csv")


def analyse_map(m, textures):
    md, res = solve(m, textures)
    _, dbg = pm.analyse(md, res)
    bal = route_balance(m, md, res, dbg["legs"])
    health = [leg.detour[2] for leg in bal.legs]
    row = dict(map=m.slot, game=m.game, legs=len(bal.legs), **bal.summary,
               route_min_health=round(min(health)) if health else "",
               route_start_fire=len(bal.start_fire))
    rate = health_rate(bal)
    row["route_health_per_khp"] = round(1000 * rate, 2) if rate is not None else ""
    return row, bal


def main(argv):
    maps, out, argv = dw.select(argv, OUT)
    textures = {}
    for key in {(m.iwad, m.pwads) for m in maps}:
        tx = iwad_textures(*key)[0]
        textures[key] = (tx, next(iter(tx.values()))[1])
    rows = []
    for m in maps:
        if argv and m.slot not in argv:
            continue
        row, bal = analyse_map(m, textures[m.iwad, m.pwads])
        if argv:
            lines, warnings = report(bal, m.game)
            print("\n".join(lines + [f"warning: {w}" for w in warnings]))
            print(row)
            continue
        rows.append(dw.with_meta(row, m))
        print(m.wad, m.slot, row.get("route_min_detour_ratio"), row.get("route_max_long_hitscan"), file=sys.stderr)
    if argv:
        return
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="") as fh:
        # A map whose exit the model can't reach has no route columns: blank them.
        w = csv.DictWriter(fh, fieldnames=list(dict.fromkeys(k for r in sorted(rows, key=len, reverse=True)
                                                             for k in r)), restval="")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out} ({len(rows)} rows)")
    for game in sorted({r["game"] for r in rows}):
        for k in ("route_min_detour_ratio", "route_min_thorough_share", "route_max_long_hitscan", "route_min_health",
                  "route_health_per_khp"):
            v = sorted(r[k] for r in rows if r["game"] == game and isinstance(r.get(k), (int, float)))
            if len(v) >= 4:
                q = statistics.quantiles(v, n=10, method="exclusive")
                print(f"{game} {k}: p10 {q[0]:.4g}  quartiles {statistics.quantiles(v, n=4, method='exclusive')}  "
                      f"p90 {q[-1]:.4g}")
        fire = sum(1 for r in rows if r["game"] == game and r["route_start_fire"])
        print(game, "maps with a start under fire:", fire)


if __name__ == "__main__":
    main(sys.argv[1:])
