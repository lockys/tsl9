# Record transition and the two 0x58988 tails

[繁體中文](README.md) · [Previous configuration chain](../tsl9-resident-record-configuration/README.md) · [Allocation contract](../tsl9-scheduler-allocation-contract/readme.en.md)

[C/C++](resident_record_transition.c) adds **2 complete candidate SDK bodies / 918 bytes / 322 instructions**. Original register context is required. This is neither a HOST API nor original manufacturer C source.

| Original half-open range | Bytes / instructions | Own frame |
| --- | --- | --- |
| `0x58988..0x58C52` | 714 / 251 | 32 bytes |
| `0x580A4..0x58170` | 204 / 71 | 32 bytes |

Actual C11/C++17 objects match: 51 positive FUNC regions and 47 relocations (39 direct controls, 4 far calls). Seventeen Xwchc ports agree with primary definitions and the existing 52 positive vectors. Every byte matches after original-address normalization. Complete CFG instructions are reachable and own frames balance at exits. Adjacent `0x58170` and caller `0x58C52` are outside these bodies.

## Evidence

- The actual `0x58988` call in original caller `0x58C52` is retained in `contract.actual_58988_call_sites` in [audit-result-v1.json](audit-result-v1.json).
- `0x58B6C` remains **JAL zero → 0x58788**; `0x58C2E` remains **JAL zero → 0x58744**. Both paths restore the original record argument and RA, then release their 32-byte frame. They are not ordinary C calls. Both target complete real bodies supplied previously.
- The first path retains the bit0-zero branch at `0x58B56`. The second retains the equality-to-1 guard at `0x58C1A` after the comparison helper. Numeric polarities are not assigned physical success/failure meanings.
- `0x580A4` obtains bases through original slots `0x2000353C` and `0x20003508`. Encoded requests write `0x8E89BED6` to second-base+8 and `0x00555555` to second-base+4. It writes record byte+6 as `0xB3`, then normally calls the real existing `0x63C54` provider with A1=255 and A2=0. Physical register names, radio behavior and hardware success remain unproved.

All nine imports have real existing bodies; no new named gap or stub is introduced. Unique CODE ownership and two independent ELF readers verify **32,386 CODE + 256 DATA bytes / 11,209 instructions**, 2187 FUNC regions and 1754 relocations. Named gaps decrease from 2 to **1**, `0x58498`. This entry exposes further dependencies; the count cannot establish execution-chain or firmware completion.

Evidence: [audit-result-v1.json](audit-result-v1.json), [evidence-v1.json](evidence-v1.json), [summary.json](summary.json), [frames_abi.c](frames_abi.c). Original APP remains 159 C/H files and 95.54% static byte coverage. Physical ROM/RAM/ISA/IRQ, Flash/OTA, global initialization and callback effects remain unproved, including the inherited 4-byte startup-source gap. **No new BIN or flashability claim.**

## Recheck

Supply the hash-pinned references, prior artifacts and local tools first. Nothing is downloaded. From the project root:

```sh
python experiments/tsl9-resident-record-transition/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-record-transition/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT" --link-trial composition-v1 --output audit-result-v1.json
```

Creation names must be absent. For retained artifacts, replace the first line's trial with `--replay experiments/tsl9-resident-record-transition/build/native-v1` and omit `--link-trial` and `--output` from the second. No target/HOST-model/ISA/hardware execution occurs.

Potential feature: offline explanations of original state branches and configuration provenance. Not implemented; no physical success label or control command before protocol meaning is proved.
