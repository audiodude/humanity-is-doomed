#!/usr/bin/env python3
"""Scripted, headless playtests of DOOM / DOOM II maps in GZDoom.

    playtest.py WAD MAP SCRIPT [--skill 4] [--shots DIR] [--timeout 120]
    playtest.py WAD MAP --describe       # player start, keys, special lines (Doom-format maps)

SCRIPT is a text file, one step per line, `#` starts a comment. Coordinates
are map units; a line is named by any point within 8 units of it (use its
midpoint). Steps run in order, one per game tic unless they wait:

    teleport X Y [ANGLE]      put the player on the floor at X Y (ANGLE: 0 east, 90 north)
    walk X Y [X Y ...]        run there like a player (16 units/tic), through each waypoint:
                              picks up items, crosses walk-over lines, enters secrets,
                              takes step-ups <= 24. Aborts if no progress for 2 s.
    open X Y                  open the door on that line from the player's side and wait until it
                              is passable; a door that is already open is left alone (pressing use
                              on an open DR door closes it again)
    use X Y                   press use on that line from the player's side (within 64 units)
    exit X Y                  `use` an exit line, then expect the level to end within 3 s
    shoot X Y                 trigger a gun-activated line
    give ITEM                 e.g. BlueCard, RedSkull, RocketLauncher
    killall                   kill every monster (so they don't block `walk`)
    look ANGLE [PITCH]        turn the view (PITCH: positive looks down)
    wait TICS                 35 tics = 1 second
    shot NAME                 screenshot to SHOTS/NAME.png (holds still for 1 s)
    expect floor X Y OP N     floor height at X Y        OP: == != < <= > >=
    expect ceil X Y OP N      ceiling height at X Y (doors: open when ceil > floor)
    expect has ITEM           player carries ITEM
    expect pos X Y [TOL]      player within TOL (default 16) of X Y
    expect secrets OP N       secrets found;  also: kills, items, monsters (total)

The player has god mode and notarget, so tests check wiring, not balance.
Exit status: 0 all checks passed, 1 a check failed, 2 the engine or script broke.
"""
import argparse
import os
import re
import select
import shutil
import signal
import struct
import subprocess
import sys
import tempfile
import threading
import time
import zipfile

DEFAULT_IWAD = os.environ.get("DOOM2_WAD", os.path.expanduser("~/.local/share/dsda-doom/doom2.wad"))
WIDTH, HEIGHT = 640, 480   # GZDoom opens a 640x480 window; the Xvfb screen matches it
OPS = {"==", "!=", "<", "<=", ">", ">="}
COUNTERS = {"secrets": "level.found_secrets", "kills": "level.killed_monsters",
            "items": "level.found_items", "monsters": "level.total_monsters"}

