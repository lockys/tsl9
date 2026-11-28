/* Dispatcher continuation; jump-table cases then gated copy. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch24")))
void tsl9_ota_dispatch_1473e(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch24:\n"
        "c.li a1, 4\n"
        "c.mv a0, s1\n"
        "jal ra, tsl9_dispatch24_provider_13ba6\n"
        "c.j .Ldispatch24-0x6a6\n"
        "c.li a1, 3\n"
        "c.mv a0, s1\n"
        "jal ra, tsl9_dispatch24_provider_13ba6\n"
        "auipc a5, 0x1fff8\n"
        "lbu a5, 68(a5)\n"
        "bne a5, zero, .Ldispatch24-0x6a6\n"
        "lui a5, 0x40\n"
        "c.lw a5, 72(a5)\n"
        "c.li a2, 8\n"
        "c.li a1, 0\n"
        "addi a0, sp, 36\n"
        "c.jalr a5\n"
        "addi a2, sp, 48\n"
        "c.li a1, 4\n"
        "c.li a0, 1\n"
        "jal ra, tsl9_dispatch24_feature_82a8\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
