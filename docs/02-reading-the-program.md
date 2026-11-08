# 02 · Reading the program

Everything else depends on one decision: how does the brain learn which blocks
the child laid out, in what order, with what nesting?

## The four realistic options

### A. Camera over a baseplate (recommended)

The child snaps blocks onto a LEGO baseplate. A camera on a short stand looks
straight down. Each block carries a machine-readable marker (ArUco style, 4×4
cells) next to its icon. On RUN the brain takes one photo, finds every marker,
maps marker centres to the baseplate grid, and reads the program top-to-bottom
with indentation as nesting.

- Blocks: pure plastic, two-colour print (or sticker) for the marker.
- Brain: Pi Zero 2 W + Camera Module 3. ArUco detection on one still image
  takes well under a second.
- Reads 2-D structure natively (repeat bodies, if/else branches, parameters
  beside a block).
- Unlimited vocabulary; a new block type is a new marker ID.
- Risks: lighting and glare, camera alignment, a child's hand in the frame.
  Mitigations: fixed stand clamped to the baseplate, small LED ring around the
  lens, matte filament, retake automatically if the start block is not found.

### B. Tap-to-scan with NFC tags

Each block has a cheap NFC sticker inside (NTAG213, a few cents). The brain is a
hand-held wand with a PN532 reader. The child taps blocks in order, hears each
one named, then presses RUN.

- Simplest, most robust reader; works in any light; blocks stay passive.
- Loses 2-D structure: loops become `REPEAT 3 … END` scanned linearly, which
  KIBO shows is fine for young children but is a step back from Scratch.
- Scanning 15 blocks one by one gets tedious; errors in tap order are invisible.
- Excellent **Plan B** or complement: shares the block vocabulary, compiler and
  robot driver with option A. Only the reader module differs.

### C. Electrical daisy chain

Each block has a tiny microcontroller and spring or magnetic contacts; blocks
pass a token down the chain so the brain learns the order. This is how Project
Bloks, Code Jumper and Robo Wunderkind work.

- Instant feedback (a block can light up when it is reached), no camera, no
  lighting problems.
- Every block needs a PCB, a chip, contacts and power routing. Kid-proof
  connectors are the hard part; contact wear and intermittent faults are
  frustrating to debug and worse to explain to a child.
- Branching (if/else) needs blocks with two outputs and is awkward.
- Right choice for a product team; wrong first step for a one-parent project.
  Keep as a possible version 3.

### D. Slot reader ("punch-card strip")

Blocks form a flat strip the child slides through a slot in the brain; optical
or Hall sensors read a bit pattern of bumps or magnets on each block as it
passes.

- Deeply satisfying physical gesture; blocks fully passive.
- Mechanically fiddly: speed variation, jams, alignment, self-clocking.
- Linear only, like B. Small vocabulary (4 to 5 bits per block).
- Fun side quest, not the main path.

## Comparison

| | A Camera | B NFC tap | C Electrical | D Slot |
| --- | --- | --- | --- | --- |
| Electronics per block | none | sticker | PCB + MCU | none |
| Reads nesting / branches | yes | linear only | partially | linear only |
| Vocabulary size | unlimited | unlimited | unlimited | ~16 to 32 |
| Robustness in child use | medium (lighting) | high | low to medium (contacts) | medium (jams) |
| Build effort for parent | medium | low | high | medium to high |
| Cost per block | ~0.20 € filament | ~0.40 € | ~3 to 5 € | ~0.20 € |
| Time to first robot movement | days | days | weeks | weeks |

## Recommendation

Build **A (camera over baseplate)** as the primary reader. Design the software
so the reader is a swappable module that outputs the same intermediate
representation, so **B (NFC tap)** can be added later for a younger sibling, for
play away from the baseplate, or as a fallback if lighting turns out to be a
daily annoyance.

The next document assumes option A.
