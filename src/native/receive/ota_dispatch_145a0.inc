/* Dispatcher continuation; pack stack words then call 0x82A8. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch17")))
void tsl9_ota_dispatch_145a0(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch17:\n"
        "lbu a5, 40(sp)\n"
        "lbu a4, 41(sp)\n"
        ".2byte 0x1050\n"
        "c.slli a5, 8\n"
        "c.slli a4, 16\n"
        "c.add a5, a4\n"
        "lbu a4, 39(sp)\n"
        "c.li a1, 5\n"
        "c.li a0, 1\n"
        "c.add a5, a4\n"
        "lbu a4, 42(sp)\n"
        "c.slli a4, 24\n"
        "c.add a5, a4\n"
        "c.swsp a5, 52(sp)\n"
        "lbu a4, 45(sp)\n"
        "lbu a5, 44(sp)\n"
        "c.slli a4, 16\n"
        "c.slli a5, 8\n"
        "c.add a5, a4\n"
        "lbu a4, 43(sp)\n"
        "c.add a5, a4\n"
        "lbu a4, 46(sp)\n"
        "c.slli a4, 24\n"
        "c.add a5, a4\n"
        "c.swsp a5, 56(sp)\n"
        "jal ra, tsl9_dispatch17_feature_82a8\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
