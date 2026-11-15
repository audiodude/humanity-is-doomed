"""playtest.py --explore: play a map with no route, knowing only what the
player has seen, to find where players get lost.

    uv run --with vizdoom scripts/tools/playtest.py LEVEL --explore [--seed N] [--watch]

The explorer starts each map knowing nothing. It sees the way a player does:
rays across its 90-degree view, stopped by walls and shut doors, mark the
floor and lines it has seen, and keys count once they've been on screen.
Each time it has nothing to do it picks the cheapest thing it knows about,
by walking distance over floor it has seen:

  - an exit it has seen (a quarter of the distance: it's what the player is after)
  - a key it has seen, from a floor level with it (a third)
  - a switch it hasn't pressed (two thirds), including a switch on a lift's
    edge when the lift is up against its ceiling, shut like a door; one that
    works when shot (a gun-activated line with a switch texture) it shoots
    ("shot" in the report)
  - a door it hasn't opened, if it has the key (a locked one a third: having
    the key, that door is what it's after)
  - a teleporter it has seen and not been through (a player knows a pad),
    if the pad has room to stand on: it steps on from the side that works
  - the edge of what it has seen, where it goes and looks round

When none is left it goes and stands in places it has only seen from afar,
then uses again, once each, the repeatable switches it has used (a door it
opened may have shut behind it: logged as "switch ... again", not progress).
Before giving up it waits for anything it can see moving to stop.

Lifts: it walks over a lift it can step or drop onto and off as it stands;
otherwise it calls it, or (standing on it, going down) uses a lift switch on
the lift's own edge and rides it. A switch it uses that sends a lift it has
seen down (one it isn't standing on) has it run for that lift and ride it up
before it goes back ("lift" in the report, not progress); a lift out of reach
that a repeatable switch sent down before, it goes and calls with that switch
(twice between progress, "switch ... again, to call ..."). A lift it got
stuck riding counts as a plain floor at its height until the next progress.
A floor or ceiling it has seen moving (a walk-over line it crossed, a switch
far off) makes the places it looked round from and couldn't reach worth
another try, a few times between progress. Getting stuck on the same spot
twice blocks the cells just past it toward where it was going.

Teleporters: a jump in position is a teleport, logged as an event (not
progress). It looks round where it landed and carries on from there; it
knows only what it has seen, so the new place starts as unknown ground.
A teleporter it has been through (and the rest of that pad) then counts as
a way from the pad to where it landed, a few cells long, so it goes back
and forth through it like through a door (a one-shot line once). It keeps
off the pads it has seen unless it means to use one: no step that would set
one off (box touching, centre crossing from the front, as Doom does), and
cells just in front cost extra. A target it keeps being teleported away
from on the way to is given up after three goes.

Costs are jittered by --seed, so seeds explore in different orders. Secret
doors look like walls to it. Monsters are killed at the start and it plays
in god mode: this measures finding the way, not fighting (--fight does that).

Before using a switch it waits (up to 3 s) for anything moving near it to
stop: a switch used on a door still on the move does nothing.

When it has nothing left it knows to try, it does what a stuck player does:
it searches the walls it has seen ("search" in the report), and the faces
of ledges too high to climb, walking up to each, using it, and shooting it
if that did nothing. Walls that stand out (a switch or door texture, or a
texture the faces either side of it in the room don't have) cost a quarter
of their walking distance, so it tries those first. If a floor or ceiling
near that wall (within 512 units, not one already moving or a door it
knows) moves, that's "found": a secret door found that way is a door it
can open again. Neither the search nor a find counts as progress, so a map
whose way on is hidden shows the whole search as a stretch with no progress.

It stops at the exit, when it has nothing left to try, or at --max-time. The
report lists what it did and when, how far it walked against the map's
critical path (the reach model's shortest route through every required key
and switch, for level modules), how much of the map it saw, and the longest
stretches with no progress (no key, switch, door or exit) and where it spent
them: the places a player wanders. Run several seeds; one seed's wandering
is a coin flip, the same place in every seed is the map.
"""
import csv
import heapq
import importlib
import json
import math
import os
import random
import struct
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import playtest as pt  # noqa: E402
from levels.doom2 import LINE_SPECIALS  # noqa: E402

KEYS = {"blue": {"BlueCard", "BlueSkull"}, "yellow": {"YellowCard", "YellowSkull"},
        "red": {"RedCard", "RedSkull"}}
KEY_ITEMS = set().union(*KEYS.values())
ML_SECRET = 32         # a line the automap shows as a wall: a secret door looks like one
EXITS = {"exit", "secret_exit"}
FOV, RAYS, RAY_STEP = 90, 46, 12
LOOK_EVERY = 6         # tics between looks
SIGHT = 2048
LOOKED = 4             # cells round a spot it looked round from that aren't the edge any more
VISITED = 6            # cells round where it has been that count as visited
STALL = 30 * 35        # a stretch this long with no progress is reported
RETRY = 60 * 35        # tics before a key or switch it gave up on is tried again
MOVES = 10             # times between progress that something it saw moving makes it look again
WEIGHT = {"exit": 0.25, "key": 1 / 3, "switch": 2 / 3, "door": 1.0, "teleport": 1.0, "frontier": 1.0,
          "unvisited": 1.0, "again": 1.0}
DOORISH = ("DOOR", "BIGDOOR", "SPCDOOR", "EXITDOOR")   # textures that read as a door (but door tracks don't)
NOT_DOOR = ("DOORTRAK", "DOORSTOP")
NEARBY = 512          # a floor or ceiling that moves this close to a wall it searched is what it found
CUE = 0.25            # a wall that stands out costs this much of its walking distance to search
JUMP = 64             # moved further than this in a tic: it was teleported
LINK = 4              # cells a teleporter it has used costs to go through


class Teleported(Exception):
    """The player was teleported: whatever it was doing is over."""


class Replan(Exception):
    """What it was doing changed the map under it (it rode a lift up): think again."""


def cross(p, q, a, b):
    """Where along p-q (0..1) it crosses segment a-b, or None."""
    rx, ry = q[0] - p[0], q[1] - p[1]
    sx, sy = b[0] - a[0], b[1] - a[1]
    d = rx * sy - ry * sx
    if d == 0:
        return None
    t = ((a[0] - p[0]) * sy - (a[1] - p[1]) * sx) / d
    u = ((a[0] - p[0]) * ry - (a[1] - p[1]) * rx) / d
    return t if 0 <= t <= 1 and 0 <= u <= 1 else None


def line_textures(m):
    """Per line, the textures on each side a player sees: ((upper, lower,
    mid), back side's or None), '-' for none."""
    sides = [tuple(t.rstrip(b"\0").decode("ascii", "replace").upper() for t in s[2:5])
             for s in struct.iter_unpack("<hh8s8s8sh", m["SIDEDEFS"])]
    return [(sides[f], sides[b] if b >= 0 else None)
            for _v1, _v2, _fl, _sp, _tag, f, b in struct.iter_unpack("<hhhhhhh", m["LINEDEFS"])]


def is_switch(tex):
    return any(t.startswith(("SW1", "SW2")) for t in tex)


