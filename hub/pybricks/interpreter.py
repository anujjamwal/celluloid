# Interpreter for the LEGO SPIKE Prime hub, running Pybricks firmware.
#
# Download once with:   pybricksdev run ble hub/pybricks/interpreter.py
# then press the hub's centre button to start it whenever the hub is on.
#
# Protocol (one JSON object per line, over the Pybricks stdin/stdout link):
#   brain -> hub   {"cmd":"load","program":[...]}   store a program (see brain/language/ir.py)
#                  {"cmd":"run"}                     run it from the start
#                  {"cmd":"step"}                    run the next block only (enters step mode)
#                  {"cmd":"stop"}                    stop motors, abandon the program
#                  {"cmd":"hb"}                      heartbeat; motors stop if none arrives for 2 s while running
#                  {"cmd":"ping"}
#   hub -> brain   {"ev":"ready","blocks":N}  {"ev":"block","src":i}  {"ev":"done"}  {"ev":"stopped"}
#                  {"ev":"error","msg":"..."}  {"ev":"pong"}  {"ev":"waiting"}  (step mode: waiting for next step)
#
# Requires Pybricks 3.5 or later (DriveBase.use_gyro, ForceSensor, display.number).

from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor, ForceSensor
from pybricks.parameters import Port, Direction, Color, Icon
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch
from usys import stdin, stdout
from uselect import poll
import ujson

# ----------------------------------------------------------------- robot config
# Change these to match the build. Ports follow LEGO's SPIKE Prime Driving Base.
WHEEL_DIAMETER_MM = 56
AXLE_TRACK_MM = 112
LEFT, RIGHT = Port.A, Port.E
ARM, DISTANCE, COLOUR, FORCE = Port.C, Port.D, Port.F, Port.B
UNIT_MM = 150            # "forward 1" = one floor square
TURN_DEG = 90            # "turn right 1" = a quarter turn
DRIVE_SPEED = 200        # mm/s
TURN_RATE = 120          # deg/s
ARM_SPEED = 300          # deg/s
ARM_ANGLE = 90           # degrees between "down" and "up"
CLOSE_MM = 150           # "sees something close"
DARK_PCT, BRIGHT_PCT = 10, 60
HEARTBEAT_TIMEOUT_MS = 2000

NOTES = {"low": 262, "mid": 523, "high": 1047}
COLOURS = {"red": Color.RED, "green": Color.GREEN, "blue": Color.BLUE, "yellow": Color.YELLOW, "white": Color.WHITE}
FACES = {"happy": Icon.HAPPY, "surprised": Icon.SURPRISED if hasattr(Icon, "SURPRISED") else Icon.HAPPY, "sleepy": Icon.ASLEEP}


class Stopped(Exception):
    pass


def optional(cls, port, *args):
    try:
        return cls(port, *args)
    except OSError:
        return None


class Robot:
    def __init__(self):
        self.hub = PrimeHub()
        self.left = Motor(LEFT, Direction.COUNTERCLOCKWISE)
        self.right = Motor(RIGHT)
        self.base = DriveBase(self.left, self.right, WHEEL_DIAMETER_MM, AXLE_TRACK_MM)
        self.base.settings(straight_speed=DRIVE_SPEED, turn_rate=TURN_RATE)
        try:
            self.base.use_gyro(True)
        except AttributeError:
            pass
        self.arm = optional(Motor, ARM)
        self.distance = optional(UltrasonicSensor, DISTANCE)
        self.colour = optional(ColorSensor, COLOUR)
        self.force = optional(ForceSensor, FORCE)

    def stop(self):
        self.base.stop()
        if self.arm:
            self.arm.stop()

    def cond(self, c):
        s = c["sensor"]
        if s == "distance_close":
            return self.distance is not None and self.distance.distance() < CLOSE_MM
        if s == "sees_colour":
            return self.colour is not None and self.colour.color() == COLOURS.get(c.get("colour"))
        if s == "bumped":
            return self.force is not None and self.force.pressed()
        if s == "dark":
            return self.colour is not None and self.colour.ambient() < DARK_PCT
        if s == "bright":
            return self.colour is not None and self.colour.ambient() > BRIGHT_PCT
        if s == "shaken":
            x, y, z = self.hub.imu.acceleration()
            return abs((x * x + y * y + z * z) ** 0.5 - 9800) > 4000
        return False


class Link:
    """Line-oriented JSON over the Pybricks stdin/stdout BLE link."""

    def __init__(self):
        self.poller = poll()
        self.poller.register(stdin)
        self.buf = b""

    def send(self, **msg):
        stdout.write(ujson.dumps(msg) + "\n")

    def read(self):
        """Return the next decoded message, or None if nothing is waiting."""
        while self.poller.poll(0):
            ch = stdin.buffer.read(1)
            if not ch:
                break
            if ch == b"\n":
                line, self.buf = self.buf, b""
                if line.strip():
                    try:
                        return ujson.loads(line)
                    except ValueError:
                        self.send(ev="error", msg="bad json")
            else:
                self.buf += ch
        return None


