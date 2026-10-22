# Clock initialization: read MMIO before allocating the frame

[繁體中文](README.md)

The current [clock_init.c](../../src/native/clock/clock_init.c) combines a readable C body with minimal entry/return ports to preserve the original first-read/frame order. This is an offline component, **not validated flashable firmware**.

- The first four instructions,12B, match the original: A5=40021000 → fresh LW A4 → A3=F8FF0000 → SP−16.
- C imports that A4 sample and allocated frame. No resample, second frame, spills or RA save; only SP+8/+12 are accessed.
- Actual C11/C++17 objects and linked ELFs are240B/95 instructions: entry16B, body220B, return4B. Linked artifacts have no undefined symbols or relocations; objects have two internal JAL relocations.
- All85 computational IR lines match the [previous reviewed C core](../tsl9-boot-clock-registers/readme.en.md) under the declared SSA/frame mapping. The21 C volatile loads plus entry read retain22 total loads,20 stores, three polls and the conditional normal A2–A5 exit.

## Verify

Requires Python and existing LLVM18 tools. From the repository root; no download or target execution:

```sh
python3 experiments/tsl9-boot-clock-prefix/verify.py --project-root . --tool-dir "/absolute/LLVM/bin" --build-root "/absolute/project/experiments/tsl9-boot-clock-prefix/build/new-run"
python3 experiments/tsl9-boot-clock-prefix/verify.py --project-root . --replay "/absolute/project/experiments/tsl9-boot-clock-prefix/build/new-run/c/verification.json"
```

Tested on Windows with Android NDK27.1.12297006/LLVM18; Windows can use py -3. Each language has12 in-memory negative controls for the prefix, sample, jumps, restore, W and poll contracts without relying on whole-code/IR hashes as their rejection gate. Original BOOT/Runtime inputs are reread. Current local receipts use build/component-v4.

## Limits and next step

This is a private entry ABI: never call the body as an ordinary C function. Two JAL x0 instructions are added; subsequent scheduling, PCs and timing differ. Matching the prefix does not establish complete IRQ/fault equivalence. VMA zero is not a physical allocation. No BIN was generated or flashed.

Next: compose this entry with reset/resident handoff and check placement, installed ROM identity and interrupt observations. The existing [startup limits](../../analysis/boot2580-reset-resident-2026-10-22/readme.en.md) remain open.
