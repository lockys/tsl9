# Candidate SDK initialized data: 136-byte prefix

[繁體中文](README.md) · [Previous clock/random proof](../tsl9-original-clock-random-idle-binding/readme.en.md) · [Earlier C/C++ bodies](../tsl9-resident-scheduled-record-callback/readme.en.md)

The [C/C++ source](resident_initial_data.c) reconstructs **34 words / 136 bytes** from `[0x6EAA4,0x6EB2C)`, conditionally copied to RAM `[0x20002E70,0x20002EF8)`. This is actual readonly DATA, not a function stub, hardware model or Flash image. No CODE was added.

Actual C11/C++17 objects are identical: one positive-size OBJECT, alignment4, zero FUNC/relocation/UND. Two ELF readers verify every byte against the captured segment. The real partial link contains **35,324 CODE + 392 DATA bytes / 12,195 instructions**, 2401 FUNC, 1914 relocations, 4174 sections and zero named UND. All prior CODE and typed relations are retained. [Full receipt](audit-result-v1.json)

## Why four bytes remain unprovided

The original HEX has **17 disjoint segments / 191,244 data bytes**. Its 191,078-byte main segment does not contain this final 136-byte data segment. The verifier independently checks all 11,973 record lengths, checksums and addresses, plus every segment. It inserts no zero or FF filler.

The startup helper's unsigned guard includes the final word at its upper bound:

| Operation | Required source / destination ranges (end exclusive) | Bytes |
| --- | --- | ---: |
| First copy | `0x402B0..0x430E4` → `0x20000040..0x20002E74` | 11,828 |
| Second copy | `0x6EAA4..0x6EB30` → `0x20002E70..0x20002EFC` | 140 |
| Captured second prefix | `0x6EAA4..0x6EB2C` → `0x20002E70..0x20002EF8` | 136 |
| Unprovided final READ32 | `0x6EB2C..0x6EB30` → `0x20002EF8..0x20002EFC` | 4 |

The later zero helper covers `[0x20002EF8,0x20003618)`. It runs only after a normal copy return. **Later zeroing does not justify skipping the earlier READ32.** Missing capture does not prove physical read failure; the word must not be invented.

## Conditional initial value

Prefix word index22 contains `0x012F81C3` at source `0x6EAFC`, mapping to random-state RAM `0x20002EC8`. If the known prefix is actually copied, earlier memory requests complete normally and no overwrite occurs, that word is written before the unprovided load.

This does not establish complete startup, the value observed by the first random call, entropy, MRET context or installed ROM identity. Earlier live-seed limitations remain valid.

The APP's 159 C/H files and **95.54% static byte coverage** are unchanged. This is candidate SDK data and is not integrated into the original APP. No final original-address link, hardware execution or new BIN was produced. ROM/RAM/ISA/IRQ/Flash/OTA compatibility remains unresolved. **This is not flash-ready firmware.**

The offline sparse-input check could be added to future artifact validation. It currently exists only in the verifier, with no App or flasher integration.

Provide the pinned original references, prior native artifacts and LLVM; nothing is downloaded automatically. First build from the project root:

```sh
python experiments/tsl9-resident-initial-data-prefix/build-v1.py --tool-dir "$LLVM_BIN" --build
python experiments/tsl9-resident-initial-data-prefix/audit-v1.py --tool-dir "$LLVM_BIN" --link --write-receipt
```

For existing artifacts omit `--build`, `--link` and `--write-receipt` for read-only verification. Creation does not overwrite existing outputs.
