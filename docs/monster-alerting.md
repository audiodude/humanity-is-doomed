# Monster alerting in DOOM II

In vanilla DOOM II a sleeping monster runs `A_Look` every few tics. It wakes up in one of three ways: it **sees** you, it **hears** you, or it **gets hurt**. Each map tool below changes one of those three.

## How monsters wake up

| Trigger | Rule |
|---|---|
| **Sight** | The monster needs a clear line of sight inside a 180° cone in front of it, so a monster facing away won't notice you. The exception is when you're within 64 units of it (melee range), where it notices you from any direction. The REJECT lump can also rule out sight between two sectors. |
| **Sound** | Firing any weapon, including the fist, alerts monsters through sound. The noise floods outward from your sector through two-sided lines that have an opening. Every sector it reaches remembers you as its sound target, and sleeping monsters in those sectors wake on their next look. |
| **Damage** | A monster that gets hurt by anything (your shot, splash damage, another monster) wakes up and goes after the attacker. |

Sound comes only from weapon fire. Doors, lifts, item pickups, footsteps and monster noises don't wake anyone.

## Tools for controlling alerting

1. **The Ambush thing flag**, often mislabeled "deaf". A monster with this flag ignores sound unless it can also see you. Once it can, the 180° cone doesn't apply. It's still awake to normal sight, so a deaf monster facing you while you're in the open will wake up. Use it for monsters that should wait in place instead of coming toward the noise.
2. **The sound-blocking linedef flag** (value 64). Sound gets through one of these lines and stops at the second. One flagged line does nothing on its own, so flag a line on each side of the area you want to cut off, for example both sides of a doorway.
3. **Closed doors and zero-height openings.** A line with no vertical gap blocks sound entirely. Sound also isn't re-checked when the door opens later.
4. **Sound targets that stay set.** A sector keeps its sound target after the shooting stops. Monsters that lower, rise or teleport into that sector later wake up right away. This is the usual way to make closet monsters active as soon as they're revealed.
5. **Monster closets with teleport lines.** Put monsters in a sealed sector that sound can reach, for example through a thin sound-only connection, and line it with teleport lines (W1 39, WR 97, or the monster-only 125/126). When you fire somewhere, they wake, walk onto the lines and teleport in. Monsters only teleport when they cross a line from its front side.
6. **Facing direction.** Point monsters away from where you'll enter so you can sneak up on them. Point them toward the entrance if they should react the moment you appear.
7. **Revealing monsters with a trigger.** A door, lowering wall or lift opens to show them. They wake once the newly opened space lets them see or hear you.
8. **REJECT table tricks.** You can edit REJECT so certain monsters never see you from certain sectors. Most modern node builders write an empty REJECT, and some ports ignore it, so this is fragile.

## Support in the level generator (`levels/`)

- `levels/model.py`: adding `"a"` to a `Thing`'s `skills` sets the Ambush flag.
- There's no sound-blocking constant. `model.py` defines only `ML_BLOCKING`, `ML_TWOSIDED`, `ML_DONTPEGTOP`, `ML_DONTPEGBOTTOM` and `ML_SECRET`, so tool 2 isn't available to generated levels yet. Supporting it means adding `ML_SOUNDBLOCK = 64` and a way to put it on shared lines.
