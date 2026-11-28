/* Continuation in the original dispatcher frame; not independently callable. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch37")))
void tsl9_ota_dispatch_148fc(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".option norelax\n"
        ".Ldispatch37:\n"
        "and t1, a1, a7\n"
        "beqz t1, .Ldispatch37-0x24\n"
        "addi t1, a5, 1\n"
        "addi t3, sp, 160\n"
        "c.slli a5, 1\n"
        "c.add a5, t3\n"
        "sh a1, -124(a5)\n"
        "andi a5, t1, 255\n"
        "c.j .Ldispatch37-0x24\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
