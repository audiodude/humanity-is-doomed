#!/usr/bin/env python3
"""Per-map geometry / space / aesthetic metrics for the 68 vanilla IWAD maps.

Operationalises Romero's rules 1-4 (texture change => height change, border
textures, texture alignment, light/space contrast), Doomkid's "skinny
hallways" and "symmetry" warnings, and The Level Design Book's room-size
scale. Writes research/data/metrics_space.csv (one row per map, E1M1..MAP32).

Run from the repo root (stdlib only, uses all cores, ~2 min on 16 cores):
    python3 scripts/metrics/space_metrics.py
    python3 scripts/metrics/space_metrics.py E1M1 MAP07  # print a subset, no CSV
    python3 scripts/metrics/space_metrics.py --summary   # markdown tables from the CSV
                                                         # + Doom Wiki mapdata check

Method notes (full definitions in research/facets/10-quant-space.md):
* Space is sampled on a G=8-unit grid whose cell centres sit on multiples of
  8 (Doom's construction grid). Each centre is assigned the sector found by
  a +x ray cast (same rule as levels.wadmap.Map.sector_of_point), row by
  row, with the scanline nudged up by 1/1024 so it never passes through a
  vertex.
* A sector is *walkable* if ceil-floor >= 56 or it is a door sector.
* A line is a *movement wall* if it is one-sided, flagged ML_BLOCKING, or a
  two-sided line where one side is not walkable, the opening is < 56 (doors
  exempt), or the floor step is > 24 (lift/platform sectors exempt). Ledges
  count as walls in both directions (a drop still bounds dodging room).
* Clearance = exact Euclidean distance from a walkable cell centre to the
  nearest movement-wall segment. Local width = diameter of the largest
  wall-free disk containing the cell ("local thickness"), computed by
  painting maximal disks (medial-axis cells) in descending radius order.
"""
import math
import multiprocessing as mp
import os
import re
import struct
import sys
from collections import Counter, defaultdict, deque

sys.path.insert(0, os.path.dirname(__file__))
from doomwad import (DAMAGE_SPECIALS, IWADS, LIGHT_SPECIALS, LINE_SPECIALS,  # noqa: E402
                     ML_BLOCKING, ML_DONTPEGBOTTOM, ML_DONTPEGTOP, SKY, load_all)
from levels.wad import iwad_textures, read_wad  # noqa: E402  (doomwad put repo root on sys.path)

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
OUT = os.path.join(ROOT, "research", "data", "metrics_space.csv")

G = 8            # raster cell size (map units); centres sit on multiples of G
EPS = 1 / 1024   # scanline nudge so no scanline passes through an (integer) vertex
BUCKET = 128     # spatial hash for wall segments
TOL = 1.0        # width tolerance for threshold tests (inclusive "<= T")
PLAYER_H, STEP = 56, 24
LARGE_SPACE = 1024 * 1024
ROOM_MAX_CHOKE = 128  # cells of local width <= this (hallways/doorways) split "spaces"
SYM_G = 32            # symmetry raster
VPERIOD = 128         # vanilla column drawing wraps texture rows at 128 (R_DrawColumn & 127)

# --- texture classes ------------------------------------------------------
# Romero rule 2 "border" textures. CORE = what Chubzdoomer names ("support,
# door track and light textures"); EXTENDED adds IWAD trims designed as edge
# pieces (key-colour door strips, panel/skin/brown edge pieces, pipes, METAL
# column, COMPSPAN computer divider, PLAT1 platform side).
BORDER_CORE = re.compile(r"^(SUPPORT\d|DOORTRAK|DOORSTOP|LITE.*|TEKLITE\d?)$")
BORDER_EXT = re.compile(
    r"^(SUPPORT\d|DOORTRAK|DOORSTOP|LITE.*|TEKLITE\d?|DOOR(BLU|RED|YEL)2?|"
    r"COMPSPAN|PANBORD\d|SKINEDGE|SKINBORD|BRNBIG[LR]|BRNSMAL[LR]|PIPE[0-9S]+|METAL|PLAT1)$")
# Animated liquid flats (Doom / Doom II).
LIQUID = re.compile(r"^(NUKAGE\d|FWATER\d|SWATER\d|LAVA\d|BLOOD\d|SLIME(0\d|1[0-2])|RROCK0[5-8])$")
DOOR_KINDS = {"door", "door_close"}
LIFT_KINDS = {"lift", "platform"}


