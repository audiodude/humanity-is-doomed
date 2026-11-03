"""Slot defaults: what the engine does by map slot unless the map's UMAPINFO
entry says otherwise (DOOM II's text screens, secret-exit routing, boss deaths,
skies)."""
import pytest
from conftest import module, needs_iwad

from levels import checks
from levels.doom2 import CYBER, FATSO, PLAYER1, S1_DOOR_OPEN, W1_EXIT, W1_FLOOR_LOWEST, W1_SECRET_EXIT
from levels.mapgen import compile_level
from levels.model import Place, Sector, Special, Thing, load, rect

EXIT = {((256, 400), (320, 400)): Special(W1_EXIT)}
SECRET_EXIT = {((256, 400), (320, 400)): Special(W1_SECRET_EXIT)}


def room(slot, *things, pad_tag=0, free_lines=EXIT, scratch=False, **attrs):
    """A room with the player and an exit line, loaded at `slot`; a raised pad
    in it tagged `pad_tag` (0: no tag)."""
    sectors = [Sector("room", [rect(0, 0, 512, 512), rect(128, 128, 256, 256)], 0, 128, "FLOOR4_8", "CEIL3_5",
                      160, "STARTAN3"),
               Sector("pad", [rect(128, 128, 256, 256)], 32, 128, "FLOOR4_8", "CEIL3_5", 160, "STARTAN3",
                      tag=pad_tag)]
    mod = module(SECTORS=sectors, FREE_LINES=free_lines, THINGS=[Thing(PLAYER1, 64, 64), *things], **attrs)
    return load(mod, Place("test.wad", slot, scratch=scratch))


def warnings(level):
    return checks.findings(level, compile_level(level)).warnings


def warned(level, text):
    return any(text in w for w in warnings(level))


@pytest.mark.parametrize("slot, text", [
    ("MAP05", False), ("MAP06", True), ("MAP07", False), ("MAP11", True), ("MAP20", True), ("MAP30", True),
])
def test_doom2_shows_its_own_text_after_map06_11_20_30(slot, text):
    assert warned(room(slot), "DOOM II shows its own text screen after") == text


@pytest.mark.parametrize("umapinfo, default_text, quoted_clear", [
    ({"levelname": "Pump Hall"}, True, False),
    ('levelname = "Pump Hall"\nintertext = clear', False, False),
    ({"intertext": "The pumps fall silent."}, False, False),
    ({"intertext": "clear"}, False, True),   # the dict form writes it quoted: ports show the word
])
def test_intertext_replaces_the_default_text(umapinfo, default_text, quoted_clear):
    found = warnings(room("MAP06", UMAPINFO=umapinfo))
    assert any("DOOM II shows its own text screen" in w for w in found) == default_text
    assert any('intertext = "clear" is written quoted' in w for w in found) == quoted_clear


def test_a_scratch_build_isnt_in_its_slot_so_only_its_umapinfo_is_checked():
    found = warnings(room("MAP06", Thing(FATSO, 400, 400, skills="h"), pad_tag=666, free_lines=SECRET_EXIT,
                          scratch=True, UMAPINFO={"intertext": "clear"}))
    assert [w for w in found if "is written quoted" not in w] == []
    assert any("is written quoted" in w for w in found)


def test_secret_exit_off_map15_and_map31_has_nowhere_to_go_without_umapinfo():
    assert warned(room("MAP05", free_lines=SECRET_EXIT), "the one on MAP05 reloads MAP05")
    assert not warned(room("MAP15", free_lines=SECRET_EXIT), "DOOM II only has secret exits")


def test_map15_secret_exit_needs_umapinfo_nextsecret_and_intertextsecret():
    bare = room("MAP15", free_lines=SECRET_EXIT, UMAPINFO={"levelname": "Pump Hall"})
    assert warned(bare, "goes where the normal exit does")
    assert warned(bare, "after MAP15's secret exit")
    full = room("MAP15", free_lines=SECRET_EXIT, UMAPINFO={"levelname": "Pump Hall", "nextsecret": "MAP31",
                                                          "intertextsecret": "You found the vault."})
    assert not warned(full, "goes where the normal exit does")
    assert not warned(full, "secret exit (")


