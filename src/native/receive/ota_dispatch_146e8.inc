/* Dispatcher continuation; more mask-stores then leaf/get calls. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch22")))
void tsl9_ota_dispatch_146e8(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch22:\n"
        "c.andi a0, 3\n"
        "slli a5, a0, 28\n"
        "c.lwsp a0, 68(sp)\n"
        "lui a4, 0xd0000\n"
        "c.addi a4, -1\n"
        "c.and a0, a4\n"
        "c.or a0, a5\n"
        "c.swsp a0, 68(sp)\n"
        "jal ra, tsl9_dispatch22_leaf_d4e0\n"
        "andi a0, a0, 127\n"
        "slli a5, a0, 7\n"
        "c.lwsp a0, 72(sp)\n"
        "c.lui a4, 0xffffc\n"
        "addi a4, a4, 127\n"
        "c.and a0, a4\n"
        "c.or a0, a5\n"
        "c.swsp a0, 72(sp)\n"
        "jal ra, tsl9_dispatch22_get_1008a\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
