# TSL9 TX entry and frame observation order

[繁體中文](readme.zh-TW.md)

This offline component covers `0x8A56..0x8B6E` with a real 8-byte entry, a 270-byte typed C11/C++17 valid body and a 2-byte compiled returning C leaf. The actual linked extent is 280 bytes. No BIN is exported and the existing twelve-function image is unchanged.

The narrow entry uses only LI A5,1039 and unsigned BLTU A5,A3. A standard R_RISCV_BRANCH relocation targets the real typed RET leaf at original 0x8B6C. Valid input falls through to C; oversized input touches no SP, RA, A0 or stack. There is no whole-function assembly, borrowed original-byte template, padding, custom branch encoder or false noreturn/unreachable contract.

Two identity-preserving C layout hints restore actual ROM gate return PCs 0x8A90/0x8AB6 and the RAM PCREL anchor at offset0x80. HOST expands these hints to identity; its algorithm is unchanged and the old HOST suite was not rerun this milestone.

The explicit `postpass/schedule.py` reorders only five existing compiled C.SWSP words and five existing C.LWSP words. It restores source save order, RA/S1/S2/S3 reads before descriptor SH, and S0 read after SH but before the ROM-tail pointer read. All other instruction-word order, metadata, length and relocations remain unchanged. This is C/C++ plus narrow ABI layers, not pure compiler output, and does not claim fault/alias equivalence with the unscheduled object.

```sh
sh experiments/tsl9-v4160-tx-register-abi/verify.sh --tool-dir /path/to/audited/llvm/bin --language both
python -B experiments/tsl9-v4160-tx-register-abi/verify.py --project-root . --replay /path/to/ordered/c/verification.json
```

Set PYTHON to choose Python. The default build is a fresh UUID directory. Explicit --build-root must be new and inside this model's build directory. --firmware accepts the pinned original validation input and never supplies generated code bytes. Replay is read-only and rejects build-only tool/language/output options.

Each language freshly compiles three source inputs: raw assembly entry with no preprocessing/includes, typed body and typed leaf. Two LLVM IR outputs are retained. Actual -MD closure covers three project inputs for body, one for leaf and the real Clang resource include/stdint.h. The audited tool binaries are LLVM NDK for Windows; portable Python/shell interfaces do not constitute live Linux/macOS compiler validation.

pre/{c,cpp} retains compiler outputs. ordered/{c,cpp} retains the explicit scheduling receipt, ordered body, relocatable composite and COMPONENT-ONLY-NOT-FIRMWARE.elf. The actual ET_REL has one AX280 allocation, real FUNC offsets0/8/278 and sizes8/270/2, three standard relocations and sole unresolved SRAM symbol. Strict missing-RAM linking and actual out-of-range-leaf linker controls must reject. Numeric 0x2000B18C witnesses an address only; no SRAM or ROM implementation is supplied.

Independent static checks cover entry/leaf, both gate RAs, save/restore frontiers, complete280B/96-instruction coverage, complementary original BLTU/new BGEU loop CFG, low16 counter versus live S0, live byte-copy effects, backedge and checksum finish. Whole-original ABI, private/computed-target roles, pointwise interrupt/fault behavior, complete-image integration and physical compatibility remain unadmitted. Public entry is truthfully FUNC8, not a fabricated whole-FUNC280 role.

Historical local diagnoses show that enabled shrink wrapping, a register-only guard and restore-region splitting did not repair the original single function. The ordinary C dispatcher totals290B; initial external-branch adapter lowering totals284B and was rejected. Ordinary file probes traced the earlier temporary-file failure to unusable inherited sandbox TEMP. The same compiler now uses owned per-build TMP/TEMP without permission changes or approval bypass.