# --- small stats helpers --------------------------------------------------
def quantile(xs, q):
    """Linear-interpolated quantile of an already sorted list."""
    if not xs:
        return float("nan")
    pos = (len(xs) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def wmean_sd(vals, wts):
    tw = sum(wts)
    if tw <= 0:
        return float("nan"), float("nan")
    mu = sum(v * w for v, w in zip(vals, wts)) / tw
    var = sum(w * (v - mu) ** 2 for v, w in zip(vals, wts)) / tw
    return mu, math.sqrt(var)


def entropy_bits(counter):
    tot = sum(counter.values())
    return -sum(c / tot * math.log2(c / tot) for c in counter.values() if c > 0) if tot else 0.0


# --- sector classes ---------------------------------------------------------
def sector_roles(m):
    """(door sectors, lift/platform sectors) from line specials."""
    doors, lifts = set(), set()
    for ln in m.lines:
        sp = LINE_SPECIALS.get(ln.special)
        if not sp:
            continue
        if sp.kind in DOOR_KINDS:
            if sp.trigger == "D":
                if ln.back >= 0:
                    doors.add(m.sides[ln.back].sector)
            else:
                doors.update(m.tagged(ln.tag))
        elif sp.kind in LIFT_KINDS:
            lifts.update(m.tagged(ln.tag))
    for i, s in enumerate(m.sectors):
        if s.special in (10, 14):   # timed door sectors
            doors.add(i)
    return doors, lifts


def line_class(m, ln, walkable, doors, lifts):
    """'wall' (movement boundary) or 'pass'."""
    if ln.back < 0 or ln.flags & ML_BLOCKING:
        return "wall"
    f, b = m.line_sectors(ln)
    if f == b:
        return "pass"
    if f not in walkable or b not in walkable:
        return "wall"
    sf, sb = m.sectors[f], m.sectors[b]
    if f in doors or b in doors:
        return "pass"
    if min(sf.ceil, sb.ceil) - max(sf.floor, sb.floor) < PLAYER_H:
        return "wall"
    if abs(sf.floor - sb.floor) > STEP and not (f in lifts or b in lifts):
        return "wall"
    return "pass"


# --- rasterisation -----------------------------------------------------------
class Grid:
    """Cell (i, j) has its centre at (ox + i*G, oy + j*G); ox, oy are
    multiples of G so centres land on Doom's 8/16/32/64 construction grid."""
    def __init__(self, m):
        x0, y0, x1, y1 = m.bbox
        self.ox = (math.floor(x0 / G) - 2) * G
        self.oy = (math.floor(y0 / G) - 2) * G
        self.w = (x1 - self.ox) // G + 3
        self.h = (y1 - self.oy) // G + 3

    def cx(self, i):
        return self.ox + i * G

    def cy(self, j):
        return self.oy + j * G

    def cell(self, x, y):
        i = round((x - self.ox) / G)
        j = round((y - self.oy) / G)
        if 0 <= i < self.w and 0 <= j < self.h:
            return i, j
        return None


def rasterise_sectors(m, grid):
    """rows[j][i] = sector index or -1 (void): per row, a +x ray from each
    centre takes the facing side of the nearest crossed line (the rule of
    levels.wadmap.Map.sector_of_point). The scanline is nudged up by EPS."""
    crossings = [[] for _ in range(grid.h)]
    for ln in m.lines:
        (x1, y1), (x2, y2) = m.verts[ln.v1], m.verts[ln.v2]
        if y1 == y2:
            continue
        f, b = m.line_sectors(ln)
        left = f if y2 < y1 else (b if b is not None else -1)
        j0 = max(0, (min(y1, y2) - grid.oy) // G)
        j1 = min(grid.h - 1, (max(y1, y2) - grid.oy) // G + 1)
        for j in range(j0, j1 + 1):
            y = grid.cy(j) + EPS
            if (y1 > y) == (y2 > y):
                continue
            crossings[j].append((x1 + (y - y1) * (x2 - x1) / (y2 - y1), left))
    rows = []
    for j in range(grid.h):
        row = [-1] * grid.w
        prev = 0
        for xi, left in sorted(crossings[j]):
            end = min(grid.w, max(0, math.floor((xi - grid.ox) / G) + 1))   # centres with x <= xi
            if end > prev:
                row[prev:end] = [left] * (end - prev)
                prev = end
        rows.append(row)
    return rows


def clearance_field(grid, free, segs):
    """Exact distance from each free cell centre to the nearest wall segment.
    free: list of (i, j). Returns dict (i, j) -> distance."""
    buckets = defaultdict(list)
    segdata = []
    for k, (x1, y1, x2, y2) in enumerate(segs):
        dx, dy = x2 - x1, y2 - y1
        segdata.append((x1, y1, dx, dy, dx * dx + dy * dy or 1.0,
                        min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)))
        for bx in range(math.floor(min(x1, x2) / BUCKET), math.floor(max(x1, x2) / BUCKET) + 1):
            for by in range(math.floor(min(y1, y2) / BUCKET), math.floor(max(y1, y2) / BUCKET) + 1):
                buckets[(bx, by)].append(k)
    if buckets:
        bxs = [b[0] for b in buckets]
        bys = [b[1] for b in buckets]
        kmax = max(max(bxs) - min(bxs), max(bys) - min(bys)) + 2
    else:
        kmax = 1
    by_bucket = defaultdict(list)
    for i, j in free:
        x, y = grid.cx(i), grid.cy(j)
        by_bucket[(math.floor(x / BUCKET), math.floor(y / BUCKET))].append((i, j, x, y))
    out = {}
    for (bx, by), cells in by_bucket.items():
        rx0, ry0 = bx * BUCKET, by * BUCKET
        rx1, ry1 = rx0 + BUCKET, ry0 + BUCKET
        pending = cells
        k = 1
        while pending:
            cand = set()
            for ax in range(bx - k, bx + k + 1):
                for ay in range(by - k, by + k + 1):
                    cand.update(buckets.get((ax, ay), ()))
            ordered = []
            for s in cand:
                d = segdata[s]
                gx = max(0.0, d[5] - rx1, rx0 - d[7])
                gy = max(0.0, d[6] - ry1, ry0 - d[8])
                ordered.append((gx * gx + gy * gy, d))
            ordered.sort(key=lambda t: t[0])
            limit = (k * BUCKET) ** 2
            nxt = []
            for i, j, x, y in pending:
                best = math.inf
                for lb, (x1, y1, dx, dy, l2, *_r) in ordered:
                    if lb >= best:
                        break
                    t = ((x - x1) * dx + (y - y1) * dy) / l2
                    t = 0.0 if t < 0 else (1.0 if t > 1 else t)
                    ex, ey = x - x1 - t * dx, y - y1 - t * dy
                    d2 = ex * ex + ey * ey
                    if d2 < best:
                        best = d2
                if best <= limit or k >= kmax:
                    out[(i, j)] = math.sqrt(best) if best < math.inf else 0.0
                else:
                    nxt.append((i, j, x, y))
            pending = nxt
            k = k * 2 if k < kmax else kmax
            k = min(k, kmax)
    return out


def local_width(clear):
    """Local thickness: max diameter of a wall-free disk containing the cell."""
    diag = G * math.sqrt(2)
    nbrs = [(1, 0, G), (-1, 0, G), (0, 1, G), (0, -1, G),
            (1, 1, diag), (1, -1, diag), (-1, 1, diag), (-1, -1, diag)]
    centres = []
    for (i, j), r in clear.items():
        dominated = False
        for di, dj, d in nbrs:
            q = clear.get((i + di, j + dj))
            if q is not None and q >= r + d - 0.5:
                dominated = True
                break
        if not dominated:
            centres.append((r, i, j))
    centres.sort(reverse=True)
    width = {}
    for r, ci, cj in centres:
        rc = int(r // G) + 1
        r2 = (r / G) ** 2
        w = 2 * r
        for dj in range(-rc, rc + 1):
            span = r2 - dj * dj
            if span < 0:
                continue
            di_max = int(math.sqrt(span))
            jj = cj + dj
            for ii in range(ci - di_max, ci + di_max + 1):
                key = (ii, jj)
                if key not in width and key in clear:
                    width[key] = w
    for key, r in clear.items():
        if key not in width:
            width[key] = 2 * r
    return width


def components(cells):
    """4-connected components of a set of (i, j); returns lists of members."""
    seen, comps = set(), []
    for c in sorted(cells):
        if c in seen:
            continue
        seen.add(c)
        dq, comp = deque([c]), []
        while dq:
            p = dq.popleft()
            comp.append(p)
            i, j = p
            for q in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if q in cells and q not in seen:
                    seen.add(q)
                    dq.append(q)
        comps.append(comp)
    return comps


def symmetry(rows, grid, walkable, clear):
    """Symmetry of the layout under mirror_x (x -> -x, i.e. left/right about a
    vertical axis), mirror_y (top/bottom), rot180 and rot90, all about the
    walkable centroid, on a SYM_G grid. Returns {name: (area_iou, edge_match)}:
    area_iou = IoU of the walkable mask with its transform; edge_match =
    share of wall-adjacent coarse cells (holding a fine cell with clearance
    <= 16) whose transform lands within one coarse cell of another one (less
    dominated by big convex outdoor areas than area IoU)."""
    step = SYM_G // G
    cells = set()
    for j in range(0, grid.h, step):
        row = rows[j]
        for i in range(0, grid.w, step):
            if row[i] in walkable:
                cells.add((i // step, j // step))
    edges = {(i // step, j // step) for (i, j), r in clear.items() if r <= 16}
    if not cells or not edges:
        return {}
    cx = sum(c[0] for c in cells) / len(cells)
    cy = sum(c[1] for c in cells) / len(cells)
    tf = {
        "mirror_x": lambda i, j: (2 * cx - i, j),
        "mirror_y": lambda i, j: (i, 2 * cy - j),
        "rot180": lambda i, j: (2 * cx - i, 2 * cy - j),
        "rot90": lambda i, j: (cx - (j - cy), cy + (i - cx)),
    }
    near = set()
    for i, j in edges:
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                near.add((i + di, j + dj))
    res = {}
    for name, f in tf.items():
        best_iou = best_edge = 0.0
        # The optimal axis passes near the centroid; allow +-1/2 cell of rounding.
        for sx in (-0.5, 0, 0.5):
            for sy in (-0.5, 0, 0.5):
                inter = 0
                for i, j in cells:
                    a, b = f(i, j)
                    if (round(a + sx), round(b + sy)) in cells:
                        inter += 1
                best_iou = max(best_iou, inter / (2 * len(cells) - inter))
                hit = 0
                for i, j in edges:
                    a, b = f(i, j)
                    if (round(a + sx), round(b + sy)) in near:
                        hit += 1
                best_edge = max(best_edge, hit / len(edges))
        res[name] = (best_iou, best_edge)
    return res


def texture_info(path, resources=()):
    """{texture: (width, height, h_period, v_period)}. Widths/heights come from
    levels.wad.iwad_textures; periods from compositing each texture's patches
    (PNAMES + patch posts): the smallest horizontal shift (dividing the width)
    and vertical shift (dividing 128, the vanilla row wrap; the texture height
    if it is shorter than 128) under which the composed pixels repeat. Walls
    that differ by a multiple of the period look seamless. resources: PWADs
    loaded after the IWAD at path (a later lump of the same name wins, as
    with -file)."""
    sizes = iwad_textures(path, resources)[0]
    lumps = {}
    for p in (path, *resources):
        lumps.update(read_wad(p))
    pn = lumps["PNAMES"]
    pnames = [pn[4 + 8 * i:12 + 8 * i].split(b"\0")[0].decode().upper()
              for i in range(struct.unpack_from("<i", pn)[0])]
    upper = {k.upper(): v for k, v in lumps.items()}
    cache = {}

    def patch(name):
        if name not in cache:
            d = upper.get(name)
            cols = []
            if d:
                w = struct.unpack_from("<h", d)[0]
                for x in range(w):
                    o = struct.unpack_from("<i", d, 8 + 4 * x)[0]
                    posts = []
                    while d[o] != 0xFF:
                        top, n = d[o], d[o + 1]
                        posts.extend((top + y, d[o + 3 + y]) for y in range(n))
                        o += n + 4
                    cols.append(posts)
            cache[name] = cols
        return cache[name]

    out = {}
    for tl in ("TEXTURE1", "TEXTURE2"):
        data = lumps.get(tl)
        if not data:
            continue
        for i in range(struct.unpack_from("<i", data)[0]):
            o = struct.unpack_from("<i", data, 4 + 4 * i)[0]
            name = data[o:o + 8].split(b"\0")[0].decode().upper()
            w, h = struct.unpack_from("<hh", data, o + 12)
            canvas = [[0] * h for _ in range(w)]
            for p in range(struct.unpack_from("<h", data, o + 20)[0]):
                px, py, pi = struct.unpack_from("<hhh", data, o + 22 + 10 * p)
                for x, posts in enumerate(patch(pnames[pi])):
                    tx = px + x
                    if 0 <= tx < w:
                        col = canvas[tx]
                        for y, c in posts:
                            if 0 <= py + y < h:
                                col[py + y] = c + 1
            cols = [bytes(c) for c in canvas]
            hp = next(p for p in range(1, w + 1)
                      if w % p == 0 and all(cols[x] == cols[x - p] for x in range(p, w)))
            vh = VPERIOD if h >= VPERIOD else h
            vp = next(q for q in range(1, vh + 1)
                      if vh % q == 0 and all(c[y] == c[y - q] for c in cols for y in range(q, vh)))
            out[name] = (*sizes.get(name, (w, h)), hp, vp)
    return out


def wall_parts(m, textures):
    """Visible wall surfaces as tuples (line, start_v, end_v, tex, zlo, zhi,
    x_offset, vanchor, vanchor_default, length, h_period, v_period).
    Orientation follows the sidedef (front: v1->v2, back: v2->v1), so the
    texture column at start_v is x_offset. vanchor = world height of texture
    row 0 (r_segs.c pegging rules) + y_offset; vanchor_default is the same
    with no peg flags and y_offset 0. Two-sided mid textures are excluded."""
    S = m.sectors
    out = []
    for k, ln in enumerate(m.lines):
        L = m.length(ln)
        if ln.back < 0:
            s = m.sides[ln.front]
            F = S[s.sector]
            if s.mid in ("-", "") or F.ceil <= F.floor:
                continue
            _, h, hp, vp = textures.get(s.mid, (0, VPERIOD, 0, VPERIOD))
            anchor = F.floor + h if ln.flags & ML_DONTPEGBOTTOM else F.ceil
            out.append((k, ln.v1, ln.v2, s.mid, F.floor, F.ceil, s.x_offset,
                        anchor + s.y_offset, F.ceil, L, hp, vp))
            continue
        for me, other, v1, v2 in ((ln.front, ln.back, ln.v1, ln.v2), (ln.back, ln.front, ln.v2, ln.v1)):
            s = m.sides[me]
            F, B = S[s.sector], S[m.sides[other].sector]
            if B.ceil < F.ceil and not (F.ctex == SKY and B.ctex == SKY) and s.upper not in ("-", ""):
                _, h, hp, vp = textures.get(s.upper, (0, VPERIOD, 0, VPERIOD))
                anchor = F.ceil if ln.flags & ML_DONTPEGTOP else B.ceil + h
                out.append((k, v1, v2, s.upper, B.ceil, F.ceil, s.x_offset,
                            anchor + s.y_offset, B.ceil + h, L, hp, vp))
            if B.floor > F.floor and s.lower not in ("-", ""):
                _, h, hp, vp = textures.get(s.lower, (0, VPERIOD, 0, VPERIOD))
                anchor = F.ceil if ln.flags & ML_DONTPEGBOTTOM else B.floor
                out.append((k, v1, v2, s.lower, F.floor, B.floor, s.x_offset,
                            anchor + s.y_offset, B.floor, L, hp, vp))
    return out


# --- per-map metrics ---------------------------------------------------------
def analyse(args):
    m, textures = args
    S = m.sectors
    areas = m.sector_areas
    doors, lifts = sector_roles(m)
    walkable = {i for i, s in enumerate(S) if s.ceil - s.floor >= PLAYER_H or i in doors}
    r = {"map": m.slot}

    # 1. size --------------------------------------------------------------
    x0, y0, x1, y1 = m.bbox
    r["bbox_w"], r["bbox_h"] = x1 - x0, y1 - y0
    r["n_sectors"], r["n_lines"] = len(S), len(m.lines)
    r["n_two_sided"] = sum(1 for ln in m.lines if ln.back >= 0)
    r["total_sector_area"] = round(sum(areas))
    walk_area = sum(areas[i] for i in walkable)
    r["walkable_area"] = round(walk_area)
    wa = sorted(areas[i] for i in walkable)
    r["sector_area_median"] = round(quantile(wa, 0.5))
    r["sector_area_p90"] = round(quantile(wa, 0.9))
    r["n_sectors_ge_1m"] = sum(1 for a in wa if a >= LARGE_SPACE)

    # raster + clearance ----------------------------------------------------
    grid = Grid(m)
    rows = rasterise_sectors(m, grid)
    free = [(i, j) for j in range(grid.h) for i, s in enumerate(rows[j]) if s in walkable]
    cls = [line_class(m, ln, walkable, doors, lifts) for ln in m.lines]
    segs = []
    for ln, c in zip(m.lines, cls):
        if c == "wall":
            (ax, ay), (bx, by) = m.verts[ln.v1], m.verts[ln.v2]
            segs.append((ax, ay, bx, by))
    clear = clearance_field(grid, free, segs)
    width = local_width(clear)
    cellA = G * G
    r["raster_walkable_area"] = len(free) * cellA
    n = len(free) or 1
    ws = sorted(width.values())
    cs = sorted(clear.values())
    r["frac_width_le64"] = sum(1 for w in ws if w <= 64 + TOL) / n
    r["frac_width_le96"] = sum(1 for w in ws if w <= 96 + TOL) / n
    r["frac_width_le128"] = sum(1 for w in ws if w <= 128 + TOL) / n
    r["frac_width_ge512"] = sum(1 for w in ws if w >= 512 - TOL) / n
    r["width_p10"] = quantile(ws, 0.1)
    r["width_median"] = quantile(ws, 0.5)
    r["width_p90"] = quantile(ws, 0.9)
    r["clearance_median"] = quantile(cs, 0.5)
    r["clearance_p90"] = quantile(cs, 0.9)
    r["clearance_max"] = cs[-1] if cs else 0.0
    # 3. contrast ---------------------------------------------------------
    mu = sum(ws) / n
    r["width_cv"] = math.sqrt(sum((w - mu) ** 2 for w in ws) / n) / mu if mu else 0.0
    lw = [math.log2(max(w, 1.0)) for w in ws]
    lmu = sum(lw) / n
    r["width_log2_sd"] = math.sqrt(sum((v - lmu) ** 2 for v in lw) / n)
    roomish = {c for c, w in width.items() if w > ROOM_MAX_CHOKE + TOL}
    sizes = [len(comp) * cellA for comp in components(roomish)]
    r["n_spaces"] = sum(1 for s in sizes if s >= 256 * 256)
    r["n_large_spaces"] = sum(1 for s in sizes if s >= LARGE_SPACE)
    r["largest_space_area"] = max(sizes) if sizes else 0
    # Narrow -> open transitions: 4-connected components of "narrow" cells
    # (width <= 128, area >= 128x128 so wall-corner slivers drop out) that
    # touch (8-neighbourhood) a component of "open" cells (width >= T);
    # counted once per (narrow component, open component) pair.
    narrow_comps = [c for c in components({c for c, w in width.items() if w <= 128 + TOL})
                    if len(c) * cellA >= 128 * 128]
    for label, thr in (("room", 256), ("large", 512)):
        open_id = {}
        for k, comp in enumerate(components({c for c, w in width.items() if w >= thr - TOL})):
            for c in comp:
                open_id[c] = k
        trans = 0
        for comp in narrow_comps:
            touched = set()
            for i, j in comp:
                for di in (-1, 0, 1):
                    for dj in (-1, 0, 1):
                        k = open_id.get((i + di, j + dj))
                        if k is not None:
                            touched.add(k)
            trans += len(touched)
        r[f"narrow_to_{label}_transitions"] = trans
        r[f"narrow_to_{label}_per_mu2"] = trans / (walk_area / 1e6) if walk_area else 0.0

    # 4. height -----------------------------------------------------------
    wl = sorted(walkable)
    wts = [areas[i] for i in wl]
    r["distinct_floor_heights"] = len({S[i].floor for i in wl})
    r["floor_height_sd"] = wmean_sd([S[i].floor for i in wl], wts)[1]
    r["floor_height_range"] = (max(S[i].floor for i in wl) - min(S[i].floor for i in wl)) if wl else 0
    two = [(ln, *m.line_sectors(ln)) for ln in m.lines if ln.back >= 0]
    two = [(ln, f, b) for ln, f, b in two if f != b]
    nt = len(two) or 1
    r["frac_2s_floor_change"] = sum(1 for _, f, b in two if S[f].floor != S[b].floor) / nt
    ledges = [(ln, f, b) for ln, f, b in two if abs(S[f].floor - S[b].floor) > STEP]
    r["n_ledge_lines"] = len(ledges)
    r["frac_2s_ledge"] = len(ledges) / nt
    r["max_floor_to_ceil"] = max((S[i].ceil - S[i].floor for i in wl), default=0)
    r["mean_floor_to_ceil"] = wmean_sd([S[i].ceil - S[i].floor for i in wl], wts)[0]
    sky = sum(areas[i] for i in wl if S[i].ctex == SKY)
    r["sky_area_frac"] = sky / walk_area if walk_area else 0.0

    # 5. light --------------------------------------------------------------
    lm, lsd = wmean_sd([S[i].light for i in wl], wts)
    r["light_mean"], r["light_sd"] = lm, lsd
    r["dark_area_frac"] = sum(areas[i] for i in wl if S[i].light < 128) / walk_area
    r["bright_area_frac"] = sum(areas[i] for i in wl if S[i].light >= 192) / walk_area
    num = den = 0.0
    for ln, f, b in two:
        L = m.length(ln)
        num += L * abs(S[f].light - S[b].light)
        den += L
    r["light_delta_mean"] = num / den if den else 0.0
    r["frac_2s_light_change"] = sum(1 for _, f, b in two if S[f].light != S[b].light) / nt
    r["n_light_special_sectors"] = sum(1 for s in S if s.special in LIGHT_SPECIALS)

    # 6. Romero rule 1 -------------------------------------------------------
    def r1(plane):
        chg = viol = chg_nd = viol_nd = 0.0
        for ln, f, b in two:
            a, c = S[f], S[b]
            tex_a, tex_c = (a.ftex, c.ftex) if plane == "floor" else (a.ctex, c.ctex)
            h_a, h_c = (a.floor, c.floor) if plane == "floor" else (a.ceil, c.ceil)
            if tex_a == tex_c:
                continue
            L = m.length(ln)
            same = h_a == h_c
            chg += L
            viol += L * same
            if f not in doors and b not in doors:
                chg_nd += L
                viol_nd += L * same
        return (viol / chg if chg else 0.0), (viol_nd / chg_nd if chg_nd else 0.0)
    r["r1_floor_viol"], r["r1_floor_viol_nodoor"] = r1("floor")
    r["r1_ceil_viol"], r["r1_ceil_viol_nodoor"] = r1("ceil")

    # 7/8. Romero rules 2-3 on visible wall parts ------------------------------
    parts = wall_parts(m, textures)
    starts = defaultdict(list)
    for p in parts:
        starts[p[1]].append(p)
    cos30 = math.cos(math.radians(30))
    junc = junc_b = junc_flat = junc_flat_b = junc_flat_core = 0
    h_pairs = h_ok = h_def = h_fix_n = h_fix = 0
    v_pairs = v_ok = v_def = v_fix_n = v_fix = 0
    for a in parts:
        la_line, _, va, ta, zlo, zhi, xa, pha, pha0, la, hp, _vp = a
        for b in starts.get(va, ()):
            if b[0] == la_line or min(zhi, b[5]) - max(zlo, b[4]) <= 0:
                continue
            tb = b[3]
            (ax, ay), (vx, vy), (bx, by) = m.verts[a[1]], m.verts[va], m.verts[b[2]]
            ux, uy, wx, wy = vx - ax, vy - ay, bx - vx, by - vy
            if la == 0 or b[9] == 0:
                continue
            collinear = (ux * wx + uy * wy) / (la * b[9]) > cos30
            if ta != tb:
                border = bool(BORDER_EXT.match(ta) or BORDER_EXT.match(tb))
                junc += 1
                junc_b += border
                if collinear:
                    junc_flat += 1
                    junc_flat_b += border
                    junc_flat_core += bool(BORDER_CORE.match(ta) or BORDER_CORE.match(tb))
                continue
            # same texture: vertical alignment at any angle, modulo the
            # texture's vertical period
            vp = a[11]
            dv = (pha - b[7]) % vp
            ok = min(dv, vp - dv) < 0.5
            dv0 = (pha0 - b[8]) % vp
            ok0 = min(dv0, vp - dv0) < 0.5
            v_pairs += 1
            v_ok += ok
            v_def += ok0
            if not ok0:
                v_fix_n += 1
                v_fix += ok
            # horizontal alignment along (near-)collinear continuations,
            # modulo the texture's horizontal period
            if collinear and hp > 0:
                tol = 1.01 if (ux == 0 or uy == 0) else 2.01
                d = (b[6] - (xa + la)) % hp
                ok = min(d, hp - d) <= tol
                d0 = la % hp
                ok0 = min(d0, hp - d0) <= tol
                h_pairs += 1
                h_ok += ok
                h_def += ok0
                if not ok0:
                    h_fix_n += 1
                    h_fix += ok
    nan = float("nan")
    r["r2_junctions"] = junc
    r["r2_border_frac"] = junc_b / junc if junc else nan
    r["r2_collinear_junctions"] = junc_flat
    r["r2_border_frac_collinear"] = junc_flat_b / junc_flat if junc_flat else nan
    r["r2_border_frac_collinear_core"] = junc_flat_core / junc_flat if junc_flat else nan
    r["r3_h_pairs"] = h_pairs
    r["r3_h_aligned_frac"] = h_ok / h_pairs if h_pairs else nan
    r["r3_h_default_aligned_frac"] = h_def / h_pairs if h_pairs else nan
    r["r3_h_fix_rate"] = h_fix / h_fix_n if h_fix_n else nan
    r["r3_v_pairs"] = v_pairs
    r["r3_v_aligned_frac"] = v_ok / v_pairs if v_pairs else nan
    r["r3_v_default_aligned_frac"] = v_def / v_pairs if v_pairs else nan
    r["r3_v_fix_rate"] = v_fix / v_fix_n if v_fix_n else nan

    # 9. texture variety ------------------------------------------------------
    wall_use = Counter()
    for p in parts:
        wall_use[p[3]] += p[9] * (p[5] - p[4])
    for ln in m.lines:   # two-sided mid textures (grates, bars) also count as usage
        if ln.back < 0:
            continue
        f, b = m.line_sectors(ln)
        gap = max(min(S[f].ceil, S[b].ceil) - max(S[f].floor, S[b].floor), 0)
        for sd in (ln.front, ln.back):
            if m.sides[sd].mid not in ("-", ""):
                wall_use[m.sides[sd].mid] += m.length(ln) * gap
    flat_use = Counter()
    for i in range(len(S)):
        flat_use[S[i].ftex] += areas[i]
        flat_use[S[i].ctex] += areas[i]
    r["distinct_wall_textures"] = len(wall_use)
    r["distinct_flats"] = len(flat_use)
    r["wall_tex_entropy"] = entropy_bits(wall_use)
    r["flat_entropy"] = entropy_bits(flat_use)
    tot = sum(wall_use.values())
    top, topv = wall_use.most_common(1)[0] if wall_use else ("", 0)
    r["top_wall_texture"] = top
    r["top_wall_tex_share"] = topv / tot if tot else 0.0

    # 10. symmetry -------------------------------------------------------------
    sym = symmetry(rows, grid, walkable, clear)
    for k2 in ("mirror_x", "mirror_y", "rot180", "rot90"):
        r[f"sym_{k2}"] = sym.get(k2, (0.0, 0.0))[0]
    r["sym_max"] = max(v[0] for v in sym.values()) if sym else 0.0
    r["sym_max_kind"] = max(sym, key=lambda k2: sym[k2][0]) if sym else ""
    r["sym_edge_max"] = max(v[1] for v in sym.values()) if sym else 0.0
    r["sym_edge_max_kind"] = max(sym, key=lambda k2: sym[k2][1]) if sym else ""

    # 11. hazards ----------------------------------------------------------------
    r["damage_floor_frac"] = sum(areas[i] for i in wl if S[i].special in DAMAGE_SPECIALS) / walk_area
    r["liquid_floor_frac"] = sum(areas[i] for i in wl if LIQUID.match(S[i].ftex)) / walk_area
    r["liquid_floor_frac_all"] = (sum(areas[i] for i in range(len(S)) if LIQUID.match(S[i].ftex))
                                  / sum(areas))
    return r


def fmt(v):
    if isinstance(v, float):
        if math.isnan(v):
            return ""
        return f"{v:.4f}" if abs(v) < 100 else f"{v:.1f}"
    return str(v)


GROUPS = [("DOOM", lambda s: s.startswith("E")), ("DOOM II", lambda s: s.startswith("MAP"))] + \
    [(f"E{e}", lambda s, e=e: s.startswith(f"E{e}")) for e in range(1, 5)] + \
    [("MAP01-11", lambda s: s.startswith("MAP") and int(s[3:]) <= 11),
     ("MAP12-20", lambda s: s.startswith("MAP") and 12 <= int(s[3:]) <= 20),
     ("MAP21-30", lambda s: s.startswith("MAP") and 21 <= int(s[3:]) <= 30),
     ("MAP31-32", lambda s: s.startswith("MAP") and int(s[3:]) >= 31)]
KEY = ["walkable_area", "frac_width_le96", "frac_width_le128", "width_median", "width_log2_sd",
       "n_large_spaces", "narrow_to_room_per_mu2", "distinct_floor_heights", "floor_height_sd",
       "frac_2s_ledge", "max_floor_to_ceil", "sky_area_frac", "light_mean", "light_sd",
       "dark_area_frac", "light_delta_mean", "r1_floor_viol_nodoor", "r1_ceil_viol_nodoor",
       "r2_border_frac_collinear", "r3_h_aligned_frac", "r3_v_aligned_frac", "r3_v_fix_rate",
       "distinct_wall_textures", "wall_tex_entropy", "top_wall_tex_share", "sym_max", "sym_edge_max",
       "damage_floor_frac", "liquid_floor_frac"]


def summary():
    """Markdown tables from the CSV: group medians [IQR], top/bottom 5, and a
    check of lump counts against the Doom Wiki {{mapdata}} infoboxes."""
    with open(OUT) as f:
        hdr = f.readline().strip().split(",")
        rows = [dict(zip(hdr, ln.strip().split(","))) for ln in f]

    def num(r, k):
        try:
            return float(r[k])
        except ValueError:
            return None

    def cell(v):
        return f"{v:.0f}" if abs(v) >= 100 else f"{v:.3g}"

    print("| metric | " + " | ".join(g for g, _ in GROUPS) + " |")
    print("|---" * (len(GROUPS) + 1) + "|")
    for k in KEY:
        out = []
        for _, pred in GROUPS:
            xs = sorted(v for r in rows if pred(r["map"]) for v in [num(r, k)] if v is not None)
            out.append(f"{cell(quantile(xs, .5))} [{cell(quantile(xs, .25))}–{cell(quantile(xs, .75))}]")
        print(f"| `{k}` | " + " | ".join(out) + " |")
    print()
    print("| metric | top 5 | bottom 5 |\n|---|---|---|")
    for k in KEY:
        xs = sorted((v, r["map"]) for r in rows for v in [num(r, k)] if v is not None)
        top = ", ".join(f"{s} {cell(v)}" for v, s in sorted(xs, key=lambda t: (-t[0], t[1]))[:5])
        bot = ", ".join(f"{s} {cell(v)}" for v, s in xs[:5])
        print(f"| `{k}` | {top} | {bot} |")
    print()
    # Doom Wiki infobox validation
    wiki = os.path.join(ROOT, "research", "sources", "doomwiki")
    bad = 0
    for m in load_all():
        try:
            with open(os.path.join(wiki, f"{m.slot}.wiki")) as f:
                txt = f.read()
        except OSError:
            print(f"{m.slot}: no wiki page")
            continue
        md = re.search(r"\{\{mapdata(.*?)\}\}", txt, re.S)
        if not md:
            print(f"{m.slot}: no mapdata")
            continue
        vals = dict(re.findall(r"(\w+)\s*=\s*(\d+)", md.group(1)))
        ours = {"things": len(m.things), "vertexes": len(m.verts), "linedefs": len(m.lines),
                "sidedefs": len(m.sides), "sectors": len(m.sectors)}
        for k, v in ours.items():
            if k in vals and int(vals[k]) != v:
                bad += 1
                print(f"MISMATCH {m.slot} {k}: wiki {vals[k]} lumps {v}")
    print(f"wiki mapdata check: {bad} mismatches over {len(rows)} maps")


def main(argv):
    if argv == ["--summary"]:
        summary()
        return
    maps = load_all()
    tex = {g: texture_info(IWADS[g]) for g in ("doom", "doom2")}
    if argv:
        maps = [m for m in maps if m.slot in argv]
    jobs = [(m, tex[m.game]) for m in maps]
    with mp.Pool(min(len(jobs), os.cpu_count() or 1)) as pool:
        rows = pool.map(analyse, jobs, chunksize=1)
    cols = list(rows[0])
    if argv:
        for r in rows:
            print("\n".join(f"{r['map']:6} {k:30} {fmt(v)}" for k, v in r.items() if k != "map"))
        return
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write(",".join(cols) + "\n")
        for r in rows:
            f.write(",".join(fmt(r[c]) for c in cols) + "\n")
    print(f"wrote {OUT} ({len(rows)} rows, {len(cols)} columns)")


if __name__ == "__main__":
    main(sys.argv[1:])
