"""playtest.py --play: you play a map, and get the explorer's report on your play.

    uv run --with vizdoom scripts/tools/playtest.py WAD... MAP --play [--monsters] [--skill N]
    uv run --with vizdoom scripts/tools/playtest.py LEVEL --play
    uv run --with vizdoom scripts/tools/playtest.py --play --recording DIR    # the report again

The map opens in a window at normal speed, with modern-port controls (as in
DOOM + DOOM II and dsda-doom): WASD to move and strafe, the mouse to turn
(it doesn't move you forward or back), E or space to use, mouse 1 or Ctrl to
fire, 1-7 or the wheel for weapons, always run (hold Shift to walk). Two
more keys:

    L   "I'm lost": marks the moment, as often as you like
    K   stop: ends the play and records it (so does reaching the exit)

Closing the window instead may lose the recording. By default the monsters
are removed and god mode is on, as the explorer plays, so the play measures
finding the way; --monsters keeps them (and drops god mode).

Each play gets a folder in ~/.local/share/playtest/plays/ with the demo
(play.lmp), a copy of every PWAD it loaded (a demo only plays back right on
the exact WAD it was made with, so rebuilding or regenerating the map later
doesn't matter), meta.json and report.txt.

The report comes from playing the demo back headless, tic by tic, through
the explorer's own bookkeeping, so it reads like an --explore report and the
two can be laid side by side: what you did and when, how far you walked
(against the critical path, for a level module or an id map), how much of
the map you saw (rays across your view), and the longest stretches with no
progress, with where you spent them. Progress for a person is what it is
for the explorer: a key picked up, a switch's or shot line's sectors
starting to move for the first time ("switch": a tag any switch or shot line
acts on; lifts don't count), a locked door opening, and the exit. Sectors
only walk-over lines set off are noted ("walk"), as are teleports, but don't
count. Then each L press:
when, where, and which stretch it fell in. The L presses come from the demo
itself, so they line up with the play to the tic.
"""
import json
import os
import shutil
import time
from types import SimpleNamespace

import playtest as pt
from explore import Explorer, Teleported, level_info, line_textures
from levels.doom2 import BOOM_SPECIALS as SPECIALS

PLAYS = os.path.expanduser("~/.local/share/playtest/plays")


