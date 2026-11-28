/* Dispatcher-frame continuation, not an independently callable function. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch52")))
void tsl9_ota_dispatch_149fc(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        ".Ldispatch52:\n"
        "lbu a0, 0(s0)\n"
        ".option rvc\n"
        "c.li a4, 4\n"
        ".option norvc\n"
        "addi a5, a0, -1\n"
        "andi a5, a5, 255\n"
        "bltu a4, a5, .Ldispatch52+0x16\n"
        "jal ra, .Ldispatch52-0x9308\n"
        "lbu a2, 0(s0)\n"
        "addi a1, zero, 162\n"
        "jal zero, .Ldispatch52-0x8e2\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
