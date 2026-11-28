/* Continuation in the original dispatcher frame; not independently callable. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch40")))
void tsl9_ota_dispatch_14934(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".option norelax\n"
        "lbu a5, 0(s0)\n"
        "lbu a4, 1(s0)\n"
        "andi a2, s2, 255\n"
        "c.slli a5, 8\n"
        "c.or a5, a4\n"
        "sh a5, 48(sp)\n"
        "sb a2, 50(sp)\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
