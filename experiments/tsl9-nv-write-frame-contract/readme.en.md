# NV write callback: frame and fresh source reload

[繁體中文](readme.zh-TW.md)

Readable C reconstruction of the stack and five calls in official ID2966 V4.1.60 `[0x197BE,0x197F0)`. This is a separate candidate, not integrated into an OTA BIN.

## Improvement

The earlier volatile single-slot candidate had a16-byte frame and source at caller SP−12. A24-byte C frame object plus compiler-saved RA/S0 now produces:

- A32-byte frame.
- Saved RA at caller SP−4 and saved S0 at caller SP−8.
- Entry A2 saved at caller SP−20, freshly reloaded after unlock/erase return.
- No initialization of the remaining frame bytes; the original does not initialize them.
- Five genuine JAL relocations requiring real C provider definitions, without ABS/constant-return stubs.

C11/C++17 callback objects are both50 bytes/20 instructions. Their first40 bytes match the original after masking only the five JAL relocation immediates, including prologue, source save/reload and argument preparation order.

## Specific remaining difference

Original tail: `LW RA -> LW S0 -> A0=0 -> SP+=32 -> RET`.

Current tail: `A0=0 -> LW RA -> LW S0 -> SP+=32 -> RET`.

Normal A0/RA/S0/SP can agree, while A0 differs during a restore fault or intervening IRQ. This is not whole-callback code or asynchronous equivalence. The original's constant zero return does not establish hardware write success.

Minimal register/JAL bridges surround C volatile save/reload and a sized stack object. There is no naked function, copied opcode carrier or hand-coded full prologue/epilogue. Initial `native-v1` reversed A1/A0 preparation; the register-dependency repair produced `native-v2`, preserving earlier output.

## Providers and evidence boundary

`src/flash_provider.c` compiles six existing genuine Flash helpers, retaining both A1 clobber repairs and noinline boundaries. `tsl9_delay_registers_19764` uses the separately compiled, whole54-byte exact delay source, rather than the old timer inside the NV translation unit.

Actual C11/C++17 component verification passed: three translation units, eight linked FUNC definitions, ten genuine JALs (including all five callback targets), allocated sections, UND/global ABS, relocations and compiler dependency closure. The six helper object hashes match the prior recipe, and the linked timer remains whole54-byte original equality. The recipe uses neither GC nor provider stubs.

C allocated size is366B; C++ is410B (366B code plus44B .eh_frame). Callback entry is0 in C and0x2C in C++; these are offline layouts, not physical Flash placement. Both linked components have zero UND, global ABS and unresolved relocations. The identical callback source is curated at [src/native/nv/nv_write_frame_contract.c](../../src/native/nv/nv_write_frame_contract.c).

## Getting started

From the project root, supply the original BIN, installed tools and a new build directory explicitly:

```sh
python3 experiments/tsl9-nv-write-frame-contract/verify.py --project-root . --tool-dir "/absolute/path/to/llvm/bin" --firmware "/absolute/path/to/ID-2966-V4.1.60-decoded.bin" --build-root "/absolute/project/path/experiments/tsl9-nv-write-frame-contract/build/new-run"
```

On Windows use `py -3` or `python` if needed. Actual tools were Windows Android NDK27.1.12297006/LLVM18; the verifier checks recorded tool/stdint hashes. Other platforms were not tested. Latest local receipts are `build/component-v1/{c,cpp}/verification.json`, including source/tool hashes, actual commands and logs.

Read-only replay does not compile:

```sh
python3 experiments/tsl9-nv-write-frame-contract/verify.py --project-root . --replay "/absolute/path/to/build/component-v1/c/verification.json"
```

Source equality to entry A2 and restored entry RA/S0 require absence of adverse frame aliases/external mutation. Existing normal helper projections do not establish complete fault/IRQ/installed-ROM identity. The original busy loops have no timeout; this candidate introduces no behavioral timeout change.

Operations read the original BIN and compile/link local components only. No RV32/MMIO execution, hardware operation or Feifan service access. Complete physical compatibility and a flashable image remain unproved.
