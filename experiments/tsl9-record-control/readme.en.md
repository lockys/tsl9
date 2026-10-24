# Record control and event scheduling

[繁體中文](README.md)

Original1798A–179FC:114B/44 instructions/12 architectural regions. Actual C11/C++17 objects preserve98 non-control bytes andsix typed references; data-only original-VA encoding matches the full range. The unsigned selector<=35 guard before the32B frame,7B record arguments,full-word SP+8/SP+12 loads,conditional GP+367/368 stores,GP+376/379 andtwo resident calls are retained.

These architectural C blocks require original adjacency/private register contracts, not ordinary independently callable C APIs. The direct1787C provider remains unresolved. Memory ownership,installed resident identity/ABI,original startup/IRQ andOTA are unproved.

```sh
python3 experiments/tsl9-record-control/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-control/build/trial-v1
```

Set LLVM_BIN to an existing LLVM tool directory. Only compilation andnormal static-artifact checks are performed;no target/HOST-model execution,emulation,hardware access orBIN generation.
