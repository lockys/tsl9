# Formal mode lookup DATA integration

[繁體中文](README.md) · [Project](../../README.md) · [C/C++ source](../../src/native/receive/record_mode_row_data.c)

Two readonly rows for conditional modes 1 and 3 now have curated `src/`, manifest entries, and original-coordinate linkage: **32 new bytes**. Identical C11/C++17 diagnostic ELFs match **73,510 / 76,800 bytes (95.72%)** of the official image at original addresses: 69,412B CODE + 4,098B DATA. This is static byte coverage, not feature completion.

| Item | Evidence |
| --- | --- |
| Sources | 163 C/H files; 125 CODE and 12 DATA units |
| Compilation provenance | Retain the parent 544-object proof and 2,197 parent inputs; compile four origin/src C11/C++17 objects. Total composite evidence: 274 comparisons / 548 objects, without claiming a full rebuild of all objects |
| Original coordinates | 6,182 CODE owners, 63 DATA OBJECTs, 41 adjacent spans; all 5,270 relocation roles retained |
| Remaining | 3,290B: 3,128 deliberately excluded + 162 other unselected bytes; 6 unresolved APP source providers |

## Use evidence for the new DATA

The original read at `0xCF5A` uses `0x1A078 + 16*mode + ((fresh_record4+1)&15)`. The [whole lookup contract](../tsl9-third-provider-lookup-contract/readme.en.md) and [writer provenance](../tsl9-mode-state-writer-contract/readme.en.md) identify these conditional half-open read windows:

- Mode 1: `[0x1A088, 0x1A098)`, 16 bytes.
- Mode 3: `[0x1A0A8, 0x1A0B8)`, 16 bytes.

Both rows have real C constant arrays and positive native OBJECTs matching the original DATA. No complete `1A078` provider alias was added. The setter accepts any incoming A0 low byte; explicit local writes of 1 through 5 do not prove a global mode domain. Indirect callers, aliases, excluded CODE, IRQ/DMA, initialization effects, and write-to-read coherence remain open. No mode clamp or actual reachability of every column is claimed.

All previous CODE/DATA owner contents and coordinates, six imports, six DATA labels, and CODE continuation observations remain unchanged, including the `0x8034→0x8038` startup boundary. No zero filling, padding, stubs, or complete provider aliases were used to close gaps.

## Verify and check readiness

With the frozen local parent artifacts and LLVM available, run from the repository root:

```sh
python3 experiments/tsl9-record-mode-row-integration/audit-v1.py --tool-dir "$LLVM_BIN"
python3 experiments/tsl9-record-mode-row-integration/check-readiness-v1.py --tool-dir "$LLVM_BIN"
```

`LLVM_BIN` is the locally configured LLVM tools directory. The first command checks formal evidence. The second currently returns **exit 2**: evidence verified, firmware not ready. Exit 1 indicates evidence drift or a failed check and must not be ignored. Only the source/native evidence gate is proved out of eight; complete APP bytes, providers, a loadable artifact, installed ROM/ABI, startup/IRQ, RAM, and Flash/OTA/rebuilt-device behavior remain incomplete or unproved.

The diagnostic ELF has entry 0 and PT_LOAD 0: **it is not a flashable BIN**. No target, HOST model, ISA, hardware, or third-party API execution occurred. Parent source and mode-use proofs were replayed before the extension; afterward, their exact evidence and inputs are retained, with a byte-exact reconstructed historical manifest as the sole manifest exception.

[Summary](summary.json) · [Full receipt](audit-result-v1.json) · [Readiness receipt](readiness-v1.json) · [Source extension](source-extension-v1.json) · [Unimplemented feature candidate](feature-candidates.json)
