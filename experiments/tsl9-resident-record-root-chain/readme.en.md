# The 0x58498 root and its actual dependency chain

[繁體中文](README.md) · [Previous two tails](../tsl9-resident-record-transition/README.md) · [Conditional original APP callback evidence](../tsl9-original-callback-provenance/readme.en.md)

[C/C++](resident_record_root_chain.c) adds **10 complete candidate SDK bodies / 1,700 bytes / 572 instructions**. Original context remains required; this is neither a HOST API nor recovered manufacturer C source.

| Original half-open range | Bytes / instructions | Own frame |
| --- | --- | --- |
| `0x58498..0x585C8` | 304 / 104 | 16 |
| `0x58462..0x58498` | 54 / 20 | 16 |
| `0x5784A..0x57862` | 24 / 9 | 0 |
| `0x59D3E..0x59E3E` | 256 / 84 | 32 |
| `0x59E64..0x5A004` | 416 / 128 | 32 |
| `0x5E3A8..0x5E40E` | 102 / 39 | 32 |
| `0x57962..0x57A1E` | 188 / 64 | 16 |
| `0x57A4A..0x57AC4` | 122 / 43 | 16 |
| `0x57A1E..0x57A4A` | 44 / 15 | 16 |
| `0x578A4..0x57962` | 190 / 66 | 32 |

Actual C11/C++17 objects match: 113 positive FUNC regions and 94 relocations (76 direct controls, 9 far calls). Forty Xwchc ports agree with primary definitions and the existing 52 positive vectors. All bytes match after original-address normalization. Complete CFGs are reachable, own frames balance at exits, and late reachable arms after early RETs remain intact.

## Findings

- Actual caller `0x588B4` calls `0x58498` at `0x5895E`. The root's no-link tail `0x585BA → 0x58462` retains argument/RA restoration and 16-byte frame release.
- Tails `0x59E3A → 0x56716` and `0x5E3F8 → 0x43208` retain their original 32-byte frame restoration and no-link transfers. The former target remains genuinely unresolved; the latter has a real existing message-send body. No ordinary C call replaces a tail.
- Lookup `0x5784A` reads head slot `0x20003454`, compares a node+8 unsigned halfword against full A0, and follows node+0. A0 is not silently truncated. Valid memory, acyclicity and termination are unproved.
- `0x59E08` and `0x59E16` freshly load callback slot `0x20003220`. The first has a null guard and passes A0=13 with a word from record+152 as A1. The second passes A0=14 and a word from record+156; no second null guard exists in the original. Pointer values, callback bodies/effects and event meanings remain unknown. No live record is read and no guard or fake callback is added.

Eight imports have real existing bodies. Supplying `0x58498` exposes **8 new named unresolved entries**: `0x55D00`, `0x55D3C`, `0x5605C`, `0x560AA`, `0x56326`, `0x56716`, `0x57B28`, `0x63966`. Named gaps therefore change from 1 to 8, plus two original callback sites in this unit. This reflects the expanded call chain; stubs do not hide dependencies.

Unique CODE ownership and two independent ELF readers verify **34,086 CODE + 256 DATA bytes / 11,781 instructions**, 2300 FUNC regions and 1848 relocations. Original APP remains 159 C/H files and **95.54% static byte coverage**, not functional completion.

Evidence: [audit-result-v1.json](audit-result-v1.json), [evidence-v1.json](evidence-v1.json), [summary.json](summary.json), [frames_abi.c](frames_abi.c). Installed SDK/ROM identity, physical RAM/ISA/IRQ, Flash/OTA, global initialization and callback effects remain unproved, including the inherited 4-byte startup-source gap. **No new BIN or flashability claim.**

## Recheck

Supply the hash-pinned references, prior artifacts and local tools first. Nothing is downloaded. From the project root:

```sh
python experiments/tsl9-resident-record-root-chain/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-record-root-chain/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT" --link-trial composition-v1 --output audit-result-v1.json
```

Creation names must be absent. For retained artifacts, replace the first line's trial with `--replay experiments/tsl9-resident-record-root-chain/build/native-v1` and omit `--link-trial` and `--output` from the second. No target/HOST-model/ISA/hardware execution occurs.

Potential feature: offline callback/lookup provenance and initialization diagnostics. Not implemented; no assumed live callback binding or hardware command.
