/* In-frame continuation [0x14bf6, 0x14c10); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch73")))
void tsl9_ota_dispatch_14bf6(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".Ldispatch73:\n"
        ".option norvc\n"
        "jal ra, .Ldispatch73-0x1ba4\n" /* 0x13052 */
        ".option rvc\n"
        "li a3, 0\n"
        ".option norvc\n"
        "addi a2, zero, 100\n"
        ".option rvc\n"
        "li a1, 0\n"
        ".option norvc\n"
        "auipc a0, 0xffff5\n"
        "addi a0, a0, -1524\n" /* 0x960e */
        "jal ra, .Ldispatch73-0xbad2\n" /* 0x9124 */
        ".option rvc\n"
        "c.j .Ldispatch73-0x3a\n" /* 0x14bbc */
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
