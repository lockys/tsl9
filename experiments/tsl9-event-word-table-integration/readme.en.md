# Formal seven-word event DATA integration

[繁體中文](README.md) · [Project](../../README.md) · [C/C++ source](../../src/native/receive/event_word_table_data.c)

The **28 bytes** at `0x1AAE8..0x1AB04` now have curated `src/`, manifest entries, and original-coordinate diagnostic linkage. Identical C11/C++17 diagnostic ELFs match **73,538 / 76,800 bytes (95.75%)** at original addresses: 69,412B CODE + 4,126B DATA. This is static byte coverage, not feature completion or flash success.

| Item | Actual evidence |
| --- | --- |
| Sources | 164 C/H files; 125 CODE and 13 DATA units |
| Compilation provenance | Retain the parent 548-object proof and 2,240 parent inputs; compile four origin/src C11/C++17 objects. Composite total: 276 comparisons / 552 objects, without claiming a full rebuild of every object |
| Original coordinates | 6,182 CODE owners, 64 DATA OBJECTs, 40 adjacent spans; all 5,270 relocation roles retained |
| Remaining | 3,262B: 3,128 deliberately excluded + 134 other unselected bytes; six unresolved APP source providers |

## Use conditions and semantics

The [complete consumer contract](../tsl9-event-word-table-data/readme.en.md) covers all 388B / 135 instructions of `0x176F8..0x1787C` and its 48-byte frame. The load at `0x17844` uses `0x1AAE8 + 4*uint8(GP+370)`. Seven words cover the read only when its index is 0 through 6 at that read.

The `(old_index+1)%7` store occurs after the read and does not bound the first read. The 196 GP address takes, aliases, indirect writers, excluded CODE, IRQ/DMA, initialization, and coherence remain open. No clamp or proof of the complete table declaration is introduced by backing these conditional reads.

The low three table bytes become record offsets 2/3/4. The original complete `LW(SP+12)` is retained; its factor selects SP+14 bits 2 through 6 and adds one, giving 1 through 32 and raw A2 values `800*factor`. Time units, installed slot `0x40058` identity, and effects remain unproved. The seven low24-bit words resemble a palette; this is an inference, **not confirmation of RGB channels, lighting hardware, or a product feature**.

All previous CODE/DATA owner contents and coordinates, six imports, six DATA labels, and CODE continuation observations remain unchanged, including the `0x8034→0x8038` startup boundary. No zero filling, padding, stubs, or complete provider aliases were added. Only 28B were selected; no conservative 1,024B envelope or excluded payload was read.

## Replay and readiness

With the frozen local parent artifacts and LLVM available, run from the repository root:

```sh
python3 experiments/tsl9-event-word-table-integration/audit-v1.py --tool-dir "$LLVM_BIN"
python3 experiments/tsl9-event-word-table-integration/check-readiness-v1.py --tool-dir "$LLVM_BIN"
```

The second command currently returns **exit 2**: evidence verified, but only the source/native evidence gate is proved out of eight. Exit 1 means evidence drift or a failed check. Complete APP bytes, providers, a loadable artifact, installed ROM/ABI, startup/IRQ, RAM, and Flash/OTA/rebuilt-device behavior remain incomplete or unproved.

The diagnostic ELF has entry 0 and PT_LOAD 0: **it is not a flashable BIN**. No target, HOST model, ISA, hardware, or third-party API execution occurred. Parent source and experimental proofs were replayed before the extension; afterward their inputs and a byte-exact historical manifest are retained, without claiming a fresh replay of incompatible historical snapshots.

[Summary](summary.json) · [Full receipt](audit-result-v1.json) · [Readiness receipt](readiness-v1.json) · [Source extension](source-extension-v1.json) · [Offline feature idea](feature-candidates.json)
