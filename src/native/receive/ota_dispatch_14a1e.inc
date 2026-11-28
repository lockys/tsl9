/* Dispatcher-frame continuation; not independently callable. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch53")))
void tsl9_ota_dispatch_14a1e(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        ".Ldispatch53:\n"
        "c.li s3, 0\n"
        ".option norvc\n"
        "jal zero, .Ldispatch53-0x730\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
