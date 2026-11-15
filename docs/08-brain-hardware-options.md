# 08 · Brain hardware: bare Pi, Coral, or AI HAT

Prices are list prices in USD as of November 2026 and vary by country; street
prices for Coral parts are often higher because of scarcity.

## What the brain actually has to do

| Workload | Needs an accelerator? |
| --- | --- |
| Read the board: one ArUco pass on a 2304 px still | No. Classical CV, well under a second on any Pi. |
| Speak pre-recorded clips | No. Any Pi. |
| Neural text-to-speech (Piper) | No, but CPU speed matters: slow on Zero 2 W, instant on Pi 5. |
| Hear "run" / "stop" / a wake word (Vosk, openWakeWord, whisper.cpp tiny) | No. Marginal on Zero 2 W, comfortable on Pi 5. |
| Markerless icon recognition (small CNN, one shot) | No. Pi 5 CPU does it in tens of ms; Zero 2 W in a few hundred. |
| Live tracking of blocks at 10 to 15 fps | Pi 5 CPU is enough; an NPU helps if you add a detector. |
| A local language model (a talking helper: "why did my robot turn the wrong way?") | Pi 5 with 8 GB can run a 1B model on CPU at a few tokens/s. The AI HAT+ 2 runs 1 to 1.5B models on its own NPU and memory, faster and with the CPU free. |
| A local vision-language model ("what do you see?") | AI HAT+ 2 territory, and still early. |

## The boards

| | Pi Zero 2 W | Pi 5 (4 GB) | Pi 5 + AI HAT+ (Hailo-8L / 8) | Pi 5 + AI HAT+ 2 (Hailo-10H) | Pi 5 + Coral USB |
| --- | --- | --- | --- | --- | --- |
| Board cost | $15 | $60 (2 GB $50, 8 GB $80) | $60 + $70 / $110 | $80 (8 GB Pi) + $130 | $60 + ~$60 list, often $100+ |
| Brain total with camera, ring, speaker, buttons, power | ~$90 | ~$140 | ~$210 / $250 | ~$290 | ~$220 |
| Compute | 4× A53 1 GHz, 512 MB | 4× A76 2.4 GHz, 4 GB | + 13 / 26 TOPS INT8, no own memory | + 40 TOPS INT4, 8 GB own memory | + 4 TOPS INT8 |
| Board-read latency | 0.3 to 0.5 s | < 0.1 s | same as Pi 5 (not used) | same | same |
| Boot to ready | ~25 to 30 s | ~12 to 15 s | ~15 s | ~15 s | ~15 s |
| Power | 1.5 to 2.5 W, runs from a power bank | 5 to 8 W, needs the 27 W supply | + 2 to 4 W | + up to 5 W peak | + 2 W |
| Neural TTS | several seconds per sentence | real time | real time (CPU) | real time, Whisper STT can run on the NPU | CPU only |
| Local LLM | no | 1B at a few tokens/s, 8 GB model recommended | no (no memory on the chip) | yes, officially Llama 3.2 1B, Qwen 2.5 1.5B, DeepSeek-R1 1.5B | no |
| Software health | Raspberry Pi OS, first party | first party | Hailo runtime, first-party Pi support | Hailo runtime, first-party Pi support, newest | pycoral frozen on Python 3.9, Docker workarounds, no updates in years |
| Fits our enclosure? | smallest | HAT-sized footprint | adds ~20 mm height, GPIO passes through on a stacking header | same | USB dongle hanging off the side |
| Verdict | enough for version 1, dead end for voice | the sweet spot | vision-only; wrong tool for a talking helper | the one accelerator worth buying, later | avoid for a new project |

Two other parts worth knowing about:

- **Raspberry Pi AI Camera** (Sony IMX500, $70). Runs a small vision model
  on the sensor itself and hands the Pi results, so it works even with a Zero
  2 W. Only interesting if we ever want markerless blocks on a Zero. ArUco
  makes it unnecessary.
- **Cloud models over Wi-Fi.** Far more capable than anything local, costs
  cents, but needs internet in the play room and sends a child's voice and
  photos off the device. A reasonable later option, as an explicit opt-in, not
  the default.

