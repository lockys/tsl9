# Seven-byte record queue, callback and encoder

[繁體中文](README.md)

Original1787C–1798A covers270B/94 instructions/14 architectural regions. Actual C11/C++17 objects preserve246 non-control bytes andseven typed references;data-only original-VA encoding matches all270B. Queue16B/constructor32B frames,the frameless encoder,AUIPC,two fresh count reads,fresh post-call index/count updates andword/halfword/byte store ordering are retained.

Architectural blocks require original adjacency/private register contracts,not ordinary C APIs. Trial-v2 is the accepted receipt. Trial-v1 was rejected because the assembler shortened an original4B ADDI; its local outputs remain unclaimed. Full-width asm ports now explicitly retain4B encoding.

```sh
python3 experiments/tsl9-record-queue/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-queue/build/trial-v2
```

Set LLVM_BIN to an existing LLVM directory. Verification compiles andreads normal static artifacts without target/HOST-model execution,ISA emulation,hardware orBIN generation. Direct17666,installed ROM/ABI,original placement,memory,startup/IRQ andOTA remain unproved.
