"""Top-down SVGs of the official maps, drawn the way the builder draws our
own (levels/preview.py): each map is decompiled (levels/decompile.py), its
module loaded and compiled, and the preview written. Writes
research/maps/<set>/<map>.svg and research/maps/INDEX.md, which links each
SVG with a line of measurements from the research CSVs, where they exist. A
map the decompiler refuses is drawn from its raw linedefs and things instead
(no sector shading), and INDEX.md says so. Each map's decompile outcome goes
to data/metrics/decompile_status.csv, which the metrics scripts read for
their `decompile` column, so run this first.

Run from the repo root (stdlib only, uses all cores):
    python3 scripts/metrics/map_svgs.py                    # every set
    python3 scripts/metrics/map_svgs.py tnt master         # some sets
    python3 scripts/metrics/map_svgs.py --index            # only rewrite INDEX.md from the CSVs

Sets: doom and doom2 (DOOM_WAD, DOOM2_WAD) and doomwad.SETS (DOOM_STEAM_BASE).
A Master Level's SVG is <WAD>_<slot>.svg; every other map's is <slot>.svg.
"""
import csv
import glob
import importlib.util
import multiprocessing as mp
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import doomwad as dw  # noqa: E402  (also puts the repo root on sys.path)
from levels.decompile import Refused, decompile, map_entries, open_source  # noqa: E402
from levels.doom2 import ACTORS, PLAYERS  # noqa: E402
from levels.mapgen import compile_level  # noqa: E402
from levels.model import LevelError, Place, load  # noqa: E402
from levels.preview import write_svg  # noqa: E402
from levels.wadmap import parse  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
OUT = os.path.join(ROOT, "research", "maps")
DATA = dw.METRICS
SET_NAMES = ("doom", "doom2", *dw.SETS)
LINES_ONLY = "lines only (the decompiler refused this map)"


def wads_of(name):
    """The WADs a set's maps come from."""
    if name in ("doom", "doom2"):
        return [dw.IWADS[name]]
    base = os.path.expanduser(dw.read_env()["DOOM_STEAM_BASE"])
    iwad, pwads = dw.SETS[name]
    return sorted(glob.glob(os.path.join(base, pwads))) if pwads else [os.path.join(base, iwad)]


def svg_name(name, stem, slot):
    return f"{stem}_{slot}.svg" if name == "master" else f"{slot}.svg"


def write_raw_svg(m, path, scale=0.4, pad=96):
    """Lines-only preview of a wadmap.Map: one-sided lines black, two-sided
    grey, specials red; monsters red, the player start green."""
    x0, y0, x1, y1 = m.bbox
    x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    w, h = (x1 - x0) * scale, (y1 - y0) * scale + 40

    def xy(x, y):
        return (x - x0) * scale, (y1 - y) * scale

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" font-family="sans-serif">',
           '<rect width="100%" height="100%" fill="#fbfbf7"/>']
    for ln in m.lines:
        (ax, ay), (bx, by) = xy(*m.verts[ln.v1]), xy(*m.verts[ln.v2])
        style = ('stroke="#d0201a" stroke-width="2.5"' if ln.special else
                 'stroke="#111" stroke-width="1.6"' if ln.back < 0 else 'stroke="#777" stroke-width="0.6"')
        out.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" {style}/>')
    for t in m.things:
        x, y = xy(t.x, t.y)
        if t.type in PLAYERS:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{16 * scale + 1:.1f}" fill="#1a9e3a"/>')
        elif t.type in ACTORS:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{ACTORS[t.type].radius * scale:.1f}" '
                       'fill="#e03030" fill-opacity="0.6"/>')
    out.append(f'<text x="8" y="{h - 14:.0f}" font-size="11" fill="#222">{m.slot}: {LINES_ONLY}; black = wall, '
               'grey = two-sided, red = special; red circles = monsters, green = start</text>')
    out.append("</svg>")
    with open(path, "w") as f:
        f.write("\n".join(out))


