# Task-0 clock/status callback conditions

[繁體中文](README.md)

Check **3 complete existing SDK functions / 1,816 bytes / 592 instructions**, joining the remaining 12 register transfers to original APP configuration evidence. No new target C/C++, compilation or BIN this round.

| Family | Sites | Conditional conclusion |
|---|---:|---|
| Raw clock | 10 | After the original nonnull 16-byte clock configuration is accepted/copied and remains stable, `200031E0 → 191C6` |
| Status | 2 | After the known BLE configuration clear/copy, stable zero at `20003220` makes the original guards skip `20000EC6` / `2000137A` |

These sites load the **raw-clock slot** at `200031E0`, not a different clock-provider layer. Recheck original APP `191C6`'s complete 90-byte body and configuration/native witnesses. Physical MMIO meaning, coherent sampling and frequency remain unproved. Earlier heap-call status values, global initialization ordering and other writers remain open.

Execution precondition: `20000F8E` reads the clock and `20000F90` saves it; `20000F92` reloads the pointer, `20000F96` calls again, and `20000F98` loops while values match. **There is no explicit retry bound or timeout: a different observed clock value is required to leave this loop.** Correct pointer binding, zero named UND and local byte checks do not prove termination. A constant-return stub cannot replace the real clock behavior.

Original-address byte re-encoding, complete CFGs, own frames, finite may-reaching-definitions and original APP configuration contracts pass. Retain every pointer definition and both actual null guards in the [site ledger](ledger-v1.json).

**Only the 63 register-transfer sites in this partial SDK object have at least one evidenced conditional domain**: 51 targets/target sets and 12 skips/caller gates. This does not prove universal live binding, the entire APP, unselected code or functional completion.

The union stays **40,874 CODE + 392 DATA bytes**; APP static coverage stays **95.54%**. Four startup source bytes, physical chip, ROM, RAM, IRQ, Flash, OTA, clock progress and complete behavior evidence remain missing. No target, model, emulator or hardware execution; **flash compatibility remains unproved**.

Feature candidate: read-only clock-progress and initialization diagnostics before updating. Proposal only; no hardware test performed.

[Checker](verify-v1.py) · [Evidence index](evidence-v1.json) · [Receipt](verification-v1.json) · [Summary](summary.json)

Read-only revalidation from the project root, using retained references, native objects and checked LLVM:

```sh
python3 experiments/tsl9-resident-task0-clock-status-binding/verify-v1.py --tool-dir "$LLVM_BIN"
```

Use `py -3` on Windows if needed. Public text receipts do not replace references or build artifacts.
