# Seven-word event record DATA

[繁體中文](README.md) · [C/C++ definitions](event_words.v1.c) · [Current formal integration](../tsl9-record-mode-row-integration/readme.en.md)

This milestone reconstructs the **28-byte conditional read window** at `0x1AAE8..0x1AB04`. Actual C11/C++17 DATA objects and partial components are identical; every new DATA byte matches the official APP. This remains experimental source, pending curated `src/` and new original-coordinate linkage. Formal coverage stays **95.72% / 163 C/H files**.

## Confirmed program behavior

- The complete `0x176F8..0x1787C` consumer contains 388B / 135 instructions and a 48-byte frame. All CFG instructions are reachable, normal exits restore SP, and all bytes match existing native C/C++ original-coordinate ELFs.
- The word load at `0x17844` uses `0x1AAE8 + 4*uint8(GP+370)`. The 28B window covers the read only when its index is 0 through 6 at that read.
- The store at `0x17868` updates the low byte of `(old_index+1)%7` after the read. A u8 input plus one lies in 1 through 256, so the original signed REM result lies in 0 through 6. This does not bound the first read or justify a new pre-read clamp.
- Across the selected 69,412 CODE bytes, these are the only direct GP accesses overlapping this byte. There are also 196 GP ADDI address takes. Aliases, indirect writers, excluded CODE, and IRQ/DMA are not fully covered; no global invariant is claimed.
- Bits 0 through 23 of the table word become record offsets 2, 3, and 4. Other record bytes retain their original frame accesses. The highest word byte is not used by these three writes.
- The complete fresh four-byte `LW(SP+12)` is preserved despite earlier copy arguments of length 7. `((word>>18)&31)+1` selects SP+14 bits 2 through 6, not the table byte just stored at SP+12. Its range is 1 through 32; multiplication by 800 gives raw A2 values 800 through 25,600.
- The indirect transfer at `0x1782E` loads slot `0x40058` and passes A1=2. The installed callee, physical time units, and effects are unproved; these values cannot be labeled milliseconds or a lighting timer.

## Inference and limitations

The seven words are distinct and have a zero highest byte. Nonzero positions in their low three bytes follow masks `1,3,3,2,6,4,5`. This resembles a three-channel palette sequence. **That is a data-pattern inference, not confirmation of RGB wiring, lighting hardware, or a product feature.** An offline record-field / candidate-palette inspector is an [unimplemented feature idea](feature-candidates.json).

Using only the index byte width yields a conservative 1,024B envelope, including 744B beyond the supplied APP. This proves neither a full table declaration nor an actual out-of-bounds access. Only seven words / 28B were selected; no conservative envelope, excluded payload, or complete provider alias was used.

The experimental partial component contains 69,412B CODE + 4,126B DATA. Every parent allocated byte, global symbol, and all 5,270 relocation roles are retained; six APP source providers remain unresolved. A VMA 0 ET_REL object is not a flashable BIN. Installed ROM/RAM/IRQ/Flash/OTA compatibility and the global initial index remain unproved.

## Replay

With the frozen local parent artifacts and LLVM available, run from the repository root:

```sh
python3 experiments/tsl9-event-word-table-data/verify-v1.py --tool-dir "$LLVM_BIN"
```

This experiment pins the current 163-source manifest; later source extensions must retain its historical proof. All checks are offline. No target, HOST model, ISA, hardware, or third-party API execution occurred.

[Inputs](inputs-v1.json) · [Complete consumer contract](contract-v1.py) · [Native receipt](verification-v1.json)
