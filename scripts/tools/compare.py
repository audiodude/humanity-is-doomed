"""compare.py: score the explorer against a person's --play of the same map,
by the rubric in docs/explore-rubric.md.

    uv run --with vizdoom scripts/tools/compare.py PLAY_DIR [--seeds 1,2,3] [--choice M:SS-M:SS ...]
    uv run --with vizdoom scripts/tools/compare.py --pool [--commit HASH]

It runs --explore on the play's own copy of the WAD for each seed, then plays
every demo back (the person's and each seed's) through the --play report's
bookkeeping, so a milestone means the same thing on both sides, and scores
them. It writes compare-<commit>/ in the play folder: each seed's explore
report, report.txt (milestone times, the scores, the verdict, and the
mismatches to give a cause code) and scores.json. --choice drops stretches of
the person's run coded H-choice. --pool adds up S3 and S5 over every play
scored at a commit and says whether the explorer has passed the rubric's bar.
"""
import argparse
import concurrent.futures as cf
import glob
import itertools
import json
import math
import multiprocessing
import os
import subprocess
import sys
from collections import Counter
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import playtest as pt  # noqa: E402
from explore import KEYS, line_textures  # noqa: E402
from play import PLAYS, Observer  # noqa: E402

RUBRIC = 2
TIC = 35
CAP = 15 * 60 * TIC   # runs are cut off at 15 minutes
STALL = 30 * TIC      # a stall, and a lure's or a trap's time
SQUARE = 256
SAME = 0.25          # two stretches are in the same place: a quarter of their time in common


# ------------------------------------------------------------ the demos ---

class Tracker(Observer):
    """The --play bookkeeping, keeping what the rubric needs: each milestone
    by what it is, and the square it was in every tic. Quiet, and it skips
    working out what it saw, which nothing here scores."""

    def __init__(self, *a):
        super().__init__(*a)
        self.milestones = []   # (tic, ("key", colour) | ("switch", tag) | ("door", sector) | ("exit",))
        self.squares = []      # square on tic 1, 2, ...
        self._keys = set()

    def say(self, s):
        pass

    def look(self):
        pass

    def progress(self):
        fired, unlocked = set(self.fired), set(self.unlocked)
        super().progress()
        new = [("switch", t) for t in sorted(self.fired - fired) if t in self.used]
        new += [("door", s) for s in sorted(self.unlocked - unlocked)]
        keys = {c for c, names in KEYS.items() if names & self.had}
        new += [("key", c) for c in sorted(keys - self._keys)]
        self._keys = keys
        self.milestones += [(self.tics, m) for m in new]
        x, y = self.pos()
        self.squares.append((math.floor(x / SQUARE), math.floor(y / SQUARE)))


def trace(folder, demo, seed, bot, ended, iwad):
    """Play a demo back headless: {milestones, squares, lost, end, exited,
    doors}, cut off at CAP. Runs in a process of its own."""
    import vizdoom as vzd
    with open(os.path.join(folder, "meta.json")) as f:
        meta = json.load(f)
    wads = [os.path.join(folder, w) for w in meta["wads"]]
    args = SimpleNamespace(
        map=meta["map"], skill=meta["skill"], seed=seed, wad=wads, module=None,
        monsters=bot,   # a seed's demo kills its own monsters, so it plays back with them, as recorded
        iwad=meta["iwad"] if os.path.exists(meta["iwad"]) else iwad, replaying=demo, play=False,
        recording=None, fight=False, explore=False, watch=False,
        shots=os.path.join("/tmp", "playtest-shots", meta["map"]), max_time=10 ** 6)
    m = pt.find_map(wads, args.map)
    r = Tracker(args, vzd, pt.Geometry(m), line_textures(m))
    r.ended = ended
    try:
        exited = r.follow() is None
    finally:
        r.game.close()
    if exited:
        r.milestones.append((r.tics, ("exit",)))
    end = min(r.tics, CAP)
    return dict(milestones=[(t, m) for t, m in r.milestones if t <= end], squares=r.squares[:end],
                lost=[(t, x, y) for t, x, y, _s in r.lost if t <= end], end=end, exited=exited and r.tics <= CAP,
                doors=r.key_doors)


