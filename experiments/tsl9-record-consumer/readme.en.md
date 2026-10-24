# Record copy, clear and completion callback

[繁體中文](README.md)

OriginalC776–C7E8 family:114B,42 instructions and11 architectural regions. Entries areC776 with16B frame,C798 withframeless clear tail,andC7AA withconditional32B frame. Actual C11/C++17 objects preserve94 non-control bytes andseven typed references;data-only original-VA encoding matches all114B.

```sh
python3 experiments/tsl9-record-consumer/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-consumer/build/trial-v1
```

GP+220 seven-byte arguments andthe distinct literal object,status-store-before-branch,fresh post-call pointer/record reads andrestore-before-tail ordering are retained. Offline compilation/normal static checks only. Callee ABI,memory ownership,hardware/ROM/IRQ/OTA are unproved;no target/HOST-model/ISA execution orBIN generation.

Integration checked: genuine42B82A8 provider andwhole102B12A08 dispatcher reused; main4424B code+456B data/299RELA/22UND. See[analysis](../../analysis/record-consumer-2026-10-24/readme.en.md). This is a diagnostic VMA-zero ET_REL, not a firmware BIN.

~~~sh
python3 experiments/tsl9-record-consumer/verify-providers-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-consumer/build/providers-v1
python3 experiments/tsl9-record-consumer/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-consumer/build/component-v1
python3 scripts/check-record-consumer-publication.py
~~~
