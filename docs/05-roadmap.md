# 05 · Roadmap and open questions

## Decisions needed before anything else

1. **Which robot?** EV3 brick, Robot Inventor / SPIKE Prime hub, or
   something else? This picks the hub driver and the firmware story
   (Pybricks vs ev3dev). It also sets what "Forward 1" means physically.
2. **How old is she, and does she read yet?** Decides icon-only versus
   icon-plus-word, number tiles versus repeated blocks, and block size.
3. **Printer capabilities.** Single colour with pause-and-swap, or
   multi-material? Decides how markers and icons get their contrast.
4. **Does the brain have to be portable?** The camera-on-a-stand approach
   assumes a table. If programming must happen on the floor next to the robot,
   the NFC wand (option B) moves up the list.

## Phases

### Phase 0 · Paper prototype (1 to 2 weekends, no printing)
- Print the block icons on card, cut 32 mm tiles, use a real baseplate.
- Parent plays the robot. Try 10 small tasks (drive to the cup, draw a square,
  dance). Note which icons confuse, whether REPEAT is understood, whether she
  wants numbers.
- Freeze the version 1 vocabulary from what we learn.

### Phase 1 · Pipeline on a laptop (1 to 2 weekends)
- Webcam + printed paper ArUco tiles + Pybricks on the hub.
- `reader → language → driver` working end to end, robot drives from a photo.
- Simulator driver and unit tests for layout and validation.
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
