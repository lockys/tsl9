# Original trap / startup numeric contract

[繁體中文](README.md) · [Existing LLE C/C++](../tsl9-resident-lle-callback-gateway/readme.en.md)

This study compares **122 original V4.1.60 reset bytes /33 instructions** with two saved official WCH headers pinned by commit andSHA. The added C11/C++17 source contains compile-time numeric constraints,not executable functionality,an IRQ handler or a firmware provider.

| Official candidate name | Index | APP vector word | Original value |
| --- | ---: | --- | --- |
| Ecall_M_Mode_IRQn | 5 | 0x804C | 0x8448 restore |
| Ecall_U_Mode_IRQn | 8 | 0x8058 | 0x8448 restore |
| BB_IRQn | 63 | 0x8134 | 0x1873E |
| LLE_IRQn | 64 | 0x8138 | 0x8498 wrapper |

These are actual enum/byte correspondences,**not verified physical mtvec-mode3 dispatch**. See [source provenance](source-provenance.json) and [full derivation](evidence-v1.json) for saved primary references,line numbers and hashes. No new documents were downloaded.

## New constraints

Original reset0x186AA..0x18724 formsGP=0x20004000,SP=0x20010000,vector base0x8038 andmtvec=0x803B,and writesCSR0x804=3. The saved core header documents bit1 as the nesting enable/disable bit;it is initially set under that candidate mapping. Original restore0x8448..0x8450 usesCSRRS mask32,setting bit5 while preserving other bits. It does not disable bit1. **The physical meaning of bit5 andmode3 remains unknown.**

If original reset zeroing completes,GP+384=0x20004180 lies inside0x20004080..0x2000C958 and the callback word is initially zero. The original LLE wrapper directly calls its loaded pointer. Therefore slot2-to-GP+384 binding must precede every possible LLE dispatch,and GP must remain stable across ROM calls. This ordering is unproved;no IRQ policy was changed.

## Verification and reproduction

Actual C11/C++17 objects are identical. Two independent ELF readers compare the complete object:zero nonempty allocated sections,relocations,providers andimports. Fresh prior native/CFG/frame proofs retain the actual **9608 CODE+256 DATA bytes /3367 instructions**. Handlers0x57DAE/0x6020A remain unavailable. Added functional implementation bytes=0;APP byte coverage remains95.54%.

```sh
python experiments/tsl9-trap-profile-contract/build-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT" --trial native-v1
python experiments/tsl9-trap-profile-contract/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

`REFERENCE_ROOT` is the saved local official-reference root;relative paths and pins are recorded in provenance. Trial names must be fresh. With retained artifacts,use `--replay experiments/tsl9-trap-profile-contract/build/native-v1`. Tool hashes currently pin Windows NDK LLVM;cross-platform compilation is unverified. Missing inputs stop the check;no automatic downloads occur.

Physical ROM/RAM/ISA,trap frame/vector mode,GP/aliasing/IRQ nesting,global stack,the inherited4-byte startup gap,Flash andOTA remain open. No firmware,HOST model or ISA execution,hardware access,API traffic,APP integration or newBIN. **Usable replacement firmware has not been successfully reverse engineered.** A future OTA UI could display SHA-pinned evidence and unmet gates;that UI is unimplemented.

[Audit receipt](audit-result-v1.json) · [Summary](summary.json) · [C/C++ constraints](trap_context_contract.c)
