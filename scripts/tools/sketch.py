#!/usr/bin/env python3
"""Draw a design doc's plan sketch: the ```sketch block in
levels/designs/<module>.md becomes levels/designs/<module>.svg, a top-down
drawing in map units with a 64-unit grid, and a report of the plan's
geometry. Polygons, not a character grid, so angled, polygonal and curved
spaces are as easy to sketch as boxes, and the build copies the outlines.

    python3 scripts/tools/sketch.py levels/designs/<module>.md

The block holds one space per line, then marks:

    ```sketch
    # name     floor/ceil  tags        : outline (map units)
    yard       0/320       sky         : 0,0 1024,0 1024,640 768,896 0,896
    tower      96/256                  : regular(512, 448, 160, 8)
    moat       -48/320     liquid sky  : regular(512, 448, 288, 8)
    dock       24/160                  : chamfer(1024, 128, 1408, 512, 64)
    * 128,128 start
    * 512,448 yellow key
    ```

- outline: `x,y` pairs, or a Python expression over the loop helpers in
  levels/model.py (`rect`, `strip`, `regular`, `chamfer`, `arc`, `inset`):
  `regular(512, 448, 160, 8)`, `[(0, 0)] + arc(0, 0, 512, 0, 90, 6)`.
- tags: `liquid`, `sky`, `door`, `lift`, `secret` (colour and a note only).
- Later spaces are drawn over earlier ones: a space inside another is an
  island or pit there, and the builder needs it as a hole of the outer one.
- `* x,y text` marks a point: the start, keys, switches, secrets, triggers.

The report lists each space (area, bounding box), spaces whose outlines cross
(an error for the builder: sectors meet only along shared edges), islands,
marks outside every space, and the plan's off-axis share of line length and
axis-aligned share of spaces >= 128x128, measured as in
scripts/metrics/space_metrics.py. Exits 1 if outlines cross.
"""
import math
import os
import re
import sys
from html import escape

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from levels import model  # noqa: E402
from levels.model import area2, edges, point_in_loop, segments_cross  # noqa: E402

HELPERS = {n: getattr(model, n) for n in ("rect", "strip", "regular", "chamfer", "arc", "inset")}
TAG_FILL = {"liquid": "#7ccf4a", "door": "#a0703c", "lift": "#e8c547", "secret": "#c9a0f0"}
PAIR = re.compile(r"^\s*(-?\d+)\s*,\s*(-?\d+)\s*$")
MAX_PX = 1400


