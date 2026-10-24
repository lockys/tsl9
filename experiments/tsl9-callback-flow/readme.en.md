# Callback-flow reconstruction

[繁體中文](README.md)

Seven complete roots and the literal1061C/1333C function-address targets: **1082B /368 instructions /79 regions plus96B readonly data**. C11/C++17 produce identical objects. All selected original bytes,60 direct controls,10 PC-relative references and constant data pass static original-address checks.

[Source](../../src/native/receive/callback_flow.c) · [Evidence](../../analysis/callback-flow-2026-10-24/evidence.json) · [Specification](spec-v1.json) · [Native receipt](build/native-v1/measurement.json)

Retains the complete672B13346 state builder, paths after its first return, original frames,fresh memory and control order. Existing names are reused only at identical original PCs. All35 standalone external providers remain explicit; no stubs. Now integrated into the startup component:13864B code+674B data/930 relocations/95 UND. [Integration evidence](../../analysis/callback-flow-2026-10-24/readme.en.md).

```sh
python3 experiments/tsl9-callback-flow/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-callback-flow/build/native-v1
```

These are architectural regions,not ordinary independently callable C ABI entries. Field meaning,bounds,RAM ownership,installed resident/private ABI,original placement,physical MCU/ROM/IRQ and OTA compatibility remain unproved. No target/model/ISA execution,network/hardware access or BIN generation.
