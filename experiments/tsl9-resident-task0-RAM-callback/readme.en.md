# Task-0 record callback C/C++

[繁體中文](README.md)

Add complete RAM callback **`2000138E..200013E8`: 90 bytes / 35 instructions**, sourced from candidate SDK Flash `415FE..41658` through the existing startup copy mapping. **The installed ROM and physical mapping remain unproved.**

The actual no-link tail `567B4 → 43414` in `56716` passes callback `2000138E`. `43414` scans the first 16 records at stride 12, then stores callback, argument and cleanup mode at offsets 0/4/8 after successful allocation. RAM `2000322C` holds the record-array pointer.

Given task ID 0, the selected event bit, stable records/pointers and the original private ABI, `432EA` calls `2000138E` with the record's second word in A0. Verify its nonzero guard, every reaching pointer definition and complete CFGs. Live values, initialization ordering and valid physical memory remain unobserved.

The consumer uses `16*taskID+k`, while its post-callback third-word check uses `k`. **They identify the same record only for taskID zero with a stable array base.** The third word comes from a freshly reloaded global array pointer after callback return. Zero clears the previously selected callback/argument; nonzero skips clearing. This proves neither replacement safety, concurrency safety nor universal one-shot behavior.

Actual C11/C++17 objects are identical. All 90 original-address re-encoded bytes, full CFG/own-frame checks, independent ELF readers and nonloadable partial linking pass. The union contains **36,852 CODE + 392 DATA bytes / 12,721 instructions**.

| Genuine callee with no supplied body | Source |
|---|---|
| `20001122` | Direct call |
| `20000D50` | Direct call |
| `436A8` | Actual AUIPC/JALR pair |

Retain all three as named UND symbols; no stub or fabricated provider. Complete callback effects remain open.

**Only the 51 register-transfer sites in this partial SDK object have at least one evidenced conditional domain**: 41 targets/target sets and 10 skips/caller gates. This excludes the entire APP, calls inside unprovided callees and universal live bindings. It is not runtime closure or functional completion.

APP static coverage stays **95.54%**. Four startup source bytes and physical chip, ROM, RAM, IRQ, Flash, OTA and complete behavior evidence remain missing. No target, model, emulator or hardware execution; **no BIN generated and flash compatibility remains unproved**.

[C/C++](resident_task0_RAM_callback.c) · [Original instructions](evidence-v1.json) · [Registration references](provenance-inputs-v1.json) · [Checker](audit-v1.py) · [Receipt](audit-result-v1.json) · [Summary](summary.json)

Read-only revalidation from the project root, using retained references, native objects and checked LLVM tools:

```sh
python3 experiments/tsl9-resident-task0-RAM-callback/audit-v1.py --tool-dir "$LLVM_BIN"
```

Use `py -3` on Windows if needed. Public text receipts do not replace reference or object files.
