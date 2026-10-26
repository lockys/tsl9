# Task registration candidate C/C++

[繁體中文](README.md) · [SDK queue/events](../tsl9-resident-message-queue/readme.en.md) · [Conditional RAM layout](../tsl9-resident-task-layout-contract/readme.en.md)

Official slot19 binds TMOS_ProcessEventRegister to0x43C4E. Adjacent slot28 BLE_LibInit starts at0x43C7E. The complete intervening **48 bytes/16 instructions** are reconstructed,excluding adjacent bodies. **Installed compatibility remains unproved;no flashable BIN was produced.**

[C/C++ source](resident_task_registration.c):4 positive FUNC regions and2 relocations. Actual C11/C++17 objects are identical;every byte matches after original-address encoding. Three conditional Xwchc byte ports are checked against primary definitions and28 official vectors. Original register/private execution context is required.

## Behavior and conditions

- Read count byte0x2000319D and capacity byte0x2000319E. If count≥capacity,return255 without stores. Otherwise store count+1,write entry A0 to handler-array+4*old_count,and return old_count.
- The handler pointer comes from0x200031C4. With a stable valid4*capacity-byte array and no concurrent mutation,success gives count+1≤capacity without byte wrap. Sequential execution preserves count≤capacity when initially true. An initially excessive count is not repaired.
- **The function checks neither null nor callable-handler validity.** Instruction0x43C6A stores count before0x43C72 stores the handler word. No encoded gate save/restore or FENCE sequence exists. A successful return does not prove handler validity or atomic registration.
- Conditional capacity29 and three completed built-in registrations leave26 numerically available successful registrations. This still assumes unchanged count/pointers after SNV. Actual IRQ state and concurrent observation order remain unproved.

## Actual partial composition

With the preceding2264-byte candidate,the actual nonloadable C/C++ ET_REL compositions contain **2312 bytes/821 instructions**,208 positive FUNC regions and151 relocations. Every input byte,symbol and relocation is retained. Slot19 has a real body;zero named UND symbols does not close runtime dependencies.

This is not linked into the APP. RAM/callback ownership,atomicity,whole-program IRQ/stack,installed ROM/ISA,Flash and OTA remain open. Formal APP byte coverage stays **95.54%**,not functional completion. Serialized registration and callable-handler diagnostics are possible additions,not implemented features.

Evidence: [audit-result-v1.json](audit-result-v1.json),[summary.json](summary.json),[original instructions and official bindings](evidence-v1.json).

## Reproduce

Provide the original APP,SDK/header/instruction references and preceding retained artifacts required by [spec-v1.json](spec-v1.json)/[evidence-v1.json](evidence-v1.json) and the audit. Original SDK inputs and native artifacts are not included in this commit. Nothing downloads them automatically. From the project root using the hash-pinned Windows NDK LLVM:

```sh
python experiments/tsl9-resident-task-registration/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-task-registration/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

Trial names must be fresh. With retained artifacts,use `--replay experiments/tsl9-resident-task-registration/build/native-v1` for the first command and omit `--link-trial` for the second. No target,HOST model or ISA execution,hardware access or vendor API traffic was performed.
