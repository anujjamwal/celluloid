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
4. **Keep the Zero 2 W as the documented budget build.** The code is the
   same; only timings differ. Useful for a second unit or a gift to a friend.

## What changes in the design docs

- `04-architecture.md` brain hardware table: Pi 5 4 GB, active cooler, 27 W
  USB-C supply; Zero 2 W listed as the budget alternative.
- Enclosure: Pi 5 footprint (85 × 56 mm) plus HAT headroom; camera on the
  Pi 5's 22-pin CSI connector (needs the 22-to-15-pin camera cable).
- Audio: Pi 5 still has no headphone jack; the I2S amplifier stays.
