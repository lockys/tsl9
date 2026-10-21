# V4.1.60 clock query and derived fields

This fixed C11/C++17 dataflow model reconstructs original ID2966 V4.1.60 functions `18834..188E2` (174 bytes/58 instructions) and `1973C..19764` (40 bytes/11 instructions). Ends are exclusive. The sealed raw-source proof covers all 214 bytes/69 instructions and rejects 50 raw operand mutations. The original Runtime SHA-256 is `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.

`sf_query_18834` selects source and PLL arithmetic from separate live reads, preserves the multiplier17-to18 rule, and first stores the base result at GP+108. It separately rereads the prescaler, reads a live byte through GP+64+index, rereads GP+108, performs an unsigned shift using only the low five shift bits, then stores the final word. The RAM table is never replaced by a constant table. Its conditional reset mapping is separate source evidence.

`sf_derive_1973c` freshly reads GP+108, divides unsigned by8,000,000, masks to255, writes a byte at GP+382, multiplies that masked value by1000, and writes a halfword at GP+380. The original code has no local stack frame, nested callee or A0 return-value assignment. The meanings and physical units of these derived fields remain unconfirmed.

Providers receive numeric addresses and state snapshots before each effect. Load responses then update the destination register; later addresses use the live state. A provider may model an explicitly declared synthetic register/environment change while preserving engine control and budget. This does not prove physical interrupt behavior. Partial arithmetic retains conservative known-bit sets. Ambiguous branches stop; unknown bits never silently become zero. Definite source order, widths and prefix effects survive HALT, TRANSFER and budget boundaries.

`sf_ml_init_call` binds only ML9254→18834 and ML925C→1973C with the exact source profile and explicit continuation. It shares all represented registers and memory with the actual runtime-loop model. The middle9A42 remains an opaque provider and may change GP or the clock word; the later callee must reread it. SF and ML budgets remain separate.

From this folder, run:

```sh
sh ./verify.sh --language both
```

Use `tests/run-tests.sh --language c` only for a labelled host-only run. Full verification also checks the exact firmware, sealed source members and declared dependencies. Python3.10+ plus a working native C/C++ compiler are required; PowerShell is not required. The latest Windows source tests pass7 groups/1,414 checks per language. Cross-platform results are separate receipts.

WCH CH32V20x is a hardware candidate, not an established physical profile. This model does not execute original RISC-V instructions, emulate an ISA, install a ROM provider, produce a native BIN, touch physical hardware or establish BLE OTA compatibility.
