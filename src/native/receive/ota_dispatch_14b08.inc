/* Dispatcher-frame continuation [0x14b08, 0x14b1c); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch62")))
void tsl9_ota_dispatch_14b08(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "addi a4, gp, 96\n"
        "lui a5, 0x40\n"
        ".option rvc\n"
        "c.lw a0, 0(a4)\n"
        "c.lw a5, 76(a5)\n"
        ".option norvc\n"
        "addi a2, zero, 256\n"
        ".option rvc\n"
        "c.mv a1, s0\n"
        "c.jalr a5\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
