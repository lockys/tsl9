/* Continuation in the original dispatcher frame; not independently callable. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch46")))
void tsl9_ota_dispatch_14976(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        ".Ldispatch46:\n"
        "jal ra, .Ldispatch46-0x1f6e\n"
        ".option rvc\n"
        "c.j .Ldispatch46-0x152\n"
        ".option norvc\n"
        "slli a4, a5, 19\n"
        "bge a4, zero, .Ldispatch46+0x14\n"
        ".option rvc\n"
        "c.li a4, 1\n"
        ".option norvc\n"
        "sb a4, 59(sp)\n"
        "slli a4, a5, 18\n"
        "bge a4, zero, .Ldispatch46-0xa\n"
        ".option rvc\n"
        "c.li a5, 2\n"
        ".option norvc\n"
        "sb a5, 59(sp)\n"
        ".option rvc\n"
        "c.j .Ldispatch46-0xa\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
