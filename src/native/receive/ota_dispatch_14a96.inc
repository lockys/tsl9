/* Dispatcher-frame continuation [0x14a96, 0x14a9e); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch58")))
void tsl9_ota_dispatch_14a96(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        ".Ldispatch58:\n"
        "c.addi a4, 1\n"
        "c.addi a5, 1\n"
        ".option norvc\n"
        "bne a1, a4, .Ldispatch58-0x6e0\n" /* 0x143b6 */
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
