/* In-frame continuation [0x14c50, 0x14c78); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch77")))
void tsl9_ota_dispatch_14c50(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        ".Ldispatch77:\n"
        "jal ra, .Ldispatch77+0x2f42\n" /* 0x17b92 */
        ".option rvc\n"
        "c.beqz a0, .Ldispatch77_zero\n"
        ".option norvc\n"
        "lbu a1, 2(s0)\n"
        "addi a5, zero, 35\n"
        "bltu a5, a1, .Ldispatch77-0xbb8\n" /* 0x14098 */
        "lbu a0, 1(s0)\n"
        "jal ra, .Ldispatch77+0x2d3a\n" /* 0x1798a */
        ".option rvc\n"
        "c.j .Ldispatch77-0x298\n" /* 0x149b8 */
        ".option norvc\n"
        ".Ldispatch77_zero:\n"
        "addi a2, zero, 255\n"
        "addi a1, zero, 185\n"
        "jal zero, .Ldispatch77-0xb36\n" /* 0x1411a */
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
