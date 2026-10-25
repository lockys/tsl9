# Readonly pool and genuine interior labels

[繁體中文](README.md) · [Evidence and limits](../../analysis/record-sequence-pool-2026-10-25/readme.en.md)

`src/record_sequence_pool.v1.c` defines 89 readonly uint16_t values. Three zero-allocation OBJECT labels refer to offsets 0/36/72 in that same actual DATA section; they are not ABS address substitutes.

Compilation uses the existing hash-pinned Windows LLVM tools without downloads or installation. Set `LLVM_BIN` to that directory and choose a fresh trial from the project root:

```sh
python3 experiments/tsl9-record-sequence-pool/build-v1.py --tool-dir "$LLVM_BIN" --trial my-pool
python3 experiments/tsl9-record-sequence-pool/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-sequence-pool/build/my-pool
```

Windows can use `py -3`; PowerShell uses `$env:LLVM_BIN`. `--trial` creates a new directory; `--replay` only reads and revalidates. Existing measured parent components and local evidence sources are required. Objects and partial links are never executed. No BIN,hardware or network operations. Toolchains on other hosts remain unvalidated.

The v1 experiment itself does not modify accepted source/component state. Subsequent [curation and original-coordinate integration](../../analysis/record-sequence-integration-2026-10-25/readme.en.md) passed. Declaration extents,global bounds and installed ROM/IRQ/OTA compatibility remain unproved.
