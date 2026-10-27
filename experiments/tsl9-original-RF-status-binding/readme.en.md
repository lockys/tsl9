# Original APP RF status callback binding

[繁體中文](README.md)

Join original APP callback `174EE` to ten conditional SDK RF register-transfer sites. Verify **9 complete SDK functions / 2,666 bytes / 940 instructions**, plus **586 original APP bytes** covering main initialization, constructor and callback. No new target C/C++, compilation or BIN this round.

The constructor prepares a 32-byte configuration: mode `01`, channel `25` (decimal 37), and callback `174EE` at offset 16. Candidate `RF_Config` has actual far calls requesting zeroing and copying into `20003540`. After normal completion, with no replacement, `20003550` contains the callback. This requires matching installed ROM/RAM, valid disjoint memory and the original private ABI; actual installation and ordering remain unobserved.

| Call PC | All reaching A0 status values | Original APP callback route |
|---|---|---|
| `63F26` | 17 | Tail to retry `17442` |
| `64452`, `64588` | 1 / 17 | Return / retry |
| `64658` | 2 | Retry if A1 is nonzero; otherwise compare buffer bytes |
| `64690` | 18 | Retry |
| `6534C`, `6553E`, `6555A` | 3 | Return |
| `6565E` | 4 / 20 | Return |
| `657AE` | 34 / 36 | Return |

Four sites contain branch joins, with **14 actual pointer loads** in total. Finite may-reaching-definitions over complete CFGs retains every source. Calls conservatively clobber volatile registers; saved-register preservation across callees remains a private-ABI condition.

At status-2 site `64658`, A1 zero causes reads of `A2+1`, `+2`, `+3`: at least four readable bytes are required. **The original callback has no local null/length guard.** All comparisons passing tails to `173EE` with A0 zero; failures tail to `17442`. This proves neither the full packet protocol nor all caller memory safety.

Original bytes, original-address re-encoding of compiled C/C++, complete CFGs, own frames, APP sources and the nonloadable diagnostic ELF pass verification. **50 of 51** SDK register sites have at least one evidenced conditional domain; `432EA` remains unjoined. This is not functional completion or universal live resolution.

APP static coverage stays **95.54%**; the candidate union stays **36,762 CODE + 392 DATA bytes**. Four startup source bytes and physical ROM, chip, RAM, IRQ, Flash, OTA and complete behavior evidence remain unresolved. No target, model, emulator or hardware execution; **flash compatibility is unproved**.

Feature candidate: offline RF status decoding and callback-route diagnostics. Proposal only, not implemented.

[Checker](verify-v1.py) · [Evidence](evidence-v1.json) · [Site ledger](ledger-v1.json) · [Receipt](verification-v1.json) · [Summary](summary.json)

Read-only revalidation from the project root, requiring retained references, native objects and checked LLVM tools:

```sh
python3 experiments/tsl9-original-RF-status-binding/verify-v1.py --tool-dir "$LLVM_BIN"
```

Use `py -3` on Windows if needed. Public text receipts do not replace actual reference files.