## Pi Zero-sized alternatives: Radxa Zero 3W and Orange Pi Zero 3W

Worth a look because the Pi Zero 2 W has been sold out for much of 2026 and
has only 512 MB of RAM, which is tight for OpenCV plus Bluetooth plus speech.

| | Pi Zero 2 W | Radxa Zero 3W | Orange Pi Zero 3W | Orange Pi Zero 2W |
| --- | --- | --- | --- | --- |
| SoC | BCM2710, 4× A53 1.0 GHz | Rockchip RK3566, 4× A55 1.6 GHz | Allwinner A733, 2× A76 + A55 cores, 2.0 GHz | Allwinner H618, 4× A53 1.5 GHz |
| RAM | 512 MB | 1 / 2 / 4 / 8 GB LPDDR4 | 1 to 16 GB LPDDR5 | 1 to 4 GB LPDDR4 |
| NPU | none | 0.8 TOPS (small CNNs via RKNN, no LLMs) | 3 TOPS (claimed; toolchain new) | none |
| Storage | microSD | microSD + optional eMMC (survives power cuts better than SD) | microSD + optional eMMC / UFS | microSD + optional eMMC |
| Camera | 22-pin CSI, Pi camera modules just work via picamera2 | 22-pin 4-lane CSI; only the sensors Radxa lists, Camera Module 3 is not among them | 2× 4-lane CSI; driver stack brand new | no CSI; USB webcam only |
| Wireless | Wi-Fi 4, BT 4.2 | Wi-Fi 6, BT 5.4 | Wi-Fi 6, BT 5.4 | Wi-Fi 5, BT 5.0 |
| USB | 1× micro-USB 2.0 OTG | USB 3.0 host + USB 2.0 OTG (Type-C) | USB 3.1 OTG + USB 2.0 (Type-C) | 2× Type-C 2.0 |
| Price | $15 list, scarce | ~$15 to 35 (1 GB) up to ~$100 (8 GB) depending on region; availability patchy | $25 claimed for 1 GB, realistically $55+ for 4 GB; launched April 2026 | $15 to 30 |
| Board-read estimate | 0.3 to 0.5 s | 0.15 to 0.25 s | under 0.1 s | 0.25 to 0.4 s |
| Neural TTS (Piper) | several seconds a sentence | about real time, usable for short phrases | real time, Pi 5 class | slow |
| Local 1B LLM | no | no | possible on CPU with 8 GB, like a Pi 5 | no |
| Software maturity | Raspberry Pi OS, picamera2, gpiozero, rpi_ws281x: everything in this repo runs as is | RK3566 is well supported (Radxa OS, Armbian, near-mainline kernel); GPIO via libgpiod or mraa, LED ring via SPI, BLE via BlueZ works | new SoC: vendor kernel, immature camera, ISP and NPU stacks; expect rough edges for a year or more | H618 is reasonably supported by Armbian; no camera path other than USB |

What changes on a non-Raspberry board:

- **Camera:** use a USB UVC webcam with autofocus (a 1080p autofocus module
  is $20 to 30, a Logitech C920-class webcam $50 to 70) instead of a CSI
  module. OpenCV reads it the same way everywhere, and the camera driver
  question disappears. `brain/reader/camera.py` supports both.
- **LED ring:** drive WS2812 over SPI (`spidev`) rather than the Pi PWM
  library.
- **Buttons:** `gpiod` instead of `gpiozero`.
- **Bluetooth:** `bleak` on BlueZ works on all of them, but test the specific
  Wi-Fi/BT module early: BLE stability is the one thing this project cannot
  live without.

### Checked: the Radxa Zero 3W camera path (November 2026)

- **Supported sensors** per Radxa's docs: Raspberry Pi Camera V1.3 (OV5647),
  Raspberry Pi Camera V2 (IMX219) and Radxa's own Camera 8M 219 (IMX219).
  Not supported: Camera Module 3 (IMX708) or any autofocus module.
