# Bounded notification-child candidate contract

[繁體中文](readme.zh-TW.md)

Only retained candidate functions V1.40 0x45228 and V1.31 0x45194 are reviewed: each is **54B /22instructions**, with a **56B /17instruction** helper conditionally mapped at RAM0x200001E4. No ROM C/C++ model, download, target execution/emulation, old-seal edit or BIN was produced. Candidate identity is not installed identity.

| Version | Wrapper | Actual builder pointer | Unclosed tail |
| --- | --- | --- | --- |
| V1.40 | 0x45228..0x4525E | 0x44E44 | 0x44866 |
| V1.31 | 0x45194..0x451CA | 0x44DB0 | 0x447D2 |

The wrapper allocates32bytes, saves S0@24/RA@28, retains incoming A0 in S0, freshly loads32bits from descriptor A1+4, and defaults A4=0. If nonnull, it saves the descriptor atSP+12 and calls RAM0x200001E4 with pointer and delta3. It then freshly reloads SP+12 intoA3 and setsA4 to the helper result. Replacing this load with a cached local would assume stable stack contents.

It sets A0=liveS0, freshly restores S0/RA, passes the builder pointer inA1 and27 inA2, pops32bytes and tail-jumps with rd0. There is no local normalized result. The unknown tail inherits the restored caller RA. Unspecified raw arguments are not a proven full GPR projection.

The local wrapper reads no GP/S4/S7 and uses incoming RA only for save/restore before forwarding it. This does not establish transitive non-observation by the tail. LiveS0/SP changes, aliases, faults and asynchronous effects remain conditional.

The closed helper's source mapping is V1.40 flash0x40494 and V1.31 flash0x40454. Its globals are respectively0x200031E4/0x200031DC and0x20003194/0x2000318C. It retains original=A0, computes adjusted=u32(A0-A1), and follows next=READ32(node) until the sentinel. It returns adjusted only when both original and adjusted lie in unsigned [u32(node+8),next); otherwise it continues, returning original at the sentinel. It writes no memory and uses no SP/GP/S register or nested call; RA is only RET. No allocator interpretation, termination bound or validity guarantee is invented.

Only128bytes/54instruction boundaries of the tail are retained. They show a64-byte frame, new calls, an S6 indirect call and CFG edges beyond the prefix. The bounded reader leaves raw2C08 unknown (r2 suggests an SP-relative ADDI); QK halfword stack stores remain conditional Xwchc interpretations. Unknown never means NOP. Complete tail/builder/deeper behavior and notification outcome remain unknown.

Archived header literal0x1B is ATT_HANDLE_VALUE_NOTI; header names support candidate interpretation only. An early builder-address arithmetic error451E4/451B0 was caught before sealing by raw LUI+signedADDI validation; correct values are44E44/44DB0.

```sh
python3 -B analysis/v4160-notification-callees-2026-10-22/candidate-review/review.py
python3 -B analysis/v4160-notification-callees-2026-10-22/candidate-review/review.py --candidate-root /existing/wch-resident-candidate-2026-10-21
```

Development prefix is apk-analysis/tsl9-; publication uses analysis/. Optional --project-root ROOT is supported; Windows can use python -B. Default rederives metadata and238excerptbytes per candidate without vendor files (actual_candidate_bytes_read=false). Explicit candidate-root verifies pinned HEX/segments/profile references and excerpts (true). No whole vendor ROM is copied toP, and the checker invokes no r2 or target. Six actual static r2 observations are retained without ESIL. Eight raw-field controls reject. Full ABI, installed identity and OTA remain false.
