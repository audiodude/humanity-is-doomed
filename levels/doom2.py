"""DOOM and DOOM II definitions: every vanilla thing type (with the games it
exists in, and size and health for monsters), pickups, every line action
1-141 (trigger, kind, key) and the sector specials. THING_NAMES,
ACTION_NAMES and SECTOR_NAMES map numbers back to the constant names. Level
modules usually `from .doom2 import *`; scripts/metrics/doomwad.py imports
these too."""
from dataclasses import dataclass

# ------------------------------------------------------------ thing types ---
PLAYER1, PLAYER2, PLAYER3, PLAYER4, DM_START = 1, 2, 3, 4, 11
ZOMBIE, SARGE, IMP, DEMON, SPECTRE, CACO, KNIGHT, CHAINGUY, REVENANT, FATSO, BARON, LOSTSOUL = \
    3004, 9, 3001, 3002, 58, 3005, 69, 65, 66, 67, 3003, 3006
ARCHVILE, ARACHNO, PAIN, SS, CYBER, SPIDER, KEEN, BOSSBRAIN, BOSSSPIT, BOSSTARGET = \
    64, 68, 71, 84, 16, 7, 72, 88, 89, 87
CHAINSAW, SHOTGUN, SSG, CHAINGUN, LAUNCHER, PLASMA, BFG = 2005, 2001, 82, 2002, 2003, 2004, 2006
CLIP, AMMOBOX, SHELLS, SHELLBOX, ROCKET, ROCKETBOX, CELL, CELLPACK = 2007, 2048, 2008, 2049, 2010, 2046, 2047, 17
STIM, MEDI, HBONUS, ABONUS, GREENARMOR, BLUEARMOR, SOUL, MEGA, BACKPACK = \
    2011, 2012, 2014, 2015, 2018, 2019, 2013, 83, 8
INVULN, BERSERK, INVIS, RADSUIT, COMPMAP, VISOR = 2022, 2023, 2024, 2025, 2026, 2045
BLUEKEY, YELLOWKEY, REDKEY, BLUESKULL, YELLOWSKULL, REDSKULL = 5, 6, 13, 40, 39, 38
BARREL, BURNING_BARREL, TELEPORT_DEST = 2035, 70, 14
# Light sources and columns. TORCH: tall blue firestick.
COLUMN, TECHLAMP, SHORT_TECHLAMP, CANDLE, CANDELABRA = 2028, 85, 86, 34, 35
TORCH, GREENTORCH, REDTORCH, SHORT_BLUE_TORCH, SHORT_GREEN_TORCH, SHORT_RED_TORCH = 44, 45, 46, 55, 56, 57
TALL_GREEN_COLUMN, SHORT_GREEN_COLUMN, TALL_RED_COLUMN, SHORT_RED_COLUMN, HEART_COLUMN, SKULL_COLUMN = \
    30, 31, 32, 33, 36, 37
TECHPILLAR, EVIL_EYE, FLOATING_SKULL, BURNT_TREE, STALAGMITE, BIG_TREE = 48, 41, 42, 43, 47, 54
# Gore. Hanging bodies block movement; the _NB ones don't.
GIBS, GIBS2, DEAD_PLAYER, DEAD_ZOMBIE, DEAD_SARGE, DEAD_IMP, DEAD_DEMON, DEAD_CACO, DEAD_LOSTSOUL = \
    10, 12, 15, 18, 19, 20, 21, 22, 23
GUTS, IMPALED, IMPALED_TWITCH, SKULL_POLE, SKULL_KEBAB, SKULL_PILE = 24, 25, 26, 27, 28, 29
HANGING_TWITCH, HANGING_ARMS, HANGING_ONELEG, HANGING_LEGS, HANGING_LEG = 49, 50, 51, 52, 53
HANGING_ARMS_NB, HANGING_LEGS_NB, HANGING_ONELEG_NB, HANGING_LEG_NB, HANGING_TWITCH_NB = 59, 60, 61, 62, 63
HANGING_GUTS, HANGING_GUTS_NOBRAIN, HANGING_TORSO_DOWN, HANGING_TORSO_OPEN, HANGING_TORSO_UP, \
    HANGING_TORSO_NOBRAIN = 73, 74, 75, 76, 77, 78