- **How it works:** enable the camera overlay with `rsetup`, reboot, then the
  camera is a plain V4L2 device at `/dev/video0` delivering NV12 (Radxa's
  example captures 1920×1080 with GStreamer). OpenCV's `VideoCapture` reads
  that directly, so `brain/reader/camera.py` works unchanged through its UVC
  path with `--webcam 0`. ArUco does not care about the ISP.
- **Community record is mixed.** On the forum the 8M camera worked on
  Radxa's Debian image only with kernel 5.10.160-26; a later 5.10.160-38 and
  Armbian's 6.1 vendor kernel did not. Several owners found the CSI connector
  on early boards assembled inverted and fixed it by flipping the cable or the
  connector latch. Radxa's IMX219 cable pinout also differs from the Pi's, so
  use Radxa's cable, not a Pi one.
- **Optics:** IMX219 modules are fixed focus set around 1 m. At the 30 to
  40 cm stand height the lens must be twisted a quarter turn (the Pi V2
  module allows this) or the image is soft. 3280 px across 270 mm gives
  12 px/mm, more than enough.
- **Verdict:** workable, with a weekend of risk: pin the kernel Radxa's docs
  recommend, buy Radxa's 8M camera and cable, test on day one. A USB
  autofocus webcam removes all of that and costs the same.

### Checked: the Allwinner A733 NPU (Orange Pi Zero 3W)

- **What it is:** a Vivante VIP9000-series NPU rated 3 TOPS INT8. It is a
  real, usable unit on Linux: Radxa's Cubie A7 boards (same SoC) document the
  flow, with YOLOv8n at about 79 fps and YOLO11s-pose at about 31 fps at
  640×640.
- **How you use it:** models are converted on an x86 PC inside a vendor
  Docker image (ACUITY toolkit, exported to a "NBG" binary), then run on the
  board through the VIPLite / awnn C runtime. Python access is through
  wrapping the C demo. Compared with Hailo's or even Rockchip's RKNN tooling
  this is the least friendly flow of the three.
- **On the Orange Pi Zero 3W specifically:** reviewers report that Orange
  Pi's stock images ship without GPU and video-engine userspace, image
  download links were empty at launch, and mainline kernel support for the
  A733 is still incomplete. Nobody has published an NPU or camera result on
  this board yet; the working examples are on Radxa's A733 boards.
- **Does it help this project?** No, and that is a property of the project
  rather than the chip. Reading markers is not a neural network, so an NPU
  cannot touch it. The one neural task on the roadmap, a markerless icon
  classifier, is a tiny model the A733's A76 cores run in a few
  milliseconds; the NPU would save power, not time. Language and
  vision-language models are beyond 3 TOPS without on-chip memory. The
  A733's attraction here is its CPU, not its NPU.
- **Verdict:** a promising compact board whose software is six months old.
  If you want it, start from Radxa's Cubie A7Z documentation and images,
  which are the most complete A733 stack, and expect to do kernel and
  userspace work that Raspberry Pi owners never see.

Verdict on the class: these compete with the Zero 2 W for the budget or compact build,
not with the Pi 5 for the main build. **Radxa Zero 3W with 4 GB** is the
safe pick in that class today: mature kernel, eMMC, eight times the RAM of
the Pi Zero, and Piper speech becomes usable. **Orange Pi Zero 3W** has Pi 5
class CPU in a Zero footprint and would be the ideal compact board once its
software settles; revisit it in 2027 rather than debugging a vendor kernel
with a child waiting. **Orange Pi Zero 2W** only if price is everything.

## The A733 class: Orange Pi Zero 3W and Radxa Cubie A7Z

Same Allwinner A733 (2× Cortex-A76 + 6× Cortex-A55, 3 TOPS NPU), same
65 × 30 mm footprint, two vendors. If this class is worth exploring, the
question is which board, and the answer is Radxa's.

