/* Dispatcher continuation; depends on its original frame and table slots. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch5")))
void tsl9_ota_dispatch_142fc(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch5:\n"
        "addi s1, gp, 84\n"
        "c.lw a5, 0(s1)\n"
        "lbu a4, 27(s0)\n"
        "lbu a5, 3(a5)\n"
        "c.xor a5, a4\n"
        "c.andi a5, 16\n"
        "c.beqz a5, .Ldispatch5+0x1e\n"
        "srli a0, a4, 4\n"
        "c.andi a0, 1\n"
        "jal ra, tsl9_dispatch5_ingress_9b02\n"
        "c.lw a5, 0(s1)\n"
        "lbu a4, 24(s0)\n"
        "lbu a5, 0(a5)\n"
        "c.xor a5, a4\n"
        "c.andi a5, 7\n"
        "c.beqz a5, .Ldispatch5+0x32\n"
        "jal ra, tsl9_dispatch5_callback_fa3c\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
