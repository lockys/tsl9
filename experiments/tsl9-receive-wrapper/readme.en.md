# Receive entry and flag-consumer pipeline (offline C/C++)

[繁體中文](README.md)

Reconstructs official ID2966 V4.1.60 `16B0A..16B50`,70B/26 instructions: read register `2C`, handle `61`/`71`, restore the frame and tail-jump to write `2C=0`. After the first downstream call, original code consumes then-live physical S0/S1; unknown resident preservation is not assumed.

The14B entry falls through to a56B body. All54B outside four JAL windows match; four calls/tail jump retain three genuine UND providers. Another actual ET_REL artifact places the prior62B consumer and this70B receiver in one132B section with a real receiver definition. Relocations remain; this is not resolved executable code.

The original16B frame and fresh saved-slot reads are retained. RA/SP/S0/S1 belong to explicit architectural ports. S0 storage and its mask0x02 test/branch use assembly ports to avoid LLVM18 adding callee-save spills. Other conditions, arguments and call flow use C. This is neither a pure-C second-bit test nor an ordinary C ABI function.

```sh
python3 experiments/tsl9-receive-wrapper/verify.py --project-root . --tool-dir "$LLVM_BIN" \
  --build-root experiments/tsl9-receive-wrapper/build/my-check
```

Set `LLVM_BIN` to existing RISC-V LLVM; `my-check` must be new. Replace `--build-root` with `--replay` to verify a local receipt; `--require-firmware-ready` must reject. No downloads, RV32/MMIO execution, BIN generation or flashing occur.

Downstream SPI/packet/installed-resident implementations and full ABI, main-loop/IRQ/physical hardware and OTA compatibility remain unproved. Earlier frame-mismatch probes remain local and are excluded from `src/`.
