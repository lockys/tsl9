# Three candidate central-role callbacks: C/C++ experiment

Reconstruct three complete original bodies from the official ID2966 V4.1.60 BIN: `0x10C36..0x10C7A`, `0x10D2E..0x10D30`, and `0x10D30..0x10D60`: **118 bytes / 41 instructions**. C and C++ each produce 11 actual FUNC regions and five typed branch relocations. Resolving those branches at original coordinates reproduces every original instruction. Both languages produce identical objects, checked with two ELF readers.

- Confirmed: the first body compares 16-bit fields in three RAM records and conditionally writes the matching record's first byte. The second original body is RET. The third calls ROM slot `0x40038`, reduces its result modulo 1,000,000, and tail-calls slot `0x40170`.
- Candidate SDK meanings: `gapCentralRoleCB_t.rssiCB`, `gapBondCBs_t.pairStateCB`, and `gapBondCBs_t.passcodeCB`. SDK `tmos_rand` / `GAPBondMgr_PasscodeRsp` signatures also agree. **The installed ROM ABI remains unproved.**
- The separate `0x11544..0x119C8` event window contains 1,156 bytes / 374 instructions. Its 0..16 guard, 68-byte relative jump table, and seven internal targets are verified. Of 20 direct calls, four target addresses still lack formal CODE owners: `0x10CE0`, `0x110F8`, `0x11266`, and `0x114E2`.

This is an experimental component, not yet added to the curated `src/` proof or original-coordinate integration. **Formal coverage stays at 89.03%.** No new BIN, target execution, or hardware access. These results do not prove feature completion, recovery of original source, or flashability.

## Local verification

From the repository root run `python experiments/tsl9-central-callback-leaves/audit-v1.py` and `python experiments/tsl9-central-callback-leaves/build-v1.py`. They require the retained firmware, formal layout map, and identically hashed NDK LLVM. Only positive static inspection and cross-compilation are performed.

Next: reconstruct the event callback and four helpers, establish typed DATA/CODE jump-table bindings, then integrate the three verified bodies. RSSI connection diagnostics and event tracing are potential additions, not implemented features.

[繁體中文](README.md) · [Source](src/central_callback_leaves.v1.c) · [Verification summary](summary.json)
