# Conditional callback binding

[繁體中文](README.md) · [Current C/C++ bodies](../tsl9-resident-scheduled-record-callback/readme.en.md)

This study joins the candidate SDK's **51 register-transfer sites** to original APP configuration, registration and table provenance. It checks **14 complete SDK functions / 4,730 bytes / 1,629 instructions**. The [receipt](verification-v1.json) and [per-site ledger](ledger-v1.json) retain addresses, conditions and witnesses.

| Path | Sites | Conditional result |
| --- | ---: | --- |
| Raw clock | 7 | Target `0x191C6` after accepted original clock configuration with stable slots |
| Clock provider | 2 | Target `0x43D62` in the specified TimerInit caller/registration context |
| Sample / calibration | 4 | Targets `0x197F0` / `0x197B8` after the original BLE copy with stable fields |
| Status | 5 | Original guards skip calls when the known post-copy staCB remains zero |
| Scheduled record | 1 | `0x43390` calls `0x56CDC` under the specified producer/table/event conditions |
| Not joined here | 32 | No missing-function count is inferred; earlier conditional analyses remain valid |

`0x43538` calls the provider, which then calls raw clock at `0x43D7A`: these are distinct stages. TimerInit calls calibration at `0x43F60` **before** validating clock configuration; successful clock configuration is not a prerequisite for that call.

Status claims apply only to the known post-copy zero-value domain. The earlier heap-call value remains unproved. The first `0x59E0C` guard skips `0x59E20`; there is no added second null guard. The scheduled route covers event bits 0..14; IDs31/47 are outside that proof, not declared unusable.

Fresh checks cover original bytes, complete CFGs, pointer flow, existing C11/C++17 artifacts, independent ELF readers and the original APP callback configuration contract. Older recursive audit receipts are hash-pinned; that entire older chain was not rerun here. All bindings require the original private ABI, valid disjoint memory, normal returns and no asynchronous overwrite, among other listed conditions. No live binding was observed.

No target C/C++, compilation or BIN was added. The existing candidate remains **35,324 CODE + 256 DATA bytes / 12,195 instructions / 0 named UND**. APP static byte coverage remains **95.54%**, not functional completion. Installed ROM/RAM/ISA/IRQ/Flash/OTA compatibility, global initialization order and the inherited four-byte startup-source gap remain unresolved. **This is not flash-ready firmware.**

A possible future feature is read-only callback-route diagnostics. This study adds no hardware control or original-behavior changes.

Run offline from the project root, with `LLVM_BIN` pointing to the existing LLVM tools:

```sh
python experiments/tsl9-resident-callback-binding-ledger/verify-v1.py --tool-dir "$LLVM_BIN"
```

The verifier does not execute the target, a HOST model, ISA emulation, hardware or network operations.
