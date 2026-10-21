# OTA page reply: evidence index

[繁體中文](README.md)

This pass adds readable C/C++ for original `0x9B8E..0x9C0A`. Fresh standalone
components in both languages match all original 124 bytes / 50 instructions
after explicit ABI ordering and fixed placement. The eleven-function complete
image is unchanged; the twelfth readable function is not integrated yet.

**Source contract correction:** `69 3b` at `0x9DF4` is RV32 `C.JAL`, setting
`RA=0x9DF6` and calling `0x9B8E`, not a no-link tail jump. The old sealed
`source-review/contracts.json` field `recorded_RELA.external_incoming_role`
and the three accompanying language descriptions of a shared physical tail
are superseded by the [incoming-call correction](entry-call-correction/readme.en.md).
Old seals remain intact for traceability. This does not change the function's
own no-link T1 release tail at `0x9BF8`.

| Question | Evidence | Limit |
| --- | --- | --- |
| Original operands and flow | [Raw source](source-review/readme.en.md), with correction above | Static fields, no execution observation |
| Readable C/C++ and host model | [Implementation](implementation/readme.en.md) | Each language: 87 cases / 3,634 checks, six compiled negatives |
| Independent source effects | [Independent review](code-review/readme.en.md) | Each language: 90 cases / 6,699 checks, ten compiled negatives |
| Native calls, IR and placement | [ABI review](ABI-review/readme.en.md) | TX numeric-address witness; no unknown service implementation |
| Additional instruction ordering | [Ordering tool](../../experiments/tsl9-v4160-reply-abi-order/readme.en.md) | 28 bytes within two regions; existing compiler words, not compiler-only output |
| Original entry-role integration | [Partial-link boundary](integration-plan/readme.en.md) | Two actual objects, not a full 691-allocation image |

Default metadata checks, actual artifact replay and fresh compilation are
distinct evidence levels. Publication contains sources and selected receipt
metadata, excluding generated objects, ELF files and host executables. Build
fresh local artifacts before requesting actual replay. Windows LLVM/host
evidence does not establish Linux, macOS, shell or CI execution.

Actual chip/board identity, installed ROM/BOOT, memory and interrupts, unknown
callee register preservation, BLE OTA acceptance and recovery remain
unproved. **No flash-readiness claim; the full goal stays active.**
[Feature candidates](integration-plan/readme.en.md) remain separate from
implemented functions.
