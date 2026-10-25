"""The research measurements, run on a level as it builds, against the DOOM II maps.

Every build prints these, so a map's numbers are known before it's played:
rule-1 slips (floor-texture changes with no height change) by sector pair, and
a table of the research metrics (scripts/metrics/) with each one's DOOM II
median and interquartile range, flagged when outside it.
"""
import os
import sys
from collections import Counter

METRICS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "metrics")

# DOOM II MAP01-MAP32 quartiles (q1, median, q3) of each metric, from the
# research CSVs (research/data/metrics_*.csv, written by scripts/metrics/).
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
    from .preview import label_point
    errors = []
    for s in level.sectors.values():
        p = label_point(s)
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


def measure(level, lines, map_lumps, iwad_path):
    """Report lines: rule-1 slips, then each metric against DOOM II."""
    if METRICS_DIR not in sys.path:
        sys.path.insert(0, METRICS_DIR)
    import combat_metrics as cm
    import doomwad as dw
    import progression_metrics as pm
    import space_metrics as sm
    from .wad import iwad_textures
    if iwad_path not in _textures:
        sizes = iwad_textures(iwad_path)[0]
        _textures[iwad_path] = (sm.texture_info(iwad_path), (sizes, next(iter(sizes.values()))[1]))
    tex_space, tex_prog = _textures[iwad_path]
    m = dw._parse("doom2", level.map, dict(map_lumps[1:]))
    row = {**sm.analyse((m, tex_space)), **cm.map_metrics(m, {})[0], **pm.analyse_map(m, tex_prog)[0]}
    out = []
    slips = rule1_slips(level, lines)
    if slips:
        out.append("rule-1 slips (floor texture changes, height doesn't): "
                   + ", ".join(f"{a}/{b} {n:.0f}" for (a, b), n in slips))
    out.append(f"{'measure':<44} {'map':>9}   DOOM II median [IQR]")
    for k, (q1, med, q3) in DOOM2.items():
        v = row.get(k)
        if v is None:
            continue
        flag = "  below" if v < q1 else "  above" if v > q3 else ""
        out.append(f"{LABELS[k]:<44} {fmt(v):>9}   {fmt(med)} [{fmt(q1)}-{fmt(q3)}]{flag}")
    return out


def fmt(v):
    return f"{v:,.0f}" if abs(v) >= 100 else f"{v:.2f}".rstrip("0").rstrip(".") if v % 1 else f"{v:.0f}"

