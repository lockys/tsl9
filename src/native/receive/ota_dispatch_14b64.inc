/* Dispatcher-frame continuation [0x14b64, 0x14b8c); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch66")))
void tsl9_ota_dispatch_14b64(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".Ldispatch66:\n"
        ".option norvc\n"
        "addi a4, gp, 88\n"
        "lui a5, 0x40\n"
        ".option rvc\n"
        "lw a0, 0(a4)\n"
        "lw a5, 76(a5)\n"
        ".option norvc\n"
        "addi a2, zero, 256\n"
        ".option rvc\n"
        "mv a1, s0\n"
        "jalr a5\n"
        ".option norvc\n"
        "jal ra, .Ldispatch66-0x1c7e\n" /* 0x12ee6 */
        ".option rvc\n"
        "li a1, 0\n"
        "li a0, 1\n"
        ".option norvc\n"
        "jal ra, .Ldispatch66-0x2516\n" /* 0x1264e */
        ".option rvc\n"
        "mv a0, s1\n"
        ".option norvc\n"
        "jal ra, .Ldispatch66-0x1494\n" /* 0x136d0 */
        ".option rvc\n"
        "c.j .Ldispatch66-0x3e\n" /* 0x14b26 */
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
