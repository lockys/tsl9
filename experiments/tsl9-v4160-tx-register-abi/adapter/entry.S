/* Narrow returning entry adapter; all body logic is compiled typed C/C++. */
.section .text.tsl9_tx_entry,"ax",@progbits
.p2align 1
.globl tsl9_ota_tx_8a56
.type tsl9_ota_tx_8a56,@function
tsl9_ota_tx_8a56:
    li a5,1039
.Ltx_guard_branch:
    bltu a5,a3,0
    .reloc .Ltx_guard_branch,R_RISCV_BRANCH,tsl9_tx_oversized_return
.size tsl9_ota_tx_8a56,.-tsl9_ota_tx_8a56
