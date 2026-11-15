# 0xab68 isolated byte getter

The pinned v4.1.60 original bytes at `0xab68` are `17150020034505388280`: AUIPC and LBU resolve to `0x2000bee8`, followed by return. The candidate is an experimental unsigned volatile byte load; the stock inline-assembly owner remains unchanged.

`verify_compiled.py BIN LLVM_BIN` compares separately compiled C11/C++17 section bytes at the original PC under a numeric data-address binding, with wrong-address, signed, increment and constant controls. `test_instruction_projection.py` checks the raw instruction fields and target. This is an isolated check; its ELF section check does not verify the candidate function's symbol name or callers, and identical bytes for a single load do not establish that removal of `volatile` is harmless in other contexts.

Static evidence records direct calls at `0x10394` and `0x13ac6`; this is not an exhaustive call graph. A future integration must check the actual owner and aliases, call relocations, RAM binding and the full build. None of this establishes runtime reachability, device behavior or flashability.
