#!/usr/bin/env python3
"""Scripted, headless playtests of DOOM II maps, run in ViZDoom.

    uv run --with vizdoom scripts/tools/playtest.py WAD MAP SCRIPT [--skill 4] [--shots DIR] [--from NAME]
    python3 scripts/tools/playtest.py WAD MAP --describe     # start, keys, special lines (no ViZDoom needed)

ViZDoom (pip install vizdoom) runs a ZDoom-based engine as a Python library.
The script drives the player with real inputs, as fast as the machine runs
the game: a minute of play takes a few seconds, with no window.

SCRIPT is a text file, one step per line, `#` starts a comment. Coordinates
are map units; a line is named by any point within 8 units of it (use its
midpoint). Steps run in order:

    walk X Y [X Y ...]        run to each point in turn. The runner finds its own way there
                              round walls, pillars, steps too high to climb and closed doors,
                              and avoids damaging floors when it can; extra points only
                              matter to force a route. Picks up items, crosses walk-over
                              lines, enters secrets. Fails if there's no way there, or the
                              player makes no progress for 2 s.
    open X Y                  walk up to that line, open the door behind it from the player's
                              side and wait until it's passable. A door already open is left
                              alone (using an open DR door would close it again).
    use X Y                   walk up to that line and press use on it (switches)
    exit X Y                  `use` an exit line, then expect the level to end within 3 s
    shoot X Y                 face the line and fire (gun-activated lines)
    teleport X Y [ANGLE]      put the player at X Y (ANGLE: 0 east, 90 north)
    give ITEM                 console `give`, e.g. bluecard, rocketlauncher
    killall                   kill every monster (so they don't block `walk`)
    look ANGLE [PITCH]        turn the view (PITCH: positive looks down)
    wait TICS                 35 tics = 1 second of game time
    shot NAME                 screenshot to SHOTS/NAME.png, then hold still for 1 s
    checkpoint NAME           save the game here; `--from NAME` starts from this point
    expect floor X Y OP N     floor height at X Y        OP: == != < <= > >=
    expect ceil X Y OP N      ceiling height at X Y (doors: open when ceil > floor)
    expect has ITEM           the player has picked up an ITEM (or been given one): a pickup
                              of that class is gone from the map. BasicArmor means any armor;
                              PowerIronFeet the radiation suit. Keys and weapons by class name.
    expect pos X Y [TOL]      player within TOL (default 16) of X Y
    expect secrets OP N       secrets found;  also: kills, items

`--from NAME` loads the save made at `checkpoint NAME` by an earlier run and
carries on after it. A save only counts if the WAD, map, skill and every
script line up to the checkpoint are unchanged; otherwise the run says so and
starts from the beginning, saving checkpoints as it goes. Saves live in
~/.cache/playtest/.

The player has god mode and notarget, so tests check wiring, not balance.
Exit status: 0 all checks passed, 1 a check failed, 2 the engine or script broke.
"""
import argparse
import hashlib
import heapq
import json
import math
import os
import re
import struct
import sys
import time
import zlib

DEFAULT_IWAD = os.environ.get("DOOM2_WAD", os.path.expanduser("~/.local/share/dsda-doom/doom2.wad"))
CACHE = os.path.expanduser("~/.cache/playtest")
WIDTH, HEIGHT = 640, 480
OPS = {"==": lambda a, b: a == b, "!=": lambda a, b: a != b, "<": lambda a, b: a < b,
       "<=": lambda a, b: a <= b, ">": lambda a, b: a > b, ">=": lambda a, b: a >= b}
COUNTERS = {"secrets": "SECRETCOUNT", "kills": "KILLCOUNT", "items": "ITEMCOUNT"}
# `expect has` names whose pickups have other class names.
PICKUPS = {"PowerIronFeet": ("RadSuit",), "BasicArmor": ("GreenArmor", "BlueArmor")}

RADIUS, HEIGHT_P, STEP, USE_RANGE = 16, 56, 24, 64
GRID = 16
DAMAGING = {4, 5, 7, 11, 16}
LIFTS = {10, 21, 62, 88, 120, 121, 122, 123}   # lift specials: their tagged sectors move up and down
USE_DOORS = {1, 26, 27, 28, 31, 32, 33, 34, 117, 118}   # doors the player opens by using them
STUCK_TICS, ARRIVE, PASS_BY = 70, 3, 24
# Solid decorations the player has to go round, by radius. Monsters aren't here:
# scripts kill them first, and their corpses keep their names.
SOLID = {"ExplosiveBarrel": 10, "TechLamp": 16, "TechLamp2": 16, "Column": 16, "TallGreenColumn": 16,
         "ShortGreenColumn": 16, "TallRedColumn": 16, "ShortRedColumn": 16, "BlueTorch": 16, "GreenTorch": 16,
         "RedTorch": 16, "ShortBlueTorch": 16, "ShortGreenTorch": 16, "ShortRedTorch": 16, "Candelabra": 16,
         "TechPillar": 16, "EvilEye": 16, "FloatingSkull": 16, "HeartColumn": 16, "SkullColumn": 16,
         "Stalagtite": 16, "TorchTree": 16, "BigTree": 32, "HangNoGuts": 16}