| | Orange Pi Zero 3W | Radxa Cubie A7Z |
| --- | --- | --- |
| RAM | 1 to 16 GB LPDDR5 | 1 to 16 GB LPDDR4x |
| Storage | microSD, optional eMMC or UFS | microSD, optional UFS |
| Camera | 2× 4-lane CSI; no documented sensor support yet | 1× 4-lane CSI (v1.1), 2× on v2.0; sensor list not published either |
| Wireless | Wi-Fi 6, BT 5.4, chip not named | Wi-Fi 6, BT 5.4, external antenna connector |
| PCIe | Gen 3 ×1 on FPC | Gen 3 ×1 on FPC (NVMe works with some drives) |
| Price | $25 claimed (1 GB); ~$56 for 4 GB on AliExpress | $19 to 35 for 1 GB; ~$62 for 2 GB at US resellers; often out of stock |
| Idle / load power (reviews) | 2 to 3 W / 6.6 to 7 W | 1.9 to 2.0 W / 3.9 to 4.5 W, with a heatsink |
| Thermals | reviewers used active cooling at 50 °C under stress | passive heatsink: 52 °C idle, under 70 °C in a 10 min stress test |
| Software | Orange Pi images missing GPU/VPU userspace at launch, no NPU or camera results published, download links empty for weeks | Radxa OS (Debian) with working GPU and Vulkan, documented ACUITY NPU SDK and YOLO model zoo for the A733, the same docs tree as the Cubie A7A/A7S |
| Community | thin | Radxa forum and docs; the one public A733 NPU project runs on this board |

Two things the numbers settle:

- **Power is not Radxa Zero 3W class.** The A76 cores cost roughly 2 W idle
  and 4 to 7 W under load, which is Pi 5 territory under load and double the
  Zero 3W at idle. Still power-bank feasible, but the "small and frugal"
  advantage mostly belongs to the RK3566 board, not to the A733 ones.
- **Same chip, different software.** The Orange Pi's problems are all
  software and documentation, and Radxa ships the same SoC with the stack
  the Orange Pi lacks. There is no reason to take the Orange Pi's risk to
  get this chip.

Where the A733 class sits for this project: compute between a Pi 4 and a Pi
5 in a Zero footprint, so neural speech for everything the brain says is
comfortable, and with 8 GB a 1B language model runs on the CPU at a few
tokens per second. The NPU remains irrelevant to marker reading and only
useful if we ever add a camera-based detector, where Radxa's model zoo makes
it reachable. Software is still six months old: expect the vendor 5.15 kernel,
no mainline, and camera sensor support to be discovered rather than read.

## Head to head: Pi 5 versus Radxa Zero 3W

Size and power are real differences; "equally capable" is not. Numbers are
typical, not measured by us yet.

| | Pi 5 (4 GB) | Radxa Zero 3W (4 GB) |
| --- | --- | --- |
| Board | 85 × 56 mm, 17 mm tall with the active cooler, 45 g | 65 × 30 mm, 8 mm tall, 15 g |
| Idle power | ~2.7 W | ~1 W |
| Working power (our bursts) | 5 to 8 W | 2.5 to 3.5 W |
| Supply | 5 V / 5 A official; a 5 V / 3 A supply works with USB current capped | 5 V / 2 A; runs from any power bank |
| CPU | 4× Cortex-A76 at 2.4 GHz | 4× Cortex-A55 at 1.6 GHz: roughly a quarter of the Pi 5 per core, about a Pi 3B+ to Pi 4 overall |
| RAM | 4 GB | 4 GB |
| Storage | microSD (NVMe via HAT) | microSD or on-board eMMC |
| Board read, 2304 px still | < 0.1 s | 0.15 to 0.25 s |
| Piper neural voice, one sentence | ~0.2 s | 1 to 2 s with a "low" voice, longer with "medium": fine for one sentence, sluggish for a whole program read-back |
| Voice commands ("stop") | whisper.cpp tiny, comfortable | Vosk small model, workable; whisper too slow |
| Local 1B language model | a few tokens/s on CPU, more with an AI HAT+ 2 | no |
| Add-on path | AI HAT+ 2 over PCIe | none (0.8 TOPS NPU, CNNs only) |
| Camera | any Pi camera module incl. autofocus Module 3 | IMX219 / OV5647 on a pinned kernel, or a USB webcam |
| Software for this repo | everything runs as is | SPI ring, libgpiod buttons, USB webcam: all supported in the code now; expect an evening or two of distro work |
| Boot | 12 to 15 s | 15 to 20 s |

