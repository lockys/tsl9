# Real dependencies of the task-0 RAM callback

[繁體中文](README.md)

Supply the previous three missing callees and their shared helper using register-context C/C++ with explicit instruction ports: **four complete bodies / 1,892 bytes / 626 instructions**. Installed ROM and physical RAM mapping remain unproved.

| Candidate original interval | Bytes | Own frame |
|---|---:|---:|
| `436A8..43728` | 128 | 32 |
| `20000D50..20001122` | 978 | 32 |
| `20001122..2000138E` | 620 | 32 |
| `200014C6..2000156C` | 166 | 48 |

RAM bodies trace actual SDK Flash bytes through the existing startup copy mapping. Full CFGs retain reachable branches after the first return, two released-frame tails and 26 conditional Xwchc operations. These are not ordinary HOST-callable APIs.

`436A8` requires an ID in 0..15 and a nonzero callback word. It looks up task 0 with event `low16(1 << ID)`. If found, it clears the event and writes entry A1 into timer record `+8`. **A null lookup also returns zero without that update.** An invalid ID or empty callback returns 2. Zero does not prove an actual timer update or physical success; time units remain unproved.

Actual C11/C++17 objects are identical. Original-address re-encoding compares every byte; complete CFG/frame checks, independent ELF readers and nonloadable partial linking pass. The union contains **38,744 CODE + 392 DATA bytes / 13,347 instructions**. Genuine bodies resolve all three previous UND symbols. Two deeper named gaps remain: **`56972` and `2000156C`**, with no stubs.

The new bodies introduce **11 unjoined register transfers**. This partial SDK object now has **62 sites, 51 with at least one evidenced conditional domain**. The larger denominator reflects actual added code. It is neither functional completion nor a missing-function count, and excludes the entire APP and calls inside unprovided callees.

APP static coverage remains **95.54%**. Four startup source bytes and physical chip, ROM, RAM, IRQ, Flash, OTA and complete behavior evidence remain missing. No target, model, emulator or hardware execution; **no BIN generated and flash compatibility remains unproved**.

Feature candidate: offline timer diagnostics showing lookup hit/miss, actual field update and returned status separately. Proposal only, not implemented.

[C/C++](resident_task0_RAM_dependencies.c) · [Original instructions](evidence-v1.json) · [Checker](audit-v1.py) · [Receipt](audit-result-v1.json) · [Summary](summary.json)

Read-only revalidation from the project root, using retained references, objects and checked LLVM:

```sh
python3 experiments/tsl9-resident-task0-RAM-dependencies/audit-v1.py --tool-dir "$LLVM_BIN"
```

Use `py -3` on Windows if needed. Public text receipts do not replace references or build artifacts.
