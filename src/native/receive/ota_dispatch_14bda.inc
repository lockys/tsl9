/* Dispatcher-frame continuation [0x14bda, 0x14be4); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch71")))
void tsl9_ota_dispatch_14bda(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        ".Ldispatch71:\n"
        "lbu a5, 1(s0)\n"
        ".option norvc\n"
        "addi a1, s0, 2\n"
        ".option rvc\n"
        "c.beqz a5, .Ldispatch71+0x36\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
