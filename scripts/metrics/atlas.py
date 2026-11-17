#!/usr/bin/env python3
"""Geometry atlas: what id's and well-rated community maps do with space, read
off their top-down previews by an agent, so `doom-design` can draw shapes
from real maps instead of boxes.

    python3 scripts/metrics/atlas.py prep [--min-rating 4.25]

`prep` picks the maps (every decompiled map of DOOM, DOOM II, TNT, Plutonia and
the Master Levels, plus community maps from releases rated at least
--min-rating), and for each writes to research/atlas/maps/:
  <key>.png  the map's preview (research/maps/, from map_svgs.py) without
             monsters and items (the start and keys stay), at most 2000 px on a side
  <key>.txt  facts and the pixel -> map-unit transform, then its sectors,
             largest first, with heights, bounding box, vertex count and how
             many edges are off the axes
and research/atlas/manifest.jsonl, one row per map. <key> is the preview's
path under research/maps/ without .svg, slashes as "__" (doom2__MAP11).
Run map_svgs.py first; this reads data/metrics/decompile_status.csv and the
decompiled modules in levels/imported/.

The entries themselves (research/atlas/entries/<key>.json) are written by
agents reading each map's .png and .txt, prompted by atlas_prompt.md.
"""
import argparse
import csv
import importlib
import json
import math
import os
import re
import subprocess
import sys
from multiprocessing import Pool

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from levels.model import area2, edges  # noqa: E402

MAPS = os.path.join(ROOT, "research", "maps")
ATLAS = os.path.join(ROOT, "research", "atlas")
METRICS = os.path.join(ROOT, "data", "metrics")
ID_SETS = ("doom", "doom2", "tnt", "plutonia", "master")
SCALE, PAD = 0.4, 96   # levels/preview.py write_svg defaults
MAX_PX = 2000
MIN_AREA = 64 * 64     # sectors listed in the summary
MAX_SECTORS = 150


def off_axis(a, b):
    return a[0] != b[0] and a[1] != b[1]


def meta():
    """{(set, wad, slot): metrics row} for rating, year and authors."""
    out = {}
    paths = [os.path.join(METRICS, "metrics_space.csv")] + [
        os.path.join(METRICS, "sets", s, "metrics_space.csv") for s in os.listdir(os.path.join(METRICS, "sets"))]
    for p in paths:
        if os.path.exists(p):
            for r in csv.DictReader(open(p, newline="")):
                out[r["set"], r["wad"], r["slot"]] = r
    return out


def ratings():
    """{release: rating} from the idgames manifest."""
    p = os.path.join(ROOT, "research", "sources", "idgames", "manifest.csv")
    return {r["filename"].lower().rsplit(".", 1)[0]: float(r["rating"]) for r in csv.DictReader(open(p))}


def select(min_rating):
    rel, md = ratings(), meta()
    picked = []
    for r in csv.DictReader(open(os.path.join(METRICS, "decompile_status.csv"), newline="")):
        if r["decompile"] not in ("ok", "repaired") or not r["svg"] or not r["module"]:
            continue
        official = r["set"] in ID_SETS
        if not official and rel.get(r["set"], 0) < min_rating:
            continue
        m = md.get((r["set"], r["wad"], r["slot"]), {})
        picked.append({
            "key": r["svg"][:-4].replace("/", "__"), "set": r["set"], "wad": r["wad"], "slot": r["slot"],
            "svg": r["svg"], "module": r["module"], "official": official,
            "rating": m.get("rating") or (str(rel[r["set"]]) if r["set"] in rel else ""),
            "rating_scope": m.get("rating_scope") or ("per-WAD" if r["set"] in rel else ""),
            "year": m.get("year", ""), "authors": m.get("authors", ""),
        })
    return picked


