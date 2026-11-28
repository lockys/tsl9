/* Continuation in the original dispatcher frame; not independently callable. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch38")))
void tsl9_ota_dispatch_1491a(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".option norelax\n"
        "c.addi s2, -2\n"
        "slli a4, s2, 16\n"
        "c.srli a4, 16\n"
        "c.li a5, 8\n"
        "bltu a5, a4, 0\n"
        ".reloc .-4, R_RISCV_BRANCH, tsl9_dispatch38_return_14098\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
