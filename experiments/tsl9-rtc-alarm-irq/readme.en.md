# RTC alarm IRQ native reconstruction

[繁體中文](README.md) · [Source](src/rtc_alarm.v1.c) · [Specification](spec-v1.json) · [Integration results](../../analysis/rtc-alarm-irq-2026-10-24/readme.en.md)

Five original regions,78B/23 instructions,compile as C11 and C++17.62 noncontrol bytes match directly;four typed direct references match after static original-VA encoding,covering all78 bytes. GP+392,original halfword polling,mask clearing,tail jump andMRET remain. No target/ISA execution,hardware,network or firmware BIN.

The native object retains four relocations;it is not an executable original-address image. Physical MCU,ROM,frame/IRQ contracts,poll termination andOTA remain unproved. Use an existing LLVM tool-path variable:

```sh
python3 experiments/tsl9-rtc-alarm-irq/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-rtc-alarm-irq/build/trial-v1
python3 experiments/tsl9-rtc-alarm-irq/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-rtc-alarm-irq/build/component-v1
python3 scripts/check-rtc-alarm-irq-publication.py
```

Verified on Windows Android NDK27.1.12297006/LLVM18 with pinned hashes and `.exe` tools;other systems are untested. Retained local artifacts are required;replay does not download or rebuild missing outputs.
