# Complete offline image with readable OTA reply

[繁體中文](README.md)

This pipeline rebuilds the76800-byte V4.1.60 ID2966 image from source. Twelve readable C/C++ functions occupy650 bytes: existing IRQ/Flash plus OTA page reply9B8E..9C0A. Another679 sections remain original-content source carriers. This is partial readable reconstruction, not recovery of the complete original project.

Actual C11 and C++17 builds compile34 carriers plus9 typed translation units. A standalone reply ABI-order stage precedes merging; the existing IRQ/Flash frame-order stage follows. Both only permute freshly compiled words, retaining pre/post objects and receipts. No archived object, old BIN, instruction template or padding supplies new code.

Both actual `NOT-FLASH-VALIDATED-reply-integrated.bin` exports equal the original:

```text
bytes: 76800
SHA256: 0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667
differences from original / previous eleven-function image: 0 / 0
```

## Rebuild and readonly checks

Run from the project root with `LLVM` pointing to local LLVM NDK tools:

```sh
sh experiments/tsl9-v4160-reply-image-integration/verify.sh --tool-dir "$LLVM" --language both
python -B experiments/tsl9-v4160-reply-image-integration/verify.py --project-root . --replay RECEIPT
```

The Python entry also accepts `--tool-dir`, `--firmware`, `--clang`, `--linker`, `--objcopy`, `--language c|cpp|both` and a create-only project-local `--build-root`. Replay rejects compiler/build overrides and mismatched explicit language. Shell wrappers honor `PYTHON`, otherwise `python3`/`python`. Actual evidence uses Windows NDK27.1.12297006; other host platforms were not tested.

Published metadata-only check:

```sh
python -B analysis/v4160-reply-image-integration-2026-10-22/implementation/check_image.py --project-root .
```

Working-tree cases use `apk-analysis/tsl9-v4160-reply-image-integration-2026-10-22/`. Default checking verifies sealed sources/selected metadata without automatically replaying artifacts. `--require-local-builds` requires both selected actual archives; `--receipt FRESH_RECEIPT` accepts fresh evidence under a new root. Generated objects, logs and controls stay in ignored `build/`; published metadata does not imply those archives are published.

## Evidence and limits

The61 chronological commands comprise59 LLVM compile/query/link/export operations and2 explicit Python ABI stages. The43 actual `-MD` rules bind74 project inputs,14 generated filtered/adaptor inputs and1 discovered Clang resource header. Fourteen TUs actually include that resource header.

All691 original allocations and679 retained carrier hashes pass. Actual8269 RELAs partition into8257 fully retained roles and12 typed JALs, with53 canonical relative bindings,21 incoming entries and11 discharged private branches. Reply's original public NOTYPE/size0 and local relative entry0 remain; new C FUNC124 is separate. Actual9DF4 is a2-byte C.JAL with RA9DF6.

All15 LOAD byte/memory/permission extents agree with section ownership and the exported bytes. There are no holes, hidden padding, RAM or ROM bytes in the export. Excluded `.llvm_addrsig` metadata is explicitly checked as the old56-byte prefix plus one new native-function symbol index; final ELF omits it.

Each language rejects41 actual artifact/receipt controls:30 ELF/RELA/image,4 dependency,6 ABI receipts and1 chronology. Five readonly CLI cases also pass. Strict linking rejects the missing resident ROM provider; successful witness ELF only declares numeric0x40000 and supplies no ROM bytes. This whole image retains actual original TX code, rather than the previous standalone component's numeric TX witness.

Byte identity is not proof of resident ABI, arbitrary SP/register destruction, async/fault behavior, computed interior entries, physical board, BLE, Flash or OTA compatibility. No RV32 execution, ISA emulation, network, packets or device I/O occurs.
