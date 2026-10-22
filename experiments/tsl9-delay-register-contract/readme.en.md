# Delay helper: original register contract

[繁體中文](readme.zh-TW.md)

Readable C reconstruction of official ID2966 V4.1.60 `[0x19764,0x1979A)`. The complete C11 and C++17 functions are **54 bytes / 22 instructions**, byte-identical to the original in both objects and separately linked components. The identical source is curated at [src/native/timer/delay.c](../../src/native/timer/delay.c).

## Implementation and contract

Volatile accesses, multiplication, bit operations and polling are C. Inline asm supplies fixed-register/live-GP ports and materializes zero in A3 after the first fresh read. There is no copied instruction stream, naked function or constant external provider.

With B=0xE000F000:

1. Fresh R32(B+4), then A3=0; clear bit0 and write back.
2. Fresh R8(live GP+382), multiply by full entry A0; write low32 to B+16 and zero to B+20.
3. Separate fresh R32/OR0x10/W32 and fresh R32/OR0x21/W32 at B.
4. Repeated fresh R32(B+4) until bit0 is set; finally fresh R32(B), clear bit0 and write back.

Normal outputs: unchanged A0/A1; A2=product, A3=0, A4=final fresh CTRL with bit0 cleared, A5=B. Only A2/A3/A4/A5 are written. No frame, call, CSR or fence. A3 is still its entry value if the first read faults; A2 is still its entry value if the GP byte read faults. Whole-code equality supports the local instruction sequence, rather than proving the global fault/IRQ context.

The C return type describes only A0. Other register residues depend on this recipe and actual output; arbitrary C callers do not automatically receive this extended contract. This is a separate translation unit. It has not replaced the old timer within the NV callback or been integrated into an OTA BIN.

## Offline verification

From the project root, supply installed LLVM and the original firmware explicitly:

```sh
python3 experiments/tsl9-delay-register-contract/verify.py --project-root . --tool-dir "/absolute/path/to/llvm/bin" --firmware "/absolute/path/to/ID-2966-V4.1.60-decoded.bin"
```

On Windows use `py -3` or `python` if needed. The actual run used Windows Android NDK27.1.12297006/LLVM18. Tool and stdint hashes must match; other platforms were not tested. The shell wrapper delegates to Python and was not executed in this Windows session.

```sh
python3 experiments/tsl9-delay-register-contract/verify.py --project-root . --replay "/absolute/path/to/build/native-v3/c/verification.json"
```

Latest local receipts: `build/native-v3/{c,cpp}/verification.json`. Checks cover the complete FUNC, exact allocated section shapes/flags/types, UND/global ABS, relocations, actual compiler dependency closure, tool/source hashes, commands and logs, followed by read-only replay. IR is retained for review; the checker does not claim a separate IR semantic proof. GPR/access facts follow from the original rows and complete code equality.

| Artifact | Function bytes | Allocated bytes | Detail |
| --- | --- | --- | --- |
| C object/linked | 54 | 54 | No relocations, function VMA=0 |
| C++ object | 54 | 94 | 40-byte .eh_frame, 3 unwind relocations |
| C++ linked | 54 | 98 | 44-byte .eh_frame, function VMA=0x2C, no relocations |

These VMAs are offline layouts. `native-v1` failed at 58B/24 instructions because A2 became an early scratch register; its output remains retained. A read/write A4 register barrier produced code-exact `native-v2`; verifier hardening produced `native-v3`. Older receipts are historical snapshots, not claimed replayable with the revised verifier.

## Remaining gaps

Physical chip, GP initialization order/scale units, complete IRQ/memory placement, installed ROM/BOOT, NV callback frame/source slot and whole-device startup remain unproved. The original has no timeout and the reconstruction preserves its polling condition. Tools compile, link and read files only; no RV32/MMIO execution, firmware BIN generation, hardware operation or network access.
