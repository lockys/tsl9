/* In-frame continuation [0x14c28, 0x14c32); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch75")))
void tsl9_ota_dispatch_14c28(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        ".Ldispatch75:\n"
        "c.li a1, 0\n"
        "c.mv a0, s1\n"
        ".option norvc\n"
        "jal ra, .Ldispatch75-0xcaa\n" /* 0x13f7e */
        ".option rvc\n"
        "c.j .Ldispatch75-0x2e\n" /* 0x14bfa */
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
