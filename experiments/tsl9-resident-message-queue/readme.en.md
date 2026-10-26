# Message queue and event candidate C/C++

[繁體中文](README.md) · [Previous task callbacks](../tsl9-resident-task-callbacks/readme.en.md)

The public WCH SDK V1.31 message receiver and its complete named dependencies are reconstructed. **Installed ROM/RAM/ISA compatibility remains unproved;no flashable BIN was produced.**

| Body | Candidate range | Bytes |
| --- | --- | ---: |
| Message receive | Conditional RAM `0x2000028C..0x20000314` | 136 |
| Unlink node | Flash `0x4319C..0x431BA` | 30 |
| Set event | Flash `0x4354A..0x4358A` | 64 |
| Clear event | Flash `0x4358A..0x435CE` | 68 |
| tmos_stop_task | Flash `0x439A8..0x43A14` | 108 |
| Timer lookup | Conditional RAM `0x20000314..0x20000332` | 30 |

[C/C++ source](resident_message_queue.c): **436 bytes/151 instructions**,40 positive FUNC regions and29 relocations. Actual C11/C++17 objects are identical;every byte matches after original-address encoding. Six conditional Xwchc ports are checked against primary definitions and28 official vectors. Original register/private execution context is required;these are not ordinary callable C APIs.

## Instruction evidence

- Receive walks the list at `0x20003198`,selects the first message with a matching task tag and checks for a later match. A later match sets official `SYS_EVENT_MSG=0x8000`;otherwise it calls the real tmos_stop_task. Helper return values are unused.
- Unlink updates the head or predecessor link,clears the selected payload[-8] word and sets payload[-2] to0xFF. It neither allocates nor frees. The tag matches the existing deallocator guard,subject to valid ownership and no intervening mutation.
- Set/clear event checks task-count byte `0x2000319D`,then uses the halfword-array pointer at `0x200031E4` with offset2*taskID. Set uses OR;clear uses AND NOT. Valid task IDs return0;out-of-range IDs return3.
- tmos_stop_task searches the list at `0x200031E8` for task/event,clears a found node's event halfword and still calls clear-event. It ignores that result and returns0 or6 based on lookup success. This behavior is preserved rather than replacing it with a simple event clear.
- Original MMIO `0x4002420C` save/zero/restore and FENCE.I ordering are retained. Physical semantics,atomicity and IRQ effects remain unproved. List termination requires valid stable acyclic lists and is not proved here.

## Partial composition and limits

An actual nonloadable ET_REL composition with the prior1828-byte candidate yields **2264 bytes/805 instructions**,204 positive FUNC regions and149 relocations in both languages. The preceding receiver import resolves to its real new body. Every input byte,symbol and relocation is retained.

**Zero named UND symbols does not close runtime dependencies.** Raw RAM/heap/callback ownership,installed ROM/ISA,IRQ,stack,Flash and OTA compatibility remain open. This is not linked into the APP. Formal APP byte coverage stays **95.54%**,not functional completion. The previous conditional fixed256-byte Flash CPU-transfer evidence is unchanged.

Evidence: [audit-result-v1.json](audit-result-v1.json),[summary.json](summary.json),[original SDK instructions/vectors](evidence-v1.json). Per-task message backlog and queue/event consistency diagnostics are possible additions,not implemented features.

## Reproduce

Provide the original APP,SDK carrier,header/instruction references and prior retained build artifacts required by [spec-v1.json](spec-v1.json)/[evidence-v1.json](evidence-v1.json) and the audit. Original SDK inputs and native artifacts are not included in this commit. Nothing downloads them automatically. From the project root using the hash-pinned Windows NDK LLVM:

```sh
python experiments/tsl9-resident-message-queue/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-message-queue/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

Trial names must be fresh. With retained artifacts,use `--replay experiments/tsl9-resident-message-queue/build/native-v1` for the first command and omit `--link-trial` for the second. No target,HOST model or ISA execution,hardware access or vendor API traffic was performed.
