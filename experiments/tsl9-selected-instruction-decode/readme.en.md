# Selected source-section instruction decoding

[繁體中文](README.md)

`python scripts/verify-selected-instruction-decode.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>` rebuilds a nonflashable source diagnostic ELF and decodes its selected executable sections using LLVM with explicit `+m,+a,+c,+zicsr,+zifencei`. Both C and C++ decode 23,602 instructions with zero unknown instructions and no observed `fence.i`; a synthetic invalid-instruction negative control is detected. No candidate image or excluded range is read, and no target is executed.

The diagnostic ELF omits RISC-V architecture attributes. Without explicit features, LLVM can show multiplication and other instructions as unknown; this alone does not establish image corruption. WCH's [QingKe V4 manual page](https://www.wch-ic.com/downloads/QingKeV4_Processor_Manual_PDF.html) states that the V4 series supports RV32IMAC and identifies CH32V208 with V4C. This supports the base decoding direction; `zicsr`/`zifencei` are explicitly assumed for decoding and the tool output does not establish every CSR or side effect on the device.

Linear decoding does not verify control flow, original ABI, execution or hardware compatibility. Unselected/excluded ranges are outside scope. The full BIN and seven strict-link dependencies remain incomplete; output must not be flashed.
