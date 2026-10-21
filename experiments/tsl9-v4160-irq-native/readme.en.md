# Native IRQ C/C++ core

[繁體中文](README.md)

Each branch owns its fresh read, RMW, store and normal return, replacing the old core's shared OR/AND/select live ranges. Native I/O primitives bind bases, masks and output registers to the original boundary registers; readable C/C++ still expresses the RMW and peripheral operations. The native profile permits A0/A1/A4/A5, reserves the other integer registers and disables LLVM's machine outliner. This bridges compiler allocation to the original contract; it does not recover complete original source.

## Reproduce

```sh
sh experiments/tsl9-v4160-irq-native/verify.sh --language both
```

Alternatively run `python experiments/tsl9-v4160-irq-native/verify.py --language both`. C11 and C++17 each use the pinned canonical oracle: 4 groups, 9184 cases and 246384 assertions, plus the original 264-byte/94-instruction proof. Only our compiled host test program executes.

The separate [compiler-review](../../analysis/v4160-irq-native-2026-10-21/compiler-review/) entry accepts a caller-supplied LLVM tool directory and records actual tool hashes. It compiles, links, reads ELF and disassembles without executing or emulating RV32.

## Evidence and limits

Each RCC helper at 0x19124, 0x19142, 0x19160 and 0x1917E produces 30 bytes identical to the corresponding pinned V4.1.60 original BIN bytes. This applies to these exact functions and compiler conditions, not the full image.

The IRQ initializer is 180 bytes, exceeding the original 144-byte `[0x9A42,0x9AD2)` extent by 36 bytes. It cannot replace that extent directly. Normal A0/A1/A4/A5 outputs and A2/A3 preservation can be checked separately; intermediate A1 address scratch and different stack/call/CSR timing leave asynchronous IRQ equivalence unproved.

C++ also introduces allocated read-only unwind metadata, which requires separate storage and integration accounting. Matching function bytes does not discharge that obligation. Exact hardware, installed ROM, full placement, startup and OTA compatibility remain unproved. **This component supplies no flashable BIN and performs no BLE/UART/CAN/Flash operations.**
