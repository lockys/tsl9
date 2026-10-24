# Original addresses and static transfer positions

[繁體中文](README.md)

The actual native linker placed **13,864B code and 674B data** from the current measured C/C++ component at the official V4.1.60 addresses. All **14,538B** and **930 relocation roles** match. C11/C++17 diagnostic ELFs are identical, SHA-256 `471defe5103e82e57c855e2ab6f4a9638edce55caa1880deedff6a5d2e8c587e`.

This is a **non-loadable ET_EXEC diagnostic, entry 0, PT_NULL only, zero PT_LOAD segments**, rather than an OTA BIN. The source still has 95 undefined implementations. Separately named local, hidden, NOTYPE ABS constants preserve their original reference addresses without supplying function bodies. The 65 spans concatenate only originally adjacent owners of the same kind/alignment, without unknown gap bytes. Earlier `ld.lld -r` ET_REL output zeroed section VMAs and did not prove original placement.

| Check | Result |
| --- | --- |
| Sized code/data owners | 1,196/7; actual addresses, lengths and every byte match |
| Instructions/direct transfers | 4,832/805; 788 native control relocations plus 17 unchanged intra-owner branches |
| Direct targets | 709 select measured instructions; 96 select unimplemented provider reference addresses |
| Ordinary next/potential call-return positions | 4,447/286; every position has a real compiled instruction |
| Register-indirect transfers/MRET | 213/10; runtime destinations and context remain unproved |
| Startup EBREAK | Original EBREAK at `0x8034`; 328B vector data starts at `0x8038`; trap/debug handling and resume destination remain unknown |

The conservative owner-tail check retains 812 potential continuations: 811 select code, with the breakpoint/vector boundary remaining. The instruction-wide audit separates traps from ordinary next positions. Zero ordinary continuation gaps does not prove trap, indirect-call, IRQ or whole-CFG closure. Neither reachability nor execution was observed.

[Summary](summary.json) · [Native linker receipt](../../experiments/tsl9-original-layout/build/original-v3/measurement.json) · [Instruction evidence](../../experiments/tsl9-original-layout/build/flow-v2/c-flow.json) · [Unimplemented providers](../callback-flow-2026-10-24/next-providers.json)

Replay from the project root with the already-installed, pinned LLVM directory:

```sh
python3 experiments/tsl9-original-layout/build-v3.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/original-v3
python3 experiments/tsl9-original-layout/verify-flow-v2.py --replay experiments/tsl9-original-layout/build/flow-v2
```

Next: reconstruct original `19BF0` and actual dependencies. Inexact clock `18834`, fields `1973C` and IRQ `9A42` candidates stay unbound. Hardware, resident, private ABI, startup/RAM/IRQ and OTA remain unproved. This milestone changes no C/C++ source and produces no BIN, target execution, hardware/network access, commit or push.

Extension candidates: offline reconstruction coverage checks now exist for the measured scopes. Read-only deferred-event diagnostics remain a candidate, not firmware functionality; the user-facing meaning and time units of `2000C794` remain unknown.

