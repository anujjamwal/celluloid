# 07 · The blocks in LEGO's own app (reference)

What the child will meet when she moves on to the SPIKE App (the same app
serves SPIKE Prime, SPIKE Essential and, in the old MINDSTORMS app, Robot
Inventor). Written from working knowledge of the app; wording may differ
slightly between SPIKE Legacy, SPIKE App 3 and the MINDSTORMS app. Verify
against the app's palette before quoting it in materials for her.

## Two languages in one app

**Icon Blocks** (SPIKE Essential first, also available on Prime). Horizontal
strips read left to right, pictures only, no text. Parameters are picked from
small pop-ups (a number, a colour, a direction). Aimed at ages 6 to 8. This is
the closest thing LEGO ships to what we are building, so it is our first
reference for icons and for what a non-reader can handle.

**Word Blocks**. Vertical Scratch 3 stacks with text. Aimed at ages 10+.
This is what most tutorials and FIRST LEGO League teams use.

**Python** is the third step; Pybricks is a parallel Python route that we
happen to use on the hub.

## Word Blocks palette

| Category | Blocks (parameters in brackets) |
| --- | --- |
| **Motors** | run [A] (clockwise) for (1) [rotations / degrees / seconds] · go to position (0) · start motor · stop motor · set speed to (75) % · position · speed |
| **Movement** | set movement motors to [A+B] · move (forward) for (10) [cm / in / rotations / degrees / seconds] · start moving (forward) · move (steering) for (10) cm · start moving (steering) · stop moving · set movement speed to (50) % · set 1 motor rotation to (17.5) cm moved |
| **Light** | turn on [5×5 image] for (2) seconds · turn on [image] · write [Hello] · turn off pixels · set pixel (x)(y) to (100) % · set pixel brightness · set orientation / rotate orientation · set Center Button light to [colour] · distance sensor lights |
| **Sound** | play sound [Cat Meow] until done · start sound · beep (60) for (0.2) seconds · start beep · stop all sounds · set / change pitch effect · set / change volume |
| **Events** (hats) | when program starts · when [left] button pressed · when hub [shaken / tapped / falling] · when hub orientation is [front] · when [colour sensor] sees [red] · when [distance] closer than (15) cm · when [force] is pressed · when timer > (10) · when I receive [message] · broadcast [message] |
| **Control** | wait (1) seconds · wait until ⟨⟩ · repeat (10) · forever · if ⟨⟩ then · if ⟨⟩ then / else · repeat until ⟨⟩ · stop [all / this stack / other stacks] |
| **Sensors** | is [colour] colour [red]? · colour · is reflected light [<] (50) %? · reflected light · is [force] [pressed / hard-pressed / released]? · pressure % · is [distance] [closer than] (15) [cm]? · distance · is hub [button] pressed? · is hub [shaken / tapped / falling]? · is hub orientation [front]? · pitch / roll / yaw angle · set yaw to 0 · timer · reset timer |
| **Operators** | + − × ÷ · pick random · < = > · and · or · not · join · letter of · length · mod · round · maths functions |
| **Variables** | make a variable · set / change · show / hide · lists |
| **My Blocks** | define custom blocks with inputs |
| Extensions | Music · More Motors · More Movement · More Sensors · Weather · Line Graph · Display |

SPIKE App 3 trimmed the Movement category (duplicate power settings moved
into Motors) and dropped a few Light blocks; SPIKE Legacy and the MINDSTORMS
app have the fuller list.

## How our version 1 blocks line up

| Ours | Icon Blocks | Word Blocks |
| --- | --- | --- |
| START | the play arrow at the left of a strip | when program starts |
| Forward / Backward *n* | move forward / backward (duration picker) | move (forward) for (n) cm |
| Turn left / right *n* | turn (direction) | move (steering) for … / run motor … |
| Stop | stop | stop moving |
| Beep *note* | play sound | beep (60) for (0.2) seconds |
| Light *colour* | light (colour) | set Center Button light to [colour] |
| Face *expr* | show image | turn on [image] |
| Wait *n* | wait | wait (n) seconds |
| Arm up / down | motor run | run [C] for (90) degrees |
| Repeat *n* / forever | repeat (loop strip) | repeat (n) / forever |
| If *sensor* / Else | (not in Icon Blocks) | if ⟨⟩ then / else |
| Wait until *sensor* | wait until event | wait until ⟨⟩ |
| Sees something close | distance sensor event | is [distance] closer than (15) cm? |
| Sees colour | colour sensor event | is [colour] colour [red]? |
| Bumped | force sensor event | is [force] pressed? |
| Shaken | hub shaken event | is hub shaken? |
| Dark / Bright | (none) | is reflected light < 50 %? (approximate) |

What we deliberately leave out of version 1: motor-level control, steering
values, operators, variables, broadcasts, custom blocks, and the hub's yaw
and timer. Each is a later family if she wants it, and each has a word block
waiting for her in the real app.

## What this tells the design

- Our blocks are a physical Icon-Blocks layer with Word-Blocks structure
  (vertical stacks, nesting). That is the right bridge: pictures for now,
  shape that already matches what she will see on a screen later.
- Icon Blocks have no if/else. If the paper test shows IF is too early, drop
  it without guilt; LEGO did the same for that age.
- LEGO's distance condition defaults to 15 cm and its movement unit is cm;
  our "close" threshold and floor squares should feel the same in practice.
