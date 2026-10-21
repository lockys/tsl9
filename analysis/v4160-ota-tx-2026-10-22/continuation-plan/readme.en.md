# Trace packet construction through to actual transmission

[繁體中文](README.md)

## Confirmed static boundaries

`check.py --firmware <absolute official BIN path>` rereads official ID2966 V4.1.60 and decodes four AUIPC/ADDI bit-field pairs. Sites `0x86C0`, `0x876C`, `0x8AD6` and `0x8E9C` each form `0x2000B18C`. It also checks the transmit function's two pointer loads from `0x4013C` and final pointer load from `0x40050`. Seven operand mutations are rejected by those same predicates. There is no CPU state model, ISA emulation or network operation.

The recorded object owners are `callback_8614`, `code_continuation_8a56` and `init_8e88`; the first has two selected references. Original `0x8614..0x888C`, 632 bytes, is a follow-up candidate. Its memory effects, events and ROM calls still need instruction-level analysis. Shared buffer addresses alone do not prove that it completes Bluetooth transmission. These four selected references are not a complete inventory of computed addresses or of the entire image.

## Candidate interpretation, not installed-ROM proof

Previously saved local WCH V1.30 and V1.40 headers both declare function-table base `0x40034`, JT7 as `tmos_set_event`, and JT66 as `GATTServApp_ReadCharCfg`. These numeric slots suggest notification-configuration gating followed by buffer construction and task-event submission. `sdk-candidates.json` records exact local header hashes, line numbers and candidate types. No documentation was downloaded this round.

This does not identify the installed version. A candidate two-argument prototype cannot eliminate the actual A2/A3 residues at the original calls. Pointer words, callee bodies, return types, register and SP/GP preservation remain unproved. Constructing or handing off a packet does not prove actual transmission, reception or acceptance.

## Feature candidates

1. **Offline packet preflight and preview:** show command, payload size, header and checksum; reject original entry payloads over 1039 bytes. No BLE connection is needed. Synthetic host data still does not prove ROM behavior.
2. **Update wait-reason display:** distinguish notification configuration, buffer waiting and update-reply waiting in the app. Original states and response meanings must be confirmed first. The original path-dependent A0 must not be replaced by an assumed common success/failure status.

These are proposals, not completed hardware features. Remaining work includes event consumers, GATT ingress, the complete OTA handler, and board/ROM/BOOT/memory/interrupt/OTA acceptance and recovery evidence. No flashability claim is added.
