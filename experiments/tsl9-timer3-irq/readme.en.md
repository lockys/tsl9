# TIM3 IRQ native regions

[繁體中文](README.md) · [Source](src/timer3_irq.v1.c) · [Specification](spec-v1.json) · [Integration results](../../analysis/timer3-irq-2026-10-24/readme.en.md)

Original979E–9958 contains442B/138 instructions in32 architectural regions with explicit fallthrough order. Actual C11/C++17 outputs preserve376 noncontrol bytes;24 typed direct edges match after static original-VA encoding,covering every442 bytes.

These are not ordinary independently callable C functions. C unsigned operations and volatile accesses use explicit SP/S-register/AUIPC/DIV/call ports. The16B frame,S0/S1/S2,signedDIV andMRET remain. Two indirect sources are literal word40068 andthen-liveS2+12;callee identities remain unknown.

Use an installed Windows LLVM tool directory matching the pinned hashes:

```sh
python3 experiments/tsl9-timer3-irq/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-timer3-irq/build/trial-v1
python3 experiments/tsl9-timer3-irq/select-providers-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-timer3-irq/build/providers-v1
python3 experiments/tsl9-timer3-irq/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-timer3-irq/build/component-v1
python3 scripts/check-timer3-irq-publication.py
```

Verified with Android NDK27.1.12297006/LLVM18,pinned hashes and `.exe` tools;other systems are untested. Missing retained local outputs are not downloaded or rebuilt by replay. Provider selection retains four whole real functions totaling60B without synthesizing a provider.

No target/HOST/ISA execution,hardware or network. Physical MCU,resident,IRQ ABI,original placement/RAM,full boot andOTA remain unproved. No flashable BIN.
