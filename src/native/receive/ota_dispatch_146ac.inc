/* Dispatcher continuation; more mask-stores then leaf calls. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch21")))
void tsl9_ota_dispatch_146ac(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch21:\n"
        "andi a0, a0, 1023\n"
        "slli a5, a0, 18\n"
        "c.lwsp a0, 68(sp)\n"
        "lui a4, 0xf0040\n"
        "c.addi a4, -1\n"
        "c.and a0, a4\n"
        "c.or a0, a5\n"
        "c.swsp a0, 68(sp)\n"
        "jal ra, tsl9_dispatch21_leaf_d472\n"
        "c.lwsp a5, 68(sp)\n"
        "slli a4, a0, 30\n"
        "c.srli a0, 2\n"
        "c.slli a5, 2\n"
        "c.srli a5, 2\n"
        "c.or a5, a4\n"
        "c.swsp a5, 68(sp)\n"
        "c.lwsp a5, 72(sp)\n"
        "andi a0, a0, 127\n"
        "andi a5, a5, -128\n"
        "c.or a0, a5\n"
        "c.swsp a0, 72(sp)\n"
        "jal ra, tsl9_dispatch21_leaf_d322\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