def explore(folder, meta, seed, iwad, out):
    """Run --explore on the play's copy of the WAD; the recording, and whether it exited."""
    wads = [os.path.join(folder, w) for w in meta["wads"]]
    cmd = [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "playtest.py"), *wads,
           meta["map"], "--explore", "--seed", str(seed), "--skill", str(meta["skill"]), "--iwad", iwad,
           "--max-time", str(CAP // (60 * TIC))]
    with open(out, "w") as f:
        subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, check=False)
    with open(out) as f:
        exited = any(line.startswith("EXITED") for line in f)
    return pt.recording_path(SimpleNamespace(wad=wads, map=meta["map"], skill=meta["skill"], seed=seed,
                                             explore=True)), exited


# ------------------------------------------------------------- scoring ---

def stretches(run):
    """(start, end) of each stretch between milestones, the last to the run's end."""
    marks = [0] + [t for t, _m in run["milestones"]] + [run["end"]]
    return [(a, b) for a, b in itertools.pairwise(marks) if b > a]


def stalls(run):
    """The stretches of STALL tics or more."""
    return [(a, b) for a, b in stretches(run) if b - a >= STALL]


def area(squares, a, b):
    """Where tics a to b were spent: square -> share of the time, each tic
    counted for the 3x3 block of squares around it (so the shares sum to 1)."""
    n = 9 * (b - a)
    out = Counter()
    for (x, y), k in Counter(squares[a:b]).items():
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                out[x + dx, y + dy] += k / n
    return out


def overlap(f, g):
    """The share of time two areas have in common, 0 to 1."""
    return sum(min(v, g[q]) for q, v in f.items() if q in g)


def phase(run, common, t):
    return frozenset(m for tm, m in run["milestones"] if tm <= t and m in common)


def hot(f):
    """The middle of an area's busiest square, as map coordinates."""
    x, y = max(f, key=lambda q: (f[q], q))
    return round((x + 0.5) * SQUARE), round((y + 0.5) * SQUARE)


