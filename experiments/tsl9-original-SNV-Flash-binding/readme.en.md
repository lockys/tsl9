# Original APP SNV / Flash callbacks

[繁體中文](README.md) · [Previous callback ledger](../tsl9-resident-callback-binding-ledger/readme.en.md) · [Candidate SNV C/C++](../tsl9-resident-snv-initialization/readme.en.md)

This study checks eight complete original APP functions (632 bytes) and four complete candidate SDK functions (718 bytes): **1,350 bytes / 492 instructions**. It joins two additional indirect sites. The [receipt](verification-v1.json) retains full scopes, CFGs, conditions and existing native witnesses. No target code or BIN was added.

| Item | Original static evidence and conditional result |
| --- | --- |
| Configuration | The 64-byte BLE configuration in `0x199E2`, passed at `0x19AEC` |
| SNV fields | Base `0x08077C00`; original block=0 becomes SDK default 256; SNVNum=3 |
| Read callback | Store `0x19A7E` selects `0x1979A`; SDK site `0x44056` uses slot `0x20003224` |
| Write callback | Store `0x19A88` selects `0x197BE`; SDK site `0x440BE` uses slot `0x20003228` |
| Initialization | BLE `0x43C7E` → `0x43B3E` → SNV `0x44022`, subject to original branches and normal returns |

If the first marker differs, a valid 256-byte buffer is returned and the original loop completes, the three write arguments are `0x08077C00`, `0x08077D00` and `0x08077E00`. The logical window is `[0x08077C00, 0x08077F00)`. **This does not establish physical Flash capacity, partitioning or MCU identity.**

### Numerical comparison with APP settings pages

The existing [six APP settings records](../tsl9-NVM-record-layout/readme.en.md) use `[0x08077500,0x08077B00)` at 256-byte numerical granularity in their writers; the conditional three-page SNV window above is `[0x08077C00,0x08077F00)`. These windows do not overlap, with a 256-byte numerical gap `[0x08077B00,0x08077C00)` between them. The gap's **purpose is unknown**; it must not be treated as blank or available.

If both groups of high addresses mapped to one contiguous region starting at `0x08000000`, reaching the end of the SNV window would require offset `0x77F00` (491,264 bytes). This is arithmetic under that assumption, not established chip capacity, physical addresses or a writable partition. Each path retains its own slot, memory, initialization and execution conditions; SNV pages may not be written when the marker matches. No device was read and no page contents were inferred. The [offline checker](check-snv-settings-ranges.py) pins two existing receipts and cross-checks the intervals.

The read callback converts num=1 into a four-byte copy, using candidate slot `0x4004C` → `0x20000332` to the SDK's own SP+12. This copy also accesses `0x4002420C` and issues FENCE.I; an ordinary RAM memcpy alone does not establish equivalent hardware effects. The callback returns A0=0 on normal return without validating copy success.

The buffer is filled with `0xFF`, then its first word is set to the current page address before each write. The SDK passes num=64 words. Original `0x197BE` ignores that argument, saves the source and calls unlock, erase, program, lock and delay. Program has a fixed 64-word / 256-byte span; erase and program both align the destination down to 256. Actual allocation capacity, Flash success and polling termination remain unproved. Delay also depends on live GP+382 and MMIO.

**Return values do not establish persistence success:**

- Only the first page's first word is compared. A matching marker skips writes without validating all three pages.
- Read and write callbacks set A0=0 on normal return without checking hardware results.
- SNV may return 1 for either a matching marker or allocation failure. Outer BLE still overwrites the result with 0 at `0x43D4E` / `0x43D56`.

Cumulative joins are **21 / 51 sites**: 16 conditional targets and five zero-value skips. The other 30 sites are outside this cumulative ledger, not a missing-function count. All previous 19 joins and their assumptions remain. The result requires matching ROM, valid disjoint memory, stable fields, the original private ABI, normal returns and no IRQ/reentrant overwrite; no live binding was observed.

Existing C/C++ bodies: APP [callbacks](../../src/native/startup/resident_startup.c), [Flash helpers](../../src/native/receive/ota_runtime.c) and [delay](../../src/native/startup/peripheral_primitives.c). Two independent ELF readers recheck the original-address native diagnostic; current SDK byte ownership is also checked. Existing ABI receipts are retained; no new compilation was performed. APP static byte coverage remains **95.54%**. ROM/RAM/ISA/IRQ/Flash/OTA compatibility and the inherited four-byte startup-source gap remain unresolved. **This is not flash-ready firmware.**

A possible feature is offline per-page marker/content consistency diagnostics for a supplied NVM dump. It is not implemented; no hardware or current page contents were read.

Run offline from the project root:

```sh
python experiments/tsl9-original-SNV-Flash-binding/verify-v1.py --tool-dir "$LLVM_BIN"
```
