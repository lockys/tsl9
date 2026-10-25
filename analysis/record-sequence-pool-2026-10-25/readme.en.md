# C/C++ sequence DATA-pool experiment

[繁體中文](README.md)

This round adds a [readonly C/C++ DATA pool](../../experiments/tsl9-record-sequence-pool/src/record_sequence_pool.v1.c) and genuine interior labels for three original references. It is a **separate compile/partial-link experiment**, pending `src/` curation and accepted original-coordinate integration.

## Storage and labels

Original source literals are `0x1A430`,`0x1A454`,`0x1A478`;locally assigned nonzero limits are 17 or 53. Pairing the three literals independently with both limits gives six conditional read windows. Their union is `0x1A430..0x1A4E2` (exclusive end), **178 bytes**.

This preserves relative storage for known literal sources combined with known literal limits without assuming the three ideal configurations always remain correlated. It is neither a bound on arbitrary RAM values nor an original array declaration extent.

| Symbol role | Original coordinate | Pool offset | Allocated bytes |
|---|---|---:|---:|
| Single actual DATA owner | `0x1A430` |0 |178 |
| Source label1 | `0x1A430` |0 |0 |
| Source label2 | `0x1A454` |36 |0 |
| Source label3 | `0x1A478` |72 |0 |

All three labels have real readonly section backing. No ABS address substitutes or duplicate byte allocations.

## Verification and new evidence

- Freshly capture 245 original instructions,checking source selection,RAM fields,limits,callbacks and stopping paths.
- The 32-bit zero store at `0xEEBE` clears both counter and limit before calling `0x90B0`. This does not prove callback quiescence or non-reentrancy.
- `0xF0B0..0xF0C6` passes zero-fill arguments for 12 bytes starting at `0x2000BF84` through ROM slot `0x40048`. If the installed slot obeys the cached SDK memset contract, the range includes the source pointer. Installed ROM identity and ABI remain unknown.
- C11/C++17 DATA objects and experimental components are respectively identical. Two ELF parsers agree on all sections,bytes,symbols and relocations.
- The experimental component preserves 64,544 CODE bytes and all prior 3,111 DATA bytes,adding the 178-byte pool. Three references bind real labels;undefined providers fall **27→24**,and 4,861 typed relocation roles are retained.

[Summary](summary.json) · [Original evidence](evidence.json) · [Native receipt](native-proof.json) · [Provider contracts](provider-contracts.json) · [Next steps](next-providers.json)

This page retains the standalone experiment and its88.09% baseline. Subsequent source/original-coordinate integration passed;current coverage is88.32%. See the [integration evidence](../record-sequence-integration-2026-10-25/readme.en.md). Physical/OTA compatibility remains unproved.
