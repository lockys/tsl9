/* Dispatcher-frame continuation [0x14b8c, 0x14b9c); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch67")))
void tsl9_ota_dispatch_14b8c(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".Ldispatch67:\n"
        ".option rvc\n"
        "li a4, 1\n"
        ".option norvc\n"
        "bgeu a4, s2, .Ldispatch67-0xaf4\n" /* 0x14098 */
        "lbu a5, 0(s0)\n"
        "beq a5, a4, .Ldispatch67+0x34\n" /* 0x14bc0 */
        ".option rvc\n"
        "c.beqz a5, .Ldispatch67+0x2c\n" /* 0x14bb8 */
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
