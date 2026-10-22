# Source proof of the callback's final RA-frame overwrite

[繁體中文](README.md) | [English](readme.en.md)

The conditional answer is yes. On the original callback's normal return path, its final `0x198E6→0x188E2` call necessarily overwrites the new ADC saved-RA word at callbackSP-4 with `0x198EA`. No later own stack store changes it before the callback's `0x1995A` RET. Under the existing private valid144-byte stack, normal access, disjointness and no async modification/observer premises, **this single word at whole-callback normal exit** matches between the original and new ADC candidate.

This does not make the word equal when the ADC callee initially returns at `0x1989A`, or permit observation of earlier temporary values. The prior sealed ABI review records the candidate's sole stack store: RA=`0x1989A` at newSP+12 in a16-byte frame, hence callbackSP-4. This scope neither recompiles nor executes that function.

The new actual ID2966 ledger contains callback `0x197F0..0x1995C`364 B/130 rows, reset-like `0x188E2..0x1892E`76 B/25 rows and RCC leaf `0x19160..0x1917E`30 B/12 rows:470 B/167 rows in three ranges. The prior checker additionally rereads the complete fourteen-range946 B/352-row source closure. These three ranges are a subset, not additional distinct coverage. Full firmware identity is76800 B, SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`; the whole file is not decoded.

This is static source CFG and stack-address algebra, not CPU/register execution modeling. Direct calls use previously closed normal-return source summaries, never assumed PSABI preservation. Sixty-eight callback CFG nodes are reachable from ADC return `0x1989A`. Removing198E6 makes the unique normal RET1995A unreachable: the final call dominates normal exit. An infinite path is not mistaken for a return.

The final four-byte JAL produces RA198EA.188E2 subtracts16 from SP, and188E8 stores input RA at12(SP), before any branch or nested call and before any RA overwrite. That store dominates both normal exit forms, which reload the same slot and restore SP. Nested19160 has no RA/SP/S0 writes or stack access, only fixed `0x4002100C` read/modify/write effects. The saved word is callbackSP-16+12=callbackSP-4=entrySP-132, inside the existing entrySP-144..entrySP-1 interval.

After reset-like return the callback makes no further call or stack store. Remaining stores use fixed RCC/ADC bases; normal-access/disjointness premises exclude aliasing this word. Later SP-relative reads use nonnegative callbackSP offsets, and19958 restores the128-byte outer frame.19920 separately restores the actual outer caller's RA:198EA is the internal saved word, not the claimed final callback return destination.

A source-based limitation remains: poll branch198D6 returns to198C6 without an encoded timeout. Perpetually zero status permits an infinite path that never reaches198E6 or returns normally. Therefore overwrite and termination are not unconditional. Faults and asynchronous observation/interference remain outside this normal source proof.

Actual `--firmware` mode rejects six raw operand controls: final CALL link register, saved slot, saved value source,16-byte frame displacement,128-byte outer-SP restoration, and a changed poll branch to19906 that bypasses the overwrite while preserving CFG reachability of the original RA/SP epilogue. Mutations stay in memory and are statically decoded; no instruction stepping, opcode stub or BIN is generated.

```sh
python3 -B check.py --project-root /absolute/project/root
python3 -B check.py --project-root /absolute/project/root --firmware /absolute/original.bin
python3 -B check.py --project-root /absolute/project/root --firmware /absolute/original.bin --receipt /new/proof.json
python3 -B check.py --project-root /absolute/project/root --replay /existing/proof.json
```

Default mode verifies sealed metadata with actual-firmware/raw-control flags false. Explicit firmware checks full identity, actual ranges and controls again. Receipts are create-only and replay is read-only. W `apk-analysis/tsl9-*` and D/P `analysis/*` lookup are supported; this scope writes neither D/P nor publication.

Single-word final equality does not prove whole RAM, full original callee ABI, fault/async/IRQ traces, chip/ROM/BOOT, Flash/NV ownership or BLE OTA. No new HOST, hardware, network, native/MMIO/ISA/ESIL execution, link or BIN occurs. No new r2 capture or decoder/ISA definition is required. The POSIX wrapper uses the same Python entry; denied Git Bash is not retried and shell runtime remains unverified. Authored text is LF/single EOF and default README equals Traditional Chinese.
