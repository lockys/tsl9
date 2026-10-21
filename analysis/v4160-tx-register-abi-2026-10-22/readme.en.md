# TSL9 TX entry and native calling frame

[繁體中文](README.md)

This milestone continues reconstruction of OTA transmit function `0x8A56..0x8B6E` from official ID2966 V4.1.60. The goal is readable C/C++ with the actual entry, resident-call and memory-order contract. Original image SHA-256: `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`. **This is not proof of original-hardware or BLE OTA compatibility.**

## Actual evidence

The original 280-byte / 96-instruction contract reuses the authenticated source decoder. This round additionally checks the oversized-input path, five saved registers and split success restores. See [source-review](source-review/readme.en.md) and the independent [ABI review](ABI-review/readme.en.md).

Two ordinary C branch hints restore both resident-call return addresses, `0x8A90` and `0x8AB6`, but the standalone compiler candidate still creates its frame before rejecting oversized input. Actual synthetic diagnostics show that removing a memory clobber or declaring a global register does not provide a sufficient repair; see [compiler diagnostics](entry-plan/readme.en.md).

A narrow entry uses two standard assembly instructions and a standard ELF `R_RISCV_BRANCH` relocation. The body and identity-return leaf are compiled C11/C++17. Both actual linked language variants have:

| Part | Address | Bytes |
| --- | --- | --- |
| Real entry FUNC | 0x8A56 | 8 |
| Readable C/C++ valid-input body | 0x8A5E | 270 |
| Real C/C++ return leaf | 0x8B6C | 2 |

They are adjacent and own 280 bytes in total. The public entry honestly retains its eight-byte FUNC size, rather than pretending to be one 280-byte C function. Oversized input takes only the A5 assignment, unsigned branch and RET, with no stack/memory access or new RA link. This is a narrow assembly port plus typed code, not pure compiler output or whole-original-function assembly.

Actual loop CFG correspondence is also checked: original BLTU's true edge corresponds to candidate BGEU's false edge. Both preserve the low16 counter comparison, live S0, eight payload instructions and the backedge to the corresponding counter header. Nine actual instruction-byte mutations are rejected per language. This proof assumes corresponding header registers and memory responses; it excludes asynchronous interference and reads that treat replaced code bytes themselves as payload.

## Remaining requirements

Success must freshly restore RA/S1/S2/S3 before descriptor halfword stores, restore S0 afterwards, and restore SP only after the task-byte read. The compiler's late restores can change values when frame memory aliases the descriptor. A separate bounded scheduling stage now repairs this by reordering only five newly compiled save instructions and five restore instructions. Actual C/C++ outputs pass independent checks, with every other ELF byte and metadata unchanged. These restored boundaries do not prove whole-function or arbitrary asynchronous equivalence.

The installed ROM contract, actual stack reachability, unknown computed entries, physical chip/peripherals, BOOT/updater acceptance and recovery are still not fully proved. This component is not yet in a complete image. That image remains the prior twelve readable functions / 650 bytes; this round produces no new flashable BIN.

A passing check or seal proves only its stated static conditions. RV32 output is data only: no execution/emulation, BLE/CAN/Flash operation or vendor service request. The full objective remains original-hardware firmware accepted by the original BLE updater; it is not reduced to a HOST model.

Offline packet preflight and update wait-reason display remain [feature proposals](../v4160-ota-tx-2026-10-22/continuation-plan/readme.en.md), not implemented hardware features.
