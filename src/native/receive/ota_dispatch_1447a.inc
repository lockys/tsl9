/* Dispatcher continuation; commands 193/192 then epilogue. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch11")))
void tsl9_ota_dispatch_1447a(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch11:\n"
        "li a5, 193\n"
        "beq a1, a5, .Ldispatch11+0x520\n"
        "bltu a5, a1, .Ldispatch11+0x48\n"
        "li a5, 192\n"
        "bne a1, a5, .Ldispatch11-0x3e2\n"
        "c.li a4, 1\n"
        "lbu a5, 0(s0)\n"
        "bne s2, a4, .Ldispatch11+0x36a\n"
        "beq a5, s2, .Ldispatch11+0x34c\n"
        "beq a5, zero, .Ldispatch11+0x334\n"
        "c.li a4, 2\n"
        "bne a5, a4, .Ldispatch11-0x3e2\n"
        "c.li a1, 2\n"
        "c.mv a0, s1\n"
        "jal ra, tsl9_dispatch11_provider_13ba6\n"
        "c.li a0, 0\n"
        "jal ra, tsl9_dispatch11_flow_12aa0\n"
        "c.li a0, 1\n"
        "jal ra, tsl9_dispatch11_flow_12aa0\n"
        "c.li a0, 2\n"
        "jal ra, tsl9_dispatch11_flow_12aa0\n"
        "c.j .Ldispatch11-0x3e2\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
