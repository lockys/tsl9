# Offline linking of eight real C providers

[繁體中文](README.md)

Actual C11/C++17 ET_REL inputs are linked with pinned ld.lld using eight real C definitions. No GC or relaxation is used; genuine status/quarter functions unused by the new write entry remain present. No fabricated ABS provider, stub, original-opcode carrier or numeric ROM witness is added.

Input has 394 bytes / 148 instructions, eight global FUNC, five R_RISCV_JAL and five R_RISCV_CALL_PLT relocations. ET_EXEC output retains eight functions / 394 code bytes; all ten calls resolve to real function definitions in that ELF, with no UND, remaining RELA or ABS address provider. STT_FILE and a discarded-comment local mapping symbol are ELF metadata, not fabricated address providers.

VMA0 is only an offline component layout, with write entry at offset322. It supplies no startup, stack/GP initialization, BLE, installed ROM or flashable image. One RX LOAD exactly covers the394-byte `.text`; a separate non-LOAD PT_RISCV_ATTRIBUTES exactly describes the nonallocated `.riscv.attributes`, not executable storage. The first reader incorrectly required one total PHDR; failure/source snapshots remain under build. Only metadata parsing changed, with no instruction or link-recipe change.

C/C++ linked code matches, SHA256 `bc6c4438642ee15072836bb30b7e97fdff168b1c49bda5fe9ce9fdde58283aca`. Every byte outside actual relocation spans is preserved from the real C object. Function extents, entire code allocation, entry, segment and actual call targets are reread. A separate independent struct/immediate-bit/control review does not use this builder replay as its verdict.

**This is not a firmware BIN and cannot be flashed.** New write frames, timer register outputs and helper A1 clobbers do not satisfy the full original ABI. Retained quarter asm-call declarations additionally omit a generic A1 clobber; no observed counterexample in the pinned machine artifact does not prove the C compiler contract complete. Physical ownership, BOOT/ROM, IRQ and BLE OTA remain unproved. No native/MMIO/CPU/ISA/ESIL or hardware execution occurs.

```sh
python -B check.py --project-root /absolute/project/root
python -B check.py --project-root /absolute/project/root --component-receipt /existing/build/verification.json
```

Default mode checks metadata; an explicit receipt rereads existing sources/tools/ELFs/logs without linking or producing a BIN. Actual linking uses `probe.py --project-root ROOT --native-folder ACTUAL_NATIVE --tool-dir LLVM --build-root NEW_CASE_BUILD`, accepting only a new owned build subdirectory.
