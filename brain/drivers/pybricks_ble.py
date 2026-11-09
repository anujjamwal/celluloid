"""Talk to the hub interpreter over Bluetooth Low Energy.

Uses the Pybricks GATT service directly through bleak, so there is no
dependency on pybricksdev at run time (pybricksdev is still the easiest way to
download hub/pybricks/interpreter.py to the hub in the first place).

Pybricks protocol essentials (see pybricks.com/technical-info):
  service  c5f50001-8280-46da-89f4-6d8051e4aeef
  command  c5f50002-8280-46da-89f4-6d8051e4aeef   write: [0x06] + stdin bytes
                                                   notify: [0x01] + stdout bytes, [0x00] + status flags
Messages to and from the hub are JSON lines (hub/pybricks/interpreter.py).

Not yet exercised against a real hub: written from the protocol documentation.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any, Awaitable, Callable

try:
    from bleak import BleakClient, BleakScanner
except ImportError:  # keeps the language tests importable without bleak
    BleakClient = BleakScanner = None  # type: ignore

PYBRICKS_SERVICE = "c5f50001-8280-46da-89f4-6d8051e4aeef"
PYBRICKS_COMMAND = "c5f50002-8280-46da-89f4-6d8051e4aeef"
CMD_WRITE_STDIN = 0x06
EVT_STATUS = 0x00
EVT_STDOUT = 0x01
STATUS_PROGRAM_RUNNING = 1 << 6

Program = list[dict[str, Any]]
Handler = Callable[[dict[str, Any]], Awaitable[None] | None]


class HubLink:
    def __init__(self, name_prefix: str = "Pybricks", on_event: Handler | None = None):
        self.name_prefix = name_prefix
        self.on_event = on_event
        self.client: BleakClient | None = None
        self.buf = b""
        self.program_running = False
        self.events: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._hb_task: asyncio.Task | None = None

    # ---- connection
    async def connect(self, timeout: float = 15.0) -> None:
        if BleakScanner is None:
            raise RuntimeError("bleak is not installed")
        device = await BleakScanner.find_device_by_filter(
            lambda d, ad: PYBRICKS_SERVICE in (ad.service_uuids or []) and (d.name or "").startswith(self.name_prefix),
            timeout=timeout)
        if device is None:
            raise TimeoutError("no Pybricks hub found; is it on, and is the interpreter running?")
        self.client = BleakClient(device)
        await self.client.connect()
        await self.client.start_notify(PYBRICKS_COMMAND, self._notify)

    async def close(self) -> None:
        self.stop_heartbeat()
        if self.client:
            await self.client.disconnect()
            self.client = None

    def _notify(self, _sender, data: bytearray) -> None:
        if not data:
            return
        if data[0] == EVT_STATUS and len(data) >= 5:
            flags = int.from_bytes(data[1:5], "little")
            self.program_running = bool(flags & STATUS_PROGRAM_RUNNING)
        elif data[0] == EVT_STDOUT:
            self.buf += bytes(data[1:])
            while b"\n" in self.buf:
                line, self.buf = self.buf.split(b"\n", 1)
                if line.strip():
                    try:
                        msg = json.loads(line)
                    except ValueError:
                        msg = {"ev": "garbage", "raw": line.decode(errors="replace")}
                    self.events.put_nowait(msg)
                    if self.on_event:
                        res = self.on_event(msg)
                        if asyncio.iscoroutine(res):
                            asyncio.ensure_future(res)

    # ---- messages
    async def send(self, **msg: Any) -> None:
        assert self.client is not None, "not connected"
        payload = (json.dumps(msg, separators=(",", ":")) + "\n").encode()
        # BLE writes are limited by the MTU; 20 bytes is safe on every hub
        for i in range(0, len(payload), 20):
            await self.client.write_gatt_char(PYBRICKS_COMMAND, bytes([CMD_WRITE_STDIN]) + payload[i:i + 20], response=True)

    async def wait_for(self, *events: str, timeout: float = 30.0) -> dict[str, Any]:
        while True:
            msg = await asyncio.wait_for(self.events.get(), timeout)
            if msg.get("ev") in events:
                return msg

    # ---- high level
    async def load(self, program: Program) -> int:
        await self.send(cmd="load", program=program)
        ready = await self.wait_for("ready", timeout=10)
        return int(ready.get("blocks", 0))

    async def run(self) -> None:
        await self.send(cmd="run")
        self.start_heartbeat()

    async def step(self) -> None:
        await self.send(cmd="step")
        self.start_heartbeat()

    async def stop(self) -> None:
        await self.send(cmd="stop")
        self.stop_heartbeat()

    def start_heartbeat(self, period: float = 0.5) -> None:
        if self._hb_task is None or self._hb_task.done():
            self._hb_task = asyncio.ensure_future(self._heartbeat(period))

    def stop_heartbeat(self) -> None:
        if self._hb_task:
            self._hb_task.cancel()
            self._hb_task = None

    async def _heartbeat(self, period: float) -> None:
        try:
            while True:
                await self.send(cmd="hb")
                await asyncio.sleep(period)
        except asyncio.CancelledError:
            pass


async def demo(program: Program) -> None:
    """python -m brain.drivers.pybricks_ble  (runs a tiny program on the hub)"""
    link = HubLink(on_event=lambda m: print("hub:", m))
    await link.connect()
    try:
        n = await link.load(program)
        print(f"loaded {n} blocks")
        await link.run()
        await link.wait_for("done", "stopped", "error", timeout=120)
    finally:
        await link.close()


if __name__ == "__main__":
    asyncio.run(demo([{"op": "beep", "note": "mid", "src": 1}, {"op": "forward", "n": 1, "src": 2},
                      {"op": "turn", "dir": "right", "n": 1, "src": 3}]))
