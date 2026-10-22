/* Source-owned narrow runtime entry: canonical resident symbol, real FUNC8. */
.section .text.tsl9_tx_entry,"ax",@progbits
.p2align 1
.globl __tsl9v4160_call_8a56
.type __tsl9v4160_call_8a56,@function
__tsl9v4160_call_8a56:
    li a5,1039
.Ltx_guard_branch:
    bltu a5,a3,0
    .reloc .Ltx_guard_branch,R_RISCV_BRANCH,tsl9_tx_oversized_return
.size __tsl9v4160_call_8a56,.-__tsl9v4160_call_8a56
