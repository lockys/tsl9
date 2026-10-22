# V1.31 resident copy reference source

This is a **public SDK reference candidate**, not the resident read from the user's TSL9. The selected main carrier is `[0x40000,0x6EA66)`, 191,078B, SHA-256 `133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22`. It comes from the already downloaded December2023 IntelHEX at official commit `ec059e0b18046b111ee850e44f105fcd095e775c`; the captured marker is `CH32V20x_BLE_LIB_V1.31`. No download or new dependency was used here.

The actual LE32 word at slot `0x4004C` is `0x20000332` (`32030020`), a RAM address. It is **not** a function at `0x4004C` or within the carrier's flash-text range. The loader operands and the inclusive word-copy helper establish this conditional mapping:

- Entry seeds48B from `0x40280` to `0x20000010`, including the18B word-copy helper.
- The first loader requests source `0x402B0`, destination `0x20000040`, inclusive last destination word `0x20002E70`: **2,957 words / 11,828B**, all represented in the retained main segment.
- Therefore RAM `0x20000332` maps to source `0x405A2`. Static traversal from that source entry reaches exactly `[0x405A2,0x405DC)`, **58B / 18 instructions**, SHA-256 `558a82658cb54901945d4c2884f2e87e763f64d57c0cafa831307beb44ae0c36`. Its mapped RAM interval is `[0x20000332,0x2000036C)`. All local branch targets and the return are covered; there is no external call or unresolved control frontier. The end was derived from the reachable CFG, not the next symbol. Copying the first812B/203words of the first loader normally is sufficient to represent this whole helper; that is an address calculation, not evidence that execution occurred.

The58B body has these ordered effects:

1. Read32 from literal `0x4002420C` into A4, write32 zero to the same address, then execute `FENCE.I`.
2. Only afterward test destination A0, source A1 and u32 byte count A2. A zero pointer or zero count skips byte requests but still reaches the restore store.
3. Otherwise copy forward: compute source+oldIndex, read an unsigned byte at `0x405C8`, compute destination+oldIndex, increment index at `0x405D0`, write that byte at `0x405D2`, then compare index with count. Reads are live; overlapping destinations can affect subsequent source reads. This is not a `memmove` contract.
4. Write A4 back to `0x4002420C` at `0x405BE` and RET through live RA. No second `FENCE.I` follows the restore. A0 remains the numeric destination; it is not a status boolean. This body makes no explicit SP/GP access or call.

The hardware role of `0x4002420C`, accessibility, fault/IRQ behavior, physical ISA, caller ABI and the installed slot value remain unknown. HALT or TRANSFER at any request stops that prefix; the original code does not promise a synthetic `finally` restoration. The instruction fields used here are standard RV32I/C plus the literal `FENCE.I` encoding. No V1.30 `RC_WCH`/XWCHC profile was selected or borrowed.

Mapping also does **not** prove startup completion. The independently retained second loader requests140B from `0x6EAA4`; only136B through `0x6EB2C` are present in the captured segment ledger. Its final required word `[0x6EB2C,0x6EB30)` remains absent. A later zero operation cannot prove that the earlier missing source read succeeds. No holes were filled, no resident provider was generated, and no reference bytes were injected into APP/BOOT.

The package retains the actual slot/header and derives the loader mapping from raw operands. `source-map.json` includes the loader rows, all helper PCs in both source and conditional RAM coordinates, the complete CFG, and **23 raw operand mutation rejections**. Sixty selected instruction rows/210B across entry, loader, seed helper and copy helper are verified byte for byte. `contract.json` contains the numeric/live-memory schema for a later C/C++ reference model. `retained-source.json` is self-contained, hard-pinned evidence with the compact segment/hole ledger; replay needs neither radare2 nor the old report tree.

Portable, entirely read-only replay:

```powershell
python -B "<source-package>\inspect-source.py" --check --carrier "<absolute-REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin>" --source-root "<source-package>"
```

To additionally recheck the already sealed historical carrier/handoff trees in the original workspace, append:

```powershell
--verify-historical --workspace "$env:TSL9_ANALYSIS_WORKSPACE"
```

`--check` regenerates and byte-compares both JSON reports, checks all seal members, and writes nothing. `--write` is restricted to this checker's own unsealed directory. No original ISA execution, emulation, network, hardware, real UID packet, ROOT change, D change or BIN/provider construction is performed.
