"""The research measurements, run on a level as it builds, against the id maps
of its game (DOOM II, or Ultimate Doom for ExMy maps).

Every build prints these, so a map's numbers are known before it's played:
rule-1 slips (floor-texture changes with no height change) by sector pair,
rule-2 seams (two wall materials meeting in one plane with no border texture
between them) by sector, and a table of the research metrics (scripts/metrics/)
with each one's median and interquartile range over the game's maps, flagged
when outside it, then the resource curve and exposure flags along the route
(levels/balance.py). The progression metrics reuse the build checks'
reach-model run.
"""
import math
import os
import re
import sys
from collections import Counter, defaultdict

from .balance import health_rate, report, route_balance
from .model import label_point

METRICS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "metrics")

# Quartiles (q1, median, q3) of each metric over DOOM II MAP01-MAP32 and
# Ultimate Doom E1M1-E4M9, from the research CSVs (research/data/metrics_*.csv,
# written by scripts/metrics/; route_* from route_metrics.py, see
# levels/balance.py): statistics.quantiles(values, n=4, method="exclusive"),
# rounded to 4 significant digits.
DOOM2 = {
    "walkable_area": (4.681e+06, 8.382e+06, 1.144e+07),
    "frac_width_le96": (0.02797, 0.06135, 0.1148),
    "distinct_floor_heights": (15.25, 23, 34.5),
    "light_sd": (19.23, 23.48, 29.23),
    "n_light_special_sectors": (3, 9, 14),
    "r1_floor_viol": (0.008825, 0.03095, 0.0913),
    "top_wall_tex_share": (0.1961, 0.2955, 0.4505),
    "r2_border_frac_collinear": (0.1295, 0.313, 0.6276),
    "sym_max": (0.4349, 0.5367, 0.642),
    "optional_area_share": (0.3285, 0.497, 0.7077),
    "n_secrets": (2, 4, 6.75),
    "monsters_hard": (80, 111.5, 158),
    "hp_density_hard": (1021, 1985, 2477),
    "share_heavy_hard": (0.018, 0.1005, 0.25),
    "ammo_ratio_ps_hard": (1.374, 1.812, 2.727),
    "health_per_khp_hard": (25.7, 39.8, 60.02),
    "count_ratio_easy_hard": (0.2677, 0.3315, 0.4565),
    "count_ratio_medium_hard": (0.6538, 0.7, 0.7648),
    "ambush_share_hard": (0.2278, 0.4235, 0.6635),
    "nearest_monster_dist_hard": (231, 299.5, 515.2),
    "route_min_detour_ratio": (0.3217, 0.6535, 1.544),
    "route_min_thorough_share": (-0.6893, 0.113, 0.728),
    "route_max_long_hitscan": (0, 0, 35.5),
    "route_health_per_khp": (9.947, 17.29, 30.7),
}
ULTIMATE = {
    "walkable_area": (4.803e+06, 6.386e+06, 9.306e+06),
    "frac_width_le96": (0.049, 0.07235, 0.1099),
    "distinct_floor_heights": (14.25, 23, 32),
    "light_sd": (17.84, 30.01, 37.88),
    "n_light_special_sectors": (2, 9, 14),
    "r1_floor_viol": (0.0241, 0.0481, 0.1026),
    "top_wall_tex_share": (0.1812, 0.3089, 0.5327),
    "r2_border_frac_collinear": (0.4444, 0.64, 0.7748),
    "sym_max": (0.4617, 0.5495, 0.64),
    "optional_area_share": (0.3553, 0.4395, 0.587),
    "n_secrets": (2, 3.5, 6),
    "monsters_hard": (60.75, 90.5, 124.5),
    "hp_density_hard": (826.7, 1552, 2443),
    "share_heavy_hard": (0, 0.08, 0.129),
    "ammo_ratio_ps_hard": (1.554, 2.081, 2.975),
    "health_per_khp_hard": (27.17, 37.9, 56.17),
    "count_ratio_easy_hard": (0.279, 0.4485, 0.563),
    "count_ratio_medium_hard": (0.661, 0.749, 0.8188),
    "ambush_share_hard": (0.1915, 0.3245, 0.6545),
    "nearest_monster_dist_hard": (250, 365.5, 560.5),
    "route_min_detour_ratio": (0.5897, 0.8885, 1.566),
    "route_min_thorough_share": (-0.4617, 0.009, 0.5358),
    "route_max_long_hitscan": (0, 10, 21.5),
    "route_health_per_khp": (16.66, 22.02, 45.44),
}
LABELS = {
    "walkable_area": "walkable area (units^2)",
    "frac_width_le96": "area <= 96 wide",
    "distinct_floor_heights": "distinct floor heights",
    "light_sd": "light SD",
    "n_light_special_sectors": "light-effect sectors",
    "r1_floor_viol": "rule-1 slips (share of flat changes)",
    "top_wall_tex_share": "most-used wall texture",
    "r2_border_frac_collinear": "rule-2 seams with a border texture",
    "sym_max": "whole-map symmetry",
    "optional_area_share": "optional share of area",
    "n_secrets": "secrets",
    "monsters_hard": "monsters (UV)",
    "hp_density_hard": "monster HP per million units^2 (UV)",
    "share_heavy_hard": "heavy-monster share (UV)",
    "ammo_ratio_ps_hard": "ammo damage / monster HP (UV, pistol start)",
    "health_per_khp_hard": "health per 1000 monster HP (UV)",
    "count_ratio_easy_hard": "easy / UV monsters",
    "count_ratio_medium_hard": "HMP / UV monsters",
    "ambush_share_hard": "deaf share (UV)",
    "nearest_monster_dist_hard": "nearest monster to the start (UV)",
    "route_min_detour_ratio": "lowest ammo ratio near the route (UV)",
    "route_min_thorough_share": "lowest ammo left / HP, taking everything",
    "route_max_long_hitscan": "long-range hitscan peak per second (UV)",
    "route_health_per_khp": "health per 1000 HP the route affords",
}