def score(human, bots, choice=()):
    """The rubric's scores for one map. human and each of bots (seed -> run)
    are trace() results; choice is the human run's H-choice stretches, in tics."""
    def chosen(t):
        return any(a <= t < b for a, b in choice)

    seeds = sorted(bots)
    need = math.ceil(2 * len(seeds) / 3)
    common = {m for _t, m in human["milestones"]} & {m for b in bots.values() for _t, m in b["milestones"]}
    # The human's stalls and lost stretches (any stretch with an L press in it:
    # a person presses L after wandering, so the press marks the whole stretch,
    # not where they stood), H-choice dropped.
    presses = [t for t, _x, _y in human["lost"] if not chosen(t)]
    spans = stretches(human)
    items = []
    for k, (a, b) in enumerate(spans):
        if any(a < y and x < b for x, y in choice):
            continue
        last = k == len(spans) - 1
        mine = [t for t in presses if a <= t < b or (last and t == b)]
        if b - a >= STALL or mine:
            items.append(dict(span=(a, b), phase=phase(human, common, a), area=area(human["squares"], a, b),
                              stall=b - a >= STALL, presses=mine))
    hst = [i for i in items if i["stall"]]
    lost = [i for i in items if i["presses"]]
    bst = {s: [dict(seed=s, span=(a, b), phase=phase(bots[s], common, a), area=area(bots[s]["squares"], a, b))
               for a, b in stalls(bots[s])] for s in seeds}

    def matches(st, other):
        """A bot stall matches a human stretch: same phase, same place."""
        return st["phase"] == other["phase"] and overlap(st["area"], other["area"]) >= SAME

    def predicted(item):
        on = [s for s in seeds if any(matches(st, item) for st in bst[s])]
        return len(on) >= need, on
    for item in items:
        item["ok"], item["on"] = predicted(item)
    # Recurring bot stalls: same phase and same place across seeds, grouped.
    every = [st for s in seeds for st in bst[s]]
    group = list(range(len(every)))

    def root(i):
        while group[i] != i:
            group[i] = group[group[i]]
            i = group[i]
        return i
    for i, j in itertools.combinations(range(len(every)), 2):
        a, b = every[i], every[j]
        if a["seed"] != b["seed"] and a["phase"] == b["phase"] and overlap(a["area"], b["area"]) >= SAME:
            group[root(i)] = root(j)
    groups = {}
    for i, st in enumerate(every):
        groups.setdefault(root(i), []).append(st)
    recurring = []
    for sts in groups.values():
        if len({st["seed"] for st in sts}) >= need:
            ok = any(matches(st, x) for st in sts for x in items)
            recurring.append(dict(stalls=sts, ok=ok))
    # Order: pairs of common milestones both sides reached, in the same order.
    order = []
    for s in seeds:
        ht = {m: t for t, m in human["milestones"] if m in common}
        bt = {m: t for t, m in bots[s]["milestones"] if m in ht}
        pairs = list(itertools.combinations(sorted(bt), 2))
        if pairs:
            order.append(sum((ht[a] < ht[b]) == (bt[a] < bt[b]) for a, b in pairs) / len(pairs))
    # Lures and traps: where one side spent STALL tics or more that the other never entered.
    htime = Counter(sq for t, sq in enumerate(human["squares"], 1) if not chosen(t))
    entered = {sq for b in bots.values() for sq in b["squares"]}
    lures = sorted(sq for sq, n in htime.items() if n >= STALL and sq not in entered)
    long = Counter(sq for b in bots.values() for sq, n in Counter(b["squares"]).items() if n >= STALL)
    traps = sorted(sq for sq, n in long.items() if n >= need and sq not in set(human["squares"]))

    def frac(items):
        return [sum(1 for i in items if i["ok"]), len(items)]
    s1 = human["exited"] == (sum(b["exited"] for b in bots.values()) * 2 > len(seeds))
    s2 = sum(order) / len(order) if order else None
    s3, s4, s5 = frac(lost), frac(hst), frac(recurring)

    def rate(f):
        return f[0] / f[1] if f[1] else None
    r3 = rate(s3) if s3[1] else rate(s4)   # no L presses: S4 stands in
    r5 = rate(s5)
    if s1 and (r3 is not None and r3 >= 2 / 3) and (r5 is None or r5 >= 1 / 2):
        verdict = "Predicts"
    elif max(rate(s3) or 0, rate(s4) or 0) >= 1 / 3:
        verdict = "Partial"
    else:
        verdict = "Misses"
    return dict(common=common, items=items, bot_stalls=bst, recurring=recurring,
                lures=lures, traps=traps, S1=s1, S2=s2, S3=s3, S4=s4, S5=s5, verdict=verdict,
                reached={"human": sum(1 for _t, m in human["milestones"] if m in common),
                         **{s: sum(1 for _t, m in bots[s]["milestones"] if m in common) for s in seeds}})


# -------------------------------------------------------------- report ---

def name(m, doors):
    if m[0] == "key":
        return f"{m[1]} key"
    if m[0] == "switch":
        return f"switch, tag {m[1]}"
    if m[0] == "door":
        return f"{doors.get(m[1], 'locked')} door, sector {m[1]}"
    return "exit"


