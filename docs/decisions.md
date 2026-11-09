# Decision log

Short records of choices that shape everything downstream. Newest first.

## 2026-11-09 · Markers are black-on-white, standard ArUco polarity

A white field with black cells on every block, whatever the body colour. Keeps
OpenCV in its default, best-tested mode. Costs a third colour on the top face:
multi-material print, or a laser-printed sticker in a shallow recess.

## 2026-11-09 · Target robot: LEGO SPIKE Prime (45678) + Expansion Set (45681)

**Decision.** The robot is built from SPIKE Prime with the Expansion Set. The
hub runs Pybricks firmware. The brain talks to it over Bluetooth Low Energy
using the Pybricks protocol.

**What we have to work with.**

| Part | Count | Used for |
| --- | --- | --- |
| Prime hub (6 ports, 5×5 matrix, gyro, speaker, Bluetooth) | 1 | runs the interpreter |
| Medium angular motor | 2 | left and right drive wheels |
| Large angular motor | 2 (1 + 1 from expansion) | arm / grabber; spare |
| Distance sensor | 1 | *sees something close*, front |
| Colour sensor | 2 (1 + 1 from expansion) | one facing the floor (*sees colour*, *dark/bright*), one spare |
| Force sensor | 1 | *bumped*, front bumper |

**Consequences.**
- The full version 1 vocabulary is available, including *arm up/down* and
  *bumped*. No blocks need to be dropped.
- Turns use the hub gyro, so *turn right 1* is a reliable quarter turn.
- Progress and faces are shown on the 5×5 matrix.
- Default ports follow LEGO's SPIKE Prime Driving Base instructions; the
  config block at the top of the hub program is the single place to change
  them.
- EV3, Essential and Boost remain possible later through the same driver
  interface but are no longer a design constraint.

## 2026-11-08 · Reader: camera over a baseplate; NFC tap as Plan B

See `02-reading-the-program.md`.

## 2026-11-08 · Blocks are passive 3D prints with ArUco markers

See `03-interaction-design.md` and `04-architecture.md`.
