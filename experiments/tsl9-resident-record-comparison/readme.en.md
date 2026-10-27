# Record comparison helper and 0x588B4 handler

[繁體中文](README.md) · [Previous bodies](../tsl9-resident-task-final-handlers/README.md) · [Allocation contract](../tsl9-scheduler-allocation-contract/readme.en.md)

[C/C++](resident_record_comparison.c) reconstructs two complete candidate SDK bodies, **592 bytes / 211 instructions**. Original registers and context are required. This is neither a HOST API nor recovered original manufacturer C source.

| Original half-open range | Bytes / instructions | Own stack frame |
| --- | --- | --- |
| `0x588B4..0x58988` | 212 / 77 | 32 bytes |
| `0x585C8..0x58744` | 380 / 134 | 32 bytes |

Actual C11/C++17 objects match: 59 positive FUNC regions and 62 relocations (46 direct controls, 7 far calls, 1 far tail). All bytes match after original-address normalization. Fifteen Xwchc ports agree with primary definitions and the existing 52 positive vectors. All CFG instructions are reachable, own frames balance at exits, and late reachable arms after early RETs remain intact.

## Evidence

- The complete original `0x58C52` caller contains an encoded call to `0x588B4`; its PC is retained in `contract.actual_588B4_call_sites` in [audit-result-v2.json](audit-result-v2.json).
- `0x58956` calls `0x585C8`. The guard at `0x5895A` skips `0x58498` on zero A0 and calls it on nonzero A0. No physical success/failure meaning is assigned to that polarity.
- The helper reads halfwords at offsets `+2/+4/+6/+8`, combines each high half with a 16-bit shift into A0/A1, restores RA at `0x586F4`, releases its 32-byte frame at `0x586FC`, then uses **AUIPC t1 / JALR zero** at `0x586FE/0x58702` to tail-transfer to the real existing RAM `0x20002276` provider. This remains a no-link tail, not an ordinary C call.
- Five imports have real existing bodies. `0x58498` remains genuinely unresolved, without a stub. Adjacent functions such as `0x58744` are outside these two complete bodies and are not supplied here.

Unique CODE ownership and two independent ELF readers verify the composition: **30,440 CODE + 256 DATA bytes / 10,532 instructions**, 2067 FUNC regions, 1648 relocations. Named gaps decrease from 4 to **3**: `0x58498`, `0x58788`, `0x58988`. Those entries expose further dependencies; the named-gap count is not full execution-chain coverage.

Evidence: [audit-result-v2.json](audit-result-v2.json), [evidence-v1.json](evidence-v1.json), [summary.json](summary.json), [frames_abi.c](frames_abi.c). Original APP sources remain 159 C/H files with 95.54% static byte coverage. Installed SDK identity, physical ROM/RAM/ISA/IRQ, Flash and OTA compatibility remain unproved, including the inherited 4-byte startup-source gap. **No new BIN or flashability claim.**

## Recheck

Supply the hash-pinned references and prior build artifacts first. Nothing is downloaded. From the project root, set `LLVM_BIN` and `REFERENCE_ROOT` to local tools and existing references:

```sh
python experiments/tsl9-resident-record-comparison/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-record-comparison/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT" --link-trial composition-v1 --output audit-result-v2.json
```

Creation names must be absent. For retained artifacts, replace the first line's trial with `--replay experiments/tsl9-resident-record-comparison/build/native-v1` and omit `--link-trial` and `--output` from the second. No target/HOST-model/ISA/hardware execution occurs.

Potential feature: offline status-code diagnostics linked to original branches and PCs. Not implemented; no physical success label before the protocol meaning is proved.
