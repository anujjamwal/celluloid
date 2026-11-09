# 04 · Architecture

## Overview

```
 child lays out blocks on baseplate
            │
            ▼ photo on RUN
 ┌──────────────────────────────┐          BLE          ┌─────────────────────┐
 │  BRAIN  (Raspberry Pi Zero 2 W)│ ───────────────────▶ │ LEGO hub (Pybricks) │
 │                                │                      │                     │
 │  capture ─▶ recognise ─▶ parse │   compact program    │ resident            │
 │     ─▶ compile ─▶ send         │   + run/stop/step    │ interpreter         │
 │  LED ring · speaker · buttons  │ ◀─────────────────── │ sensor/status msgs  │
 └──────────────────────────────┘                        └─────────────────────┘
```

Three layers that can be developed and tested independently:

1. **Reader** turns the physical world into a list of placed tokens
   (`marker id, grid x, grid y, rotation`). Camera today, NFC tomorrow.
2. **Language** turns placed tokens into a program: grid → statements and
   nesting → validation → an intermediate representation (IR).
3. **Robot driver** turns the IR into something a specific hub runs.

## Brain hardware

| Part | Choice | Why |
| --- | --- | --- |
| Compute | Raspberry Pi Zero 2 W | quad-core 64-bit, built-in BLE and Wi-Fi, runs OpenCV. The original Zero (single core) is too slow for comfortable image work; avoid it. |
| Camera | Raspberry Pi Camera Module 3 (wide) | autofocus, 12 MP, wide lens covers a 256 mm baseplate from ~300 mm height |
| Lights | 16-LED RGB ring (WS2812) around the lens | status display and even illumination of the blocks |
| Sound | I2S amplifier (MAX98357A) + 3 W speaker | voice clips and effects; the Zero has no audio jack |
| Buttons | 3 arcade buttons: RUN (green, 60 mm), STOP (red), STEP (yellow) + power | big, satisfying, unambiguous |
| Power | USB-C power bank or 5 V supply | stationary unit, no battery management to design |
| Storage | 16 GB microSD, read-only root once stable | survives being switched off without shutdown |

Mechanical: a 3D-printed stand clamps to one edge of the baseplate and holds
the camera at a fixed height and angle. Fixed geometry makes the grid mapping a
one-time calibration rather than a per-shot computation.

## Brain software (Python on Raspberry Pi OS Lite)

```
brain/
  reader/
    camera.py        picamera2 still capture, exposure lock, flash via ring
    aruco.py         OpenCV ArUco detection → marker centres in pixels
    grid.py          homography from 4 corner markers on the stand → grid cells
    nfc.py           (later) PN532 tap reader producing the same token list
  language/
    vocabulary.py    marker id → block type, colour, arity
    layout.py        tokens on grid → ordered statements with nesting
    validate.py      shape/grammar checks, child-friendly error messages
    ir.py            intermediate representation (small JSON list)
  drivers/
    pybricks_ble.py  send IR to hub, run/stop/step, receive status
    ev3dev_ssh.py    (if an EV3 is the robot)
    simulator.py     prints what the robot would do; used for tests
  ui/
    ring.py, speaker.py, buttons.py
  main.py            state machine: boot → ready → photograph → speak → run
```

Key libraries: `picamera2`, `opencv-python` (ArUco is in the main module),
`pybricksdev` (BLE download and run of MicroPython programs, and message
exchange with a running program), `bleak` under it, `rpi_ws281x` or `pi5neo`
for the ring, `simpleaudio` or `aplay` for clips.

### Intermediate representation

Small, hub-independent, easy to speak aloud and easy to interpret:

```json
[
  {"op": "forward", "n": 3},
  {"op": "turn", "dir": "right", "n": 1},
  {"op": "repeat", "n": 2, "body": [
      {"op": "forward", "n": 1},
      {"op": "beep", "note": "mid"}
  ]},
  {"op": "if", "cond": {"sensor": "distance_close"}, "then": [
      {"op": "stop"}
  ], "else": []}
]
```

The read-aloud step walks this same tree, so what the child hears is exactly
what will run.

## Robot driver: why a resident interpreter

Two ways to make the hub do things:

- **Compile to MicroPython and download** each time. Simple, but each RUN pays
  a BLE download (1 to 2 s), and STEP mode means a new download per step.
