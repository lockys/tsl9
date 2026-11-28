/* Continuation in the original dispatcher frame; not independently callable. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch44")))
void tsl9_ota_dispatch_14970(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norvc\n"
        ".option norelax\n"
        ".Ldispatch44:\n"
        "jal ra, .Ldispatch44-0xc764\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
