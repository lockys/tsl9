# Resident providers and RF configuration candidate

[繁體中文](README.md)

Original1753A–17666 covers300B,103 instructions and12 architectural regions. Actual C11/C++17 objects preserve298 non-control bytes andone typed branch;data-only original-VA encoding matches all300B. A6/A7 private ports,the guard before the16B frame,the48B constructor andeight indirect calls are retained.

```sh
python3 experiments/tsl9-resident-providers/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-resident-providers/build/trial-v1
```

Set LLVM_BIN to an existing LLVM directory. Only compilation andnormal static-artifact checks occur;no target/HOST-model/ISA execution orhardware. SDK RF_Config/RF_SetChannel macros are default profile correspondence,not installed ROM,physical MCU,ABI orOTA proof. Architectural blocks are not ordinary C APIs;literal callbacks still require original placement.
