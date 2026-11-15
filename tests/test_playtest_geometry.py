"""The playtest runner's map raster (scripts/tools/playtest.py Geometry)."""
import os
import struct
import sys

from conftest import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts", "tools"))
import playtest  # noqa: E402


def lumps(lines):
    """A 256-unit square room, sector 0, from (v1, v2, front sidedef, back sidedef) lines."""
    verts = [(0, 0), (0, 256), (256, 256), (256, 0)]
    return {
        "VERTEXES": b"".join(struct.pack("<hh", *v) for v in verts),
        "SIDEDEFS": struct.pack("<hh8s8s8sh", 0, 0, b"-", b"-", b"STARTAN3", 0),
        "SECTORS": struct.pack("<hh8s8shhh", 0, 128, b"FLOOR4_8", b"CEIL3_5", 160, 0, 0),
        "LINEDEFS": b"".join(struct.pack("<hhhhhhh", a, b, 1, 0, 0, f, bk) for a, b, f, bk in lines),
        "THINGS": b"",
    }


ROOM = [(0, 1, 0, -1), (1, 2, 0, -1), (2, 3, 0, -1), (3, 0, 0, -1)]


def test_duplicated_line_keeps_the_room():
    # SLIGE writes some lines twice; here the west wall again the other way
    # round, one-sided, so a scanline hits the room and the void at the same x.
    geo = playtest.Geometry(lumps(ROOM + [(1, 0, 0, -1)]))
    assert geo.sector_at((128, 128)) == 0
    inside = geo.cell_sector[(128 - geo.y0) // playtest.GRID][(128 - geo.x0) // playtest.GRID]
    assert inside == 0
