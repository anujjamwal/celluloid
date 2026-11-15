"""The brain's state machine: boot -> ready -> photograph -> speak -> run.

Hardware (ring, speaker, buttons) is behind small classes with console
fallbacks, so the same loop runs on a laptop with a webcam or a saved photo.

    python -m brain.main --image tests/fixtures/board.jpg --simulate
    python -m brain.main                      # on the Pi, real camera and hub
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

from brain.language import layout, speech
from brain.language.vocabulary import default as vocabulary
from brain.reader.camera import Camera
from brain.reader.grid import GridError, read_board
from brain.ui.buttons import Buttons
from brain.ui.ring import Ring
from brain.ui.speaker import Speaker

# Where the four stand markers sit, in mm, in whatever frame you like.
# Only their relative positions matter. Measure once when the stand is built.
CORNERS_MM = {90: (10.0, 10.0), 91: (270.0, 10.0), 92: (10.0, 270.0), 93: (270.0, 270.0)}


class Brain:
    def __init__(self, camera: Camera, driver, ring: Ring, speaker: Speaker, buttons: Buttons):
        self.camera, self.driver, self.ring, self.speaker, self.buttons = camera, driver, ring, speaker, buttons
        self.last_program = None
        self.last_run_at = 0.0

    async def photograph_and_parse(self):
        self.ring.show("flash")
        image = self.camera.capture()
        self.ring.show("thinking")
        placed = read_board(image, CORNERS_MM, vocabulary().dictionary)
        return layout.parse(placed)

    async def handle(self, button: str):
        if button == "stop":
            await self.driver.stop()
            self.ring.show("ready")
            return
        if button not in ("run", "step"):
            return
        # RUN again within 5 s of a finished run repeats the last program without a photo
        if button == "run" and self.last_program is not None and time.time() - self.last_run_at < 5:
            lay = self.last_program
        else:
            try:
                lay = await self.photograph_and_parse()
            except (layout.LayoutError, GridError) as e:
                self.ring.show("error")
                self.speaker.say(getattr(e, "message", str(e)))
                time.sleep(1.5)
                self.ring.show("ready")
                return
            self.speaker.say(speech.sentence(lay.program))
            self.speaker.say_keys(speech.clip_keys(lay.program))
            for w in lay.warnings:
                print("[warn]", w)
        self.last_program = lay
        await self.driver.load(lay.program)
        self.ring.show("running" if button == "run" else "stepping")
        if button == "run":
            await self.driver.run()
        else:
            await self.driver.step()
        ev = await self.driver.wait_for("done", "stopped", "error", "waiting", timeout=600)
        if ev.get("ev") == "error":
            self.speaker.say("The robot had a problem: " + str(ev.get("msg")))
        self.last_run_at = time.time()
        self.ring.show("ready")

    async def loop(self):
        self.ring.show("booting")
        await self.driver.connect()
        self.ring.show("ready")
        self.speaker.say("Ready.")
        while True:
            b = await asyncio.get_event_loop().run_in_executor(None, self.buttons.wait)
            if b == "quit":
                break
            await self.handle(b)
        await self.driver.close()


class SimDriver:
    """Stands in for the hub: runs the program in brain.drivers.simulator."""
    def __init__(self):
        self.program = []
        self.events: asyncio.Queue = asyncio.Queue()

    async def connect(self): print("[hub] simulated")
    async def close(self): pass
    async def load(self, program):
        self.program = program
        return len(program)
    async def run(self):
        from brain.drivers.simulator import Simulator
        sim = Simulator(on_block=lambda i: print(f"[hub] block {i}"))
        sim.run(self.program)
        print("[hub]", "; ".join(sim.log))
        await self.events.put({"ev": "done"})
    async def step(self): await self.run()
    async def stop(self): await self.events.put({"ev": "stopped"})
    async def wait_for(self, *evs, timeout=0):
        return await self.events.get()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", help="use this photo instead of the camera")
    ap.add_argument("--webcam", type=int, help="use USB webcam N instead of the Pi camera")
    ap.add_argument("--simulate", action="store_true", help="no hub: print what the robot would do")
    ap.add_argument("--clips", help="folder of <key>.wav voice clips")
    args = ap.parse_args(argv)

    camera = Camera(fallback_file=args.image, uvc_index=args.webcam)
    if args.simulate:
        driver = SimDriver()
    else:
        from brain.drivers.pybricks_ble import HubLink
        driver = HubLink(on_event=lambda m: print("[hub]", json.dumps(m)))
    brain = Brain(camera, driver, Ring(), Speaker(Path(args.clips) if args.clips else None), Buttons())
    asyncio.run(brain.loop())


if __name__ == "__main__":
    sys.exit(main())
