/* Dispatcher-frame continuation [0x14af4, 0x14b08); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch61")))
void tsl9_ota_dispatch_14af4(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        ".Ldispatch61:\n"
        "addi a5, zero, 256\n"
        "bne s2, a5, .Ldispatch61-0xa5c\n" /* 0x14098 */
        "lbu a4, 255(s0)\n"
        "addi a5, zero, 90\n"
        "bne a4, a5, .Ldispatch61-0xc0\n" /* 0x14a34 */
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
