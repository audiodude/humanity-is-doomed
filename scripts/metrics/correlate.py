"""Correlate per-map metrics with community reception.

Joins research/data/reception.csv (column `score`, -2..+2) with every
research/data/metrics_*.csv on `map`, then for each numeric metric computes
Spearman's rho against the score:
  all      all 68 maps
  doom     E1M1-E4M9 only
  doom2    MAP01-MAP32 only
  within   ranks taken within each game, then pooled (removes the
           DOOM-vs-DOOM II difference in both score and metric)
plus a two-sided permutation p-value for `within` (5000 shuffles of the
scores inside each game, seeded) and a Benjamini-Hochberg q-value across all
metrics. Two robustness columns repeat `within` with ranks taken inside each
episode (DOOM II split MAP01-11 / MAP12-20 / MAP21-32), and with the
arena/joke maps in ARENA_MAPS left out. Also prints mean reception per
designer from designers.csv.

Run from the repo root: python3 scripts/metrics/correlate.py
Writes research/data/correlations.csv and prints the strongest rows.
"""
import csv
import glob
import math
import os
import random
from collections import defaultdict

DATA = os.path.join(os.path.dirname(__file__), "..", "..", "research", "data")
PERMUTATIONS = 5000
# Single-arena boss fights and joke maps, whose geometry is unlike a normal level.
ARENA_MAPS = {"E2M8", "E3M8", "E2M9", "MAP07", "MAP30", "MAP31", "MAP32"}


def episode(slot):
    if slot.startswith("E"):
        return slot[:2]
    n = int(slot[3:])
    return "D2a" if n <= 11 else "D2b" if n <= 20 else "D2c"


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def num(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a))
    sb = math.sqrt(sum((y - mb) ** 2 for y in b))
    if sa == 0 or sb == 0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)


def spearman(a, b):
    return pearson(ranks(a), ranks(b)) if len(a) >= 5 else None


def within_ranks(values, games):
    """Ranks normalised to 0..1 inside each game."""
    out = [0.0] * len(values)
    for g in set(games):
        idx = [i for i, gg in enumerate(games) if gg == g]
        r = ranks([values[i] for i in idx])
        for i, rr in zip(idx, r):
            out[i] = (rr - 1) / max(1, len(idx) - 1)
    return out


def bh(pvals):
    """Benjamini-Hochberg q-values (None passes through)."""
    idx = sorted((p, i) for i, p in enumerate(pvals) if p is not None)
    q = [None] * len(pvals)
    m, prev = len(idx), 1.0
    for rank in range(m, 0, -1):
        p, i = idx[rank - 1]
        prev = min(prev, p * m / rank)
        q[i] = prev
    return q


def main():
    rec = {r["map"]: r for r in read_csv(os.path.join(DATA, "reception.csv"))}
    metrics = defaultdict(dict)  # map -> {column: value}
    sources = {}
    for path in sorted(glob.glob(os.path.join(DATA, "metrics_*.csv"))):
        name = os.path.basename(path)[8:-4]
        for row in read_csv(path):
            for k, v in row.items():
                if k == "map":
                    continue
                col = f"{name}.{k}"
                sources[col] = name
                metrics[row["map"]][col] = v

    rng = random.Random(1993)
    results = []
    for col in sources:
        maps = [m for m in rec if num(rec[m]["score"]) is not None and num(metrics[m].get(col)) is not None]
        if len(maps) < 20:
            continue
        x = [num(metrics[m][col]) for m in maps]
        y = [num(rec[m]["score"]) for m in maps]
        games = ["doom2" if m.startswith("MAP") else "doom" for m in maps]
        if len(set(x)) < 3:
            continue
        sub = {g: [i for i, gg in enumerate(games) if gg == g] for g in ("doom", "doom2")}
        xw, yw = within_ranks(x, games), within_ranks(y, games)
        rho_w = pearson(xw, yw)
        p = None
        if rho_w is not None:
            hits = 0
            for _ in range(PERMUTATIONS):
                ys = yw[:]
                for idx in sub.values():
                    vals = [ys[i] for i in idx]
                    rng.shuffle(vals)
                    for i, v in zip(idx, vals):
                        ys[i] = v
                r = pearson(xw, ys)
                if r is not None and abs(r) >= abs(rho_w) - 1e-12:
                    hits += 1
            p = (hits + 1) / (PERMUTATIONS + 1)
        # Robustness: ranks within episode (DOOM II split into its three
        # story stretches), and within game with the arena/joke maps left out.
        eps = [episode(m) for m in maps]
        rho_ep = pearson(within_ranks(x, eps), within_ranks(y, eps))
        keep = [i for i, m in enumerate(maps) if m not in ARENA_MAPS]
        kx, ky, kg = [x[i] for i in keep], [y[i] for i in keep], [games[i] for i in keep]
        rho_ex = pearson(within_ranks(kx, kg), within_ranks(ky, kg))
        results.append({
            "metric": col, "n": len(maps),
            "rho_all": spearman(x, y),
            "rho_doom": spearman([x[i] for i in sub["doom"]], [y[i] for i in sub["doom"]]),
            "rho_doom2": spearman([x[i] for i in sub["doom2"]], [y[i] for i in sub["doom2"]]),
            "rho_within": rho_w, "p_within": p,
            "rho_within_episode": rho_ep, "rho_within_no_arenas": rho_ex,
        })
    for r, q in zip(results, bh([r["p_within"] for r in results])):
        r["q_within"] = q
    results.sort(key=lambda r: -abs(r["rho_within"] or 0))

    out = os.path.join(DATA, "correlations.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0]))
        w.writeheader()
        for r in results:
            w.writerow({k: (f"{v:.3f}" if isinstance(v, float) else v) for k, v in r.items()})
    print(f"wrote {out}: {len(results)} metrics\n")
    print("| metric | n | rho all | rho DOOM | rho DOOM II | rho within | p | q | within episode | no arenas |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    fmt = lambda v: "" if v is None else f"{v:+.2f}"  # noqa: E731
    for r in results[:60]:
        print(f"| {r['metric']} | {r['n']} | {fmt(r['rho_all'])} | {fmt(r['rho_doom'])} | {fmt(r['rho_doom2'])} "
              f"| {fmt(r['rho_within'])} | {r['p_within']:.4f} | {r['q_within']:.3f} "
              f"| {fmt(r['rho_within_episode'])} | {fmt(r['rho_within_no_arenas'])} |")

    dpath = os.path.join(DATA, "designers.csv")
    if os.path.exists(dpath):
        by = defaultdict(list)
        for row in read_csv(dpath):
            s = num(rec.get(row["map"], {}).get("score"))
            if s is None:
                continue
            for d in row["designers"].split(";"):
                if d.strip():
                    by[d.strip()].append((s, row["map"]))
        print("\n| designer | maps | mean score | maps |\n|---|---|---|---|")
        for d, v in sorted(by.items(), key=lambda kv: -sum(s for s, _ in kv[1]) / len(kv[1])):
            print(f"| {d} | {len(v)} | {sum(s for s, _ in v) / len(v):+.2f} | {' '.join(m for _, m in v)} |")


if __name__ == "__main__":
    main()
