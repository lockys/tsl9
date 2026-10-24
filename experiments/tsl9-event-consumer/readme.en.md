# Event consumer and callback family

[繁體中文](README.md)

Original17666–1787C covers534B,187 instructions and35 architectural regions. Actual C11/C++17 objects preserve472 non-control bytes and23 typed references;data-only original-VA encoding matches all534B. The16B/32B/48B frames,shared restores,four indirect calls,fresh post-call GP/queue accesses andoriginal signed REM are retained.

These architectural blocks require original adjacency/private register contracts,not ordinary C APIs. Trial-v2 is accepted. Trial-v1 failed because an original4B ADDI compiled as2B; its local outputs remain unclaimed. Explicit width now retains the original instruction.

```sh
python3 experiments/tsl9-event-consumer/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-event-consumer/build/trial-v2
```

Set LLVM_BIN to an existing LLVM directory. Only compilation andnormal static-artifact checks are performed;no target/HOST-model/ISA execution,hardware orBIN generation. Table1AAE8/initial index bounds,literal callback placement,installed ROM/ABI andoriginal startup/IRQ/OTA remain unproved.
