/* Dispatcher continuation; command 176 then command 208 jump table. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch13")))
void tsl9_ota_dispatch_144f8(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch13:\n"
        "lbu a4, 0(s0)\n"
        "c.li a5, 1\n"
        "c.li a1, 0\n"
        "bne a4, a5, .Ldispatch13+0x248\n"
        "c.li a1, 1\n"
        "c.mv a0, s1\n"
        "jal ra, tsl9_dispatch13_provider_13ba6\n"
        "jal ra, tsl9_dispatch13_state_13c4e\n"
        "c.j .Ldispatch13-0x460\n"
        "lbu a5, 0(s0)\n"
        "c.li a4, 4\n"
        "bltu a4, a5, .Ldispatch13-0x460\n"
        "auipc a4, 0x6\n"
        "addi a4, a4, 392\n"
        "c.slli a5, 2\n"
        "c.add a5, a4\n"
        "c.lw a5, 0(a5)\n"
        "c.add a5, a4\n"
        "c.jr a5\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
