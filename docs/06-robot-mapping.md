# 06 · How the blocks map to the LEGO robot

Two things sit on the table and never touch each other physically:

```
  programming station                         robot
  ┌───────────────────────────┐                ┌────────────────────────────┐
  │ baseplate with blocks     │   Bluetooth    │ LEGO hub running Pybricks  │
  │ camera stand + brain      │ ─────────────▶ │ 2 drive motors + caster    │
  │ RUN / STOP / STEP buttons │ ◀───────────── │ distance sensor (front)    │
  │ speaker, LED ring         │  status, sensors│ colour sensor (down)       │
  └───────────────────────────┘                │ optional 3rd motor (arm)   │
                                               └────────────────────────────┘
```

The blocks describe *what* the robot should do. The brain reads them and sends
a tiny program to the hub. The hub runs it with its own motors and sensors and
reports progress back. The robot can drive anywhere in the room; the baseplate
stays on the table.

## Which LEGO kit, and what it gives us

| Kit | Hub | Ports | Motors in box | Sensors in box | Display | Gyro | Pybricks |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **MINDSTORMS Robot Inventor 51515** | Inventor hub | 6 | 4 medium angular | distance, colour | 5×5 LED matrix | yes | yes |
| **SPIKE Prime 45678** | Prime hub (same hardware) | 6 | 2 medium + 1 large angular | distance, colour, force | 5×5 LED matrix | yes | yes |
| **MINDSTORMS EV3 31313** | EV3 brick (Linux) | 4 motor + 4 sensor | 2 large + 1 medium | colour, touch, infrared (edu: ultrasonic, gyro) | 178×128 LCD | edu only | recent, check status; ev3dev as fallback |
| **SPIKE Essential 45345** | Essential hub | 2 | 2 small | colour | 3×3 LED matrix | yes | yes |
| **Boost 17101** | Move hub | 2 external + 2 built-in motors | 1 external | colour/distance | none (one RGB light) | tilt only | yes |
| **WeDo 2.0** | WeDo smart hub | 2 | 1 | tilt, motion | none | no | **no**: would need its own driver |

The best fit is the Inventor or Prime hub: six ports, a gyro that makes 90°
turns accurate, a matrix that can show the current block number, and first
class Pybricks support. EV3 works too, through Pybricks' newer EV3 support or
the older `ev3dev` Python route, but turns are less accurate without the gyro
and the brick is slower to boot.

## The standard robot build

Every block in version 1 assumes one robot shape: a **driving base**. LEGO
publishes instructions for one in every kit (Robot Inventor: the base used by
"Tricky"; SPIKE Prime: "Driving Base"; EV3: "Educator Vehicle" / "Track3r").

- Two drive motors on fixed ports (left A, right B on Prime/Inventor; B and C on EV3).
- A caster or skid at the back.
- Distance sensor facing forward on a fixed port (for *sees something close*).
- Colour sensor pointing at the floor on a fixed port (for *sees colour*, *dark/bright*).
- Optional third motor for an arm or grabber (*arm up / arm down*).
- Force sensor or touch sensor on the front bumper (*bumped*). The Inventor
  kit has no force sensor; on that hub *bumped* maps to a sharp deceleration
  read from the accelerometer, or the block is simply left out of the set.

The robot's geometry and port map live in one config block at the top of the
hub program, so any build works as long as that block is right:

```python
WHEEL_DIAMETER_MM = 56
AXLE_TRACK_MM     = 112
LEFT, RIGHT, ARM  = Port.A, Port.B, Port.C
DISTANCE, COLOUR  = Port.D, Port.E
UNIT_MM           = 150     # what "forward 1" means
```

### What "forward 1" means