BLOOD_POOL, BLOOD_POOL2, BRAINS = 79, 80, 81

# Every int constant above, by number.
THING_NAMES = {v: k for k, v in dict(globals()).items() if k.isupper() and type(v) is int}
# DOOM II added types 64-89; DOOM (Ultimate Doom) has the rest, as does DOOM II.
THING_GAMES = {t: ("doom2",) if 64 <= t <= 89 else ("doom", "doom2") for t in THING_NAMES}

PLAYERS = {PLAYER1, PLAYER2, PLAYER3, PLAYER4}
KEY_OF = {BLUEKEY: "blue", BLUESKULL: "blue", YELLOWKEY: "yellow", YELLOWSKULL: "yellow",
          REDKEY: "red", REDSKULL: "red"}


@dataclass(frozen=True)
class Actor:
    radius: int
    height: int
    health: int = 0
    flies: bool = False


# Things checked for clearance; everything here except players counts as a
# monster (as in info.c). Keen hangs from the ceiling and the boss brain sits
# in a wall; neither moves.
ACTORS = {
    **{p: Actor(16, 56, 100) for p in PLAYERS},
    ZOMBIE: Actor(20, 56, 20), SARGE: Actor(20, 56, 30), IMP: Actor(20, 56, 60),
    DEMON: Actor(30, 56, 150), SPECTRE: Actor(30, 56, 150), CACO: Actor(31, 56, 400, flies=True),
    KNIGHT: Actor(24, 64, 500), CHAINGUY: Actor(20, 56, 70), REVENANT: Actor(20, 56, 300),
    FATSO: Actor(48, 64, 600), BARON: Actor(24, 64, 1000), LOSTSOUL: Actor(16, 56, 100, flies=True),
    ARCHVILE: Actor(20, 56, 700), ARACHNO: Actor(64, 64, 500), PAIN: Actor(31, 56, 400, flies=True),
    SS: Actor(20, 56, 50), CYBER: Actor(40, 110, 4000), SPIDER: Actor(128, 100, 3000),
    KEEN: Actor(16, 72, 100), BOSSBRAIN: Actor(16, 16, 250),
}
MONSTERS = set(ACTORS) - PLAYERS
MAX_STEP = 24   # highest step up an actor can walk
HITSCANNERS = {ZOMBIE, SARGE, CHAINGUY, SS, SPIDER}
# Research names (scripts/metrics CSVs) of monsters, weapons and power-ups.
LABELS = {
    ZOMBIE: "zombieman", SARGE: "shotgunguy", CHAINGUY: "chaingunner", SS: "wolfss", IMP: "imp",
    DEMON: "demon", SPECTRE: "spectre", LOSTSOUL: "lostsoul", CACO: "cacodemon", KNIGHT: "hellknight",
    BARON: "baron", ARACHNO: "arachnotron", PAIN: "painelemental", REVENANT: "revenant",
    FATSO: "mancubus", ARCHVILE: "archvile", SPIDER: "spidermastermind", CYBER: "cyberdemon",
    KEEN: "keen", BOSSBRAIN: "bossbrain",
    CHAINSAW: "chainsaw", SHOTGUN: "shotgun", SSG: "supershotgun", CHAINGUN: "chaingun",
    LAUNCHER: "rocketlauncher", PLASMA: "plasmarifle", BFG: "bfg9000",
    INVULN: "invulnerability", BERSERK: "berserk", INVIS: "invisibility", RADSUIT: "radsuit",
    COMPMAP: "computermap", VISOR: "lightamp", SOUL: "soulsphere", MEGA: "megasphere", BACKPACK: "backpack",
}
WEAPONS = (CHAINSAW, SHOTGUN, SSG, CHAINGUN, LAUNCHER, PLASMA, BFG)
POWERUPS = (INVULN, BERSERK, INVIS, RADSUIT, COMPMAP, VISOR, SOUL, MEGA, BACKPACK)