def prep_one(row):
    key = row["key"]
    png, txt = (os.path.join(ATLAS, "maps", key + ext) for ext in (".png", ".txt"))
    mod = importlib.import_module("levels." + row["module"])
    title = (mod.__doc__ or "").strip().splitlines()[0] if mod.__doc__ else row["slot"]
    if row["set"] in ("tnt", "plutonia"):   # the decompiler gives IWAD maps DOOM II's titles by slot
        title = f"{row['set'].upper()} {row['slot']}"
    secs = [s for s in mod.SECTORS if s.loops]
    pts = [p for s in secs for loop in s.outer_loops() for p in loop]
    minx, maxy = min(x for x, _ in pts) - PAD, max(y for _, y in pts) + PAD
    maxx, miny = max(x for x, _ in pts) + PAD, min(y for _, y in pts) - PAD
    w, h = (maxx - minx) * SCALE, (maxy - miny) * SCALE + 40
    zoom = min(MAX_PX / max(w, h), 2.0)
    k = 1 / (SCALE * zoom)   # map units per pixel

    # Preview without monsters and items (one element per line in write_svg's
    # output); the start (green) and keys (rects) stay.
    with open(os.path.join(MAPS, row["svg"])) as f:
        svg = "".join(ln for ln in f if not (ln.startswith("<circle") and 'fill="#1a9e3a"' not in ln))
    subprocess.run(["rsvg-convert", "-z", f"{zoom:.4f}", "-b", "#fbfbf7", "-o", png],
                   input=svg.encode(), check=True)

    seen, total, off, n_edges = set(), 0.0, 0.0, 0
    rows, box_big, big = [], 0, 0
    for s in secs:
        outers = s.outer_loops()
        holes = [lp for lp in s.loops if lp not in outers]
        area = (sum(abs(area2(lp)) for lp in outers) - sum(abs(area2(lp)) for lp in holes + list(s.pillars))) / 2
        es = [e for lp in s.loops + list(s.pillars) for e in edges(lp)]
        n_off = sum(off_axis(a, b) for a, b in es)
        for a, b in es:
            e = (a, b) if a <= b else (b, a)
            if e not in seen:
                seen.add(e)
                L = math.dist(a, b)
                total += L
                off += L * off_axis(a, b)
                n_edges += 1
        if area >= 128 * 128:
            big += 1
            box_big += n_off == 0
        if area >= MIN_AREA:
            xs, ys = [x for lp in outers for x, _ in lp], [y for lp in outers for _, y in lp]
            rows.append((area, f"{s.name:<14} {s.floor:>5}/{s.ceil:<5} {s.light:>3}  "
                               f"({min(xs)},{min(ys)})-({max(xs)},{max(ys)})  {area / 1000:>7.1f}k  "
                               f"{len(es):>3}v {n_off:>3}off  {len(holes)}h {len(s.pillars)}p  {s.ftex}"))
    rows.sort(key=lambda t: -t[0])
    floors = sorted({s.floor for s in secs})
    with open(txt, "w") as f:
        f.write(f"{title}\n{row['set']} {row['wad']} {row['slot']}, {row['year'] or '?'}, "
                f"by {row['authors'] or '?'}; rating {row['rating'] or '?'} ({row['rating_scope'] or 'none'})\n")
        f.write(f"Module: levels/{row['module'].replace('.', '/')}.py; preview: research/maps/{row['svg']}\n")
        f.write(f"Image {os.path.basename(png)}: map x = {minx} + px * {k:.3f}, map y = {maxy} - py * {k:.3f}\n")
        f.write(f"Size {maxx - minx - 2 * PAD} x {maxy - miny - 2 * PAD}; {len(secs)} sectors; "
                f"floors {floors[0]}..{floors[-1]} ({len(floors)} distinct)\n")
        f.write(f"Off-axis share of wall length {off / total:.2f}; sectors >= 128^2 with every edge on an axis "
                f"{box_big}/{big}\n\n")
        f.write(f"Sectors >= {MIN_AREA} units^2, largest first (max {MAX_SECTORS}): "
                "name floor/ceil light bbox area vertices off-axis-edges holes pillars floor-flat\n")
        f.write("\n".join(r for _, r in rows[:MAX_SECTORS]) + "\n")
    return {**row, "title": title, "off_axis_share": round(off / total, 4),
            "all_axis_sectors": round(box_big / big, 4) if big else None}


