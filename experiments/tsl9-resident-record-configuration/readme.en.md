# Record configuration and the 0x58788 tail chain

[繁體中文](README.md) · [Previous comparison helper](../tsl9-resident-record-comparison/README.md) · [Allocation contract](../tsl9-scheduler-allocation-contract/readme.en.md)

[C/C++](resident_record_configuration.c) adds **3 complete candidate SDK bodies / 1,028 bytes / 355 instructions**. Original register context is required. This is neither a HOST API nor original manufacturer C source.

| Original half-open range | Bytes / instructions | Own frame |
| --- | --- | --- |
| `0x58788..0x588B4` | 300 / 109 | 16 bytes |
| `0x58744..0x58788` | 68 / 25 | 16 bytes |
| `0x581CE..0x58462` | 660 / 221 | 32 bytes |

Actual C11/C++17 objects match: 69 positive FUNC regions and 59 relocations (45 direct controls, 7 far calls). Forty-five Xwchc ports agree with primary definitions and the existing 52 positive vectors. Every byte matches after original-address normalization. Complete CFG instructions are reachable and own frames balance at exits. The adjacent function starting at `0x58462` is excluded.

## Evidence

- The actual `0x58788` call in the original `0x58C52` caller is retained in `contract.actual_58788_call_sites` in [audit-result-v1.json](audit-result-v1.json).
- `0x58890..0x5889A` restores the original record argument, saved registers and RA, then releases the 16-byte frame. `0x5889C` remains **JAL zero → 0x58744**, a no-link tail. `0x5874C` subsequently makes a normal call to `0x581CE`.
- `0x58744` reads record+148 and writes that word to base+112 through pointer slot `0x2000353C`. Through pointer slot `0x20003508`, it ORs word+0 with `0x08000000` and clears the low two bits of word+44. These are encoded access relations; physical register names, radio effects and hardware success remain unassigned.
- Depending on record byte+57 equaling 8, `0x581CE` writes byte+6 as `0xB5` or `0xB4`. Both actual calls to existing `0x63B0E` use A1=34. The original `DIVU` at `0x5840C` and list-next load at `0x58442` remain intact. A nonzero runtime divisor, valid memory and traversal termination are unproved. No assumed C division or bounded execution model replaces them.

All six imports have real existing bodies; no new named gap or stub is introduced. Unique CODE ownership and two independent ELF readers verify **31,468 CODE + 256 DATA bytes / 10,887 instructions**, 2136 FUNC regions and 1707 relocations. Named gaps decrease from 3 to **2**: `0x58498` and `0x58988`. They expose further dependencies, so this count is not full execution-chain completion.

Evidence: [audit-result-v1.json](audit-result-v1.json), [evidence-v1.json](evidence-v1.json), [summary.json](summary.json), [frames_abi.c](frames_abi.c). Original APP remains 159 C/H files and 95.54% static byte coverage. Physical ROM/RAM/ISA/IRQ, Flash/OTA and global initialization ordering remain unproved, including the inherited 4-byte startup-source gap. **No new BIN or flashability claim.**

## Recheck

Supply the hash-pinned references, prior artifacts and local tools first. Nothing is downloaded. From the project root:

```sh
python experiments/tsl9-resident-record-configuration/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-record-configuration/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT" --link-trial composition-v1 --output audit-result-v1.json
```

Creation names must be absent. For retained artifacts, replace the first line's trial with `--replay experiments/tsl9-resident-record-configuration/build/native-v1` and omit `--link-trial` and `--output` from the second. No target/HOST-model/ISA/hardware execution occurs.

Potential feature: offline comparison of record fields and configuration-write provenance. Not implemented; no physical feature before register meaning is established.
