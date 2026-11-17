# v4.1.60 writer: reduced-barrier offline trial

The fixed 0x18ca4 component has seven regions, 212 bytes and 72 decoded instructions. A temporary candidate removes only the `LIVE()` immediately after `a4 &= 15u` in the 0x18cec metadata region. The original firmware and formal source were not modified.

For the pinned C11 and C++17 RV32 -Oz profiles, both baseline and candidate passed the existing native and linked ELF subcontracts with complete artifact hashes enabled. The candidate's component bytes equal the SHA-256-pinned original firmware span. A mask-7 mutant was rejected by the native and linked typed-instruction checks with complete artifact hashing disabled. Normal and Python -O runs passed.

Actual LLVM IR differs: the number of `asm sideeffect` calls fell from 79 to 78; volatile load/store counts remained 22/8. The unchanged source and IR subcontracts reject the candidate even with full hashes disabled, respectively at the ordered source-line and selected SSA-line comparisons. Those text-identity failures do not themselves prove semantic differences. The original source and IR passed their full-hash subcontracts. These direct subcontract calls are not a full verifier run against the candidate.

This is a bounded offline compiler result, not proof of equivalent C semantics across compiler versions, device ABI, MMIO behavior or whole-firmware integration. It does not increase source coverage or establish a flashable image. Test code and modified source remain local pending publication review.
