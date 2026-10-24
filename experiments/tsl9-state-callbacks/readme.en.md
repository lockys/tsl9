# State readers and helpers

[繁體中文](README.md)

Reconstructs 27 state-event reader roots and their two actual helper callees from the official ID2966 V4.1.60 BIN: 472 bytes, 153 instructions, 45 architectural basic blocks. C11 and C++17 produce identical native objects. All 438 non-control bytes match directly; static original-address encoding of ten branch/call relocations restores all 472 original bytes.

[Curated source](../../src/native/receive/state_leaf_reads.c) · [Instruction evidence](../../analysis/state-callbacks-2026-10-24/leaf-evidence.json) · [Native receipt](build/native-v1/measurement.json)

Preserves AUIPC/GP accesses, read widths, conditional bit packing, both helper calls, and B082's 16-byte stack frame and RA save/restore. These are architectural regions with deliberate fall-through adjacency, not independently callable ordinary C APIs.

Replay locally using `python build-v1.py --tool-dir "$LLVM_BIN" --replay build/native-v1`; substitute the local LLVM bin directory. Use `--trial <new-name>` for a new build.

Field meaning, RAM ownership/mapping, private ABI, final original placement, MCU/ROM/IRQ and OTA compatibility remain unproved. No target/model/ISA execution, hardware access or flashable BIN generation.

## Integrated component

[Current integration evidence](../../analysis/state-callback-integration-2026-10-24/readme.en.md): 12224B code + 516B data / 807 relocations / 79 unresolved symbols. Replay with integrate-v1.py --tool-dir "$LLVM_BIN" --replay build/component-v1. This remains a non-executable VMA-zero partial object; physical compatibility is unproved.
