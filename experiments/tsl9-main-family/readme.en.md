# Native main/application/initialization family

[繁體中文](README.md) · [Source](src/main_family.v1.c) · [Specification](spec-v1.json) · [Integration results](../../analysis/main-family-2026-10-24/readme.en.md)

Three original ranges:application8180–81AA42B/15i,main9008–901A18B/8i,initialization9250–929064B/19i. Total124B/42 instructions in23 architectural regions with explicit adjacency. Actual C11/C++17 preserve52 noncontrol bytes;20 typed direct edges match after static original-VA encoding,covering all124B.

All three original16B frames,RA/S-register ports,then-liveS2+0 callback,watchdog write andno-link initialization tail to17BF6 remain. These are not ordinary independently callable C functions. Entry/provider ABI andruntime callback identity remain unproved.

Use an installed Windows LLVM directory matching the pinned hashes:

```sh
python3 experiments/tsl9-main-family/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-main-family/build/trial-v2
python3 experiments/tsl9-main-family/select-providers-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-main-family/build/providers-v1
python3 experiments/tsl9-main-family/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-main-family/build/component-v1
python3 scripts/check-main-family-publication.py
```

Verified with pinned Android NDK27.1.12297006/LLVM18 tools;native replay currently requires `.exe` andother systems are untested. trial-v2 is the formal standalone receipt. trial-v1 is an incomplete compilation before correcting the multi-range verifier andis not passing evidence;the C source did not change. Missing retained outputs are not downloaded or rebuilt.

No target/HOST/ISA execution,hardware ornetwork. Physical MCU/ROM,original placement/RAM,full boot andBLE OTA remain unproved. No flashable BIN.
