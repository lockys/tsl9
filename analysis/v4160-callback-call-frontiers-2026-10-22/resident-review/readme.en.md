# Resident candidates: bounded callback-slot evidence

[繁體中文](readme.zh-TW.md)

This scope reads two already retained official SDK resident candidates and only callback slots `0x40000+0x13C` and `+0xD4`. No download, RV32 execution/emulation, hardware access, sealed-source modification or BIN generation occurred. **Neither candidate identifies the installed resident.**

| Embedded version | +0x13C word / direct helper | +0xD4 word |
| --- | --- | --- |
| V1.40 | 0x4B4EE / 0x4B37C | 0x4C25C |
| V1.31 | 0x4B456 / 0x4B2E4 | 0x4C1C4 |

HEX/main sparse-segment identities and tiny address-bound byte excerpts/hashes are retained. Only296bytes per candidate are excerpted as text; the vendor ROM is not published in this scope. Conditional RAM helper mapping differs: V1.40 flash0x402F0→RAM0x20000040, V1.31 flash0x402B0→the same RAM base. This does not establish that a runtime copy occurred.

## Closed +0x13C pair: a byte value, not a Boolean

Both candidates have a22-byte wrapper and36-byte lookup. The wrapper's sole call targets that lookup; the lookup makes no call. Under the retained LLVM `HasVendorXwchc` profile, raw `28 21` means `qk.c.lbu a0,2(a0)`, rather than r2's default floating-load spelling. No match returns0; a match returns the zero-extended byte at entry+2. The normal range is **0–255, not restricted to0/1**.

The archived V1.40 header defines table base0x40034 and names JT66/+0x13C `GATTServApp_ReadCharCfg`. This supports a candidate CCC-configuration interpretation, not installed-device attribution. The callback's first gate requires `A0==1`, while its second tests `A0&1`; value3 fails the former and passes the latter. They must remain distinct rather than a generic link-status Boolean.

The entire58-byte pair has no GP or S-register operand, including S4/S7. Incoming RA is only saved atSP+12, restored and returned through; the lookup only returns through RA. There is no numeric RA test or use as data/address. Semantic inputs are full A0 and pointer A1; required A2–A5 values are locally overwritten before use. **Conditional on the actual provider being this candidate/profile and ordinary stack/table/return-memory assumptions, differing callback call-site RA numbers or incoming S4/S7 values are not observed by this pair.** This is not a universal resident ABI proof and does not erase the callback's own fault/async/stack-alias differences.

## +0xD4 frontier: deeper behavior remains unknown

Header JT40/+0xD4 is named `GATT_Notification`. Each local118-byte body saves/restores S0/S1/S2/RA in a32-byte frame and has no GP/S4/S7 operand. Its five calls comprise two linked-RAM helpers and three deeper flash routines.

The44-/76-byte helpers at conditional RAM0x20000A1C/0x20000A48 are closed, have no nested call or S/GP operand, and use RA only for RET; some halfword loads remain Xwchc-conditional. Unexpanded flash targets are V1.40 0x45228/0x4B82C/0x4EF0A and V1.31 0x45194/0x4B794/0x4EE72. Their transitive S/GP/SP/RA/memory behavior is not proved. This supports a candidate notification path, not physical success. No broader BLE ROM exploration was performed.

## Replay and portability

```sh
python3 -B analysis/v4160-callback-call-frontiers-2026-10-22/resident-review/review.py
python3 -B analysis/v4160-callback-call-frontiers-2026-10-22/resident-review/review.py --candidate-root /path/to/existing/wch-resident-candidate-2026-10-21
```

Development uses `apk-analysis/tsl9-`; publication uses `analysis/`. Windows may use `python -B`; a POSIX `review.sh` is included. **Default needs no vendor files and reports actual_candidate_bytes_read=false**: it checks the seal, excerpt fields, limited contracts and eight field controls. Explicit `--candidate-root` verifies fixed HEX/main-segment/profile-reference pins and all retained slots/excerpts, reportingtrue. It invokes no r2/target and downloads nothing. P can reference the existing D candidate directory; missing/mismatched data fails.

`r2-observations.json` retains ten actual bounded static commands and raw observations. r2 sometimes prints QK words as floating instructions or split invalid bytes. These strings alone are not semantic evidence: raw2/4-byte boundaries and explicitly conditional Xwchc fields are kept separate. Unsupported instructions remain unknown and are never treated as NOPs.
