/* Continuation in the original dispatcher frame; not independently callable. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch42")))
void tsl9_ota_dispatch_14964(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norvc\n"
        ".option norelax\n"
        ".Ldispatch42:\n"
        "bltu a4, a5, .Ldispatch42+0x18\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
