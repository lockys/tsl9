# IRQ callframe C/C++ core

[繁體中文](README.md)

This version retains six calls to shared RCC helpers instead of inlining six RMWs into the initializer. Readable C/C++ expresses call order, masks and peripheral stores. Narrow native primitives bind S0/S1/S2, four-byte JALs, CSR operations and output registers; the compiler creates/restores the stack frame. The entire original function is not pasted as assembly.

## Reproduce

```sh
sh experiments/tsl9-v4160-irq-callframe/verify.sh --language both
```

Alternatively run `python experiments/tsl9-v4160-irq-callframe/verify.py --language both`. Separate C translation units provide main and the four helpers. Each C11/C++17 canonical host suite passes 9184 cases /246384 assertions and rechecks the pinned original 264-byte/94-instruction proof. Host tests do not prove native inline asm, stack or hardware behavior.

## Native results

Both linked languages produce a **144-byte** main and four **30-byte** helpers at the original entries. C++ additionally uses `-fno-exceptions`, without extra unwind allocations. Actual tool hashes and ELF checks must establish these facts; other compilers are not assumed equivalent.

The main's initial SP adjustment and 134 bytes after offset10 match the original. Only four stack-store instructions are reordered. Both establish a 16-byte frame with RA@12, S0@8, S1@4 and S2@0, but the compiler stores RA first while the original stores S2 first. Their normally completed frame can be compared separately; **pointwise stack state and asynchronous IRQ equivalence remain unproved**. No assumption about real interrupts or external actors follows.

All six four-byte JAL PCs, targets and return links can be checked. The helpers' 120 bytes equal the original BIN. This closes the standalone extent-size gap, not full firmware, ROM, chip, board, startup or OTA compatibility. Any integrated image must separately disclose retained original raw code and unmet gates.

Native/source evidence is under `analysis/v4160-irq-callframe-2026-10-21/`. Original firmware is read only. No RV32 execution/emulation or BLE/UART/CAN/physical Flash I/O occurs.