def check_sector_overlaps(level):
    """No sector lies inside another that doesn't have it as a hole. (Sectors
    whose edges cross are caught when lines are built, so a sector inside
    another is the remaining way two can overlap.)"""
    errors = []
    for s in level.sectors.values():
        for loop in s.outer_loops():
            if (p := label_point(s, loop)) is None:
                continue
            for o in level.sectors.values():
                if o is not s and o.contains(p):
                    errors.append(f"sector {s.name} overlaps {o.name} (at {p[0]:.0f},{p[1]:.0f}); "
                                  f"make it a hole in {o.name} or move it")
    return errors


def rule1_slips(level, lines):
    """{(sector, sector): length} of two-sided lines where the floor texture
    changes but the height doesn't (Romero's rule 1), longest first."""
    slips = Counter()
    for l in lines:
        f, b = l.front, l.back
        if b and f is not b and f.ftex != b.ftex and f.floor == b.floor:
            slips[tuple(sorted((f.name, b.name)))] += l.length
    return slips.most_common()


def texture_family(name):
    """A texture's family: its name without trailing digits, first four
    letters (STARTAN1/STARTAN3/STARG2 -> STAR, BROWN1/BROWNGRN -> BROW)."""
    return re.sub(r"\d+$", "", name)[:4]


def rule2_seams(m, names, sm, textures):
    """[(sector, tex, tex, count, (x, y))] of wall surfaces that meet another
    texture in the same plane (within 30 degrees) where neither is a border
    texture (Romero's rule 2), most first, with one junction to look at. These
    are the r2_border_frac_collinear metric's unbordered junctions, less those
    between variants of one family (STONE2 beside STONE3), which belong
    together."""
    parts = sm.wall_parts(m, textures)
    starts = defaultdict(list)
    for p in parts:
        starts[p[1]].append(p)
    cos30 = math.cos(math.radians(30))
    seams, where = Counter(), {}
    for a in parts:
        line, v0, va, ta, zlo, zhi, la = a[0], a[1], a[2], a[3], a[4], a[5], a[9]
        ln = m.lines[line]
        side = ln.front if (v0, va) == (ln.v1, ln.v2) else ln.back
        for b in starts.get(va, ()):
            tb = b[3]
            if (b[0] == line or ta == tb or min(zhi, b[5]) - max(zlo, b[4]) <= 0 or not la or not b[9]
                    or sm.BORDER_EXT.match(ta) or sm.BORDER_EXT.match(tb)
                    or texture_family(ta) == texture_family(tb)):
                continue
            (ax, ay), (vx, vy), (bx, by) = m.verts[v0], m.verts[va], m.verts[b[2]]
            if ((vx - ax) * (bx - vx) + (vy - ay) * (by - vy)) / (la * b[9]) > cos30:
                k = (names[m.sides[side].sector], *sorted((ta, tb)))
                seams[k] += 1
                where.setdefault(k, (vx, vy))
    return [(*k, n, where[k]) for k, n in seams.most_common()]


_textures = {}


def measure(level, lines, found):
    """Report lines: rule-1 slips, then each metric against the game's id
    maps. found: the level's checks.Findings, whose reach run is reused."""
    if METRICS_DIR not in sys.path:
        sys.path.insert(0, METRICS_DIR)
    import combat_metrics as cm
    import progression_metrics as pm
    import space_metrics as sm
    from .wad import IWADS
    key = (level.game, tuple(level.resources))
    if key not in _textures:
        _textures[key] = sm.texture_info(IWADS[level.game], level.resources)
    m, md, res = found.reach
    prog, route = pm.analyse(md, res)
    bal = route_balance(m, md, res, route["legs"], names=list(level.sectors))
    rate = health_rate(bal)
    row = {**sm.analyse((m, _textures[key])), **cm.map_metrics(m, {})[0], **prog, **bal.summary,
           "route_health_per_khp": "" if rate is None else 1000 * rate}
    out = []
    slips = rule1_slips(level, lines)
    if slips:
        out.append("rule-1 slips (floor texture changes, height doesn't): "
                   + ", ".join(f"{a}/{b} {n:.0f}" for (a, b), n in slips))
    seams = rule2_seams(m, list(level.sectors), sm, _textures[key])
    if seams:
        out.append("rule-2 seams (wall material changes in one plane, no border texture): "
                   + ", ".join(f"{s} {a}|{b} x{n} at ({x:.0f},{y:.0f})" for s, a, b, n, (x, y) in seams))
    table, name = (ULTIMATE, "Ultimate Doom") if level.game == "doom" else (DOOM2, "DOOM II")
    out.append(f"{'measure':<44} {'map':>9}   {name} median [IQR]")
    for k, (q1, med, q3) in table.items():
        v = row.get(k)
        if not isinstance(v, (int, float)):   # missing, or "" where undefined (no monsters, ...)
            continue
        flag = "  below" if v < q1 else "  above" if v > q3 else ""
        out.append(f"{LABELS[k]:<44} {fmt(v):>9}   {fmt(med)} [{fmt(q1)}-{fmt(q3)}]{flag}")
    lines, warnings = report(bal, level.game)
    return out + lines + [f"warning: {w}" for w in warnings]


def fmt(v):
    return f"{v:,.0f}" if abs(v) >= 100 else f"{v:.2f}".rstrip("0").rstrip(".") if v % 1 else f"{v:.0f}"