class Explorer(pt.Run):
    def __init__(self, args, vzd, geo, textures):
        super().__init__(args, vzd, geo)
        self.textures = textures  # per line: ((upper, lower, mid), back side's or None)
        self.rng = random.Random(args.seed)
        self.names = None         # sector names, for a level module
        self.retried = False      # cleared what it got stuck on since the last progress
        self.known = set()        # cells the player has seen
        self.seen_lines = set()
        self.spotted = {}         # key object id -> (name, x, y), once on screen
        self.done = set()         # ("line", i) pressed or opened, ("key", id) taken
        self.again = set()        # repeatable switches used again since the last progress
        self.failed = set()       # targets it couldn't get to
        self.tries = Counter()    # failed attempts per target since the last progress
        self.gave_up = {}         # key or line target -> tic it was given up on
        self.looked = set()       # cells near spots it looked round from
        self.events = []          # (tic, kind, text, x, y)
        self.samples = []         # (tic, sector) at each look
        self.walked, self._last = 0.0, None
        self._look_at = -LOOK_EVERY
        self.blocked = set()      # cells it got stuck walking into
        self.stuck = Counter()    # times stuck on each 8-unit spot since the last progress
        self.static = set()       # lifts it got stuck riding: plain floors till the next progress
        self.moves = 0            # times since the last progress something it saw moved
        self._h_last, self._seen_n, self._seen_secs = None, -1, set()
        self.visited = set()      # cells within VISITED of where it has been
        # Doors a player can open by hand: line -> (door sector, key). Once
        # it has seen one, it can walk through it, opening it on the way.
        self.door_lines = {}
        for i, (_a, _b, flags, sp, _t, _fs, bs) in enumerate(geo.lines):
            spec = LINE_SPECIALS.get(sp)
            if spec and spec.trigger == "D" and bs is not None and not flags & ML_SECRET:
                self.door_lines[i] = (bs, spec.key)
        self.cell_lines = {}
        for i, (a, b, *_rest) in enumerate(geo.lines):
            n = max(1, int(math.dist(a, b) / 4))
            for k in range(n + 1):
                c = self.plan.cell((a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n))
                self.cell_lines.setdefault(c, []).append(i)
        self.line_ends = {}       # vertex -> lines that end there
        for i, (a, b, *_rest) in enumerate(geo.lines):
            self.line_ends.setdefault(a, []).append(i)
            self.line_ends.setdefault(b, []).append(i)
        self.searched = set()     # (line, side) of walls it used and shot at
        self.searching = False    # searching the walls since the last progress
        # Teleporters: a player knows one by its pad. Once it has used a
        # repeatable one it knows where that goes: line -> (from cell, to cell).
        self.teleports = {i for i, (*_r, sp, _t, _fs, _bs) in enumerate(geo.lines)
                          if sp in LINE_SPECIALS and LINE_SPECIALS[sp].kind == "teleport"}
        self.links = {}
        self._via = {}            # (from cell, to cell) -> teleport line, for go_to
        self._pads = {}           # cell -> seen teleporter lines the box touches there, for reach
        self._touch, self._guards, self._guard = {}, {}, set()   # cells it keeps out of beside teleporters
        # Lifts a repeatable switch it used sent down: lift -> (line, side)
        self.lift_switch = {}
        self.calls = Counter()    # times it went back to such a switch per lift since the last progress
        self._calling = False

    # -- seeing --------------------------------------------------------------
    def watch(self):
        super().watch()
        held = self.had & KEY_ITEMS
        for name in held - getattr(self, "_held", set()):
            self.event("key", name)
        self._held = held
        for lb in self.state().labels:
            if lb.object_name in KEY_ITEMS:
                self.spotted[lb.object_id] = (lb.object_name, lb.object_position_x, lb.object_position_y)
        p = self.pos()
        if self._last:
            jump = math.dist(p, self._last)
            if jump > JUMP:
                self.teleported(self._last, p)
            self.walked += jump
        self._last = p
        if self.tics - self._look_at >= LOOK_EVERY:
            self._look_at = self.tics
            self.look()

    def teleported(self, was, p):
        """It moved further than it can walk in a tic: a teleporter. Note
        where the pad it stepped on (the teleporter line nearest where it was,
        crossed from the front) took it, and stop whatever it was doing: the
        way it was following is gone."""
        self._last = p
        g = self.geo
        near = [(self.side_of(i, was), pt.seg_dist(was, *g.lines[i][:2]), i) for i in self.teleports]
        near = [n for n in near if n[1] <= 48]
        i = min(near)[2] if near else None
        here = g.sector_at(p)
        self._landed = (i, self.plan.cell(p))
        if i is None:
            self.event("teleport", f"to {self.name(here)}", progress=False, clear=False, at=was)
        else:
            self.learn(i, self.plan.cell(p))
            spec = LINE_SPECIALS[g.lines[i][3]]
            self.event("teleport", f"{spec.trigger} by {self.name(g.lines[i][5])} -> {self.name(here)}",
                       progress=False, clear=False, at=was)
        raise Teleported()

    def learn(self, i, to):
        """Teleporter line i took it to cell `to`: so does the rest of its pad
        (the lines like it round the same spot). A one-shot line is spent."""
        g = self.geo
        self.seen_lines.add(i)
        _a, _b, _f, sp, tag, _fs, _bs = g.lines[i]
        mid = [(g.lines[i][0][k] + g.lines[i][1][k]) / 2 for k in (0, 1)]
        for j in self.teleports:
            if j == i or (g.lines[j][3] == sp and g.lines[j][4] == tag and ("line", j) not in self.done
                          and pt.seg_dist(mid, *g.lines[j][:2]) <= 128):
                self.links[j] = (self.plan.cell(self.spot(j, 0)), to)
        if LINE_SPECIALS[sp].trigger != "WR":
            self.done.add(("line", i))
            del self.links[i]

    def blocks(self, i, closed):
        _a, _b, _f, _sp, _t, fs, bs = self.geo.lines[i]
        return bs is None or fs in closed or bs in closed

    def look(self):
        """Mark what the player can see from here: rays across its view."""
        x, y = self.pos()
        g, plan = self.geo, self.plan
        closed = {s for s, (f, c) in enumerate(self.heights()) if c - f <= 0}
        here = plan.cell((x, y))
        self.known.add(here)
        self.visited |= {(here[0] + i, here[1] + j) for i in range(-VISITED, VISITED + 1)
                         for j in range(-VISITED, VISITED + 1) if i * i + j * j <= VISITED * VISITED}
        self.samples.append((self.tics, g.cell_sector[plan.cell((x, y))[1]][plan.cell((x, y))[0]], x, y))
        ang = self.var("ANGLE")
        for k in range(RAYS):
            a = math.radians(ang - FOV / 2 + FOV * k / (RAYS - 1))
            dx, dy = math.cos(a) * RAY_STEP, math.sin(a) * RAY_STEP
            prev, pc = (x, y), plan.cell((x, y))
            for s in range(1, SIGHT // RAY_STEP):
                q = (x + dx * s, y + dy * s)
                qc = plan.cell(q)
                inside = 0 <= qc[0] < g.nx and 0 <= qc[1] < g.ny
                hits = []
                for c in {pc, qc, (pc[0], qc[1]), (qc[0], pc[1])}:
                    for i in self.cell_lines.get(c, ()):
                        t = cross(prev, q, *g.lines[i][:2])
                        if t is not None:
                            hits.append((t, i))
                stop = not inside   # (but a wall on the map's very edge is seen first)
                for _t, i in sorted(hits):
                    self.seen_lines.add(i)
                    if self.blocks(i, closed):
                        stop = True
                        break
                if stop:
                    break
                self.known.add(qc)
                prev, pc = q, qc

    def look_round(self):
        for _ in range(24):
            self.tic(turn=15)
        c = self.plan.cell(self.pos())
        self.looked |= {(c[0] + i, c[1] + j) for i in range(-LOOKED, LOOKED + 1) for j in range(-LOOKED, LOOKED + 1)}

    # -- deciding ------------------------------------------------------------
    def name(self, s):
        return self.names[s] if self.names and s is not None and s < len(self.names) else f"sector {s}"

    def around(self, s, stretch):
        """ (x,y): where in sector s it was, on average, for a map without names."""
        pts = [(x, y) for t, x, y in stretch if t == s]
        return f" ({sum(p[0] for p in pts) / len(pts):.0f},{sum(p[1] for p in pts) / len(pts):.0f})"

    def event(self, kind, text, progress=None, clear=True, at=None):
        """Note what it did. After it the map may have changed, so the edges
        it has looked round from, and the places it couldn't reach, are worth
        another try (a teleport changes nothing: clear=False)."""
        if clear:
            self.looked.clear()
            self.failed.clear()
            self.tries.clear()
            self.blocked.clear()
            self.static.clear()
            self.retried = False
            self.searching = False
        progress = kind in ("key", "switch", "shot", "exit") if progress is None else progress
        if progress:
            self.again.clear()
            self.moves = 0
            self.stuck.clear()
            self.calls.clear()
        self.note(kind, text, progress, at)

    def note(self, kind, text, progress=False, at=None):
        """Log what it did, without counting it as progress."""
        x, y = at or (self._last if self.game.is_episode_finished() else self.pos())
        self.events.append((self.tics, kind, text, x, y, progress))
        self.say(f"  {pt.clock(self.tics)} {kind:<8} {text} at {x:.0f},{y:.0f}")

    def keys(self):
        return {k for k, names in KEYS.items() if names & self.had}

    def doors(self):
        """Sectors of the doors it has seen and can open."""
        have = self.keys()
        return {bs for i, (bs, key) in self.door_lines.items() if i in self.seen_lines and (not key or key in have)}

    def route_heights(self, doors):
        """The live heights, with the doors it can open taken as open."""
        h = list(self.heights())
        for s in doors:
            top = min(h[n][1] for n in self.geo.neighbours(s)) - 4
            h[s] = (h[s][0], max(h[s][1], top))
        return h

    def reach(self, lv, doors):
        """Walking distance (cells) from the player to every seen cell it can
        get to over seen floor, through doors it can open and teleporters it
        has used, and the way back. It doesn't step onto teleporters it has
        seen (they'd take it away), except to go through one on purpose."""
        plan, g = self.plan, self.geo
        s = plan.free_near(plan.cell(self.pos()), lv)
        if s is None:
            return {}, {}
        # A margin outside each pad as well: running past at full tilt can clip one.
        self._pads = pads = {}
        guard = set()
        for i in self.teleports & self.seen_lines:
            if ("line", i) not in self.done:
                for c in self.touch(i):
                    pads.setdefault(c, []).append(i)
                guard |= self.guard(i)
        self._guard = guard
        jumps = {}
        self._via = {}
        for i, (a, b) in self.links.items():
            t = plan.free_near(b, lv)
            if t is not None:   # from anywhere just in front of the pad
                for di in range(-2, 3):
                    for dj in range(-2, 3):
                        jumps.setdefault((a[0] + di, a[1] + dj), []).append((t, i))
        dist, prev, todo = {s: 0.0}, {}, [(0.0, s)]
        while todo:
            d, c = heapq.heappop(todo)
            if d > dist[c]:
                continue
            for t, i in jumps.get(c, ()):
                if d + LINK < dist.get(t, 1e18):
                    dist[t], prev[t] = d + LINK, c
                    self._via[(c, t)] = i
                    heapq.heappush(todo, (d + LINK, t))
            here = lv[c[1]][c[0]]
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                n = (c[0] + di, c[1] + dj)
                if not (0 <= n[0] < g.nx and 0 <= n[1] < g.ny) or n in self.blocked or (
                        n not in self.known and g.cell_sector[n[1]][n[0]] not in doors):
                    continue
                if (c in pads or n in pads) and self.onto_pad(plan.centre(c), plan.centre(n)):
                    continue
                if not plan.step_ok(here, lv[n[1]][n[0]]):
                    continue
                if di and dj and not (plan.step_ok(here, lv[c[1]][n[0]]) and plan.step_ok(here, lv[n[1]][c[0]])):
                    continue
                nd = d + math.hypot(di, dj) * (20 if g.cell_sector[n[1]][n[0]] in g.damaging else
                                               10 if n in guard else 1)
                if nd < dist.get(n, 1e18):
                    dist[n], prev[n] = nd, c
                    heapq.heappush(todo, (nd, n))
        return dist, prev

    def touch(self, i):
        """The cells where the player's box touches teleporter line i."""
        if i not in self._touch:
            self._touch[i] = self.cells_near(i, pt.RADIUS + 4, None)
        return self._touch[i]

    def guard(self, i):
        """The cells on teleporter line i's working side close enough that
        the player's box, running past, could cross it."""
        if i not in self._guards:
            self._guards[i] = self.cells_near(i, pt.RADIUS + 8, 0)
        return self._guards[i]

    def cells_near(self, i, r, side):
        g, plan = self.geo, self.plan
        a, b = g.lines[i][:2]
        c0 = plan.cell((min(a[0], b[0]) - r, min(a[1], b[1]) - r))
        c1 = plan.cell((max(a[0], b[0]) + r, max(a[1], b[1]) + r))
        return {(x, y) for x in range(c0[0], c1[0] + 1) for y in range(c0[1], c1[1] + 1)
                if pt.seg_dist(plan.centre((x, y)), a, b) <= r
                and (side is None or self.side_of(i, plan.centre((x, y))) == side)}

    def onto_pad(self, p, q):
        """Walking p to q would set off a teleporter it has seen (as of the
        last reach). As in Doom: the box touches the line on the way and the
        centre goes from its front to its back (of the line extended, so a
        pad's corner counts too)."""
        pads = self._pads
        n = max(1, int(math.dist(p, q) / 8))
        cells = {self.plan.cell((p[0] + (q[0] - p[0]) * k / n, p[1] + (q[1] - p[1]) * k / n))
                 for k in range(n + 1)}
        for i in {i for c in cells for i in pads.get(c, ())}:
            a, b = self.geo.lines[i][:2]
            if self.side_of(i, p) == 0 and self.side_of(i, q) == 1 and (
                    cross(p, q, a, b) is not None
                    or min(pt.seg_dist(p, a, b), pt.seg_dist(q, a, b), pt.seg_dist(a, p, q),
                           pt.seg_dist(b, p, q)) < pt.RADIUS):
                return True
        return False

    def solid(self):
        """Solid things in the way: (x, y, radius)."""
        return [(round(o.position_x), round(o.position_y), pt.SOLID[o.name]) for o in self.state().objects
                if o.name in pt.SOLID]

    def near(self, p, dist, lv=None, r=3):
        """The reachable cell nearest p, within r cells. Given lv, only cells with
        their floor within a step of the floor at p: a key on a ledge can't be
        picked up from below (a switch can: using a line doesn't look at heights)."""
        c = self.plan.cell(p)
        g = self.geo
        s = g.cell_sector[c[1]][c[0]] if lv and 0 <= c[0] < g.nx and 0 <= c[1] < g.ny else None
        f = None if s is None else self.heights()[s][0]
        cells = [(c[0] + i, c[1] + j) for i in range(-r, r + 1) for j in range(-r, r + 1)]
        return min((n for n in cells if n in dist and (f is None or abs(lv[n[1]][n[0]][0] - f) <= pt.STEP)),
                   key=lambda n: math.dist(self.plan.centre(n), p), default=None)

    def frontier(self, c, closed):
        """A seen cell next to an unseen one with no wall or shut door between
        them (a door is a thing to open, not an edge to look past)."""
        g = self.geo
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c[0] + di, c[1] + dj)
            if n in self.known or not (0 <= n[0] < g.nx and 0 <= n[1] < g.ny):
                continue
            a, b = self.plan.centre(c), self.plan.centre(n)
            if not any(self.blocks(i, closed) and cross(a, b, *g.lines[i][:2]) is not None
                       for i in set(self.cell_lines.get(c, ())) | set(self.cell_lines.get(n, ()))):
                return True
        return False

    def spot(self, i, side, d=40):
        """A point d units off line i's middle, on `side` (0 front, 1 back)."""
        (x1, y1), (x2, y2) = self.geo.lines[i][:2]
        L = math.hypot(x2 - x1, y2 - y1) or 1
        s = d if side == 0 else -d
        return (x1 + x2) / 2 + (y2 - y1) / L * s, (y1 + y2) / 2 - (x2 - x1) / L * s

    def options(self, lv, dist):
        """(cost, kind, cell, what): everything it knows of that it could do next."""
        out = []
        have = self.keys()
        here = {o.id for o in self.state().objects}
        for oid, (name, x, y) in self.spotted.items():
            if oid in here and ("key", oid) not in self.failed:
                c = self.near((x, y), dist, lv)
                if c:
                    out.append((dist[c], "key", c, ("key", oid, name, (x, y))))
        h = self.heights()
        for i in self.seen_lines:
            a, b, flags, sp, _tag, fs, bs = self.geo.lines[i]
            spec = LINE_SPECIALS.get(sp)
            if not spec or ("line", i) in self.done or ("line", i) in self.failed:
                continue
            if spec.key and spec.key not in have:
                continue
            if spec.trigger == "D":
                if (flags & ML_SECRET and i not in self.door_lines) or bs is None or \
                        h[bs][1] - h[bs][0] >= pt.HEIGHT_P or ("door", bs) in self.done:
                    continue
                kind, sides = "door", (0, 1)
            elif spec.trigger in ("S1", "SR") and not (spec.kind == "lift" and bs is not None and h[bs][1] > h[bs][0]
                                                       and {fs, bs} & self.tagged(_tag)):
                # (a switch on the lift's own side calls it, which ride() does,
                # unless the lift is up against its ceiling, shut like a door)
                kind, sides = ("exit" if spec.kind in EXITS else "switch"), (0,)
            elif spec.trigger == "W1" and spec.kind in EXITS:
                kind, sides = "exit", (0, 1)
            elif spec.trigger in ("G1", "GR"):
                # A switch that using doesn't work on: a player shoots it.
                sides = tuple(s for s, tex in enumerate(self.textures[i]) if tex and is_switch(tex))
                if not sides:
                    continue
                kind = "switch"
            elif i in self.teleports and i not in self.links:
                # a pad it hasn't been through, if there's room to stand on it:
                # step on from the side that works
                if bs is None or h[bs][1] - h[bs][0] < pt.HEIGHT_P:
                    continue
                kind, sides = "teleport", (0,)
            else:
                continue
            for side in sides:
                c = self.near(self.spot(i, side), dist)
                if c:
                    # A locked door it has the key for now is what it's after, as a key is.
                    d = dist[c] * (WEIGHT["key"] / WEIGHT["door"] if kind == "door" and spec.key else 1)
                    out.append((d, kind, c, ("line", i, spec, side)))
        closed = {s for s, (f, c) in enumerate(h) if c - f <= 0}
        for c in dist:
            if c not in self.looked and ("cell", c) not in self.failed and self.lift_of(c) is None \
                    and self.frontier(c, closed):
                out.append((dist[c], "frontier", c, ("cell", c)))
        if not out:
            # Nothing new in sight: go and stand in places it has only seen from
            # afar, as a player does when stuck (a newly opened way, a far ledge).
            out = [(dist[c], "unvisited", c, ("cell", c)) for c in dist
                   if c not in self.visited and ("cell", c) not in self.failed and self.lift_of(c) is None]
        if not out:
            # Still nothing: use again a repeatable switch it has used (a door
            # it opened may have shut behind it), once each till the next progress.
            for i in self.seen_lines:
                spec = LINE_SPECIALS.get(self.geo.lines[i][3])
                if spec and spec.trigger == "SR" and spec.kind not in EXITS and ("line", i) in self.done \
                        and i not in self.again and ("line", i) not in self.failed:
                    c = self.near(self.spot(i, 0), dist)
                    if c:
                        out.append((dist[c], "again", c, ("line", i, spec, 0)))
        return [(d * WEIGHT[k] * self.rng.uniform(0.85, 1.15), k, c, w) for d, k, c, w in out]

    def tagged(self, tag):
        return {s for s, sec in enumerate(self.geo.sectors) if tag and sec[6] == tag}

    def lift_of(self, c):
        return next((s for s in self.plan.under[c[1]][c[0]] or () if s in self.geo.lifts and s not in self.static),
                    None)

    def go_to(self, c, prev, lv, final=None):
        """Follow the way to c: walk the stretches off lifts, ride the lifts,
        go through the teleporters it has used."""
        self._lv = lv
        path = [c]
        while path[-1] in prev:
            path.append(prev[path[-1]])
        path.reverse()
        start = 0
        for k in range(len(path) - 1):
            i = self._via.get((path[k], path[k + 1]))
            if i is not None:
                self.follow(path[start:k + 1], lv)
                self.through(i)
                start = k + 1
        self.follow(path[start:], lv, final)

    def through(self, i):
        """Cross teleporter line i from its front, and wait out the freeze.
        If it can't get across, or crossing takes it nowhere (the pad has
        moved or shut since), it forgets where that pad goes."""
        try:
            try:
                self.drive(self.spot(i, 1), 0, True)
            except Teleported:
                self.tic(n=18)
                return
            raise pt.Abort("the teleporter didn't take it anywhere")
        except pt.Abort:
            if i in self.links:
                to = self.links[i][1]
                for j in [j for j, (_a, b) in self.links.items() if b == to]:
                    del self.links[j]
            raise

    def follow(self, path, lv, final=None):
        k = 0
        while k < len(path):
            j = k
            while j < len(path) and self.lift_of(path[j]) is None:
                j += 1
            if j > k:
                pts = self.smooth(path[k:j], lv)
                if final and j == len(path):
                    pts[-1] = final
                for n, p in enumerate(pts):
                    self.walk(p, n == len(pts) - 1)
            if j == len(path):
                return
            m = j
            while m < len(path) and self.lift_of(path[m]) is not None:
                m += 1
            self.ride(path[j:m], path[m] if m < len(path) else None)
            k = m

    def smooth(self, path, lv, span=8):
        """Waypoints along the path, cutting corners where it's straight, but
        no more than `span` cells apart: a long straight run steered at full
        speed can slide off a ramp or a ledge's edge."""
        out, i = [], 0
        while i < len(path) - 1:
            j = min(len(path) - 1, i + span)
            while j > i + 1 and not (self.plan.straight(path[i], path[j], lv, path[i:j + 1])
                                     and not self.through_blocked(path[i], path[j])
                                     and not self.past_pad(path[i], path[j], path[i:j + 1])):
                j -= 1
            out.append(self.plan.centre(path[j]))
            i = j
        return out or [self.plan.centre(path[-1])]

    def past_pad(self, a, b, along):
        """Cutting straight from cell a to b would cross a teleporter it has
        seen, or pass closer to one than the path does."""
        pa, pb = self.plan.centre(a), self.plan.centre(b)
        if self.onto_pad(pa, pb):
            return True
        if not self._guard:
            return False
        n = max(1, int(math.dist(pa, pb) / 4))
        return any(c in self._guard and c not in along for c in
                   {self.plan.cell((pa[0] + (pb[0] - pa[0]) * k / n, pa[1] + (pb[1] - pa[1]) * k / n))
                    for k in range(n + 1)})

    def through_blocked(self, a, b):
        pa, pb = self.plan.centre(a), self.plan.centre(b)
        n = max(1, int(math.dist(pa, pb) / 4))
        return any(self.plan.cell((pa[0] + (pb[0] - pa[0]) * k / n, pa[1] + (pb[1] - pa[1]) * k / n)) in self.blocked
                   for k in range(n + 1))

    def walk(self, p, final):
        try:
            self.drive(p, 0, final)
        except pt.Abort:
            # Whatever is in the way (a lip, a railing) isn't on its map: mark
            # the way ahead impassable and think again.
            x, y = self.pos()
            d = math.dist((x, y), p) or 1
            ahead = {self.plan.cell((x + (p[0] - x) / d * r, y + (p[1] - y) / d * r)) for r in (16, 32, 48)}
            self.blocked |= {(c[0] + i, c[1] + j) for c in ahead for i in (-1, 0, 1) for j in (-1, 0, 1)}
            # The planner stands the player's box on the highest floor it
            # touches, so the cells along a stair's side read as steps: block
            # any nearby cell it thinks is above a step from here.
            here, z, lv = self.plan.cell((x, y)), self.var("POSITION_Z"), self._lv
            self.blocked |= {(here[0] + i, here[1] + j) for i in range(-4, 5) for j in range(-4, 5)
                             if 0 <= here[0] + i < self.geo.nx and 0 <= here[1] + j < self.geo.ny
                             and lv[here[1] + j][here[0] + i] and lv[here[1] + j][here[0] + i][0] > z + pt.STEP}
            # A waypoint closer than the cells ahead (a corner it can't round)
            # is in the way itself.
            self.blocked.add(self.plan.cell(p))
            # Stuck on the same spot again since the last progress: the cells
            # just beyond it toward the waypoint are in the way too.
            spot = (round(x / 8), round(y / 8))
            self.stuck[spot] += 1
            if self.stuck[spot] >= 2:
                ang = math.atan2(p[1] - y, p[0] - x)
                self.blocked |= {(here[0] + i, here[1] + j) for i in range(-2, 3) for j in range(-2, 3)
                                 if (i or j) and math.cos(math.atan2(j, i) - ang) > 0.5}
            self.blocked.discard(here)
            raise

    def ride(self, cells, after):
        """Ride a lift as a player does, from beside it: if it's up, use it to
        call it down and step on while it waits; if it's level and the way on
        is down, use it and step on as it sinks; then wait for it to reach the
        floor beyond. A lift that has walk-over lines goes by itself. Getting
        stuck anywhere on the way makes it a plain floor at the height it's at
        till the next progress: another ride would only get stuck the same way,
        but it may still walk over it or drop off it."""
        s = self.lift_of(cells[0])
        try:
            self._ride(s, cells, after)
        except pt.Abort:
            self.static.add(s)
            raise

    def inside(self, c, lifts, margin):
        """The player's box in cell c, and in the cells within `margin` of
        it, is wholly on `lifts`."""
        g, under, wall = self.geo, self.plan.under, self.plan.wall
        return all(0 <= n[0] < g.nx and 0 <= n[1] < g.ny and not wall[n[1]][n[0]]
                   and (under[n[1]][n[0]] or {None}) <= lifts
                   for n in ((c[0] + i, c[1] + j) for i in range(-margin, margin + 1)
                             for j in range(-margin, margin + 1)))

    def _ride(self, s, cells, after):
        # Where to stand on it: the cell nearest the middle of the way across
        # where the box is well onto the lift (on its edge, the ledge beside
        # it would hold the player up while it's down).
        mid = cells[len(cells) // 2]
        near = [(mid[0] + i, mid[1] + j) for i in range(-4, 5) for j in range(-4, 5)]
        inner = [c for c in near if self.inside(c, {s}, 1)] or [c for c in near if self.inside(c, {s}, 0)]
        on = self.plan.centre(min(inner, key=lambda c: math.dist(c, mid)) if inner else mid)
        g = self.geo
        z = lambda: self.var("POSITION_Z")  # noqa: E731
        lift = lambda: self.heights()[s][0]  # noqa: E731
        want = self.heights()[g.cell_sector[after[1]][after[0]]][0] if after else lift()
        lf, lc = self.heights()[s]
        a = self._lv[after[1]][after[0]] if after else None
        if a and lift() - z() <= 24 and lc - max(lf, z()) >= pt.HEIGHT_P and a[0] - lf <= 24 \
                and a[1] - max(lf, a[0]) >= pt.HEIGHT_P:
            # It can step or drop onto the lift as it is, and step or drop off
            # it where it's going: just walk over it.
            self.walk(on, False)
            self.walk(self.plan.centre(after), False)
            return
        if abs(lift() - z()) > 24:            # up (or down) out of reach: call it
            if s in self.lift_switch and not self._calling and self.calls[s] < 2:
                # from the switch it saw send it down before (twice between progress)
                self.calls[s] += 1
                self.call_from_switch(s)
                raise Replan()
            self.face(on)
            self.press()
            for _ in range(175):
                self.tic()
                if abs(lift() - z()) <= 24:
                    break
            else:
                raise pt.Abort("the lift didn't come")
        elif want < z() - 24:                 # level with the player, going down: set it off
            # A lift switch it has seen on the lift's own edge (a switch in the
            # room that is the lift): use it from where it is, and ride down.
            switch = min((i for i in self.seen_lines if self.geo.lines[i][5] == s
                          and self.geo.lines[i][3] in LINE_SPECIALS
                          and LINE_SPECIALS[self.geo.lines[i][3]].kind == "lift"
                          and LINE_SPECIALS[self.geo.lines[i][3]].trigger in ("S1", "SR")),
                         key=lambda i: pt.seg_dist(self.pos(), *self.geo.lines[i][:2]), default=None)
            if self.geo.sector_at(self.pos()) == s and switch is not None:
                (x1, y1), (x2, y2) = self.geo.lines[switch][:2]
                try:
                    self.drive(self.spot(switch, 0, 24), 0, True)
                except pt.Abort:
                    pass
                self.face(((x1 + x2) / 2, (y1 + y2) / 2))
                self.press()
            else:
                if self.geo.sector_at(self.pos()) == s:   # from beside it: step off first
                    here = self.plan.cell(self.pos())
                    lv = self._lv
                    # A cell the player's box fits in, off the lift and level with it.
                    off = min((c for c in ((here[0] + i, here[1] + j) for i in range(-5, 6) for j in range(-5, 6))
                               if 0 <= c[0] < g.nx and 0 <= c[1] < g.ny and c in self.known and c not in self.blocked
                               and self.lift_of(c) is None and lv[c[1]][c[0]] is not None
                               and abs(lv[c[1]][c[0]][0] - z()) <= 24),
                              key=lambda c: math.dist(c, here), default=None)
                    if off is None:
                        raise pt.Abort("on a lift with nowhere level to step off to")
                    self.walk(self.plan.centre(off), True)
                self.face(on)
                self.press()
        self.walk(on, True)
        if after is None:
            return
        for _ in range(245):
            if abs(z() - want) <= 24:
                break
            self.tic()
        else:
            raise pt.Abort("the lift didn't take it there")
        self.walk(self.plan.centre(after), False)

    def act(self, kind, c, what, lv, prev):
        if what[0] == "cell":
            self.go_to(c, prev, lv)
            self.look_round()
            return
        if what[0] == "key":
            self.go_to(c, prev, lv, final=what[3])
            if any(o.id == what[1] for o in self.state().objects):
                raise pt.Abort(f"couldn't pick up the {what[2]}")
            return
        _, i, spec, side = what
        (x1, y1), (x2, y2) = self.geo.lines[i][:2]
        mid = ((x1 + x2) / 2, (y1 + y2) / 2)
        if kind == "teleport":
            self.go_to(c, prev, lv)
            self.through(i)
            self.look_round()   # where is this?
            return
        if spec.trigger == "W1":   # a walk-over exit: cross it
            self.go_to(c, prev, lv)
            self.drive(self.spot(i, 1 - side), 0, True)
            return
        self.go_to(c, prev, lv)
        before = self.heights()
        try:
            self.drive(self.spot(i, side, 24), 0, True)
        except pt.Abort:
            pass   # a step or a lip in the way: it may be in reach already
        if kind != "door":
            self.quiet(before)
        pressed = self.heights()
        if spec.trigger in ("G1", "GR"):
            self.shoot(i, side)
        else:
            self.face(mid)
            if pt.seg_dist(self.pos(), (x1, y1), (x2, y2)) > pt.USE_RANGE:
                raise pt.Abort("couldn't get within reach of the line")
            self.press()
        a, b, _flags, _sp, tag, fs, bs = self.geo.lines[i]
        if kind == "door":
            self.done.add(("door", bs))
            self.event(kind, f"{self.name(bs)}" + (f" ({spec.key} key)" if spec.key else ""), bool(spec.key))
        else:
            self.done.add(("line", i))
            if kind == "again":
                self.again.add(i)
            moved = sorted({self.name(t) for t in self.tagged(tag)})
            self.event("shot" if spec.trigger in ("G1", "GR") else "switch" if kind == "again" else kind,
                       f"{spec.trigger} {spec.kind} by {self.name(fs)}"
                       + (f" -> {'/'.join(moved[:3])}{'...' if len(moved) > 3 else ''}" if moved else "")
                       + (" again" if kind == "again" else ""), False if kind == "again" else None)
        lifts = self.lifts_off() if kind in ("switch", "again") else set()
        lowered = []
        for t in range(70 if kind != "exit" else 35):
            self.tic()
            if lifts and t >= 8:
                lowered = [s for s in lifts if self.heights()[s][0] < pressed[s][0] - pt.STEP]
                if lowered:
                    break
        if lowered:
            if spec.trigger == "SR":
                self.lift_switch.update((s, (i, side)) for s in lowered)
            self.catch_lift(lowered, pressed)
        if kind in ("switch", "again"):
            self.look_round()   # as a player does: what did that do?

    def seen_lifts(self):
        """Lifts it has seen (a side of a line it has seen)."""
        return {s for i in self.seen_lines for s in self.geo.lines[i][5:7] if s in self.geo.lifts}

    def lifts_off(self):
        """Lifts it has seen, but not one it's standing on."""
        here = self.plan.cell(self.pos())
        return self.seen_lifts() - set(self.plan.under[here[1]][here[0]] or ())

    def call_from_switch(self, s):
        """Lift s is out of reach and a repeatable switch it has used sent it
        down before: go and use that switch again, and catch the lift."""
        i, side = self.lift_switch[s]
        a, b, _flags, sp, _tag, fs, _bs = self.geo.lines[i]
        spec = LINE_SPECIALS[sp]
        self._calling = True
        try:
            doors = self.doors()
            lv = self.plan.levels(self.route_heights(doors), self.solid(), frozenset(self.static))
            dist, prev = self.reach(lv, doors)
            c = self.near(self.spot(i, side), dist)
            if c is None:
                raise pt.Abort("can't get to the switch that calls the lift")
            self.go_to(c, prev, lv)
            try:
                self.drive(self.spot(i, side, 24), 0, True)
            except pt.Abort:
                pass
            self.face(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2))
            if pt.seg_dist(self.pos(), a, b) > pt.USE_RANGE:
                raise pt.Abort("couldn't get within reach of the switch that calls the lift")
            pressed, lifts = self.heights(), self.lifts_off()
            self.press()
            self.event("switch", f"{spec.trigger} {spec.kind} by {self.name(fs)} again, to call {self.name(s)}",
                       False)
            for _ in range(40):
                self.tic()
                lowered = [t for t in lifts if self.heights()[t][0] < pressed[t][0] - pt.STEP]
                if lowered:
                    self.catch_lift(lowered, pressed)
                    break
            else:
                self.note("lift", f"{self.name(s)} didn't go down")
        finally:
            self._calling = False

    def catch_lift(self, lowered, was):
        """A switch it used sent a lift it has seen down (heights `was`
        before): as a player does, run and get on it before it goes back up,
        and ride it up."""
        # Once it's down, the lift is a floor like any other: plan a way onto
        # it that doesn't clip the ledges round it.
        for _ in range(40):
            h = [self.heights()[s] for s in lowered]
            self.tic()
            if [self.heights()[s] for s in lowered] == h:
                break
        added = set(lowered) - self.static
        self.static |= added
        try:
            doors = self.doors()
            lv = self.plan.levels(self.route_heights(doors), self.solid(), frozenset(self.static))
            dist, prev = self.reach(lv, doors)
            # Standing well onto it, the nearest such spot (on a lift too
            # narrow for that, the nearest spot on it at all).
            low = set(lowered)
            on = [c for c in dist if self.inside(c, low, 1)] or [c for c in dist if self.inside(c, low, 0)] or \
                [c for c in dist if (self.plan.under[c[1]][c[0]] or set()) & low]
            if not on:
                self.note("lift", f"no way it knows onto {'/'.join(self.name(t) for t in lowered)}")
                return
            c = min(on, key=dist.get)
            s = next(iter(self.plan.under[c[1]][c[0]] & low))
            self.note("lift", f"runs for {self.name(s)}, which went down ({dist[c] * pt.GRID:.0f} away)")
            try:
                self.go_to(c, prev, lv)
            except pt.Abort as e:
                self.note("lift", f"missed {self.name(s)}: {e}")
                return
            still, f = 0, self.heights()[s][0]
            while f < was[s][0] and still < 140:   # ride it back up (if it comes back up)
                self.tic()
                still, f = (still + 1 if self.heights()[s][0] == f else 0), self.heights()[s][0]
        finally:
            self.static -= added

    def quiet(self, before):
        """Before a switch, if anything near it moved since `before`, wait
        (up to 3 s) for it to stop, as a player does after a door slams
        behind them: a switch used on a door still on the move does nothing."""
        g = self.geo
        p = self.pos()
        near = [s for s in range(len(g.sectors))
                if any(pt.seg_dist(p, *g.lines[k][:2]) <= NEARBY for k in g.sector_lines[s])]
        h = before
        for _ in range(35):
            now = self.heights()
            if all(now[s] == h[s] for s in near):
                return
            h = now
            self.tic(n=3)

    def aim_z(self, i, side):
        """Height of the middle of what's showing of line i's `side`: the
        switch texture of a shootable switch, else the wall face."""
        _a, _b, _f, _sp, _t, fs, bs = self.geo.lines[i]
        h = self.heights()
        near, far = (fs, bs) if side == 0 else (bs, fs)
        if far is None:
            return sum(h[near]) / 2
        (nf, nc), (ff, fc) = h[near], h[far]
        upper, lower, mid = self.textures[i][side]
        parts = [(upper, (max(fc, nf), nc)), (lower, (nf, min(ff, nc))), (mid, (max(nf, ff), min(nc, fc)))]
        lo, hi = next((span for tex, span in parts if is_switch((tex,)) and span[1] > span[0]),
                      max((span for _tex, span in parts), key=lambda s: s[1] - s[0]))
        return (lo + hi) / 2

    def shoot(self, i, side):
        """Fire at line i's middle, aiming up or down at what's showing."""
        (x1, y1), (x2, y2) = self.geo.lines[i][:2]
        mid = ((x1 + x2) / 2, (y1 + y2) / 2)
        d = max(1.0, math.dist(self.pos(), mid))
        rise = self.aim_z(i, side) - (self.var("POSITION_Z") + 41)
        self.face(mid, pitch=-math.degrees(math.atan2(rise, d)))
        self.press("attack")
        self.tic(n=8)
        self.face(self.var("ANGLE"), pitch=0.0)

    # -- searching -----------------------------------------------------------
    def showing(self, i, side):
        """The textures on line i's `side`."""
        tex = self.textures[i][side]
        return {t for t in tex or () if t != "-"}

    def wall_sides(self, i, h):
        """The sides of line i that are a wall to stand at: a one-sided
        line's front, or the side of a two-sided line that faces a shut
        sector or a ledge too high to step up (heights `h`)."""
        _a, _b, _f, _sp, _t, fs, bs = self.geo.lines[i]
        if bs is None:
            return (0,)
        out = []
        for side, (near, far) in enumerate(((fs, bs), (bs, fs))):
            (nf, nc), (ff, fc) = h[near], h[far]
            if nc - nf >= pt.HEIGHT_P and (fc - ff <= 0 or ff - nf > pt.STEP):
                out.append(side)
        return tuple(out)

    def cue(self, i, side):
        """Whether the wall stands out as a player would notice: a switch or
        a door's texture, or a texture none of the faces either side of it in
        the same room has."""
        tex = self.showing(i, side)
        if is_switch(tex) or any(t.startswith(DOORISH) and not t.startswith(NOT_DOOR) for t in tex):
            return True
        a, b, _f, _sp, _t, fs, bs = self.geo.lines[i]
        room = fs if side == 0 else bs
        others = []
        for j in set(self.line_ends[a]) | set(self.line_ends[b]):
            if j == i:
                continue
            _a2, _b2, _f2, _sp2, _t2, fs2, bs2 = self.geo.lines[j]
            others += [self.showing(j, s2) for s2, sec in ((0, fs2), (1, bs2)) if sec == room]
        others = [o for o in others if o]
        return bool(tex and others) and all(not tex & o for o in others)

    def search_options(self, dist):
        """(cost, "wall", cell, what): walls it has seen and not searched."""
        h = self.heights()
        out = []
        for i in self.seen_lines:
            a, b, _flags, sp, _tag, _fs, _bs = self.geo.lines[i]
            if i in self.door_lines or ("line", i) in self.done or math.dist(a, b) < 16:
                continue
            for side in self.wall_sides(i, h):
                if (i, side) in self.searched:
                    continue
                c = self.near(self.spot(i, side, 32), dist)
                if c is None:
                    continue
                w = CUE if self.cue(i, side) else 1.0
                out.append((dist[c] * w * self.rng.uniform(0.85, 1.15), "wall", c, ("wall", i, side)))
        return out

    def heard(self, i, before, moving):
        """Sectors near line i that moved since `before` (not ones already on
        the move, nor doors it knows of): what using or shooting it did."""
        a, b = self.geo.lines[i][:2]
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        now, known, g = self.heights(), self.doors(), self.geo
        return [s for s, hs in enumerate(now) if hs != before[s] and s not in moving and s not in known and any(
            pt.seg_dist(mid, *g.lines[k][:2]) <= NEARBY for k in g.sector_lines[s])]

    def search(self, c, what, lv, prev):
        """Walk up to a wall, use it, and if nothing moves, shoot it."""
        _, i, side = what
        self.searched.add((i, side))
        self.go_to(c, prev, lv)
        a, b, _flags, sp, _tag, fs, bs = self.geo.lines[i]
        try:
            self.drive(self.spot(i, side, 24), 0, True)
        except pt.Abort:
            pass
        if pt.seg_dist(self.pos(), a, b) > pt.USE_RANGE:
            raise pt.Abort("couldn't get within reach of the wall")
        self.face(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2))
        h0 = self.heights()
        self.tic(n=4)
        before = self.heights()
        moving = {s for s, hs in enumerate(before) if hs != h0[s]}
        how = "using"
        self.press()
        self.tic(n=20)
        moved = self.heard(i, before, moving)
        if not moved:
            how = "shooting"
            self.shoot(i, side)
            self.tic(n=20)
            moved = self.heard(i, before, moving)
        if not moved:
            return
        spec = LINE_SPECIALS.get(sp)
        if spec and spec.trigger == "D" and bs is not None:
            self.door_lines[i] = (bs, spec.key)   # a door: now it knows, it can open it again
        names = sorted({self.name(s) for s in moved})
        self.event("found", f"{how} a wall by {self.name(fs if side == 0 else bs)} moved "
                   f"{'/'.join(names[:3])}{'...' if len(names) > 3 else ''}")
        self.look_round()

    def seen_sectors(self):
        """Sectors either side of a line it has seen, but not doors it opens by
        hand or lifts (they go back by themselves, which tells it nothing new)."""
        if self._seen_n != len(self.seen_lines):
            self._seen_n = len(self.seen_lines)
            self._seen_secs = {s for i in self.seen_lines for s in self.geo.lines[i][5:7] if s is not None} \
                - self.geo.lifts
        return self._seen_secs - self.doors()

    def notice_moves(self):
        """A floor or ceiling it has seen moved since it last looked (a walk-over
        line it crossed, a switch far off): the edges it has looked round from
        and the places it couldn't reach are worth another try, as for progress,
        a few times between real progress (a crusher or a platform goes on moving)."""
        h = self.heights()
        last, self._h_last = self._h_last, h
        if last is None or self.moves >= MOVES:
            return False
        if not any(h[s] != last[s] for s in self.seen_sectors()):
            return False
        self.moves += 1
        self.looked.clear()
        self.failed.clear()
        self.tries.clear()
        self.blocked.clear()
        self.static.clear()
        self.retried = False
        return True

    def settle(self):
        """With nothing left to try: if something it has seen is moving, wait
        (up to 5 s) for it to stop, then look again. True if anything moved."""
        moved = False
        for _ in range(35):
            h = self.heights()
            self.tic(n=5)
            if not any(self.heights()[s] != h[s] for s in self.seen_sectors()):
                break
            moved = True
        if moved:
            self.look_round()
        return self.notice_moves() or moved

    def explore(self):
        for c in ("god", "notarget", "kill monsters"):
            self.game.send_game_command(c)
        self.tic(n=35)
        self.say(f"EXPLORE {self.args.map.upper()} skill {self.args.skill} seed {self.args.seed}: no route, "
                 "monsters removed, god mode")
        self.look_round()
        cap = self.args.max_time * 60 * 35
        while self.tics < cap:
            self.notice_moves()
            doors = self.doors()
            lv = self.plan.levels(self.route_heights(doors), self.solid(), frozenset(self.static))
            dist, prev = self.reach(lv, doors)
            # A key or switch it gave up on is worth another go a minute
            # later: it may have found another way up since.
            for t in [t for t, at in self.gave_up.items() if self.tics - at > RETRY]:
                del self.gave_up[t]
                self.failed.discard(t)
                self.tries[t] = 0
            opts = self.options(lv, dist)
            if not opts and (self.blocked or self.failed or self.static) and not self.retried:
                # Before giving up, try again what it got stuck on once: a lift
                # may be down now, a door it bumped into open.
                self.retried = True
                self.blocked.clear()
                self.failed.clear()
                self.static.clear()
                continue
            if not opts and self.moves < MOVES and self.settle():
                continue
            if not opts:
                # Nothing left it knows of: as a stuck player does, go along
                # the walls it has seen using them and shooting them.
                opts = self.search_options(dist)
                if not opts:
                    return "nothing left it knows to try" + (
                        f" (searched {len(self.searched)} walls)" if self.searched else "")
                if not self.searching:
                    self.searching = True
                    self.note("search", "nothing left it knows to try: searching the walls")
            _, kind, c, what = min(opts, key=lambda o: o[0])
            blocked = set(self.blocked) if what[0] == "wall" else None
            try:
                if what[0] == "wall":
                    self.search(c, what, lv, prev)
                else:
                    self.act(kind, c, what, lv, prev)
            except Replan:
                pass
            except Teleported:
                if kind == "teleport":
                    self.learn(what[1], self._landed[1])   # it stepped on the pad it was making for
                else:
                    # It stepped on a teleporter on the way. It knows that one now
                    # and keeps off it, but if the only way there is over pads
                    # it can't tell apart, give the target up after a few goes.
                    self.missed(what, c, 3)
                self.tic(n=18)
                try:
                    self.look_round()   # where is this?
                except Teleported:
                    pass
            except pt.Abort:
                if not self.game.is_episode_finished():
                    if what[0] == "wall":
                        # The wall is searched either way; what it bumped
                        # into on the way shouldn't cut it off from the rest.
                        self.blocked = blocked
                        continue
                    # Getting stuck marked the way it tried as blocked, so a
                    # key or a switch is worth another way round, twice.
                    self.missed(what, c, 1 if what[0] == "cell" else 3)
            if self.game.is_episode_finished():
                if not self.events or self.events[-1][1] != "exit":
                    self.event("exit", "walked over the exit")
                return None
        return f"--max-time {self.args.max_time:g} min"

    def missed(self, what, c, chances):
        """It didn't get to `what` (at cell c): after `chances` goes give up on it."""
        target = what[:2] if what[0] != "cell" else ("cell", c)
        self.tries[target] += 1
        if self.tries[target] >= chances:
            self.failed.add(target)
            if what[0] != "cell":
                self.gave_up[target] = self.tics

    # -- report --------------------------------------------------------------
    def report(self, stopped, crit, boss):
        g = self.geo
        self.say("")
        if stopped is None:
            self.say(f"EXITED at {pt.clock(self.tics)}")
        else:
            self.say(f"NO EXIT: stopped at {pt.clock(self.tics)} ({stopped})")
            if boss:
                self.say("  the exit opens on a monster's death (UMAPINFO bossaction), which ViZDoom doesn't run and "
                         "this run has no monsters for: read the stretches before the boss fight only")
        line = f"walked {self.walked:,.0f}"
        if crit:
            line += f"; the critical path is {crit:,.0f} ({self.walked / crit:.1f}x)"
        standable = sum(1 for row in g.cell_sector for s in row if s is not None)
        self.say(line + f"; saw {len(self.known) / max(standable, 1):.0%} of the map")
        marks = [0] + [e[0] for e in self.events if e[5]] + [self.tics]
        gaps = sorted(((b - a, a, b) for a, b in zip(marks, marks[1:]) if b - a >= STALL), reverse=True)[:5]
        if gaps:
            self.say("longest stretches with no key, switch, locked door or exit (where it spent them):")
        for span, a, b in gaps:
            stretch = [(s, x, y) for t, s, x, y in self.samples if a <= t < b and s is not None]
            where = Counter(s for s, _x, _y in stretch)
            total = sum(where.values()) or 1
            top = ", ".join(f"{self.name(s)} {n / total:.0%}" + ("" if self.names else self.around(s, stretch))
                            for s, n in where.most_common(4))
            self.say(f"  {pt.clock(span)} from {pt.clock(a)} to {pt.clock(b)}: {top}")


