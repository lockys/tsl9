# Original and source-candidate TX instruction differences

[繁體中文](README.md)

`python scripts/compare-tx-reference.py --tool-dir <LLVM_BIN> --reference <REFERENCE_BIN> --out <NEW_OUTPUT_DIR>` reads only the reference TX window `[0x8A56,0x8B6E)` (280 bytes), recompiles the source candidate and decodes both with explicit RISC-V features. It does not read the designated excluded ranges or execute the target.

Against `legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`, the original and C/C++ candidates each decode to 96 instructions; 93 of the 280 bytes differ. They share 83 instruction boundaries, with differing normalized instruction text at 20 of those. This is not a count of functional differences: instruction length, register allocation and order also affect the comparison.

At `0x8B10`, the original uses `bltu a0,s0,0x8B52` and the candidate uses `bgeu a0,s0,0x8B2E`; the conditions are complementary for the same inputs, while the loop backedges are at `0x8B6A` and `0x8B2C` respectively. At `0x8A7E`, the original compares `a4` with `a5` and the candidate compares `a5` with `a0`. Normal fallthrough from `bne a4,a0` at `0x8A76` establishes `a4 == a0`, and only `a5` changes in between, so the branch results agree on that path. Direct interior entry and interrupts that fail to preserve registers are outside this local proof; for example, with `a4=0xfffe`, `a0=0`, and `a5=0xfffe` the branch results differ. These local facts do not prove equivalence of the complete loop, external calls, asynchronous events or TX function.

The 280-byte fragments and ELFs are not complete firmware and **must not be flashed**. Seven default strict-link dependencies, 3,128 excluded bytes and hardware compatibility remain unresolved.
