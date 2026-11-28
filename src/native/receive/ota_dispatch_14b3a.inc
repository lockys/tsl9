/* Dispatcher-frame continuation [0x14b3a, 0x14b50); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch64")))
void tsl9_ota_dispatch_14b3a(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        ".Ldispatch64:\n"
        "jal ra, .Ldispatch64-0x24da\n" /* 0x12660 */
        ".option rvc\n"
        "c.li a3, 1\n"
        "c.mv a2, s0\n"
        ".option norvc\n"
        "addi a1, zero, 186\n"
        ".option rvc\n"
        "c.mv a0, s1\n"
        ".option norvc\n"
        "jal ra, .Ldispatch64-0xca2\n" /* 0x13e98 */
        "jal zero, .Ldispatch64-0xaa2\n" /* 0x14098 */
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