class ScriptError(Exception):
    pass


class Abort(Exception):
    """The run can't go on (stuck, no route, the level ended early)."""


# ------------------------------------------------------------------ map ---

def read_map(path, name):
    with open(path, "rb") as f:
        data = f.read()
    n, off = struct.unpack("<ii", data[4:12])
    lumps = [struct.unpack("<ii8s", data[off + 16 * i: off + 16 * i + 16]) for i in range(n)]
    names = [nm.split(b"\0")[0].decode() for _, _, nm in lumps]
    if name not in names:
        return None
    i = names.index(name)
    return {names[j]: data[lumps[j][0]:lumps[j][0] + lumps[j][1]] for j in range(i + 1, min(i + 12, n))}


def find_map(wads, name):
    for wad in reversed(wads):
        m = read_map(wad, name)
        if m and "LINEDEFS" in m:
            return m
    return None


def seg_dist(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx - ax, by - ay
    l2 = dx * dx + dy * dy
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2)) if l2 else 0.0
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


class Geometry:
    """The map's static layout from its lumps. Heights come from the live game."""

    def __init__(self, m):
        self.verts = list(struct.iter_unpack("<hh", m["VERTEXES"]))
        sides = list(struct.iter_unpack("<hh8s8s8sh", m["SIDEDEFS"]))
        self.sectors = list(struct.iter_unpack("<hh8s8shhh", m["SECTORS"]))
        self.lines = []   # (a, b, flags, special, tag, front sector, back sector or None)
        for v1, v2, flags, special, tag, front, back in struct.iter_unpack("<hhhhhhh", m["LINEDEFS"]):
            fs = sides[front][5]
            bs = sides[back][5] if back >= 0 else None
            self.lines.append((self.verts[v1], self.verts[v2], flags, special, tag, fs, bs))
        self.things = list(struct.iter_unpack("<hhhhh", m["THINGS"]))
        self.sector_lines = [[] for _ in self.sectors]
        for i, (a, b, _, _, _, fs, bs) in enumerate(self.lines):
            self.sector_lines[fs].append(i)
            if bs is not None and bs != fs:
                self.sector_lines[bs].append(i)
        lift_tags = {tag for _, _, _, sp, tag, _, _ in self.lines if sp in LIFTS and tag}
        self.doors = {bs for _, _, _, sp, _, _, bs in self.lines if sp in USE_DOORS and bs is not None}
        self.lifts = {i for i, s in enumerate(self.sectors) if s[6] in lift_tags}
        self.damaging = {i for i, s in enumerate(self.sectors) if s[5] in DAMAGING}
        xs = [x for x, _ in self.verts]
        ys = [y for _, y in self.verts]
        self.x0, self.y0 = min(xs) // GRID * GRID, min(ys) // GRID * GRID
        self.nx, self.ny = (max(xs) - self.x0) // GRID + 1, (max(ys) - self.y0) // GRID + 1
        self.cell_sector = self.raster(GRID)

    def sector_at(self, p):
        """Sector index containing p (even-odd over each sector's lines), or None."""
        x, y = p
        for s, idx in enumerate(self.sector_lines):
            inside = False
            for i in idx:
                (x1, y1), (x2, y2) = self.lines[i][:2]
                if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
                    inside = not inside
            if inside:
                return s
        return None

    def raster(self, step):
        """Sector index at the centre of each step-sized cell from the map's
        corner (None outside the map), by scanlines."""
        nx, ny = self.nx * GRID // step, self.ny * GRID // step
        grid = [[None] * nx for _ in range(ny)]
        for j in range(ny):
            y = self.y0 + j * step + step / 2 + 1 / 1024
            hits = []
            for (x1, y1), (x2, y2), _, _, _, fs, bs in self.lines:
                if (y1 > y) != (y2 > y):
                    x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                    # The sector on the +x side: the front (right) side if the line runs upward.
                    hits.append((x, fs if y2 > y1 else bs))
            hits.sort()
            row = grid[j]
            k = 0
            for i in range(nx):
                x = self.x0 + i * step + step / 2
                while k < len(hits) and hits[k][0] <= x:
                    k += 1
                row[i] = hits[k - 1][1] if k else None
        return grid

    def neighbours(self, s):
        return {o for i in self.sector_lines[s] for o in self.lines[i][5:7] if o is not None and o != s}

    def line_near(self, p, within=8):
        best, bd = None, within
        for i, (a, b, *_rest) in enumerate(self.lines):
            d = seg_dist(p, a, b)
            if d <= bd:
                best, bd = i, d
        return best


# -------------------------------------------------------------- routing ---

