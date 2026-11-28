/* Continuation in the original dispatcher frame; not independently callable. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch35")))
void tsl9_ota_dispatch_148b4(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".option norelax\n"
        ".Ldispatch35:\n"
        "c.addi a2, 1\n"
        "slli a1, a2, 1\n"
        "c.add a1, s0\n"
        "lhu a1, 0(a1)\n"
        "bltu a0, a1, .Ldispatch35+0x2a\n"
        "addi t1, a3, 1\n"
        "addi t3, sp, 160\n"
        "c.slli a3, 1\n"
        "c.add a3, t3\n"
        "sh a1, -112(a3)\n"
        "andi a3, t1, 255\n"
        "andi a2, a2, 255\n"
        "c.j .Ldispatch35-0x26\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
