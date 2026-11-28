/* Dispatcher continuation; command 208 jump-table cases 0-2 prefix. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch14")))
void tsl9_ota_dispatch_1452e(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch14:\n"
        "c.mv a0, s1\n"
        "c.li a1, 0\n"
        "jal ra, tsl9_dispatch14_provider_13ba6\n"
        "c.li a0, 0\n"
        "jal ra, tsl9_dispatch14_field_12ad0\n"
        "c.j .Ldispatch14-0x496\n"
        "c.mv a0, s1\n"
        "c.li a1, 3\n"
        "jal ra, tsl9_dispatch14_provider_13ba6\n"
        "c.li a0, 2\n"
        "c.j .Ldispatch14+0xa\n"
        "c.li a1, 3\n"
        "c.mv a0, s1\n"
        "jal ra, tsl9_dispatch14_provider_13ba6\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
