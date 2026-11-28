/* Dispatcher-frame continuation [0x14bc0, 0x14bda); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch70")))
void tsl9_ota_dispatch_14bc0(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        ".Ldispatch70:\n"
        "jal ra, .Ldispatch70+0x2fd2\n"
        "c.beqz a0, .Ldispatch70+0x72\n"
        "li a5, 0x102\n"
        "bne s2, a5, .Ldispatch70-0xb28\n"
        "lbu a4, 0x101(s0)\n"
        "li a5, 0x5a\n"
        "bne a4, a5, .Ldispatch70+0x68\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
