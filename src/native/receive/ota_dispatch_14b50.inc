/* Dispatcher-frame continuation [0x14b50, 0x14b64); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch65")))
void tsl9_ota_dispatch_14b50(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        ".Ldispatch65:\n"
        "addi a5, zero, 256\n"
        "bne s2, a5, .Ldispatch65-0xab8\n" /* 0x14098 */
        "lbu a4, 255(s0)\n"
        "addi a5, zero, 90\n"
        "bne a4, a5, .Ldispatch65-0x11c\n" /* 0x14a34 */
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
