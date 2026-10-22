# Packet receive: A1 liveness repaired, reconstruction still rejected

[繁體中文](README.md)

The target is official ID2966 V4.1.60 `[0x16A7C,0x16B0A)`,142B/52 instructions. This milestone creates a [readable C/architectural-port candidate](../../experiments/tsl9-packet-receive/src/packet_receive.c), without compiler-flag search or promotion to curated `src/`.

| | v1 | v2 | Official |
| --- | --- | --- | --- |
| Bytes/instructions | 156/59 | 154/58 | 142/52 |
| SPI call offsets | 36/48/54 | 34/46/52 | 34/46/52 |
| Ring call offset | 140 | 138 | 126 |
| First non-call difference (combined offset) | +22 | +40 | — |

v1 omitted incoming A1 liveness before `SW A1,12(SP)`. The compiler reused A1 for constant1, corrupting the saved address. v2 explicitly imports A1 and feeds the save port, while comparing channel against the existing A4 value. Its first34 bytes now match the original, with correct incoming-A1 SSA flow. This fixes a real ABI bug without establishing whole-function equivalence.

Four issues remain: `MV A0,A1` moves ahead of S0/S2 initialization; the epilogue is duplicated; DLC arithmetic uses A0 and changes rejection residues; ID construction swaps `MV A3,S1` and shift order. v2 has four genuine JAL relocations/two UND providers and no fake ABS provider. It has not been composed into the352B pipeline. The zero-immediate unresolved JAL produces a raw difference at+35; the first difference outside call windows is projection+36/combined+40. These are distinct measurements.

[summary.json](summary.json) and the [two receipt derivatives](receipts/) retain exact hashes, flags and differences. Only literal paths are replaced; original receipts/ELF/IR/MD/logs remain local. Reversing substitutions reproduces complete original JSON. Existing producer variables remain; new aliases are `LOCAL_PROJECT_ROOT`, `LOCAL_LLVM_BIN`, `LOCAL_CLANG_RESOURCE`, and `LOCAL_STDINT_HEADER`. v1 is historical: the primary source now contains v2, so current direct replay is not claimed.

Next preserve LW A1 → S0/S2 initialization → MV A0,A1, then rejection A0 and shared epilogue contracts. Matching size alone is insufficient. No target/ISA/MMIO/hardware execution, network API calls or BIN generation occurred.
