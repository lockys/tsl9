/* Dispatcher-frame continuation [0x14ad4, 0x14af4); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch60")))
void tsl9_ota_dispatch_14ad4(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        ".Ldispatch60:\n"
        "c.li a2, 2\n"
        ".option norvc\n"
        "jal zero, .Ldispatch60-0x710\n" /* 0x143c4 */
        ".option rvc\n"
        "c.li a5, 1\n"
        ".option norvc\n"
        "bne s2, a5, .Ldispatch60+0x20\n" /* 0x14af4 */
        "lbu a4, 0(s0)\n"
        ".option rvc\n"
        "c.li a5, 2\n"
        ".option norvc\n"
        "bne a4, a5, .Ldispatch60-0xa3c\n" /* 0x14098 */
        ".option rvc\n"
        "c.mv a0, s1\n"
        ".option norvc\n"
        "jal ra, .Ldispatch60-0x1474\n" /* 0x13660 */
        "jal zero, .Ldispatch60-0xa3c\n" /* 0x14098 */
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