# ---------------------------------------------------------------- pickups ---
START_AMMO = {"bullets": 50}
# Ammo a pickup gives (single player, HNTR..UV; ITYTD and NM double it).
AMMO_PICKUPS = {
    CLIP: {"bullets": 10}, AMMOBOX: {"bullets": 50}, SHELLS: {"shells": 4}, SHELLBOX: {"shells": 20},
    ROCKET: {"rockets": 1}, ROCKETBOX: {"rockets": 5}, SHOTGUN: {"shells": 8}, SSG: {"shells": 8},
    CHAINGUN: {"bullets": 20}, LAUNCHER: {"rockets": 2}, PLASMA: {"cells": 40}, CELL: {"cells": 20},
    CELLPACK: {"cells": 100}, BFG: {"cells": 40},
    BACKPACK: {"bullets": 10, "shells": 4, "rockets": 1, "cells": 20},
}
DROPS = {ZOMBIE: {"bullets": 5}, SS: {"bullets": 5}, SARGE: {"shells": 4}, CHAINGUY: {"bullets": 10}}
# Rough average damage per unit of ammo on a hit (shells: shotgun, 7 pellets).
DAMAGE_PER_AMMO = {"bullets": 10, "shells": 70, "rockets": 150, "cells": 22}
HEALTH_PICKUPS = {STIM: 10, MEDI: 25, HBONUS: 1, SOUL: 100, MEGA: 200}
ARMOR_PICKUPS = {GREENARMOR: 100, BLUEARMOR: 200, ABONUS: 1, MEGA: 200}

