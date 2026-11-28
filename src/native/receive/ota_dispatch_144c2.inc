/* Dispatcher continuation; commands 208/240 then epilogue. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch12")))
void tsl9_ota_dispatch_144c2(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch12:\n"
        "li a5, 208\n"
        "beq a1, a5, .Ldispatch12+0x50\n"
        "li a5, 240\n"
        "bne a1, a5, .Ldispatch12-0x42a\n"
        "c.li a5, 13\n"
        "bgeu a5, s2, .Ldispatch12-0x42a\n"
        "c.li a1, 14\n"
        "c.mv a0, s0\n"
        "jal ra, tsl9_dispatch12_checker_92f2\n"
        "bne a0, zero, .Ldispatch12-0x42a\n"
        "addi a2, s2, -14\n"
        "c.slli a2, 16\n"
        "c.srli a2, 16\n"
        "addi a1, s0, 14\n"
        "c.mv a0, s1\n"
        "jal ra, tsl9_dispatch12_message_126a0\n"
        "c.j .Ldispatch12-0x42a\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