def box_hits(a, b, cx, cy, r):
    """The segment a-b passes through the square of half-size r centred on cx, cy."""
    (x1, y1), (x2, y2) = a, b
    t0, t1 = 0.0, 1.0
    dx, dy = x2 - x1, y2 - y1
    for p, q in ((-dx, x1 - (cx - r)), (dx, (cx + r) - x1), (-dy, y1 - (cy - r)), (dy, (cy + r) - y1)):
        if p == 0:
            if q < 0:
                return False
        else:
            t = q / p
            if p < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
            if t0 > t1:
                return False
    return True


class Planner:
    """Grid A* for the player's 32-unit box over the live map. Like Doom, a
    cell's floor is the highest floor anywhere under the box there and its
    ceiling the lowest ceiling; the player can step up 24, drop any height,
    and needs 56 of headroom. Lifts count as passable whatever their height."""

    def __init__(self, geo):
        self.g = g = geo
        self._levels = (None, None)
        fine = g.raster(GRID // 2)
        self.under = []   # per cell: the sectors under the player's box there
        self.wall = []    # per cell: a wall (one-sided or blocking line) cuts the box
        walls = [(a, b) for a, b, flags, _sp, _t, _fs, bs in g.lines if bs is None or flags & 1]
        for j in range(g.ny):
            urow, wrow = [], []
            cy = g.y0 + j * GRID + GRID / 2
            for i in range(g.nx):
                cx = g.x0 + i * GRID + GRID / 2
                ss = {fine[jj][ii] for jj in range(2 * j - 1, 2 * j + 4) for ii in range(2 * i - 1, 2 * i + 4)
                      if 0 <= jj < len(fine) and 0 <= ii < len(fine[0])}
                urow.append(frozenset(s for s in ss if s is not None) if None not in ss else None)
                wrow.append(False)
            self.under.append(urow)
            self.wall.append(wrow)
        for a, b in walls:
            i0 = max(0, int((min(a[0], b[0]) - RADIUS - g.x0) // GRID))
            i1 = min(g.nx - 1, int((max(a[0], b[0]) + RADIUS - g.x0) // GRID))
            j0 = max(0, int((min(a[1], b[1]) - RADIUS - g.y0) // GRID))
            j1 = min(g.ny - 1, int((max(a[1], b[1]) + RADIUS - g.y0) // GRID))
            for jj in range(j0, j1 + 1):
                for ii in range(i0, i1 + 1):
                    if box_hits(a, b, g.x0 + ii * GRID + GRID / 2, g.y0 + jj * GRID + GRID / 2, RADIUS):
                        self.wall[jj][ii] = True

    def cell(self, p):
        return (int((p[0] - self.g.x0) // GRID), int((p[1] - self.g.y0) // GRID))

    def centre(self, c):
        return (self.g.x0 + c[0] * GRID + GRID / 2, self.g.y0 + c[1] * GRID + GRID / 2)

    def levels(self, h, things):
        """Per cell: (floor, ceiling, on a lift) for the box there, or None if the
        player can't stand there at all. Reused until a height or a thing moves."""
        key = (tuple(h), tuple(things))
        if self._levels[0] == key:
            return self._levels[1]
        out = self._levels_for(h, things)
        self._levels = (key, out)
        return out

    def _levels_for(self, h, things):
        g = self.g
        out = []
        for j in range(g.ny):
            row = []
            for i in range(g.nx):
                ss = self.under[j][i]
                if ss is None or self.wall[j][i]:
                    row.append(None)
                    continue
                f = max(h[s][0] for s in ss)
                c = min(h[s][1] for s in ss)
                lift = any(s in g.lifts for s in ss)
                row.append(None if c - f < HEIGHT_P and not lift else (f, c, lift))
            out.append(row)
        for x, y, tr in things:   # Doom blocks things as squares
            reach = tr + RADIUS
            for j in range(max(0, int((y - reach - g.y0) // GRID)), min(g.ny, int((y + reach - g.y0) // GRID) + 1)):
                for i in range(max(0, int((x - reach - g.x0) // GRID)), min(g.nx, int((x + reach - g.x0) // GRID) + 1)):
                    cx, cy = self.centre((i, j))
                    if abs(cx - x) < reach and abs(cy - y) < reach:
                        out[j][i] = None
        return out

    @staticmethod
    def step_ok(a, b):
        """The player can move from a cell at level a to one at level b."""
        if a is None or b is None:
            return False
        if a[2] or b[2]:
            return True
        return b[0] - a[0] <= STEP and min(a[1], b[1]) - b[0] >= HEIGHT_P

    def free_near(self, c, lv, reach=3):
        best = None
        for dj in range(-reach, reach + 1):
            for di in range(-reach, reach + 1):
                i, j = c[0] + di, c[1] + dj
                if 0 <= i < self.g.nx and 0 <= j < self.g.ny and lv[j][i] is not None:
                    d = di * di + dj * dj
                    if best is None or d < best[0]:
                        best = (d, (i, j))
        return best and best[1]

    def route(self, start, goal, h, things=()):
        """Waypoints from start to goal, or None if there's no way. things:
        [(x, y, radius)] of solid things in the way."""
        g = self.g
        lv = self.levels(h, things)
        s, t = self.free_near(self.cell(start), lv), self.free_near(self.cell(goal), lv)
        if s is None or t is None:
            return None
        dmg = lambda c: g.cell_sector[c[1]][c[0]] in g.damaging  # noqa: E731
        dist, prev, todo = {s: 0.0}, {}, [(0.0, 0.0, s)]
        while todo:
            _, d, c = heapq.heappop(todo)
            if c == t:
                break
            if d > dist[c]:
                continue
            here = lv[c[1]][c[0]]
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                n = (c[0] + di, c[1] + dj)
                if not (0 <= n[0] < g.nx and 0 <= n[1] < g.ny) or not self.step_ok(here, lv[n[1]][n[0]]):
                    continue
                if di and dj and not (self.step_ok(here, lv[c[1]][n[0]]) and self.step_ok(here, lv[n[1]][c[0]])):
                    continue   # no cutting corners
                nd = d + math.hypot(di, dj) * (20 if dmg(n) else 1)
                if nd < dist.get(n, 1e18):
                    dist[n], prev[n] = nd, c
                    heapq.heappush(todo, (nd + math.hypot(t[0] - n[0], t[1] - n[1]), nd, n))
        if t not in dist:
            return None
        path = [t]
        while path[-1] != s:
            path.append(prev[path[-1]])
        path.reverse()
        pts = self.smooth(path, lv)
        if t == self.cell(goal):
            pts[-1] = goal
        return pts

    def smooth(self, path, lv):
        """Waypoints: the grid path with every corner a straight run can skip
        dropped, never shortcutting onto a damaging floor the path avoided."""
        out, i = [], 0
        while i < len(path) - 1:
            j = len(path) - 1
            while j > i + 1 and not self.straight(path[i], path[j], lv, path[i:j + 1]):
                j -= 1
            out.append(self.centre(path[j]))
            i = j
        return out or [self.centre(path[-1])]

    def straight(self, a, b, lv, along):
        g = self.g
        dmg_ok = {g.cell_sector[c[1]][c[0]] for c in along} & g.damaging
        pa, pb = self.centre(a), self.centre(b)
        n = max(1, int(math.dist(pa, pb) / 4))
        prev = lv[a[1]][a[0]]
        for k in range(1, n + 1):
            c = self.cell((pa[0] + (pb[0] - pa[0]) * k / n, pa[1] + (pb[1] - pa[1]) * k / n))
            here = lv[c[1]][c[0]]
            if here is not prev and not self.step_ok(prev, here):
                return False
            s = g.cell_sector[c[1]][c[0]]
            if s in g.damaging and s not in dmg_ok:
                return False
            prev = here
        return True


# ------------------------------------------------------------------ run ---

def parse(text):
    """Script text -> [(line number, command, args, source line)]."""
    steps = []
    for ln, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        cmd, *args = line.split()
        steps.append((ln, cmd, args, line))
        check_step(ln, cmd, args, raw)
    return steps


def check_step(ln, cmd, args, raw):
    def need(lo, hi=None):
        hi = lo if hi is None else hi
        if not lo <= len(args) <= hi:
            raise ScriptError(f"line {ln}: `{cmd}` takes {lo}" + (f"-{hi}" if hi != lo else "") + f" arguments: {raw.strip()}")

    def nums(*idx):
        for i in idx:
            try:
                float(args[i])
            except ValueError:
                raise ScriptError(f"line {ln}: expected a number, got {args[i]!r}")

    if cmd == "walk":
        if len(args) < 2 or len(args) % 2:
            raise ScriptError(f"line {ln}: `walk` takes X Y pairs: {raw.strip()}")
        nums(*range(len(args)))
    elif cmd in ("open", "use", "exit", "shoot"):
        need(2), nums(0, 1)
    elif cmd == "teleport":
        need(2, 3), nums(*range(len(args)))
    elif cmd in ("give", "checkpoint"):
        need(1)
        if cmd == "checkpoint" and not re.fullmatch(r"[\w.-]+", args[0]):
            raise ScriptError(f"line {ln}: checkpoint name must be letters, digits, _ . -")
    elif cmd == "killall":
        need(0)
    elif cmd == "look":
        need(1, 2), nums(*range(len(args)))
    elif cmd == "wait":
        need(1), nums(0)
    elif cmd == "shot":
        need(1)
        if not re.fullmatch(r"[\w.-]+", args[0]):
            raise ScriptError(f"line {ln}: shot name must be letters, digits, _ . -")
    elif cmd == "expect":
        what, rest = (args[0], args[1:]) if args else (None, [])
        if what in ("floor", "ceil"):
            if len(rest) != 4 or rest[2] not in OPS:
                raise ScriptError(f"line {ln}: expect {what} X Y OP N")
        elif what == "has":
            if len(rest) != 1:
                raise ScriptError(f"line {ln}: expect has ITEM")
        elif what == "pos":
            if len(rest) not in (2, 3):
                raise ScriptError(f"line {ln}: expect pos X Y [TOL]")
        elif what in COUNTERS:
            if len(rest) != 2 or rest[0] not in OPS:
                raise ScriptError(f"line {ln}: expect {what} OP N")
        else:
            raise ScriptError(f"line {ln}: unknown expect subject {what!r}")
    else:
        raise ScriptError(f"line {ln}: unknown step {cmd!r}")


def write_png(path, rgb):
    h, w = rgb.shape[:2]
    raw = b"".join(b"\0" + rgb[y].tobytes() for y in range(h))

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw, 3)) + chunk(b"IEND", b""))


class Run:
    def __init__(self, args, vzd, geo):
        self.args, self.vzd, self.geo = args, vzd, geo
        self.plan = Planner(geo)
        self.checks = self.fails = 0
        self.had = set()      # item classes picked up or given
        self.seen = {}        # object id -> class name, for pickups that vanish
        self._state = None
        self.shots = args.shots or os.path.join("/tmp", "playtest-shots", args.map.upper())
        os.makedirs(self.shots, exist_ok=True)
        g = self.game = vzd.DoomGame()
        g.set_doom_game_path(args.iwad)
        g.set_doom_scenario_path(args.wad[0])
        if args.wad[1:]:
            g.add_game_args("-file " + " ".join(args.wad[1:]))
        g.set_doom_map(args.map.upper())
        g.set_doom_skill(args.skill)
        g.set_window_visible(False)
        g.set_mode(vzd.Mode.PLAYER)
        g.set_screen_resolution(vzd.ScreenResolution.RES_640X480)
        g.set_screen_format(vzd.ScreenFormat.RGB24)
        g.set_render_hud(True)
        g.set_sectors_info_enabled(True)
        g.set_objects_info_enabled(True)
        g.set_sound_enabled(False)
        B = vzd.Button
        g.set_available_buttons([B.MOVE_FORWARD_BACKWARD_DELTA, B.MOVE_LEFT_RIGHT_DELTA, B.TURN_LEFT_RIGHT_DELTA,
                                 B.LOOK_UP_DOWN_DELTA, B.USE, B.ATTACK, B.SPEED])
        V = vzd.GameVariable
        self.vars = ["POSITION_X", "POSITION_Y", "POSITION_Z", "ANGLE", "PITCH", "VELOCITY_X", "VELOCITY_Y",
                     "ARMOR", *COUNTERS.values()]
        g.set_available_game_variables([getattr(V, v) for v in self.vars])
        g.add_game_args("+sv_cheats 1")
        g.init()

    # -- the game ------------------------------------------------------------
    def tic(self, fwd=0.0, side=0.0, turn=0.0, look=0.0, use=0, attack=0, n=1):
        g = self.game
        if g.is_episode_finished():
            raise Abort("the level ended before the script finished")
        g.make_action([fwd, side, turn, look, use, attack, 1], n)
        self._state = None
        if not g.is_episode_finished():
            self.watch()

    def state(self):
        """The game state after the last tic (fetched once: it copies the screen)."""
        if self._state is None:
            self._state = self.game.get_state()
            if self._state is None:
                raise Abort("the level ended before the script finished")
        return self._state

    def var(self, name):
        return float(self.state().game_variables[self.vars.index(name)])

    def pos(self):
        v = self.state().game_variables
        return float(v[0]), float(v[1])

    def heights(self):
        return [(float(s.floor_height), float(s.ceiling_height)) for s in self.state().sectors]

    def watch(self):
        objs = {o.id: o.name for o in self.state().objects}
        for oid, name in self.seen.items():
            if oid not in objs:
                self.had.add(name)
        self.seen.update(objs)
        self.seen = {k: v for k, v in self.seen.items() if k in objs}

    def say(self, s):
        print(s, flush=True)

    def check(self, ok, ln, what):
        self.checks += 1
        if not ok:
            self.fails += 1
        self.say(f"{'PASS' if ok else 'FAIL'} {ln}: {what}")

    # -- moving --------------------------------------------------------------
    def face(self, target, pitch=None):
        """Turn to face a point or an angle (degrees, 0 east)."""
        for _ in range(3):
            if isinstance(target, tuple):
                x, y = self.pos()
                want = math.degrees(math.atan2(target[1] - y, target[0] - x))
            else:
                want = target
            turn = (self.var("ANGLE") - want + 180) % 360 - 180   # positive turns right
            look = 0.0 if pitch is None else pitch - (-self.var("PITCH"))
            if abs(turn) < 0.5 and abs(look) < 0.5:
                return
            self.tic(turn=turn, look=-look if pitch is not None else 0.0)

    def drive(self, target, ln, final):
        """Run at target; on the last leg brake to stop within ARRIVE units."""
        last, since, presses = self.pos(), 0, 0
        while True:
            x, y = self.pos()
            dx, dy = target[0] - x, target[1] - y
            dist = math.hypot(dx, dy)
            vx, vy = self.var("VELOCITY_X"), self.var("VELOCITY_Y")
            speed = math.hypot(vx, vy)
            if dist <= (ARRIVE if final else PASS_BY) and (not final or speed < 1):
                if final:
                    self.tic()
                return
            # Speed to aim for: full run, slowing on the final approach.
            want = min(16.0, dist * 0.2 + 0.3) if final else 16.0
            ux, uy = dx / dist, dy / dist
            ex, ey = ux * want - vx, uy * want - vy     # velocity error, in world space
            ang = math.radians(self.var("ANGLE"))
            fwd = ex * math.cos(ang) + ey * math.sin(ang)
            side = ex * math.sin(ang) - ey * math.cos(ang)
            turn = (self.var("ANGLE") - math.degrees(math.atan2(dy, dx)) + 180) % 360 - 180
            k = 25
            self.tic(fwd=max(-100, min(100, fwd * k)), side=max(-100, min(100, side * k)),
                     turn=max(-30, min(30, turn)))
            now = self.pos()
            if math.dist(now, last) > 8:
                last, since = now, 0
            else:
                since += 1
                if since == STUCK_TICS // 3 and presses < 3:
                    # As a player would: use whatever is in the way (a door that closed
                    # again, a lift that went back up) and give it time to move. A
                    # moving lift ignores use, so try a few times.
                    self.face(target)
                    self.press()
                    presses, since = presses + 1, 0
                if since > STUCK_TICS:
                    raise Abort(f"line {ln}: walk stuck at {now[0]:.0f},{now[1]:.0f} (z {self.var('POSITION_Z'):.0f}) "
                                f"heading for {target[0]:.0f},{target[1]:.0f}")

    def walk_to(self, target, ln, final=True):
        solid = [(round(o.position_x), round(o.position_y), SOLID[o.name]) for o in self.state().objects
                 if o.name in SOLID]
        h = self.heights()
        pts = self.plan.route(self.pos(), target, h, solid)
        if pts is None:
            # Through doors the player can open: they get used on the way, when bumped into.
            g = self.geo
            opened = list(h)
            for d in g.doors:
                top = min(h[n][1] for n in g.neighbours(d)) - 4
                opened[d] = (h[d][0], max(h[d][1], top))
            pts = self.plan.route(self.pos(), target, opened, solid)
        if pts is None:
            raise Abort(f"line {ln}: no way from {self.pos()[0]:.0f},{self.pos()[1]:.0f} "
                        f"to {target[0]:.0f},{target[1]:.0f}")
        for k, p in enumerate(pts):
            self.drive(p, ln, final and k == len(pts) - 1)

    def line(self, x, y, ln):
        i = self.geo.line_near((x, y))
        if i is None:
            raise Abort(f"line {ln}: no line within 8 units of {x:g},{y:g}")
        return i

    def side_of(self, i, p):
        """0 if p is on line i's front (right) side, else 1."""
        (x1, y1), (x2, y2) = self.geo.lines[i][:2]
        return 0 if (x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1) <= 0 else 1

    def approach(self, i, ln):
        """Walk to a point in front of line i's midpoint, on the player's side,
        and face the midpoint."""
        (x1, y1), (x2, y2) = self.geo.lines[i][:2]
        mid = ((x1 + x2) / 2, (y1 + y2) / 2)
        if seg_dist(self.pos(), (x1, y1), (x2, y2)) > USE_RANGE - 20:
            nx, ny = (y2 - y1), -(x2 - x1)   # the front (right) side's normal
            n = math.hypot(nx, ny)
            sign = 1 if self.side_of(i, self.pos()) == 0 else -1
            spot = (mid[0] + sign * nx / n * 32, mid[1] + sign * ny / n * 32)
            self.walk_to(spot, ln)
        self.face(mid)
        d = seg_dist(self.pos(), (x1, y1), (x2, y2))
        if d > USE_RANGE:
            raise Abort(f"line {ln}: couldn't get within {USE_RANGE} of the line (got to {d:.0f})")

    def press(self, button="use"):
        self.tic(use=int(button == "use"), attack=int(button == "attack"))
        self.tic(n=2)

    def door_gap(self, i):
        """Opening height of the sector across line i from the player, or None."""
        a, b, _f, _s, _t, fs, bs = self.geo.lines[i]
        if bs is None:
            return None
        far = bs if self.side_of(i, self.pos()) == 0 else fs
        h = self.heights()[far]
        return h[1] - h[0]

    # -- steps ---------------------------------------------------------------
    def step(self, ln, cmd, a, line):
        num = [float(v) for v in a] if cmd not in ("give", "checkpoint", "shot", "expect") else None
        if cmd == "walk":
            for k in range(0, len(num), 2):
                self.walk_to((num[k], num[k + 1]), ln)
        elif cmd == "open":
            i = self.line(num[0], num[1], ln)
            gap = self.door_gap(i)
            if gap is None:
                raise Abort(f"line {ln}: open: one-sided line; use `use` for switches")
            if gap >= HEIGHT_P:
                return
            self.approach(i, ln)
            self.press()
            last = None
            for _ in range(140):   # until the door is passable and has stopped rising
                gap = self.door_gap(i)
                if gap >= HEIGHT_P and gap == last:
                    return
                last = gap
                self.tic()
            if self.door_gap(i) < HEIGHT_P:
                self.check(False, ln, f"open: door still only {self.door_gap(i):.0f} high after 4 s")
        elif cmd in ("use", "exit"):
            i = self.line(num[0], num[1], ln)
            self.approach(i, ln)
            self.press()
            if cmd == "exit":
                for _ in range(105):
                    if self.game.is_episode_finished():
                        break
                    self.tic()
                self.check(self.game.is_episode_finished(), ln,
                           "level exited" if self.game.is_episode_finished() else "the level did not end within 3 s")
        elif cmd == "shoot":
            i = self.line(num[0], num[1], ln)
            (x1, y1), (x2, y2) = self.geo.lines[i][:2]
            self.face(((x1 + x2) / 2, (y1 + y2) / 2))
            self.press("attack")
        elif cmd == "teleport":
            self.game.send_game_command(f"warp {num[0]:g} {num[1]:g}")
            self.tic()
            if len(num) == 3:
                self.face(num[2])
        elif cmd == "give":
            self.game.send_game_command(f"give {a[0]}")
            self.had.add(a[0].lower())
            self.tic()
        elif cmd == "killall":
            self.game.send_game_command("kill monsters")
            self.tic()
        elif cmd == "look":
            self.face(num[0], num[1] if len(num) == 2 else None)
        elif cmd == "wait":
            for _ in range(int(num[0])):
                self.tic()
        elif cmd == "shot":
            path = os.path.join(self.shots, a[0] + ".png")
            write_png(path, self.state().screen_buffer)
            self.say(f"shot {path}")
            for _ in range(35):
                self.tic()
        elif cmd == "checkpoint":
            path = self.save_path(a[0])
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.game.save(path)
            with open(path + ".json", "w") as f:
                json.dump({"had": sorted(self.had), "checks": self.checks, "fails": self.fails}, f)
            self.say(f"checkpoint {a[0]} saved")
        elif cmd == "expect":
            self.expect(ln, a, line)

    def expect(self, ln, a, line):
        what, rest = a[0], a[1:]
        if what in ("floor", "ceil"):
            x, y, op, n = float(rest[0]), float(rest[1]), rest[2], float(rest[3])
            s = self.geo.sector_at((x, y))
            if s is None:
                self.check(False, ln, f"{line} (no sector there)")
                return
            v = self.heights()[s][0 if what == "floor" else 1]
            self.check(OPS[op](v, n), ln, f"{line} (it is {v:.0f})")
        elif what == "has":
            item = rest[0]
            if item == "BasicArmor":
                ok = self.var("ARMOR") > 0
            else:
                names = {n.lower() for n in PICKUPS.get(item, (item,))}
                ok = bool({h.lower() for h in self.had} & (names | {item.lower()}))
            self.check(ok, ln, line)
        elif what == "pos":
            x, y = float(rest[0]), float(rest[1])
            tol = float(rest[2]) if len(rest) == 3 else 16
            px, py = self.pos()
            self.check(math.hypot(px - x, py - y) <= tol, ln, f"{line} (player at {px:.0f},{py:.0f})")
        else:
            v = int(self.var(COUNTERS[what]))
            self.check(OPS[rest[0]](v, int(rest[1])), ln, f"{line} (it is {v})")

    # -- checkpoints ---------------------------------------------------------
    def key(self, upto):
        h = hashlib.sha256()
        for w in self.args.wad:
            h.update(open(w, "rb").read())
        h.update(f"{self.args.map.upper()}|{self.args.skill}|".encode())
        h.update("\n".join(s[3] for s in self.steps[:upto + 1]).encode())
        return h.hexdigest()[:16]

    def save_path(self, name):
        k = next(i for i, s in enumerate(self.steps) if s[1] == "checkpoint" and s[2][0] == name)
        return os.path.join(CACHE, self.key(k), name + ".zds")

    def go(self, steps, start_from=None):
        self.steps = steps
        begin = 0
        if start_from:
            names = [s[2][0] for s in steps if s[1] == "checkpoint"]
            if start_from not in names:
                raise ScriptError(f"no `checkpoint {start_from}` in the script")
            path = self.save_path(start_from)
            if os.path.exists(path):
                self.game.load(path)
                self.tic()
                saved = json.load(open(path + ".json"))
                self.had = set(saved["had"])
                self.checks, self.fails = saved["checks"], saved["fails"]
                begin = next(i for i, s in enumerate(steps) if s[1] == "checkpoint" and s[2][0] == start_from) + 1
                self.say(f"resumed at checkpoint {start_from} ({self.checks} checks before it, {self.fails} failed)")
            else:
                self.say(f"no current save for checkpoint {start_from} (the WAD, skill or an earlier step changed, "
                         f"or it was never reached); running from the start")
        if begin == 0:
            for c in ("god", "notarget"):
                self.game.send_game_command(c)
            self.tic(n=35)    # the engine ignores turning for the first tics of a level
            self.say(f"START {self.args.map.upper()} skill {self.args.skill}")
        for ln, cmd, a, line in steps[begin:]:
            self.say(f"STEP {ln}: {line}")
            self.step(ln, cmd, a, line)


def run(args):
    try:
        import vizdoom as vzd
    except ImportError:
        print("playtests need ViZDoom: run with `uv run --with vizdoom scripts/tools/playtest.py ...`, "
              "or `pip install vizdoom` in a virtualenv")
        return 2
    try:
        steps = parse(open(args.script).read())
    except ScriptError as e:
        print("script error:", e)
        return 2
    m = find_map(args.wad, args.map.upper())
    if not m:
        print(f"{args.map} not found as a Doom-format map in {args.wad}")
        return 2
    t0 = time.time()
    r = Run(args, vzd, Geometry(m))
    status = None
    try:
        r.go(steps, args.start_from)
    except Abort as e:
        r.fails += 1
        r.say(f"FAIL {e}")
        status = 1
    except ScriptError as e:
        print("script error:", e)
        status = 2
    finally:
        r.game.close()
    print(f"DONE checks={r.checks} fails={r.fails} ({time.time() - t0:.1f} s)")
    return status if status is not None else (1 if r.fails else 0)


# ------------------------------------------------------------- describe ---

SPECIAL_NAMES = {
    1: "DR door", 26: "DR blue door", 27: "DR yellow door", 28: "DR red door", 31: "D1 door", 32: "D1 blue door",
    33: "D1 red door", 34: "D1 yellow door", 11: "S1 exit", 51: "S1 secret exit", 52: "W1 exit",
    124: "W1 secret exit", 39: "W1 teleport", 97: "WR teleport", 62: "SR lift", 88: "WR lift", 21: "S1 lift",
    10: "W1 lift", 103: "S1 door open", 2: "W1 door open", 61: "SR door open", 86: "WR door open",
    23: "S1 floor lowest", 38: "W1 floor lowest", 60: "SR floor lowest", 82: "WR floor lowest",
    20: "S1 raise & change", 22: "W1 raise & change", 68: "SR raise & change", 95: "WR raise & change",
    13: "W1 light 255", 35: "W1 light 35", 46: "GR door open", 24: "G1 floor raise", 47: "G1 floor raise",
}
THING_NAMES = {1: "player 1 start", 5: "blue keycard", 6: "yellow keycard", 13: "red keycard",
               40: "blue skull", 39: "yellow skull", 38: "red skull", 14: "teleport destination"}


def describe(args):
    m = find_map(args.wad, args.map.upper())
    if not m:
        print(f"{args.map} not found as a Doom-format map in {args.wad}")
        return 2
    geo = Geometry(m)
    print("things:")
    for x, y, angle, kind, flags in geo.things:
        if kind in THING_NAMES:
            print(f"  {THING_NAMES[kind]:22} {x:6} {y:6}  angle {angle}")
    print("special lines (midpoint; front sector floor/ceil; tag -> tagged sector floors):")
    for (x1, y1), (x2, y2), flags, special, tag, fs, bs in geo.lines:
        if not special:
            continue
        f = geo.sectors[fs]
        tagged = [s[0] for s in geo.sectors if tag and s[6] == tag]
        label = SPECIAL_NAMES.get(special, f"special {special}")
        print(f"  {label:18} mid {(x1 + x2) / 2:7.0f} {(y1 + y2) / 2:7.0f}   {x1},{y1} -> {x2},{y2}"
              f"   front {f[0]}/{f[1]}" + (f"   tag {tag} -> floors {tagged}" if tag else "")
              + ("" if bs is not None else "   one-sided"))
    print(f"secret sectors: {sum(1 for s in geo.sectors if s[5] == 9)}")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("wad", nargs="+", help="PWAD(s) to load, then the map, e.g. wads/X.WAD MAP02")
    p.add_argument("--script", help="step script (or give it as the last positional argument)")
    p.add_argument("--describe", action="store_true", help="list the map's start, keys and special lines")
    p.add_argument("--iwad", default=DEFAULT_IWAD)
    p.add_argument("--skill", type=int, default=4, help="1 ITYTD .. 4 UV, 5 NM (default 4)")
    p.add_argument("--shots", help="screenshot directory (default /tmp/playtest-shots/MAP)")
    p.add_argument("--from", dest="start_from", metavar="NAME", help="start at `checkpoint NAME` (see above)")
    args = p.parse_args()
    pos = args.wad
    if not args.describe and not args.script:
        if len(pos) < 3:
            p.error("give WAD... MAP SCRIPT")
        args.script = pos.pop()
    if len(pos) < 2:
        p.error("give WAD... MAP")
    args.map = pos.pop()
    args.wad = pos
    sys.exit(describe(args) if args.describe else run(args))


if __name__ == "__main__":
    main()
