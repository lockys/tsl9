/* Dispatcher-frame continuation [0x14a40, 0x14a56); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch55")))
void tsl9_ota_dispatch_14a40(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        ".Ldispatch55:\n"
        "andi a1, s2, 255\n"
        ".option rvc\n"
        "c.mv a0, s0\n"
        ".option norvc\n"
        "jal ra, .Ldispatch55-0xb74e\n" /* 0x92f2 */
        "bne a0, zero, .Ldispatch55-0x9a8\n" /* 0x14098 */
        "addi a1, zero, 0xa4\n"
        "jal zero, .Ldispatch55-0x89c\n" /* 0x141a4 */
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
