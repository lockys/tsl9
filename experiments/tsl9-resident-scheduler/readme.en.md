# RAM-JT0 scheduler candidate C/C++

[繁體中文](README.md) · [Registration](../tsl9-resident-task-registration/readme.en.md) · [Queue/events](../tsl9-resident-message-queue/readme.en.md)

Public SDK V1.31 calls TMOS_SystemProcess through RAM table index0. Actual initialization stores **0x200007D0** at0x20000000. The earlier0x200004FA candidate is a callee,not this table's main entry. **The installed device ROM remains unidentified.**

[C/C++ source](resident_scheduler.c)reconstructs the complete **438 bytes/150 instructions** at0x200007D0..0x20000986,with39 positive FUNC regions and30 relocations. Actual C11/C++17 objects are identical;every byte matches after original-address encoding. Fourteen conditional Xwchc ports are checked against primary definitions and28 official vectors. Original register/private execution context is required.

## Table and code provenance

- The official header defines RAM_BASE_ADDRESSS=0x20000000 and uses RAM indices0/1/2 for TMOS_SystemProcess/BB IRQ/LLE IRQ.
- V1.31 stores0x200007D0/0x2000251C/0x20002E34 at instructions0x6DE1C/0x6DE26/0x6DE3C. These are explicit stores;the code-copy bias cannot simply be applied to RAM0.
- Assuming normal seed and first word-copy completion,the scheduler maps from captured Flash0x40A40..0x40BF6. Later second-copy/zero numeric spans do not overlap this body or the three table words.
- The retained V1.31 sparse-source contract still records a4-byte second-copy gap at0x6EB2C..0x6EB30. Later zeroing cannot prove that source read completes. **No hole is filled or full startup completion claimed.** Another234 bytes of startup/seed fragments are checked,not compiled into a new BOOT.

## Event dispatch

- Current task index0x2000319C and registered count0x2000319D select pending events. The scheduler takes an event halfword,clears its slot and calls handler-array[current_task] with A0=task index/A1=event. No handler null check exists here.
- It clears mask halfword0x200031DC before the call. After return,it **reloads the current task index** and stores the low16 bits of `(returned_A0 & ~live_clear_mask) | live_pending_event` into the reselected slot. Callback reentry or concurrent mutation may prevent identifying it with the original slot.
- This matches the shared halfword used by tmos_stop_task. Four opaque callback sites still require lifetime/effect contracts.
- The complete local CFG reaches the registered-handler call at most once per normal entry. Nested scheduler calls through callbacks are excluded. Its own32-byte frame balances at the normal return and external tail;this is **not a callee or whole-program IRQ stack budget**.

## Partial composition and limits

With the preceding2312-byte candidate,the actual nonloadable C/C++ ET_REL objects contain **2750 bytes/971 instructions**,247 positive FUNC regions and181 relocations. Every input byte,symbol and relocation is retained.

Four real named callees remain unresolved:RAM0x200004FA/0x2000061A/0x20002610 and Flash0x63DD0. No stub,APP integration or new BIN is provided. RAM/callback ownership,full startup,atomicity,IRQ/stack,installed ROM/ISA,Flash and OTA remain open. APP byte coverage stays **95.54%**.

Evidence: [audit-result-v1.json](audit-result-v1.json),[summary.json](summary.json),[original instructions/startup fragments](evidence-v1.json). Event-merge and callback-reentry diagnostics are possible additions,not implemented features.

## Reproduce

Provide the original APP,SDK/header/instruction references and preceding retained artifacts required by [spec-v1.json](spec-v1.json)/[evidence-v1.json](evidence-v1.json) and the audit. Original SDK inputs and native artifacts are not included in this commit. Nothing downloads them automatically. From the project root using the hash-pinned Windows NDK LLVM:

```sh
python experiments/tsl9-resident-scheduler/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-scheduler/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

Trial names must be fresh. With retained artifacts,use `--replay experiments/tsl9-resident-scheduler/build/native-v1` for the first command and omit `--link-trial` for the second. No target,HOST model or ISA execution,hardware access or vendor API traffic was performed.
