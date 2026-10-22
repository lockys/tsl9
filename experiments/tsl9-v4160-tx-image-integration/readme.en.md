# TX whole offline image integration

[繁體中文](readme.zh-TW.md)

This experiment freshly compiles and links a complete 76,800-byte offline image. Thirteen original regions, totaling 930 bytes, have readable C/C++ and explicit ABI providers. They form fifteen real FUNC providers. The other 678 sections remain source carriers; this is a partial readable reconstruction.

The canonical `__tsl9v4160_call_8a56` is an allocated FUNC8 entry, followed by a LOCAL FUNC270 typed body and a GLOBAL FUNC2 typed returning leaf. No FUNC280 fiction, ABS function provider, padding, original opcode borrowing, or old-BIN fallback is used. Standard assembly mnemonics and `R_RISCV_BRANCH` describe the narrow entry. A separate source-owned stage moves only five existing compiled SWSP and five existing LWSP words. The sealed reply and IRQ/quarter ordering tools remain unchanged.

The measured pipeline has 46 compilation units: 34 carrier C/C++, eleven typed C/C++, and one directly assembled entry. Its 67 internal recipes comprise 64 LLVM commands and three explicit Python ABI stages. An outer resource query and generator invocation are recorded separately. The 45 actual `-MD` rules observe 78 existing project files, fourteen generated sources/adapters and one Clang `stdint.h`. Assembly is a directly pinned input without preprocessing. The 85 source-ledger pins are not a claim that all 85 files were compiler dependencies.

```sh
python -B experiments/tsl9-v4160-tx-image-integration/verify.py \
  --project-root /path/to/project --tool-dir /path/to/LLVM --language both
```

The POSIX `verify.sh` wrapper accepts the same arguments and `PYTHON=/path/to/python`. An optional `--firmware` selects byte-identical original ID2966 firmware for validation only. A default UUID build is create-only; an explicit `--build-root` must be new and inside this model's `build/`. The Python/sh interfaces are portable; only the pinned Windows NDK LLVM tools were actually tested.

Each `BUILD/{c,cpp}/` contains fresh objects, eleven IR files, 45 dependency rules, three ABI receipts, partial and linked ELF witnesses, `NOT-FLASH-VALIDATED-tx-integrated.bin`, and `verification.json`. Every exported byte must be actual section/LOAD storage. Original firmware is validation input only, never a compiler/linker/export input.

```sh
python -B experiments/tsl9-v4160-tx-image-integration/verify.py \
  --project-root /path/to/project --replay /path/to/verification.json
```

Replay reads real artifacts, logs, exact recipes, dependencies, current source/tool hashes and ABI evidence. It does not compile or execute the target. Published metadata does not imply retained build archives; fresh compilation creates new local evidence.

All 76,520 bytes outside TX remain identical to original. There are 93 changed bytes inside TX280. The image SHA256 is `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`. Actual inventory is 691 allocations, 8,261 RELA records (8,246 outside, twelve prior typed JALs and three TX records), 53 canonical relative bindings, 29 outside incoming references and fifteen LOADs. Seven original TX control labels and one PCREL anchor are accounted for separately.

Strict linking rejects the absent real ROM provider. A numeric `0x40000` witness supplies no ROM code. Complete original ABI, computed targets, asynchronous/fault behavior, physical hardware compatibility and OTA acceptance remain unproved. This BIN is an offline experiment, not flash-validated firmware.