What this means for the enclosure: the board is not the biggest thing in the
box. A 60 mm arcade button, a 45 mm LED ring, a 40 mm speaker and the camera
arm set the footprint at roughly 120 × 80 mm either way. The Radxa saves depth
and lets the box run from a power bank; the Pi 5 needs a mains lead and a fan
slot.

**Decision rule**

- Choose the **Radxa Cubie A7Z** (4 or 8 GB) if: you want Pi 5 class
  compute in the Zero footprint, accept 2 W idle and a heatsink, and are
  willing to be an early adopter on the A733 software stack. It is the
  Orange Pi Zero 3W done properly.
- Choose the **Radxa Zero 3W** if: the brain should be small and run from a
  battery, recorded voice clips are the plan (with Piper for short phrases at
  most), and any future "AI helper" may live elsewhere: on a home server over
  Wi-Fi, or in the cloud as an opt-in. For this project's actual workloads it
  is capable enough.
- Choose the **Pi 5** if: you want an on-board path to a local language model
  through the AI HAT+ 2, want neural speech for everything the brain says,
  or want zero platform work.

The AI question is the real fork. A local model does not have to run inside
the brain: the brain can stay a small camera-and-buttons box and ask a
machine elsewhere in the house. That decouples "small and low power" from
"local AI later", and it is the cheaper way to get a capable model anyway.

## Recommendation

1. **Pick by the decision rule above.** Three sanctioned boards: Radxa Zero
   3W 4 GB (smallest power draw, most mature of the small boards), Radxa
   Cubie A7Z 4 or 8 GB (Pi 5 class compute in the same footprint, early
   software), Pi 5 4 GB (zero platform work, AI HAT+ 2 path). Orange Pi
   Zero 3W is the same chip as the Cubie A7Z with worse software; skip it.
   Either way, run the day-one smoke test below before designing the
   enclosure around the board.
2. **No accelerator now.** Version 1 and 2 (sensors, step mode, voice
   feedback) run entirely on the CPU.
3. **Leave 20 mm of headroom and the GPIO stacking header in the enclosure
   design**, so an AI HAT+ 2 can drop in later for a local helper that talks
   to her about her program. Skip the first AI HAT+ (vision-only) and skip
   Coral entirely.
4. **Keep a documented budget / compact build.** Pi Zero 2 W if you can
   get one, otherwise Radxa Zero 3W 4 GB with a USB webcam. The code is the
   same; only timings and the hardware shims differ.

## Day-one smoke test for any non-Raspberry board

Do this before anything else; it covers every platform risk at once.

1. Flash the vendor image the docs recommend; note the kernel version.
2. `pip install bleak`, run `python -m brain.drivers.pybricks_ble` with the
   hub interpreter loaded: the hub must beep and drive. Leave it looping for
   an hour; BLE stability is the one thing we cannot work around.
3. Plug in the USB webcam, run `python -m brain.main --webcam 0 --simulate`
   with the paper tiles on the baseplate: it must read the program aloud.
4. Wire the ring to the SPI MOSI pin and a button to a GPIO line; check the
   backends `Ring().backend` and `Buttons().backend` report `spidev` and
   `gpiod`.
5. Play a wav with `aplay` through the I2S amplifier.

If all five pass in one evening, the board is in. If BLE or the webcam fail,
stop and take the Pi 5.

## What changes in the design docs

- `04-architecture.md` brain hardware table: Pi 5 4 GB, active cooler, 27 W
  USB-C supply; Zero 2 W listed as the budget alternative.
- Enclosure: Pi 5 footprint (85 × 56 mm) plus HAT headroom; camera on the
  Pi 5's 22-pin CSI connector (needs the 22-to-15-pin camera cable).
- Audio: Pi 5 still has no headphone jack; the I2S amplifier stays.