def level_info(module, wads, slot):
    """Sector names (SECTORS order), the reach model's critical path length,
    and whether a monster's death opens the exit (UMAPINFO bossaction), of a
    level module. For an id map (an IWAD given as the WAD) the critical path
    comes from data/metrics/metrics_progression.csv. Otherwise (None, None, False)."""
    if not module:
        from levels.wad import IWADS
        iwads = {os.path.realpath(p) for p in IWADS.values() if p}
        crit = None
        if len(wads) == 1 and os.path.realpath(wads[0]) in iwads:
            with open(os.path.join(pt.ROOT, "data", "metrics", "metrics_progression.csv")) as f:
                row = next((r for r in csv.DictReader(f) if r["map"] == slot.upper()), None)
            if row and row.get("crit_path_len"):
                crit = float(row["crit_path_len"])
        return None, crit, False
    from levels import checks
    from levels.mapgen import compile_level
    from levels.model import load
    from levels.reach import umapinfo_boss
    sys.path.insert(0, os.path.join(pt.ROOT, "scripts", "metrics"))
    import progression_metrics as pm
    level = load(importlib.import_module(f"levels.{module}"), pt.place(module))
    _m, md, res = checks.findings(level, compile_level(level)).reach
    crit = pm.analyse(md, res)[0].get("crit_path_len")
    return list(level.sectors), (crit if isinstance(crit, (int, float)) else None), bool(umapinfo_boss(level.umapinfo))


def run(args, vzd):
    m = pt.find_map(args.wad, args.map.upper())
    if not m:
        print(f"{args.map} not found as a Doom-format map in {args.wad}")
        return 2
    t0 = time.time()
    names, crit, boss = level_info(args.module, args.wad, args.map)
    r = Explorer(args, vzd, pt.Geometry(m), line_textures(m))
    r.names = names
    stopped = "error"
    try:
        stopped = r.explore()
    finally:
        r.report(stopped, crit, boss)
        r.game.close()
        if r.recording:
            os.replace(r.recording_part, r.recording)
            with open(r.recording + ".json", "w") as f:
                json.dump({"wad": pt.wad_hash(args.wad)}, f)
            print(f"recorded to {r.recording}; watch it with --replay --explore")
    print(f"DONE ({time.time() - t0:.1f} s)")
    return 0 if stopped is None else 1
