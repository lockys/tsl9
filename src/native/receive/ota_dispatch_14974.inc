/* Continuation in the original dispatcher frame; not independently callable. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch45")))
void tsl9_ota_dispatch_14974(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".option norelax\n"
        "c.addi4spn a0, sp, 48\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
