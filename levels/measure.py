"""The research measurements, run on a level as it builds, against the id maps
of its game (DOOM II, or Ultimate Doom for ExMy maps).

Every build prints these, so a map's numbers are known before it's played:
rule-1 slips (floor-texture changes with no height change) by sector pair, and
a table of the research metrics (scripts/metrics/) with each one's median and
interquartile range over the game's maps, flagged when outside it. The
progression metrics reuse the build checks' reach-model run.
"""
import os
import sys
from collections import Counter

from .model import label_point

METRICS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "metrics")

# Quartiles (q1, median, q3) of each metric over DOOM II MAP01-MAP32 and
# Ultimate Doom E1M1-E4M9, from the research CSVs (research/data/metrics_*.csv,
# written by scripts/metrics/): statistics.quantiles(values, n=4,
# method="exclusive"), rounded to 4 significant digits.
DOOM2 = {
    "walkable_area": (4.681e+06, 8.382e+06, 1.144e+07),
    "frac_width_le96": (0.02797, 0.06135, 0.1148),
    "distinct_floor_heights": (15.25, 23, 34.5),
    "light_sd": (19.23, 23.48, 29.23),
    "n_light_special_sectors": (3, 9, 14),
    "r1_floor_viol": (0.008825, 0.03095, 0.0913),
    "top_wall_tex_share": (0.1961, 0.2955, 0.4505),
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
}
ULTIMATE = {
    "walkable_area": (4.803e+06, 6.386e+06, 9.306e+06),
    "frac_width_le96": (0.049, 0.07235, 0.1099),
    "distinct_floor_heights": (14.25, 23, 32),
    "light_sd": (17.84, 30.01, 37.88),
    "n_light_special_sectors": (2, 9, 14),
    "r1_floor_viol": (0.0241, 0.0481, 0.1026),
    "top_wall_tex_share": (0.1812, 0.3089, 0.5327),
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
}
LABELS = {
    "walkable_area": "walkable area (units^2)",
    "frac_width_le96": "area <= 96 wide",
    "distinct_floor_heights": "distinct floor heights",
    "light_sd": "light SD",
    "n_light_special_sectors": "light-effect sectors",
    "r1_floor_viol": "rule-1 slips (share of flat changes)",
    "top_wall_tex_share": "most-used wall texture",
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
    row = {**sm.analyse((m, _textures[key])), **cm.map_metrics(m, {})[0], **pm.analyse(md, res)[0]}
    out = []
    slips = rule1_slips(level, lines)
    if slips:
        out.append("rule-1 slips (floor texture changes, height doesn't): "
                   + ", ".join(f"{a}/{b} {n:.0f}" for (a, b), n in slips))
    table, name = (ULTIMATE, "Ultimate Doom") if level.game == "doom" else (DOOM2, "DOOM II")
    out.append(f"{'measure':<44} {'map':>9}   {name} median [IQR]")
    for k, (q1, med, q3) in table.items():
        v = row.get(k)
        if not isinstance(v, (int, float)):   # missing, or "" where undefined (no monsters, ...)
            continue
        flag = "  below" if v < q1 else "  above" if v > q3 else ""
        out.append(f"{LABELS[k]:<44} {fmt(v):>9}   {fmt(med)} [{fmt(q1)}-{fmt(q3)}]{flag}")
    return out


def fmt(v):
    return f"{v:,.0f}" if abs(v) >= 100 else f"{v:.2f}".rstrip("0").rstrip(".") if v % 1 else f"{v:.0f}"

