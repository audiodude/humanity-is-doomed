"""Event-driven reachability model of the vanilla DOOM / DOOM II maps, and the
layout/progression metrics derived from it (keys and locks, critical path,
optional area, backtracking, loops, dead ends, one-way drops, teleporters,
secrets, sky). Writes data/metrics/metrics_progression.csv.

Run from the repo root:
    python3 scripts/metrics/progression_metrics.py          # all 68 maps
    python3 scripts/metrics/progression_metrics.py E1M7     # debug one map
    python3 scripts/metrics/progression_metrics.py --set tnt  # an official set (doomwad.SETS)

Model (levels/reach.py; see research/facets/12-quant-progression.md for the full write-up):
- Nodes are regions: connected pieces of sectors (vanilla maps reuse one
  sector number for separate areas). The player crosses a two-sided,
  non-impassable line from a to b when some height state of a and of b gives
  a step up <= 24, an opening (lowest ceiling - highest floor) >= 56, and the
  contiguous run of crossable lines is >= 32 units wide. Drops are any height.
  Trenches/ledges narrower than 32 units are straddled (Doom stands the
  player on the highest floor its box touches).
- Every region keeps the set of (floor, ceiling) states it has ever had; the
  fixed point is monotone (moving floors add states, nothing is taken away).
- Manual doors (D lines) open their back sector; open-wait-close ones only let
  you in from a side with a usable D line. Tagged specials fire once their
  trigger is reachable (S/D: the front sector, or a reachable sector within
  use range; W: the line can be walked across; G: shot from a reachable
  sector) and add the vanilla target heights (p_floor/p_plats/p_doors/
  p_ceilng/p_spec rules, searched over the whole sector). Lifts and
  perpetual platforms keep both heights. Teleports (39/97) send the player to
  the first teleport destination in the tagged sectors. Boss deaths (tags
  666/667, E2M8/E3M8/MAP30 exits, MAP32 keens) fire once every boss monster
  can be shot from a reachable sector. Keys are picked up when their region
  is reached (or touched across a line). Iterate until nothing changes.
- Running jumps (tic-by-tic straight runs under vanilla gravity) are only
  enabled for the 13 maps whose exit needs them (column model_jumps).
"""
import heapq
import itertools
import math
import os
import sys
from collections import defaultdict, deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import doomwad as dw  # noqa: E402  (also puts the repo root on sys.path)
from levels.reach import HEIGHT, seg_cross, solve  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
OUT = os.path.join(dw.METRICS, "metrics_progression.csv")


def episode(slot):
    if slot.startswith("E"):
        return slot[:2]
    n = int(slot[3:])
    return "D2-1" if n <= 11 else "D2-2" if n <= 20 else "D2-3" if n <= 30 else "D2-S"




# ------------------------------------------------------------------ metrics --
def dijkstra(model, src, dst, base, man, keys):
    """Shortest sector path src -> dst over centroid/portal distances."""
    if src == dst:
        return 0.0, [src], []
    dist = {src: 0.0}
    prev = {}
    pq = [(0.0, src)]
    while pq:
        d, a = heapq.heappop(pq)
        if a == dst:
            break
        if d > dist.get(a, math.inf):
            continue
        for b, w, kind in model.moves(a, base, man, keys):
            nd = d + w
            if nd < dist.get(b, math.inf):
                dist[b], prev[b] = nd, (a, kind)
                heapq.heappush(pq, (nd, b))
    if dst not in dist:
        return None
    path, kinds = [dst], []
    while path[-1] != src:
        a, kind = prev[path[-1]]
        path.append(a)
        kinds.append(kind)
    return dist[dst], path[::-1], kinds[::-1]


