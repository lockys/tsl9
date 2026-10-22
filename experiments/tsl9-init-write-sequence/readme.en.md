# Five initialization writes:9F4C

[繁體中文](README.md)

The complete official ID2966 V4.1.60 leaf is `[0x9F4C,0x9F74)`, called at`0x9260`. One readable C source is compiled as C11 and C++17. Actual `volatile uint32_t` writes perform this sequence:

```text
WRITE32[40003000] = 5555
WRITE32[40003004] = 0003
WRITE32[40003008] = 05DC  (1500 decimal)
WRITE32[40003000] = AAAA
WRITE32[40003000] = CCCC
```

Empty register ports preserve the first three instruction boundaries and normal A4=`CCCC`/A5=`40003000` outputs without opcode carriers. Other GPR/GP/SP/RA are unchanged. The original leaf contains no read, call, frame, CSR, fence or poll. A different6B function begins immediately at`9F74`.

## Run

From the project root, point the variables to the existing local tools:

```sh
python3 experiments/tsl9-init-write-sequence/verify.py --project-root "$PROJECT_ROOT" --tool-dir "$LLVM_BIN" --build-root experiments/tsl9-init-write-sequence/build/my-run
python3 experiments/tsl9-init-write-sequence/verify.py --project-root "$PROJECT_ROOT" --tool-dir "$LLVM_BIN" --replay experiments/tsl9-init-write-sequence/build/my-run/c/verification.json
```

Windows can use `py -3` and PowerShell variables `$env:PROJECT_ROOT`, `$env:LLVM_BIN`. The build directory must be new. No tools are downloaded, and no RV32/MMIO execution, emulation or hardware operation occurs.

The first40B candidate reordered the first three instructions; its local `build/probe-v1` is preserved. After explicit empty-port ordering, both C11/C++17 objects and linked functions in`build/probe-v2` match all40B/15 instructions. This is whole-function equality, beyond comparing just store values. Formal receipts and the public summary are in the [analysis directory](../../analysis/init-write-sequence-2026-10-23/summary.json).

**This is not a complete firmware.** The write pattern alone does not identify the chip, peripheral meaning or timeout. Complete main/resident/vector/IRQ, physical RAM ownership and OTA compatibility remain unproved. Diagnostic ELF placement at the original VA is for static comparison; no firmware BIN is generated. `--require-firmware-ready` must refuse.

The tool reads the pinned official BIN already in the repository; there is no `--firmware` parameter. Formal local receipts are `build/verified-v3/{c,cpp}/verification.json`:13 negative controls,4 actual recipes and2 actual ELFs per language. ABS providers are zero; compiler local ABS metadata is listed separately.