# ----------------------------------------------------------- line actions ---
_before_actions = set(globals())
# Trigger prefix: D manual (use; acts on the line's back sector), S switch,
# W walk over, G shoot; 1 once, R repeatable. The rest act on tagged sectors.
# DOOR = open, wait, close; DOOR_OPEN = open, stay; DOOR_CLOSE_30 = close, reopen
# after 30 s. FLOOR_LOWEST/HIGHEST: lower to the lowest/highest neighbouring
# floor (HIGHEST_FAST: 8 above it); FLOOR_NEXT: raise to the next higher
# neighbouring floor; FLOOR_RAISE: raise to the lowest neighbouring ceiling
# (FLOOR_CRUSH: 8 below it, crushing); RAISE_CHANGE, RAISE_24_CHANGE,
# RAISE_32_CHANGE: raise (to the next floor, by 24, by 32) taking the
# trigger's floor texture and clearing the special.
DR_DOOR, DR_BLUE, DR_YELLOW, DR_RED, DR_DOOR_FAST = 1, 26, 27, 28, 117
D1_DOOR, D1_BLUE, D1_RED, D1_YELLOW, D1_DOOR_FAST = 31, 32, 33, 34, 118
W1_DOOR_OPEN, S1_DOOR_OPEN, SR_DOOR_OPEN, WR_DOOR_OPEN, GR_DOOR_OPEN = 2, 103, 61, 86, 46
W1_DOOR, S1_DOOR, SR_DOOR, WR_DOOR = 4, 29, 63, 90
W1_DOOR_CLOSE, S1_DOOR_CLOSE, SR_DOOR_CLOSE, WR_DOOR_CLOSE = 3, 50, 42, 75
W1_DOOR_CLOSE_30, WR_DOOR_CLOSE_30 = 16, 76
W1_DOOR_FAST, S1_DOOR_FAST, SR_DOOR_FAST, WR_DOOR_FAST = 108, 111, 114, 105
W1_DOOR_OPEN_FAST, S1_DOOR_OPEN_FAST, SR_DOOR_OPEN_FAST, WR_DOOR_OPEN_FAST = 109, 112, 115, 106
W1_DOOR_CLOSE_FAST, S1_DOOR_CLOSE_FAST, SR_DOOR_CLOSE_FAST, WR_DOOR_CLOSE_FAST = 110, 113, 116, 107
SR_DOOR_BLUE_FAST, SR_DOOR_RED_FAST, SR_DOOR_YELLOW_FAST = 99, 134, 136   # open, stay
S1_DOOR_BLUE_FAST, S1_DOOR_RED_FAST, S1_DOOR_YELLOW_FAST = 133, 135, 137
S1_FLOOR_LOWEST, W1_FLOOR_LOWEST, SR_FLOOR_LOWEST, WR_FLOOR_LOWEST = 23, 38, 60, 82
W1_FLOOR_LOWEST_CHANGE, WR_FLOOR_LOWEST_CHANGE = 37, 84
S1_FLOOR_HIGHEST, W1_FLOOR_HIGHEST, SR_FLOOR_HIGHEST, WR_FLOOR_HIGHEST = 102, 19, 45, 83
S1_FLOOR_HIGHEST_FAST, W1_FLOOR_HIGHEST_FAST, SR_FLOOR_HIGHEST_FAST, WR_FLOOR_HIGHEST_FAST = 71, 36, 70, 98
S1_FLOOR_RAISE, W1_FLOOR_RAISE, SR_FLOOR_RAISE, WR_FLOOR_RAISE, G1_FLOOR_RAISE = 101, 5, 64, 91, 24
S1_FLOOR_CRUSH, W1_FLOOR_CRUSH, SR_FLOOR_CRUSH, WR_FLOOR_CRUSH = 55, 56, 65, 94
S1_FLOOR_NEXT, W1_FLOOR_NEXT, SR_FLOOR_NEXT, WR_FLOOR_NEXT = 18, 119, 69, 128
S1_FLOOR_NEXT_FAST, W1_FLOOR_NEXT_FAST, SR_FLOOR_NEXT_FAST, WR_FLOOR_NEXT_FAST = 131, 130, 132, 129
W1_FLOOR_24, WR_FLOOR_24, S1_FLOOR_512 = 58, 92, 140
W1_FLOOR_TEXTURE, WR_FLOOR_TEXTURE = 30, 96   # raise by the shortest lower texture
S1_RAISE_CHANGE, W1_RAISE_CHANGE, SR_RAISE_CHANGE, WR_RAISE_CHANGE, G1_RAISE_CHANGE = 20, 22, 68, 95, 47
S1_RAISE_24_CHANGE, W1_RAISE_24_CHANGE, SR_RAISE_24_CHANGE, WR_RAISE_24_CHANGE = 15, 59, 66, 93
S1_RAISE_32_CHANGE, SR_RAISE_32_CHANGE = 14, 67
S1_LIFT, W1_LIFT, SR_LIFT, WR_LIFT = 21, 10, 62, 88   # lower, wait, raise
S1_LIFT_FAST, W1_LIFT_FAST, SR_LIFT_FAST, WR_LIFT_FAST = 122, 121, 123, 120
W1_PERPETUAL, WR_PERPETUAL, W1_PLAT_STOP, WR_PLAT_STOP = 53, 87, 54, 89
S1_STAIRS_8, W1_STAIRS_8, S1_STAIRS_16_FAST, W1_STAIRS_16_FAST = 7, 8, 127, 100
S1_DONUT = 9
W1_CEILING_HIGHEST = 40                                       # raise to the highest neighbouring ceiling
S1_CEILING_FLOOR, SR_CEILING_FLOOR = 41, 43                   # lower ceiling to floor
W1_CEILING_LOWER, WR_CEILING_LOWER = 44, 72                   # lower ceiling to floor + 8
S1_CRUSHER, W1_CRUSHER, WR_CRUSHER, W1_CRUSHER_FAST, WR_CRUSHER_FAST, W1_CRUSHER_SILENT = 49, 25, 73, 6, 77, 141
W1_CRUSHER_STOP, WR_CRUSHER_STOP = 57, 74
W1_LIGHT_35, WR_LIGHT_35, SR_LIGHT_35 = 35, 79, 139            # tagged sectors' light drops to 35
W1_LIGHT_255, WR_LIGHT_255, SR_LIGHT_255 = 13, 81, 138         # tagged sectors light up to 255
W1_LIGHT_BRIGHTEST, WR_LIGHT_BRIGHTEST, W1_LIGHT_DARKEST = 12, 80, 104   # to the neighbours' light
W1_LIGHT_BLINK = 17
W1_TELEPORT, WR_TELEPORT = 39, 97   # only from the line's front side
W1_MONSTER_TELEPORT, WR_MONSTER_TELEPORT = 125, 126
S1_EXIT, W1_EXIT, S1_SECRET_EXIT, W1_SECRET_EXIT = 11, 52, 51, 124
SCROLL_LEFT = 48   # passive: the wall's texture scrolls