def prep(min_rating):
    os.makedirs(os.path.join(ATLAS, "maps"), exist_ok=True)
    rows = select(min_rating)
    out = []
    with Pool() as pool:
        for i, r in enumerate(pool.imap(_safe, rows), 1):
            if isinstance(r, str):
                print(r, file=sys.stderr)
            else:
                out.append(r)
            if i % 100 == 0:
                print(f"{i}/{len(rows)}", file=sys.stderr)
    with open(os.path.join(ATLAS, "manifest.jsonl"), "w") as f:
        f.writelines(json.dumps(r) + "\n" for r in out)
    print(f"{len(out)} maps ({sum(r['official'] for r in out)} official) -> {ATLAS}")


def _safe(row):
    try:
        return prep_one(row)
    except Exception as e:   # one bad module shouldn't stop the batch
        return f"{row['key']}: {type(e).__name__}: {e}"


def entries():
    """[(manifest row, entry)] for every map with an atlas entry."""
    with open(os.path.join(ATLAS, "manifest.jsonl")) as f:
        man = {r["key"]: r for r in map(json.loads, f)}
    out, d = [], os.path.join(ATLAS, "entries")
    for name in sorted(os.listdir(d)):
        if name.endswith(".json") and name[:-5] in man:
            with open(os.path.join(d, name)) as f:
                out.append((man[name[:-5]], json.load(f)))
    return out


def _rating(row):
    try:
        return float(row["rating"])
    except ValueError:
        return -9.0


def find(words, move, plan, source, n):
    """Print the moves matching the query: official maps first, then
    community maps, each by rating, with what to look at."""
    words = [w.lower() for w in words]
    hits = []
    for row, e in entries():
        if source != "all" and row["official"] != (source == "official"):
            continue
        if plan and e.get("plan") != plan:
            continue
        if plan and not move and not words:   # the map itself, not each of its moves
            hits.append((not row["official"], -_rating(row), row["key"], row, e, None))
            continue
        for mv in e.get("moves", []):
            text = " ".join(str(mv.get(k, "")) for k in ("name", "how", "effect")).lower()
            if (move and mv.get("name") != move) or not all(w in text for w in words):
                continue
            hits.append((not row["official"], -_rating(row), row["key"], row, e, mv))
    hits.sort(key=lambda h: h[:3])
    for *_, row, e, mv in hits[:n]:
        print(f"{row['key']}  {row['title']} ({row['year'] or '?'}, {row['authors'] or '?'}; "
              f"rating {row['rating'] or '?'} {row['rating_scope']})  plan {e.get('plan')}, grid {e.get('grid')}")
        print(f"  shape: {e.get('shape')}")
        if mv:
            print(f"  {mv.get('name')}: {', '.join(mv.get('sectors', []))} at {tuple(mv.get('at', ()))} "
                  f"{mv.get('size', '')}")
            print(f"  how: {mv.get('how')}\n  effect: {mv.get('effect')}")
        else:
            print(f"  lesson: {e.get('lesson')}")
        print(f"  look: research/atlas/maps/{row['key']}.png (transform in its .txt); "
              f"module levels/{row['module'].replace('.', '/')}.py\n")
    print(f"{len(hits)} matches" + (f", first {n} shown" if len(hits) > n else ""))


