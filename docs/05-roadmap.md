# 05 · Roadmap and open questions

## Decisions needed before anything else

1. ~~Which robot?~~ **Settled: SPIKE Prime + Expansion Set** (see `decisions.md`).
2. **How old is she, and does she read yet?** Decides icon-only versus
   icon-plus-word, number tiles versus repeated blocks, and block size.
3. **Printer capabilities.** Single colour with pause-and-swap, or
   multi-material? Decides how markers and icons get their contrast.
4. **Does the brain have to be portable?** The camera-on-a-stand approach
   assumes a table. If programming must happen on the floor next to the robot,
   the NFC wand (option B) moves up the list.

## Phases

### Phase 0 · Paper prototype (1 to 2 weekends, no printing)
- **Ready to print:** `docs/paper/paper-blocks.pdf` (3 pages of 1:1 tiles with
  real markers, plus the stand markers). Run `python tools/paper_tiles.py`
  to regenerate after changing the vocabulary.
- Cut the tiles, use a real baseplate.
- Parent plays the robot. Try 10 small tasks (drive to the cup, draw a square,
  dance). Note which icons confuse, whether REPEAT is understood, whether she
  wants numbers.
- Freeze the version 1 vocabulary from what we learn.

### Phase 1 · Pipeline on a laptop (1 to 2 weekends)
- **Done in code, untested on hardware:** `reader → language → driver`
  exists; the synthetic camera test proves image → markers → mm → program;
  the hub interpreter and the BLE driver are written from the Pybricks
  documentation and still need a real hub.
- Next: photograph the paper tiles with a webcam, run
  `python -m brain.main --image photo.jpg --simulate`, then with the hub.
- Deliverable: a video of the robot moving from a paper program.

### Phase 2 · Real blocks and the brain (3 to 5 weekends)
- Tolerance test prints, then the full version 1 block set and parameter tiles.
- Brain enclosure, camera stand, ring, speaker, buttons on Pi Zero 2 W.
- Voice clips recorded. Boot-to-ready under 30 s, read-only root.
- Deliverable: child uses it alone for a session.

### Phase 3 · Control flow and sensors
- REPEAT brackets, IF/ELSE, WAIT UNTIL, sensor tiles.
- STEP mode with hub matrix progress display.
- Deliverable: a line-following or obstacle-avoiding program built in blocks.

### Phase 4 · Polish and share
- Add NFC tap reader if wanted. Second baseplate support. Second hub family.
- Publish STL/3MF, build guide, firmware image, marker generator.

## Risks and how we handle them

| Risk | Mitigation |
| --- | --- |
| Camera recognition flaky in home lighting | fixed stand, LED ring, matte prints, auto-retake, clear spoken errors; NFC fallback shares all other code |
| 3D-printed LEGO fit too tight or loose | tolerance test plate per printer, tune one parameter |
| Pi boot time kills the mood | leave on a power bank; read-only root; or wake on button |
| Pybricks firmware changes break BLE protocol | pin `pybricksdev` version; the hub interpreter is small and easy to update |
| Vocabulary grows faster than icons stay guessable | one new family at a time, each tested with paper first |
| Child outgrows it | the IR maps one-to-one onto LEGO's own app blocks, so moving to the real app is a continuation, not a restart |
