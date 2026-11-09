# 01 · Vision

## Who it is for

One child (age to be confirmed, assume roughly 5 to 9) who has access to LEGO
MINDSTORMS and related LEGO robotics parts, and a parent who does not want to
hand over a laptop or tablet yet. The parent can 3D print, solder and write
firmware.

## What success looks like

- The child can, **without an adult**, build a program of 5 to 15 blocks, run
  it on the robot, see what went wrong, change it and run again.
- The time from "press RUN" to "robot moves" is under 3 seconds.
- A session needs no setup beyond switching two things on (brain and hub).
- The blocks survive being dropped, stepped on and mixed into a LEGO bin.
- Adding a new block type is a one-evening job for the parent: design the tile,
  assign an ID, add one entry to the compiler.

## Design principles

1. **The blocks are dumb.** No electronics, batteries or wires in a block.
   Blocks are pure plastic you can print by the dozen. All intelligence lives
   in one brain unit.
2. **Shape is grammar.** If two blocks fit together, the program is valid.
   The child should never be able to build something that cannot run.
3. **Feedback without a screen.** Lights, sounds and the robot itself tell the
   child what happened. The brain reads the program aloud before running it.
4. **LEGO-compatible.** Blocks snap onto a standard LEGO baseplate and
   accept LEGO parts on top, so the programming surface is just another part of
   the build.
5. **Start tiny, grow with the child.** Version 1 is forward/back/turn/repeat.
   Sensors, conditions and variables come later as separate block families.
6. **One abstraction over the robot.** The brain produces a small
   hub-independent program; a driver layer talks to whatever LEGO hub is on the
   table (SPIKE / Robot Inventor, EV3, Boost, Essential).

## The LEGO landscape we are building on

Facts worth having straight before designing.

- **MINDSTORMS EV3** (2013, set 31313 / education 45544). The brick runs
  Linux. Official programming was LabVIEW-based (EV3 Lab), later Scratch-based
  (EV3 Classroom). The community `ev3dev` Debian image boots from microSD and
  gives SSH plus Python. Pybricks has also been adding EV3 support; check its
  current status before relying on it.
- **MINDSTORMS Robot Inventor** (2020, set 51515). Same hub as **SPIKE Prime**
  (6 ports, 5×5 LED matrix, gyro, Bluetooth Low Energy). LEGO retired the
  MINDSTORMS brand at the end of 2022, but the hub lives on in SPIKE Prime and
  the hardware is fully supported by Pybricks.
- **SPIKE Prime / SPIKE Essential**, **Boost**, **Powered Up** (City and
  Technic) hubs: all BLE, all supported by Pybricks. **WeDo 2.0** is BLE too
  but is not supported by Pybricks and would need its own driver.
- **Pybricks** is an open-source MicroPython firmware for every modern LEGO
  hub. It is the key enabler here: it lets a Raspberry Pi send and run a
  program on the hub over BLE, and lets a running hub program exchange messages
  with the Pi. It is installed through a browser once; the hub keeps it until
  you restore LEGO's firmware.
- The official LEGO apps are Scratch-derived block languages: motion, light,
  sound, events, control (repeat / forever / if), sensors, operators,
  variables. Our vocabulary should feel like a physical subset of that, so the
  child can move to the real app later with nothing to unlearn.

## Prior art (so we steal the right ideas)

| Product / project | How blocks are read | What to take from it |
| --- | --- | --- |
| **Cubetto** (Primo Toys) | Board with 12+4 slots; each block is a resistor the board reads | Shape-coded grammar, a "function" row, no screen, age 3+ |
| **KIBO** (KinderLab) | Wooden blocks with barcodes; the child scans each block with the robot | Scanning is a ritual kids enjoy; passive blocks; proven with 4 to 7 year olds |
| **Tern / Tangible K** (Tufts) | Camera photographs a chain of jigsaw blocks with circular TopCode markers | The approach we recommend: passive blocks, free-form layout, one photo per run |
| **Osmo Coding** | iPad camera plus mirror reads magnet-linked tiles | Number tiles clipped to the side of a command tile as parameters |
| **Google Project Bloks** | Electrical "pucks" on "boards" chained to a brain | Separating base block (connector) from puck (meaning) |
| **Microsoft Code Jumper** | Electrical pods connected by cables, designed for blind children | Audio-first feedback; program read back aloud |
| **LEGO Coding Express** | Coloured action bricks placed on track, read by a sensor on the train | Already LEGO; shows LEGO is comfortable with physical code |
| **Matatalab** | Camera tower looks down on a board of tiles | Fixed camera over a board is a known, shippable form factor |
