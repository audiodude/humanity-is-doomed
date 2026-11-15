# Explorer vs human rubric, v1

How well the `--explore` bot's stalls predict where a person gets lost, scored
by fixed rules. `scripts/tools/compare.py` applies every rule except the cause
codes in section 6, which need someone to watch both runs.

## 1. What it measures, and what it doesn't

It scores the **explorer**, never the map. A map where players stall, press L
or wander into side areas can be a good map. Some searching is part of
DOOM, lure areas add fun and dimension, and a map with no wrong turns is one
strangely shaped corridor. So:

- A lure (S6) the bot ignores is the bot's miss. The fix is to give the bot
  the pull a person felt, not to take the lure out of the map.
- Once the explorer passes the bar in section 7, its stalls describe a map
  (where players will search, and for how long). They don't grade it. How much
  searching is too much is the designer's call.

## 2. Which runs can be scored

- **Same conditions:** same WAD (by hash), map and skill. Monsters off and god
  mode on for both.
- **Human run:** the person's first play of the map. They haven't seen its
  layout, an explorer report or a replay of it. They head for the exit rather
  than secrets, press L whenever they feel lost, and the run ends at the exit,
  at K, or at 15 minutes. Anything past 15 minutes is cut off.
- **Bot runs:** seeds 1, 2 and 3 of one explorer commit, each capped at 15 minutes.

## 3. Definitions (the same for both sides)

- **Milestone:** one of these, and nothing else:
  - a key picked up (by colour)
  - a switch's or shot line's sectors moving for the first time (by tag;
    lifts and sectors only walk-over lines move don't count)
  - a locked door opening (by sector)
  - the exit

  Teleports, wall searches and re-pressed switches are not milestones.
- **Common milestone:** one the human and at least one seed both reached.
- **Phase:** the set of common milestones done so far. A stall's phase is
  taken at its start, an L press's when it was pressed.
- **Stall:** 30 s or more of game time with no milestone. The stretch from the
  last milestone to the end of the run counts.
- **Square:** a 256×256-unit square of the map.
- **Area:** where a stall's time went. The position on every tic counts for
  the 3×3 block of squares around it, each square getting a ninth of the
  tic, and each square's total is divided by the stall's length. This gives
  shares that add up to 1.
- **Same place:** two stalls are in the same place when their areas have at
  least **0.25** of their time in common (the sum over squares of the smaller
  of the two shares). A stall is where an L press was when at least **0.10** of
  its time was within one square of the press.
- **Predicted:** a human stall or L press is predicted on a seed when that seed
  has a stall in the same phase and the same place. It's predicted overall
  when that happens on at least 2 of the 3 seeds (with other seed counts, two
  thirds, rounded up).
- **Recurring bot stall:** a group of stalls in the same phase, linked pairwise
  by being in the same place, on at least 2 of the 3 seeds.
- **L presses:** a press within 30 s of the previous one and in the same
  square is the same press.

## 4. Scores

| | Score | Rule | Pass |
|---|---|---|---|
| S1 | Outcome | The human and most seeds have the same result (exit or no exit). The number of common milestones each reached is reported too. | same result |
| S2 | Order | Of the pairs of common milestones both the human and a seed reached, the share done in the same order, averaged over the seeds | ≥ 0.75 |
| S3 | **Lost recall** (main score) | Predicted L presses ÷ all L presses | ≥ 2/3 |
| S4 | Stall recall | Predicted human stalls ÷ all human stalls | ≥ 1/2 |
| S5 | Stall precision | Recurring bot stalls in the same phase and place as a human stall or an L press ÷ all recurring bot stalls | ≥ 1/2 |
| S6 | Lures | Squares where the human spent 30 s or more in all and no seed ever entered | listed; each is a miss for the bot, not a flaw in the map |
| S7 | Bot traps | Squares where at least 2 seeds each spent 30 s or more and the human never entered | listed |

With no L presses, S3 is n/a and S4 stands in for it. With no recurring bot
stalls, S5 is n/a and passes.

## 5. Verdict for each map

- **Predicts:** S1, S3 and S5 all pass.
- **Partial:** not Predicts, but S3 or S4 is at least 1/3.
- **Misses:** anything else.
- **Bot-limited:** not scored. The seeds fail on a known blind spot (running
  jumps, gun lines with no switch texture, timed doors and lifts, unread line
  types) before the human's first L press. That takes a B-blind code (section
  6), so `compare.py` gives the verdict as if the map weren't bot-limited, and
  the person coding the mismatches overrules it.

## 6. A cause for every mismatch

This is the part that needs judgement. For each unmatched L press, human stall,
recurring bot stall, lure and trap that `compare.py` lists, watch both runs at
that time and place and give it one code:

- **B-blind:** a mechanic the bot doesn't have.
- **B-weak:** a bot navigation failure (getting stuck, a lift, a bad path).
- **B-lure:** the human was drawn by something the bot gives no weight to: open
  space, light, an item, or a place they could see but not reach.
- **B-memory:** the bot found the way only because it never forgets floor it
  has seen and sweeps edges in order. The human had simply overlooked it.
- **H-choice:** the human chose to detour (a secret, an item, sightseeing).
  These come out of the scores: rerun `compare.py` with `--choice M:SS-M:SS`
  for each such stretch of the human run.

B-lure and B-memory point opposite ways: the first means the bot lacks a human
pull, the second that it is better than a human. Each needs a different fix.

## 7. Pooling, and when to trust the explorer

- Add up the S3 and S5 counts over every scored map (`compare.py --pool`).
- Use the explorer's stalls as evidence in map review only once pooled lost
  recall is at least 60% and pooled precision at least 50%, over at least 5
  maps and 10 L presses. Until then they're hints.
- Tune the explorer on some plays and keep others aside, never tuned on, to
  check the gain is real.
- Any rule change gets a new version number, and every map is scored again
  under it.
- When the explorer changes, rerun the seeds and score again. Old scores stay
  (each commit's scores have their own folder), so you can see whether a change
  helped the bot predict people, not just finish more maps.

## 8. Running it

```sh
uv run --with vizdoom scripts/tools/compare.py ~/.local/share/playtest/plays/<folder>
uv run --with vizdoom scripts/tools/compare.py ~/.local/share/playtest/plays/<folder> --choice 2:10-2:55
uv run --with vizdoom scripts/tools/compare.py --pool        # S3 and S5 over every scored play, this commit
```

It runs the explorer on the play's own copy of the WAD for each seed, plays
every demo (the person's and the seeds') back through the `--play` report's
bookkeeping, so milestones mean the same on both sides, and writes
`compare-<commit>/` in the play folder: the seeds' explore reports,
`report.txt` (milestone times, the scores, the verdict and the mismatches to
code) and `scores.json`.
