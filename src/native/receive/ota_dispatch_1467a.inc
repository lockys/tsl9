/* Dispatcher continuation; compare stack byte then mask-store. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch20")))
void tsl9_ota_dispatch_1467a(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch20:\n"
        "lbu a3, 38(sp)\n"
        "c.li a4, 8\n"
        "c.li a5, 1\n"
        "bne a3, a4, .Ldispatch20+0x1c\n"
        "lbu a5, 45(sp)\n"
        "lbu a4, 44(sp)\n"
        "c.slli a5, 8\n"
        "c.or a5, a4\n"
        "andi a5, a5, 1023\n"
        "c.lwsp a4, 68(sp)\n"
        "lui a3, 0xfffc0\n"
        "addi a3, a3, 255\n"
        "c.and a4, a3\n"
        "c.slli a5, 8\n"
        "c.or a5, a4\n"
        "c.swsp a5, 68(sp)\n"
        "jal ra, tsl9_dispatch20_leaf_d4ea\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
