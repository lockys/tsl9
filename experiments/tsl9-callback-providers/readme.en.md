# Callback-provider reconstruction

[繁體中文](README.md)

Retains five complete roots D272,B0FC,12B24,13D48,10630 and B0FC's actually registered B0D0 callback: **558B / 188 instructions / 47 regions plus 62B readonly data**. C11 and C++17 produce identical native objects. Static original-address encoding restores all code bytes; all seven signed relative-table words and two 17-byte templates match the original firmware.

[Source](../../src/native/receive/callback_providers.c) · [Instruction evidence](../../analysis/callback-providers-2026-10-24/evidence.json) · [Specification](spec-v1.json) · [Accepted native receipt](build/native-v2/measurement.json)

12B24 includes cases after its shared return and is retained through 12BC8. The audit checks 31 direct controls, eight PC-relative and 14 data references, original frames, GP counters and notification conditions. Standalone compilation keeps twelve external symbols explicit. The unit is now integrated into the startup graph; five callees bind actual parent code and seven remain genuine gaps. [Integration evidence](../../analysis/callback-providers-2026-10-24/readme.en.md).

Replay with the local LLVM directory:

```sh
python3 experiments/tsl9-callback-providers/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-callback-providers/build/native-v2
```

The initial native-v1 compile failed because generated literal-pair assembly contained escaped newline separators. Its rejected source and UNACCEPTED record are retained and not counted as passing. Original placement, data index bounds, RAM ownership, installed resident identity/private ABI, physical MCU/ROM/IRQ and OTA compatibility remain unproved. No target/model/ISA execution, network/hardware access or BIN generation.
