/* Dispatcher continuation; commands 185/186 then epilogue. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch10")))
void tsl9_ota_dispatch_14446(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch10:\n"
        "li a5, 185\n"
        "beq a1, a5, .Ldispatch10+0x746\n"
        "li a5, 186\n"
        "bne a1, a5, .Ldispatch10-0x3ae\n"
        "c.li a5, 1\n"
        "bne s2, a5, .Ldispatch10+0x70a\n"
        "lbu a5, 0(s0)\n"
        "beq a5, s2, .Ldispatch10+0x6f4\n"
        "c.li a4, 2\n"
        "bne a5, a4, .Ldispatch10-0x3ae\n"
        "c.li a1, 0\n"
        "c.li a0, 1\n"
        "jal ra, tsl9_dispatch10_message_1264e\n"
        "c.mv a0, s1\n"
        "jal ra, tsl9_dispatch10_gap_136d0\n"
        "c.j .Ldispatch10-0x3ae\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
