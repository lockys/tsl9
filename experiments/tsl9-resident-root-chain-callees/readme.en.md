# Eight named root-chain gaps and two actual helpers

[繁體中文](README.md) · [Previous root chain](../tsl9-resident-record-root-chain/README.md) · [Allocation contract](../tsl9-scheduler-allocation-contract/readme.en.md)

[C/C++](resident_root_chain_callees.c) adds **10 complete candidate SDK bodies / 1,064 bytes / 352 instructions**, supplying the prior eight named gaps and two actual callees. Original execution context remains required; this is neither a HOST API nor manufacturer C source.

| Original half-open range | Bytes / instructions | Maximum own frame |
| --- | --- | --- |
| `0x55D00..0x55D3C` | 60 / 21 | 32 |
| `0x55D3C..0x55DEA` | 174 / 55 | 0 |
| `0x5605C..0x56086` | 42 / 14 | 0 |
| `0x560AA..0x560B2` | 8 / 4 | 0 |
| `0x56326..0x5649C` | 374 / 120 | 48 |
| `0x56716..0x567BE` | 168 / 50 | 16 |
| `0x57B28..0x57B7C` | 84 / 33 | 32 |
| `0x63966..0x639CA` | 100 / 37 | 0 |
| `0x6DEC2..0x6DEEE` | 44 / 15 | 0 |
| `0x43ED2..0x43EDC` | 10 / 3 | 0 |

Actual C11/C++17 objects match: 85 positive FUNC regions, 56 direct-control relocations and 12 Xwchc ports. All bytes match after original-address normalization. Complete CFGs remain reachable, including delayed-frame paths; every original exit has no outstanding own frame. Late reachable arms after early RETs remain intact.

## Evidence and limits

- Tail `0x55D38 → 0x43874` preserves its no-link transfer, RA restoration and 32-byte frame release. LUI/ADDI constructs A0=**`0x56CDC`**. Its body is not supplied and its physical CODE-pointer role is unproved; named-symbol resolution does not hide this literal dependency.
- Tail `0x567B4 → 0x43414` also remains no-link. The function has delayed frame allocation. The proof establishes no outstanding own frame at its exits; it does not claim that every tail path previously allocated 16 bytes.
- Original signed `DIV` at `0x56078` and variable shifts in `0x6DEC2` remain explicit instruction ports, without nonzero-divisor or shift-count assumptions. `0x560AA` only establishes clearing bits2/3 in original pointer byte+12; no hardware feature name is assigned.
- `0x43ED6` stores original A0 as a 32-bit word at `0x20003244`. No live value or physical role is inferred. The previous two callback sites and other original memory/callback/initialization uncertainties remain open.

This candidate partial composition is **35,150 CODE + 256 DATA bytes / 12,133 instructions**, 2385 FUNC regions and 1904 relocations. All four new imports have real existing bodies. Named UND decreases from 8 to **0**. **Zero named UND does not close raw pointers, callbacks, physical ROM/RAM/IRQ or the execution environment.**

## Readers and verification

Both actual C/C++ compositions have **4,147 sections**, exceeding retained v6's 4,096 ceiling. [v7](elf_reader-v7.py) changes only that ceiling to 8,192 and its explanatory text. Frozen v6, ownership-v2 and compare-v2 remain unchanged. New [ownership-v3](verify-ownership-v3.py) and [compare-v3](compare-readers-v3.py) only switch reader selection and corresponding fixed hashes. The checker verifies these exact text changes and compares every section field/byte, symbol and relocation against an independent ELF reader.

Evidence: [audit-result-v1.json](audit-result-v1.json), [evidence-v1.json](evidence-v1.json), [summary.json](summary.json), [frames_abi.c](frames_abi.c). Original APP remains 159 C/H files and **95.54% static byte coverage**, not functional completion. Physical ROM/RAM/ISA/IRQ, Flash/OTA and global initialization remain unproved, including the inherited 4-byte startup-source gap. **No new BIN or flashability claim.**

## Recheck retained artifacts

Supply the locally retained hash-pinned references, earlier native artifacts and this composition's measured-link receipt. These commands perform read-only verification of existing artifacts; they neither download references nor create missing build artifacts:

```sh
python experiments/tsl9-resident-root-chain-callees/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-resident-root-chain-callees/build/native-v1
python experiments/tsl9-resident-root-chain-callees/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

No target/HOST-model/ISA/hardware execution occurs. Potential feature: offline numeric-flag and callback-argument provenance decoding, not an implemented or validated hardware feature.
