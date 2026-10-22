# Bounded reordering of callback save words

[繁體中文](README.md)

This stage accepts an actual single-FUNC624 C/C++ ET_REL object. It swaps the existing two-byte `SW RA,44(SP)` at offset+2 with `SW S0,40(SP)` at offset+4, restoring the relative order of eleven stack stores. It creates no instruction, uses no original BIN as a code-generation template and does not fill the remaining eight bytes.

Admission checks the 48-byte frame, all eleven register/slot pairs, one honest GLOBAL FUNC624 in an independent code section, zero REL/RELA, no interior symbols and no file-storage/header/section overlap. Every ELF byte outside the four selected bytes must remain identical. Symbol, section and relocation metadata are untouched.

## Evidence boundary

The original callback also places a four-byte SLLI A5 before its first S0 store; other native register operations and call locations differ. **This proves relative save ordering, not the whole entry prefix, resident call/return ABI or placement.** Being smaller than632 is only numeric fit. It does not establish safe padding/tail ownership or produce a flashable BIN.

```sh
python3 -B experiments/tsl9-v4160-callback-registers/postpass/frame.py --project-root /absolute/re-tsl9 --input /absolute/re-tsl9/experiments/tsl9-v4160-callback-registers/build/new/raw.o --output /absolute/re-tsl9/experiments/tsl9-v4160-callback-registers/build/new/ordered.o --receipt /absolute/re-tsl9/experiments/tsl9-v4160-callback-registers/build/new/frame.json
python3 -B experiments/tsl9-v4160-callback-registers/postpass/frame.py --project-root /absolute/re-tsl9 --replay /absolute/re-tsl9/experiments/tsl9-v4160-callback-registers/build/new/frame.json
```

All three paths must be distinct and inside this model's build directory. Outputs are create-only. Replay reads both actual objects, recomputes the existing-word swap and compares every byte. No RISC-V execution/emulation or broadening of old IRQ/Flash/TX schedulers occurs.