Numbers on the tiles need a physical meaning the child can see. Recommendation:
**a floor mat of squares**, 15 cm each (masking tape on the floor, or a printed
mat like Cubetto's). *Forward 1* is one square, *turn right 1* is a quarter
turn. Then "drive to the cup" becomes a counting problem she can check by
walking it herself. `UNIT_MM` is the square size.

## Block by block

How each block becomes a call in the hub interpreter. Pybricks names are for
the Prime/Inventor hub; the EV3 column notes differences.

| Block | IR | Pybricks (Prime / Inventor) | EV3 notes |
| --- | --- | --- | --- |
| Forward *n* | `forward n` | `base.straight(n * UNIT_MM)` | same (`DriveBase`) |
| Backward *n* | `back n` | `base.straight(-n * UNIT_MM)` | same |
| Turn left / right *n* | `turn dir n` | `base.turn(±90 * n)`, gyro-corrected | wheel odometry unless the edu gyro is fitted |
| Stop | `stop` | `base.stop()` | same |
| Beep *note* | `beep note` | `hub.speaker.beep(freq, 300)` | `ev3.speaker.beep` |
| Light *colour* | `light colour` | `hub.light.on(Color.RED)` | brick status light, limited colours |
| Face *expr* | `face expr` | `hub.display.image(...)` on the 5×5 matrix | draw on LCD |
| Wait *n* | `wait n` | `wait(n * 1000)` | same |
| Arm up / down | `arm dir` | `arm.run_angle(300, ±90)` | same |
| Repeat *n* / forever | `repeat n body` | `for _ in range(n)` / `while True`, checking for STOP between blocks | same |
| If *sensor* / Else | `if cond then else` | evaluate once, run one branch | same |
| Wait until *sensor* | `wait_until cond` | poll every 20 ms | same |

Sensor tiles become conditions:

| Tile | Condition on the hub |
| --- | --- |
| Sees something close | `distance.distance() < 150` (mm) |
| Sees colour X | `colour.color() == Color.X` |
| Bumped | `force.pressed()`, or touch sensor on EV3 |
| Dark / Bright | `colour.ambient()` below / above a threshold |
| Hub shaken / tilted | `hub.imu.acceleration()` magnitude or `hub.imu.tilt()` |

The hub interpreter sends `{"block": i}` as each block starts, shows `i` on
the matrix, and sends `{"done": true}` at the end. STOP from the brain stops
the drive base and all motors immediately, inside any loop.

## Same ideas as the LEGO app

Each physical block has a direct twin in the SPIKE / Robot Inventor app, so
moving to the real app later is a continuation:

| Our block | LEGO app block (word blocks) |
| --- | --- |
| Forward *n* | Move forward for *n* rotations / cm |
| Turn right *n* | Turn right for *n* degrees |
| Beep | Play beep for *n* seconds |
| Light *colour* | Set light to *colour* |
| Face | Show image |
| Wait *n* | Wait *n* seconds |
| Repeat *n* | Repeat *n* |
| If *sensor* | If ⟨sensor⟩ then |
| Wait until *sensor* | Wait until ⟨sensor⟩ |
| Sees something close | Is distance closer than *n* cm? |
| Sees colour | Is colour *X*? |
| Bumped | Is force sensor pressed? |

## A session from the robot's side

1. Child switches the hub on and presses its centre button once. The hub runs
   the stored interpreter program and advertises over Bluetooth.
2. The brain connects (it remembers the hub's name) and both ends show "ready".
3. On RUN the brain sends the IR as one JSON message, then `run`.
4. The hub executes, streaming `block i` messages; the brain speaks and lights
   accordingly. A missing heartbeat for 2 s stops the motors.
5. On `done` the hub shows a smiley and waits for the next program.

## What this means for the open decision

- **Inventor / Prime hub:** everything above works as written. Start here if
  you have it.
- **EV3:** same blocks, same brain; swap the hub program for the EV3 variant,
  accept less precise turns unless you have the gyro, and expect 30 to 60 s of
  brick boot time.
- **Essential or Boost:** a smaller vocabulary (no arm, limited sensors, no
  matrix); still a good fit for a younger child.
