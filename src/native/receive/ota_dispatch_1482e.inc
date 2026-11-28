/* Dispatcher cases; require the original live registers and frame. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch30")))
void tsl9_ota_dispatch_1482e(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        "c.li a0, 1\n"
        "jal ra, tsl9_dispatch30_provider_12a6e\n"
        "c.li a0, 0\n"
        "c.j 0\n"
        ".reloc .-2, R_RISCV_RVC_JUMP, tsl9_dispatch30_continue_1481a\n"
        "c.li a0, 2\n"
        "jal ra, tsl9_dispatch30_provider_12a6e\n"
        "c.li a0, 0\n"
        "jal ra, tsl9_dispatch30_provider_12aa0\n"
        "c.li a0, 1\n"
        "c.j 0\n"
        ".reloc .-2, R_RISCV_RVC_JUMP, tsl9_dispatch30_continue_14820\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
