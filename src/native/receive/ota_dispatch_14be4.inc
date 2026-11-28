/* In-frame continuation [0x14be4, 0x14bf6); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch72")))
void tsl9_ota_dispatch_14be4(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "addi a4, gp, 104\n"
        "lui a5, 0x40\n"
        ".option rvc\n"
        "c.lw a5, 76(a5)\n"
        "c.lw a0, 0(a4)\n"
        ".option norvc\n"
        "addi a2, zero, 256\n"
        ".option rvc\n"
        "c.jalr a5\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
