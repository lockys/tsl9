/* Continuation in the original dispatcher frame; not independently callable. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch36")))
void tsl9_ota_dispatch_148de(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".option norelax\n"
        ".Ldispatch36:\n"
        "and t1, a1, a6\n"
        "beqz t1, .Ldispatch36+0x1e\n"
        "addi t1, a4, 1\n"
        "addi t3, sp, 160\n"
        "c.slli a4, 1\n"
        "c.add a4, t3\n"
        "sh a1, -136(a4)\n"
        "andi a4, t1, 255\n"
        "c.j .Ldispatch36-6\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
