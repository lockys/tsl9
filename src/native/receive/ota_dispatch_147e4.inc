/* Dispatcher guard; requires the original live registers and frame. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch27")))
void tsl9_ota_dispatch_147e4(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norvc\n"
        "addi a4, zero, 255\n"
        "bne a5, a4, 0\n"
        ".reloc .-4, R_RISCV_BRANCH, tsl9_dispatch27_reject_1491a\n"
        "lbu a4, 1(s0)\n"
        "bne a4, a5, 0\n"
        ".reloc .-4, R_RISCV_BRANCH, tsl9_dispatch27_reject_1491a\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
