/* Continuation in the original dispatcher frame; not independently callable. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch41")))
void tsl9_ota_dispatch_1494c(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".option norelax\n"
        "lui a5, 0x40\n"
        "c.lw a5, 76(a5)\n"
        ".option norvc\n"
        "addi a1, s0, 2\n"
        "addi a0, sp, 51\n"
        ".option rvc\n"
        "c.jalr a5\n"
        "lhu a5, 48(sp)\n"
        "addi a4, zero, 2047\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
