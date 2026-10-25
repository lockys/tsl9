# Original software-copy source windows

[繁體中文](README.md)

This round checks the original caller `0x12AD0..0x12B24` and the complete software-copy body `0x19BF0..0x19CA6`: **82 original instructions** and two readonly C/C++ data windows.

| Source range (exclusive end) | Length | Copy call | Local destination |
|---|---:|---|---|
| `0x19D08..0x19D66` | 94 bytes | `0x12AFC` | `SP+4..SP+98` |
| `0x19D68..0x19DD2` | 106 bytes | `0x12B1A` | `SP+4..SP+110` |

Lengths come from original instructions, not neighboring addresses. The two-byte gap is excluded. The caller reserves 128 stack bytes and saves its return address at `SP+124`; neither selected buffer overlaps that slot. This does not establish whole-stack or interrupt safety.

## Verified evidence

- Fresh local r2 static disassembly agrees with retained evidence and all 82 original instruction byte ranges.
- All 54 copy instructions are classified, including 24 memory operations and 10 bit-decoded control transfers. The final load of each 36-byte group uses `-4` after source increment36, reading old source `+32`.
- With valid accessible nonwrapping pointers and an available stack, the 36-byte, word and byte paths stay within each requested source length. This is a static bound argument, not firmware or model execution.
- C11 and C++17 compile to identical objects: 200 readonly bytes, two actual OBJECT definitions, no functions, unresolved symbols or relocations. Two independent ELF parsers agree on all sections, bytes, symbols and relocations.
- Neither source window overlaps any of the current 5,721 integrated CODE/DATA owners. All 149 existing C/H files and the source manifest remain unchanged.

[C/C++ data](../../experiments/tsl9-record-copy-windows/src/record_copy_windows.v1.c) · [Original evidence](evidence.json) · [Native proof](native-proof.json) · [Summary](summary.json)

## Scope and next step

This record preserves the standalone experiment and its87.83% baseline. Source curation,component integration and original-coordinate proof have since passed;current coverage is88.09%. See the [integration evidence](../record-copy-integration-2026-10-25/readme.en.md).

Physical feature meanings, original declaration extents and complete MCU/ROM/RAM/IRQ/BLE OTA compatibility remain unproved. No new BIN, hardware access or backend requests. The [feature candidate](feature-candidates.json) is update-artifact completeness preflight; it has not been added to the OTA workflow.
