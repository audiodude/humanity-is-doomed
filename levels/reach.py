"""Event-driven reachability model of a Doom-format map (a levels.wadmap.Map):
which sectors the player reaches as keys are picked up and line actions fire,
and where a monster can walk. Used by the build checks (levels/checks.py) and
the research metrics (scripts/metrics/progression_metrics.py, whose docstring
describes the model in full).

    md = Model(m, textures)   # textures: ({name: (width, height)}, height of the first)
    res = md.run()            # res["R"]: regions the player reaches

Boss deaths are the slot's vanilla ones (BOSS), or a UMAPINFO entry's
`bossaction`s in their place (umapinfo_boss; pass them as Model's boss).

Movement takes an actor: None is the player; a doom2.Actor is a monster of
that size (no keys, no running jumps, opens only DR_DOOR lines that aren't
ML_SECRET, blocked by ML_BLOCKMONSTERS, no step limit if it flies, uses
monster-only teleports too). monster_closure() also fires the other walk
lines vanilla lets a monster cross (MONSTER_WALK) as the monster goes.
"""
import itertools
import math
import re
from collections import defaultdict, deque

from .doom2 import (ACTORS, KEY_OF, LINE_SPECIALS, MAX_STEP, MONSTER_DOORS, MONSTERS, PLAYER1,
                    TELEPORT_DEST, UMAPINFO_ACTORS)
from .wadmap import HARD, ML_BLOCKING, ML_BLOCKMONSTERS, ML_SECRET, ML_TWOSIDED

MIN_GAP = 32       # player is 32 units wide
USE_RANGE = 64     # USERANGE
KEY_TOUCH = 20     # key radius 20 + player 16, minus the 16 the player keeps off a wall
JUMP_MAX = 384     # longest gap considered by the running-jump model
RUN_SPEEDS = (16.67, 12.0, 8.0, 4.0)   # straight-run speeds tried (full run = 16.67 units/tic)
MISSILE_RANGE = 2048   # MISSILERANGE (hitscan reach), also used for rockets
STEP, HEIGHT = MAX_STEP, ACTORS[PLAYER1].height
BIG = 1 << 30

# ---------------------------------------------------------------- actions ---
# Vanilla line type -> what it does to its tagged sectors (p_spec.c switch tables).
ACTION = {}
for _t in (2, 46, 61, 86, 99, 103, 106, 109, 112, 115, 133, 134, 135, 136, 137):
    ACTION[_t] = "door_open"          # open, stay open
for _t in (4, 29, 63, 90, 105, 108, 111, 114):
    ACTION[_t] = "door_open_wait"     # open, wait 4 s, close
for _t in (5, 24, 64, 91, 101):
    ACTION[_t] = "floor_LnC"          # raiseFloor: lowest neighbour ceiling
for _t in (55, 56, 65, 94):
    ACTION[_t] = "floor_LnC-8"        # raiseFloorCrush
for _t in (18, 69, 119, 128, 129, 130, 131, 132):
    ACTION[_t] = "floor_NnF"          # raise to next higher neighbour floor
for _t in (19, 45, 83, 102):
    ACTION[_t] = "floor_HnF"          # lowerFloor: highest neighbour floor
for _t in (23, 38, 60, 82, 37, 84):
    ACTION[_t] = "floor_LnF"          # lowerFloorToLowest (+change)
for _t in (36, 70, 71, 98):
    ACTION[_t] = "floor_HnF+8"        # turboLower
for _t in (58, 92, 59, 93, 15, 66):
    ACTION[_t] = "floor_+24"          # raiseFloor24(+change), plat raiseAndChange 24
for _t in (14, 67):
    ACTION[_t] = "floor_+32"          # plat raiseAndChange 32
for _t in (20, 22, 47, 68, 95):
    ACTION[_t] = "floor_NnF"          # plat raiseToNearestAndChange
ACTION[140] = "floor_+512"
for _t in (30, 96):
    ACTION[_t] = "floor_tex"          # raiseToTexture
for _t in (10, 21, 62, 88, 120, 121, 122, 123):
    ACTION[_t] = "lift"               # downWaitUpStay
for _t in (53, 87):
    ACTION[_t] = "perpetual"
for _t in (7, 8):
    ACTION[_t] = "stairs8"
for _t in (100, 127):
    ACTION[_t] = "stairs16"
ACTION[9] = "donut"
ACTION[40] = "ceil_HnC"               # raiseToHighest ceiling
# Ignored (only ever shrink the space, or are cosmetic): door closes 3 16 42 50
# 75 76 107 110 113 116, ceiling lowers/crushers 6 25 41 43 44 49 72 73 77 141,
# stops 54 57 74 89, lights, scrollers. Monster-only teleports 125 126 move
# only monsters.
MANUAL_WAIT = {1, 26, 27, 28, 117}    # DR: open, wait, close
MANUAL_STAY = {31, 32, 33, 34, 118}   # D1: open, stay open
TELEPORT = {39, 97}
MONSTER_TELEPORT = {125, 126}
MONSTER_WALK = {4, 10, 88}   # with the teleports, the walk lines monsters fire (P_CrossSpecialLine)
EXITS = {11: "exit", 52: "exit", 51: "secret_exit", 124: "secret_exit"}
CONNECTOR_ACTIONS = {"door_open", "door_open_wait", "lift", "perpetual"}

# Boss deaths (p_enemy.c A_BossDeath / A_KeenDie / A_BrainDie):
# slot -> [(monster types that must all die, action or "exit", tag)]
BOSS = {
    "E1M8": [({3003}, "floor_LnF", 666)],
    "E2M8": [({16}, "exit", 0)],
    "E3M8": [({7}, "exit", 0)],
    "E4M6": [({16}, "door_open", 666)],
    "E4M8": [({7}, "floor_LnF", 666)],
    "MAP07": [({67}, "floor_LnF", 666), ({68}, "floor_tex", 667)],
    "MAP30": [({88}, "exit", 0)],
    "MAP32": [({72}, "door_open", 666)],
}
EXIT_SECTOR_SPECIAL = 11   # E1M8: damage, end level below 11% health


def umapinfo_boss(info):
    """The boss deaths a UMAPINFO entry's body defines, as [(types, action,
    tag)] like BOSS, or None if it has no `bossaction` (the slot's vanilla
    ones apply). `bossaction = clear` drops the ones before it. Each entry
    fires when every monster of its type is dead. A dict entry (values written
    quoted) can't hold one. Raises ValueError for a monster name, line special
    or form it can't read."""
    if not isinstance(info, str):
        return None
    names = {n.lower(): t for n, t in UMAPINFO_ACTORS.items()}
    out = None
    for value in re.findall(r"(?im)^\s*bossaction\s*=\s*(.*?)\s*$", info):
        if value.lower() == "clear":
            out = []
            continue
        parts = [v.strip() for v in value.split(",")]
        if len(parts) != 3 or not parts[1].isdigit() or not parts[2].isdigit():
            raise ValueError(f"bossaction = {value}: expected `thingtype, linespecial, tag`")
        name, special, tag = parts[0], int(parts[1]), int(parts[2])
        if name.lower() not in names:
            raise ValueError(f"bossaction = {value}: unknown monster {name}")
        act = "exit" if EXITS.get(special) == "exit" else ACTION.get(special)
        if act is None or (act != "exit" and not tag):
            raise ValueError(f"bossaction = {value}: line special {special} with tag {tag} isn't modelled")
        out = (out or []) + [({names[name.lower()]}, act, tag)]
    return out


