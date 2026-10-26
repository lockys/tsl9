# Registered task callback candidate C/C++

[繁體中文](README.md) · [Previous SNV initialization](../tsl9-resident-snv-initialization/readme.en.md)

Two complete public WCH SDK V1.31 callbacks are reconstructed,with a static argument check of the existing original APP Flash helpers. **Installed compatibility remains unproved;no flashable BIN was produced.**

| Body | Candidate Flash range | Bytes |
| --- | --- | ---: |
| Registered callback1 | `0x432A4..0x43326` | 130 |
| Registered callback2 | `0x43326..0x433A8` | 130 |

[C/C++ source](resident_task_callbacks.c): **260 bytes/104 instructions**,26 positive FUNC regions and16 relocations. Actual C11/C++17 objects are identical;every byte matches after original-address encoding. No custom instruction is selected. These regions require original register/private execution context;they are not ordinary callable C APIs.

## Observed instructions

- Registration stores `0x43C1A`/`0x43C30`/`0x43C42` write `0x432A4`/`0x43326`/`0x43326`. The numeric CODE pointers now have real reconstructed bodies;original-address execution linking remains undone.
- Both callbacks select `record_array + 12*(16*entry_A0 + bit)` and handle at most one event per return. Call `0x432EA` has a null guard;`0x43390` does not. Callback A0 is loaded from the selected record's second word.
- Callback1 tests its third word at `record_array + 12*bit + 8`,a different index formula. This difference is preserved without diagnosing or correcting it. Callback2 receives a message when bit15 is set and passes a nonnull result to the real deallocator,whose result is ignored.

## Flash argument evidence

Four existing complete APP bodies cover **226 bytes/90 instructions**. This section adds no APP CODE.

- `0x1979A` transforms arguments into `copy(buffer,address,num << 2)` via pointer storage `0x4004C`. The SDK candidate points there to reconstructed `0x20000332`. A normal return yields numeric0 without checking copied contents.
- `0x197BE → 0x18EF2` passes the saved buffer pointer in A1/A2;the helper replaces A2 with256 before its data loop. Pointer reuse alone therefore does not establish an ABI error. The incoming num is not forwarded as this helper's transfer count.
- With normally terminating polls and valid register/memory contracts,the helper loads64 words from256 consecutive source bytes at A1 and performs64 CPU word stores to256 bytes starting at `(A0 & 0xFFFFFF00)`. The erase helper also clears the low8 address bits. **This does not prove physical Flash commit,capacity or safe flashability.**
- A256-byte SNVBlock is numerically consistent with the fixed transfer size. Other block sizes,ancillary helpers,physical mappings,poll termination,IRQ/stack/alias contracts remain open. No Flash read/write was executed.

## Partial composition and limits

An actual nonloadable ET_REL composition with the prior1568-byte candidate yields **1828 bytes/654 instructions**,164 positive FUNC regions and120 relocations in both languages. The real deallocator resolves one import. **Message receive `0x2000028C` remains a named unresolved dependency**;no stub fills it. Every input byte,symbol and relocation is retained.

Raw RAM,record callbacks,installed ROM/ISA,IRQ and OTA compatibility remain open. This is not linked into the APP. Formal APP byte coverage stays **95.54%**,not functional completion. Callback lifecycle and persistence diagnostics are possible additions,not implemented features.

Evidence: [audit-result-v1.json](audit-result-v1.json),[summary.json](summary.json),[original SDK instructions](evidence-v1.json).

## Reproduce

Provide the original APP,SDK carrier,header/instruction references and preceding retained build artifacts required by [spec-v1.json](spec-v1.json)/[evidence-v1.json](evidence-v1.json) and the audit. Original SDK inputs and native artifacts are not included in this commit. Nothing downloads them automatically. From the project root with the hash-pinned Windows NDK LLVM:

```sh
python experiments/tsl9-resident-task-callbacks/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-task-callbacks/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

Trial names must be fresh. With retained artifacts,use `--replay experiments/tsl9-resident-task-callbacks/build/native-v1` for the first command and omit `--link-trial` for the second. No target,HOST model or ISA execution,hardware access or vendor API traffic was performed.
