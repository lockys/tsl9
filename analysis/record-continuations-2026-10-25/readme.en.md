# Timed records and flags: offline reconstruction

Eight whole functions are reconstructed as C and separately compiled as C11/C++17. Original-instruction comparison covers 418 bytes, 138 instructions, 20 direct transfers and four callback-address pairs. Explicit architecture ports retain original registers, stack and call behavior.

| Entry | Confirmed static behavior |
|---|---|
| `0xBD46` / `0xBD50` | Return pointers `0x2000BF11` / `0x2000BF10`, respectively. |
| `0xBD64` | Read the byte at `0x2000BF13`. |
| `0xEDF2` | Fetch record nine, toggle a full byte with XOR one, put its low bit into bit two of record byte three and pass the record to an existing output function. |
| `0xEE30` | Toggle first, compare a halfword counter and limit, then obtain an indexed halfword parameter and schedule itself or clear the limit and flag. Both paths subsequently increment the halfword counter. |
| `0xEE9A` | Depending on a flag, clear state, pass the `0xEE30` address to an existing function, zero the counter word and toggle. Return zero or one. |
| `0xEEE0` | On zero input, toggle and schedule using a mode-selected parameter 11/50. Decrement and wrap the byte counter, then conditionally schedule itself with 100/200 or the prior parameter. Nonzero input clears another flag. |
| `0xEF6C` | Return the complete toggle flag byte. |

Evidence: [original instructions](evidence.json), [reconstructed C](../../src/native/receive/record_continuations.c), [compiler and comparison](../../experiments/tsl9-record-continuations/build-v1.py). [繁體中文](README.md)

Whole-source proof passes 212 comparisons/424 objects. Seven imports are resolved without new dependencies; 134 remain. All 43,641 selected original-coordinate bytes match. Static flow covers 2,377 direct transfers with no ordinary continuation gaps. No mixed direct/address provider gap remains. Time units,feature attribution,private ABI and hardware/OTA remain unproved; no target or hardware execution and no new BIN.