def final_graph(model, res):
    """Directed sector graph of the end state: current (last) heights plus the
    oscillating heights of lifts/platforms/doors; manual doors as in play.
    Returns ({a: {b: kind}}, base, man). Gap crossings are kept only where
    the player could not simply walk through the gap sector."""
    base, man, keys = model.final_state(res)
    out = defaultdict(dict)
    for a in range(model.n):
        for b in model.adj[a]:
            if model.can_pass(a, b, base, man, keys):
                out[a][b] = "walk"
        for y, s, pt in model.gaps.get(a, ()):
            if y not in out[a] and model.gap_ok(a, y, s, base, man, keys) and not (
                    model.can_pass(a, s, base, man, keys) and model.can_pass(s, y, base, man, keys)):
                out[a][y] = "gap"
        for b, _, kind in model.moves_nonwalk(a, base, man, keys):
            if kind != "gap":
                out[a].setdefault(b, kind)
    return out, base, man


def bfs(out, starts):
    seen = set(starts)
    q = deque(starts)
    while q:
        a = q.popleft()
        for b in out.get(a, ()):
            if b not in seen:
                seen.add(b)
                q.append(b)
    return seen


def components(nodes, edges):
    parent = {v: v for v in nodes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    return {v: find(v) for v in nodes}


def linear_extensions(items, before):
    """Number of orders of items consistent with `before` (set of (x, y): x before y)."""
    count = 0
    for perm in itertools.permutations(items):
        pos = {x: i for i, x in enumerate(perm)}
        if all(pos[x] < pos[y] for x, y in before if x in pos and y in pos):
            count += 1
    return count


class LOS:
    """2D line of sight, blocked by one-sided lines and closed two-sided lines."""

    def __init__(self, model, base):
        m = model.m
        self.segs = []
        for i, ln in enumerate(m.lines):
            f, b = model.secs_of_line[i]
            if b is not None and b != f:
                if any(min(ca, cb) - max(fa, fb) > 0 for fa, ca in base[f] for fb, cb in base[b]):
                    continue
            elif b is not None:
                continue
            p, q = m.verts[ln.v1], m.verts[ln.v2]
            self.segs.append((p, q, min(p[0], q[0]), max(p[0], q[0]), min(p[1], q[1]), max(p[1], q[1])))

    def clear(self, a, b):
        x0, x1 = min(a[0], b[0]), max(a[0], b[0])
        y0, y1 = min(a[1], b[1]), max(a[1], b[1])
        for p, q, sx0, sx1, sy0, sy1 in self.segs:
            if sx1 < x0 or sx0 > x1 or sy1 < y0 or sy0 > y1:
                continue
            if seg_cross(a, b, p, q):
                return False
        return True


def seen_before(model, snaps, wave, target):
    """Is the point visible from a sector reachable at an earlier wave?"""
    if wave <= 0:
        return None
    base, man, keys, R = snaps[wave - 1]
    los = LOS(model, base)
    for s in sorted(R, key=lambda s: math.dist(model.inner[s], target)):
        if los.clear(model.inner[s], target):
            return 1
    return 0


SOUND_RANGE = 1200   # S_CLIPPING_DIST: vanilla plays no sound from farther (P_AproxDistance)


def _aprox(a, b):
    """P_AproxDistance."""
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return dx + dy - min(dx, dy) / 2


def _offset(m, ln, t, d, along=0.0):
    """The point d units to the right (front) of line ln at fraction t along
    it, moved `along` units further along it."""
    (x1, y1), (x2, y2) = m.verts[ln.v1], m.verts[ln.v2]
    L = m.length(ln) or 1
    x, y = x1 + (x2 - x1) * t + (x2 - x1) / L * along, y1 + (y2 - y1) * t + (y2 - y1) / L * along
    return x + (y2 - y1) / L * d, y - (x2 - x1) / L * d


def _seg_dist(p, a, b):
    (ax, ay), (bx, by) = a, b
    L2 = (bx - ax) ** 2 + (by - ay) ** 2 or 1
    t = max(0.0, min(1.0, ((p[0] - ax) * (bx - ax) + (p[1] - ay) * (by - ay)) / L2))
    return math.dist(p, (ax + (bx - ax) * t, ay + (by - ay) * t))


def switch_views(md, res, effective, required):
    """For each trigger group that changes the map (effective) and has a switch
    or a shootable line the player sets off: can the player see the change
    from where they set it off, and would they hear it. Returns dicts: group,
    required, trigger (index into md.triggers), site (the region it's used
    from), wave, eye (x, y), visible, dist (vanilla's approximate distance to
    the nearest moved sector's sound origin), heard.

    Seen: 2D line of sight, with the heights of the wave the switch is used
    in, from anywhere the player can stand to use it (points 16-64 units in
    front of the switch, up to 48 along it either way, within 64 of it, in a
    region reachable then, with nothing between them and the switch; a
    shootable line counts from either side) to a moved sector's floor (its
    inner point) or to a face of it (points just outside its two-sided
    boundary lines). The player may turn
    round, so any direction counts; a floor sinking below a ledge's lip still
    counts as seen. Heard: vanilla plays a door's, lift's or floor's sound
    from its sector's bounding-box centre, to anyone within 1200 units
    (P_AproxDistance; light changes make no sound and aren't modelled)."""
    m = md.m
    snaps = res["snaps"]
    los = {}
    origin = {}
    for i, (fs, bs) in enumerate(md.osecs_of_line):
        for s in (fs, bs):
            if s is not None:
                o = origin.setdefault(s, [math.inf, math.inf, -math.inf, -math.inf])
                for v in (m.lines[i].v1, m.lines[i].v2):
                    x, y = m.verts[v]
                    o[:] = min(o[0], x), min(o[1], y), max(o[2], x), max(o[3], y)
    out = []
    for g in effective:
        if g[0] == "boss":
            continue
        fired = [ti for ti, t in enumerate(md.triggers)
                 if t["group"] == g and t["trig"][0] in "SG" and ti in res["trig_wave"]]
        if not fired:
            continue
        moved = set(md.tagged.get(g[0], []))
        targets = [md.inner[r] for s in moved for r in md.group[s]]
        for i, (fs, bs) in enumerate(md.osecs_of_line):
            if bs is None or (fs in moved) == (bs in moved):
                continue
            side = 2 if bs in moved else -2   # just outside the moved sector, facing it
            targets += [_offset(m, m.lines[i], t, side) for t in (0.25, 0.5, 0.75)]
        sounds = [((o[0] + o[2]) / 2, (o[1] + o[3]) / 2) for o in (origin[s] for s in moved if s in origin)]
        best = None
        for ti in fired:
            w, site = res["trig_wave"][ti], res["trig_site"][ti]
            t = md.triggers[ti]
            ln = m.lines[t["line"]]
            R = snaps[w][3]
            if w not in los:
                los[w] = LOS(md, snaps[w][0])
            a, b = m.verts[ln.v1], m.verts[ln.v2]
            half = (m.length(ln) or 1) / 2
            eyes = [p for side in ((1,) if t["trig"][0] == "S" else (1, -1)) for d in (16, 32, 48, 64)
                    for along in (0, -24, 24, -48, 48)
                    if _seg_dist(p := _offset(m, ln, 0.5, side * d, along), a, b) <= 64
                    and (r := md.region_of_point(*p)) is not None and r in R
                    and los[w].clear(_offset(m, ln, 0.5, side, max(-half, min(half, along))), p)]   # not through a wall
            for eye in eyes or [_offset(m, ln, 0.5, 16)]:
                seen = any(los[w].clear(eye, p) for p in sorted(targets, key=lambda p: math.dist(p, eye)))
                dist = min((_aprox(eye, p) for p in sounds), default=math.inf)
                cand = dict(group=g, required=g in required, trigger=ti, site=site, wave=w, eye=eye, visible=seen,
                            dist=dist if dist == math.inf else round(dist), heard=dist <= SOUND_RANGE)
                if best is None or (cand["visible"], cand["heard"], -cand["dist"]) > \
                        (best["visible"], best["heard"], -best["dist"]):
                    best = cand
        out.append(best)
    return out


def scc(graph):
    """Strongly connected components (iterative Tarjan) of {node: [succ]}."""
    index, low, on, stack, out = {}, {}, set(), [], []
    counter = 0
    for root in graph:
        if root in index:
            continue
        work = [(root, iter(graph[root]))]
        index[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on.add(root)
        while work:
            v, it = work[-1]
            advanced = False
            for w in it:
                if w not in index:
                    index[w] = low[w] = counter
                    counter += 1
                    stack.append(w)
                    on.add(w)
                    work.append((w, iter(graph.get(w, ()))))
                    advanced = True
                    break
                if w in on:
                    low[v] = min(low[v], index[w])
            if advanced:
                continue
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[v])
            if low[v] == index[v]:
                comp = []
                while True:
                    w = stack.pop()
                    on.discard(w)
                    comp.append(w)
                    if w == v:
                        break
                out.append(comp)
    return out


def analyse(md, res):
    """The metrics row (and debug data) of a model and its run (run with snapshots)."""
    m = md.m
    R = res["R"]
    area = md.area
    walk = [s for s in range(md.n)
            if area[s] > 0 and any(c - f >= HEIGHT for f, c in res["perm"][s] | {md.manual_open[s] or (0, 0)})]
    walk_area = sum(area[s] for s in walk)
    reach_area = sum(area[s] for s in R)
    row = dict(map=m.slot, game=m.game, episode=episode(m.slot), sectors=md.ns, regions=md.n,
               walkable_area_mu2=round(walk_area), reachable_area_share=round(reach_area / walk_area, 3),
               reachable_region_share=round(len(R) / len(walk), 3))
    ex = md.normal_exit(res)
    sx = md.secret_exit(res)
    row["exit_reachable"] = int(ex is not None)
    row["exit_type"] = ("none" if ex is None else
                        "boss" if ex[2][0] == "boss" else "sector" if ex[2][0] == "sector"
                        else ("switch" if next(t for k, i, t in md.exits if i == ex[2][1])[0] == "S" else "walk"))
    row["secret_exit"] = int(any(k == "secret_exit" for k, _, _ in md.exits))
    row["secret_exit_reachable"] = int(sx is not None)
    row["event_waves"] = res["waves"]
    row["exit_wave"] = ex[0] if ex else ""

    # ---- keys and locks
    row["n_keys"] = len(md.key_colours)
    locked_secs, locked_lines = set(), 0
    for (f, b), ks in md.door_in.items():
        if any(ks):
            locked_secs.add(b)
    for i, f, b, key in md.stay_doors:
        if key:
            locked_secs.add(b)
    for t in md.triggers:
        if t["key"]:
            locked_secs.update(r for o in md.tagged.get(t["tag"], []) for r in md.group[o])
    for ln in m.lines:
        spec = dw.LINE_SPECIALS.get(ln.special)
        if spec and spec.key:
            locked_lines += 1
    row["n_locked_doors"] = len(locked_secs)
    row["n_locked_lines"] = locked_lines

    def exit_ok(r):
        return md.normal_exit(r) is not None

    keys_req = []
    key_dep = set()
    for k in md.key_colours:
        r = md.run(off_keys=frozenset([k]))
        if ex and not exit_ok(r):
            keys_req.append(k)
        for k2 in md.key_colours:
            if k2 != k and k2 in res["keys"] and k2 not in r["keys"]:
                key_dep.add((k, k2))
    row["n_keys_required"] = len(keys_req)
    # longest chain of keys in the dependency order
    depth = {}
    for k in sorted(md.key_colours, key=lambda k: res["key_wave"].get(k, 99)):
        depth[k] = 1 + max((depth.get(a, 1) for a, b in key_dep if b == k), default=0)
    row["key_chain_depth"] = max(depth.values(), default=0)
    got = [k for k in md.key_colours if k in res["keys"]]
    row["key_orders"] = linear_extensions(got, key_dep) if got else 0

    # ---- triggers
    trig_lines = defaultdict(int)
    for t in md.triggers:
        trig_lines[t["trig"][0]] += 1
    row["n_switch_lines"] = trig_lines["S"]
    row["n_walk_lines"] = trig_lines["W"]
    row["n_gun_lines"] = trig_lines["G"]
    groups = [g for g in md.groups] + [("boss", i) for i in range(len(md.boss))]
    base_R = R
    effective, required = [], []
    for g in groups:
        if g[0] == "boss":
            if g[1] not in res["boss_wave"]:
                continue
        elif not any(t["group"] == g for ti, t in enumerate(md.triggers) if ti in res["trig_wave"]):
            continue
        r = md.run(off_groups=frozenset([g]))
        if len(r["R"]) < len(base_R) or r["keys"] != res["keys"] or not exit_ok(r):
            effective.append(g)
        if ex and not exit_ok(r):
            required.append(g)
    row["n_trigger_groups"] = len(md.groups)
    row["n_triggers_effective"] = sum(1 for g in effective if g[0] != "boss")
    row["n_triggers_required"] = sum(1 for g in required if g[0] != "boss")
    row["boss_gate"] = int(any(g[0] == "boss" for g in required) or (ex is not None and ex[2][0] == "boss"))

    # ---- critical path: start -> required keys/triggers (in the wave they
    # become available; best order within a wave) -> exit, each leg the
    # shortest sector path under the heights of that wave.
    snaps = res["snaps"]
    goals = []   # (wave, site sector or [sectors], label)
    for k in keys_req:
        goals.append((res["key_wave"][k], res["key_site"][k][0], "key:" + k))
    for g in required:
        if g[0] == "boss":
            goals.append((res["boss_wave"][g[1]], res["boss_site"][g[1]], "boss"))
            continue
        cands = [(res["trig_wave"][ti], res["trig_site"][ti]) for ti, t in enumerate(md.triggers)
                 if t["group"] == g and ti in res["trig_wave"]]
        w = min(c[0] for c in cands)
        goals.append((w, sorted({c[1] for c in cands if c[0] == w}), "trig:%s/%s" % g))
    crit_seq, steps, fallbacks = [md.start], [], 0   # steps: (a, b, kind, length, one_way)
    legs = []   # (goal label, wave, region path, length) in walking order
    if ex:
        by_wave = defaultdict(list)
        for w, site, lab in goals:
            by_wave[w].append((site, lab))
        cur_s = md.start
        for w in sorted(set(by_wave) | {ex[0]}):
            base, man, keys, Rw = snaps[w]

            def leg(a, site):
                best = None
                for s in (site if isinstance(site, list) else [site]):
                    p = dijkstra(md, a, s, base, man, keys)
                    if p and (best is None or p[0] < best[0]):
                        best = p
                return best

            items = by_wave.get(w, [])
            order = items
            if 1 < len(items) <= 6:
                best = None
                for perm_ in itertools.permutations(items):
                    total, a, ok = 0.0, cur_s, True
                    for site, _ in perm_:
                        p = leg(a, site)
                        if p is None:
                            ok = False
                            break
                        total += p[0]
                        a = p[1][-1]
                    if ok and (best is None or total < best[0]):
                        best = (total, perm_)
                order = best[1] if best else items
            if w == ex[0]:
                order = list(order) + [(ex[1], "exit")]
            for site, lab in order:
                p = leg(cur_s, site)
                if p is None:
                    fallbacks += 1
                    p = leg(md.start, site)
                    if p is None:
                        continue
                length, path, kinds = p
                legs.append((lab, w, path, length))
                for a, b, kind in zip(path, path[1:], kinds):
                    one_way = kind in ("walk", "gap") and not any(
                        x == a for x, _, _ in md.moves(b, base, man, keys))
                    L = md.edge_len(a, b) if kind == "walk" else next(
                        ln for x, ln, kd in md.moves(a, base, man, keys) if x == b and kd == kind)
                    steps.append((a, b, kind, L, one_way))
                crit_seq.extend(path[1:] if path[0] == crit_seq[-1] else path)
                cur_s = path[-1]
    crit_len = sum(s[3] for s in steps)
    uniq = set(crit_seq)
    row["crit_goals"] = len(goals)
    row["crit_path_len"] = round(crit_len) if ex else ""
    if ex:
        straight = math.dist(md.centroid[md.start], md.centroid[ex[1]])
        row["crit_path_straightness"] = round(crit_len / straight, 2) if straight > 0 else ""
    else:
        row["crit_path_straightness"] = ""
    row["crit_sector_share"] = round(len(uniq) / len(R), 3)
    crit_area = sum(area[s] for s in uniq)
    row["crit_area_share"] = round(crit_area / reach_area, 3)
    row["optional_area_share"] = round(1 - crit_area / reach_area, 3)
    row["crit_revisits"] = len(crit_seq) - len(uniq)
    row["crit_revisit_ratio"] = round(len(crit_seq) / len(uniq), 2)
    back_len, seen_s = 0.0, {md.start}
    for a, b, kind, L, _ in steps:
        if b in seen_s:
            back_len += L
        seen_s.add(b)
    row["crit_backtrack_len_share"] = round(back_len / crit_len, 3) if crit_len else 0.0
    row["crit_one_way_steps"] = sum(1 for s in steps if s[4])
    row["crit_teleports"] = sum(1 for s in steps if s[2] == "teleport")
    row["crit_gap_steps"] = sum(1 for s in steps if s[2] in ("gap", "jump"))
    row["crit_fallback_legs"] = fallbacks

    # ---- final-state graph: loops, rooms, dead ends, one-way regions
    out, fbase, fman = final_graph(md, res)
    und = set()
    for a in R:
        for b in out.get(a, ()):
            if b in R and a != b:
                und.add((min(a, b), max(a, b)))
    comp = components(R, und)
    row["cyclomatic_sector"] = len(und) - len(R) + len(set(comp.values()))
    # Rooms: merge sectors joined by a two-way walk edge unless either is a
    # door or lift/platform sector (those stay single-sector connector nodes).
    merge = [(a, b) for a, b in und if a not in md.connectors and b not in md.connectors
             and out[a].get(b) == "walk" and out[b].get(a) == "walk"]
    room = components(R, merge)
    rooms = set(room.values())
    room_out = defaultdict(set)
    for a in R:
        for b in out.get(a, ()):
            if b in R and room[a] != room[b]:
                room_out[room[a]].add(room[b])
    room_edges = {(min(x, y), max(x, y)) for x in room_out for y in room_out[x]}
    rc = components(rooms, room_edges)
    row["cyclomatic_room"] = len(room_edges) - len(rooms) + len(set(rc.values()))
    row["one_way_room_links"] = sum(1 for x in list(room_out) for y in room_out[x]
                                    if x not in room_out.get(y, ()))
    is_conn = {r: all(s in md.connectors for s in R if room[s] == r) for r in rooms}
    real = [r for r in rooms if not is_conn[r]]
    room_adj = defaultdict(set)
    for x, y in room_edges:
        room_adj[x].add(y)
        room_adj[y].add(x)
    nbr = defaultdict(set)   # neighbouring rooms, looking through connector nodes
    for r in real:
        seen_r, q = {r}, deque([r])
        while q:
            x = q.popleft()
            for y in room_adj[x]:
                if y in seen_r:
                    continue
                seen_r.add(y)
                if is_conn[y]:
                    q.append(y)
                else:
                    nbr[r].add(y)
    dead = [r for r in real if len(nbr[r]) == 1]
    row["n_rooms"] = len(real)
    row["dead_end_rooms"] = len(dead)
    row["dead_end_room_share"] = round(len(dead) / len(real), 3) if real else 0.0
    # Strongly connected components: regions you cannot walk back out of.
    sccs = scc({a: [b for b in out.get(a, ()) if b in R] for a in R})
    scc_area = sorted((sum(area[s] for s in c) for c in sccs), reverse=True)
    row["main_region_area_share"] = round(scc_area[0] / reach_area, 3)
    row["one_way_regions"] = sum(1 for x in scc_area[1:] if x >= 0.02 * reach_area)
    # critical path at room level
    rseq = []
    for s in crit_seq:
        r = room.get(s, ("x", s))
        if not rseq or rseq[-1] != r:
            rseq.append(r)
    row["crit_rooms"] = len(set(rseq))
    row["crit_room_revisits"] = len(rseq) - len(set(rseq))
    # exploration tour: twice the minimum spanning tree of the reachable walk graph
    par = {v: v for v in R}

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    mst = 0.0
    for w, a, b in sorted((md.edge_len(a, b), a, b) for a, b in und if (a, b) in md.portal):
        ra, rb = find(a), find(b)
        if ra != rb:
            par[ra] = rb
            mst += w
    row["crit_tour_share"] = round(crit_len / (2 * mst), 3) if ex and mst else ""

    # ---- teleporters
    row["n_teleport_lines"] = len(md.teleports)
    row["n_teleporters"] = len({(b, ds) for i, f, b, ds, _ in md.teleports if f in R})

    # ---- secrets (counted per sector, as the game does)
    secrets = [o for o, sec in enumerate(m.sectors) if sec.special == dw.SECRET_SPECIAL]
    row["n_secrets"] = len(secrets)
    row["secrets_reachable"] = sum(1 for o in secrets if any(r in R for r in md.group[o]))
    row["secret_area_share"] = round(sum(area[r] for o in secrets for r in md.group[o]) / walk_area, 4)

    # ---- sky (Romero rule 5: if you can see outside you can get there)
    sky = [s for s in range(md.n)
           if md.sec(s).ctex == dw.SKY and area[s] > 0 and max(c - f for f, c in res["perm"][s]) > 0]
    sky_area = sum(area[s] for s in sky)
    row["sky_area_share"] = round(sky_area / walk_area, 3)
    row["sky_reachable_share"] = round(sum(area[s] for s in sky if s in R) / sky_area, 3) if sky_area else ""

    # ---- see it before you reach it
    teased, later = 0, 0
    for k in got:
        w = res["key_wave"][k]
        ki = res["key_site"][k][1]
        v = seen_before(md, snaps, w, md.keys[ki][2])
        if v is not None:
            later += 1
            teased += v
    row["keys_after_events"] = later
    row["keys_teased"] = teased
    if ex and ex[2][0] == "line":
        ln = m.lines[ex[2][1]]
        mid = m.midpoint(ln)
        (x1, y1), (x2, y2) = m.verts[ln.v1], m.verts[ln.v2]
        L = m.length(ln) or 1
        pt = (mid[0] + (y2 - y1) / L * 2, mid[1] - (x2 - x1) / L * 2)  # 2 units in front
        v = seen_before(md, snaps, ex[0], pt)
        row["exit_teased"] = "" if v is None else v
    elif ex:
        v = seen_before(md, snaps, ex[0], md.inner[ex[1]])
        row["exit_teased"] = "" if v is None else v
    else:
        row["exit_teased"] = ""

    # ---- switches: is what they do seen or heard from where they're used
    views = switch_views(md, res, effective, required)
    for pre, vs in (("", views), ("req_", [v for v in views if v["required"]])):
        hidden = [v for v in vs if not v["visible"]]
        row[pre + "switches"] = len(vs)
        row[pre + "switches_hidden"] = len(hidden)
        row[pre + "switches_unheard"] = sum(1 for v in hidden if not v["heard"])
        row[pre + "switch_hidden_max_dist"] = max((v["dist"] for v in hidden if v["dist"] != math.inf), default="")
    debug = dict(model=md, res=res, goals=goals, keys_req=keys_req, required=required,
                 effective=effective, key_dep=key_dep, crit_seq=crit_seq, legs=legs, room=room, exit=ex,
                 switches=views)
    return row, debug


def analyse_map(m, textures):
    """The metrics row and debug data of a map, running jumps only where the
    exit needs them (see levels.reach.solve)."""
    md, res = solve(m, textures)
    row, dbg = analyse(md, res)
    row["model_jumps"] = int(md.use_jumps)
    return row, dbg


def _row(job):
    return analyse_map(*job)[0]


def main(argv):
    maps, out, argv = dw.select(argv, OUT)
    textures = dw.reach_textures(maps)
    if argv:
        for m in maps:
            if m.slot in argv:
                row, dbg = analyse_map(m, textures[m.iwad, m.pwads])
                for k, v in row.items():
                    print(f"{k:28} {v}")
                print("goals", dbg["goals"])
                print("required", dbg["required"], "keys_req", dbg["keys_req"], "key_dep", dbg["key_dep"])
                print("exit", dbg["exit"], "start", dbg["model"].start)
        return
    rows = dw.parallel_rows(_row, [(m, textures[m.iwad, m.pwads]) for m in maps], maps, out)
    dw.write_rows(rows, out)


if __name__ == "__main__":
    main(sys.argv[1:])
