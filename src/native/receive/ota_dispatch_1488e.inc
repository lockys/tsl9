/* Continuation in the original dispatcher frame; not independently callable. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch33")))
void tsl9_ota_dispatch_1488e(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".option norelax\n"
        ".Ldispatch33:\n"
        "bltu a2, s2, .Ldispatch33+0x26\n"
        "c.addi4spn a1, sp, 48\n"
        "li a2, 112\n"
        "c.li a0, 0\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
