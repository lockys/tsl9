/* Standalone reconstruction: five target-minus-table-base RV32 relocations. */
__asm__(
    ".section .rodata.relative_table,\"a\",@progbits\n"
    ".balign 4\n"
    ".globl relative_table\n"
    ".type relative_table,@object\n"
    "relative_table:\n"
    ".macro entry target\n"
    "1: .word 0\n"
    ".reloc 1b, R_RISCV_ADD32, \\target\n"
    ".reloc 1b, R_RISCV_SUB32, relative_table\n"
    ".endm\n"
    "entry target_1452e\n"
    "entry target_1453e\n"
    "entry target_1454a\n"
    "entry target_1473e\n"
    "entry target_14748\n"
    ".size relative_table, .-relative_table\n"
);