def write_report(sc, human, bots, head):
    seeds = sorted(bots)
    doors = human["doors"]
    out = list(head)
    first = {}
    for who, run in [("you", human)] + [(s, bots[s]) for s in seeds]:
        for t, m in run["milestones"]:
            first.setdefault(m, {})[who] = t
    out.append("")
    out.append(f"{'milestone':<28}{'you':>7}" + "".join(f"{'seed ' + str(s):>9}" for s in seeds))
    for m, at in sorted(first.items(), key=lambda kv: min(kv[1].values())):
        out.append(f"{name(m, doors):<28}{pt.clock(at['you']) if 'you' in at else '-':>7}"
                   + "".join(f"{pt.clock(at[s]) if s in at else '-':>9}" for s in seeds)
                   + ("" if m in sc["common"] else "   (not common)"))
    out.append(f"{'end':<28}{pt.clock(human['end']) + ('' if human['exited'] else '*'):>7}"
               + "".join(f"{pt.clock(bots[s]['end']) + ('' if bots[s]['exited'] else '*'):>9}" for s in seeds)
               + "   (* no exit)")

    def pf(f, bar):
        return f"{f[0]}/{f[1]}" + (f"  {'pass' if f[0] / f[1] >= bar else 'fail'}" if f[1] else "  n/a")
    out += ["", f"S1 outcome          {'pass' if sc['S1'] else 'fail'}  (common milestones reached: you "
            f"{sc['reached']['human']}, seeds " + ", ".join(str(sc['reached'][s]) for s in seeds)
            + f" of {len(sc['common'])})",
            "S2 order            " + ("n/a" if sc["S2"] is None
                                       else f"{sc['S2']:.2f}  {'pass' if sc['S2'] >= 0.75 else 'fail'}"),
            f"S3 lost recall      {pf(sc['S3'], 2 / 3)}",
            f"S4 stall recall     {pf(sc['S4'], 1 / 2)}",
            f"S5 stall precision  {pf(sc['S5'], 1 / 2)}",
            f"S6 lures            {len(sc['lures'])}",
            f"S7 bot traps        {len(sc['traps'])}",
            f"verdict: {sc['verdict']} (unless the mismatches below make it Bot-limited)",
            "", "to give a cause code (docs/explore-rubric.md section 6):"]
    todo = 0
    for h in sc["items"]:
        if not h["ok"]:
            todo += 1
            a, b = h["span"]
            ls = ", ".join(f"{pt.clock(t)} ({pt.clock(t - a)} in)" for t in h["presses"])
            out.append(f"  {'lost stretch' if ls else 'your stall'} {pt.clock(a)}-{pt.clock(b)}"
                       + (f", L at {ls}," if ls else "")
                       + f" around {hot(h['area'])}: predicted on {len(h['on'])} of {len(seeds)} seeds")
    for g in sc["recurring"]:
        if not g["ok"]:
            todo += 1
            out.append("  bot stall you didn't have: " + ", ".join(
                f"seed {st['seed']} {pt.clock(st['span'][0])}-{pt.clock(st['span'][1])} around {hot(st['area'])}"
                for st in g["stalls"]))
    for sq in sc["lures"]:
        todo += 1
        out.append(f"  lure: you spent 30 s or more around {hot({sq: 1})}, where no seed went")
    for sq in sc["traps"]:
        todo += 1
        out.append(f"  bot trap: seeds spent 30 s or more around {hot({sq: 1})}, where you never went")
    if not todo:
        out.append("  nothing")
    return out


# ---------------------------------------------------------------- main ---

def commit():
    def git(*a):
        return subprocess.run(["git", "-C", pt.ROOT, *a], capture_output=True, text=True, check=False).stdout.strip()
    return git("rev-parse", "--short", "HEAD") + ("-dirty" if git("status", "--porcelain", "--", "scripts/tools", "levels")
                                                  else "")


def tics(clock):
    m, s = clock.split(":")
    return (int(m) * 60 + int(s)) * TIC


def pool(at):
    files = sorted(glob.glob(os.path.join(PLAYS, "*", f"compare-{at}", "scores.json")))
    if not files:
        print(f"no plays scored at {at}")
        return 2
    s3, s5 = [0, 0], [0, 0]
    for p in files:
        with open(p) as f:
            sc = json.load(f)
        print(f"{sc['play']}: {sc['verdict']}  S3 {sc['S3'][0]}/{sc['S3'][1]}  S5 {sc['S5'][0]}/{sc['S5'][1]}")
        s3 = [a + b for a, b in zip(s3, sc["S3"])]
        s5 = [a + b for a, b in zip(s5, sc["S5"])]
    r3 = s3[0] / s3[1] if s3[1] else 0
    r5 = s5[0] / s5[1] if s5[1] else 1
    met = len(files) >= 5 and s3[1] >= 10 and r3 >= 0.6 and r5 >= 0.5
    print(f"pooled over {len(files)} maps at {at}: lost recall {s3[0]}/{s3[1]}, stall precision {s5[0]}/{s5[1]}")
    print("the explorer's stalls are evidence for map review" if met else
          "not yet evidence (needs 5 maps, 10 lost stretches, lost recall 60%, precision 50%): hints only")
    return 0