def draw(job):
    """Decompile, load and preview one map: a dict for decompile_status.csv.
    decompile is ok or repaired (the decompiler repaired unclosed sectors),
    refused (decompile raised Refused) or lines-only (the module was written
    but doesn't load or compile). The last two get write_raw_svg."""
    name, path, slot, tmp = job
    src = open_source(path)
    fname = svg_name(name, src.stem, slot)
    out = os.path.join(OUT, name, fname)
    parts = dict(map_entries(src.lumps))[slot]
    row = {"set": name, "wad": src.stem, "slot": slot, "svg": f"{name}/{fname}"}
    try:
        res = decompile(src, slot, parts)
    except Refused as e:
        write_raw_svg(parse("doom" if slot[0] == "E" else "doom2", slot, parts), out)
        return {**row, "decompile": "refused", "detail": str(e).splitlines()[0][:300]}
    try:
        mod_path = os.path.join(tmp, f"{name}_{res.modname}.py")
        with open(mod_path, "w") as f:
            f.write(res.text)
        spec = importlib.util.spec_from_file_location(f"levels.imported.{name}_{res.modname}", mod_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        level = load(module, Place(f"imported/{src.stem}.WAD", slot))
        write_svg(level, compile_level(level).lines, out)
    except LevelError as e:
        write_raw_svg(parse("doom" if slot[0] == "E" else "doom2", slot, parts), out)
        return {**row, "decompile": "lines-only", "detail": str(e).splitlines()[0][:300]}
    return {**row, "decompile": "repaired" if res.done else "ok",
            "detail": f"{len(res.done)} repairs" if res.done else ""}


def measurements():
    """{(set, wad, slot): progression + space row} from every research CSV."""
    rows = {}
    for kind in ("progression", "space"):
        for path in [os.path.join(DATA, f"metrics_{kind}.csv")] + \
                sorted(glob.glob(os.path.join(DATA, "sets", "*", f"metrics_{kind}.csv"))):
            if os.path.exists(path):
                with open(path, newline="") as f:
                    for r in csv.DictReader(f):
                        if "set" in r:
                            rows.setdefault((r["set"], r["wad"], r["slot"]), {}).update(r)
    return rows


def summary(r):
    if not r:
        return "no measurements"
    out = []
    if "bbox_w" in r:
        out.append(f"{int(float(r['bbox_w']))}x{int(float(r['bbox_h']))}")
    if "sectors" in r:
        out.append(f"{r['sectors']} sectors")
    if "key_chain_depth" in r:
        out.append(f"key-chain depth {r['key_chain_depth']}")
    if "crit_path_len" in r:
        out.append(f"critical path {r['crit_path_len']}")
    return ", ".join(out)


def main(argv):
    if argv == ["--index"]:
        write_index(dw._csv(dw.DECOMPILE_STATUS))
        return
    names = argv or list(SET_NAMES)
    if bad := [n for n in names if n not in SET_NAMES]:
        sys.exit(f"unknown set {', '.join(bad)}: one of {', '.join(SET_NAMES)}")
    with tempfile.TemporaryDirectory() as tmp:
        jobs = []
        for name in names:
            os.makedirs(os.path.join(OUT, name), exist_ok=True)
            for path in wads_of(name):
                jobs += [(name, path, slot, tmp) for slot, _ in map_entries(open_source(path).lumps)]
        with mp.Pool(os.cpu_count() or 1) as pool:
            done = pool.map(draw, jobs, chunksize=1)
    for r in done:
        if r["decompile"] in ("refused", "lines-only"):
            print(f"{r['svg']}: {r['decompile']}: {r['detail'][:200]}")
    print(f"wrote {len(done)} SVGs under {os.path.relpath(OUT)} "
          f"({sum(r['decompile'] in ('refused', 'lines-only') for r in done)} lines only)")
    # decompile_status.csv: this run's rows replace those of the same sets.
    status = [r for r in dw._csv(dw.DECOMPILE_STATUS) if r["set"] not in names] + done
    with open(dw.DECOMPILE_STATUS, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(done[0]))
        w.writeheader()
        w.writerows(status)
    print(f"wrote {os.path.relpath(dw.DECOMPILE_STATUS)} ({len(status)} rows)")
    write_index(status)


def write_index(status):
    """research/maps/INDEX.md from decompile_status rows and the metrics CSVs."""
    index = ["# Official maps, top down", "",
             "Written by `scripts/metrics/map_svgs.py` (see `levels/preview.py` for the legend). "
             "Size is the bounding box in map units; critical path is the progression model's "
             "(scripts/metrics/progression_metrics.py). *Lines only*: the decompiler refused the map, "
             "or its module didn't compile, so its SVG has no sector shading.", ""]
    rows = measurements()
    for name in SET_NAMES:
        maps = [r for r in status if r["set"] == name]
        if not maps:
            continue
        index += [f"## {name}", ""]
        for r in sorted(maps, key=lambda r: r["svg"]):
            note = " *(lines only)*" if r["decompile"] in ("refused", "lines-only") else ""
            index.append(f"- [{r['wad']} {r['slot']}]({r['svg']}){note}: "
                         f"{summary(rows.get((r['set'], r['wad'], r['slot'])))}")
        index.append("")
    with open(os.path.join(OUT, "INDEX.md"), "w") as f:
        f.write("\n".join(index))


if __name__ == "__main__":
    main(sys.argv[1:])
