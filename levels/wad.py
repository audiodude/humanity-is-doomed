"""WAD file reading and writing, map lump packing, and IWAD texture sizes."""
import os
import re
import struct

ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")


def read_env(path=ENV_FILE):
    """KEY=VALUE settings from the repo's .env (see .env.example), with
    variables already set in the environment taking precedence. Blank lines
    and # comments are skipped; quotes around a value are dropped."""
    env = {}
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                key, sep, value = line.strip().partition("=")
                if sep and not key.startswith("#"):
                    env[key.strip()] = value.strip().strip("\"'")
    return {**env, **os.environ}


# IWAD paths by game, None if unset: DOOM_WAD (Ultimate Doom) and DOOM2_WAD.
IWAD_VARS = {"doom": "DOOM_WAD", "doom2": "DOOM2_WAD"}
_env = read_env()
IWADS = {game: os.path.expanduser(_env[var]) if _env.get(var) else None for game, var in IWAD_VARS.items()}
IWAD = IWADS["doom2"]


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


def umapinfo_body(info: dict[str, str]) -> str:
    """The UMAPINFO entry body a {key: value} dict is written as."""
    return "\n" + "".join(f'  {k} = "{v}"\n' for k, v in info.items())


def umapinfo_lump(level):
    """level's UMAPINFO entry: a dict's values are written quoted, a string
    is the body between the braces, written as it is."""
    info = level.umapinfo
    body = info if isinstance(info, str) else umapinfo_body(info)
    return f"MAP {level.map}\n{{{body}}}\n".encode()


MAP_MARKER = re.compile(r"MAP\d\d|E\dM\d")
# Lumps after a map marker that belong to the map (Doom, Hexen and UDMF formats).
MAP_LUMPS = {"THINGS", "LINEDEFS", "SIDEDEFS", "VERTEXES", "SEGS", "SSECTORS", "NODES", "SECTORS",
             "REJECT", "BLOCKMAP", "BEHAVIOR", "TEXTMAP", "ZNODES", "DIALOGUE", "ENDMAP"}
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


FLAT_MARKER = re.compile(r"F[F1-3]?_(START|END)")


def iwad_textures(path, resources=()):
    """({texture: (width, height)}, {flat names}, {medusa textures}) from an
    IWAD and the PWADs `resources` loaded after it, or None if the path is
    unset or missing. As with vanilla -file, a later TEXTURE1, TEXTURE2,
    PNAMES or patch lump replaces an earlier one; flats (between F_START and
    F_END, or FF_START and FF_END) add up. A medusa texture has a column
    where patches overlap; vanilla can't draw those on two-sided lines."""
    if not path or not os.path.exists(path):
        return None
    by_name, flats = {}, set()
    for wad in (path, *resources):
        lumps = read_wad(wad)
        by_name.update((name.upper(), data) for name, data in lumps)
        names = [n.upper() for n, _ in lumps]
        for start, end in (("F_START", "F_END"), ("FF_START", "FF_END")):
            if start in names and end in names:
                flats |= {n for n in names[names.index(start) + 1:names.index(end)] if not FLAT_MARKER.fullmatch(n)}
    pnames = by_name["PNAMES"]
    patches = [pnames[4 + 8 * i:12 + 8 * i].split(b"\0")[0].decode().upper()
               for i in range(struct.unpack_from("<i", pnames)[0])]
    patch_width = [struct.unpack_from("<h", by_name[p])[0] if p in by_name else 0 for p in patches]
    textures, medusa = {}, set()
    for data in (by_name[n] for n in ("TEXTURE1", "TEXTURE2") if n in by_name):
        for i in range(struct.unpack_from("<i", data)[0]):
            o = struct.unpack_from("<i", data, 4 + 4 * i)[0]
            tex = data[o:o + 8].split(b"\0")[0].decode().upper()
            w, h = textures[tex] = struct.unpack_from("<hh", data, o + 12)
            cover = [0] * w
            for k in range(struct.unpack_from("<h", data, o + 20)[0]):
                x, _, patch = struct.unpack_from("<hhh", data, o + 22 + 10 * k)
                pw = patch_width[patch] if patch < len(patch_width) else 0   # not in PNAMES: draws nothing
                for c in range(max(0, x), min(w, x + pw)):
                    cover[c] += 1
            if max(cover) > 1:
                medusa.add(tex)
    return textures, flats, medusa
