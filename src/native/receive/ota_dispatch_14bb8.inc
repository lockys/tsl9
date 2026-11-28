/* Dispatcher-frame continuation [0x14bb8, 0x14bc0); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch69")))
void tsl9_ota_dispatch_14bb8(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        ".Ldispatch69:\n"
        "jal ra, .Ldispatch69+0x2fda\n"
        "li a2, 0\n"
        "c.j .Ldispatch69+0x8a\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
