# Monster alerting in DOOM II

In vanilla DOOM II a sleeping monster runs `A_Look` every few tics. It wakes up in one of three ways: it **sees** you, it **hears** you, or it **gets hurt**. Each map tool below changes one of those three.

## How monsters wake up

| Trigger | Rule |
|---|---|
| **Sight** | The monster needs a clear line of sight inside a 180° cone in front of it, so a monster facing away won't notice you. The exception is when you're within 64 units of it (melee range), where it notices you from any direction. The REJECT lump can also rule out sight between two sectors. |
| **Sound** | Firing any weapon, including the fist, alerts monsters through sound. The noise floods outward from your sector through every two-sided line with an opening, bars and railings included: a line's impassable flag doesn't stop sound, only a zero-height opening does. Every sector it reaches remembers you as its sound target, and sleeping monsters in those sectors wake on their next look. |
| **Damage** | A monster that gets hurt by anything (your shot, splash damage, another monster) wakes up and goes after the attacker. |

Sound comes only from weapon fire. Doors, lifts, item pickups, footsteps and monster noises don't wake anyone.

## Tools for controlling alerting

1. **The Ambush thing flag**, often mislabeled "deaf". A monster with this flag that hears you wakes only if it can also see you, but that sight check has no cone: once it has heard you, any line of sight wakes it, whichever way it faces. Before you fire it's an ordinary sleeper, woken by sight in its cone. Use it for monsters that should wait in place instead of coming toward the noise from out of view.
   - **In an open space it does almost nothing.** Your first shot floods the whole space, and every ambush monster with any view of you wakes at once, facing away or not. In MAP09 the lake's island monsters were all ambush and faced away from the dam, yet the first shots on the shelves above woke every one that could see up the cascade; they walked to the foot of the dam and waited under the drop in a clump. Facing away protects only until the first shot. To keep an open area asleep, cut its sound off (tool 2).
2. **The sound-blocking linedef flag** (value 64). Sound crosses one flagged line and stops at the second, so it takes two flagged lines in series to cut an area off. Flag a line on each side of a doorway, or shield an area inside an open space:
   - Flag the lines where the noise comes in (MAP09: the dam's lip, between the shelves and the lake) and the outline of each area to keep quiet (MAP09: every island in the lake). Noise from above crosses the lip once, reaches the open lake (the Cyberdemon there hears you coming) and stops at the islands.
   - It's one-way in effect: a shot fired inside the open lake reaches the islands, because it crosses only their outline. So the islands wake when you fight in the lake, not before.
3. **Closed doors and zero-height openings.** A line with no vertical gap blocks sound entirely. Sound also isn't re-checked when the door opens later.
4. **Sound targets that stay set.** A sector keeps its sound target after the shooting stops. Monsters that lower, rise or teleport into that sector later wake up right away, and an ambush monster there wakes whenever it next gets a line of sight to you. This is the usual way to make closet monsters active as soon as they're revealed.
5. **Monster closets with teleport lines.** Put monsters in a sealed sector that sound can reach, for example through a thin sound-only connection, and line it with teleport lines (W1 39, WR 97, or the monster-only 125/126). When you fire somewhere, they wake, walk onto the lines and teleport in. Monsters only teleport when they cross a line from its front side.
6. **Facing direction.** Point monsters away from where you'll enter so you can sneak up on them. Point them toward the entrance if they should react the moment you appear.
7. **Revealing monsters with a trigger.** A door, lowering wall or lift opens to show them. They wake once the newly opened space lets them see or hear you.
8. **REJECT table tricks.** You can edit REJECT so certain monsters never see you from certain sectors. Most modern node builders write an empty REJECT, and some ports ignore it, so this is fragile.

## Hearing monsters

The Cyberdemon's and the Spider Mastermind's sight and death sounds play at full volume wherever you are (`A_Look` and `A_Scream` start them with no origin); every other monster's sounds come from where it stands and fade with distance. So you hear a boss wake from anywhere on the map. In MAP09 the Cyberdemon, deaf and facing away, wakes when you fire from a spot he can see (the balcony rail, the near side of shelf 3), and players hear him while still coming down the shelves, before they've seen more than a speck of him. A sound you can't place builds dread better than a clear view.

## After waking: when a monster attacks

A monster attacks only along a line of sight, and its chance to fire falls off with distance. The arch-vile won't start its attack at all from more than about 1,088 units away (`P_CheckMissileRange`). So an arch-vile can be put in plain view at a distance, awake, and still give you time to take cover while it closes in: MAP09's stands in the exit alcove at the back of the dome, about 1,500 units from where you land in the lake, in view through the hatch.

## Support in the level generator (`levels/`)

- `levels/model.py`: adding `"a"` to a `Thing`'s `skills` sets the Ambush flag.
- `ML_SOUNDBLOCK` (from `levels/model.py`) goes on lines through `OVERRIDES`, whose `flags` replaces the line's whole flags word: give the flags the builder would have set plus `ML_SOUNDBLOCK` (two-sided `ML_TWOSIDED`; a railing also `ML_BLOCKING | ML_DONTPEGBOTTOM`). MAP08's windows and MAP09's dam and islands do this.
- The build doesn't model sound: no check catches a crowd of ambush monsters woken by one shot. Test it in the engine: fire from a spot on the route and see which monsters move.