def parse(text):
    m = re.search(r"```sketch\n(.*?)```", text, re.S)
    if not m:
        sys.exit("no ```sketch block")
    spaces, marks, errors = [], [], []
    for n, raw in enumerate(m.group(1).splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("*"):
            pm = re.match(r"\*\s*(-?\d+)\s*,\s*(-?\d+)\s*(.*)", line)
            if not pm:
                errors.append(f"line {n}: mark is `* x,y text`")
                continue
            marks.append(((int(pm[1]), int(pm[2])), pm[3].strip()))
            continue
        head, _, outline = line.partition(":")
        parts = head.split()
        if len(parts) < 2 or "/" not in parts[1]:
            errors.append(f"line {n}: space is `name floor/ceil [tags] : outline`")
            continue
        name, hts, tags = parts[0], parts[1], parts[2:]
        floor, ceil = (int(v) for v in hts.split("/"))
        pairs = outline.split()
        if pairs and all(PAIR.match(p) for p in pairs):
            loop = [tuple(int(v) for v in p.split(",")) for p in pairs]
        else:
            try:
                loop = eval(outline, {"__builtins__": {}}, dict(HELPERS))   # noqa: S307 - our own docs
            except Exception as e:
                errors.append(f"line {n}: {name}: {type(e).__name__}: {e}")
                continue
            loop = [(round(x), round(y)) for x, y in loop]
        if len(loop) < 3:
            errors.append(f"line {n}: {name}: fewer than 3 points")
            continue
        spaces.append({"name": name, "floor": floor, "ceil": ceil, "tags": tags, "loop": loop})
    return spaces, marks, errors


def inside(a, b):
    """Loop a lies inside loop b (they may share edges)."""
    pts = [((u[0] + v[0]) / 2, (u[1] + v[1]) / 2) for u, v in edges(a)] + list(a)
    probe = [p for p in pts if not any(_on(p, u, v) for u, v in edges(b))]
    return bool(probe) and all(point_in_loop(p, b) for p in probe)


def _on(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    if abs((bx - ax) * (py - ay) - (by - ay) * (px - ax)) > 1e-6:
        return False
    return min(ax, bx) <= px <= max(ax, bx) and min(ay, by) <= py <= max(ay, by)


def report(spaces, marks):
    out, bad = [], False
    for s in spaces:
        xs, ys = [x for x, _ in s["loop"]], [y for _, y in s["loop"]]
        s["area"] = abs(area2(s["loop"])) / 2
        out.append(f"{s['name']:<16} {s['floor']:>5}/{s['ceil']:<5} {' '.join(s['tags']):<12} "
                   f"{s['area'] / 1000:>7.1f}k  ({min(xs)},{min(ys)})-({max(xs)},{max(ys)})")
    for i, a in enumerate(spaces):
        ea = list(edges(a["loop"]))
        for p, q in ea:
            for r, t in ea:
                if (p, q) < (r, t) and segments_cross(p, q, r, t):
                    out.append(f"ERROR {a['name']}: its outline crosses itself at {p}-{q} / {r}-{t}")
                    bad = True
        for b in spaces[i + 1:]:
            hit = next(((p, q, r, t) for p, q in ea for r, t in edges(b["loop"]) if segments_cross(p, q, r, t)),
                       None)
            if hit:
                out.append(f"ERROR {a['name']} and {b['name']} cross at {hit[0]}-{hit[1]} / {hit[2]}-{hit[3]}: "
                           "sectors may only meet along shared edges")
                bad = True
    for i, b in enumerate(spaces):   # each island's smallest container: the space it is a hole of
        around = [(a["area"], j, a) for j, a in enumerate(spaces) if a is not b and inside(b["loop"], a["loop"])]
        if around:
            _, j, a = min(around, key=lambda t: t[:2])
            out.append(f"island: {b['name']} inside {a['name']} (a hole of {a['name']} in the build)"
                       + (", but listed first, so drawn under it" if i < j else ""))
    for p, text in marks:
        if not any(point_in_loop(p, s["loop"]) for s in spaces):
            out.append(f"mark outside every space: {p} {text}")
    seen, total, off = set(), 0.0, 0.0
    for s in spaces:
        for a, b in edges(s["loop"]):
            e = (a, b) if a <= b else (b, a)
            if e in seen:
                continue
            seen.add(e)
            L = math.dist(a, b)
            total += L
            off += L * (a[0] != b[0] and a[1] != b[1])
    big = [s for s in spaces if s["area"] >= 128 * 128 and "door" not in s["tags"]]
    axis = [s for s in big if all(a[0] == b[0] or a[1] == b[1] for a, b in edges(s["loop"]))]
    out.append(f"off-axis share of line length {off / total:.2f}" if total else "no lines")
    out.append(f"axis-aligned spaces >= 128x128: {len(axis)}/{len(big)}"
               + (f" ({', '.join(s['name'] for s in axis)})" if axis else ""))
    return out, bad


def label_at(loop, over=()):
    """A point inside loop and outside the loops drawn over it, near its
    bounding-box centre."""
    xs, ys = [x for x, _ in loop], [y for _, y in loop]
    c = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)

    def free(p):
        return point_in_loop(p, loop) and not any(point_in_loop(p, o) for o in over)
    if free(c):
        return c
    grid = [(x, y) for x in range(min(xs) + 8, max(xs), 16) for y in range(min(ys) + 8, max(ys), 16) if free((x, y))]
    return min(grid, key=lambda p: math.dist(p, c), default=c)


def svg(spaces, marks, title):
    pts = [p for s in spaces for p in s["loop"]] + [p for p, _ in marks]
    minx, maxx = min(x for x, _ in pts) - 128, max(x for x, _ in pts) + 128
    miny, maxy = min(y for _, y in pts) - 128, max(y for _, y in pts) + 128
    k = min(MAX_PX / (maxx - minx), MAX_PX / (maxy - miny), 1.0)
    w, h = (maxx - minx) * k, (maxy - miny) * k

    def xy(p):
        return f"{(p[0] - minx) * k:.1f},{(maxy - p[1]) * k:.1f}"

    floors = [s["floor"] for s in spaces]
    lo, span = min(floors), (max(floors) - min(floors)) or 1
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h + 24:.0f}" '
           'font-family="sans-serif">', '<rect width="100%" height="100%" fill="#fbfbf7"/>']
    for g in range(math.ceil(minx / 64) * 64, maxx, 64):
        major = g % 256 == 0
        out.append(f'<line x1="{(g - minx) * k:.1f}" y1="0" x2="{(g - minx) * k:.1f}" y2="{h:.1f}" '
                   f'stroke="{"#c8c8c0" if major else "#e8e8e0"}" stroke-width="{1 if major else 0.5}"/>')
        if g % 512 == 0:
            out.append(f'<text x="{(g - minx) * k + 2:.1f}" y="10" font-size="9" fill="#999">{g}</text>')
    for g in range(math.ceil(miny / 64) * 64, maxy, 64):
        major = g % 256 == 0
        out.append(f'<line x1="0" y1="{(maxy - g) * k:.1f}" x2="{w:.1f}" y2="{(maxy - g) * k:.1f}" '
                   f'stroke="{"#c8c8c0" if major else "#e8e8e0"}" stroke-width="{1 if major else 0.5}"/>')
        if g % 512 == 0:
            out.append(f'<text x="2" y="{(maxy - g) * k - 2:.1f}" font-size="9" fill="#999">{g}</text>')
    for s in spaces:
        fill = next((TAG_FILL[t] for t in s["tags"] if t in TAG_FILL), None)
        if fill is None:
            v = int(150 + 90 * (s["floor"] - lo) / span)
            fill = f"rgb({v},{v},{v})"
        dash = ' stroke-dasharray="6 3"' if "sky" in s["tags"] else ""
        out.append(f'<polygon points="{" ".join(xy(p) for p in s["loop"])}" fill="{fill}" stroke="#111" '
                   f'stroke-width="1.4"{dash}><title>{escape(s["name"])}</title></polygon>')
    for i, s in enumerate(spaces):
        p = label_at(s["loop"], [o["loop"] for o in spaces[i + 1:]])
        x, y = (float(v) for v in xy(p).split(","))
        out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="11" text-anchor="middle" fill="#222">'
                   f'{escape(s["name"])} {s["floor"]}/{s["ceil"]}</text>')
    for p, text in marks:
        x, y = (float(v) for v in xy(p).split(","))
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#d0201a"/>'
                   f'<text x="{x + 6:.1f}" y="{y + 4:.1f}" font-size="11" fill="#d0201a">{escape(text)}</text>')
    out.append(f'<text x="8" y="{h + 16:.0f}" font-size="11" fill="#222">{escape(title)}: grid 64, '
               'heavier lines every 256, labels every 512; grey = floor (lighter is higher), dashed = sky, '
               'green = liquid, brown = door, yellow = lift, purple = secret</text>')
    out.append("</svg>")
    return "\n".join(out)


def main(argv):
    if len(argv) != 1:
        sys.exit(__doc__)
    path = argv[0]
    spaces, marks, errors = parse(open(path).read())
    for e in errors:
        print("ERROR", e)
    if not spaces:
        sys.exit(1)
    lines, bad = report(spaces, marks)
    print("\n".join(lines))
    out = os.path.splitext(path)[0] + ".svg"
    with open(out, "w") as f:
        f.write(svg(spaces, marks, os.path.basename(os.path.splitext(path)[0])))
    print(f"wrote {out}")
    sys.exit(1 if bad or errors else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
