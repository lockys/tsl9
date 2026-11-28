/* Dispatcher continuation; jump-table case 2 gate and copy. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch15")))
void tsl9_ota_dispatch_14552(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch15:\n"
        "auipc a5, 0x1fff8\n"
        "lbu a5, 578(a5)\n"
        "bne a5, zero, .Ldispatch15-0x4ba\n"
        "lui a5, 0x40\n"
        "c.lw a5, 72(a5)\n"
        "c.li a2, 29\n"
        "c.li a1, 0\n"
        "addi a0, sp, 48\n"
        "c.jalr a5\n"
        ".2byte 0x1050\n"
        "c.li a1, 1\n"
        "c.li a0, 1\n"
        "jal ra, tsl9_dispatch15_feature_82a8\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
