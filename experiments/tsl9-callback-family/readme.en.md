# Native callback-table reconstruction

[繁體中文](README.md)

Original V4.1.60 range `901A–9124`: 266B, 102 instructions and 20 architectural regions. Actual C11/C++17 objects preserve all 244 non-control bytes plus eight typed direct branches after data-only original-VA encoding. `9070` is a shared loop, while frame entries are `901A`, `907A` and `90B0`.

Four indirect calls, one `t1` indirect tail transfer, original 16B frames and shared exits are retained. These architectural C blocks require original adjacency and private register contracts; they are not ordinary independently callable C APIs. AUIPC still depends on original PCs. VMA-zero ET_REL does not prove original placement or a flashable image.

```sh
python3 experiments/tsl9-callback-family/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-callback-family/build/trial-v1
```

Set LLVM_BIN to an existing LLVM tool directory. Verification reads retained native objects and receipts without target/HOST-model execution, emulation, hardware or network access. Installed ROM, full ABI/startup/IRQ and BLE OTA compatibility remain unproved.