# Every int constant in this section, by number.
ACTION_NAMES = {v: k for k, v in dict(globals()).items()
                if k not in _before_actions and k.isupper() and type(v) is int}

MONSTER_DOORS = {DR_DOOR}   # the only manual door a monster opens (never an ML_SECRET line)
# The builder's guesses (model.floor_movers): what moves a tagged floor.
FLOOR_LOWERERS = {S1_FLOOR_LOWEST, W1_FLOOR_LOWEST, SR_FLOOR_LOWEST, WR_FLOOR_LOWEST}
FLOOR_RAISERS = {S1_RAISE_CHANGE, W1_RAISE_CHANGE, SR_RAISE_CHANGE, WR_RAISE_CHANGE}


@dataclass(frozen=True)
class LineSpecial:
    trigger: str  # D, S1, SR, W1, WR, G1, GR, or "" for passive
    kind: str
    key: str | None = None

    @property
    def tagged(self):
        """Acts on the sectors tagged like the line (manual doors act on the back sector)."""
        return self.trigger not in ("D", "")


# action: trigger kind [key]. Kinds group behaviour.
_LS = """
1 D door; 2 W1 door; 3 W1 door_close; 4 W1 door; 5 W1 floor_raise; 6 W1 crusher; 7 S1 stairs;
8 W1 stairs; 9 S1 donut; 10 W1 lift; 11 S1 exit; 12 W1 light; 13 W1 light; 14 S1 floor_raise;
15 S1 floor_raise; 16 W1 door_close; 17 W1 light; 18 S1 floor_raise; 19 W1 floor_lower;
20 S1 floor_raise; 21 S1 lift; 22 W1 floor_raise; 23 S1 floor_lower; 24 G1 floor_raise;
25 W1 crusher; 26 D door blue; 27 D door yellow; 28 D door red; 29 S1 door; 30 W1 floor_raise;
31 D door; 32 D door blue; 33 D door red; 34 D door yellow; 35 W1 light; 36 W1 floor_lower;
37 W1 floor_lower; 38 W1 floor_lower; 39 W1 teleport; 40 W1 ceiling_raise; 41 S1 ceiling_lower;
42 SR door_close; 43 SR ceiling_lower; 44 W1 ceiling_lower; 45 SR floor_lower; 46 GR door;
47 G1 floor_raise; 48 _ scroll; 49 S1 crusher; 50 S1 door_close; 51 S1 secret_exit; 52 W1 exit;
53 W1 platform; 54 W1 platform_stop; 55 S1 floor_raise; 56 W1 floor_raise; 57 W1 crusher_stop;
58 W1 floor_raise; 59 W1 floor_raise; 60 SR floor_lower; 61 SR door; 62 SR lift; 63 SR door;
64 SR floor_raise; 65 SR floor_raise; 66 SR floor_raise; 67 SR floor_raise; 68 SR floor_raise;
69 SR floor_raise; 70 SR floor_lower; 71 S1 floor_lower; 72 WR ceiling_lower; 73 WR crusher;
74 WR crusher_stop; 75 WR door_close; 76 WR door_close; 77 WR crusher; 79 WR light; 80 WR light;
81 WR light; 82 WR floor_lower; 83 WR floor_lower; 84 WR floor_lower; 86 WR door; 87 WR platform;
88 WR lift; 89 WR platform_stop; 90 WR door; 91 WR floor_raise; 92 WR floor_raise;
93 WR floor_raise; 94 WR floor_raise; 95 WR floor_raise; 96 WR floor_raise; 97 WR teleport;
98 WR floor_lower; 99 SR door blue; 100 W1 stairs; 101 S1 floor_raise; 102 S1 floor_lower;
103 S1 door; 104 W1 light; 105 WR door; 106 WR door; 107 WR door_close; 108 W1 door; 109 W1 door;
110 W1 door_close; 111 S1 door; 112 S1 door; 113 S1 door_close; 114 SR door; 115 SR door;
116 SR door_close; 117 D door; 118 D door; 119 W1 floor_raise; 120 WR lift; 121 W1 lift;
122 S1 lift; 123 SR lift; 124 W1 secret_exit; 125 W1 monster_teleport; 126 WR monster_teleport;
127 S1 stairs; 128 WR floor_raise; 129 WR floor_raise; 130 W1 floor_raise; 131 S1 floor_raise;
132 SR floor_raise; 133 S1 door blue; 134 SR door red; 135 S1 door red; 136 SR door yellow;
137 S1 door yellow; 138 SR light; 139 SR light; 140 S1 floor_raise; 141 W1 crusher
"""
LINE_SPECIALS = {}
for _item in _LS.split(";"):
    _p = _item.split()
    LINE_SPECIALS[int(_p[0])] = LineSpecial("" if _p[1] == "_" else _p[1], _p[2], _p[3] if len(_p) > 3 else None)