ZSCRIPT_HEAD = r'''version "4.14"

class PlaytestHandler : EventHandler
{
	int step, resumeAt, checks, fails, progressTic, exitLine;
	bool done, walking, expectExit;
	Vector2 progressPos;

	void Say(String s) { Console.Printf("PLAYTEST %s", s); }

	void Check(bool ok, int ln, String what)
	{
		checks++;
		if (ok) Say(String.Format("PASS %d: %s", ln, what));
		else { fails++; Say(String.Format("FAIL %d: %s", ln, what)); }
	}

	void Finish()
	{
		done = true;
		Say(String.Format("DONE checks=%d fails=%d", checks, fails));
	}

	void Abort(int ln, String why)
	{
		fails++;
		Say(String.Format("FAIL %d: %s", ln, why));
		Finish();
	}

	static double SegDist(Vector2 p, Vector2 a, Vector2 b)
	{
		Vector2 d = b - a;
		double len2 = d dot d;
		double t = len2 > 0 ? clamp(((p - a) dot d) / len2, 0., 1.) : 0.;
		return (p - (a + d * t)).Length();
	}

	Line FindLine(Vector2 p)
	{
		Line best;
		double bestDist = 8;
		for (int i = 0; i < level.Lines.Size(); i++)
		{
			Line l = level.Lines[i];
			double d = SegDist(p, l.v1.p, l.v2.p);
			if (d <= bestDist) { best = l; bestDist = d; }
		}
		return best;
	}

	double FloorAt(Vector2 p) { return level.PointInSector(p).floorplane.ZatPoint(p); }
	double CeilAt(Vector2 p) { return level.PointInSector(p).ceilingplane.ZatPoint(p); }

	// Press use (or shoot) on the line nearest p. Returns false if it couldn't.
	bool Trigger(PlayerPawn mo, Vector2 p, int type, int ln)
	{
		Line l = FindLine(p);
		if (!l) { Abort(ln, String.Format("no line within 8 units of %.0f,%.0f", p.x, p.y)); return false; }
		double d = SegDist(mo.pos.xy, l.v1.p, l.v2.p);
		if (type == SPAC_Use && d > 64)
		{
			Check(false, ln, String.Format("player is %.0f units from the line; use reaches 64", d));
			return false;
		}
		if (!l.Activate(mo, level.ActorOnLineSide(mo, l), type))
		{
			Check(false, ln, "line did not activate (no special, wrong side, locked, or already used)");
			return false;
		}
		return true;
	}

	// Opening height (ceiling - floor) of the door on the far side of line l
	// from the player, or -1 if l has no sector there.
	double DoorGap(PlayerPawn mo, Line l)
	{
		Sector s = level.ActorOnLineSide(mo, l) == 0 ? l.backsector : l.frontsector;
		return s ? s.CenterCeiling() - s.CenterFloor() : -1;
	}

	// One tic of `open`: press use if the door is shut, then wait for 56 units of headroom.
	bool OpenDoor(PlayerPawn mo, Vector2 p, int ln)
	{
		Line l = FindLine(p);
		if (!l) { Abort(ln, String.Format("no line within 8 units of %.0f,%.0f", p.x, p.y)); return false; }
		double gap = DoorGap(mo, l);
		if (gap < 0) { Abort(ln, "open: one-sided line; use `use` for switches"); return false; }
		if (!walking)
		{
			walking = true;
			progressTic = level.maptime;
			if (gap < 56 && !Trigger(mo, p, SPAC_Use, ln)) { walking = false; return true; }
		}
		if (DoorGap(mo, l) >= 56) { walking = false; return true; }
		if (level.maptime - progressTic > 105)
		{
			Check(false, ln, String.Format("open: door still only %.0f high after 3 s", DoorGap(mo, l)));
			walking = false;
			return true;
		}
		return false;
	}

	// One tic of walking toward t. True on arrival.
	bool WalkTo(PlayerPawn mo, Vector2 t, int ln)
	{
		if (!walking)
		{
			walking = true;
			progressPos = mo.pos.xy;
			progressTic = level.maptime;
		}
		Vector2 d = t - mo.pos.xy;
		double dist = d.Length();
		if (dist <= 6)
		{
			mo.vel.xy = (0, 0);
			walking = false;
			return true;
		}
		if ((mo.pos.xy - progressPos).Length() > 8)
		{
			progressPos = mo.pos.xy;
			progressTic = level.maptime;
		}
		else if (level.maptime - progressTic > 70)
		{
			Abort(ln, String.Format("walk stuck at %.0f,%.0f (z %.0f) heading for %.0f,%.0f",
				mo.pos.x, mo.pos.y, mo.pos.z, t.x, t.y));
			return false;
		}
		mo.vel.xy = d.Unit() * min(16., dist);   // running speed
		mo.angle = atan2(d.y, d.x);
		return false;
	}

	int KillAll()
	{
		int n;
		let it = ThinkerIterator.Create("Actor");
		Actor a;
		while (a = Actor(it.Next()))
		{
			if (a.bIsMonster && a.health > 0)
			{
				a.DamageMobj(null, null, a.health, 'None', DMG_FORCED);
				n++;
			}
		}
		return n;
	}

	override void WorldUnloaded(WorldEvent e)
	{
		if (done || !(level.MapName ~== "%MAP%")) return;
		if (expectExit) Check(true, exitLine, "level exited to " .. e.NextMap);
		else Check(false, step, "level ended before the script finished (next map " .. e.NextMap .. ")");
		Finish();
	}

	override void WorldTick()
	{
		if (done || !(level.MapName ~== "%MAP%") || level.maptime < resumeAt) return;
		let mo = players[consoleplayer].mo;
		switch (step)
		{
		case 0:
			players[consoleplayer].cheats |= CF_GODMODE | CF_NOTARGET;
			Say(String.Format("START %s skill %d, %d monsters, %d secrets",
				level.MapName, G_SkillPropertyInt(SKILLP_ACSReturn) + 1, level.total_monsters, level.total_secrets));
			step++;
			break;
'''

