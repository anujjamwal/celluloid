# Tangible blocks for LEGO robots

A screen-free way for a child to program a LEGO MINDSTORMS / SPIKE robot by
snapping together 3D-printed blocks, then pressing a big RUN button.

> Working title only. Rename the repo and this file once the name is settled.

## The idea in one paragraph

LEGO's own apps program the robot with Scratch-style blocks on a tablet or
laptop. We keep the blocks but make them physical: each block is a 3D-printed
tile with an icon on top that snaps to its neighbours (and to a LEGO baseplate).
A small "brain" (Raspberry Pi Zero 2 W) reads the arrangement of blocks,
compiles it into a program, and sends it to the LEGO hub over Bluetooth. The
child never touches a screen; feedback comes from lights, sounds and the robot
itself.

![An example program on a baseplate](docs/images/program-layout.svg)

## Status

Concept and interaction-design phase. Nothing is built yet. The documents under
`docs/` are the deliverable for now; code, CAD and firmware come later.

## Documents

| File | What it answers |
| --- | --- |
| [docs/01-vision.md](docs/01-vision.md) | Who this is for, what success looks like, design principles, what already exists |
| [docs/02-reading-the-program.md](docs/02-reading-the-program.md) | The core technical question: how does the brain know which blocks are where? Four options compared, one recommended |
| [docs/03-interaction-design.md](docs/03-interaction-design.md) | What a session feels like for the child, block vocabulary and grammar, feedback without a screen, error handling |
| [docs/04-architecture.md](docs/04-architecture.md) | Brain hardware, software pipeline, robot driver layer (Pybricks / ev3dev), block encoding, printing plan |
| [docs/05-roadmap.md](docs/05-roadmap.md) | Phases, what to build first, and the decisions that are still open |

## Planned repository layout

```
docs/            concept, design, decisions (this phase)
blocks/          block vocabulary spec, marker ID table, icon artwork
hardware/cad/    3D-printable blocks, brain enclosure, camera stand
hardware/pcb/    (only if we ever add electronics to blocks)
brain/           Python that runs on the Raspberry Pi (capture, recognise, compile, send)
hub/             Pybricks MicroPython interpreter that runs on the LEGO hub
tools/           helpers: marker generator, calibration, simulator
```
