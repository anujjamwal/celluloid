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

## Recommendation

1. **Build the brain on a Pi 5 with 4 GB.** It costs about $50 more than
   the Zero 2 W, and in exchange: half the boot time, instant board reads,
   real-time neural speech if we outgrow the recorded clips, voice commands
   ("stop!") become feasible, and the enclosure never has to be redesigned.
   The stand is stationary, so mains power is no loss. Take the 8 GB board
   (+$20) only if a local language model is a real intention rather than a
   maybe.
2. **No accelerator now.** Version 1 and 2 (sensors, step mode, voice
   feedback) run entirely on the CPU.
3. **Leave 20 mm of headroom and the GPIO stacking header in the enclosure
   design**, so an AI HAT+ 2 can drop in later for a local helper that talks
   to her about her program. Skip the first AI HAT+ (vision-only) and skip
   Coral entirely.
4. **Keep a documented budget / compact build.** Pi Zero 2 W if you can
   get one, otherwise Radxa Zero 3W 4 GB with a USB webcam. The code is the
   same; only timings and the hardware shims differ.

## What changes in the design docs

- `04-architecture.md` brain hardware table: Pi 5 4 GB, active cooler, 27 W
  USB-C supply; Zero 2 W listed as the budget alternative.
- Enclosure: Pi 5 footprint (85 × 56 mm) plus HAT headroom; camera on the
  Pi 5's 22-pin CSI connector (needs the 22-to-15-pin camera cable).
- Audio: Pi 5 still has no headphone jack; the I2S amplifier stays.
