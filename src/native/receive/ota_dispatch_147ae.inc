/* Dispatcher continuation; two more jump-table cases. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch26")))
void tsl9_ota_dispatch_147ae(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch26:\n"
        "c.li a1, 0\n"
        "c.mv a0, s1\n"
        "jal ra, tsl9_dispatch26_provider_13ba6\n"
        "c.li a0, 0\n"
        "jal ra, tsl9_dispatch26_status_820c\n"
        "c.li a0, 0\n"
        "jal ra, tsl9_dispatch26_feature_1074c\n"
        "jal zero, .Ldispatch26-0x716\n"
        "c.li a1, 2\n"
        "c.mv a0, s1\n"
        "jal ra, tsl9_dispatch26_provider_13ba6\n"
        "c.li a0, 0\n"
        "jal ra, tsl9_dispatch26_gap_12a6e\n"
        "c.li a0, 1\n"
        "jal ra, tsl9_dispatch26_gap_12a6e\n"
        "c.li a0, 2\n"
        "jal ra, tsl9_dispatch26_gap_12a6e\n"
        "jal zero, .Ldispatch26-0x716\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
