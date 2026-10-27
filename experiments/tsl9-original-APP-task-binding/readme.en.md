# Original APP task registration and dispatch

[繁體中文](README.md) · [Previous initialized data](../tsl9-resident-initial-data-prefix/readme.en.md) · [Previous callback ledger](../tsl9-original-clock-random-idle-binding/readme.en.md)

This study checks **five complete APP functions / 896 bytes** and **seven complete SDK functions / 1,536 bytes**: **2,432 bytes / 827 instructions**. It connects original APP handler `0x1995C`, candidate registration API `0x43C4E` and scheduler site `0x2000090A`. [Full receipt](verification-v1.json) · [Cumulative ledger](ledger-v1.json)

## Registration and table provenance

Original main calls BLE initialization at `0x8EA8`, then `0x19B16` at `0x8EAC`. The APP forms callback `0x1995C` at `0x19B26` and registers it at `0x19B2E` through candidate slot `0x40080 → 0x43C4E`.

If candidate initialization observes count=0 at `0x43C06`, valid allocation completes normally, and no intervening registration or overwrite occurs, the first four handlers are:

| Task ID | Table value | Source |
| ---: | --- | --- |
| 0 | `0x432A4` | Candidate initialization |
| 1, 2 | `0x43326` | Candidate initialization |
| 3 | `0x1995C` | Subsequent original APP registration |

Handler-base slot `0x200031C4` has stride4; pending-event-base slot `0x200031E4` has stride2. For unsigned-byte x, `n=3*((x>>2)+(x&3))+14` yields n14..212. Under stable n/p and valid allocation, the first four handlers' 16 bytes and events' eight bytes fit their respective suffixes. **Actual capacity, ownership and all subsequent writes remain unproved.**

Registration returns 255 without writing a handler when capacity≤count. The APP saves that result to **live GP+388** and schedules without checking rejection. Task3 is therefore conditional, not a physical observation or universal guarantee.

The scheduler loads `table+4*taskID`, passing taskID and the pre-clear 16-bit event. It then reloads live task index, clear mask and pending events, storing `low16((returned & ~fresh_mask) | fresh_pending)`. If a callback changes the index, applying the return to the original task is not guaranteed by this proof.

## Original handler priority

Only one priority arm runs per invocation. These are original instruction semantics, not an execution test:

| Priority | Event bit | Original action | Normal return |
| ---: | --- | --- | --- |
| 1 | `0x8000` | Receive; deallocate only if nonnull | `events XOR 0x8000` |
| 2 | `0x0001` | Acknowledge the bit | `events XOR 1` |
| 3 | `0x2000` | Candidate `0x641B0`, calibration `0x197B8`, reschedule the same bit | `events XOR 0x2000` |
| 4 | `0x4000` | Reschedule the same bit | `events XOR 0x4000` |
| Other | Unmatched | Normal return | 0 |

Initial scheduling and bit13 pass delay `0x2EE00`; bit14 passes 1600. **These are raw values, not proved physical timing, calibration effects or successful rescheduling.** The handler does not check scheduling results. Initial scheduling at `0x19B54` is `jr t1` after frame release, preserving a tail transfer without a new link RA.

Seven original APP indirect API call/tail sites also have real candidate bodies at `0x43C4E`, `0x2000028C`, `0x431BA`, `0x641B0` and `0x43728`. They are not added to the SDK's 51-site denominator. The cumulative SDK ledger covers **36 / 51 sites**, leaving 15 unjoined; this is not a missing-function count.

## C/C++ and limitations

The [existing APP C/C++](../../src/native/startup/resident_startup.c) is retained. Two independent ELF readers check its original-address native diagnostic; actual candidate SDK CODE ownership is checked too. New [ABI assertions](task_handler_abi.c), compiled as RV32 C11/C++17, check the saved primary header's `uint16_t (*)(uint8_t, uint16_t)` declaration. Objects contain no allocated CODE/DATA, functions or providers. **This does not prove the installed private ABI or add an executable adapter.**

The result requires matching ROM, original GP/stack/ABI, valid disjoint memory, normal returns, stable tables and no IRQ/reentrant overwrite. Global initialization before all dispatch, physical ROM/RAM/ISA/IRQ/Flash/OTA compatibility, calibration effects and the four-byte startup-source gap remain unresolved. The candidate stays at **35,324 CODE + 392 DATA bytes**; APP static coverage remains **95.54%**. **This is not flash-ready firmware.**

A possible feature is offline registration-rejection, event-priority and rescheduling diagnostics. No UI or hardware control was added.

First build ABI assertions, then verify offline with the pinned references and prior artifacts:

```sh
python experiments/tsl9-original-APP-task-binding/build-v1.py --tool-dir "$LLVM_BIN" --build
python experiments/tsl9-original-APP-task-binding/verify-v1.py --tool-dir "$LLVM_BIN" --write-receipts
```

For existing artifacts omit `--build` and `--write-receipts` for read-only verification.