def _limits(actor):
    """(highest step up, height) of an actor; None is the player. Anyone may
    drop any height (vanilla monsters avoid drops over 24, but get pushed off)."""
    if actor is None:
        return STEP, HEIGHT
    return (BIG if actor.flies else STEP), actor.height


def seg_dist(p1, p2, q1, q2):
    """Distance between segments p1p2 and q1q2."""
    if seg_cross(p1, p2, q1, q2):
        return 0.0
    return min(_pt_seg(p1, q1, q2), _pt_seg(p2, q1, q2), _pt_seg(q1, p1, p2), _pt_seg(q2, p1, p2))


def _pt_seg(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def _orient(a, b, c):
    v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    return (v > 0) - (v < 0)


def seg_cross(p1, p2, q1, q2):
    """Proper or touching intersection."""
    d1, d2 = _orient(q1, q2, p1), _orient(q1, q2, p2)
    d3, d4 = _orient(p1, p2, q1), _orient(p1, p2, q2)
    if d1 != d2 and d3 != d4:
        return True
    return False


def closest(p1, q1, p2, q2):
    """(distance, point on p1q1, point on p2q2) of the closest approach."""
    if seg_cross(p1, q1, p2, q2):
        return 0.0, p1, p1
    best = None
    for p, a, b, flip in ((p1, p2, q2, False), (q1, p2, q2, False), (p2, p1, q1, True), (q2, p1, q1, True)):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = dx * dx + dy * dy
        t = 0.0 if L == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L))
        c = (a[0] + t * dx, a[1] + t * dy)
        d = math.hypot(p[0] - c[0], p[1] - c[1])
        if best is None or d < best[0]:
            best = (d, c, p) if flip else (d, p, c)
    return best


def _simulate_run(prof, L, H, y):
    """Tic-by-tic straight run along a profile (see Model._profile) with
    sector heights H; True if, at one of RUN_SPEEDS, the player ends up
    standing on y (no air control: speed is fixed once off the edge)."""
    fy = H[y][0]
    for speed in RUN_SPEEDS:
        pos, z, momz = -2.0, H[prof[0][2]][0], 0
        for _ in range(int((L + 64) / speed) + 2):
            pos += speed
            lo, hi = pos - 16, pos + 16
            floor, ceil, on_y, wall = -BIG, BIG, False, False
            for t0, t1, s in prof:
                if t1 <= lo or t0 >= hi:
                    continue
                if s is None:
                    wall = True
                    break
                f, c = H[s]
                floor, ceil = max(floor, f), min(ceil, c)
                on_y |= s == y
            if wall or floor - z > STEP or ceil - max(floor, z) < HEIGHT:
                break
            z += momz                      # P_ZMovement
            if z <= floor:
                z, momz = floor, 0
            else:
                momz = -2 if momz == 0 else momz - 1
            if on_y and z == floor == fy:
                return True
    return False


def _in_edges(pt, edges):
    """Point in the area bounded by directed edges (even-odd rule)."""
    x, y = pt[0] + 0.013, pt[1] + 0.017   # dodge vertices
    inside = False
    for _, _, (x1, y1), (x2, y2) in edges:
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def _dangling(edges):
    """Some vertex of these boundary edges has unequal in/out degree and does
    not sit on another of the edges (i.e. the piece is not closed)."""
    deg = defaultdict(int)
    for _, _, p, q in edges:
        deg[p] += 1
        deg[q] -= 1
    return any(d and not any(_pt_seg(v, e[2], e[3]) < 1 for e in edges if v not in (e[2], e[3]))
               for v, d in deg.items())


def _trace_loops(edges):
    """Trace boundary edges (sector on the right) into minimal loops: at each
    vertex continue along the outgoing edge with the smallest
    counter-clockwise angle from the way we came, so pieces of a sector that
    only touch at a vertex come out as separate loops. A trace that reaches a
    vertex with no unused outgoing edge (T-junction, unclosed sector) ends as
    an open piece."""
    out = defaultdict(list)
    for k, e in enumerate(edges):
        out[e[2]].append(k)
    used = [False] * len(edges)
    loops = []
    for k0 in range(len(edges)):
        if used[k0]:
            continue
        loop, k = [], k0
        while k is not None and not used[k]:
            used[k] = True
            loop.append(edges[k])
            p, q = edges[k][2], edges[k][3]
            back = math.atan2(p[1] - q[1], p[0] - q[0])
            best, best_ang = None, None
            for k2 in out[q]:
                if used[k2] and k2 != k0:
                    continue
                p2, q2 = edges[k2][2], edges[k2][3]
                ang = (math.atan2(q2[1] - p2[1], q2[0] - p2[0]) - back) % (2 * math.pi)
                if ang < 1e-9:
                    ang = 2 * math.pi
                if best is None or ang < best_ang:
                    best, best_ang = k2, ang
            k = best
        loops.append(loop)
    return loops


def _merge_loops(loops):
    """Join boundary pieces that are one loop in fact: pieces meeting at a
    T-junction (a vertex inside another piece's line), and pieces that are
    not closed (merged into the nearest piece)."""
    if len(loops) < 2:
        return loops
    parent = list(range(len(loops)))

    def find(k):
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    def t_junction(pts, es):
        return any(_pt_seg(p, e[2], e[3]) < 1 and math.dist(p, e[2]) >= 1 and math.dist(p, e[3]) >= 1
                   for p in pts for e in es)
    for a, b in itertools.combinations(range(len(loops)), 2):
        if find(a) == find(b):
            continue
        pts_a = {p for e in loops[a] for p in (e[2], e[3])}
        pts_b = {p for e in loops[b] for p in (e[2], e[3])}
        if t_junction(pts_a, loops[b]) or t_junction(pts_b, loops[a]):
            parent[find(a)] = find(b)
    groups = defaultdict(list)
    for k in range(len(loops)):
        groups[find(k)].extend(loops[k])
    loops = list(groups.values())
    while len(loops) > 1:
        bad = next((k for k, lp in enumerate(loops) if _dangling(lp)), None)
        if bad is None:
            break
        near = min((k for k in range(len(loops)) if k != bad),
                   key=lambda k: min(seg_dist(e[2], e[3], f[2], f[3]) for e in loops[bad] for f in loops[k]))
        loops[near] = loops[near] + loops[bad]
        del loops[bad]
    return loops


