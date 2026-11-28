/* Continuation within the original dispatcher frame; not independently callable. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch49")))
void tsl9_ota_dispatch_149c2(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        ".Ldispatch49:\n"
        "lbu a0, 0(s0)\n"
        ".option rvc\n"
        "c.li a1, 1\n"
        ".option norvc\n"
        "sltu a0, zero, a0\n"
        "jal ra, .Ldispatch49+0x2982\n"
        "jal zero, .Ldispatch49-0x92a\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
