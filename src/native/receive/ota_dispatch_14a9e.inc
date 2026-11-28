/* Dispatcher-frame continuation [0x14a9e, 0x14ad4); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch59")))
void tsl9_ota_dispatch_14a9e(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        ".Ldispatch59:\n"
        "lui a5, 0x40\n"
        ".option rvc\n"
        "c.lw a5, 76(a5)\n"
        "c.li a2, 4\n"
        "c.jalr a5\n"
        ".option norvc\n"
        "jal ra, .Ldispatch59-0x1966\n" /* 0x13138 */
        ".option rvc\n"
        "c.li a1, 0\n"
        "c.mv a0, s1\n"
        ".option norvc\n"
        "jal ra, .Ldispatch59-0xc90\n" /* 0x13e0e */
        ".option rvc\n"
        "c.li a2, 1\n"
        ".option norvc\n"
        "addi a1, zero, 169\n"
        ".option rvc\n"
        "c.mv a0, s1\n"
        ".option norvc\n"
        "jal ra, .Ldispatch59-0xb38\n" /* 0x13f66 */
        ".option rvc\n"
        "c.li a3, 0\n"
        ".option norvc\n"
        "addi a2, zero, 100\n"
        ".option rvc\n"
        "c.li a1, 0\n"
        ".option norvc\n"
        "auipc a0, 0xffff4\n"
        "addi a0, a0, 848\n" /* 0x8e18 */
        "jal zero, .Ldispatch59-0x846\n" /* 0x14258 */
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
