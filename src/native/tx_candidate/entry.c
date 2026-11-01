/* Source-owned TX entry, encoded by the assembler; not a complete firmware. */
__asm__(
    ".section .text.tsl9_tx_entry,\"ax\",@progbits\n"
    ".p2align 1\n"
    ".globl __tsl9v4160_call_8a56\n"
    ".type __tsl9v4160_call_8a56,@function\n"
    "__tsl9v4160_call_8a56:\n"
    "li a5,1039\n"
    ".Ltx_guard_branch:\n"
    "bltu a5,a3,0\n"
    ".reloc .Ltx_guard_branch,R_RISCV_BRANCH,tsl9_tx_oversized_return\n"
    ".size __tsl9v4160_call_8a56,.-__tsl9v4160_call_8a56\n"
);
