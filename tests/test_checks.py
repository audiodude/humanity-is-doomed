"""Checks on the reach model: monsters behind doors, KNOWN_ISSUES and IMPORTED."""
import pytest
from conftest import module, needs_iwad

from levels import build, checks
from levels.doom2 import BLUEKEY, DAMAGE_5, DEMON, DR_BLUE, DR_DOOR, PLAYER1, S1_DOOR_OPEN, S1_EXIT, W1_EXIT
from levels.mapgen import compile_level
from levels.model import Line, LevelError, Sector, Special, Thing, door, load, rect

pytestmark = needs_iwad("doom2")
SEALED = "DEMON at 592,256 in closet can't be reached and can't come to the player"


def closet_map(action, *things, **attrs):
    """A room, and east of it a closet with a demon behind a door."""
    return module(
        SECTORS=[Sector("room", [rect(0, 0, 512, 512)], 0, 128, "FLOOR4_8", "CEIL3_5", 160, "STARTAN3"),
                 door("d", rect(512, 192, 528, 320), action=action),
                 Sector("closet", [rect(528, 192, 656, 320)], 0, 128, "FLOOR4_8", "CEIL3_5", 160, "STARTAN3")],
        FREE_LINES={((256, 400), (320, 400)): Special(W1_EXIT)},
        THINGS=[Thing(PLAYER1, 64, 64), Thing(DEMON, 592, 256), *things], **attrs)


def findings(mod):
    level = load(mod)
    return checks.findings(level, compile_level(level))


def test_monster_behind_a_locked_door_with_no_key_is_sealed():
    assert SEALED in findings(closet_map(DR_BLUE)).playability


def test_key_in_reach_opens_the_door():
    assert findings(closet_map(DR_BLUE, Thing(BLUEKEY, 256, 256))).playability == []


def test_monster_opens_a_plain_door_the_player_cant():
    # Only the closet side of the door has the use action: the player can't
    # open it, but the demon can come out.
    mod = closet_map(DR_DOOR, OVERRIDES={((512, 320), (512, 192)): Line(action=0)})
    assert findings(mod).playability == []
    mod = closet_map(DR_BLUE, OVERRIDES={((512, 320), (512, 192)): Line(action=0)})
    assert SEALED in findings(mod).playability


def test_known_issue_doesnt_fail_the_build_but_a_new_one_does(tmp_path, capsys):
    out = str(tmp_path / "t.wad")
    with pytest.raises(LevelError, match="can't come to the player"):
        build(closet_map(DR_BLUE), check_only=True, out=out)
    build(closet_map(DR_BLUE, KNOWN_ISSUES=[SEALED]), check_only=True, out=out)
    build(closet_map(DR_BLUE, Thing(BLUEKEY, 256, 256), KNOWN_ISSUES=[SEALED]), check_only=True, out=out)
    assert "fixed: " + SEALED in capsys.readouterr().out


def boss_gate_map(umapinfo):
    """The exit switch is on the back wall of a 16-deep shutter that only tag 1
    opens: within use range of the room, but a use stops at the closed shutter."""
    return module(
        SECTORS=[Sector("room", [rect(0, 0, 512, 512)], 0, 128, "FLOOR4_8", "CEIL3_5", 160, "STARTAN3"),
                 door("d", rect(512, 192, 528, 320), tag=1)],
        SPECIAL_WALLS={((528, 192), (528, 320)): Special(S1_EXIT)},
        THINGS=[Thing(PLAYER1, 64, 64), Thing(DEMON, 256, 256)], UMAPINFO=umapinfo)


@pytest.mark.parametrize("umapinfo, reached", [
    ('levelname = "x"', False),                                              # the shutter never opens
    (f"bossaction = Demon, {S1_DOOR_OPEN}, 1", True),
    (f"bossaction = demon, {S1_DOOR_OPEN}, 1\nbossaction = clear", False),   # clear drops what came before
    (f"bossaction = Cyberdemon, {S1_DOOR_OPEN}, 1", False),                  # no Cyberdemon to kill
])
def test_umapinfo_bossaction_opens_the_way_to_the_exit(umapinfo, reached):
    assert ("the exit can't be reached" not in findings(boss_gate_map(umapinfo)).playability) == reached


def test_unreadable_bossaction_is_a_finding():
    assert "UMAPINFO bossaction = Imp, 103, 1: unknown monster Imp" in findings(
        boss_gate_map("bossaction = Imp, 103, 1")).playability


def pit_map(**attrs):
    """A nukage pool that isn't sunk below the room around it: a style finding."""
    return module(
        SECTORS=[Sector("room", [rect(0, 0, 512, 512), rect(128, 128, 256, 256)], 0, 128, "FLOOR4_8", "CEIL3_5",
                        160, "STARTAN3"),
                 Sector("pool", [rect(128, 128, 256, 256)], 0, 128, "NUKAGE1", "CEIL3_5", 160, "STARTAN3",
                        special=DAMAGE_5)],
        FREE_LINES={((256, 400), (320, 400)): Special(W1_EXIT)}, THINGS=[Thing(PLAYER1, 64, 64)], **attrs)


def test_style_findings_fail_our_maps_but_only_warn_on_imported_ones(tmp_path, capsys):
    out = str(tmp_path / "t.wad")
    assert any("isn't below its neighbour" in s for s in findings(pit_map()).style)
    with pytest.raises(LevelError, match="isn't below its neighbour"):
        build(pit_map(), check_only=True, out=out)
    build(pit_map(IMPORTED=True), check_only=True, out=out)
    assert "warning: damaging floor pool" in capsys.readouterr().out
