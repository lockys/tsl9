# Allocator callback field origin and OTA reply-frame experiments

[繁體中文](README.md)

This round advances pointer/callee/memory contracts needed for original-hardware compatibility. **No new BIN. The existing77,824-byte source-wired experimental image and568-byte component remain unchanged and unvalidated for flashing.**

## Confirmed progress

| Scope | Actual evidence | Unproved |
|---|---|---|
| Callback writer | Each114B/41-instruction BLE-init prefix copies64 bytes into2000323C/200031EC; +52 equals20003270/20003220 | Live value, subsequent writers, lifetime, installed ROM |
| Candidate SDK layout | Actual RV32 C compilation of both headers gives staCB52/readFlash56/writeFlash60/config64 | Installed callback arguments/effects |
| Original App | Actual308B;32 selected fields/23 standard stores; numerical SNVAddr08077C00 and no explicit SP68..71 store | Zero across unknown calls/aliases, full NV extent, free Flash |
| C lifetime experiments | 568→560→556B; final188 instructions/48-byte frame removes an S8 spill pair | Original530-byte placement/full ABI |
| Reply object | Genuine independent SP10/11, no overlap with savedS7@12; original seven common save locations retained | Entry-relative−38 still differs from original−36; address observation |

After14098 the original caller restores its own RA/S0..S3 and returns, without restoring S7. Redirecting the reply into the new savedS7 slot would propagate corruption beyond that caller; it is not used as a fix. Original/new save order also differs. Equal common save locations do not establish the complete frame contract.

## Code and reproduction

- [Bounded C/C++ experiment](../../experiments/tsl9-v4160-ota-reply-frame/readme.en.md) and[actual compilation/replay](implementation/readme.en.md). Only two motivated source profiles; no third flag sweep, opcode patch, fabricated size, borrowed spill object or new image link.
- [Independent frame/source-delta review](frame-review/readme.en.md) reads old568/new556 with caller/UID/pointer limits and two ELF controls.
- [Candidate callback writer](callback-review/readme.en.md) covers each114B prefix,30B zero helper and8B initializer tail. Twelve adjacent read patterns per candidate and no adjacent direct stores do not exclude bulk/computed writers. Eight raw controls are retained.
- [App/SDK configuration fields](config-review/readme.en.md) covers two40-byte data-only layout objects and five valid immediate-only controls. Default metadata, explicit actual reads and fresh compilation are distinct.

Python/POSIX-shell interfaces are portable; native proof is pinned Windows LLVM, without Linux/macOS/CI claims. Unchanged HOST algorithm suites are not rerun. No RV32 execution, ISA emulation, BLE/UART/CAN/Flash, vendor API or device-ID transmission occurs.

## Next conditions and feature proposal

Prioritize writable ranges of unknown App config calls/indirect stores, remaining allocator paths and staCB lifetime. New C needs another safely removed save or legitimate independent-object layout. Numeric pointer equality alone cannot prove the full ABI. Physical board/ROM/BOOT/RAM/IRQ, Flash/NV ownership and BLE OTA acceptance/recovery remain unproved.

A useful proposed enhancement to offline pre-update inspection is an **NV/ROM condition summary** showing source-visible SNV numbers, appended image extents, candidate type origins and missing evidence together. It is not an implemented hardware feature or flashing authorization.
