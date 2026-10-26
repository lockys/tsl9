# tsCB encoded CPU-store contract

[繁體中文](README.md) · [BLE initialization C/C++](../tsl9-resident-ble-initialization/readme.en.md)

This study checks **encoded CPU stores** in the existing C/C++ callback `0x197F0..0x1995C` and its callees. No target code was added or recompiled,and no firmware,HOST model or ISA was executed.

The14 complete bodies contain1072 bytes/390 instructions. Original BIN bytes,retained source identities,eight actual C/C++ objects and two independent ELF readers are checked. The [receipt](verification-v1.json) records all79 store sites. The [checker](verify-v1.py) performs reaching-definition,literal-address and affine-stack analysis;it does not simulate memory or hardware.

| Store class | Sites | Established scope/conditions |
| --- | ---: | --- |
| Local stack | 27 | Within each allocated frame |
| Numeric MMIO | 33 |17 explicit peripheral word addresses;physical mapping unproved |
| Fill word | 4 | This length32/value0 invocation with valid16-byte-aligned stack;two16-byte iterations |
| Byte tail | 15 | Unreachable under that specialization;not a general fill semantics proof |

The callback allocates128 bytes. Including its deepest selected callee,the **local allocated depth is144 bytes**,conditional on normal returns and the stated memory contracts. It is not a whole-program stack budget,IRQ nesting bound or physical RAM proof.

## Proof boundary

Encoded CPU-store destinations are narrowed to local stack/fill intervals and17 numeric MMIO word addresses. Excluding effects on SDK configuration or the APP heap still requires the incoming stack location,valid nonwrapping memory,nonoverlapping intervals and appropriate hardware nonaliasing.

**staCB being zero at heap allocation remains unproved.** IRQ,DMA,asynchronous peripheral effects,register read/write side effects,polling termination,installed ROM/ISA and OTA are outside this CPU-store contract. Numeric peripheral addresses do not identify the physical chip.

See the [existing callback C/C++](../../src/native/startup/resident_startup.c),[peripheral helpers](../../src/native/startup/peripheral_primitives.c),[RCC helpers](../../src/native/irq/irq_initializer.c),[fill](../../src/native/receive/fill_provider.c) and [summary](summary.json).

## Reproduce

Provide the original BIN,sources and retained curation artifacts/receipt pinned by [spec-v1.json](spec-v1.json). No downloads or recompilation are automatic. From the project root:

```sh
python experiments/tsl9-tscb-store-contract/verify-v1.py
```

Formal APP byte coverage remains **95.54%**;new reconstructed bytes in this study are0. Callback-stage/wait-state diagnostics remain an unimplemented feature candidate,pending safe read semantics and IRQ/stack budgets. No new BIN or hardware operation occurred.
