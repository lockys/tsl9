/* Dispatcher-frame continuation [0x14b9c, 0x14bb8); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch68")))
void tsl9_ota_dispatch_14b9c(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        ".Ldispatch68:\n"
        "li a4, 2\n"
        ".option norvc\n"
        "beq a5, a4, .Ldispatch68+0xb4\n"
        ".option rvc\n"
        "li a4, 3\n"
        ".option norvc\n"
        "bne a5, a4, .Ldispatch68-0xb04\n"
        "jal ra, .Ldispatch68+0x2ff6\n"
        "lbu a5, 1(s0)\n"
        ".option rvc\n"
        "c.beqz a5, .Ldispatch68+0xdc\n"
        ".option norvc\n"
        "jal ra, .Ldispatch68-0x1b18\n"
        ".option rvc\n"
        "c.j .Ldispatch68+0x5e\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
