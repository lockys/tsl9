/* Continuation inside the existing dispatcher frame; not independently callable. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch51")))
void tsl9_ota_dispatch_149ea(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        ".Ldispatch51:\n"
        "lbu a2, 0(s0)\n"
        "addi a1, zero, 167\n"
        ".option rvc\n"
        "c.mv a0, s1\n"
        ".option norvc\n"
        "jal ra, .Ldispatch51+0x19c2\n"
        "jal zero, .Ldispatch51-0x952\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