def run(args, vzd):
    if args.recording:
        return report(vzd, args.recording, iwad=args.iwad)
    m = pt.find_map(args.wad, args.map.upper())
    if not m:
        print(f"{args.map} not found as a Doom-format map in {args.wad}")
        return 2
    stem = os.path.splitext(os.path.basename(args.wad[-1]))[0]
    folder = os.path.join(PLAYS, f"{time.strftime('%Y%m%d-%H%M%S')}-{stem}-{args.map.upper()}")
    os.makedirs(folder)
    wads = []
    for k, w in enumerate(args.wad):
        name = os.path.basename(w)
        if name in wads:
            name = f"{k}-{name}"
        shutil.copy2(w, os.path.join(folder, name))
        wads.append(name)
    meta = dict(map=args.map.upper(), skill=args.skill, seed=args.seed, monsters=args.monsters,
                iwad=os.path.abspath(args.iwad), wads=wads, sources=[os.path.abspath(w) for w in args.wad],
                module=args.module, wad_hash=pt.wad_hash(args.wad), played=time.strftime("%Y-%m-%d %H:%M:%S"))
    with open(os.path.join(folder, "meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    meta["ended"] = play(args, vzd, pt.Geometry(m), os.path.join(folder, "play.lmp"))
    with open(os.path.join(folder, "meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    if not os.path.exists(os.path.join(folder, "play.lmp")):
        print(f"no recording was written: the game window closed before the play ended ({folder})")
        return 2
    print(f"recorded to {folder}")
    return report(vzd, folder)


def play(args, vzd, geo, demo):
    """The live play, in a window: record it to `demo` until the exit, K, or
    death. Returns how it ended: "stopped", "died", "exited" or "closed"."""
    r = pt.Run(args, vzd, geo)
    g = r.game
    # Modern-port controls, as in DOOM + DOOM II (2024) and dsda-doom: WASD
    # to move and strafe, the mouse to turn only (no forward/back on the
    # mouse, no free look), E or space to use, mouse 1 or Ctrl to fire,
    # the wheel to change weapons, always run (Shift walks).
    for c in ("bind w +forward", "bind s +back", "bind a +moveleft", "bind d +moveright",
              "bind e +use", "bind space +use", "bind mouse1 +attack", "bind ctrl +attack",
              "bind mwheelup weapprev", "bind mwheeldown weapnext", "bind shift +speed",
              "m_forward 0", "freelook 0", "lookstrafe 0", "cl_run 1",
              "bind l +reload", "bind k +zoom"):
        g.send_game_command(c)
    part = pt.short_demo_path()   # ViZDoom hangs recording to a long path
    g.new_episode(part)
    if not args.monsters:
        g.send_game_command("god")
    lost, stop = r.buttons.index("RELOAD"), r.buttons.index("ZOOM")
    print(f"playing {args.map.upper()}{'' if args.monsters else ' (no monsters, god mode)'}: "
          "L = I'm lost, K = stop", flush=True)
    marks, held, ended = 0, False, "closed"
    try:
        while not g.is_episode_finished():
            g.advance_action()
            a = g.get_last_action()
            if a[stop]:
                print("stopped (K)")
                ended = "stopped"
                break
            if a[lost] and not held:
                marks += 1
                print(f"  marked lost ({marks})", flush=True)
            held = bool(a[lost])
        else:
            ended = "died" if g.is_player_dead() else "exited"
            print(ended)
    except (vzd.ViZDoomUnexpectedExitException, vzd.ViZDoomIsNotRunningException):
        print("the game window closed")
    finally:
        try:
            g.close()   # ends the episode, which writes the demo
        except Exception:   # noqa: BLE001  (the game may be gone already)
            pass
        if os.path.exists(part):
            pt.move_demo(part, demo)
    return ended


class Observer(Explorer):
    """The explorer's bookkeeping over a played-back demo: no decisions, it
    just watches the play go by."""

    def __init__(self, args, vzd, geo, textures):
        super().__init__(args, vzd, geo, textures)
        self.lines = []       # report lines, for report.txt
        self.lost = []        # (tic, x, y, sector) of each L press
        self.fired = set()    # tags whose sectors have moved
        self.unlocked = set()   # locked doors that have opened
        self._ph = None
        self.key_doors = {}   # door sector -> key, for locked doors opened by hand
        self.used = set()     # tags that a switch or shot line acts on (not only walk-over lines)
        for _a, _b, _f, sp, tag, _fs, bs in geo.lines:
            spec = SPECIALS.get(sp)
            if spec and spec.trigger == "D" and spec.key and bs is not None:
                self.key_doors[bs] = spec.key
            if spec and tag and spec.trigger[:1] in "SG":
                self.used.add(tag)

    def say(self, s):
        self.lines.append(s)
        print(s, flush=True)

    def follow(self):
        """Play the demo back to the end; the reason it ended, or None for the exit."""
        g = self.game
        lost, stop = self.buttons.index("RELOAD"), self.buttons.index("ZOOM")
        held = False
        self.say(f"PLAY {self.args.map.upper()} skill {self.args.skill}: a person's play, played back")
        while not g.is_episode_finished():
            g.advance_action()
            self.tics += 1
            self._state = None
            if g.is_episode_finished():
                break
            a = g.get_last_action()
            if a[stop]:
                self.tics -= 1
                return "you stopped (K)"
            if g.is_player_dead():
                return "you died"
            try:
                self.watch()
            except Teleported:
                pass
            self.progress()
            if a[lost] and not held:
                x, y = self.pos()
                self.lost.append((self.tics, x, y, self.geo.sector_at((x, y))))
                self.note("lost", "you pressed L")
            held = bool(a[lost])
        if self.ended == "closed":   # the demo just runs out where the window went
            return "the window was closed: the recording stops there"
        if g.is_player_dead():
            return "you died"
        self.event("exit", "exited")
        return None

    def progress(self):
        """A person's progress, from what moved: a tag's sectors moving for
        the first time (not lifts), and locked doors opening."""
        h = self.heights()
        was, self._ph = self._ph, h
        if was is None:
            return
        g = self.geo
        for s in [s for s, hs in enumerate(h) if hs != was[s]]:
            tag = g.sectors[s][6]
            if tag and s not in g.lifts and tag not in self.fired:
                # A switch's or a shot line's work is progress, as for the explorer;
                # what only walk-over lines set off (an ambush closet) is noted.
                self.fired.add(tag)
                moved = sorted({self.name(t) for t, sec in enumerate(g.sectors) if sec[6] == tag})
                text = f"{'/'.join(moved[:3])}{'...' if len(moved) > 3 else ''} started moving"
                if tag in self.used:
                    self.event("switch", text, True)
                else:
                    self.note("walk", text)
            if s in self.key_doors and s not in self.unlocked and h[s][1] > was[s][1]:
                self.unlocked.add(s)
                self.event("door", f"{self.name(s)} ({self.key_doors[s]} key)", True)


def report(vzd, folder, iwad=None):
    """Play a play's demo back headless and write its report."""
    folder = os.path.abspath(folder)
    with open(os.path.join(folder, "meta.json")) as f:
        meta = json.load(f)
    wads = [os.path.join(folder, w) for w in meta["wads"]]
    args = SimpleNamespace(
        map=meta["map"], skill=meta["skill"], seed=meta["seed"], monsters=meta["monsters"], wad=wads,
        iwad=meta["iwad"] if os.path.exists(meta["iwad"]) else iwad, module=meta.get("module"),
        replaying=os.path.join(folder, "play.lmp"), play=False, recording=None, fight=False, explore=False,
        watch=False, shots=os.path.join("/tmp", "playtest-shots", meta["map"]), max_time=10 ** 6)
    m = pt.find_map(wads, args.map)
    names, crit, boss = level_info(args.module, meta["sources"] if args.module else wads, args.map)
    r = Observer(args, vzd, pt.Geometry(m), line_textures(m))
    r.names = names
    r.ended = meta.get("ended")
    try:
        stopped = r.follow()
        gaps = r.report(stopped, crit, boss) or []
    finally:
        r.game.close()
    if r.lost:
        r.say("you marked yourself lost:")
        for t, x, y, s in r.lost:
            inside = next(((span, a) for span, a, b in gaps if a <= t < b), None)
            r.say(f"  {pt.clock(t)} in {r.name(s)} ({x:.0f},{y:.0f})"
                  + (f", {pt.clock(t - inside[1])} into the {pt.clock(inside[0])} stretch from {pt.clock(inside[1])}"
                     if inside else ", outside the stretches above"))
    with open(os.path.join(folder, "report.txt"), "w") as f:
        f.write("\n".join(r.lines) + "\n")
    print(f"report written to {os.path.join(folder, 'report.txt')}")
    return 0 if stopped is None else 1
