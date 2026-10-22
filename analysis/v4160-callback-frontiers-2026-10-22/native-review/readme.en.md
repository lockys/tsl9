# Independent native NV-read callback review

[繁體中文](README.md)

This reviewer reads actual C11/C++17 ET_REL objects, all symbols/sections/relocations, raw operand fields, complete LLVM static text, IR, successful logs and the entire `-MD` closure. It does not call the producer replay as its independent verdict. No native/MMIO/CPU/ISA/ESIL, old HOST matrix or hardware execution occurs.

Each language has one genuine global FUNC: 32 bytes / 14 instructions, no unused functions, UND0/RELA0/ABS0. Function bytes match, SHA256 `be3e03eacb688e38d8dbebdd509b900520385a2a2084136c4bdbfdd5f5caad3c`. The original entry is 30 bytes / 13 instructions, so the new function does not fit that original extent.

The complete machine operand contract and the entire IR def-use chain independently establish one fresh READ32(0x4004C), one indirect call to that value with entry A2, entry A0 and uint32(entry A1 shifted left two), ignored callee result and normal A0=0. This conditional register-call surface is not a recovered original C prototype. The IR tail marker is not a machine tail jump: actual JALR writes RA and the zero return/epilogue still follow.

The 16-byte frame saves/restores RA at SP+12. Own writes are RA/SP/A0..A5, adding A3 compared with the original wrapper. There are no own T/A6/A7/S/GP/TP writes; callee writes are separate. Extra A3 can escape on copy no-loop paths, so resident caller replacement and full original callee ABI remain unproved.

Original slot loading precedes frame creation, while the compiled version adjusts SP and saves RA first. Fault/IRQ prefix equivalence therefore fails. The isolated normal call projection requires valid aligned disjoint private stack, ordinary accesses, no asynchronous interference and a fresh slot satisfying the reviewed copy register/normal-return contract. Standard C syntax cannot establish the installed ROM's contract.

Eight actual controls per language are rejected: five valid single-operand raw-byte changes for slot, shift, source argument, RA save and call-to-tail conversion; three IR changes remove volatile, alter byte count or swap source/destination. These are bounded static checks, never executions of mutated code.

```sh
python -B check.py --project-root /absolute/project/root
python -B check.py --project-root /absolute/project/root --folder /actual/build/c --receipt /new/review.json
python -B check.py --project-root /absolute/project/root --replay /existing/review.json
```

Default mode checks metadata only. Explicit actual/replay modes reread artifacts and controls without compiling/linking or producing a BIN. `verify.sh` accepts the same arguments; previously denied Git Bash startup was not retried, so shell runtime remains unverified. Installed provider identity, Flash ownership, hardware update and flashability remain unproved.
