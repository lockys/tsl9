/* Dispatcher-frame continuation at 0x14a24; not independently callable. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch54")))
void tsl9_ota_dispatch_14a24(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        ".Ldispatch54:\n"
        "c.li a2, 1\n"
        "c.li a1, 0\n"
        ".option norvc\n"
        "auipc a0, 0xffff5\n" /* PC 0x14a28, target 0x9508 */
        "addi a0, a0, -1312\n"
        "jal ra, .Ldispatch54-0xb536\n" /* 0x94ee */
        ".option rvc\n"
        "c.li a1, 0\n"
        "c.mv a0, s1\n"
        ".option norvc\n"
        "jal ra, .Ldispatch54-0xaa6\n" /* 0x13f7e */
        "jal zero, .Ldispatch54-0x98c\n" /* 0x14098 */
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
