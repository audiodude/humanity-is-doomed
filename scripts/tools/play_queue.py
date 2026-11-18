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
longer blind, so its line stays used. Any other note is a detour: the play is
rendered to a video (a minute or two) that opens in your player, and you give
the detour's times off its clock (M:SS-M:SS, several separated by commas),
which go in meta.json as "choice" for compare.py. The note goes in the play's
meta.json and notes.txt, with its number and source; its report and scores
come later (compare.py, which also stores its first score).
"""
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PLAYS = os.path.expanduser("~/.local/share/playtest/plays")
QUEUE = os.path.expanduser("~/.local/share/playtest/queue.txt")


def played():
    """Pool numbers that already have a play, and every WAD any play loaded."""
    numbers, wads = set(), set()
    for path in glob.glob(os.path.join(PLAYS, "*", "meta.json")):
        with open(path) as f:
            meta = json.load(f)
        if meta.get("pool") is not None:
            numbers.add(meta["pool"])
        wads |= {os.path.realpath(w) for w in meta.get("sources", ())}
    return numbers, wads


def detour_times(folder, meta):
    """Render the play to a video, open it, and ask for the detour's times:
    a list of "M:SS-M:SS" (empty if skipped)."""
    video = os.path.join(tempfile.gettempdir(), f"{os.path.basename(folder)}.mp4")
    print("rendering the play so you can time the detour (a minute or two) ...", flush=True)
    subprocess.run([sys.executable, os.path.join(HERE, "playtest.py"), *[os.path.join(folder, w) for w in meta["wads"]],
                    meta["map"], "--replay", "--recording", os.path.join(folder, "play.lmp"), "--video", video],
                   check=False, stdout=subprocess.DEVNULL)
    if os.path.exists(video):
        subprocess.Popen(["xdg-open", video], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)
    else:
        print("the video didn't render; give the times from memory, or Enter to skip")
    while True:
        ans = input("detour times off the video's clock, M:SS-M:SS (commas between several; Enter to skip): ").strip()
        spans = [s.strip() for s in ans.split(",") if s.strip()]
        if all(re.fullmatch(r"\d+:[0-5]\d-\d+:[0-5]\d", s) for s in spans):
            return spans
        print("  like 3:37-4:05, or 3:37-4:05, 6:10-6:40")


def main():
    queue = sys.argv[1] if len(sys.argv) > 1 else QUEUE
    with open(queue) as f:
        lines = [ln.split(None, 3) for ln in f if ln.strip() and not ln.startswith("#")]
    numbers, wads = played()
    todo = []
    for n, src, m, w in lines:
        if int(n) in numbers:
            continue
        if os.path.realpath(w.strip()) in wads:
            print(f"#{n}: {w.strip()} has been played before, so it isn't blind; skipped (give #{n} another map)")
            continue
        todo.append((int(n), src, m, w))
    if not todo:
        print(f"nothing left to play in {queue}")
        return 0
    for k, (n, src, m, wad) in enumerate(todo):
        if input(f"\nplay #{n} ({src}, {k + 1} of {len(todo)}): press ENTER to start, or type q to stop: ").strip().lower() == "q":
            break
        before = set(os.listdir(PLAYS))
        subprocess.run([sys.executable, os.path.join(HERE, "playtest.py"), wad.strip(), m, "--play", "--no-report"],
                       check=False)
        new = sorted(set(os.listdir(PLAYS)) - before)
        if not new:
            print("no play was recorded; this map stays in the queue")
            continue
        folder = os.path.join(PLAYS, new[-1])
        note = input("Normal play? Just press ENTER. Otherwise type a few words on a detour, "
                     "or start with 'spoiled' if something went wrong: ").strip()
        if note.lower().rstrip(".!") in ("normal", "no", "n", "none", "yes", "y"):
            note = ""   # meant "a normal play"
        with open(os.path.join(folder, "meta.json")) as f:
            meta = json.load(f)
        meta.update(pool=n, source=src)
        if note:
            meta["note"] = note
            if note.lower().startswith("spoiled"):
                meta["spoiled"] = note
            else:
                meta["choice"] = detour_times(folder, meta)
            with open(os.path.join(folder, "notes.txt"), "w") as f:
                f.write(f"Play #{n} ({src}), noted right after the play: {note}\n"
                        + (f"detour times (--choice): {', '.join(meta['choice'])}\n" if meta.get("choice") else ""))
        with open(os.path.join(folder, "meta.json"), "w") as f:
            json.dump(meta, f, indent=1)
    left = [n for n, *_ in todo if n not in played()[0]]
    print(f"\n{len(todo) - len(left)} played; {len(left)} left in the queue" + (f": #{left[0]} next" if left else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
