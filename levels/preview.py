"""Top-down SVG preview of a level: sectors shaded by floor height, walls,
line specials, and things."""
import math
from html import escape

from .doom2 import (ACTORS, AMMO_PICKUPS, ARMOR_PICKUPS, HEALTH_PICKUPS, KEY_OF, PLAYERS,
                    SECRET_AREA)
from .model import DOOR, LIFT, label_point

KEY_COLORS = {"blue": "#2255ff", "yellow": "#e0c000", "red": "#e02020"}



def write_svg(level, lines, path, scale=0.4, pad=96):
    pts = [p for s in level.sectors.values() for loop in s.outer_loops() for p in loop]
    minx, maxx = min(x for x, _ in pts) - pad, max(x for x, _ in pts) + pad
    miny, maxy = min(y for _, y in pts) - pad, max(y for _, y in pts) + pad

    def xy(x, y):
        return (x - minx) * scale, (maxy - y) * scale

    def pt(p):
        return "{:.1f},{:.1f}".format(*xy(*p))

    floors = [s.floor for s in level.sectors.values()]
    lo, span = min(floors), (max(floors) - min(floors)) or 1
    w, h = (maxx - minx) * scale, (maxy - miny) * scale + 40
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
           f'font-family="sans-serif">',
           '<rect width="100%" height="100%" fill="#fbfbf7"/>']
    for s in (s for s in level.sectors.values() if s.loops):
        if s.kind == DOOR:
            fill = "#a0703c"
        elif s.kind == LIFT:
            fill = "#e8c547"
        elif s.special == SECRET_AREA:
            fill = "#c9a0f0"
        elif s.ftex.startswith(("NUKAGE", "SLIME", "LAVA", "BLOOD", "FWATER")):
            fill = "#7ccf4a"
        else:
            v = int(150 + 90 * (s.floor - lo) / span)
            fill = f"rgb({v},{v},{v})"
        d = " ".join("M" + " L".join(pt(p) for p in loop) + " Z" for loop in s.loops + s.pillars)
        tip = f"{s.name}: floor {s.floor} ceil {s.ceil} {s.ftex}/{s.ctex} light {s.light}"
        if s.tag:
            tip += f" tag {s.tag}"
        out.append(f'<path d="{d}" fill="{fill}" fill-rule="evenodd"><title>{escape(tip)}</title></path>')
    for l in lines:
        (x1, y1), (x2, y2) = xy(*l.v1), xy(*l.v2)
        if l.action:
            style = 'stroke="#d0201a" stroke-width="2.5"'
        elif l.back and l.texture:
            style = 'stroke="#111" stroke-width="1.6" stroke-dasharray="4 2"'
        elif l.back is None:
            style = 'stroke="#111" stroke-width="1.6"'
        else:
            style = 'stroke="#777" stroke-width="0.6"'
        tip = " ".join(([f"action {l.action} tag {l.tag}"] if l.action else [])
                       + ([l.texture] if l.back and l.texture else []))
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" {style}>'
                   f'<title>{tip}</title></line>' if tip else
                   f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" {style}/>')
    for s in level.sectors.values():
        for loop in s.outer_loops():
            xs, ys = [x for x, _ in loop], [y for _, y in loop]
            if s.kind == DOOR or min(max(xs) - min(xs), max(ys) - min(ys)) < 48:   # too small to label
                continue
            if (p := label_point(s, loop)) is None:
                continue
            x, y = xy(*p)
            text = f"{s.name} {s.floor}" + (f" t{s.tag}" if s.tag else "")
            out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="9" text-anchor="middle" fill="#333">'
                       f'{escape(text)}</text>')
    for t in level.things:
        x, y = xy(t.x, t.y)
        actor = ACTORS.get(t.type)
        if t.type in PLAYERS:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{16 * scale + 1:.1f}" fill="#1a9e3a"/>')
        elif actor:
            dash = ' stroke-dasharray="2,1.5"' if "e" not in t.skills else ""
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{actor.radius * scale:.1f}" '
                       f'fill="#e03030" fill-opacity="{0.75 if "e" in t.skills else 0.25}" '
                       f'stroke="#900" stroke-width="0.8"{dash}><title>monster {t.type} '
                       f'skills {t.skills}</title></circle>')
        elif t.type in KEY_OF:
            out.append(f'<rect x="{x - 4:.1f}" y="{y - 4:.1f}" width="8" height="8" '
                       f'fill="{KEY_COLORS[KEY_OF[t.type]]}" stroke="#000"/>')
        elif t.type in AMMO_PICKUPS or t.type in HEALTH_PICKUPS or t.type in ARMOR_PICKUPS:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="#1f6fd0"/>')
        else:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.8" fill="#888"/>')
    legend = (f"{level.name} ({level.map}): grey = floor height (lighter is higher), brown = door, "
              "yellow = lift, purple = secret, green = liquid, red line = special, dashed = bars/fence; "
              "red circles = monsters (faint/dashed = not on easy), blue dots = pickups, green = start")
    out.append(f'<text x="8" y="{h - 14:.0f}" font-size="11" fill="#222">{escape(legend)}</text>')
    out.append("</svg>")
    with open(path, "w") as f:
        f.write("\n".join(out))
