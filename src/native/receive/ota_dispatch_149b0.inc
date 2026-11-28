/* Continuation within the original dispatcher frame; not independently callable. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch48")))
void tsl9_ota_dispatch_149b0(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        ".Ldispatch48:\n"
        "lbu a0, 0(s0)\n"
        "jal ra, .Ldispatch48+0xc20\n"
        ".option rvc\n"
        "c.li a2, 1\n"
        ".option norvc\n"
        "addi a1, zero, 187\n"
        "jal zero, .Ldispatch48-0x896\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
