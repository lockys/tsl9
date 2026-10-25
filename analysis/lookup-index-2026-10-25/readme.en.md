# Lookup-index and sequence-source provenance

[繁體中文](README.md)

This round adds offline evidence only: no firmware CODE or DATA. Integrated coverage remains **88.09%**, with 27 compiler-undefined providers.

## Confirmed local behavior

- Check 21,938 selected instructions and 64,544 reconstructed CODE bytes; freshly capture 17 windows containing 174 original instructions.
- Selected direct writes overlapping `GP+176` occur at `0xA0FA` and `0xA344`. Their fall-through paths increment then AND3, producing 0..3. No selected direct transfer bypasses the mask into either writer tail. Arbitrary indirect entries and asynchronous behavior are unproved.
- `0xA146..0xA158` loads an unsigned-byte index from memory, scales it by 2 and reads a halfword at `0x1AB48`; the lookup itself contains no AND3.
- The original GP setup and aligned word-zeroing loop cover this byte,setting it to0 after that coded startup path. Installed startup and later ROM behavior remain unproved.
- `0xA37C..0xA38E` passes `GP+172`,value0,length5 through slot `0x40048`. If the installed slot obeys the cached official SDK default `tmos_memset` contract, the write range includes `GP+176`. SDK identity/formulas are source-bound; the installed ROM and ABI remain unidentified.
- Five other sites pass `GP+128` as an argument. Opaque ROM side effects and write extents are not closed. All 185 GP-relative ADDI sites are recorded; they are not all writes or escapes.

Two masked local writers do not prove a 0..3 index on every runtime path. The unsigned-byte syntactic envelope alone is 512 bytes and extends beyond the recorded BIN; this is not evidence of an actual runtime out-of-bounds access. **No four-entry DATA definition at `0x1AB48` is supplied.**

## Corrected sequence consumer

The callback-address pairs at `0xEFE0/0xEFE4` and `0xEE8C/0xEE90` both refer to **`0xEE30`**. `0xEF6C..0xEF76` instead has just three instructions,reading and returning one byte at `0x2000BF8C`.

`0xEE30` reads a 16-bit counter at `0x2000BF84` and limit at `0x2000BF86`. Only counter<limit reaches the halfword read through the pointer at `0x2000BF88`. If the configured pointer and limit remain correlated:

| Original source | Configured limit | Conditional read range (exclusive end) |
|---|---:|---|
| `0x1A430` |17 | `0x1A430..0x1A452`,34 bytes |
| `0x1A454` |17 | `0x1A454..0x1A476`,34 bytes |
| `0x1A478` |53 | `0x1A478..0x1A4E2`,106 bytes |

These are not original declaration extents. Neighboring addresses are not used to guess 36/36/108 bytes. All writers,pointer/limit correlation under asynchronous execution and physical meanings remain unproved,so these three DATA providers remain unsupplied.

[Replayable result](result.json) · [Original instruction evidence](evidence.json) · [Next steps and gaps](next-providers.json) · [Offline inspector](../../experiments/tsl9-lookup-index/readme.en.md)

No firmware,HOST-model,ISA or hardware execution;no vendor requests or new BIN. These local facts do not establish complete RAM/ROM/OTA compatibility.
