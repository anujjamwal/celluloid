"""16-LED WS2812 ring around the lens.

Backends, tried in order: rpi_ws281x (Raspberry Pi PWM), spidev (any board
with an SPI bus: Radxa Zero 3W, Orange Pi), console print.
"""
from __future__ import annotations

COLOURS = {"off": (0, 0, 0), "booting": (40, 0, 80), "ready": (0, 0, 120), "flash": (255, 255, 255),
           "thinking": (120, 90, 0), "running": (0, 120, 0), "error": (140, 0, 0), "stepping": (120, 120, 0)}


class Ring:
    def __init__(self, n: int = 16, spi_bus: int = 0, spi_dev: int = 0, gpio_pin: int = 18):
        self.n = n
        self.backend = "console"
        self._strip = None
        self._spi = None
        try:
            from rpi_ws281x import PixelStrip, Color  # type: ignore
            self._strip = PixelStrip(n, gpio_pin, brightness=60)
            self._strip.begin()
            self._Color = Color
            self.backend = "rpi_ws281x"
            return
        except Exception:
            pass
        try:
            import spidev  # type: ignore
            self._spi = spidev.SpiDev()
            self._spi.open(spi_bus, spi_dev)
            self._spi.max_speed_hz = 2_400_000       # 3 SPI bits per WS2812 bit = 1.25 us per bit
            self._spi.mode = 0
            self.backend = "spidev"
        except Exception:
            self._spi = None

    def fill(self, rgb: tuple[int, int, int]) -> None:
        if self._strip is not None:
            for i in range(self.n):
                self._strip.setPixelColor(i, self._Color(*rgb))
            self._strip.show()
        elif self._spi is not None:
            self._spi.xfer3(self._encode([rgb] * self.n))
        else:
            print(f"[ring] rgb{rgb}")

    def show(self, name: str) -> None:
        rgb = COLOURS[name]
        if self.backend == "console":
            print(f"[ring] {name}")
        else:
            self.fill(rgb)

    @staticmethod
    def _encode(pixels: list[tuple[int, int, int]]) -> list[int]:
        """WS2812 GRB bits as SPI bytes: 1 -> 110, 0 -> 100 at 2.4 MHz."""
        bits = []
        for r, g, b in pixels:
            for byte in (g, r, b):
                for i in range(7, -1, -1):
                    bits += [1, 1, 0] if (byte >> i) & 1 else [1, 0, 0]
        bits += [0] * (8 - len(bits) % 8) if len(bits) % 8 else []
        out = [0] * (len(bits) // 8)
        for i, bit in enumerate(bits):
            if bit:
                out[i // 8] |= 1 << (7 - i % 8)
        return out + [0] * 24   # >50 us low = latch
