/* Dispatcher continuation; table-bit gate then command ordinal filter. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch7")))
void tsl9_ota_dispatch_14370(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch7:\n"
        "c.lw a5, 0(s1)\n"
        "lbu a5, 4(a5)\n"
        "c.andi a5, 8\n"
        "beq a5, zero, .Ldispatch7-0x2d8\n"
        "jal ra, tsl9_dispatch7_inputs_e20c\n"
        "c.j .Ldispatch7-0x2d8\n"
        "li a5, 166\n"
        "beq a1, a5, .Ldispatch7+0x664\n"
        "bltu a1, a5, .Ldispatch7+0x6e6\n"
        "li a5, 167\n"
        "beq a1, a5, .Ldispatch7+0x67a\n"
        "li a5, 169\n"
        "bne a1, a5, .Ldispatch7-0x2d8\n"
        "c.li a5, 25\n"
        "bgeu a5, s2, .Ldispatch7+0x764\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
