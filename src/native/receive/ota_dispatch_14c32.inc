/* In-frame continuation [0x14c32, 0x14c50); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch76")))
void tsl9_ota_dispatch_14c32(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        ".Ldispatch76:\n"
        "addi a2, zero, 255\n"
        "addi a1, zero, 185\n"
        ".option rvc\n"
        "c.mv a0, s1\n"
        ".option norvc\n"
        "jal ra, .Ldispatch76-0xccc\n" /* 0x13f66 */
        ".option rvc\n"
        "c.li a2, 1\n"
        ".option norvc\n"
        "lbu a1, 1(s0)\n"
        ".option rvc\n"
        "c.mv a0, s1\n"
        ".option norvc\n"
        "jal ra, .Ldispatch76-0x14f2\n" /* 0x13740 */
        "jal zero, .Ldispatch76-0xb9a\n" /* 0x14098 */
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
