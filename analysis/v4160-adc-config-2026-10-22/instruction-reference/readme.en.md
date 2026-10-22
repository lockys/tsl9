# Standard RISC-V fields added in this scope

These are selected lines actually read from the official riscv/riscv-opcodes public sources on2026-10-22. They support bounded static field decoding, not opcode generation or CPU execution.

- [rv_i](https://raw.githubusercontent.com/riscv/riscv-opcodes/master/extensions/rv_i): ori, sll, sltu and and definitions.
- [rv_m](https://raw.githubusercontent.com/riscv/riscv-opcodes/master/extensions/rv_m): mul definition.
- [arg_lut.csv](https://raw.githubusercontent.com/riscv/riscv-opcodes/master/arg_lut.csv): selected register, immediate and opcode positions.

Local digests cover the selected excerpts, not complete upstream files. The master URLs can change; verification uses the captured local lines. The GitHub commits/master API was inaccessible through the web reader, so no immutable commit is invented.
