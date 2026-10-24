# Original vector pointer-data C/C++ experiment

[繁體中文](README.md) · [Analysis](../../analysis/original-vectors-2026-10-24/readme.en.md)

[boot_vectors.v1.c](src/boot_vectors.v1.c) is copied unchanged into [src/native/startup/boot_vectors.c](../../src/native/startup/boot_vectors.c). [spec-v1.json](spec-v1.json) pins all82 words and compiler recipes. Address declarations store pointers only; an ordinary callable C ABI is not established.

[build-v1.py](build-v1.py) compiles and inspects actual pointer-data objects. Origin/curated complete section/symbol projections must match except for local FILE identity. [integrate-v1.py](integrate-v1.py) uses [joined-v1.ld](joined-v1.ld) to extend the genuine startup component and verifies all144 references and their ownership. No handler substitutes, ABS providers, RAM allocation or hardware operations are added.

With the retained complete local artifacts and pinned toolchain, replay read-only:

~~~sh
python3 experiments/tsl9-original-vectors/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-vectors/build/data-v1
python3 experiments/tsl9-original-vectors/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-vectors/build/component-v1
~~~

Set LLVM_BIN locally; Windows may use its installed python. Fresh builds require a new output folder. Public receipts cannot replace missing native artifacts or establish cross-machine replay.

The manifest's native_data_units registration is independently verified here. The frozen function verifier remains unchanged. Its fresh build/curated-source/original-vectors-20261024-v1/verification.json covers53 code units and106 comparisons/212 objects; pointer data separately adds2 comparisons/4 objects.

The [parent manifest derivation](parent-manifest-v1.py) recovers the exact79-file parent bytes. Only one C file and independent data-unit registration are added. [integration-v1.json](integration-v1.json) pins actual receipts, sources, objects and tools. The parent global manifest has changed, so its original whole-manifest replay is not claimed; the new proof checks the exact extension and every other retained parent input/product.

Full IRQ context, original hardware/ROM, main/memory closure and BLE OTA remain unproved. No flashable BIN is generated.
