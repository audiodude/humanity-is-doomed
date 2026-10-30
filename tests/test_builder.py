"""The level format: sectors with several outer loops, holes that are partly
walls, OVERRIDES and thing flags."""
import pytest
from conftest import module

from levels.doom2 import PLAYER1
from levels.mapgen import compile_level
from levels.model import ML_BLOCKING, ML_TWOSIDED, LevelError, Line, Sector, Side, Thing, load, rect
from levels.wadmap import parse


def room(name, *loops, floor=0, wall="STARTAN3"):
    return Sector(name, list(loops), floor, 128, "FLOOR4_8", "CEIL3_5", 160, wall)


def built(**attrs):
    attrs.setdefault("THINGS", [Thing(PLAYER1, 64, 64)])
    level = load(module(**attrs))
    compiled = compile_level(level)
    return level, parse(level.game, level.map, dict(compiled.lumps[1:]))


def line_between(m, p, q):
    return next(ln for ln in m.lines if {m.verts[ln.v1], m.verts[ln.v2]} == {p, q})


def two_rooms():
    return [room("a", rect(0, 0, 256, 256)), room("b", rect(256, 0, 512, 256), wall="BROWN1")]


@pytest.mark.parametrize("key, front, back", [
    (((256, 256), (256, 0)), 0, 1),   # going south, the right is the west room a
    (((256, 0), (256, 256)), 1, 0),
])
def test_override_sets_facing_and_sides_by_key_direction(key, front, back):
    _, m = built(SECTORS=two_rooms(), OVERRIDES={key: Line(action=1, front=Side(upper="STARTAN2", x=5),
                                                             back=Side(lower="BROWN96"))})
    ln = line_between(m, *key)
    assert (m.verts[ln.v1], m.verts[ln.v2]) == key
    f, b = m.sides[ln.front], m.sides[ln.back]
    assert (f.sector, b.sector) == (front, back)
    assert (f.upper, f.x_offset, b.lower, ln.special) == ("STARTAN2", 5, "BROWN96", 1)


def test_override_keeps_unset_fields_and_replaces_flags_whole():
    key = ((256, 0), (256, 256))
    _, plain = built(SECTORS=two_rooms())
    _, m = built(SECTORS=two_rooms(), OVERRIDES={key: Line(flags=ML_TWOSIDED | ML_BLOCKING)})
    a, b = line_between(plain, *key), line_between(m, *key)
    assert b.flags == ML_TWOSIDED | ML_BLOCKING
    sides = sorted(((s.sector, s.upper, s.lower, s.mid, s.x_offset) for s in
                    (m.sides[b.front], m.sides[b.back])))
    assert sides == sorted((s.sector, s.upper, s.lower, s.mid, s.x_offset) for s in
                           (plain.sides[a.front], plain.sides[a.back]))


def test_override_picture_starts_at_offset_zero_unless_x_given():
    key = ((256, 0), (0, 0))   # a's south wall: its place on a's outline gives it a non-zero offset
    off = {}
    for name, side in (("wall", Side(mid="COMPSTA2")), ("picture", Side(mid="SW1EXIT")),
                       ("given", Side(mid="SW1EXIT", x=8))):
        _, m = built(SECTORS=two_rooms(), OVERRIDES={key: Line(front=side)})
        off[name] = m.sides[line_between(m, *key).front].x_offset
    assert off["wall"] != 0 and off["picture"] == 0 and off["given"] == 8


def test_override_that_matches_no_line_is_an_error():
    with pytest.raises(LevelError, match="matches no line"):
        built(SECTORS=two_rooms(), OVERRIDES={((0, 0), (999, 999)): Line(tag=1)})


def test_back_on_a_one_sided_line_is_an_error():
    with pytest.raises(LevelError, match="sets back= on a one-sided line"):
        built(SECTORS=two_rooms(), OVERRIDES={((256, 0), (0, 0)): Line(back=Side(mid="MIDGRATE"))})


def test_override_against_a_one_sided_wall_is_an_error():
    # The south wall of a runs east to west (a on its right); flipping it would face the void.
    _, m = built(SECTORS=two_rooms(), OVERRIDES={((256, 0), (0, 0)): Line(front=Side(mid="COMPSTA2"))})
    ln = line_between(m, (0, 0), (256, 0))
    assert (m.verts[ln.v1], m.verts[ln.v2]) == ((256, 0), (0, 0)) and m.sides[ln.front].mid == "COMPSTA2"
    with pytest.raises(LevelError, match=r"runs against one-sided wall \(256, 0\)-\(0, 0\); key it"):
        built(SECTORS=two_rooms(), OVERRIDES={((0, 0), (256, 0)): Line(front=Side(mid="COMPSTA2"))})


def test_sector_with_two_outer_loops_is_one_sector():
    sectors = [room("a", rect(0, 0, 128, 128), rect(256, 0, 384, 128)), room("b", rect(128, 0, 256, 128))]
    level, m = built(SECTORS=sectors)
    assert len(m.sectors) == 2
    assert m.sector_of_point(64, 64) == m.sector_of_point(320, 64) == 0
    assert m.sector_of_point(192, 64) == 1
    assert level.sectors["a"].contains((320, 64)) and not level.sectors["a"].contains((192, 64))


def test_hole_edges_without_a_sector_become_walls():
    # b fills only the south half of a's hole; the rest of the hole is void.
    sectors = [room("a", rect(0, 0, 512, 512), rect(128, 128, 384, 384)), room("b", rect(128, 128, 384, 256))]
    _, m = built(SECTORS=sectors)
    north = line_between(m, (128, 384), (384, 384))
    assert north.back < 0 and m.sides[north.front].sector == 0
    middle = line_between(m, (128, 256), (384, 256))
    assert middle.back < 0 and m.sides[middle.front].sector == 1
    assert line_between(m, (128, 128), (384, 128)).back >= 0


def test_hole_with_no_sector_in_it_is_still_an_error():
    with pytest.raises(LevelError, match="has no sector in it"):
        built(SECTORS=[room("a", rect(0, 0, 512, 512), rect(128, 128, 384, 384))])


def test_thing_skills_multiplayer_and_extra_flags():
    _, m = built(SECTORS=two_rooms(), THINGS=[Thing(PLAYER1, 64, 64), Thing(PLAYER1, 128, 64, 0, "emhn", 32),
                                               Thing(PLAYER1, 192, 64, 0, "ea")])
    assert [t.flags for t in m.things] == [7, 7 | 16 | 32, 1 | 8]


def test_island_inside_a_pillar_of_the_same_sector():
    a = room("a", rect(0, 0, 1024, 1024), rect(384, 384, 640, 640))
    a.pillars = [rect(256, 256, 768, 768)]
    _, m = built(SECTORS=[a])
    assert a.contains((128, 128)) and a.contains((512, 512)) and not a.contains((300, 300))
    assert m.sector_of_point(512, 512) == 0 and m.sector_of_point(300, 300) is None
    assert all(ln.back < 0 for ln in m.lines)
