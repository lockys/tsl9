# TSL9 reverse engineering

[繁體中文](README.md) · [简体中文](readme.zh-CN.md)

**TSL9 = 非凡司令官**.

Rebuild Feifan TSL9 firmware in C/C++ and study Bluetooth OTA and compatibility with the original hardware.

[`legacy-options-2026-10-20`](firmware-downloads/legacy-options-2026-10-20/) contains firmware captured from the official update service.

**Disclaimer: This project uses Codex vibe coding with REA for experimental reconstruction. Reverse engineering has not yet produced verified, working TSL9 firmware. Rebuilt BINs have not passed full validation on the original hardware; successful OTA readback does not prove working features.**

**Verified reconstruction byte coverage: 91.83%** (70,522/76,800 bytes; code 66,600B + data 3,922B). Counts only C/C++ reconstruction that passes byte-for-byte comparison at original addresses; this is not feature completion or flash readiness. [Evidence](analysis/central-callback-integration-2026-10-26/summary.json)

## Getting started

Requires Python 3.10+ and C11/C++17 compilers. Run the offline model tests from the repository root:

```sh
python3 scripts/portable_verify.py --model runtime-loop --language both
```

On Windows, use `py -3` instead of `python3`. No hardware is connected or flashed.

[Source](src/) · [Build experiments](experiments/) · [Analysis](analysis/) · [Official BINs](firmware-downloads/) · [APK / experimental images](artifacts/)
