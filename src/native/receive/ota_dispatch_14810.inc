/* Dispatcher continuation; requires the original live registers and frame. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch29")))
void tsl9_ota_dispatch_14810(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        "c.bnez a5, 0\n"
        ".reloc .-2, R_RISCV_RVC_BRANCH, tsl9_dispatch29_case_14848\n"
        "c.li a0, 0\n"
        "jal ra, tsl9_dispatch29_provider_12a6e\n"
        "c.li a0, 1\n"
        "jal ra, tsl9_dispatch29_provider_12aa0\n"
        "c.li a0, 2\n"
        "jal ra, tsl9_dispatch29_provider_12aa0\n"
        "c.li a2, 1\n"
        "addi a1, zero, 188\n"
        "jal zero, tsl9_dispatch29_return_1411a\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