@pytest.mark.parametrize("slot, message", [
    ("E1M3", None),
    ("E1M6", "from E1M6 that replays E1M4-E1M6"),
    ("E1M2", "from E1M2 that skips E1M3"),
])
def test_doom_secret_exits_all_lead_to_m9_which_returns_after_ids_slot(slot, message):
    found = warnings(room(slot, free_lines=SECRET_EXIT))
    assert [w for w in found if "every secret exit in DOOM" in w] == (
        [f"without UMAPINFO, every secret exit in DOOM leads to E1M9, which returns to E1M4: {message}"]
        if message else [])


def test_bossaction_drops_map07s_rule_the_tagged_pad_relied_on():
    mancubus = Thing(FATSO, 400, 400)
    assert not any("boss rule" in w for w in warnings(room("MAP07", mancubus, pad_tag=666)))
    assert warned(room("MAP07", mancubus, pad_tag=666, UMAPINFO="bossaction = clear"),
                  "killing the last mancubus no longer lowers the sectors tagged 666 (pad)")


def test_map07s_rule_also_moves_a_tag_a_line_uses():
    lines = {**EXIT, ((64, 300), (96, 300)): Special(W1_FLOOR_LOWEST, 666)}
    assert warned(room("MAP07", Thing(FATSO, 400, 400), pad_tag=666, free_lines=lines),
                  "a line moves tag 666 too")


def test_a_map_built_for_map07s_rule_moved_to_another_slot():
    assert warned(room("MAP03", Thing(FATSO, 400, 400), pad_tag=666),
                  "nothing on MAP03 moves the sectors tagged 666 (pad): MAP07's boss rule lowers them when the "
                  "last mancubus dies")
    assert not warned(room("MAP07", Thing(FATSO, 400, 400), pad_tag=666), "nothing on")
    assert not warned(room("MAP03", pad_tag=666), "nothing on")   # no mancubus: not a MAP07 map


def test_boss_death_needs_its_monster_on_every_skill():
    assert warned(room("MAP07", Thing(FATSO, 400, 400, skills="mh"), pad_tag=666),
                  "only the last mancubus's death lowers the sectors tagged 666 (pad), and there's no "
                  "mancubus on easy")
    boss = f"bossaction = Cyberdemon, {S1_DOOR_OPEN}, 7"
    assert warned(room("MAP09", Thing(CYBER, 400, 400, skills="h"), pad_tag=7, UMAPINFO=boss),
                  "and there's no cyberdemon on easy or medium")
    assert not warned(room("MAP09", Thing(CYBER, 400, 400), pad_tag=7, UMAPINFO=boss), "there's no")


def test_e2m8_ends_when_the_cyberdemon_dies_even_with_an_exit_line():
    assert warned(room("E2M8", Thing(CYBER, 400, 400)), "ends the level when the last cyberdemon dies")
    assert not warned(room("E2M8", Thing(CYBER, 400, 400), free_lines={}), "ends the level when")


@pytest.mark.parametrize("slot, umapinfo, sky", [
    ("MAP11", {}, "SKY1"), ("MAP12", {}, "SKY2"), ("MAP20", {}, "SKY2"), ("MAP21", {}, "SKY3"),
    ("E3M1", {}, "SKY3"), ("MAP12", {"skytexture": "sky3"}, "SKY3"), ("MAP01", 'skytexture = "SKY2"', "SKY2"),
])
def test_sky_is_the_slots_unless_umapinfo_sets_one(slot, umapinfo, sky):
    assert checks.slot_sky(room(slot, UMAPINFO=umapinfo))[0] == sky


@needs_iwad("doom2")
def test_unknown_umapinfo_skytexture_is_a_playability_finding():
    level = room("MAP01", UMAPINFO={"skytexture": "SKYNOPE"})
    assert "UMAPINFO skytexture SKYNOPE: unknown texture" in checks.findings(level, compile_level(level)).playability
