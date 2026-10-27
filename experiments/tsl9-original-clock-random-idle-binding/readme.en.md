# Conditional clock, random and idle routes

[繁體中文](README.md) · [Previous SNV / Flash](../tsl9-original-SNV-Flash-binding/readme.en.md) · [Clock C/C++](../tsl9-resident-clock-services/readme.en.md) · [Random C/C++](../tsl9-resident-range-random/readme.en.md)

This study checks **11 complete SDK functions / 3,840 bytes** and the **308-byte original APP initializer**: **4,148 bytes / 1,433 instructions**. It adds 14 conditional joins. The [cumulative ledger](ledger-v1.json) covers **35 / 51 sites**: 27 conditional targets and eight zero-value skips or caller gates. The other 16 are not joined here; this is neither a missing-function count nor functional completion. [Verification receipt](verification-v1.json)

| New path | Sites | Conditional result |
| --- | ---: | --- |
| Raw clock | 10 | Target `0x191C6` after accepted original clock configuration with stable slots |
| Configured srandCB | 1 | `0x433D2` calls `0x43520`, without requiring prior clock configuration |
| Status | 2 | Original guards skip `0x6537C` / `0x655F6` when post-copy staCB remains zero |
| Idle caller gate | 1 | A zero-value guard in the specified scheduler entry prevents entering idle service; it is not a local service guard |

## Random source and state update

At `0x19A74`, the APP loads candidate slot `0x4007C`, then stores it into srandCB at `0x19A90` (configuration offset36). The actual candidate word is `0x43520`. After the copy to `0x200031EC`, load `0x433C4` reads slot `0x20003210`; the nonzero branch calls it at `0x433D2`. This binding does not establish completed clock initialization.

`0x43520` separately reads provider slot `0x20003230`. Zero skips the nested call and returns the stored word at `0x200031B0`. Nonzero follows `0x43520 → 0x43D62 → 0x191C6` only under the earlier registration/clock conditions. Registration before every random call remains unproved.

The state word is at `0x20002EC8`. When a callback runs, the function reloads the state after it returns, adds callback A0 and computes:

```text
updated = fresh_state_after_callback + callback_A0
result  = updated * 214013 + 2531011
```

All arithmetic is RV32 unsigned modulo `2^32`. A zero primary callback has a separate raw-clock fallback; when both are zero, that addition is skipped. **Initial seed, entropy, random quality and physical output remain unproved.** Accesses to MMIO `0x4002420C` and FENCE.I do not alone establish physical IRQ atomicity.

## Location of the idle gate

Under the known original zero/copy conditions, idleCB (configuration offset40 / own SP56..60) remains zero at slot `0x20003214`. Scheduler entry `0x200007D0` tests it at `0x2000087C`. The zero branch returns without reaching tail `0x200008BE → 0x2000061A`.

Idle service site `0x2000071E` **has no local null guard**. The result is limited to that caller context. It does not resolve other callers, nonzero idleCB or arbitrary direct invocation. Reconstruction must preserve the caller gate and must not silently change service semantics.

Checks cover complete original bytes, CFGs, register paths from the last definition to each use, existing C11/C++17 artifacts and two independent ELF readers. Values crossing callees still require the original saved-register ABI; IRQ, reentrancy, aliasing and installed ROM identity remain conditional. All earlier bindings and limits are retained.

No target C/C++, compilation or BIN was added. The candidate remains **35,324 CODE + 256 DATA bytes / 12,195 instructions / 0 named UND**. APP static byte coverage remains **95.54%**. The four-byte startup-source gap and installed ROM/RAM/ISA/IRQ/Flash/OTA compatibility remain unresolved. **This is not flash-ready firmware.**

A possible feature is offline callback/clock-source and idle caller-gate diagnostics. It is not implemented and sends no hardware commands.

```sh
python experiments/tsl9-original-clock-random-idle-binding/verify-v1.py --tool-dir "$LLVM_BIN"
```
