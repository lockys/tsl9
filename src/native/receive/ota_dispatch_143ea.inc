/* Dispatcher continuation; command 175 compare, notify, then join. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch9")))
void tsl9_ota_dispatch_143ea(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch9:\n"
        "c.li a5, 2\n"
        "bne s2, a5, .Ldispatch9-0x352\n"
        "auipc a0, 0\n"
        "addi a0, a0, -1128\n"
        "jal ra, tsl9_dispatch9_table_90b0\n"
        "lbu a5, 0(s0)\n"
        "lbu s0, 1(s0)\n"
        "c.slli a5, 8\n"
        "c.or s0, a5\n"
        "jal ra, tsl9_dispatch9_helper_9334\n"
        "sub s2, a0, s0\n"
        "sltiu s2, s2, 1\n"
        "bne a0, s0, .Ldispatch9+0x54\n"
        "jal ra, tsl9_dispatch9_notify_9ef0\n"
        "addi a5, gp, 84\n"
        "c.lw a5, 0(a5)\n"
        "lbu a4, 4(a5)\n"
        "c.andi a4, 8\n"
        "c.beqz a4, .Ldispatch9+0x4e\n"
        "lbu a4, 4(a5)\n"
        "c.andi a4, -9\n"
        "sb a4, 4(a5)\n"
        "jal ra, tsl9_dispatch9_writer_13138\n"
        "c.li a0, 0\n"
        "jal ra, tsl9_dispatch9_status_820c\n"
        "c.mv a2, s2\n"
        "li a1, 175\n"
        "c.j .Ldispatch9-0x2d0\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
