/* Dispatcher continuation; copies via resident slot 0x4004C then schedules. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch6")))
void tsl9_ota_dispatch_1432e(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch6:\n"
        "lui s2, 0x40\n"
        "lw a5, 76(s2)\n"
        "c.lw a0, 0(s1)\n"
        "c.li a2, 16\n"
        "addi a1, s0, 24\n"
        "c.jalr a5\n"
        "c.lw a0, 0(s1)\n"
        "lw a5, 76(s2)\n"
        "c.li a2, 16\n"
        "addi a1, s0, 59\n"
        "addi a0, a0, 96\n"
        "c.jalr a5\n"
        "jal ra, tsl9_dispatch6_writer_13138\n"
        "c.li a3, 0\n"
        "li a2, 100\n"
        "c.li a1, 0\n"
        "auipc a0, 0xffff5\n"
        "addi a0, a0, 688\n"
        "jal ra, tsl9_dispatch6_scheduler_9124\n"
        "c.li a0, 0\n"
        "jal ra, tsl9_dispatch6_entry_13dd4\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
