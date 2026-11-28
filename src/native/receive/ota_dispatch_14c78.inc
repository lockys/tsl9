/* In-frame continuations [0x14c78, 0x14c8a); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch78")))
void tsl9_ota_dispatch_14c78(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        ".Ldispatch78:\n"
        "jal ra, .Ldispatch78-0x1cfe\n" /* 0x12f7a */
        ".option rvc\n"
        "c.j .Ldispatch78-0x7e\n" /* 0x14bfa */
        "c.li a1, 2\n"
        "c.mv a0, s1\n"
        ".option norvc\n"
        "jal ra, .Ldispatch78-0xe6a\n" /* 0x13e0e */
        "jal zero, .Ldispatch78-0xabc\n" /* 0x141bc */
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