- **Resident interpreter** (recommended): a Pybricks program lives on the hub
  and waits for messages. The brain sends the IR (a few hundred bytes), then
  `run`, `stop`, `step`. The hub sends back `block N started`, sensor values and
  `done`. Fast, STOP is instant, STEP is trivial, and the hub's matrix can show
  progress.

The interpreter is one MicroPython file per hub family:

- `hub/pybricks/interpreter.py` — SPIKE Prime / Robot Inventor / Essential /
  Technic / City / Boost hubs. Robot geometry (wheel diameter, axle track,
  which ports) lives in a small config block at the top so "forward 1" means
  one robot length on any build.
- `hub/ev3dev/interpreter.py` — if the robot is an EV3 running ev3dev; same
  protocol over Bluetooth serial or Wi-Fi.

Transport detail for Pybricks hubs: the hub program reads lines from `stdin`
and writes to `stdout`, which Pybricks carries over its BLE service. The brain
speaks that service directly with `bleak` (`brain/drivers/pybricks_ble.py`).
Each message is one JSON line; the full message list is at the top of
`hub/pybricks/interpreter.py`.

## Block identity encoding (camera)

- **Markers:** ArUco `DICT_4X4_50` or `DICT_4X4_100`. 4×4 markers are robust
  at small sizes and 50 to 100 IDs covers the vocabulary with room to spare.
  Marker size on a 32 mm block: 10 mm square in the top-right corner (clear of
  the notch and the socket); the icon fills the rest. Parameter tiles get an
  8 mm marker. At the planned 2304 px capture width a 10 mm marker is about
  125 px across; ArUco decodes reliably down to roughly 25 px.
- **Marker polarity:** ArUco wants a dark pattern on a light field, so the
  marker is a white 12 mm square (10 mm pattern plus a 1 mm quiet zone) with
  black cells, whatever colour the block body is. The detector runs in its
  default mode; no inverted-marker option.
- **Printing the marker:** three colours meet on the top face (body colour,
  white field, black cells). A multi-material printer does this directly. On a
  single-extruder printer the practical route is a 0.4 mm recess for a
  laser-printed sticker covered with clear tape, or two filament-change pauses
  in the last 0.6 mm (white, then black) if you have the patience. The icon can
  be white in either case.
- **Stand markers:** four fixed markers on the stand corners give the
  homography from image to baseplate millimetres, independent of exact camera
  position.
- **Rotation** from the marker tells us the block orientation; a sideways
  block is reported as an error, not guessed.

## 3D printing plan

- Footprint 4×4 studs (31.8 mm nominal, print at 31.6 to allow tolerance).
  Height 9.6 mm (3 plates) so blocks feel like chunky LEGO bricks.
- Anti-studs underneath tuned per printer: start with LEGO-compatible
  generators (OpenSCAD LEGO libraries exist) and run a tolerance test plate
  before printing a whole set.
- Flat top face (no studs) so the camera always has a clear view of marker
  and icon. Anti-studs underneath only.
- Vertical join: 10 mm wide, 3 mm deep tab on the bottom and matching notch on
  top, offset 3 mm from the left edge so the 16 mm spine shares the same join.
  0.2 mm clearance.
- Parameter socket on the right edge: 12 mm dovetail, 4 mm deep, 0.2 mm
  clearance. Parameter tiles are 16 × 32 mm with the male dovetail.
- Spines: 16 mm wide, 1 to 4 rows (32 to 128 mm) long, same tab and notch.
- The sketches in `docs/images/` are generated by `tools/block_sketches.py`
  from these numbers; change the constants there and regenerate.
- Icons: 0.6 mm raised, so they are tactile and survive paint-free.
- Material: PLA for fit tests, PETG for the final set (tougher, less brittle
  tabs). Matte finish reduces glare for the camera.
- Colours by family (see interaction design): blue motion, purple action,
  orange control, yellow sensor, white parameters, green start.

## Software on the hub side

Pybricks firmware is installed once from a browser at code.pybricks.com
(hold the Bluetooth button while the page flashes it). The interpreter program
is downloaded once with `pybricksdev run ble hub/pybricks/interpreter.py` and
can also be stored as the hub's "start-up" program so switching the hub on
is all a child needs to do.

## Security and safety notes

- The brain exposes no network service by default; Wi-Fi is for the parent's
  SSH during development only.
- Motor commands carry a duration cap so a lost BLE link cannot leave a wheel
  running; the hub interpreter stops all motors if no heartbeat arrives for
  2 s.
