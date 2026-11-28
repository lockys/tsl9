/* Dispatcher-frame continuation [0x14b1c, 0x14b3a); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch63")))
void tsl9_ota_dispatch_14b1c(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        ".Ldispatch63:\n"
        "jal ra, .Ldispatch63-0x1cc8\n" /* 0x12e54 */
        ".option rvc\n"
        "c.mv a0, s1\n"
        ".option norvc\n"
        "jal ra, .Ldispatch63-0x14bc\n" /* 0x13660 */
        ".option rvc\n"
        "c.li a3, 0\n"
        ".option norvc\n"
        "addi a2, zero, 100\n"
        ".option rvc\n"
        "c.li a1, 0\n"
        ".option norvc\n"
        "auipc a0, 0xffff5\n"
        "addi a0, a0, -1312\n" /* 0x960e, when placed at 0x14b1c */
        "jal zero, .Ldispatch63-0x8c4\n" /* 0x14258 */
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
