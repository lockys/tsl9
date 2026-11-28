/* Dispatcher continuation; mix stack words then call 0x82A8. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch18")))
void tsl9_ota_dispatch_145e6(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch18:\n"
        "c.lwsp a4, 40(sp)\n"
        "c.lwsp a3, 36(sp)\n"
        "c.lui a5, 1\n"
        "addi a1, a5, -1\n"
        "srli a2, a3, 26\n"
        "andi a3, a4, 63\n"
        "c.slli a3, 6\n"
        "c.or a3, a2\n"
        "c.and a3, a1\n"
        "slli a2, a3, 16\n"
        "c.lwsp a3, 64(sp)\n"
        "lui a5, 0xf0010\n"
        "c.addi a5, -1\n"
        "c.and a3, a5\n"
        "srli a5, a4, 8\n"
        "c.and a5, a1\n"
        "c.or a3, a2\n"
        "c.slli a5, 16\n"
        "slli a4, a3, 4\n"
        "c.srli a5, 16\n"
        "slli a2, a5, 28\n"
        "c.srli a4, 4\n"
        "c.or a4, a2\n"
        "c.srli a5, 4\n"
        ".2byte 0x1050\n"
        "c.li a1, 6\n"
        "c.li a0, 1\n"
        "c.swsp a4, 64(sp)\n"
        "sb a5, 68(sp)\n"
        "jal ra, tsl9_dispatch18_feature_82a8\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
