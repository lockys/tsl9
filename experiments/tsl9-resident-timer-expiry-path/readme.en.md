# Timer expiry and record cleanup

[繁體中文](README.md)

Supply the previously missing `60838` body and its cleanup tail: two complete SDK candidate functions, **258 bytes / 84 instructions**. The installed hardware ROM remains unidentified.

| Original interval | Bytes | Verified static behavior |
|---|---:|---|
| `60838–60856` | 30 | Write `FF` to incoming record `+49`; call `5E3A8` with `A0=0, A1=128, A2=17`; restore RA and its 16-byte frame, then take a no-link tail to `60754` |
| `60754–60838` | 228 | Load the record from RAM `20003438`; release its `+68` pointer, clear fields, stop event masks `4/8`, conditionally cancel timer IDs at `+49/+48`, and conditionally clear the callback pointer |

Producer `5E76C` calls `43874` at `5E88A` with callback `60838`, record `s1`, delay expression `uint16(record+56) << 4`, and output-ID address `record+49`. Runtime units and delivery remain unproved. The incoming expiry record and the cleanup global record are the same object only under additional memory-consistency conditions.

Cleanup calls `43A14` for each ID unequal to `FF`, then writes `FF` after normal return. If RAM `20003240` is nonzero, it calls `2000078A` with `A0=0`, clearing pointer `20002EF8` **without clearing flag `20002EFC`**. Preserve the original read, zero, `FENCE.I` and restore sequence at `4002420C`; its physical register meaning and IRQ safety remain unproved.

Actual C11/C++17 objects are identical. Every original-address re-encoded byte, complete CFG/own-frame checks, independent ELF readers and nonloadable partial linking pass. The union contains **36,762 CODE + 392 DATA bytes / 12,686 instructions**, with zero named UND symbols; runtime dependencies remain open. **40 of 51** register-transfer sites still have at least one evidenced conditional domain. Original APP static coverage remains **95.54%**.

Four startup source bytes and physical chip, ROM, RAM, IRQ, Flash, OTA and complete behavior evidence remain missing. No target, model or emulator execution; no BIN generated.

Feature candidate: an **offline timer-record lifecycle inspector**, showing ID fields, `FF` sentinels and cleanup conditions to help review repeated-cancellation or pointer-replacement risks. This is a proposal, not an implemented feature or a confirmed firmware defect.

[C/C++](resident_timer_expiry_path.c) · [Evidence](evidence-v1.json) · [Checker](audit-v1.py) · [Receipt](audit-result-v1.json) · [Summary](summary.json)

Read-only revalidation from the project root, requiring checked LLVM tools and retained local reference/build artifacts:

```sh
python3 experiments/tsl9-resident-timer-expiry-path/audit-v1.py --tool-dir "$LLVM_BIN"
```

Use `py -3` on Windows if needed. Public text receipts do not replace actual reference or object files.
