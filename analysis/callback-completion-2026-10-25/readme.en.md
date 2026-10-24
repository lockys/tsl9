# Callback gaps and input packing: offline reconstruction

Five whole functions are reconstructed as C and separately compiled as C11/C++17. Original-instruction comparison covers 444 bytes, 162 instructions, 29 direct transfers and two callback-address pairs. Explicit architecture ports retain original registers, stack and private calls.

| Entry | Confirmed static behavior |
|---|---|
| `0x838E` | Check halfword/byte eligibility at two positions with a four-byte stride. Cap input length at 30 bytes, pack a two-byte header and payload, and pass them to an existing dispatcher. Preserve the 80-byte frame and selection order. |
| `0xA38E` | Select modes one/two from the GP+357 byte, then conditionally invert or retain an existing state result. Keep only its low bit at the end; do not normalize every intermediate result to Boolean. |
| `0xA3CC` | Gate processing with unsigned threshold 34, 16-bit magnitude threshold 61 and other state. Otherwise increment and truncate a byte retry counter. Clear it and pass the self-callback address when the result exceeds 29; otherwise reschedule with parameter 1000. |
| `0xAB5E` | Read the entire byte at nominal RAM address `0x2000BEE9`. |
| `0x10556` | Load a signed halfword at GP+320, compute its magnitude using the original sign operations, then truncate/zero-extend to 16 bits. Preserve the original -32768 to 32768 semantics. |

Evidence: [original instructions](evidence.json), [reconstructed C](../../src/native/receive/callback_completion.c), [compiler and comparison](../../experiments/tsl9-callback-completion/build-v1.py). [繁體中文](README.md)

Whole-source proof passes 214 comparisons/428 objects. Two imports are resolved without new dependencies; 132 remain. All 44,085 selected original-coordinate bytes match. Static flow covers 2,406 direct transfers with no ordinary continuation gaps. No unprovided callback-address reference remains in this selected component; indirect runtime targets remain unproved. Time units,feature attribution,private ABI and hardware/OTA remain unproved; no target or hardware execution and no new BIN.
