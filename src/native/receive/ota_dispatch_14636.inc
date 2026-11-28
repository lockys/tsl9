/* Dispatcher continuation; two more packed halfwords then 0x82A8. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch19")))
void tsl9_ota_dispatch_14636(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch19:\n"
        "lbu a5, 42(sp)\n"
        "lbu a4, 41(sp)\n"
        ".2byte 0x1050\n"
        "c.slli a5, 8\n"
        "c.or a5, a4\n"
        "sh a5, 62(sp)\n"
        "lbu a5, 44(sp)\n"
        "lbu a4, 43(sp)\n"
        "c.li a1, 7\n"
        "c.slli a5, 8\n"
        "c.or a5, a4\n"
        "c.li a0, 1\n"
        "sh a5, 60(sp)\n"
        "jal ra, tsl9_dispatch19_feature_82a8\n"
        "lbu a5, 42(sp)\n"
        "lbu a4, 41(sp)\n"
        ".2byte 0x1050\n"
        "c.slli a5, 8\n"
        "c.or a5, a4\n"
        "c.li a1, 3\n"
        "c.li a0, 1\n"
        "sh a5, 64(sp)\n"
        "jal ra, tsl9_dispatch19_feature_82a8\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
