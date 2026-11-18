"""play_queue.py: play the blind pool's next maps back to back, with no report
or scoring in between (docs/explorer-plan.md section 2).

    uv run --with vizdoom scripts/tools/play_queue.py [QUEUE]

QUEUE (default ~/.local/share/playtest/queue.txt) has one map per line:

    POOL SOURCE MAP WAD      e.g. 17 slige MAP01 ../doomedit/wads/SLIGE06.WAD

POOL is the play's number in the blind pool, SOURCE obsidian, slige or
community. A line whose number already has a play is skipped, so the same
queue can be picked up again after a break. Each map is played with
--play --no-report. After it, one question: Enter if it was a normal play, or
a few words on any deliberate detour (a secret, an item, sightseeing) or on
what spoiled it. A note starting with "spoiled" drops the play; its map is no
longer blind, so its line stays used. The note goes
in the play's meta.json and notes.txt, with its number and source; its
report and scores come later (compare.py, which also stores its first score).
"""
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLAYS = os.path.expanduser("~/.local/share/playtest/plays")
QUEUE = os.path.expanduser("~/.local/share/playtest/queue.txt")


def played():
    """Pool numbers that already have a play."""
    out = set()
    for path in glob.glob(os.path.join(PLAYS, "*", "meta.json")):
        with open(path) as f:
            n = json.load(f).get("pool")
        if n is not None:
            out.add(n)
    return out


def main():
    queue = sys.argv[1] if len(sys.argv) > 1 else QUEUE
    with open(queue) as f:
        lines = [ln.split(None, 3) for ln in f if ln.strip() and not ln.startswith("#")]
    todo = [(int(n), src, m, w) for n, src, m, w in lines if int(n) not in played()]
    if not todo:
        print(f"nothing left to play in {queue}")
        return 0
    for k, (n, src, m, wad) in enumerate(todo):
        if input(f"\nplay #{n} ({src}, {k + 1} of {len(todo)}): Enter to start, q to stop: ").strip().lower() == "q":
            break
        before = set(os.listdir(PLAYS))
        subprocess.run([sys.executable, os.path.join(HERE, "playtest.py"), wad.strip(), m, "--play", "--no-report"],
                       check=False)
        new = sorted(set(os.listdir(PLAYS)) - before)
        if not new:
            print("no play was recorded; this map stays in the queue")
            continue
        folder = os.path.join(PLAYS, new[-1])
        note = input("Enter if it was a normal play, or a few words on a detour or what spoiled it: ").strip()
        with open(os.path.join(folder, "meta.json")) as f:
            meta = json.load(f)
        meta.update(pool=n, source=src)
        if note:
            meta["note"] = note
            if note.lower().startswith("spoiled"):
                meta["spoiled"] = note
            with open(os.path.join(folder, "notes.txt"), "w") as f:
                f.write(f"Play #{n} ({src}), noted right after the play: {note}\n")
        with open(os.path.join(folder, "meta.json"), "w") as f:
            json.dump(meta, f, indent=1)
    left = [n for n, *_ in todo if n not in played()]
    print(f"\n{len(todo) - len(left)} played; {len(left)} left in the queue" + (f": #{left[0]} next" if left else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
