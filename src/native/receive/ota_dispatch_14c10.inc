/* In-frame continuation [0x14c10, 0x14c28); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch74")))
void tsl9_ota_dispatch_14c10(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".Ldispatch74:\n"
        ".option norvc\n"
        "addi a4, gp, 100\n"
        "lui a5, 0x40\n"
        ".option rvc\n"
        "lw a5, 76(a5)\n"
        "lw a0, 0(a4)\n"
        ".option norvc\n"
        "addi a2, zero, 256\n"
        ".option rvc\n"
        "jalr a5\n"
        ".option norvc\n"
        "jal ra, .Ldispatch74-0x1cc8\n" /* 0x12f48 */
        ".option rvc\n"
        "c.j .Ldispatch74-0x16\n" /* 0x14bfa */
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