# -------------------------------------------------------- sector specials ---
_before_sectors = set(globals())
LIGHT_BLINK_RANDOM, LIGHT_BLINK_FAST, LIGHT_BLINK_SLOW, LIGHT_GLOW, LIGHT_FLICKER = 1, 2, 3, 8, 17
LIGHT_BLINK_SLOW_SYNC, LIGHT_BLINK_FAST_SYNC = 12, 13
DAMAGE_20_BLINK, DAMAGE_10, DAMAGE_5, DAMAGE_20, DAMAGE_20_EXIT = 4, 5, 7, 16, 11   # EXIT: ends the level below 11% health
SECRET_AREA, DOOR_CLOSE_30S, DOOR_OPEN_5MIN = 9, 10, 14
# Every int constant above in this section, by number.
SECTOR_NAMES = {v: k for k, v in dict(globals()).items()
                if k not in _before_sectors and k.isupper() and type(v) is int}
SECTOR_DAMAGE = {DAMAGE_20_BLINK: 20, DAMAGE_10: 10, DAMAGE_5: 5, DAMAGE_20_EXIT: 20, DAMAGE_20: 20}   # per 32 tics
DAMAGING = set(SECTOR_DAMAGE)
LIGHT_SPECIALS = {LIGHT_BLINK_RANDOM, LIGHT_BLINK_FAST, LIGHT_BLINK_SLOW, DAMAGE_20_BLINK, LIGHT_GLOW,
                  LIGHT_BLINK_SLOW_SYNC, LIGHT_BLINK_FAST_SYNC, LIGHT_FLICKER}

# --------------------------------------------------------------- textures ---
# Pictures (switches, door faces, signs) that must be shown whole, never
# tiled or cropped. Door tracks (DOORTRAK, DOORBLU, ...) tile and aren't here.
DECAL_PREFIXES = ("SW1", "SW2", "BIGDOOR", "EXITDOOR", "EXITSIGN", "DOOR1", "DOOR3", "SPCDOOR")


def is_decal(texture: str) -> bool:
    return texture.startswith(DECAL_PREFIXES)
