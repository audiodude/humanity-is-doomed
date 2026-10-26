"""Contact sheets of an IWAD's wall textures and flats, to look at before choosing.

    uv run --with pillow scripts/tools/texture_sheets.py [--iwad PATH] [--out DIR]

Wall textures are drawn at full size and grouped into families by the first
four letters of their name (STARTAN*/STARG* are one family, BROWN*/BROWNGRN
another), each family starting a new row under its heading. Labels in yellow
are border textures, the ones the rule-2 metric counts as trim between
materials. Switch textures are drawn once, in their off state (SW1*). Flats
follow on their own sheets. Writes walls-NN.png, flats-NN.png and index.txt
(which sheet holds each family) to --out, by default
/tmp/texture-sheets/<IWAD name>.
"""
import argparse
import os
import struct
import sys

from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "metrics"))
from levels.measure import texture_family  # noqa: E402  the families the rule-2 seam list also uses
from levels.wad import IWAD, read_wad  # noqa: E402  DOOM2_WAD from .env or the environment
from space_metrics import BORDER_EXT  # noqa: E402

SHEET_W, SHEET_H, PAD, LABEL, HEAD = 1280, 1400, 8, 12, 16
TRANSPARENT = (255, 0, 255)


def lumps_by_name(path):
    lumps = read_wad(path)
    names = [n.upper() for n, _ in lumps]
    flats = []
    for start, end in (("F_START", "F_END"), ("FF_START", "FF_END")):
        if start in names and end in names:
            flats += [(n, d) for n, d in lumps[names.index(start) + 1:names.index(end)] if len(d) == 4096]
    return {n.upper(): d for n, d in lumps}, flats


def picture(data, canvas, w, h, ox, oy):
    """Draw a DOOM picture-format patch into canvas (a list of palette indices
    or None, w*h) with its top-left at (ox, oy)."""
    pw = struct.unpack_from("<h", data)[0]
    for c in range(pw):
        x = ox + c
        if not 0 <= x < w:
            continue
        p = struct.unpack_from("<i", data, 8 + 4 * c)[0]
        while data[p] != 255:
            top, n = data[p], data[p + 1]
            for i in range(n):
                y = oy + top + i
                if 0 <= y < h:
                    canvas[y * w + x] = data[p + 3 + i]
            p += n + 4


def textures(by_name):
    """[(name, Image)] of every wall texture, composited from its patches."""
    pnames = by_name["PNAMES"]
    patches = [pnames[4 + 8 * i:12 + 8 * i].split(b"\0")[0].decode().upper()
               for i in range(struct.unpack_from("<i", pnames)[0])]
    pal = by_name["PLAYPAL"][:768]
    out = []
    for data in (by_name[n] for n in ("TEXTURE1", "TEXTURE2") if n in by_name):
        for i in range(struct.unpack_from("<i", data)[0]):
            o = struct.unpack_from("<i", data, 4 + 4 * i)[0]
            name = data[o:o + 8].split(b"\0")[0].decode().upper()
            w, h = struct.unpack_from("<hh", data, o + 12)
            canvas = [None] * (w * h)
            for k in range(struct.unpack_from("<h", data, o + 20)[0]):
                x, y, patch = struct.unpack_from("<hhh", data, o + 22 + 10 * k)
                if patch < len(patches) and patches[patch] in by_name:
                    picture(by_name[patches[patch]], canvas, w, h, x, y)
            out.append((name, image(canvas, w, h, pal)))
    return out


def image(indices, w, h, pal):
    img = Image.new("RGB", (w, h))
    img.putdata([TRANSPARENT if i is None else tuple(pal[3 * i:3 * i + 3]) for i in indices])
    return img


def sheets(kind, groups, out):
    """Lay groups [(heading, [(name, Image)])] onto SHEET_W-wide sheets, each
    group starting a new row; returns {heading: sheet file}."""
    where, pages, bottoms = {}, [], []
    page, draw, x, y, row_h = None, None, 0, 0, 0

    def new_page():
        nonlocal page, draw, y
        if pages:
            bottoms.append(y)
        page = Image.new("RGB", (SHEET_W, SHEET_H), (24, 24, 24))
        draw, y = ImageDraw.Draw(page), PAD
        pages.append(page)

    def save_name(i):
        return f"{kind}-{i + 1:02d}.png"

    new_page()
    for heading, items in groups:
        first_h = max(img.height for _, img in items[:SHEET_W // 72]) + LABEL
        if y + HEAD + first_h > SHEET_H:
            new_page()
        draw.text((PAD, y), heading, fill=(160, 200, 255))
        y += HEAD
        x, row_h = PAD, 0
        where[heading] = save_name(len(pages) - 1)
        for name, img in items:
            if x + img.width > SHEET_W - PAD:
                x, y, row_h = PAD, y + row_h + PAD, 0
            if y + img.height + LABEL > SHEET_H:
                new_page()
                x, row_h = PAD, 0
                draw.text((PAD, y), heading + " (cont.)", fill=(160, 200, 255))
                y += HEAD
            page.paste(img, (x, y))
            trim = BORDER_EXT.match(name)
            draw.text((x, y + img.height + 1), f"{name} {img.width}x{img.height}",
                      fill=(255, 220, 0) if trim else (230, 230, 230))
            x += max(img.width, 6 * (len(name) + 8)) + PAD
            row_h = max(row_h, img.height + LABEL)
        y += row_h + PAD
    bottoms.append(y)
    for i, (p, bottom) in enumerate(zip(pages, bottoms)):
        p.crop((0, 0, SHEET_W, min(SHEET_H, bottom))).save(os.path.join(out, save_name(i)))
    return where


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--iwad", default=IWAD, help="IWAD to read (default DOOM2_WAD from .env)")
    ap.add_argument("--out", help="output directory (default /tmp/texture-sheets/<IWAD name>)")
    a = ap.parse_args()
    if not a.iwad or not os.path.exists(a.iwad):
        sys.exit(f"no IWAD at {a.iwad!r}; set DOOM2_WAD in .env or pass --iwad")
    out = a.out or os.path.join("/tmp/texture-sheets", os.path.splitext(os.path.basename(a.iwad))[0].lower())
    os.makedirs(out, exist_ok=True)
    by_name, flat_lumps = lumps_by_name(a.iwad)
    pal = by_name["PLAYPAL"][:768]

    groups = {}
    for name, img in sorted(textures(by_name), key=lambda t: t[0]):
        if not name.startswith("SW2") and name not in ("AASHITTY", "AASTINKY"):
            groups.setdefault(texture_family(name), []).append((name, img))
    walls = sheets("walls", sorted(groups.items()), out)

    fgroups = {}
    for name, data in sorted(flat_lumps, key=lambda t: t[0]):
        fgroups.setdefault(texture_family(name.upper()), []).append((name.upper(), image(list(data), 64, 64, pal)))
    flats = sheets("flats", sorted(fgroups.items()), out)

    with open(os.path.join(out, "index.txt"), "w") as f:
        for kind, where, grp in (("walls", walls, groups), ("flats", flats, fgroups)):
            for heading, sheet in where.items():
                f.write(f"{sheet}  {heading}: {' '.join(n for n, _ in grp[heading])}\n")
    print(f"{len(set(walls.values()))} wall and {len(set(flats.values()))} flat sheets in {out}")


if __name__ == "__main__":
    main()
