/* Dispatcher continuation; pack stack halfwords then call 0x82A8. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch16")))
void tsl9_ota_dispatch_14576(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch16:\n"
        "lbu a5, 40(sp)\n"
        "lbu a4, 39(sp)\n"
        ".2byte 0x1050\n"
        "c.slli a5, 8\n"
        "c.or a5, a4\n"
        "sh a5, 48(sp)\n"
        "lbu a5, 42(sp)\n"
        "lbu a4, 41(sp)\n"
        "c.li a1, 11\n"
        "c.slli a5, 8\n"
        "c.or a5, a4\n"
        "c.li a0, 1\n"
        "sh a5, 50(sp)\n"
        "jal ra, tsl9_dispatch16_feature_82a8\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