class Interpreter:
    def __init__(self, robot, link):
        self.robot = robot
        self.link = link
        self.program = []
        self.stepping = False
        self.step_credit = False     # the STEP press that started the run also runs block 1
        self.heartbeat = StopWatch()

    # ---- control messages that may arrive while running
    def pump(self):
        """Handle messages that arrived during execution. Raises Stopped on stop."""
        while True:
            msg = self.link.read()
            if msg is None:
                break
            cmd = msg.get("cmd")
            if cmd == "stop":
                raise Stopped()
            if cmd == "hb":
                self.heartbeat.reset()
            elif cmd == "run":
                self.stepping = False
            elif cmd == "step":
                self.stepping = True
                return True
            elif cmd == "ping":
                self.link.send(ev="pong")
        if self.heartbeat.time() > HEARTBEAT_TIMEOUT_MS:
            self.link.send(ev="error", msg="lost brain")
            raise Stopped()
        return False

    def idle(self, ms):
        """Wait while staying responsive to stop/heartbeat."""
        t = StopWatch()
        while t.time() < ms:
            self.pump()
            wait(20)

    def until_done(self):
        while not self.robot.base.done():
            self.pump()
            wait(20)

    def before_block(self, st):
        if self.stepping and self.step_credit:
            self.step_credit = False
        elif self.stepping:
            self.link.send(ev="waiting", src=st.get("src", 0))
            while self.stepping:
                if self.pump():          # a "step" arrived
                    break
                wait(20)
        else:
            self.pump()
        self.link.send(ev="block", src=st.get("src", 0))
        self.robot.hub.display.number(st.get("src", 0))

    # ---- execution
    def run_list(self, program):
        r = self.robot
        for st in program:
            self.before_block(st)
            op = st["op"]
            if op in ("forward", "back"):
                r.base.straight((1 if op == "forward" else -1) * st["n"] * UNIT_MM, wait=False)
                self.until_done()
            elif op == "turn":
                r.base.turn((1 if st["dir"] == "right" else -1) * st["n"] * TURN_DEG, wait=False)
                self.until_done()
            elif op == "stop":
                r.stop()
            elif op == "beep":
                r.hub.speaker.beep(NOTES.get(st.get("note"), 523), 300)
            elif op == "light":
                r.hub.light.on(COLOURS.get(st.get("colour"), Color.WHITE))
            elif op == "face":
                r.hub.display.icon(FACES.get(st.get("expr"), Icon.HAPPY))
                self.idle(800)
            elif op == "wait":
                self.idle(int(st["n"] * 1000))
            elif op == "arm":
                if r.arm:
                    r.arm.run_angle(ARM_SPEED, ARM_ANGLE if st["dir"] == "up" else -ARM_ANGLE, wait=False)
                    while not r.arm.done():
                        self.pump()
                        wait(20)
            elif op == "repeat":
                n = st["n"]
                if n == "forever":
                    while True:
                        self.run_list(st["body"])
                else:
                    for _ in range(int(n)):
                        self.run_list(st["body"])
            elif op == "if":
                self.run_list(st["then"] if r.cond(st["cond"]) else st.get("else", []))
            elif op == "wait_until":
                while not r.cond(st["cond"]):
                    self.pump()
                    wait(20)

    def run(self):
        self.heartbeat.reset()
        self.robot.hub.light.on(Color.GREEN)
        try:
            self.run_list(self.program)
            self.robot.stop()
            self.robot.hub.display.icon(Icon.HAPPY)
            self.robot.hub.light.on(Color.BLUE)
            self.link.send(ev="done")
        except Stopped:
            self.robot.stop()
            self.robot.hub.display.icon(Icon.FALSE)
            self.robot.hub.light.on(Color.ORANGE)
            self.link.send(ev="stopped")
        except Exception as e:  # report instead of dying: the child only sees a stuck robot otherwise
            self.robot.stop()
            self.robot.hub.display.icon(Icon.FALSE)
            self.link.send(ev="error", msg=str(e))
        self.stepping = False

    def main(self):
        self.robot.hub.display.icon(Icon.HAPPY)
        self.robot.hub.light.on(Color.BLUE)
        self.link.send(ev="ready", blocks=0)
        while True:
            msg = self.link.read()
            if msg is None:
                wait(20)
                continue
            cmd = msg.get("cmd")
            if cmd == "load":
                self.program = msg.get("program", [])
                self.link.send(ev="ready", blocks=count(self.program))
            elif cmd == "run":
                self.stepping = False
                self.run()
            elif cmd == "step":
                self.stepping = True
                self.step_credit = True
                self.run()
            elif cmd == "stop":
                self.robot.stop()
                self.link.send(ev="stopped")
            elif cmd == "ping":
                self.link.send(ev="pong")


def count(program):
    n = 0
    for st in program:
        n += 1
        for key in ("body", "then", "else"):
            if key in st:
                n += count(st[key])
    return n


Interpreter(Robot(), Link()).main()
