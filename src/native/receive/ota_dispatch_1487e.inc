/* Continuation in the original dispatcher frame; not independently callable. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch32")))
void tsl9_ota_dispatch_1487e(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        "c.li a2, 0\n"
        "c.li a5, 0\n"
        "c.li a4, 0\n"
        "c.li a3, 0\n"
        "li a0, 2047\n"
        "c.lui a6, 1\n"
        "c.lui a7, 2\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
