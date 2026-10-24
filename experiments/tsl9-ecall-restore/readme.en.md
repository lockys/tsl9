# ECALL native regions and vector integration

[繁體中文](README.md) · [Findings and limits](../../analysis/ecall-restore-2026-10-24/readme.en.md) · [Source](src/ecall_restore.v1.c) · [Specification](spec-v1.json) · [Link contract](integration-v1.json)

The78B/35i original8448–8496 span comprises a14B entry and64B restore suffix. Existing-frame, CSR-mask, physical-register and MRET operations are retained; the following2 zero bytes remain data. The source equals `src/native/irq/ecall_restore.c`; both actual C11/C++17 native outputs match every original byte.

From the repository root, set `LLVM_BIN` to an installed LLVM bin directory matching the pinned hashes, then replay retained local outputs:

```sh
python3 experiments/tsl9-ecall-restore/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-ecall-restore/build/trial-v1
python3 experiments/tsl9-ecall-restore/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-ecall-restore/build/component-v1
python3 scripts/check-ecall-restore-publication.py
```

Verified on Windows with Android NDK27.1.12297006/LLVM18. Native checks currently require its pinned `.exe` tools; cross-OS replay is unproved. Windows may use `python` instead of `python3`. Missing retained local artifacts are not rebuilt or downloaded by replay, and public receipts cannot replace them. A new standalone compilation uses `--trial local-new`, creating a previously absent directory without replacing old receipts.

The actual partial link contains1168B code+456B data/153 RELA/4 UND. Aliases bind real code, with no fake providers. Code and pointer-data evidence are checked separately; the frozen checker is unchanged. Historical negative matrices were not run.

The ET_REL has VMA0; it is not an executable image at original addresses. Frame creation, special CSR semantics, dynamic callbacks, ROM, physical MCU and OTA remain unproved. No firmware BIN is generated or flashed.
