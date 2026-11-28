/* Dispatcher continuation; requires the original live registers and frame. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch28")))
void tsl9_ota_dispatch_147f4(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        "c.li a1, 2\n"
        "c.mv a0, s1\n"
        "jal ra, tsl9_dispatch28_provider_13ba6\n"
        "jal ra, tsl9_dispatch28_feature_1070a\n"
        "lhu a5, 2(s0)\n"
        "c.lui a4, 1\n"
        "beq a5, a4, 0\n"
        ".reloc .-4, R_RISCV_BRANCH, tsl9_dispatch28_case_1482e\n"
        "c.lui a4, 2\n"
        "beq a5, a4, 0\n"
        ".reloc .-4, R_RISCV_BRANCH, tsl9_dispatch28_case_14838\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
