# Original startup C/C++ experiment

[繁體中文](README.md) · [Analysis](../../analysis/original-startup-2026-10-24/readme.en.md)

[boot_original.v1.c](src/boot_original.v1.c) is copied unchanged into [src/native/startup/boot_original.c](../../src/native/startup/boot_original.c). [spec-v1.json](spec-v1.json) pins original bytes, sources and tools. [integration-v1.json](integration-v1.json) separately pins actual initializer data and objcopy without changing the earlier trial.

[build-v1.py](build-v1.py) compiles and inspects native objects only. [integrate-v1.py](integrate-v1.py) selects the128B section from the real C data object and uses [joined-v1.ld](joined-v1.ld) for unresolved partial linking. No assumed RAM/stack allocation or fake provider is introduced.

With the pinned local LLVM and the entire retained build set, replay read-only:

~~~sh
python3 experiments/tsl9-original-startup/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-startup/build/trial-v1
python3 experiments/tsl9-original-startup/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-startup/build/component-v1
~~~

Set LLVM_BIN to the installed LLVM bin directory. Windows may use its installed python command. Fresh trial/build operations require a new output folder. Raw receipts require all retained local products; public portable evidence cannot replace missing compilation artifacts or establish cross-machine replay.

The local curation receipt is build/curated-source/original-startup-20261024-v1/verification.json:79 files,53 units,106 comparisons/212 objects. All prior104 results and625 artifact records are unchanged. The current manifest extends an exact78-file parent by one file/unit; [parent-manifest-v1.py](parent-manifest-v1.py) derives and checks the parent's complete original bytes.

No firmware execution, ISA emulation or BIN generation occurs. Complete original-hardware startup/ROM/vector/memory/OTA compatibility remains unproved.
