# Next provider: only the102-byte primary function

[繁體中文](next-provider-contract.md) · [Full contract / raw CFG](next-provider-contract.json) · [Original182-byte window](next-provider.json)

The official V4.1.60 primary extent is`[12A08,12A6E)`,102 B /35 instructions, SHA256 `334494853a765e550af99f0e8dd95523efaf7cbb86d392e0340a5d5f004940c9`. Fresh r2 agrees with actual BIN bytes and the first35 retained rows. Direct control targets/rd/RA were independently decoded from raw bits. The local CFG has35 nodes /38 edges; all35 rows are syntactically reachable assuming opaque calls return to their encoded continuations. Actual path feasibility is not proved.

**The182-byte window is not one function.** The cold path`12A66..12A6E` remains part of the primary function after its RET at12A64. The following`[12A6E,12AA0)`50 B and`[12AA0,12ABE)`30 B start two other entries. Neither the first RET nor the full window supplies the wrong primary extent.

| Range (exclusive end) | B | i | Analysis cut |
|---|---:|---:|---|
| `12A08..12A16` | 14 | 6 | frame_status_and_branch |
| `12A16..12A20` | 10 | 3 | status_zero_ID_fallback |
| `12A20..12A28` | 8 | 3 | predicate_index0 |
| `12A28..12A2E` | 6 | 2 | tag_split |
| `12A2E..12A50` | 34 | 10 | record_metadata_and_resident_copy |
| `12A50..12A5E` | 14 | 4 | peripheral_call |
| `12A5E..12A66` | 8 | 4 | fresh_restore_return |
| `12A66..12A6E` | 8 | 3 | post_RET_tagged_call |

Entry allocates48 B, saves S0 atSP+40 and RA atSP+44, then S0=A0. Call12A10→81AA returns at12A14. That known6-byte original leaf is`LBU A0,167(GP); RET` and its own code writes only A0. Nonzero status proceeds to the predicate; zero status requires LHU[S0]==1. Call12A22→821E sets A0=0 and returns at12A26; only the caller's zero-result rejection is established. Its full callee/ABI remains unknown. A bounded prefix or an older-version name is not DND proof.

After the predicate, fresh LBU[then-live S0+11] selects the path. Nonzero tag reaches the post-RET block: A0=then-live S0, call12A68→16B7C, RA12A6C, then jump to restore. The zero-tag path freshly loads ID/length and stores, in order, SH0 atSP+20, **SW32 ID atSP+12**, and SB length atSP+22. SP+16..19 are not initialized by these stores; do not invent a fully initialized C structure.

LUI base40000 plus C.LW offset76 reads a fresh pointer word at4004C. C.JALR at12A4E returns at12A50, with A0=then-live SP+23, A1=then-live S0+3 and A2=the loaded length byte. No memcpy, valid-pointer or preservation contract is proved. After return, A0 is formed as40006400 and A1 uses **post-call then-live SP+12**;12A5A→18CA4 returns at12A5E. A2 is not reloaded and remains a resident residue.

The sole restore freshly loads RA fromSP+44, S0 fromSP+40, adds48 toSP and RETs. A0 has no uniform status result. Do not assume ordinary C ABI preservation across821E/resident/18CA4/16B7C. The primary body contains no own GP or CSR instruction;81AA separately has a known GP+167 read.

There is no length bound in this primary body. A2 initially ranges0..255; destination argumentSP+23 versus saved S0/RA atSP+40/44 can support an offline interval diagnostic only with explicit snapshot/copy assumptions. An unknown resident does not prove an actual copy, overflow or hardware result. Other diagnostics may explain gates and explicitly initialized metadata, without inventing bytes, protocol/seat/DND/CAN identity or successful delivery.

A minimal readable-C reconstruction should cover only102 B, using C for ID/tag/metadata/argument arithmetic with explicit frame, then-live, call and cold-return ports.81AA may reference the existing6-byte C component subject to actual linkage proof.821E/18CA4/16B7C remain genuine unknown providers and the resident remains dynamic. No target/ISA/ESIL/MMIO/hardware/network/compiler execution, BIN or Git operation;`firmware_ready=false`.