def main():
    p = argparse.ArgumentParser(description="Score the explorer against a person's --play (docs/explore-rubric.md).")
    p.add_argument("play", nargs="?", help="a --play folder in ~/.local/share/playtest/plays/")
    p.add_argument("--seeds", default="1,2,3", help="explorer seeds (default 1,2,3)")
    p.add_argument("--choice", action="append", default=[], metavar="M:SS-M:SS",
                   help="a stretch of your run coded H-choice, left out of the scores (repeatable)")
    p.add_argument("--iwad", default=pt.DEFAULT_IWAD, help="the IWAD, if the play's is gone (default: DOOM2_WAD)")
    p.add_argument("--pool", action="store_true", help="pool the scores of every play scored at --commit")
    p.add_argument("--commit", help="with --pool: the explorer commit (default: this checkout's)")
    args = p.parse_args()
    at = commit()
    if args.pool:
        return pool(args.commit or at)
    if not args.play:
        p.error("give a --play folder, or --pool")
    folder = os.path.abspath(args.play)
    with open(os.path.join(folder, "meta.json")) as f:
        meta = json.load(f)
    if meta.get("monsters"):
        print("this play kept the monsters; the rubric scores plays with none (the default --play)")
        return 2
    seeds = [int(s) for s in args.seeds.split(",")]
    choice = [tuple(tics(c) for c in span.split("-")) for span in args.choice]
    iwad = meta["iwad"] if os.path.exists(meta["iwad"]) else args.iwad
    out = os.path.join(folder, f"compare-{at}")
    os.makedirs(out, exist_ok=True)
    print(f"exploring seeds {', '.join(map(str, seeds))} and playing the demos back ...", flush=True)
    spawn = multiprocessing.get_context("spawn")
    with cf.ProcessPoolExecutor(len(seeds) + 1, mp_context=spawn) as procs, cf.ThreadPoolExecutor(len(seeds)) as threads:
        human = procs.submit(trace, folder, os.path.join(folder, "play.lmp"), meta["seed"], False, meta.get("ended"), iwad)
        runs = {s: threads.submit(explore, folder, meta, s, iwad, os.path.join(out, f"seed{s}.txt")) for s in seeds}
        bots = {}
        for s in seeds:
            demo, exited = runs[s].result()
            bots[s] = procs.submit(trace, folder, demo, s, True, None if exited else "closed", iwad)
        human = human.result()
        bots = {s: f.result() for s, f in bots.items()}
    for s in seeds:
        with open(os.path.join(out, f"seed{s}.txt")) as f:
            said = any(line.startswith("EXITED") for line in f)
        if said != bots[s]["exited"] and bots[s]["end"] < CAP:
            print(f"warning: seed {s}'s playback drifted from its run (exit {'missed' if said else 'invented'})")
    sc = score(human, bots, choice)
    head = [f"COMPARE {meta['map']} skill {meta['skill']}: {os.path.basename(folder)}",
            f"rubric v{RUBRIC}, explorer {at}, seeds {', '.join(map(str, seeds))}"
            + (f", H-choice {', '.join(args.choice)}" if args.choice else "")]
    lines = write_report(sc, human, bots, head)
    print("\n".join(lines))
    with open(os.path.join(out, "report.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    with open(os.path.join(out, "scores.json"), "w") as f:
        json.dump(dict(rubric=RUBRIC, commit=at, play=os.path.basename(folder), map=meta["map"],
                       wad_hash=meta.get("wad_hash"), seeds=seeds, choice=args.choice, verdict=sc["verdict"],
                       S1=sc["S1"], S2=sc["S2"], S3=sc["S3"], S4=sc["S4"], S5=sc["S5"],
                       lures=len(sc["lures"]), traps=len(sc["traps"])), f, indent=1)
    print(f"written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
