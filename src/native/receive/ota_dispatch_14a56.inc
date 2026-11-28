/* Dispatcher-frame continuation [0x14a56, 0x14a6c); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch56")))
void tsl9_ota_dispatch_14a56(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        ".Ldispatch56:\n"
        "andi a1, s2, 255\n"
        ".option rvc\n"
        "c.mv a0, s0\n"
        ".option norvc\n"
        "jal ra, .Ldispatch56-0xb764\n" /* 0x92f2 */
        "bne a0, zero, .Ldispatch56-0x9be\n" /* 0x14098 */
        ".option rvc\n"
        "c.li a3, 0\n"
        ".option norvc\n"
        "addi a2, zero, 100\n"
        ".option rvc\n"
        "c.li a1, 0\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
