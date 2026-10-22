# Register providers and receive pipeline (offline C/C++)

[繁體中文](README.md)

Reconstructs official ID2966 V4.1.60 read `16994..169DC`,72B/26 instructions, and write `16A30..16A7C`,76B/28. Outside three SPI calls each,60B/64B match the originals. The32B frames, two independent GPIO conditions, fresh argument slots and RA reload order are retained.

Read sends3/fresh A1/0; write sends2/fresh A1/fresh A2. Both reload RA before the32-bit cleanup write `40010810=17`, then retain the third SPI result in A0 rather than forcing0. Selection writes `40010814=16`/`1`; channel3 performs both, and channel0 still performs SPI and cleanup.

An actual280B ET_REL combines consumer62+receiver70+read72+write76. Twelve JAL relocations remain: four reference genuine internal FUNC definitions, eight reference two UND providers,SPI/packet. **This proves linkage structure, not resolved executable code or a flashable BIN.**

```sh
python3 experiments/tsl9-register-providers/verify.py --project-root . --tool-dir "$LLVM_BIN" \
  --build-root experiments/tsl9-register-providers/build/my-check
```

Set `LLVM_BIN` to existing RISC-V LLVM; `my-check` must be new. Replace `--build-root` with `--replay` for a local receipt; `--require-firmware-ready` must reject. C11/C++17 use explicit GNU register/assembly architectural ports. No downloads,RV32/MMIO execution,BIN generation or flashing occur.

SPI/packet/installed-resident and full IRQ/fault/physical-hardware/OTA compatibility remain open. Read's implicit A1 capture and A0 residue are measured architectural-port evidence under fixed compiler recipes, not arbitrary-compiler C guarantees. Public receipts use portable paths and originals remain local; diagnostics remain candidate findings.
