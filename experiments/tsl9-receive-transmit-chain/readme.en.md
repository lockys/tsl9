# Original-PC receive, dispatch and transmit integration

[繁體中文](README.md) · [English](readme.en.md)

Twelve selected `src/` C units are freshly compiled as both C11 and C++17. Algorithms are unchanged and no original binary carrier replaces C. Two genuine6B/18B functions use explicit preprocessor name mappings to their callers; their bodies and strong FUNC definitions are retained.

The full partial link contains **1902B/662 instructions/107 FUNC**,97 pending relocations and four genuine UND providers:9454,9B36,12ABE,14D2E. Its five missing callsites belong to the314B queue consumer. Excluding that unit yields a separately verified **1588B/555 instructions/97 FUNC** across nine original-PC spans. Every linked code byte matches ID2966 V4.1.60; UND/RELA/global ABS are zero. This does not close the full application.

Six opaque resident transfers,17 RETs and two bounded fill-table transfers retain separate contracts. RX LOAD size is68558B, including66970B of unproved gaps. The ELF is not a flashable BIN.

The frozen upstream recipes and actual artifacts must already exist locally; public JSON is not a replacement for object files. Only the existing Windows LLVM18/NDK27.1 toolchain was tested. No tools are downloaded.

```sh
python3 "$TSL9_ROOT/experiments/tsl9-receive-transmit-chain/build-v2.py" --build --out-dir "$TSL9_ROOT/experiments/tsl9-receive-transmit-chain/build/my-run" --llvm-bin "$LLVM_BIN"
python3 "$TSL9_ROOT/experiments/tsl9-receive-transmit-chain/verify-v2.py" --out-dir "$TSL9_ROOT/experiments/tsl9-receive-transmit-chain/build/my-run" --llvm-bin "$LLVM_BIN" --write
```

Use a fresh directory for building. Replay through the verifier without `--write`. `--strict-firmware` returns1 after verification because installed hardware/resident/IRQ/OTA remain unproved. Failedv1, older checkers and receipts remain untouched; v2 tightens metadata and transitive provenance over identical compiler outputs.

The proof checks28 actual commands per language,67 artifacts, MD include closure, consumed objects,107 real bodies,97 typed edges, all nine original code spans and1217 complete LLVM address rows. It passes1538 bounded negative controls per language; independent review rejects24/24 provenance/PHDR mutations.

See the [analysis, gaps and public evidence](../../analysis/receive-transmit-chain-2026-10-23/README.md). No HOST model, ISA emulation, hardware or vendor API ran. No flashable BIN was added.