class Model:
    """Graph nodes are *regions*: connected pieces of a sector (vanilla maps
    reuse one sector number for separate areas, e.g. both sides of a locked
    barrier). Heights stay per sector: every action moves all regions of a
    sector together, using the vanilla searches over the whole sector."""

    def __init__(self, m, textures, use_jumps=True, boss=None):
        self.m = m
        self.slot = m.slot
        self.use_jumps = use_jumps
        self._boss = boss
        self.ns = len(m.sectors)
        self.osecs_of_line = [m.line_sectors(ln) for ln in m.lines]
        # Sector line lists in line order (P_GroupLines) for the vanilla
        # height searches, stairs and donuts.
        self.osec_lines = [[] for _ in range(self.ns)]
        for i, (f, b) in enumerate(self.osecs_of_line):
            self.osec_lines[f].append(i)
            if b is not None and b != f:
                self.osec_lines[b].append(i)
        self._regions()
        n = self.n
        self.init = [(m.sectors[o].floor, m.sectors[o].ceil) for o in self.nsec]
        self.sec_lines = [[] for _ in range(n)]
        for i, (f, b) in enumerate(self.secs_of_line):
            self.sec_lines[f].append(i)
            if b is not None and b != f:
                self.sec_lines[b].append(i)
        self._centroids()
        self._pairs()
        self._build_grid()
        self.gaps = self._gaps(self.free_lines, self.adj, MIN_GAP)
        self._monster_ways = {}
        if use_jumps:
            self._jumps()
        self._things()
        self._specials(textures)

    def sec(self, r):
        """The Sector record of region r."""
        return self.m.sectors[self.nsec[r]]

    # ------------------------------------------------------------ geometry --
    def _regions(self):
        """Split each sector's boundary (oriented with the sector on the
        right) into traced loops; clockwise loops are outlines, the others
        holes, each hole joining the smallest outline around it."""
        m, V, osl = self.m, self.m.verts, self.osecs_of_line
        side_edges = defaultdict(list)
        for i, ln in enumerate(m.lines):
            f, b = osl[i]
            if b == f:
                continue
            p, q = V[ln.v1], V[ln.v2]
            side_edges[f].append((i, 0, p, q))
            if b is not None:
                side_edges[b].append((i, 1, q, p))
        self.nsec, self.group, self._loops = [], defaultdict(list), []
        side_region = {}
        for o in range(self.ns):
            edges = side_edges.get(o, [])
            loops = _merge_loops(_trace_loops(edges))
            areas = [sum(p[0] * q[1] - q[0] * p[1] for _, _, p, q in lp) / 2 for lp in loops]
            outers = [k for k, A in enumerate(areas) if A < 0]
            if len(outers) <= 1:
                parts = [list(range(len(loops)))]
            else:
                own = {k: [k] for k in outers}
                for k in range(len(loops)):
                    if k in own:
                        continue
                    pt = loops[k][0][2]
                    inside = [j for j in outers if _in_edges(pt, loops[j])]
                    best = max(inside or outers, key=lambda j: areas[j])   # smallest |area| containing
                    own[best].append(k)
                parts = list(own.values())
            for ks in parts:
                r = len(self.nsec)
                self.nsec.append(o)
                self.group[o].append(r)
                es = [e for k in ks for e in loops[k]]
                self._loops.append(es)
                for i, sd, _, _ in es:
                    side_region[(i, sd)] = r
        self.n = len(self.nsec)
        self.secs_of_line = []
        for i, ln in enumerate(m.lines):
            f, b = osl[i]
            if b == f:
                r = self._locate(f, m.midpoint(ln))
                self.secs_of_line.append((r, r))
            else:
                self.secs_of_line.append((side_region[(i, 0)], None if b is None else side_region[(i, 1)]))

    def _locate(self, o, pt):
        rs = self.group[o]
        if len(rs) == 1:
            return rs[0]
        for r in rs:
            if _in_edges(pt, self._loops[r]):
                return r
        return rs[0]

    def region_of_point(self, x, y):
        o = self.m.sector_of_point(x, y)
        return None if o is None else self._locate(o, (x, y))

    def _centroids(self):
        m, n = self.m, self.n
        self.area, self.centroid = [], []
        for r in range(n):
            acc = cx = cy = 0.0
            for _, _, (x1, y1), (x2, y2) in self._loops[r]:
                c = x1 * y2 - x2 * y1
                acc += c
                cx += (x1 + x2) * c
                cy += (y1 + y2) * c
            self.area.append(abs(acc) / 2)
            if abs(acc) > 1e-6:
                self.centroid.append((cx / (3 * acc), cy / (3 * acc)))
            elif self._loops[r]:
                pts = [e[2] for e in self._loops[r]]
                self.centroid.append((sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)))
            else:
                self.centroid.append((0.0, 0.0))
        # A point inside each region (for line of sight): the centroid if it
        # lies in the region, else a point a few units inside its longest line.
        self.inner = []
        for s in range(n):
            c = self.centroid[s]
            if self.region_of_point(*c) == s:
                self.inner.append(c)
                continue
            pt = c
            if self.sec_lines[s]:
                i = max(self.sec_lines[s], key=lambda i: m.length(m.lines[i]))
                ln = m.lines[i]
                (x1, y1), (x2, y2) = m.verts[ln.v1], m.verts[ln.v2]
                L = m.length(ln) or 1
                nx, ny = (y2 - y1) / L, -(x2 - x1) / L   # right of v1->v2 = front
                if self.secs_of_line[i][0] != s:
                    nx, ny = -nx, -ny
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                for d in (4, 8, 2, 16):
                    p = (mx + nx * d, my + ny * d)
                    if self.region_of_point(*p) == s:
                        pt = p
                        break
            self.inner.append(pt)

    def _pairs(self):
        """Adjacent sector pairs (over non-impassable two-sided lines), the
        widest contiguous run of such lines per pair, and a portal point."""
        m = self.m
        by_pair = defaultdict(list)
        for i, (ln, (f, b)) in enumerate(zip(m.lines, self.secs_of_line)):
            if b is None or b == f:
                continue
            by_pair[(min(f, b), max(f, b))].append(i)
        self.pair_lines = by_pair
        self.adj, self.pair_width, self.portal = self._runs(ML_BLOCKING)
        # Non-impassable two-sided lines of each sector, for the dynamic width check.
        self.free_lines = self._free_lines(ML_BLOCKING)   # sector -> [(line, other sector)]

    def _runs(self, mask):
        """(adjacency, widest run, portal point) per sector pair over lines
        without any of the mask's flags."""
        m = self.m
        adj, pair_width, portal = defaultdict(list), {}, {}
        for key, idxs in self.pair_lines.items():
            free = [i for i in idxs if not m.lines[i].flags & mask]
            # contiguous runs share vertices
            parent = {}

            def find(x):
                while parent.setdefault(x, x) != x:
                    parent[x] = parent[parent[x]]
                    x = parent[x]
                return x
            for i in free:
                ln = m.lines[i]
                parent[find(ln.v1)] = find(ln.v2)
            runs = defaultdict(list)
            for i in free:
                runs[find(m.lines[i].v1)].append(i)
            best_w, best_mid = 0.0, None
            for run in runs.values():
                w = sum(m.length(m.lines[i]) for i in run)
                if w > best_w:
                    longest = max(run, key=lambda i: m.length(m.lines[i]))
                    best_w, best_mid = w, m.midpoint(m.lines[longest])
            pair_width[key] = best_w
            if best_mid is not None:
                a, b = key
                adj[a].append(b)
                adj[b].append(a)
                portal[key] = best_mid
            elif idxs:
                portal[key] = m.midpoint(m.lines[idxs[0]])
        return adj, pair_width, portal

    def _free_lines(self, mask):
        free_lines = defaultdict(list)
        for i, (ln, (f, b)) in enumerate(zip(self.m.lines, self.secs_of_line)):
            if b is None or b == f or ln.flags & mask:
                continue
            free_lines[f].append((i, b))
            free_lines[b].append((i, f))
        return free_lines

    def edge_len(self, a, b):
        p = self.portal[(min(a, b), max(a, b))]
        ca, cb = self.centroid[a], self.centroid[b]
        return math.hypot(ca[0] - p[0], ca[1] - p[1]) + math.hypot(cb[0] - p[0], cb[1] - p[1])

    def _gaps(self, free_lines, adj, width):
        """Sector pairs x, y on either side of a sector s with facing lines
        closer than the actor's width (the player's: 32 units): Doom stands an
        actor on the highest floor its box touches, so it can walk across such
        a trench or along such a ledge without touching s's floor."""
        m = self.m
        gaps = defaultdict(list)         # x -> [(y, s, point)]
        for s in range(self.n):
            segs = []
            for i, o in free_lines[s]:
                ln = m.lines[i]
                p, q = m.verts[ln.v1], m.verts[ln.v2]
                segs.append((o, p, q, min(p[0], q[0]), max(p[0], q[0]), min(p[1], q[1]), max(p[1], q[1])))
            best = {}
            for (o1, p1, q1, ax0, ax1, ay0, ay1), (o2, p2, q2, bx0, bx1, by0, by1) in \
                    itertools.combinations(segs, 2):
                if o1 == o2 or o1 == s or o2 == s:
                    continue
                if bx0 - ax1 >= width or ax0 - bx1 >= width or by0 - ay1 >= width or ay0 - by1 >= width:
                    continue
                d, pa, pb = closest(p1, q1, p2, q2)
                key = (o1, o2) if o1 < o2 else (o2, o1)
                if d < width and (key not in best or d < best[key][0]):
                    best[key] = (d, ((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2))
            for (x, y), (d, mid) in best.items():
                if y not in adj[x]:
                    gaps[x].append((y, s, mid))
                    gaps[y].append((x, s, mid))
        return gaps

    def _build_grid(self):
        """Lines bucketed into 128-unit cells (for segment queries)."""
        m = self.m
        cell = 128
        grid = defaultdict(list)
        boxes = []
        for i, ln in enumerate(m.lines):
            (x1, y1), (x2, y2) = m.verts[ln.v1], m.verts[ln.v2]
            bx = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
            boxes.append(bx)
            for gx in range(bx[0] // cell, bx[2] // cell + 1):
                for gy in range(bx[1] // cell, bx[3] // cell + 1):
                    grid[(gx, gy)].append(i)
        self._grid, self._boxes, self._cell = grid, boxes, cell

    def lines_near(self, a, b, pad=0):
        """Indexes of lines in the cells covering the box of segment ab."""
        cell = self._cell
        out = set()
        for gx in range(int(min(a[0], b[0]) - pad) // cell, int(max(a[0], b[0]) + pad) // cell + 1):
            for gy in range(int(min(a[1], b[1]) - pad) // cell, int(max(a[1], b[1]) + pad) // cell + 1):
                out.update(self._grid.get((gx, gy), ()))
        return out

    def _jumps(self):
        """Running-jump candidates: for two-sided lines within JUMP_MAX of
        each other, the closest approach from a sector x on one to a
        non-adjacent sector y on the other. The straight run across is
        profiled lazily (see jump_ok)."""
        m = self.m
        grid, boxes, cell = self._grid, self._boxes, self._cell
        two = [i for i, (f, b) in enumerate(self.secs_of_line)
               if b is not None and b != f and not m.lines[i].flags & ML_BLOCKING]
        two_set = set(two)
        best = {}
        R = JUMP_MAX
        for i in two:
            bx = boxes[i]
            near = set()
            for gx in range((bx[0] - R) // cell, (bx[2] + R) // cell + 1):
                for gy in range((bx[1] - R) // cell, (bx[3] + R) // cell + 1):
                    near.update(grid.get((gx, gy), ()))
            li = m.lines[i]
            p1, q1 = m.verts[li.v1], m.verts[li.v2]
            si = self.secs_of_line[i]
            for j in near:
                if j <= i or j not in two_set:
                    continue
                bj = boxes[j]
                if bj[0] - bx[2] > R or bx[0] - bj[2] > R or bj[1] - bx[3] > R or bx[1] - bj[3] > R:
                    continue
                sj = self.secs_of_line[j]
                pairs = [(x, y) for x in si for y in sj if x != y and x not in sj and y not in si
                         and y not in self.adj[x]]
                if not pairs:
                    continue
                lj = m.lines[j]
                d, pa, pb = closest(p1, q1, m.verts[lj.v1], m.verts[lj.v2])
                if d < 1 or d > R:
                    continue
                for x, y in pairs:
                    if (x, y) not in best or d < best[(x, y)][0]:
                        best[(x, y)] = (d, pa, pb)
                    if (y, x) not in best or d < best[(y, x)][0]:
                        best[(y, x)] = (d, pb, pa)
        self.jump_cands = defaultdict(list)   # x -> [(y, distance, (pa, pb))]
        for (x, y), (d, pa, pb) in best.items():
            self.jump_cands[x].append((y, d, (pa, pb)))
        self._profiles = {}
        self._jump_cache = {}

    def _profile(self, x, y, pa, pb):
        """Sectors (None = wall or void) along the straight run from 2 units
        inside x through pa and pb to 48 units past y, as (t0, t1, sector)
        with t measured from pa; plus L = |pa pb|. None if the run does not
        start in x or never reaches y."""
        key = (x, y)
        if key in self._profiles:
            return self._profiles[key]
        m = self.m
        L = math.dist(pa, pb)
        ux, uy = (pb[0] - pa[0]) / L, (pb[1] - pa[1]) / L
        a = (pa[0] - 2 * ux, pa[1] - 2 * uy)
        b = (pb[0] + 48 * ux, pb[1] + 48 * uy)
        hits = []
        for i in self.lines_near(a, b):
            ln = m.lines[i]
            p, q = m.verts[ln.v1], m.verts[ln.v2]
            ex, ey = q[0] - p[0], q[1] - p[1]
            den = ux * ey - uy * ex
            if den == 0:
                continue
            t = ((p[0] - a[0]) * ey - (p[1] - a[1]) * ex) / den
            s = ((p[0] - a[0]) * uy - (p[1] - a[1]) * ux) / den
            if not (0 <= s <= 1) or not (0 < t < L + 50):
                continue
            f, bk = self.secs_of_line[i]
            # moving along u we end up on the line's right (front) side when den > 0
            after, before = (f, bk) if den > 0 else (bk, f)
            if bk is None or ln.flags & ML_BLOCKING:
                after = None
            hits.append((t - 2, before, after))
        hits.sort(key=lambda h: h[0])
        # Lines meeting at a vertex on the path give near-equal hits: take
        # the one leaving the current sector.
        prof, t0, cur, k = [], -BIG, x, 0
        while k < len(hits):
            n = 1
            while k + n < len(hits) and hits[k + n][0] - hits[k][0] < 0.5:
                n += 1
            group = hits[k:k + n]
            k += n
            t, before, after = next((h for h in group if h[1] == cur), group[0])
            if before != cur and t < 0.5:
                self._profiles[key] = None
                return None
            prof.append((t0, t, cur))
            t0, cur = t, after
            if cur is None:
                break
        prof.append((t0, BIG, cur))
        ok = any(s == y for t0, t1, s in prof if t1 > L - 1)
        self._profiles[key] = (prof, L) if ok else None
        return self._profiles[key]

    def _states(self, s, base, man):
        return base[s] if man[s] is None else base[s] + (man[s],)

    def gap_ok(self, x, y, s, base, man, keys, actor=None):
        climb, height = _limits(actor)
        for fx, cx in self._states(x, base, man):
            for fs, cs in base[s]:
                for fy, cy in self._states(y, base, man):
                    top = max(fx, fs, fy)
                    if max(fs, fy) - fx <= climb and min(cx, cs, cy) - top >= height:
                        return True
        return False

    def jump_ok(self, x, y, ends, base, man, keys):
        """Simulate a player leaving x straight towards y at each of
        RUN_SPEEDS: per tic, stand on the highest floor the 32-unit box
        overlaps (step-ups <= 24 allowed, also in the air), need 56 units of
        headroom, fall under vanilla gravity (P_ZMovement). Succeeds when the
        player stands on y's floor while touching y."""
        Sx, Sy = self._states(x, base, man), self._states(y, base, man)
        if not any(fy - fx <= STEP for fx, _ in Sx for fy, _ in Sy):
            return False
        pr = self._profile(x, y, *ends)
        if pr is None:
            return False
        prof, L = pr
        mids = sorted({s for _, _, s in prof if s not in (x, y, None)})
        H = {}
        for s in mids:
            st = self._states(s, base, man)
            H[s] = (min(f for f, _ in st), max(c for _, c in st))
        for hx in Sx:
            for hy in Sy:
                key = (x, y, hx, hy, tuple(H[s] for s in mids))
                if key not in self._jump_cache:
                    H[x], H[y] = hx, hy
                    self._jump_cache[key] = _simulate_run(prof, L, H, y)
                if self._jump_cache[key]:
                    return True
        return False

    def moves(self, a, base, man, keys):
        """(b, length, kind) for every sector the player can move to from a."""
        for b in self.adj[a]:
            if self.can_pass(a, b, base, man, keys):
                yield b, self.edge_len(a, b), "walk"
        yield from self.moves_nonwalk(a, base, man, keys)

    # --------------------------------------------------------------- things --
    def _things(self):
        m = self.m
        uv = m.things_on(HARD)
        p1 = next(t for t in m.things if t.type == 1)
        self.start = self.region_of_point(p1.x, p1.y)
        self.start_pt = (p1.x, p1.y)
        self.keys = []   # (colour, region, (x, y))
        for t in uv:
            if t.type in KEY_OF:
                self.keys.append((KEY_OF[t.type], self.region_of_point(t.x, t.y), (t.x, t.y)))
        self.key_colours = sorted({k[0] for k in self.keys})
        self.monsters = defaultdict(list)   # type -> [(region, (x, y))]
        for t in uv:
            if t.type in MONSTERS:
                self.monsters[t.type].append((self.region_of_point(t.x, t.y), (t.x, t.y)))
        # teleport destinations in thing order (thinker order): (sector, region, point)
        self.tele_dests = [(m.sector_of_point(t.x, t.y), self.region_of_point(t.x, t.y), (t.x, t.y))
                           for t in m.things if t.type == TELEPORT_DEST]

    # ------------------------------------------------------------- specials --
    def _specials(self, textures):
        m = self.m
        tex_sizes, tex0 = textures
        self.tex_h = {k: v[1] for k, v in tex_sizes.items()}
        self.tex0_h = tex0
        self.triggers = []      # dicts: line, special, trig, key, action, tag, group
        self.manual_open = [None] * self.n     # open state of manual wait-close doors (by region)
        self.door_in = defaultdict(set)        # (front, back region) -> {key or None} for manual doors
        self.monster_door_in = set()           # (front, back region) of manual doors monsters open
        self.stay_doors = []                   # (line, front, back region, key)
        self.teleports = []                    # (line, front, back region, dest region, dest pt)
        self.monster_teleports = []            # the same for monster-only teleports
        self.exits = []                        # (kind, line, trig)
        self.connectors = set()                # door / lift regions
        self.tagged = defaultdict(list)        # tag -> sectors (not regions)
        for s, sec in enumerate(m.sectors):
            if sec.tag:
                self.tagged[sec.tag].append(s)

        def regions(tag):
            return [r for s in self.tagged.get(tag, []) for r in self.group[s]]
        cur0 = list(self.init)
        for i, ln in enumerate(m.lines):
            sp = ln.special
            if sp <= 0:
                continue
            f, b = self.secs_of_line[i]
            spec = LINE_SPECIALS.get(sp)
            if sp in MANUAL_WAIT or sp in MANUAL_STAY:
                if b is None:
                    continue
                key = spec.key
                self.connectors.add(b)
                if sp in MANUAL_WAIT:
                    self.door_in[(f, b)].add(key)
                    self.manual_open[b] = (self.init[b][0], self.lnc(self.nsec[b], cur0) - 4)
                    if sp in MONSTER_DOORS and not ln.flags & ML_SECRET:
                        self.monster_door_in.add((f, b))
                else:
                    self.stay_doors.append((i, f, b, key))
            elif sp in TELEPORT or sp in MONSTER_TELEPORT:
                dest = None
                for s in sorted(self.tagged.get(ln.tag, [])):
                    dest = next(((dr, p) for ds, dr, p in self.tele_dests if ds == s), None)
                    if dest:
                        break
                if dest:
                    (self.teleports if sp in TELEPORT else self.monster_teleports).append(
                        (i, f, b, dest[0], dest[1]))
            elif sp in EXITS:
                self.exits.append((EXITS[sp], i, spec.trigger))
            elif sp in ACTION and spec and ln.tag:
                act = ACTION[sp]
                self.triggers.append(dict(line=i, special=sp, trig=spec.trigger, key=spec.key,
                                          action=act, tag=ln.tag, group=(ln.tag, spec.kind)))
                if act in CONNECTOR_ACTIONS:
                    self.connectors.update(regions(ln.tag))
        self.groups = sorted({t["group"] for t in self.triggers})
        self.exit_sectors = [r for r in range(self.n) if self.sec(r).special == EXIT_SECTOR_SPECIAL]
        self.boss = BOSS.get(self.slot, []) if self._boss is None else self._boss
        self._shots = {}
        for types, act, tag in self.boss:
            if act in CONNECTOR_ACTIONS:
                self.connectors.update(regions(tag))
        self.tele_from = self._tele_from(self.teleports, ML_BLOCKING)

    # ------------------------------------------- vanilla height searches ----
    # These work on sectors (not regions); `cur` is indexed by region, and all
    # regions of a sector always share their heights.
    def _h(self, cur, o):
        return cur[self.group[o][0]]

    def _next(self, o):
        """getNextSector over the sector's ML_TWOSIDED lines, in line order."""
        for i in self.osec_lines[o]:
            if not self.m.lines[i].flags & ML_TWOSIDED:
                continue
            f, b = self.osecs_of_line[i]
            if b is None:
                continue
            yield b if f == o else f

    def lnc(self, o, cur):
        return min((self._h(cur, x)[1] for x in self._next(o)), default=BIG)

    def hnc(self, o, cur):
        return max((self._h(cur, x)[1] for x in self._next(o)), default=0)

    def lnf(self, o, cur):
        return min([self._h(cur, o)[0]] + [self._h(cur, x)[0] for x in self._next(o)])

    def hnf(self, o, cur):
        return max((self._h(cur, x)[0] for x in self._next(o)), default=-500)

    def nnf(self, o, cur):
        h = self._h(cur, o)[0]
        higher = [self._h(cur, x)[0] for x in self._next(o) if self._h(cur, x)[0] > h]
        return min(higher) if higher else h

    def shortest_lower(self, o):
        best = BIG
        for i in self.osec_lines[o]:
            ln = self.m.lines[i]
            if not ln.flags & ML_TWOSIDED:
                continue
            for sd in (ln.front, ln.back):
                if sd < 0:
                    continue
                name = self.m.sides[sd].lower
                h = self.tex0_h if name == "-" else self.tex_h.get(name, BIG)
                best = min(best, h)
        return 0 if best == BIG else best

    # --------------------------------------------------------------- actions --
    def apply(self, act, sectors, st):
        """Apply an action to (whole) sectors; st = (perm, osc, cur) by region."""
        perm, osc, cur = st
        changed = False
        m = self.m

        def add(o, state, oscillating=False, permanent=True):
            nonlocal changed
            for r in self.group[o]:
                if state not in perm[r]:
                    perm[r].add(state)
                    changed = True
                if oscillating:
                    osc[r].add(state)
                if permanent:
                    cur[r] = state

        for o in sectors:
            f, c = self._h(cur, o)
            if act in ("door_open", "door_open_wait"):
                top = self.lnc(o, cur) - 4
                add(o, (f, top), oscillating=act == "door_open_wait", permanent=act == "door_open")
            elif act.startswith("floor_"):
                kind = act[6:]
                if kind == "LnC":
                    t = min(self.lnc(o, cur), c)
                elif kind == "LnC-8":
                    t = min(self.lnc(o, cur), c) - 8
                elif kind == "NnF":
                    t = self.nnf(o, cur)
                elif kind == "HnF":
                    t = self.hnf(o, cur)
                elif kind == "LnF":
                    t = self.lnf(o, cur)
                elif kind == "HnF+8":
                    t = self.hnf(o, cur)
                    if t != f:
                        t += 8
                elif kind == "tex":
                    t = f + self.shortest_lower(o)
                else:
                    t = f + int(kind[1:])
                add(o, (t, c))
            elif act == "lift":
                low = min(self.lnf(o, cur), f)
                add(o, (low, c), oscillating=True, permanent=False)
                add(o, (f, c), oscillating=True, permanent=False)
            elif act == "perpetual":
                low = min(self.lnf(o, cur), f)
                high = max(self.hnf(o, cur), f)
                add(o, (low, c), oscillating=True, permanent=False)
                add(o, (high, c), oscillating=True, permanent=False)
            elif act == "ceil_HnC":
                add(o, (f, self.hnc(o, cur)))
            elif act in ("stairs8", "stairs16"):
                size = 8 if act == "stairs8" else 16
                sec, height = o, f + size
                done = {sec}
                add(sec, (height, c))
                tex = m.sectors[sec].ftex
                while True:
                    nxt = None
                    for i in self.osec_lines[sec]:
                        if not m.lines[i].flags & ML_TWOSIDED:
                            continue
                        fs, bs = self.osecs_of_line[i]
                        if fs != sec or bs is None or m.sectors[bs].ftex != tex:
                            continue
                        height += size
                        if bs in done:
                            continue
                        nxt = bs
                        break
                    if nxt is None:
                        break
                    sec = nxt
                    done.add(sec)
                    add(sec, (height, self._h(cur, sec)[1]))
            elif act == "donut":
                lines = self.osec_lines[o]
                if not lines:
                    continue
                f0, b0 = self.osecs_of_line[lines[0]]
                s2 = b0 if f0 == o else f0
                if s2 is None:
                    continue
                for i in self.osec_lines[s2]:
                    fs, bs = self.osecs_of_line[i]
                    if bs == o or bs is None:
                        continue
                    h3 = self._h(cur, bs)[0]
                    add(s2, (h3, self._h(cur, s2)[1]))
                    add(o, (h3, c))
                    break
        return changed

    # ------------------------------------------------------------ movement --
    # `actor` is None for the player, else a doom2.Actor moving as a monster.
    def ways(self, actor=None):
        """(adjacency, widest run per pair, free lines, gaps, teleports by
        source sector, width) the actor moves over."""
        if actor is None:
            return self.adj, self.pair_width, self.free_lines, self.gaps, self.tele_from, MIN_GAP
        if actor not in self._monster_ways:
            mask = ML_BLOCKING | ML_BLOCKMONSTERS
            adj, pair_width, _ = self._runs(mask)
            free_lines = self._free_lines(mask)
            width = 2 * actor.radius
            self._monster_ways[actor] = (adj, pair_width, free_lines, self._gaps(free_lines, adj, width),
                                         self._tele_from(self.teleports + self.monster_teleports, mask), width)
        return self._monster_ways[actor]

    def man_states(self, keys, actor=None):
        """Manual-door open state usable when leaving each sector."""
        man = [None] * self.n
        if actor is not None:
            for f, b in self.monster_door_in:
                man[b] = self.manual_open[b]
            return man
        for (f, b), ks in self.door_in.items():
            if self.manual_open[b] and any(k is None or k in keys for k in ks):
                man[b] = self.manual_open[b]
        return man

    def heights_ok(self, a, b, base, man, keys, actor=None):
        Sa = base[a]
        if man[a] is not None:
            Sa = Sa + (man[a],)
        Sb = base[b]
        if man[b] is not None:
            if actor is None:
                ks = self.door_in.get((a, b))
                opens = ks and any(k is None or k in keys for k in ks)
            else:
                opens = (a, b) in self.monster_door_in
            if opens:
                Sb = Sb + (man[b],)
        climb, height = _limits(actor)
        for fa, ca in Sa:
            for fb, cb in Sb:
                if fb - fa <= climb and min(ca, cb) - max(fa, fb) >= height:
                    return True
        return False

    def can_pass(self, a, b, base, man, keys, actor=None):
        """The actor can move from sector a into sector b."""
        if not self.heights_ok(a, b, base, man, keys, actor):
            return False
        _, pair_width, _, _, _, width = self.ways(actor)
        if pair_width.get((min(a, b), max(a, b)), 0) >= width:
            return True
        # Narrow boundary: count the contiguous run of lines from a (and from
        # b) into any neighbour the actor can stand across, e.g. a pillar cut
        # into 16-24 unit slices that lower together.
        return (self._run_width(a, b, base, man, keys, actor) >= width and
                self._run_width(b, a, base, man, keys, actor) >= width)

    def _run_width(self, x, y, base, man, keys, actor=None):
        m = self.m
        ok = {}
        parent = {}

        def find(v):
            while parent.setdefault(v, v) != v:
                parent[v] = parent[parent[v]]
                v = parent[v]
            return v
        chosen = []
        for i, o in self.ways(actor)[2][x]:
            if o not in ok:
                ok[o] = (o == y or self.heights_ok(x, o, base, man, keys, actor)
                         or self.heights_ok(o, x, base, man, keys, actor))
            if ok[o]:
                ln = m.lines[i]
                parent[find(ln.v1)] = find(ln.v2)
                chosen.append((i, o))
        width = defaultdict(float)
        has_y = set()
        for i, o in chosen:
            r = find(m.lines[i].v1)
            width[r] += m.length(m.lines[i])
            if o == y:
                has_y.add(r)
        return max((width[r] for r in has_y), default=0.0)

    def tele_ok(self, a, pad, base, man, keys, actor=None):
        """The actor in a can walk onto a teleport line's pad (back) side."""
        return pad == a or (pad is not None and self.can_pass(a, pad, base, man, keys, actor))

    def closure(self, base, man, keys, starts, actor=None):
        adj = self.ways(actor)[0]
        seen = set(starts)
        q = deque(starts)
        while q:
            a = q.popleft()
            for b in adj[a]:
                if b not in seen and self.can_pass(a, b, base, man, keys, actor):
                    seen.add(b)
                    q.append(b)
            for b, _, _ in self.moves_nonwalk(a, base, man, keys, seen, actor):
                seen.add(b)
                q.append(b)
        return seen

    def moves_nonwalk(self, a, base, man, keys, skip=(), actor=None):
        """Gaps straddled, running jumps (the player only) and teleports from a."""
        _, _, _, gaps, tele_from, _ = self.ways(actor)
        ca = self.centroid[a]
        for y, s, pt in gaps.get(a, ()):
            if y not in skip and self.gap_ok(a, y, s, base, man, keys, actor):
                yield y, math.dist(ca, pt) + math.dist(pt, self.centroid[y]), "gap"
        if self.use_jumps and actor is None:
            for y, d, ends in self.jump_cands.get(a, ()):
                if y not in skip and self.jump_ok(a, y, ends, base, man, keys):
                    yield y, math.dist(ca, ends[0]) + d + math.dist(ends[1], self.centroid[y]), "jump"
        for pad, dest, mid, dpt in tele_from.get(a, ()):
            if dest not in skip and self.tele_ok(a, pad, base, man, keys, actor):
                yield dest, math.dist(ca, mid) + math.dist(dpt, self.centroid[dest]), "teleport"

    def _tele_from(self, teleports, mask):
        d = defaultdict(list)
        for i, f, b, ds, dpt in teleports:
            if ds is not None and not self.m.lines[i].flags & mask:
                d[f].append((b, ds, self.m.midpoint(self.m.lines[i]), dpt))
        return d

    def final_state(self, res):
        """(base, man, keys) of a run's end: current heights plus the
        oscillating ones of lifts, platforms and doors."""
        base = [tuple({res["cur"][s]} | res["osc"][s]) for s in range(self.n)]
        return base, res["final_man"], res["keys"]

    # ------------------------------------------------------- trigger sites --
    def use_site(self, i, R, base, man):
        """Sector from which line i can be used (front side), or None: its
        front sector, or a reached neighbour within USE_RANGE of it across a
        line with an opening. A use stops at a two-sided line with no gap
        (PTR_UseTraverse), so a switch behind a closed door can't be used."""
        f, _ = self.secs_of_line[i]
        if f in R:
            return f
        ln = self.m.lines[i]
        p1, p2 = self.m.verts[ln.v1], self.m.verts[ln.v2]
        for j in self.sec_lines[f]:
            fs, bs = self.secs_of_line[j]
            if bs is None:
                continue
            x = bs if fs == f else fs
            if x in R and x != f:
                l2 = self.m.lines[j]
                if (seg_dist(p1, p2, self.m.verts[l2.v1], self.m.verts[l2.v2]) <= USE_RANGE
                        and any(min(cf, cx) > max(ff, fx) for ff, cf in self._states(f, base, man)
                                for fx, cx in self._states(x, base, man))):
                    return x
        return None

    def walk_site(self, i, R, base, man, keys, actor=None):
        ln = self.m.lines[i]
        f, b = self.secs_of_line[i]
        if b is None or ln.flags & (ML_BLOCKING if actor is None else ML_BLOCKING | ML_BLOCKMONSTERS):
            return None
        if f == b:
            return f if f in R else None
        if f in R and self.can_pass(f, b, base, man, keys, actor):
            return f
        if b in R and self.can_pass(b, f, base, man, keys, actor):
            return b
        return None

    def gun_site(self, i, R, base, man):
        f, b = self.secs_of_line[i]
        if f in R or (b is not None and b in R):
            return f if f in R else b
        return self.shoot_site(self.m.midpoint(self.m.lines[i]), f, R, base, man, skip_line=i)

    def shoot_site(self, target, tsec, R, base, man, skip_line=None):
        """A reachable sector from which the player can hit `target` (a point
        in sector tsec, or the middle of line skip_line): the straight line
        to it is at most MISSILE_RANGE long, crosses no one-sided line, and
        one level height clears every opening on the way, lies within the
        shooter's possible firing heights (floor + 32 .. floor + 41) and
        inside tsec's floor..ceiling. Vertical autoaim is ignored."""
        if tsec in R:
            return tsec
        ext = {}

        def span(s):
            if s not in ext:
                st = self._states(s, base, man)
                ext[s] = (min(f for f, _ in st), max(c for _, c in st))
            return ext[s]
        tlo, thi = span(tsec)
        for d, s in sorted((math.dist(self.inner[s], target), s) for s in R):
            if d > MISSILE_RANGE:
                break
            key = (s, target, skip_line)
            if key not in self._shots:
                a = self.inner[s]
                cross = []
                for j in self.lines_near(a, target):
                    ln = self.m.lines[j]
                    p, q = self.m.verts[ln.v1], self.m.verts[ln.v2]
                    if j != skip_line and seg_cross(a, target, p, q):
                        cross.append(self.secs_of_line[j])
                self._shots[key] = cross
            fl, cl = span(s)
            top = max(f for f, _ in self._states(s, base, man)) + 41
            lo, hi = max(fl + 32, tlo), min(top, cl, thi)
            for fs, bs in self._shots[key]:
                if bs is None or lo > hi:
                    lo, hi = 1, 0
                    break
                (f1, c1), (f2, c2) = span(fs), span(bs)
                lo, hi = max(lo, f1, f2), min(hi, c1, c2)
            if lo <= hi:
                return s
        return None

    def trigger_site(self, t, R, base, man, keys):
        if t["key"] and t["key"] not in keys:
            return None
        trig = t["trig"]
        if trig[0] in "SD":
            return self.use_site(t["line"], R, base, man)
        if trig[0] == "W":
            return self.walk_site(t["line"], R, base, man, keys)
        if trig[0] == "G":
            return self.gun_site(t["line"], R, base, man)
        return None

    def key_site(self, k, R, base):
        colour, s, (x, y) = k
        if s in R:
            return s
        # touch pickup across a line: key within KEY_TOUCH of the shared line,
        # key z - player z in [-8, 56]
        m = self.m
        for i in self.sec_lines[s]:
            fs, bs = self.secs_of_line[i]
            if bs is None:
                continue
            o = bs if fs == s else fs
            if o == s or o not in R:
                continue
            ln = m.lines[i]
            if _pt_seg((x, y), m.verts[ln.v1], m.verts[ln.v2]) > KEY_TOUCH:
                continue
            if any(-8 <= fk - fo <= HEIGHT for fk, _ in base[s] for fo, _ in base[o]):
                return o
        return None

    # ------------------------------------------------------------ fixpoint --
    def run(self, off_groups=frozenset(), off_keys=frozenset(), snapshots=False):
        perm = [{st} for st in self.init]
        osc = [set() for _ in range(self.n)]
        cur = list(self.init)
        st = (perm, osc, cur)
        keys = set()
        fired = set()          # trigger indices
        stay_fired = set()
        boss_fired = set()
        res = dict(sector_wave={}, key_wave={}, key_site={}, trig_wave={}, trig_site={},
                   exit_wave={}, exit_site={}, boss_wave={}, boss_site={}, snaps=[], snap_now=[])
        wave = 0
        while True:
            base = [tuple(p) for p in perm]
            man = self.man_states(keys)
            R = self.closure(base, man, keys, [self.start])
            for s in R:
                res["sector_wave"].setdefault(s, wave)
            if snapshots:
                res["snaps"].append((base, man, frozenset(keys), frozenset(R)))
                # heights as they are now (base keeps every state a sector has had)
                res["snap_now"].append([tuple({cur[s]} | osc[s]) for s in range(self.n)])
            changed = False
            # exits
            for kind, i, trig in self.exits:
                site = (self.use_site(i, R, base, man) if trig[0] == "S"
                        else self.walk_site(i, R, base, man, keys))
                if site is not None and ("line", i) not in res["exit_wave"]:
                    res["exit_wave"][("line", i)] = wave
                    res["exit_site"][("line", i)] = site
            for s in self.exit_sectors:
                if s in R and ("sector", s) not in res["exit_wave"]:
                    res["exit_wave"][("sector", s)] = wave
                    res["exit_site"][("sector", s)] = s
            # keys
            for ki, k in enumerate(self.keys):
                if k[0] in off_keys or k[0] in keys:
                    continue
                site = self.key_site(k, R, base)
                if site is not None:
                    keys.add(k[0])
                    res["key_wave"][k[0]] = wave
                    res["key_site"][k[0]] = (site, ki)
                    changed = True
            # manual stay-open doors
            for j, (i, f, b, key) in enumerate(self.stay_doors):
                if j in stay_fired or (key and key not in keys) or f not in R:
                    continue
                stay_fired.add(j)
                changed |= self.apply("door_open", [self.nsec[b]], st)
            # tagged triggers
            for ti, t in enumerate(self.triggers):
                if ti in fired or t["group"] in off_groups:
                    continue
                site = self.trigger_site(t, R, base, man, keys)
                if site is None:
                    continue
                fired.add(ti)
                res["trig_wave"][ti] = wave
                res["trig_site"][ti] = site
                changed |= self.apply(t["action"], self.tagged.get(t["tag"], []), st)
            # boss deaths
            for bi, (types, act, tag) in enumerate(self.boss):
                if bi in boss_fired or ("boss", bi) in off_groups:
                    continue
                mons = [ms for ty in types for ms in self.monsters.get(ty, [])]
                if not mons:
                    continue
                sites = [self.shoot_site(pt, s, R, base, man) for s, pt in mons]
                if any(x is None for x in sites):
                    continue
                boss_fired.add(bi)
                res["boss_wave"][bi] = wave
                res["boss_site"][bi] = sites[0]
                if act == "exit":
                    res["exit_wave"][("boss", bi)] = wave
                    res["exit_site"][("boss", bi)] = sites[0]
                else:
                    changed |= self.apply(act, self.tagged.get(tag, []), st)
            if not changed:
                break
            wave += 1
        res["R"] = R
        res["waves"] = wave
        res["keys"] = keys
        res["perm"], res["osc"], res["cur"] = perm, osc, cur
        res["final_man"] = self.man_states(keys)
        return res

    def monster_closure(self, res, start, actor):
        """Regions a monster (doom2.Actor) starting in region `start` gets to
        at the end of the player's run `res`, firing on the way the
        MONSTER_WALK lines the player didn't."""
        perm, osc, cur = [set(p) for p in res["perm"]], [set(o) for o in res["osc"]], list(res["cur"])
        man = self.man_states((), actor)
        todo = [t for ti, t in enumerate(self.triggers) if t["special"] in MONSTER_WALK and ti not in res["trig_wave"]]
        while True:
            base = [tuple({cur[s]} | osc[s]) for s in range(self.n)]
            R = self.closure(base, man, (), [start], actor)
            fire = [t for t in todo if self.walk_site(t["line"], R, base, man, (), actor) is not None]
            if not fire:
                return R
            for t in fire:
                todo.remove(t)
                self.apply(t["action"], self.tagged.get(t["tag"], []), (perm, osc, cur))

    def normal_exit(self, res):
        """(wave, site, key) of the earliest normal exit reached."""
        best = None
        for key, w in res["exit_wave"].items():
            if key[0] == "line":
                kind = next(k for k, i, _ in self.exits if i == key[1])
                if kind != "exit":
                    continue
            if best is None or w < best[0]:
                best = (w, res["exit_site"][key], key)
        return best

    def secret_exit(self, res):
        best = None
        for key, w in res["exit_wave"].items():
            if key[0] != "line":
                continue
            kind = next(k for k, i, _ in self.exits if i == key[1])
            if kind == "secret_exit" and (best is None or w < best[0]):
                best = (w, res["exit_site"][key], key)
        return best


def solve(m, textures, boss=None):
    """(model, run with snapshots) of a map. The conservative model first
    (walking, trench/ledge straddling, no running jumps); running jumps only
    if the exit can't be reached without them, since jumps also open
    unintended sequence breaks. md.use_jumps says which. boss: UMAPINFO boss
    deaths in place of the slot's vanilla ones (see umapinfo_boss)."""
    md = Model(m, textures, use_jumps=False, boss=boss)
    res = md.run(snapshots=True)
    if md.normal_exit(res) is None:
        md = Model(m, textures, use_jumps=True, boss=boss)
        res = md.run(snapshots=True)
    return md, res