ZSCRIPT_TAIL = r'''		default:
			Finish();
			break;
		}
	}
}
'''


class ScriptError(Exception):
    pass


def zstr(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def num(tok, ln):
    try:
        return float(tok)
    except ValueError:
        raise ScriptError(f"line {ln}: expected a number, got {tok!r}")


def vec(x, y):
    return f"({x:g}, {y:g})"


def compile_script(text, shot_tics=35):
    """Script text -> list of ZScript `case` bodies (each ends by advancing
    `step`)."""
    cases = []
    for ln, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        cmd, *args = line.split()
        say = f"Say({zstr(f'STEP {ln}: {line}')});"

        def need(n, at_most=None):
            if len(args) < n or (at_most is not None and len(args) > at_most):
                raise ScriptError(f"line {ln}: `{cmd}` takes {n}" + (f"-{at_most}" if at_most and at_most != n else "")
                                  + f" arguments: {raw.strip()}")

        if cmd == "teleport":
            need(2, 3)
            x, y = num(args[0], ln), num(args[1], ln)
            angle = f"{num(args[2], ln):g}" if len(args) == 3 else "mo.angle"
            cases.append(f"{say} mo.Teleport(({x:g}, {y:g}, FloorAt({vec(x, y)})), {angle}, 0); "
                         f"mo.vel = (0, 0, 0); step++; break;")
        elif cmd == "walk":
            if len(args) < 2 or len(args) % 2:
                raise ScriptError(f"line {ln}: `walk` takes X Y pairs: {raw.strip()}")
            for i in range(0, len(args), 2):
                x, y = num(args[i], ln), num(args[i + 1], ln)
                first = say if i == 0 else ""
                cases.append(f"if (!walking) {{ {first} }} if (WalkTo(mo, {vec(x, y)}, {ln})) step++; break;")
        elif cmd == "open":
            need(2, 2)
            x, y = num(args[0], ln), num(args[1], ln)
            cases.append(f"if (!walking) {{ {say} }} if (OpenDoor(mo, {vec(x, y)}, {ln})) step++; break;")
        elif cmd in ("use", "exit", "shoot"):
            need(2, 2)
            x, y = num(args[0], ln), num(args[1], ln)
            kind = "SPAC_Impact" if cmd == "shoot" else "SPAC_Use"
            if cmd == "exit":
                cases.append(f"{say} expectExit = true; exitLine = {ln}; "
                             f"if (Trigger(mo, {vec(x, y)}, SPAC_Use, {ln})) resumeAt = level.maptime + 105; "
                             f"step++; break;")
                cases.append(f"Check(false, {ln}, \"the level did not end within 3 s\"); expectExit = false; "
                             f"step++; break;")
            else:
                cases.append(f"{say} Trigger(mo, {vec(x, y)}, {kind}, {ln}); step++; break;")
        elif cmd == "give":
            need(1, 1)
            cases.append(f"{say} mo.GiveInventory({zstr(args[0])}, 1); step++; break;")
        elif cmd == "killall":
            need(0, 0)
            cases.append(f"{say} Say(String.Format(\"killed %d monsters\", KillAll())); step++; break;")
        elif cmd == "look":
            need(1, 2)
            pitch = f" mo.pitch = {num(args[1], ln):g};" if len(args) == 2 else ""
            cases.append(f"{say} mo.angle = {num(args[0], ln):g};{pitch} step++; break;")
        elif cmd == "wait":
            need(1, 1)
            cases.append(f"{say} resumeAt = level.maptime + {int(num(args[0], ln))}; step++; break;")
        elif cmd == "shot":
            need(1, 1)
            if not re.fullmatch(r"[\w.-]+", args[0]):
                raise ScriptError(f"line {ln}: shot name must be letters, digits, _ . -")
            cases.append(f"Say({zstr('SHOT ' + args[0])}); resumeAt = level.maptime + {shot_tics}; step++; break;")
        elif cmd == "expect":
            if not args:
                raise ScriptError(f"line {ln}: `expect` needs a subject")
            what, rest = args[0], args[1:]
            desc = zstr(line)
            if what in ("floor", "ceil"):
                if len(rest) != 4 or rest[2] not in OPS:
                    raise ScriptError(f"line {ln}: expect {what} X Y OP N")
                x, y, op, n = num(rest[0], ln), num(rest[1], ln), rest[2], num(rest[3], ln)
                fn = "FloorAt" if what == "floor" else "CeilAt"
                cases.append(f"{{ double v = {fn}({vec(x, y)}); Check(v {op} {n:g}, {ln}, "
                             f"String.Format(\"%s (it is %.0f)\", {desc}, v)); }} step++; break;")
            elif what == "has":
                if len(rest) != 1:
                    raise ScriptError(f"line {ln}: expect has ITEM")
                cases.append(f"Check(mo.CountInv({zstr(rest[0])}) > 0, {ln}, {desc}); step++; break;")
            elif what == "pos":
                if len(rest) not in (2, 3):
                    raise ScriptError(f"line {ln}: expect pos X Y [TOL]")
                x, y = num(rest[0], ln), num(rest[1], ln)
                tol = num(rest[2], ln) if len(rest) == 3 else 16
                cases.append(f"Check((mo.pos.xy - {vec(x, y)}).Length() <= {tol:g}, {ln}, String.Format("
                             f"\"%s (player at %.0f,%.0f)\", {desc}, mo.pos.x, mo.pos.y)); step++; break;")
            elif what in COUNTERS:
                if len(rest) != 2 or rest[0] not in OPS:
                    raise ScriptError(f"line {ln}: expect {what} OP N")
                expr = COUNTERS[what]
                cases.append(f"Check({expr} {rest[0]} {int(num(rest[1], ln))}, {ln}, String.Format("
                             f"\"%s (it is %d)\", {desc}, {expr})); step++; break;")
            else:
                raise ScriptError(f"line {ln}: unknown expect subject {what!r}")
        else:
            raise ScriptError(f"line {ln}: unknown step {cmd!r}")
    return cases


def build_pk3(path, map_name, cases):
    body = "".join(f"\t\tcase {i + 1}:\n\t\t\t{c}\n" for i, c in enumerate(cases))
    zscript = ZSCRIPT_HEAD.replace("%MAP%", map_name) + body + ZSCRIPT_TAIL
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("MAPINFO", 'GameInfo { AddEventHandlers = "PlaytestHandler" }\n')
        z.writestr("ZSCRIPT", zscript)
    return zscript


def start_xvfb():
    r, w = os.pipe()
    proc = subprocess.Popen(["Xvfb", "-displayfd", str(w), "-screen", "0", f"{WIDTH}x{HEIGHT}x24", "-nolisten", "tcp"],
                            pass_fds=(w,), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.close(w)
    display = b""
    deadline = time.time() + 10
    while not display.endswith(b"\n") and time.time() < deadline:
        if select.select([r], [], [], 0.5)[0]:
            chunk = os.read(r, 16)
            if not chunk:
                break
            display += chunk
    os.close(r)
    if not display.strip():
        proc.kill()
        sys.exit("Xvfb did not start")
    return proc, ":" + display.decode().strip()


def screenshot(display, path):
    time.sleep(0.5)
    subprocess.run(["import", "-display", display, "-window", "root", path],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def run(args):
    script = open(args.script).read()
    try:
        cases = compile_script(script)
    except ScriptError as e:
        print("script error:", e)
        return 2
    work = tempfile.mkdtemp(prefix="playtest-")
    pk3 = os.path.join(work, "playtest.pk3")
    zscript = build_pk3(pk3, args.map.upper(), cases)
    shots = args.shots or os.path.join(tempfile.gettempdir(), "playtest-shots", args.map.upper())
    os.makedirs(shots, exist_ok=True)
    xvfb, display = start_xvfb()
    env = dict(os.environ, DISPLAY=display, HOME=work, XDG_CONFIG_HOME=work, XDG_DATA_HOME=work, XDG_CACHE_HOME=work)
    # Window settings are read from the config before `+cvar` arguments apply; without them
    # GZDoom opens a window 80% of the screen and screenshots get a black border.
    ini = os.path.join(work, "gzdoom.ini")
    with open(ini, "w") as f:
        f.write(f"[GlobalSettings]\nvid_fullscreen=false\nwin_w={WIDTH}\nwin_h={HEIGHT}\nwin_x=0\nwin_y=0\n"
                "show_messages=false\nqueryiwad=false\ndisableautoload=true\ncl_capfps=true\n")
    # GZDoom block-buffers stdout into a pipe; stdbuf makes each PLAYTEST line arrive as it's printed.
    cmd = ["stdbuf", "-oL", "gzdoom", "-iwad", args.iwad, "-file", *args.wad, pk3, "-config", ini,
           "-nosound", "-skill", str(args.skill), "+map", args.map.upper(), "+compatmode", str(args.compat)]
    game = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, start_new_session=True)
    log, status, shooters, buf = [], None, [], b""
    deadline = time.time() + args.timeout
    try:
        while status is None:
            if time.time() > deadline:
                print(f"TIMEOUT after {args.timeout} s")
                status = 2
                break
            if not select.select([game.stdout], [], [], 0.5)[0]:
                continue
            chunk = os.read(game.stdout.fileno(), 65536)
            if not chunk:
                print("gzdoom exited before the script finished")
                status = 2
                break
            buf += chunk
            *lines, buf = buf.split(b"\n")
            for raw in lines:
                text = raw.decode("utf-8", "replace").rstrip()
                log.append(text)
                if text.startswith("PLAYTEST "):
                    msg = text[9:]
                    if msg.startswith("SHOT "):
                        path = os.path.join(shots, msg[5:] + ".png")
                        t = threading.Thread(target=screenshot, args=(display, path))
                        t.start()
                        shooters.append(t)
                        print("shot", path)
                    else:
                        print(msg)
                    if msg.startswith("DONE"):
                        status = 0 if " fails=0" in msg else 1
                elif "Script error" in text or "Execution could not continue" in text or text.startswith("Error"):
                    print("ENGINE:", text)
                    status = 2
    finally:
        for t in shooters:
            t.join()
        os.killpg(game.pid, signal.SIGKILL)
        game.wait()
        xvfb.kill()
        xvfb.wait()
    if status == 2:
        print("--- last engine output ---")
        print("\n".join(log[-40:]))
        dump = os.path.join(shots, "playtest.zs")
        open(dump, "w").write(zscript)
        print("generated ZScript:", dump)
    shutil.rmtree(work, ignore_errors=True)
    return status


# ------------------------------------------------------------- describe ---

SPECIAL_NAMES = {
    1: "DR door", 26: "DR blue door", 27: "DR yellow door", 28: "DR red door", 31: "D1 door", 32: "D1 blue door",
    33: "D1 red door", 34: "D1 yellow door", 11: "S1 exit", 51: "S1 secret exit", 52: "W1 exit",
    124: "W1 secret exit", 39: "W1 teleport", 97: "WR teleport", 62: "SR lift", 88: "WR lift", 21: "S1 lift",
    10: "W1 lift", 103: "S1 door open", 2: "W1 door open", 61: "SR door open", 86: "WR door open",
    23: "S1 floor lowest", 38: "W1 floor lowest", 60: "SR floor lowest", 82: "WR floor lowest",
    46: "GR door open", 24: "G1 floor raise", 47: "G1 floor raise",
}
THING_NAMES = {1: "player 1 start", 5: "blue keycard", 6: "yellow keycard", 13: "red keycard",
               40: "blue skull", 39: "yellow skull", 38: "red skull", 14: "teleport destination"}


def read_map(path, name):
    with open(path, "rb") as f:
        data = f.read()
    n, off = struct.unpack("<ii", data[4:12])
    lumps = [struct.unpack("<ii8s", data[off + 16 * i: off + 16 * i + 16]) for i in range(n)]
    names = [nm.split(b"\0")[0].decode() for _, _, nm in lumps]
    if name not in names:
        return None
    i = names.index(name)
    return {names[j]: data[lumps[j][0]:lumps[j][0] + lumps[j][1]] for j in range(i + 1, min(i + 12, n))}


def describe(args):
    m = None
    for wad in reversed(args.wad):
        m = read_map(wad, args.map.upper())
        if m:
            break
    if not m or "LINEDEFS" not in m:
        print(f"{args.map} not found as a Doom-format map in {args.wad}")
        return 2
    verts = list(struct.iter_unpack("<hh", m["VERTEXES"]))
    sides = list(struct.iter_unpack("<hh8s8s8sh", m["SIDEDEFS"]))
    sectors = list(struct.iter_unpack("<hh8s8shhh", m["SECTORS"]))
    print("things:")
    for x, y, angle, kind, flags in struct.iter_unpack("<hhhhh", m["THINGS"]):
        if kind in THING_NAMES:
            print(f"  {THING_NAMES[kind]:22} {x:6} {y:6}  angle {angle}")
    print("special lines (midpoint; front sector floor/ceil; tag -> tagged sector floors):")
    for v1, v2, flags, special, tag, front, back in struct.iter_unpack("<hhhhhhh", m["LINEDEFS"]):
        if not special:
            continue
        (x1, y1), (x2, y2) = verts[v1], verts[v2]
        fs = sectors[sides[front][5]]
        tagged = [s[0] for s in sectors if tag and s[6] == tag]
        label = SPECIAL_NAMES.get(special, f"special {special}")
        print(f"  {label:18} mid {(x1 + x2) / 2:7.0f} {(y1 + y2) / 2:7.0f}   {x1},{y1} -> {x2},{y2}"
              f"   front {fs[0]}/{fs[1]}" + (f"   tag {tag} -> floors {tagged}" if tag else "")
              + ("" if back >= 0 else "   one-sided"))
    secrets = [i for i, s in enumerate(sectors) if s[5] == 9]
    print(f"secret sectors: {len(secrets)}")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("wad", nargs="+", help="PWAD(s) to load, then the map, e.g. wads/X.WAD MAP02")
    p.add_argument("--script", help="step script (or give it as the last positional argument)")
    p.add_argument("--describe", action="store_true", help="list the map's start, keys and special lines")
    p.add_argument("--iwad", default=DEFAULT_IWAD)
    p.add_argument("--skill", type=int, default=4, help="1 ITYTD .. 4 UV, 5 NM (default 4)")
    p.add_argument("--compat", type=int, default=2, help="GZDoom compatmode (default 2: Doom strict)")
    p.add_argument("--shots", help="screenshot directory (default /tmp/playtest-shots/MAP)")
    p.add_argument("--timeout", type=float, default=120)
    args = p.parse_args()
    pos = args.wad
    if not args.describe and not args.script:
        if len(pos) < 3:
            p.error("give WAD... MAP SCRIPT")
        args.script = pos.pop()
    if len(pos) < 2:
        p.error("give WAD... MAP")
    args.map = pos.pop()
    args.wad = pos
    sys.exit(describe(args) if args.describe else run(args))


if __name__ == "__main__":
    main()
