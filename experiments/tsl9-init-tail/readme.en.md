# Initialization tail andshared returns

[繁體中文](README.md) · [Source](src/init_tail.v1.c) · [Specification](spec-v1.json) · [Integration results](../../analysis/init-tail-2026-10-24/readme.en.md)

Original17B92–17BC4 and17BF6–17C4E total138B/47 instructions in10 architectural regions with explicit adjacency. Actual C11/C++17 objects preserve120 noncontrol bytes;five typed edges match after static original-VA encoding,covering all138 bytes.

Constructor16B S0/RA frame,restore before tail jump,GP+378 fresh reads/two return paths,andthree resident indirect calls remain. These are not ordinary independently callable C functions. Entry/callee/IRQ ABI andresident implementation are unproved.

```sh
python3 experiments/tsl9-init-tail/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-init-tail/build/trial-v1
python3 experiments/tsl9-init-tail/verify-provider-v1.py --replay experiments/tsl9-init-tail/build/provider-v1
python3 experiments/tsl9-init-tail/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-init-tail/build/component-v1
python3 scripts/check-init-tail-publication.py
```

Verified with installed,pinned Windows Android NDK27.1.12297006/LLVM18 tools. Native checks require `.exe`;cross-OS replay is unproved. Retained local receipts/objects are required;replay does not download or rebuild missing outputs.

No target/HOST/ISA execution,hardware/network orflashable BIN. Physical MCU/ROM,RAM/original placement,full boot andBLE OTA remain unproved.
