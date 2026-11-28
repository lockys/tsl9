/* Dispatcher continuation; command 169 compare then extra ordinals. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch8")))
void tsl9_ota_dispatch_143a4(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch8:\n"
        "addi a5, gp, 84\n"
        "c.lw a5, 0(a5)\n"
        "addi a4, s0, 18\n"
        "addi a1, s0, 22\n"
        "c.addi a5, 12\n"
        "c.mv a0, a5\n"
        "lbu a2, 0(a4)\n"
        "lbu a3, 0(a5)\n"
        "beq a2, a3, .Ldispatch8+0x6f2\n"
        "c.li a2, 0\n"
        "li a1, 169\n"
        "c.j .Ldispatch8-0x28a\n"
        "li a5, 187\n"
        "beq a1, a5, .Ldispatch8+0x60c\n"
        "bltu a5, a1, .Ldispatch8+0xd6\n"
        "li a5, 176\n"
        "beq a1, a5, .Ldispatch8+0x154\n"
        "bltu a5, a1, .Ldispatch8+0xa2\n"
        "li a5, 175\n"
        "bne a1, a5, .Ldispatch8-0x30c\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
