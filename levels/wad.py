"""WAD file reading and writing, map lump packing, and IWAD texture sizes."""
import os
import re
import struct

IWAD = os.environ.get("DOOM2_WAD", os.path.expanduser("~/.local/share/dsda-doom/doom2.wad"))


def name8(s):
    return s.encode().ljust(8, b"\0")


def write_wad(path, lumps):
    body = b""
    dirs = []
    for n, data in lumps:
        dirs.append(struct.pack("<ii8s", 12 + len(body), len(data), name8(n)))
        body += data
    with open(path, "wb") as f:
        f.write(b"PWAD" + struct.pack("<ii", len(lumps), 12 + len(body)) + body + b"".join(dirs))


def read_wad(path):
    with open(path, "rb") as f:
        d = f.read()
    n, off = struct.unpack("<ii", d[4:12])
    out = []
    for i in range(n):
        o, s, nm = struct.unpack("<ii8s", d[off + 16 * i: off + 16 * i + 16])
        out.append((nm.split(b"\0")[0].decode(), d[o:o + s]))
    return out


def map_lumps(level, lines, sides_per_line):
    vlist = sorted({l.v1 for l in lines} | {l.v2 for l in lines})
    vidx = {v: i for i, v in enumerate(vlist)}
    sidx = {s: i for i, s in enumerate(level.sectors.values())}
    things = b"".join(struct.pack("<hhhhh", t.x, t.y, t.angle, t.type, t.flags) for t in level.things)
    linedefs, sidedefs, n = b"", b"", 0
    for l, sides in zip(lines, sides_per_line):
        s1, s2 = n, (n + 1 if len(sides) == 2 else -1)
        linedefs += struct.pack("<hhhhhhh", vidx[l.v1], vidx[l.v2], l.flags, l.action, l.tag, s1, s2)
        for sd in sides:
            sidedefs += struct.pack("<hh8s8s8sh", sd.x_offset, sd.y_offset, name8(sd.upper), name8(sd.lower),
                                    name8(sd.mid), sidx[sd.sector])
        n += len(sides)
    vertexes = b"".join(struct.pack("<hh", x, y) for x, y in vlist)
    sectors = b"".join(struct.pack("<hh8s8shhh", s.floor, s.ceil, name8(s.ftex), name8(s.ctex),
                                   s.light, s.special, s.tag) for s in level.sectors.values())
    return [(level.map, b""), ("THINGS", things), ("LINEDEFS", linedefs), ("SIDEDEFS", sidedefs),
            ("VERTEXES", vertexes), ("SEGS", b""), ("SSECTORS", b""), ("NODES", b""),
            ("SECTORS", sectors), ("REJECT", b""), ("BLOCKMAP", b"")]


def umapinfo_lump(level):
    body = "".join(f'  {k} = "{v}"\n' for k, v in level.umapinfo.items())
    return f"MAP {level.map}\n{{\n{body}}}\n".encode()


MAP_MARKER = re.compile(r"MAP\d\d|E\dM\d")
MAP_LUMPS = {"THINGS", "LINEDEFS", "SIDEDEFS", "VERTEXES", "SEGS", "SSECTORS", "NODES", "SECTORS",
             "REJECT", "BLOCKMAP", "BEHAVIOR"}
UMAPINFO_ENTRY = re.compile(r"MAP\s+(\w+)\s*\{[^}]*\}", re.IGNORECASE)


def replace_map(lumps, slot, map_lumps, umapinfo=None):
    """`lumps` (a WAD's lumps, possibly empty) with map `slot` replaced by or
    added as `map_lumps`, maps kept in slot order, and slot's UMAPINFO entry
    replaced by `umapinfo` (bytes, or None to drop it). Other maps, their
    UMAPINFO entries and other lumps are kept."""
    maps, other, info, i = {}, [], b"", 0
    while i < len(lumps):
        name = lumps[i][0]
        if MAP_MARKER.fullmatch(name):
            j = i + 1
            while j < len(lumps) and lumps[j][0] in MAP_LUMPS:
                j += 1
            maps[name], i = lumps[i:j], j
            continue
        if name == "UMAPINFO":
            info = lumps[i][1]
        else:
            other.append(lumps[i])
        i += 1
    maps[slot] = map_lumps
    entries = {m.group(1).upper(): m.group(0) for m in UMAPINFO_ENTRY.finditer(info.decode())}
    entries.pop(slot, None)
    if umapinfo:
        entries[slot] = umapinfo.decode().strip()
    out = [lump for name in sorted(maps) for lump in maps[name]] + other
    if entries:
        out.append(("UMAPINFO", "".join(entries[k] + "\n" for k in sorted(entries)).encode()))
    return out


def iwad_textures(path=IWAD):
    """({texture: (width, height)}, {flat names}) from an IWAD, or None if
    the file is missing."""
    if not os.path.exists(path):
        return None
    lumps = read_wad(path)
    textures = {}
    for name, data in lumps:
        if name not in ("TEXTURE1", "TEXTURE2"):
            continue
        for i in range(struct.unpack_from("<i", data)[0]):
            o = struct.unpack_from("<i", data, 4 + 4 * i)[0]
            tex = data[o:o + 8].split(b"\0")[0].decode().upper()
            textures[tex] = struct.unpack_from("<hh", data, o + 12)
    names = [n for n, _ in lumps]
    flats = set(names[names.index("F_START") + 1:names.index("F_END")])
    return textures, flats - {"F1_START", "F1_END", "F2_START", "F2_END", "F3_START", "F3_END"}
