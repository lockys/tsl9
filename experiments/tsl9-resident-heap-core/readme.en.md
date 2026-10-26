# Resident heap candidate C/C++

[繁體中文](README.md) · [Message API candidates](../tsl9-resident-message-api/readme.en.md)

This study reconstructs two private helpers from public WCH SDK V1.31. **Installed TSL9 ROM identity is unproved; this is not flashable firmware.**

| Conditional RAM body | Bytes |
| --- | ---: |
| Allocate: `0x20000040..0x20000110` | 208 |
| Release/coalesce: `0x20000110..0x200001E4` | 212 |

[Source](resident_heap_core.c):145 instructions,37 positive FUNC regions and26 typed direct relocations. Actual C11/C++17 objects are identical; all420 bytes match after original-address control encoding. There are22 explicit conditional Xwchc LHU/SH ports, checked against14 relevant official vectors.

Partial linking with the preceding message API produces a nonloadable **584-byte/207-instruction ET_REL**. Both genuine heap imports resolve to real functions;51 FUNC regions and37 relocations retain every input code byte and reference. Zero named UND does not close the runtime contract.

## Candidate behavior and evidence

- Requests undergo16-bit truncation and4-byte alignment. A52-byte threshold selects the list. The8-byte block header stores size at+4 and flags at+6; allocation returns block+8.
- Splitting requires available size minus rounded request to exceed8. Release traverses, clears flags and conditionally coalesces. Acyclicity and termination remain unproved.
- The opaque call at `0x200000A0` reads its function pointer from RAM `0x20003220`. On normal callback return this wrapper follows its failure path without retrying.
- All V1.31/V1.40 helper differences are exactly13 RAM-immediate instructions shifted by `+0x50`; all remaining bytes match. Their global RAM layouts cannot be mixed without evidence.

See [audit-result-v2.json](audit-result-v2.json),[summary.json](summary.json) and [mapped instruction evidence](evidence-v1.json). Heap initialization,RAM bounds/ownership,callback behavior,installed ISA/ROM,IRQ and OTA compatibility remain unproved. The physical meaning and restoration effect of `0x4002420C` are unknown.

## Reproduce locally

Use the pinned Windows NDK LLVM tools from [spec-v1.json](spec-v1.json). From the project root,set `LLVM_BIN` to the tool directory. The following trial names must not already exist:

```sh
python experiments/tsl9-resident-heap-core/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-heap-core/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

Omit `--link-trial` to audit retained artifacts read-only. No target/HOST model/ISA execution,hardware access or new BIN occurred. Formal APP byte coverage remains **95.54%**,not functional completion.