def stats():
    """Markdown tables: how many maps make each move, official and
    community, and how plans and grids are spread."""
    from collections import Counter
    rows = entries()
    groups = {"official": [r for r in rows if r[0]["official"]],
              "community": [r for r in rows if not r[0]["official"]]}
    print(f"{len(rows)} entries: {len(groups['official'])} official, {len(groups['community'])} community\n")
    for title, field in (("move", None), ("plan", "plan"), ("grid", "grid")):
        counts = {g: Counter() for g in groups}
        for g, rs in groups.items():
            for _, e in rs:
                counts[g].update({mv.get("name") for mv in e.get("moves", [])} if field is None else [e.get(field)])
        names = sorted(set().union(*counts.values()), key=lambda k: -sum(c[k] for c in counts.values()))
        print(f"| {title} | official maps | community maps |\n|---|---|---|")
        for k in names:
            if sum(c[k] for c in counts.values()) >= (3 if field is None else 1):
                print(f"| {k} | " + " | ".join(f"{counts[g][k] / max(1, len(rs)):.0%} ({counts[g][k]})"
                                             for g, rs in groups.items()) + " |")
        print()


def check():
    """Keys with no entry or a bad one (unparseable, missing fields, sectors
    not in the map's module, `at` outside the map), one per line; the count
    of bad ones."""
    with open(os.path.join(ATLAS, "manifest.jsonl")) as f:
        man = [json.loads(ln) for ln in f]
    bad = 0
    for row in man:
        k = row["key"]
        problems = []
        try:
            with open(os.path.join(ATLAS, "entries", k + ".json")) as f:
                e = json.load(f)
        except FileNotFoundError:
            problems.append("missing")
        except ValueError as err:
            problems.append(f"unparseable: {err}")
        else:
            with open(os.path.join(ATLAS, "maps", k + ".txt")) as f:
                txt = f.read()
            with open(os.path.join(ROOT, "levels", row["module"].replace(".", "/") + ".py")) as f:
                names = set(re.findall(r'\b(?:Sector|lift|door|window|pedestal)\("([^"]+)"', f.read()))
            m = re.search(r"map x = (-?\d+) \+ px \* [\d.]+, map y = (-?\d+) - py", txt)
            size = re.search(r"^Size (\d+) x (\d+);", txt, re.M)
            x0, y1, w, h = int(m[1]) + PAD, int(m[2]) - PAD, int(size[1]), int(size[2])
            problems += [f"no {f_}" for f_ in ("shape", "plan", "grid", "moves", "lesson") if not e.get(f_)]
            for mv in e.get("moves", []):
                if unknown := [s for s in mv.get("sectors", []) if s not in names]:
                    problems.append(f"{mv.get('name')}: unknown sectors {unknown}")
                at = mv.get("at") or [None, None]
                if not (len(at) == 2 and all(isinstance(v, (int, float)) for v in at)
                        and x0 - 64 <= at[0] <= x0 + w + 64 and y1 - h - 64 <= at[1] <= y1 + 64):
                    problems.append(f"{mv.get('name')}: at {at} outside the map")
        if problems:
            bad += 1
            print(f"{k}: {'; '.join(problems)}")
    print(f"{len(man) - bad}/{len(man)} entries ok")
    return bad


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prep", help="pick the maps and write their images and summaries")
    p.add_argument("--min-rating", type=float, default=4.25)
    p = sub.add_parser("find", help="moves matching words (in name, how or effect), a move name, or a plan")
    p.add_argument("words", nargs="*")
    p.add_argument("--move", help="exact move name, e.g. chamfer")
    p.add_argument("--plan", help="maps with this plan, e.g. descent")
    p.add_argument("--source", choices=("all", "official", "community"), default="all")
    p.add_argument("-n", type=int, default=8)
    sub.add_parser("stats", help="move, plan and grid counts as markdown")
    sub.add_parser("check", help="maps with a missing or bad entry; exits 1 if any")
    a = ap.parse_args(argv)
    if a.cmd == "prep":
        prep(a.min_rating)
    elif a.cmd == "find":
        find(a.words, a.move, a.plan, a.source, a.n)
    elif a.cmd == "stats":
        stats()
    elif check():
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
