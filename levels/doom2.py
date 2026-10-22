"""DOOM II definitions for level modules: thing types, actor stats, pickups,
line and sector specials. Level modules usually `from .doom2 import *`."""
from dataclasses import dataclass

# ------------------------------------------------------------ thing types ---
PLAYER1, PLAYER2, PLAYER3, PLAYER4 = 1, 2, 3, 4
ZOMBIE, SARGE, IMP, DEMON, SPECTRE, CACO, KNIGHT, CHAINGUY, REVENANT, FATSO, BARON = \
    3004, 9, 3001, 3002, 58, 3005, 69, 65, 66, 67, 3003
SHOTGUN, SSG, CHAINGUN, LAUNCHER, PLASMA = 2001, 82, 2002, 2003, 2004
CLIP, AMMOBOX, SHELLS, SHELLBOX, ROCKET, ROCKETBOX, CELL = 2007, 2048, 2008, 2049, 2010, 2046, 2047
STIM, MEDI, HBONUS, ABONUS, GREENARMOR, BLUEARMOR, SOUL, BACKPACK = \
    2011, 2012, 2014, 2015, 2018, 2019, 2013, 8
BLUEKEY, YELLOWKEY, REDKEY, BLUESKULL, YELLOWSKULL, REDSKULL = 5, 6, 13, 40, 39, 38
BARREL, TECHLAMP, COLUMN, TORCH, REDTORCH = 2035, 85, 2028, 44, 46   # TORCH: tall blue firestick
RADSUIT, BERSERK = 2025, 2023
TELEPORT_DEST = 14

PLAYERS = {PLAYER1, PLAYER2, PLAYER3, PLAYER4}
KEY_OF = {BLUEKEY: "blue", BLUESKULL: "blue", YELLOWKEY: "yellow", YELLOWSKULL: "yellow",
          REDKEY: "red", REDSKULL: "red"}


@dataclass(frozen=True)
class Actor:
    radius: int
    height: int
    health: int = 0
    flies: bool = False


# Things checked for clearance; everything here except players counts as a monster.
ACTORS = {
    **{p: Actor(16, 56, 100) for p in PLAYERS},
    ZOMBIE: Actor(20, 56, 20), SARGE: Actor(20, 56, 30), IMP: Actor(20, 56, 60),
    DEMON: Actor(30, 56, 150), SPECTRE: Actor(30, 56, 150), CACO: Actor(31, 56, 400, flies=True),
    KNIGHT: Actor(24, 64, 500), CHAINGUY: Actor(20, 56, 70), REVENANT: Actor(20, 56, 300),
    FATSO: Actor(48, 64, 600), BARON: Actor(24, 64, 1000),
}

# ---------------------------------------------------------------- pickups ---
START_AMMO = {"bullets": 50}
AMMO_PICKUPS = {
    CLIP: {"bullets": 10}, AMMOBOX: {"bullets": 50}, SHELLS: {"shells": 4}, SHELLBOX: {"shells": 20},
    ROCKET: {"rockets": 1}, ROCKETBOX: {"rockets": 5}, SHOTGUN: {"shells": 8}, SSG: {"shells": 8},
    CHAINGUN: {"bullets": 20}, LAUNCHER: {"rockets": 2}, PLASMA: {"cells": 40}, CELL: {"cells": 20},
    BACKPACK: {"bullets": 10, "shells": 4, "rockets": 1, "cells": 20},
}
DROPS = {ZOMBIE: {"bullets": 5}, SARGE: {"shells": 4}, CHAINGUY: {"bullets": 10}}
# Rough average damage per unit of ammo on a hit (shells: shotgun, 7 pellets).
DAMAGE_PER_AMMO = {"bullets": 10, "shells": 70, "rockets": 150, "cells": 22}
HEALTH_PICKUPS = {STIM: 10, MEDI: 25, HBONUS: 1, SOUL: 100}
ARMOR_PICKUPS = {GREENARMOR: 100, BLUEARMOR: 200, ABONUS: 1}

# ----------------------------------------------------------- line actions ---
DR_DOOR, DR_BLUE, DR_YELLOW, DR_RED = 1, 26, 27, 28          # use: open, wait, close
D1_DOOR, D1_BLUE, D1_RED, D1_YELLOW = 31, 32, 33, 34          # use once: open, stay
W1_DOOR_OPEN, S1_DOOR_OPEN, SR_DOOR_OPEN, WR_DOOR_OPEN = 2, 103, 61, 86   # tagged
S1_FLOOR_LOWEST, W1_FLOOR_LOWEST, SR_FLOOR_LOWEST, WR_FLOOR_LOWEST = 23, 38, 60, 82
SR_LIFT, WR_LIFT = 62, 88
S1_EXIT = 11
W1_LIGHT_35 = 35   # tagged sectors' light drops to 35 (a blackout)
W1_LIGHT_255 = 13  # tagged sectors light up to 255
WR_TELEPORT = 97   # only from the line's front side

# Doors opened by using the line next to them -> key needed (None = no key).
USE_DOORS = {DR_DOOR: None, DR_BLUE: "blue", DR_YELLOW: "yellow", DR_RED: "red",
             D1_DOOR: None, D1_BLUE: "blue", D1_RED: "red", D1_YELLOW: "yellow"}
TAG_DOOR_OPENERS = {W1_DOOR_OPEN, S1_DOOR_OPEN, SR_DOOR_OPEN, WR_DOOR_OPEN}
FLOOR_LOWERERS = {S1_FLOOR_LOWEST, W1_FLOOR_LOWEST, SR_FLOOR_LOWEST, WR_FLOOR_LOWEST}

# -------------------------------------------------------- sector specials ---
LIGHT_BLINK_RANDOM, LIGHT_GLOW, DAMAGE_5, SECRET_AREA, LIGHT_FLICKER = 1, 8, 7, 9, 17

# --------------------------------------------------------------- textures ---
# Pictures (switches, door faces, signs) that must be shown whole, never
# tiled or cropped. Door tracks (DOORTRAK, DOORBLU, ...) tile and aren't here.
DECAL_PREFIXES = ("SW1", "SW2", "BIGDOOR", "EXITDOOR", "EXITSIGN", "DOOR1", "DOOR3", "SPCDOOR")


def is_decal(texture: str) -> bool:
    return texture.startswith(DECAL_PREFIXES)
